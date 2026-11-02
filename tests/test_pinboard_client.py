'''
unit tests for pinboard client bug fixes.

uses a fake pinboard library so no network calls are made.
'''

from datetime import datetime

import pytest
import pinboard

from pinboard_mcp.pinboard_client import PinboardClient
from pinboard_mcp.schema import TagInfo


class FakeTag:
    '''mimic pinboard.Tag.'''

    def __init__(self, name, count):
        self.name = name
        self.count = count


class FakeBookmark:
    '''mimic pinboard.Bookmark, including save()'s yes/no serialization.'''

    def __init__(self, url, description, extended, tags, shared, toread, time):
        self.url = url
        self.description = description
        self.extended = extended
        self.tags = tags
        self.shared = shared
        self.toread = toread
        self.time = time
        self.meta = ''
        self.hash = ''
        self.saved = None

    def save(self, update_time=False):
        params = {
            'url': self.url,
            'description': self.description,
            'extended': self.extended,
            'tags': ' '.join(self.tags) if isinstance(self.tags, list) else self.tags,
            'shared': 'yes' if self.shared else 'no',
            'toread': 'yes' if self.toread else 'no',
        }
        if update_time:
            params['dt'] = self.time
        self.saved = params
        return True


class FakePosts:
    def __init__(self, bookmarks):
        self._bookmarks = bookmarks
        self.added = []

    def get(self, url):
        return {'posts': [b for b in self._bookmarks if b.url == url]}

    def add(self, **kwargs):
        self.added.append(kwargs)
        return True

    def all(self, **kwargs):
        return list(self._bookmarks)

    def update(self):
        return datetime.now()

    def suggest(self, url):
        return [{'popular': ['one'], 'recommended': ['two']}]


class FakeTags:
    def __init__(self):
        self.renamed = None

    def get(self):
        return [FakeTag('python', 3), FakeTag('ai', 10)]

    def rename(self, old, new):
        self.renamed = (old, new)
        return True


class FakePinboard:
    def __init__(self, token):
        self.token = token
        self.posts = FakePosts([
            FakeBookmark(
                url='https://example.com/a',
                description='Old title',
                extended='Old description',
                tags=['python', 'ai'],
                shared=True,
                toread=False,
                time=datetime(2023, 12, 1, 10, 30, 0),
            )
        ])
        self.tags = FakeTags()


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(pinboard, 'Pinboard', FakePinboard)
    c = PinboardClient('user:token')
    c.RATE_LIMIT_SECONDS = 0.0
    c.__enter__()
    yield c
    c.__exit__(None, None, None)


def test_update_preserves_creation_timestamp(client):
    bookmark = client._client.posts._bookmarks[0]

    client.update_bookmark('https://example.com/a', title='New title')

    assert bookmark.saved['dt'] == datetime(2023, 12, 1, 10, 30, 0)
    assert bookmark.description == 'New title'


def test_update_toread_false_clears_toread(client):
    bookmark = client._client.posts._bookmarks[0]

    client.update_bookmark('https://example.com/a', toread=False)

    assert bookmark.saved['toread'] == 'no'


def test_update_toread_true_sets_toread(client):
    bookmark = client._client.posts._bookmarks[0]

    client.update_bookmark('https://example.com/a', toread=True)

    assert bookmark.saved['toread'] == 'yes'


def test_update_returns_assigned_tags(client):
    bookmark = client._client.posts._bookmarks[0]

    updated, _ = client.update_bookmark(
        'https://example.com/a', tags=['python', 'new']
    )

    assert bookmark.saved['tags'] == 'python new'
    assert updated.tags == ['python', 'new']


def test_update_response_keeps_original_time(client):
    updated, _ = client.update_bookmark('https://example.com/a', title='New title')

    assert updated.time == datetime(2023, 12, 1, 10, 30, 0)
    assert updated.title == 'New title'


def test_get_tags_returns_taginfo_sorted(client):
    tags = client.get_tags()

    assert tags == [TagInfo('ai', 10), TagInfo('python', 3)]
