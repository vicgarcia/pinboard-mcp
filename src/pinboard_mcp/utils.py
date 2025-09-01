from typing import Optional
from dateutil import parser as date_parser


def validate_date_range(start_date: Optional[str], end_date: Optional[str]) -> tuple:
    ''' validate and parse date range with 90-day maximum limit. '''
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

    # validate date logic
    if parsed_start and parsed_end and parsed_start > parsed_end:
        raise ValueError("start_date must be before end_date")

    # check 90-day limit
    if parsed_start and parsed_end:
        date_diff = (parsed_end - parsed_start).days
        if date_diff > 90:
            raise ValueError(f"Date range cannot exceed 90 days. Current range: {date_diff} days")

    return parsed_start, parsed_end