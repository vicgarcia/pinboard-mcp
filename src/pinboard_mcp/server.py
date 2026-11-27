'''
pinboard mcp server with fastmcp tools.

provides mcp tools for interacting with pinboard bookmarks including
retrieval, creation, updating, and tag management.
'''

import argparse
import logging
import os
from typing import Annotated, Any, Dict, List, Optional

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import Field

from pinboard_mcp.pinboard_client import PinboardClient, PinboardError
from pinboard_mcp.schema import (
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


def tool_error(message: str) -> ToolError:
    '''a tool error to raise, so the client sees the call failed.'''
    return ToolError(message)


# mcp server

# guidance sent to clients as the server instructions

INSTRUCTIONS = '''
these tools work on the user's pinboard bookmarks.

- bookmarks are private by default; pass private=false to add_bookmark only when the user
  asks for a public bookmark.
- "read later" or "to read" means the bookmark's toread flag: pass toread=true when the
  user saves a link to read later, and clear it with update_bookmark once they've read it.
  their read later list is the bookmarks from get_bookmarks with toread true.
- when the user asks about their bookmarks, don't read the whole list back: share a few
  high-value examples, then answer questions from the rest. get_bookmarks filters by tag
  and date; there is no keyword search.
- when adding a bookmark, tag it the way the user already does: check get_tags (and
  suggest_tags for the url) rather than inventing new tags.
- add_bookmark fails if the url is already bookmarked; use update_bookmark to change it.
- rename_tag changes every bookmark with that tag, and renaming onto a tag that already
  exists combines the two. confirm the old and new names with the user before calling it.
'''

# tool annotations: whether a tool only reads, and whether a write can overwrite or remove
# existing data. every tool works on the user's own bookmarks, so none is open world.

READ_ONLY = ToolAnnotations(readOnlyHint=True, openWorldHint=False)
ADDS = ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=False)
CHANGES = ToolAnnotations(readOnlyHint=False, destructiveHint=True, openWorldHint=False)

# argument descriptions shared by several tools

Url = Annotated[str, Field(description='the full URL, including https://')]
Tags = Annotated[Optional[str], Field(description='comma-separated tags, e.g. "recipes,bread"')]

mcp = FastMCP('pinboard MCP', instructions=INSTRUCTIONS)


# bookmark tools

@mcp.tool(annotations=READ_ONLY)
def get_bookmarks(
    start_date: Annotated[Optional[str], Field(description='the earliest date, as YYYY-MM-DD')] = None,
    end_date: Annotated[Optional[str], Field(description='the latest date, as YYYY-MM-DD')] = None,
    tags: Annotated[Optional[str], Field(
        description='comma-separated tags, e.g. "recipes,bread"; up to three, and a bookmark '
                    'must have all of them'
    )] = None,
    limit: Annotated[int, Field(description='how many to fetch, from 1 to 500')] = 200,
) -> Dict[str, Any]:
    '''
    List the user's bookmarks, newest first, filtered by tag and date.

    There is no keyword search: narrow by tag (get_tags lists them) and date, then look
    through the results. Don't read the whole list back to the user; share a few
    high-value examples, then answer questions from the rest.

    Returns a dictionary with the bookmarks, each with its url, title, description, tags,
    time and toread flag, and the filters applied.
    '''
    try:
        if limit <= 0 or limit > 500:
            raise tool_error('limit must be between 1 and 500')

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
        raise tool_error(str(e))
    except PinboardError as e:
        logger.error(f'pinboard error retrieving bookmarks: {e}')
        raise tool_error(str(e))
    except ToolError:
        raise  # already a tool error with its own message
    except Exception as e:
        logger.exception(f'unexpected error retrieving bookmarks: {e}')
        raise tool_error(f'Unexpected error: {e}')


@mcp.tool(annotations=ADDS)
def add_bookmark(
    url: Url,
    title: Annotated[str, Field(description='the bookmark title')],
    description: Annotated[Optional[str], Field(description='notes on the bookmark')] = None,
    tags: Annotated[Optional[str], Field(
        description='comma-separated tags, e.g. "recipes,bread"; prefer tags the user already has'
    )] = None,
    private: Annotated[bool, Field(
        description='false only when the user asks for a public bookmark'
    )] = True,
    toread: Annotated[bool, Field(
        description='true when the user saves it to read later'
    )] = False,
) -> Dict[str, Any]:
    '''
    Save a new bookmark. Bookmarks are private unless private is false.

    Fails if the URL is already bookmarked; use update_bookmark to change that one. Tag it
    the way the user already does: check get_tags, and suggest_tags for the URL, rather
    than inventing new tags.

    Returns a dictionary with the created bookmark.
    '''
    try:
        if not url or not url.strip():
            raise tool_error('url is required')
        if not title or not title.strip():
            raise tool_error('title is required')

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
        raise tool_error(str(e))
    except ToolError:
        raise  # already a tool error with its own message
    except Exception as e:
        logger.exception(f'unexpected error creating bookmark: {e}')
        raise tool_error(f'Unexpected error: {e}')


@mcp.tool(annotations=CHANGES)
def update_bookmark(
    url: Annotated[str, Field(description='the URL of the bookmark, from get_bookmarks')],
    title: Annotated[Optional[str], Field(description='the new title')] = None,
    description: Annotated[Optional[str], Field(
        description='new notes, replacing the existing notes'
    )] = None,
    tags: Annotated[Optional[str], Field(
        description='comma-separated tags, replacing all existing tags'
    )] = None,
    private: Annotated[Optional[bool], Field(
        description='true for private, false for public; the current visibility is kept if left out'
    )] = None,
    toread: Annotated[Optional[bool], Field(
        description='true to mark it as to read, false to clear that'
    )] = None,
) -> Dict[str, Any]:
    '''
    Change a bookmark, found by its URL.

    Only the arguments given change; new values replace the old ones.

    Returns a dictionary with the updated bookmark and what changed.
    '''
    try:
        if not url or not url.strip():
            raise tool_error('url is required and cannot be empty')

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
        raise tool_error(str(e))
    except ToolError:
        raise  # already a tool error with its own message
    except Exception as e:
        logger.exception(f'unexpected error updating bookmark: {e}')
        raise tool_error(f'Unexpected error: {e}')


# tag tools

@mcp.tool(annotations=READ_ONLY)
def get_tags() -> Dict[str, Any]:
    '''
    List every tag the user has, with how many bookmarks use it, most used first.

    Use it to pick existing tags when adding or updating a bookmark, to filter
    get_bookmarks, and to answer what the user bookmarks most.

    Returns a dictionary with the tags, each with its tag and count.
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
        raise tool_error(str(e))
    except ToolError:
        raise  # already a tool error with its own message
    except Exception as e:
        logger.exception(f'unexpected error retrieving tags: {e}')
        raise tool_error(f'Unexpected error: {e}')


@mcp.tool(annotations=CHANGES)
def rename_tag(
    old_tag: Annotated[str, Field(description='the tag as it is now, from get_tags')],
    new_tag: Annotated[str, Field(description='the new name')],
) -> Dict[str, Any]:
    '''
    Rename a tag on every bookmark that has it.

    Confirm the old and new names with the user first: renaming onto a tag that already
    exists combines the two.

    Returns a dictionary with the result of the rename.
    '''
    try:
        if not old_tag or not old_tag.strip():
            raise tool_error('old_tag is required and cannot be empty')
        if not new_tag or not new_tag.strip():
            raise tool_error('new_tag is required and cannot be empty')

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
        raise tool_error(str(e))
    except ToolError:
        raise  # already a tool error with its own message
    except Exception as e:
        logger.exception(f'unexpected error renaming tag: {e}')
        raise tool_error(f'Unexpected error: {e}')


@mcp.tool(annotations=READ_ONLY)
def suggest_tags(url: Url) -> Dict[str, Any]:
    '''
    Get Pinboard's suggested tags for a URL: popular ones across Pinboard, and recommended
    ones the user has used before.

    Returns a dictionary with the popular and recommended tags.
    '''
    try:
        if not url or not url.strip():
            raise tool_error('url is required and cannot be empty')

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
        raise tool_error(str(e))
    except ToolError:
        raise  # already a tool error with its own message
    except Exception as e:
        logger.exception(f'unexpected error getting tag suggestions: {e}')
        raise tool_error(f'Unexpected error: {e}')


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
