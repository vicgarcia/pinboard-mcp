'''
pinboard api client with rate limiting.

provides a context manager interface for all pinboard operations.
'''

import logging
import time
from typing import Any, Dict, List, Optional

import pinboard

from pinboard_mcp.schema import (
    Bookmark,
    TagInfo,
    format_suggest_response,
    format_tags_response,
    normalize_tag,
    parse_tags,
)

logger = logging.getLogger(__name__)


class PinboardError(Exception):
    '''exception raised for pinboard operation errors.'''

    def __init__(self, message: str, operation: Optional[str] = None):
        self.message = message
        self.operation = operation
        super().__init__(message)

    def __str__(self) -> str:
        if self.operation:
            return f'{self.operation}: {self.message}'
        return self.message


class PinboardClient:
    '''
    pinboard api client with built-in rate limiting.

    usage:
        with PinboardClient(token) as client:
            bookmarks = client.get_bookmarks(limit=100)
            client.add_bookmark(url, title)
    '''

    RATE_LIMIT_SECONDS = 3.0

    def __init__(self, token: str):
        '''
        initialize the pinboard client.

        args:
            token: pinboard api token (format: username:TOKEN)
        '''
        self._token = token
        self._client: Optional[pinboard.Pinboard] = None
        self._last_api_call: float = 0.0
        logger.debug('pinboard client initialized')

    def __enter__(self) -> 'PinboardClient':
        '''enter context manager.'''
        self._client = pinboard.Pinboard(self._token)
        logger.debug('pinboard client context entered')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        '''exit context manager.'''
        self._client = None
        logger.debug('pinboard client context exited')

    def _rate_limit(self) -> None:
        '''enforce rate limiting for pinboard api calls.'''
        current_time = time.time()
        time_since_last_call = current_time - self._last_api_call

        if time_since_last_call < self.RATE_LIMIT_SECONDS:
            sleep_time = self.RATE_LIMIT_SECONDS - time_since_last_call
            logger.debug(f'rate limiting: sleeping for {sleep_time:.2f} seconds')
            time.sleep(sleep_time)

        self._last_api_call = time.time()

    def _ensure_client(self) -> pinboard.Pinboard:
        '''ensure client is initialized.'''
        if self._client is None:
            raise PinboardError('Client not initialized. Use within context manager.')
        return self._client

    # connection test

    def test_connection(self) -> bool:
        '''test connection to pinboard api.'''
        client = self._ensure_client()
        self._rate_limit()
        try:
            client.posts.update()
            logger.info('successfully connected to pinboard')
            return True
        except Exception as e:
            logger.error(f'failed to connect to pinboard: {e}')
            raise PinboardError(f'Connection failed: {e}', 'test_connection')

    # bookmark operations

    def get_bookmarks(
        self,
        start_date=None,
        end_date=None,
        tags: Optional[List[str]] = None,
        limit: int = 200
    ) -> List[Bookmark]:
        '''
        retrieve bookmarks with optional filters.

        args:
            start_date: filter by start date
            end_date: filter by end date
            tags: filter by tags
            limit: maximum bookmarks to return (max 500)

        returns:
            list of Bookmark objects
        '''
        client = self._ensure_client()

        api_params: Dict[str, Any] = {'results': limit}
        if tags:
            api_params['tag'] = tags
        if start_date:
            api_params['fromdt'] = start_date
        if end_date:
            api_params['todt'] = end_date

        logger.info(f'fetching bookmarks with params: {api_params}')

        self._rate_limit()
        bookmarks_raw = client.posts.all(**api_params)
        bookmarks = [Bookmark.from_api(b) for b in bookmarks_raw]

        logger.info(f'retrieved {len(bookmarks)} bookmarks')
        return bookmarks

    def get_bookmark(self, url: str) -> Optional[Bookmark]:
        '''
        get a specific bookmark by url.

        args:
            url: the bookmark url

        returns:
            Bookmark object or None if not found
        '''
        client = self._ensure_client()

        logger.debug(f'retrieving bookmark for URL: {url}')

        self._rate_limit()
        result = client.posts.get(url=url)
        posts = result.get('posts', [])

        if not posts:
            return None

        if len(posts) > 1:
            logger.warning(f'multiple bookmarks found for URL: {url}, using first one')

        return Bookmark.from_api(posts[0])

    def add_bookmark(
        self,
        url: str,
        title: str,
        description: str = '',
        tags: Optional[List[str]] = None,
        private: bool = False,
        toread: bool = False
    ) -> Bookmark:
        '''
        create a new bookmark.

        args:
            url: the web address to bookmark
            title: the bookmark title
            description: extended description or notes
            tags: list of tags
            private: set bookmark privacy
            toread: mark as to-read

        returns:
            the created Bookmark
        '''
        client = self._ensure_client()

        api_params = {
            'url': url,
            'description': title,  # pinboard uses 'description' for title
            'extended': description,
            'tags': tags or [],
            'shared': not private,
            'toread': toread
        }

        logger.info(f'adding bookmark: {title} -> {url}')

        self._rate_limit()
        result = client.posts.add(**api_params)

        if result is not True:
            logger.error(f'unexpected response from pinboard api: {result}')
            raise PinboardError('Failed to create bookmark - unexpected API response', 'add_bookmark')

        # return a bookmark object representing what we created
        return Bookmark(
            url=url,
            title=title,
            description=description,
            tags=tags or [],
            time=None,
            private=private,
            toread=toread
        )

    def update_bookmark(
        self,
        url: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        private: Optional[bool] = None,
        toread: Optional[bool] = None
    ) -> tuple:
        '''
        update a bookmark's properties.

        args:
            url: the URL of the bookmark to update
            title: new bookmark title
            description: new bookmark description
            tags: new tags list
            private: set bookmark privacy
            toread: mark as to-read

        returns:
            tuple of (updated Bookmark, list of update descriptions)
        '''
        client = self._ensure_client()

        # first get the existing bookmark
        self._rate_limit()
        result = client.posts.get(url=url)
        posts = result.get('posts', [])

        if not posts:
            raise PinboardError(f'No bookmark found for URL: {url}', 'update_bookmark')

        bookmark = posts[0]
        updates = []

        if title is not None:
            old_title = bookmark.description
            bookmark.description = title
            updates.append(f"title: '{old_title}' -> '{title}'")

        if description is not None:
            old_desc = bookmark.extended
            bookmark.extended = description
            updates.append(f"description: '{old_desc}' -> '{description}'")

        if tags is not None:
            old_tags = bookmark.tags
            bookmark.tags = ' '.join(tags)
            updates.append(f"tags: '{old_tags}' -> '{bookmark.tags}'")

        if private is not None:
            old_shared = bookmark.shared
            bookmark.shared = not private
            updates.append(f"private: {not old_shared} -> {private}")

        if toread is not None:
            old_toread = bookmark.toread
            bookmark.toread = 'yes' if toread else 'no'
            updates.append(f"toread: '{old_toread}' -> '{bookmark.toread}'")

        if not updates:
            raise PinboardError(
                'No updates provided. At least one field must be specified.',
                'update_bookmark'
            )

        logger.info(f'updating bookmark {url}: {", ".join(updates)}')

        self._rate_limit()
        bookmark.save()

        logger.info(f'successfully updated bookmark: {url}')
        return Bookmark.from_api(bookmark), updates

    # tag operations

    def get_tags(self) -> List[TagInfo]:
        '''
        retrieve all tags with usage counts.

        returns:
            list of TagInfo objects sorted by count (descending)
        '''
        client = self._ensure_client()

        logger.info('fetching tags from pinboard')

        self._rate_limit()
        tags_raw = client.tags.get()

        tags = format_tags_response(tags_raw)
        logger.info(f'retrieved {len(tags)} tags')
        return tags

    def rename_tag(self, old_tag: str, new_tag: str) -> None:
        '''
        rename a tag across all bookmarks.

        args:
            old_tag: the existing tag name to rename
            new_tag: the new tag name
        '''
        client = self._ensure_client()

        old_normalized = normalize_tag(old_tag)
        new_normalized = normalize_tag(new_tag)

        if old_normalized == new_normalized:
            raise PinboardError('old_tag and new_tag cannot be the same', 'rename_tag')

        logger.info(f"renaming tag: '{old_normalized}' -> '{new_normalized}'")

        self._rate_limit()
        result = client.tags.rename(old=old_normalized, new=new_normalized)

        if result is not True:
            logger.error(f'unexpected response from pinboard api: {result}')
            raise PinboardError('Failed to rename tag - unexpected API response', 'rename_tag')

        logger.info(f"successfully renamed tag: '{old_normalized}' -> '{new_normalized}'")

    def suggest_tags(self, url: str) -> Dict[str, List[str]]:
        '''
        get suggested tags for a url.

        args:
            url: the web address to get tag suggestions for

        returns:
            dict with 'popular' and 'recommended' tag lists
        '''
        client = self._ensure_client()

        logger.info(f'fetching tag suggestions for URL: {url}')

        self._rate_limit()
        suggestions = client.posts.suggest(url=url)

        formatted = format_suggest_response(suggestions)
        logger.info(
            f"retrieved {len(formatted['popular'])} popular and "
            f"{len(formatted['recommended'])} recommended tags for {url}"
        )
        return formatted
