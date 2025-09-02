import os
import time
from typing import Dict, Any
import pinboard

import logging
logger = logging.getLogger(__name__)


RATE_LIMIT_SECONDS = 3.0


def get_pinboard_client():
    ''' get authenticated pinboard client '''
    token = os.getenv('PINBOARD_TOKEN')
    if not token:
        raise ValueError('PINBOARD_TOKEN environment variable is required')
    return pinboard.Pinboard(token)


last_api_call = 0.0

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
