from typing import Optional
from urllib.parse import urlparse
from dateutil import parser as date_parser


def validate_url(url: Optional[str]) -> str:
    '''
    validate and normalize a URL for bookmark creation.
    
    args:
        url: the URL to validate
        
    returns:
        normalized URL string
        
    raises:
        ValueError: if the URL is invalid with descriptive message
    '''
    if not url:
        raise ValueError("URL is required and cannot be empty")
    
    # strip whitespace and convert to string
    url_str = str(url).strip()
    
    if not url_str:
        raise ValueError("URL cannot be empty or whitespace only")
    
    # check minimum length for a valid URL
    if len(url_str) < 7:  # http:// is minimum
        raise ValueError("URL is too short to be valid")
    
    try:
        # parse the URL
        parsed = urlparse(url_str)
        
        # validate scheme
        if not parsed.scheme:
            raise ValueError("URL must include a protocol (http:// or https://)")
        
        if parsed.scheme.lower() not in ['http', 'https']:
            raise ValueError(f"Unsupported URL scheme '{parsed.scheme}'. Only HTTP and HTTPS are supported")
        
        # validate netloc (domain)
        if not parsed.netloc:
            raise ValueError("URL must include a valid domain name")
        
        # check for suspicious characters in domain
        if any(char in parsed.netloc for char in [' ', '\t', '\n', '\r']):
            raise ValueError("URL domain contains invalid characters")
        
        # basic domain format check
        if '.' not in parsed.netloc and 'localhost' not in parsed.netloc.lower():
            raise ValueError("URL domain appears to be malformed")
        
        # reconstruct normalized URL
        normalized_url = f"{parsed.scheme}://{parsed.netloc}"
        if parsed.path:
            normalized_url += parsed.path
        if parsed.params:
            normalized_url += f";{parsed.params}"
        if parsed.query:
            normalized_url += f"?{parsed.query}"
        if parsed.fragment:
            normalized_url += f"#{parsed.fragment}"
            
        return normalized_url
        
    except ValueError:
        # re-raise our custom validation errors
        raise
    except Exception as e:
        raise ValueError(f"Invalid URL format: {e}")


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