from typing import Optional, Dict, Any
from fastmcp import FastMCP
from .pinboard import get_pinboard_client, rate_limit, format_bookmark_response
from .utils import validate_date_range

import logging
logger = logging.getLogger(__name__)


mcp = FastMCP('pinboard MCP')


@mcp.tool
def get_bookmarks(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    tags: Optional[str] = None,
    limit: int = 200
) -> Dict[str, Any]:
    '''
    retrieve bookmarks from pinboard within a specified date range

    args:
        start_date: start date in yyyy-mm-dd format (optional)
        end_date: end date in yyyy-mm-dd format (optional)
        tags: comma-separated tags to filter by (optional)
        limit: maximum bookmarks to return (default: 100, max: 500)

    returns:
        dictionary containing bookmarks and metadata
    '''
    try:
        if limit <= 0 or limit > 500:
            return {'error': 'limit must be between 1 and 500', 'success': False}

        parsed_start, parsed_end = validate_date_range(start_date, end_date)

        # parse tags
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()] if tags else []

        pinboard_client = get_pinboard_client()

        # build API parameters for posts.all()
        api_params = {
            'results': limit
        }
        if tag_list:
            api_params['tag'] = tag_list
        if parsed_start:
            api_params['fromdt'] = parsed_start
        if parsed_end:
            api_params['todt'] = parsed_end

        logger.info(f'fetching bookmarks with params: {api_params}')

        # fetch bookmarks from Pinboard
        rate_limit()
        bookmarks_raw = pinboard_client.posts.all(**api_params)
        formatted_bookmarks = [format_bookmark_response(bookmark) for bookmark in bookmarks_raw]

        # build response

        filters_applied = {'limit': limit}

        if parsed_start or parsed_end:
            filters_applied['date_range'] = {
                'start': parsed_start.isoformat() if parsed_start else None,
                'end': parsed_end.isoformat() if parsed_end else None
            }

        if tag_list:
            filters_applied['tags'] = ','.join(tag_list)

        response = {
            'count': len(formatted_bookmarks),
            'bookmarks': formatted_bookmarks,
            'filters_applied': filters_applied,
            'success': True
        }

        logger.info(f"successfully retrieved {len(formatted_bookmarks)} bookmarks")
        return response

    except Exception as e:
        logger.error(f"error retrieving bookmarks: {e}")
        return {'error': str(e), 'success': False}


@mcp.tool
def update_bookmark(
    url: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[str] = None,
    private: Optional[bool] = None,
    toread: Optional[bool] = None
) -> Dict[str, Any]:
    '''
    update a bookmark's properties by URL

    args:
        url: the URL of the bookmark to update (required)
        title: new bookmark title (optional)
        description: new bookmark description (optional)
        tags: comma-separated tags (optional)
        private: set bookmark privacy - true for private, false for public (optional)
        toread: mark as to-read - true/false (optional)

    returns:
        dictionary containing updated bookmark data and metadata
    '''
    try:
        if not url or not url.strip():
            return {'error': 'url is required and cannot be empty', 'success': False}

        pinboard_client = get_pinboard_client()

        logger.debug(f"retrieving bookmark for URL: {url.strip()}")

        # get existing bookmark
        rate_limit()
        result = pinboard_client.posts.get(url=url.strip())
        posts = result.get('posts', [])

        if not posts:
            return {'error': f"no bookmark found for URL: {url.strip()}", 'success': False}

        if len(posts) > 1:
            logger.warning(f"multiple bookmarks found for URL: {url.strip()}, using first one")

        bookmark = posts[0]
        logger.debug(f"successfully retrieved bookmark: {bookmark.description}")

        # track what we're updating for logging
        updates = []

        # update title (maps to bookmark.description in Pinboard API)
        if title is not None:
            old_title = bookmark.description
            bookmark.description = title.strip()
            updates.append(f"title: '{old_title}' -> '{bookmark.description}'")

        # update description (maps to bookmark.extended in Pinboard API)
        if description is not None:
            old_desc = bookmark.extended
            bookmark.extended = description.strip()
            updates.append(f"description: '{old_desc}' -> '{bookmark.extended}'")

        # update tags
        if tags is not None:
            old_tags = bookmark.tags
            # parse tags and clean them
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()] if tags else []
            bookmark.tags = ' '.join(tag_list)  # pinboard expects space-separated tags
            updates.append(f"tags: '{old_tags}' -> '{bookmark.tags}'")

        # update privacy setting
        if private is not None:
            old_shared = bookmark.shared
            bookmark.shared = not private  # pinboard uses 'shared', we use 'private'
            updates.append(f"private: {old_shared} -> {not bookmark.shared}")

        # update to-read status
        if toread is not None:
            old_toread = bookmark.toread
            bookmark.toread = 'yes' if toread else 'no'  # pinboard expects 'yes'/'no'
            updates.append(f"toread: '{old_toread}' -> '{bookmark.toread}'")

        # validate that at least one update was provided
        if not updates:
            return {'error': 'no updates provided. At least one field (title, description, tags, private, toread) must be specified.', 'success': False}

        logger.info(f"updating bookmark {url}: {', '.join(updates)}")

        # save the bookmark
        rate_limit()
        bookmark.save()

        # build response

        response = {
            'bookmark': format_bookmark_response(bookmark),
            'updates_applied': updates,
            'success': True
        }

        logger.info(f'successfully updated bookmark: {url}')
        return response

    except Exception as e:
        logger.error(f'error updating bookmark {url}: {e}')
        return {'error': str(e), 'success': False}


@mcp.tool
def add_bookmark(
    url: str,
    title: str,
    description: Optional[str] = None,
    tags: Optional[str] = None,
    private: bool = False,
    toread: bool = False
) -> Dict[str, Any]:
    '''
    create a new bookmark in pinboard.

    args:
        url: the web address to bookmark (required)
        title: the bookmark title/name (required)
        description: extended description or notes (optional)
        tags: comma-separated tags (optional)
        private: set bookmark privacy - true for private, false for public (default: false)
        toread: mark as to-read - true/false (default: false)

    returns:
        dictionary containing the created bookmark data and metadata
    '''
    try:
        # basic validation
        if not url or not url.strip():
            return {'error': 'url is required', 'success': False}
        if not title or not title.strip():
            return {'error': 'title is required', 'success': False}

        # prepare parameters
        url = url.strip()
        title = title.strip()
        extended_desc = description.strip() if description else ''

        # parse tags
        tag_list = []
        if tags:
            tag_list = [tag.strip().lower() for tag in tags.split(',') if tag.strip()]

        pinboard_client = get_pinboard_client()

        # build API parameters for posts.add()
        api_params = {
            'url': url,
            'description': title,  # pinboard API uses 'description' for title
            'extended': extended_desc,  # extended description
            'tags': tag_list,  # pinboard.py accepts list format
            'shared': not private,  # pinboard uses 'shared', we use 'private'
            'toread': toread
        }

        logger.info(f"adding bookmark: {title} -> {url}")

        # create the bookmark
        rate_limit()
        result = pinboard_client.posts.add(**api_params)

        if result is not True:
            logger.error(f"unexpected response from Pinboard API: {result}")
            return {'error': 'failed to create bookmark - unexpected API response', 'success': False}

        # build response

        response = {
            'bookmark': {
                'url': url,
                'title': title,
                'description': extended_desc,
                'tags': ' '.join(tag_list) if tag_list else '',
                'time': None,
                'private': private
            },
            'message': 'bookmark created successfully',
            'success': True
        }

        logger.info(f"successfully created bookmark: {title}")
        return response

    except Exception as e:
        logger.error(f"error creating bookmark: {e}")
        return {'error': str(e), 'success': False}
