'''
dataclasses and utilities for pinboard bookmark operations.
'''

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Bookmark:
    '''pinboard bookmark representation.'''
    url: str
    title: str
    description: str
    tags: List[str]
    time: Optional[datetime]
    private: bool
    toread: bool = False

    @classmethod
    def from_api(cls, bookmark) -> 'Bookmark':
        '''parse from pinboard api response object.'''
        time_value = None
        try:
            if bookmark.time:
                time_value = bookmark.time
        except Exception:
            pass

        tags = bookmark.tags if isinstance(bookmark.tags, list) else []

        return cls(
            url=bookmark.url,
            title=bookmark.description,  # pinboard uses 'description' for title
            description=bookmark.extended,
            tags=tags,
            time=time_value,
            private=not bookmark.shared,
            toread=getattr(bookmark, 'toread', False)
        )

    def to_dict(self) -> Dict[str, Any]:
        '''serialize for tool response.'''
        time_str = None
        if self.time:
            try:
                time_str = self.time.isoformat()
            except Exception:
                pass

        return {
            'url': self.url,
            'title': self.title,
            'description': self.description,
            'tags': self.tags,
            'time': time_str,
            'private': self.private,
        }


@dataclass
class TagInfo:
    '''tag with usage count.'''
    name: str
    count: int

    def to_dict(self) -> Dict[str, Any]:
        '''serialize for tool response.'''
        return {'tag': self.name, 'count': self.count}


# tag utilities

def parse_tags(tags_str: Optional[str]) -> List[str]:
    '''parse comma-separated tags string into cleaned list.'''
    if not tags_str:
        return []
    return [tag.strip().lower() for tag in tags_str.split(',') if tag.strip()]


def normalize_tag(tag: str) -> str:
    '''normalize a single tag (strip whitespace and lowercase).'''
    return tag.strip().lower()


def format_tags_response(tags_raw: Dict[str, int]) -> List[TagInfo]:
    '''format tags dictionary into sorted list of TagInfo.'''
    tags = [TagInfo(name=name, count=count) for name, count in tags_raw.items()]
    tags.sort(key=lambda x: (-x.count, x.name))
    return tags


def format_suggest_response(suggestions: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    '''format tag suggestions into popular and recommended lists.'''
    popular = []
    recommended = []

    for suggestion in suggestions:
        if suggestion.get('popular'):
            popular.extend(suggestion['popular'])
        if suggestion.get('recommended'):
            recommended.extend(suggestion['recommended'])

    return {'popular': popular, 'recommended': recommended}


# date validation

def validate_date_range(
    start_date: Optional[str],
    end_date: Optional[str],
    max_days: int = 90
) -> tuple:
    '''
    validate and parse date range.

    args:
        start_date: start date in YYYY-MM-DD format
        end_date: end date in YYYY-MM-DD format
        max_days: maximum allowed range in days

    returns:
        tuple of (parsed_start, parsed_end) as date objects or None

    raises:
        ValueError: if dates are invalid or range exceeds max_days
    '''
    from dateutil import parser as date_parser

    parsed_start = None
    parsed_end = None

    if start_date:
        try:
            parsed_start = date_parser.parse(start_date).date()
        except (ValueError, TypeError):
            raise ValueError(f"Invalid start_date format: {start_date}. Use YYYY-MM-DD format.")

    if end_date:
        try:
            parsed_end = date_parser.parse(end_date).date()
        except (ValueError, TypeError):
            raise ValueError(f"Invalid end_date format: {end_date}. Use YYYY-MM-DD format.")

    if parsed_start and parsed_end and parsed_start > parsed_end:
        raise ValueError("start_date must be before end_date")

    if parsed_start and parsed_end:
        date_diff = (parsed_end - parsed_start).days
        if date_diff > max_days:
            raise ValueError(f"Date range cannot exceed {max_days} days. Current range: {date_diff} days")

    return parsed_start, parsed_end


# response helpers

def create_error_response(message: str) -> Dict[str, Any]:
    '''create a standardized error response.'''
    return {'error': message, 'success': False}


def create_success_response(**kwargs) -> Dict[str, Any]:
    '''create a standardized success response with optional data.'''
    return {'success': True, **kwargs}
