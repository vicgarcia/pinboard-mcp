'''
unit tests for to-read support through the mcp tools, using a fake pinboard library.
'''

from datetime import datetime

import pytest
import pinboard

from pinboard_mcp import server
from pinboard_mcp.pinboard_client import PinboardClient
from test_pinboard_client import FakeBookmark, FakePinboard


def bookmark(name, toread):
    return FakeBookmark(
        url=f'https://example.com/{name}', description=name, extended='',
        tags=['python'], shared=True, toread=toread, time=datetime(2023, 12, 1),
    )


@pytest.fixture
def posts(monkeypatch):
    fake = FakePinboard('user:token')
    fake.posts._bookmarks = [
        bookmark('newest', False),
        bookmark('unread-one', True),
        bookmark('read', False),
        bookmark('unread-two', True),
    ]
    calls = []
    fake.posts.all = lambda **kwargs: calls.append(kwargs) or list(fake.posts._bookmarks)
    fake.posts.calls = calls
    monkeypatch.setattr(pinboard, 'Pinboard', lambda token: fake)
    client = PinboardClient('user:token')
    client.RATE_LIMIT_SECONDS = 0.0
    monkeypatch.setattr(server, '_client', client)
    return fake.posts


def titles(result):
    return [b['title'] for b in result['bookmarks']]


def test_responses_show_toread(posts):
    result = server.get_bookmarks()
    assert [b['toread'] for b in result['bookmarks']] == [False, True, False, True]


def test_add_response_shows_toread(posts):
    result = server.add_bookmark('https://example.com/new', 'New', toread=True)
    assert result['bookmark']['toread'] is True


def test_update_response_shows_toread(posts):
    url = 'https://example.com/newest'
    assert server.update_bookmark(url, toread=True)['bookmark']['toread'] is True
    assert server.update_bookmark(url, toread=False)['bookmark']['toread'] is False


def test_filter_to_unread(posts):
    result = server.get_bookmarks(toread=True)
    assert titles(result) == ['unread-one', 'unread-two']
    assert result['filters_applied']['toread'] is True


def test_filter_to_read(posts):
    assert titles(server.get_bookmarks(toread=False)) == ['newest', 'read']


def test_limit_applies_after_the_filter(posts):
    # the newest bookmark isn't to-read, so limiting first would find nothing
    assert titles(server.get_bookmarks(toread=True, limit=1)) == ['unread-one']
    assert 'results' not in posts.calls[-1]


def test_without_a_filter_the_limit_goes_to_the_api(posts):
    server.get_bookmarks(limit=2)
    assert posts.calls[-1]['results'] == 2
    assert 'toread' not in server.get_bookmarks()['filters_applied']
