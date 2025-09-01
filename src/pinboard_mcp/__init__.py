import os
from .pinboard import get_pinboard_client, rate_limit

import logging
logger = logging.getLogger(__name__)

__version__ = "0.1.0"
__author__ = "Pinboard MCP Team"
__description__ = "MCP server for read-only access to Pinboard.in bookmarks"


def setup_logging():
    ''' configure logging for the mcp server. '''
    return logging.getLogger(__name__)


def main():
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )

    logger.info("Starting Pinboard MCP Server")

    try:
        # validate environment
        if not os.getenv("PINBOARD_TOKEN"):
            logger.error("PINBOARD_TOKEN environment variable is required")
            raise SystemExit(1)

        # test pinboard connection
        try:
            pb = get_pinboard_client()
            rate_limit()
            last_update = pb.posts.update()
            logger.info(f"Successfully connected to Pinboard. Last update: {last_update}")
        except Exception as e:
            logger.error(f"Failed to connect to Pinboard: {e}")
            raise SystemExit(1)

        # import and run the server
        from .server import mcp
        mcp.run()

    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise SystemExit(1)
