'''
unit tests for private-by-default bookmarks through the mcp tools, using a fake pinboard library.
'''

from datetime import datetime

import pytest
import pinboard

from pinboard_mcp import server
from pinboard_mcp.pinboard_client import PinboardClient
from test_pinboard_client import FakeBookmark, FakePinboard


def bookmark(name, shared):
    return FakeBookmark(
        url=f'https://example.com/{name}', description=name, extended='',
        tags=['python'], shared=shared, toread=False, time=datetime(2023, 12, 1),
    )


def shared_param(value):
    # pinboard.py sends booleans to the api as yes/no
    return 'yes' if value else 'no'


@pytest.fixture
def posts(monkeypatch):
    fake = FakePinboard('user:token')
    fake.posts._bookmarks = [
        bookmark('public', True),
        bookmark('private', False),
    ]
    monkeypatch.setattr(pinboard, 'Pinboard', lambda token: fake)
    client = PinboardClient('user:token')
    client.RATE_LIMIT_SECONDS = 0.0
    monkeypatch.setattr(server, '_client', client)
    return fake.posts


def test_add_is_private_by_default(posts):
    result = server.add_bookmark('https://example.com/new', 'New')
    assert shared_param(posts.added[-1]['shared']) == 'no'
    assert result['bookmark']['private'] is True


def test_add_private_false_is_public(posts):
    result = server.add_bookmark('https://example.com/new', 'New', private=False)
    assert shared_param(posts.added[-1]['shared']) == 'yes'
    assert result['bookmark']['private'] is False


def test_add_private_true_is_private(posts):
    server.add_bookmark('https://example.com/new', 'New', private=True)
    assert shared_param(posts.added[-1]['shared']) == 'no'


@pytest.mark.parametrize('name, shared', [('public', 'yes'), ('private', 'no')])
def test_update_without_private_keeps_visibility(posts, name, shared):
    result = server.update_bookmark(f'https://example.com/{name}', title='New title')
    saved = posts._bookmarks[0 if name == 'public' else 1].saved
    assert saved['shared'] == shared
    assert result['bookmark']['private'] is (shared == 'no')


def test_update_private_changes_visibility(posts):
    server.update_bookmark('https://example.com/public', private=True)
    assert posts._bookmarks[0].saved['shared'] == 'no'
    server.update_bookmark('https://example.com/private', private=False)
    assert posts._bookmarks[1].saved['shared'] == 'yes'
