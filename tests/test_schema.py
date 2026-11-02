'''
unit tests for converting the pinboard library's objects, using its real classes.
'''

from types import SimpleNamespace

import pytest
from pinboard.pinboard import Bookmark as PinboardBookmark, Tag as PinboardTag

from pinboard_mcp.schema import Bookmark, TagInfo


def library_bookmark(tags):
    return PinboardBookmark({
        'href': 'https://example.com/a',
        'description': 'Title',
        'extended': 'Description',
        'meta': '',
        'hash': '',
        'shared': 'yes',
        'toread': 'no',
        'tags': tags,
        'time': '2023-12-01T10:30:00Z',
    }, 'user:token')


def test_bookmark_from_api_keeps_tags():
    assert Bookmark.from_api(library_bookmark('python ai')).tags == ['python', 'ai']


def test_bookmark_from_api_untagged_has_no_tags():
    # the library splits an empty tag string into ['']
    assert Bookmark.from_api(library_bookmark('')).tags == []


def test_bookmark_from_api_refuses_tags_it_cannot_read():
    bookmark = SimpleNamespace(
        url='https://example.com/a', description='Title', extended='',
        tags='python ai', time=None, shared=True, toread=False,
    )
    with pytest.raises(ValueError, match='tags'):
        Bookmark.from_api(bookmark)


def test_tag_info_from_api():
    assert TagInfo.from_api(PinboardTag('python', '3')) == TagInfo('python', 3)
