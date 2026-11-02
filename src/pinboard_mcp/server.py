'''
pinboard mcp server with fastmcp tools.

provides mcp tools for interacting with pinboard bookmarks including
retrieval, creation, updating, and tag management.
'''

import argparse
import logging
import os
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from pinboard_mcp.pinboard_client import PinboardClient, PinboardError
from pinboard_mcp.schema import (
    create_error_response,
    create_success_response,
    parse_tags,
    validate_date_range,
)

logger = logging.getLogger(__name__)

_HELP = '''
environment variables:
  PINBOARD_TOKEN   Pinboard API token (format: username:TOKEN)
  LOG_LEVEL        Logging level (debug or info, default: info)
'''

# module-level client singleton
_client: Optional[PinboardClient] = None


def parse_args() -> argparse.Namespace:
    '''parse command line arguments.'''
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


def get_client() -> PinboardClient:
    '''get the pinboard client singleton.'''
    if _client is None:
        raise RuntimeError('Pinboard client not initialized')
    return _client


def format_error(error: Exception) -> Dict[str, Any]:
    '''format an exception as an error response.'''
    return create_error_response(str(error))


# mcp server

mcp = FastMCP('pinboard MCP')


# bookmark tools

@mcp.tool()
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
            return create_error_response('limit must be between 1 and 500')

        parsed_start, parsed_end = validate_date_range(start_date, end_date)
        tag_list = parse_tags(tags)

        with get_client() as client:
            bookmarks = client.get_bookmarks(
                start_date=parsed_start,
                end_date=parsed_end,
                tags=tag_list,
                limit=limit
            )

        formatted_bookmarks = [b.to_dict() for b in bookmarks]

        filters_applied: Dict[str, Any] = {'limit': limit}
        if parsed_start or parsed_end:
            filters_applied['date_range'] = {
                'start': parsed_start.isoformat() if parsed_start else None,
                'end': parsed_end.isoformat() if parsed_end else None
            }
        if tag_list:
            filters_applied['tags'] = ','.join(tag_list)

        return create_success_response(
            count=len(formatted_bookmarks),
            bookmarks=formatted_bookmarks,
            filters_applied=filters_applied
        )

    except ValueError as e:
        logger.error(f'validation error: {e}')
        return create_error_response(str(e))
    except PinboardError as e:
        logger.error(f'pinboard error retrieving bookmarks: {e}')
        return format_error(e)
    except Exception as e:
        logger.exception(f'unexpected error retrieving bookmarks: {e}')
        return create_error_response(f'Unexpected error: {e}')


@mcp.tool()
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
            return create_error_response('url is required')
        if not title or not title.strip():
            return create_error_response('title is required')

        url = url.strip()
        title = title.strip()
        desc = description.strip() if description else ''
        tag_list = parse_tags(tags)

        with get_client() as client:
            bookmark = client.add_bookmark(
                url=url,
                title=title,
                description=desc,
                tags=tag_list,
                private=private,
                toread=toread
            )

        return create_success_response(
            bookmark=bookmark.to_dict(),
            message='bookmark created successfully'
        )

    except PinboardError as e:
        logger.error(f'pinboard error creating bookmark: {e}')
        return format_error(e)
    except Exception as e:
        logger.exception(f'unexpected error creating bookmark: {e}')
        return create_error_response(f'Unexpected error: {e}')


@mcp.tool()
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
            return create_error_response('url is required and cannot be empty')

        url = url.strip()
        tag_list = parse_tags(tags) if tags is not None else None
        title_clean = title.strip() if title is not None else None
        desc_clean = description.strip() if description is not None else None

        with get_client() as client:
            bookmark, updates = client.update_bookmark(
                url=url,
                title=title_clean,
                description=desc_clean,
                tags=tag_list,
                private=private,
                toread=toread
            )

        return create_success_response(
            bookmark=bookmark.to_dict(),
            updates_applied=updates
        )

    except PinboardError as e:
        logger.error(f'pinboard error updating bookmark: {e}')
        return format_error(e)
    except Exception as e:
        logger.exception(f'unexpected error updating bookmark: {e}')
        return create_error_response(f'Unexpected error: {e}')


# tag tools

@mcp.tool()
def get_tags() -> Dict[str, Any]:
    '''
    retrieve all tags from pinboard with usage counts.

    returns:
        dictionary containing tags and metadata
    '''
    try:
        with get_client() as client:
            tags = client.get_tags()

        formatted_tags = [t.to_dict() for t in tags]

        return create_success_response(
            count=len(formatted_tags),
            tags=formatted_tags
        )

    except PinboardError as e:
        logger.error(f'pinboard error retrieving tags: {e}')
        return format_error(e)
    except Exception as e:
        logger.exception(f'unexpected error retrieving tags: {e}')
        return create_error_response(f'Unexpected error: {e}')


@mcp.tool()
def rename_tag(old_tag: str, new_tag: str) -> Dict[str, Any]:
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
            return create_error_response('old_tag is required and cannot be empty')
        if not new_tag or not new_tag.strip():
            return create_error_response('new_tag is required and cannot be empty')

        old_normalized = old_tag.strip().lower()
        new_normalized = new_tag.strip().lower()

        with get_client() as client:
            client.rename_tag(old_normalized, new_normalized)

        return create_success_response(
            old_tag=old_normalized,
            new_tag=new_normalized,
            message=f"successfully renamed tag '{old_normalized}' to '{new_normalized}'"
        )

    except PinboardError as e:
        logger.error(f'pinboard error renaming tag: {e}')
        return format_error(e)
    except Exception as e:
        logger.exception(f'unexpected error renaming tag: {e}')
        return create_error_response(f'Unexpected error: {e}')


@mcp.tool()
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
            return create_error_response('url is required and cannot be empty')

        url = url.strip()

        with get_client() as client:
            suggestions = client.suggest_tags(url)

        return create_success_response(
            url=url,
            popular=suggestions['popular'],
            recommended=suggestions['recommended'],
            popular_count=len(suggestions['popular']),
            recommended_count=len(suggestions['recommended'])
        )

    except PinboardError as e:
        logger.error(f'pinboard error getting tag suggestions: {e}')
        return format_error(e)
    except Exception as e:
        logger.exception(f'unexpected error getting tag suggestions: {e}')
        return create_error_response(f'Unexpected error: {e}')


# entry point

def run():
    '''main entry point for the pinboard mcp server.'''
    global _client

    logging.basicConfig(
        level=logging.DEBUG if os.getenv('LOG_LEVEL', 'info').lower() == 'debug' else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

    args = parse_args()

    if not args.token:
        logger.error('token is required (--token or PINBOARD_TOKEN env var)')
        raise SystemExit(1)

    logger.info('starting pinboard mcp server')

    try:
        # initialize and test client
        _client = PinboardClient(args.token)

        with _client as client:
            client.test_connection()

        mcp.run()

    except KeyboardInterrupt:
        logger.info('server shutdown requested')

    except PinboardError as e:
        logger.error(f'pinboard error: {e}')
        raise SystemExit(1)

    except Exception as e:
        logger.error(f'server error: {e}')
        raise SystemExit(1)


if __name__ == '__main__':
    run()
