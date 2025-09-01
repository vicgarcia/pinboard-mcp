#!/usr/bin/env python3
'''
 Pinboard MCP Server - Read-only access to Pinboard.in bookmarks
'''

import logging
from typing import Optional, Dict, Any
from fastmcp import FastMCP

from .pinboard import get_pinboard_client, rate_limit, format_bookmark_response
from .utils import validate_date_range

logger = logging.getLogger(__name__)

# create fastmcp server
mcp = FastMCP("Pinboard MCP Server")

@mcp.tool
def get_bookmarks(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    tags: Optional[str] = None,
    limit: int = 200
) -> Dict[str, Any]:
    '''
    retrieve bookmarks from pinboard within a specified date range.

    args:
        start_date: start date in yyyy-mm-dd format (optional)
        end_date: end date in yyyy-mm-dd format (optional)
        tags: comma-separated tags to filter by (optional)
        limit: maximum bookmarks to return (default: 100, max: 500)

    returns:
        dictionary containing bookmarks and metadata
    '''
    try:
        # validate inputs
        if limit <= 0 or limit > 500:
            return {"error": "limit must be between 1 and 500", "success": False}

        # validate and parse date range
        parsed_start, parsed_end = validate_date_range(start_date, end_date)

        # parse tags
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []

        # get pinboard client
        pb = get_pinboard_client()

        # build api parameters for posts.all()
        api_params = {
            "results": limit
        }
        if tag_list:
            api_params["tag"] = tag_list
        if parsed_start:
            api_params["fromdt"] = parsed_start
        if parsed_end:
            api_params["todt"] = parsed_end

        logger.info(f"Fetching bookmarks with params: {api_params}")

        # fetch bookmarks from pinboard
        rate_limit()
        bookmarks_raw = pb.posts.all(**api_params)

        # format bookmarks for response
        formatted_bookmarks = [format_bookmark_response(bookmark) for bookmark in bookmarks_raw]

        # build response
        response = {
            "count": len(formatted_bookmarks),
            "bookmarks": formatted_bookmarks,
            "success": True,
            "filters_applied": {}
        }

        # add filters to response

        response["filters_applied"]["limit"] = limit

        if parsed_start or parsed_end:
            response["filters_applied"]["date_range"] = {
                "start": parsed_start.isoformat() if parsed_start else None,
                "end": parsed_end.isoformat() if parsed_end else None
            }

        if tag_list:
            response["filters_applied"]["tags"] = ",".join(tag_list)

        logger.info(f"Successfully retrieved {len(formatted_bookmarks)} bookmarks")
        return response

    except Exception as e:
        logger.error(f"Error retrieving bookmarks: {e}")
        return {"error": str(e), "success": False}


@mcp.tool
def get_tags() -> Dict[str, Any]:
    '''
    retrieve all tags from pinboard with usage counts.

    returns:
        dictionary containing tags and metadata
    '''
    try:
        pb = get_pinboard_client()

        logger.info("Fetching tags from pinboard")

        # fetch tags from pinboard
        rate_limit()
        tags_raw = pb.tags.get()

        # format tags for response - tags_raw is a dict with tag names as keys and counts as values
        formatted_tags = [
            {"tag": tag_name, "count": count}
            for tag_name, count in tags_raw.items()
        ]

        # sort by count descending, then by tag name
        formatted_tags.sort(key=lambda x: (-x["count"], x["tag"]))

        # build response
        response = {
            "count": len(formatted_tags),
            "tags": formatted_tags,
            "success": True
        }

        logger.info(f"Successfully retrieved {len(formatted_tags)} tags")
        return response

    except Exception as e:
        logger.error(f"Error retrieving tags: {e}")
        return {"error": str(e), "success": False}
