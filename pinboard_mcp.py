import argparse
import logging
import os
import time
from typing import Optional, Dict, Any, List
from dateutil import parser as date_parser
import pinboard
from fastmcp import FastMCP

logger = logging.getLogger(__name__)

_HELP = '''
environment variables:
  PINBOARD_TOKEN   Pinboard API token (format: username:TOKEN)
'''

# module-level token set during run()
_token: Optional[str] = None


# arg parsing

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='pinboard-mcp',
        description='Pinboard MCP server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_HELP
    )
    parser.add_argument(
        '--token',
        default=os.getenv('PINBOARD_TOKEN'),
        metavar='TOKEN',
        help='Pinboard API token (or PINBOARD_TOKEN env var)'
    )
    return parser.parse_args()


# validation utilities

def validate_date_range(start_date: Optional[str], end_date: Optional[str]) -> tuple:
    ''' validate and parse date range with 90-day maximum limit. '''
    parsed_start = None
    parsed_end = None

    if start_date:
        try:
            parsed_start = date_parser.parse(start_date).date()
        except (ValueError, TypeError):
            raise ValueError(f"Invalid start_date format: {start_date}. Use YYYY-MM-DD format.")

    if end_date:
        try:
            parsed_end = date_parser.parse(end_date).date()
        except (ValueError, TypeError):
            raise ValueError(f"Invalid end_date format: {end_date}. Use YYYY-MM-DD format.")

    if parsed_start and parsed_end and parsed_start > parsed_end:
        raise ValueError("start_date must be before end_date")

    if parsed_start and parsed_end:
        date_diff = (parsed_end - parsed_start).days
        if date_diff > 90:
            raise ValueError(f"Date range cannot exceed 90 days. Current range: {date_diff} days")

    return parsed_start, parsed_end


# pinboard api client + formatters

RATE_LIMIT_SECONDS = 3.0
last_api_call = 0.0


def get_pinboard_client():
    ''' get authenticated pinboard client '''
    if not _token:
        raise ValueError('pinboard token is required')
    return pinboard.Pinboard(_token)


def rate_limit():
    ''' enforce rate limiting for pinboard api calls '''
    global last_api_call
    current_time = time.time()
    time_since_last_call = current_time - last_api_call

    if time_since_last_call < RATE_LIMIT_SECONDS:
        sleep_time = RATE_LIMIT_SECONDS - time_since_last_call
        logger.debug(f'rate limiting: sleeping for {sleep_time:.2f} seconds')
        time.sleep(sleep_time)

    last_api_call = time.time()


def format_bookmark_response(bookmark) -> Dict[str, Any]:
    ''' format a pinboard bookmark for response '''
    time_str = None
    try:
        if bookmark.time:
            time_str = bookmark.time.isoformat()
    except Exception:
        pass
    return {
        'url': bookmark.url,
        'title': bookmark.description,
        'description': bookmark.extended,
        'tags': bookmark.tags,
        'time': time_str,
        'private': not bookmark.shared,
    }


def parse_tags(tags_str: Optional[str]) -> List[str]:
    ''' parse comma-separated tags string into cleaned list '''
    if not tags_str:
        return []
    return [tag.strip().lower() for tag in tags_str.split(',') if tag.strip()]


def format_tags_response(tags_raw: Dict[str, int]) -> List[Dict[str, Any]]:
    ''' format tags dictionary into sorted list with tag name and count '''
    formatted_tags = [
        {'tag': tag_name, 'count': count}
        for tag_name, count in tags_raw.items()
    ]
    formatted_tags.sort(key=lambda x: (-x['count'], x['tag']))
    return formatted_tags


def normalize_tag(tag: str) -> str:
    ''' normalize a single tag (strip whitespace and lowercase) '''
    return tag.strip().lower()


def format_suggest_response(suggestions: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    ''' format tag suggestions into popular and recommended lists '''
    popular = []
    recommended = []

    for suggestion in suggestions:
        if suggestion.get('popular'):
            popular.extend(suggestion['popular'])
        if suggestion.get('recommended'):
            recommended.extend(suggestion['recommended'])

    return {
        'popular': popular,
        'recommended': recommended
    }


# mcp server

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
        limit: maximum bookmarks to return (default: 200, max: 500)

    returns:
        dictionary containing bookmarks and metadata
    '''
    try:
        if limit <= 0 or limit > 500:
            return {'error': 'limit must be between 1 and 500', 'success': False}

        parsed_start, parsed_end = validate_date_range(start_date, end_date)

        tag_list = parse_tags(tags)

        pinboard_client = get_pinboard_client()

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

        rate_limit()
        bookmarks_raw = pinboard_client.posts.all(**api_params)
        formatted_bookmarks = [format_bookmark_response(bookmark) for bookmark in bookmarks_raw]

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

        rate_limit()
        result = pinboard_client.posts.get(url=url.strip())
        posts = result.get('posts', [])

        if not posts:
            return {'error': f"no bookmark found for URL: {url.strip()}", 'success': False}

        if len(posts) > 1:
            logger.warning(f"multiple bookmarks found for URL: {url.strip()}, using first one")

        bookmark = posts[0]
        logger.debug(f"successfully retrieved bookmark {bookmark.description}")

        updates = []

        if title is not None:
            old_title = bookmark.description
            bookmark.description = title.strip()
            updates.append(f"title: '{old_title}' -> '{bookmark.description}'")

        if description is not None:
            old_desc = bookmark.extended
            bookmark.extended = description.strip()
            updates.append(f"description: '{old_desc}' -> '{bookmark.extended}'")

        if tags is not None:
            old_tags = bookmark.tags
            tag_list = parse_tags(tags)
            bookmark.tags = ' '.join(tag_list)
            updates.append(f"tags: '{old_tags}' -> '{bookmark.tags}'")

        if private is not None:
            old_shared = bookmark.shared
            bookmark.shared = not private
            updates.append(f"private: {old_shared} -> {not bookmark.shared}")

        if toread is not None:
            old_toread = bookmark.toread
            bookmark.toread = 'yes' if toread else 'no'
            updates.append(f"toread: '{old_toread}' -> '{bookmark.toread}'")

        if not updates:
            return {'error': 'no updates provided. At least one field (title, description, tags, private, toread) must be specified.', 'success': False}

        logger.info(f"updating bookmark {url}: {', '.join(updates)}")

        rate_limit()
        bookmark.save()

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
        if not url or not url.strip():
            return {'error': 'url is required', 'success': False}
        if not title or not title.strip():
            return {'error': 'title is required', 'success': False}

        url = url.strip()
        title = title.strip()
        extended_desc = description.strip() if description else ''

        tag_list = parse_tags(tags)

        pinboard_client = get_pinboard_client()

        api_params = {
            'url': url,
            'description': title,
            'extended': extended_desc,
            'tags': tag_list,
            'shared': not private,
            'toread': toread
        }

        logger.info(f"adding bookmark: {title} -> {url}")

        rate_limit()
        result = pinboard_client.posts.add(**api_params)

        if result is not True:
            logger.error(f"unexpected response from Pinboard API: {result}")
            return {'error': 'failed to create bookmark - unexpected API response', 'success': False}

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

        logger.info(f"successfully created bookmark {title}")
        return response

    except Exception as e:
        logger.error(f"error creating bookmark: {e}")
        return {'error': str(e), 'success': False}


@mcp.tool
def get_tags() -> Dict[str, Any]:
    '''
    retrieve all tags from pinboard with usage counts.

    returns:
        dictionary containing tags and metadata
    '''
    try:
        pinboard_client = get_pinboard_client()

        logger.info('fetching tags from Pinboard')

        rate_limit()
        tags_raw = pinboard_client.tags.get()

        formatted_tags = format_tags_response(tags_raw)

        response = {
            'count': len(formatted_tags),
            'tags': formatted_tags,
            'success': True
        }

        logger.info(f'successfully retrieved {len(formatted_tags)} tags')
        return response

    except Exception as e:
        logger.error(f'error retrieving tags: {e}')
        return {'error': str(e), 'success': False}


@mcp.tool
def rename_tag(
    old_tag: str,
    new_tag: str
) -> Dict[str, Any]:
    '''
    rename a tag across all bookmarks.

    args:
        old_tag: the existing tag name to rename (required)
        new_tag: the new tag name (required)

    returns:
        dictionary containing rename operation result and metadata
    '''
    try:
        if not old_tag or not old_tag.strip():
            return {'error': 'old_tag is required and cannot be empty', 'success': False}
        if not new_tag or not new_tag.strip():
            return {'error': 'new_tag is required and cannot be empty', 'success': False}

        old_tag_normalized = normalize_tag(old_tag)
        new_tag_normalized = normalize_tag(new_tag)

        if old_tag_normalized == new_tag_normalized:
            return {'error': 'old_tag and new_tag cannot be the same', 'success': False}

        pinboard_client = get_pinboard_client()

        logger.info(f'renaming tag: \'{old_tag_normalized}\' -> \'{new_tag_normalized}\'')

        rate_limit()
        result = pinboard_client.tags.rename(old=old_tag_normalized, new=new_tag_normalized)

        if result is not True:
            logger.error(f'unexpected response from Pinboard API: {result}')
            return {'error': 'failed to rename tag - unexpected API response', 'success': False}

        response = {
            'old_tag': old_tag_normalized,
            'new_tag': new_tag_normalized,
            'message': f'successfully renamed tag \'{old_tag_normalized}\' to \'{new_tag_normalized}\'',
            'success': True
        }

        logger.info(f'successfully renamed tag: \'{old_tag_normalized}\' -> \'{new_tag_normalized}\'')
        return response

    except Exception as e:
        logger.error(f'error renaming tag: {e}')
        return {'error': str(e), 'success': False}


@mcp.tool
def suggest_tags(url: str) -> Dict[str, Any]:
    '''
    get suggested tags for a URL from pinboard.

    args:
        url: the web address to get tag suggestions for (required)

    returns:
        dictionary containing popular and recommended tag suggestions
    '''
    try:
        if not url or not url.strip():
            return {'error': 'url is required and cannot be empty', 'success': False}

        url = url.strip()
        pinboard_client = get_pinboard_client()

        logger.info(f'fetching tag suggestions for URL: {url}')

        rate_limit()
        suggestions = pinboard_client.posts.suggest(url=url)

        formatted = format_suggest_response(suggestions)

        response = {
            'url': url,
            'popular': formatted['popular'],
            'recommended': formatted['recommended'],
            'popular_count': len(formatted['popular']),
            'recommended_count': len(formatted['recommended']),
            'success': True
        }

        logger.info(f'successfully retrieved {len(formatted["popular"])} popular and {len(formatted["recommended"])} recommended tags for {url}')
        return response

    except Exception as e:
        logger.error(f'error getting tag suggestions for {url}: {e}')
        return {'error': str(e), 'success': False}


def run():
    logging.basicConfig(
        level=logging.DEBUG if os.getenv('LOG_LEVEL', 'info').lower() == 'debug' else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

    args = parse_args()

    if not args.token:
        logger.error('token is required (--token or PINBOARD_TOKEN env var)')
        raise SystemExit(1)

    global _token
    _token = args.token

    logger.info('starting Pinboard MCP server')

    try:
        try:
            pinboard_client = get_pinboard_client()

            rate_limit()
            pinboard_client.posts.update()
            logger.info(f'successfully connected to Pinboard')

        except Exception as e:
            logger.error(f'failed to connect to Pinboard: {e}')
            raise SystemExit(1)

        mcp.run()

    except KeyboardInterrupt:
        logger.info('server shutdown requested')

    except Exception as e:
        logger.error(f'server error: {e}')
        raise SystemExit(1)


if __name__ == '__main__':
    run()
