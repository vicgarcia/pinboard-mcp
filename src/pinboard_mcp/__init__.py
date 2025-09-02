import os
from .pinboard import get_pinboard_client, rate_limit
from .server import mcp

import logging
logger = logging.getLogger(__name__)


def main():

    logging.basicConfig(
        level=logging.DEBUG if os.getenv('LOG_LEVEL', 'info').lower() == 'debug' else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

    logger.info('starting Pinboard MCP server')

    try:
        if not os.getenv('PINBOARD_TOKEN'):
            logger.error('PINBOARD_TOKEN environment variable is required')
            raise SystemExit(1)

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
