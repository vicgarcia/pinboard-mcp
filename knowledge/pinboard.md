# Pinboard API Comprehensive Knowledge Base

**Official API Documentation**: https://pinboard.in/api/  
**Python Library**: https://github.com/lionheart/pinboard.py  
**Service URL**: https://pinboard.in/

## Table of Contents
1. [Authentication & Setup](#authentication--setup)
2. [Core Data Structures](#core-data-structures)
3. [Bookmark Operations](#bookmark-operations)
4. [Tag Management](#tag-management)
5. [User & Account Operations](#user--account-operations)
6. [Rate Limiting & Best Practices](#rate-limiting--best-practices)
7. [HTTP API Direct Usage](#http-api-direct-usage)
8. [Error Handling](#error-handling)
9. [Production Considerations](#production-considerations)
10. [Advanced Patterns](#advanced-patterns)

---

## Authentication & Setup

### API Token Authentication
```python
# Get your API token from: https://pinboard.in/settings/password
API_TOKEN = "username:1234567890ABCDEF1234567890ABCDEF"

# Authentication methods
import requests

# Method 1: Query parameter
response = requests.get(
    "https://api.pinboard.in/v1/posts/recent",
    params={"auth_token": API_TOKEN, "format": "json"}
)

# Method 2: HTTP Basic Auth (less common)
from requests.auth import HTTPBasicAuth
response = requests.get(
    "https://api.pinboard.in/v1/posts/recent",
    auth=HTTPBasicAuth("username", "password"),
    params={"format": "json"}
)
```

### Using pinboard.py Library
```python
import pinboard
import os

# Method 1: Direct token
pb = pinboard.Pinboard("username:API_TOKEN")

# Method 2: Environment variable
os.environ["PINBOARD_TOKEN"] = "username:API_TOKEN"
pb = pinboard.Pinboard()

# Method 3: Configuration file ~/.pinboardrc
# Contents: username:API_TOKEN
pb = pinboard.Pinboard()
```

### Python Library Authentication Setup
```python
import os
import pinboard

# Initialize Pinboard client
def get_pinboard_client():
    """Get authenticated Pinboard client."""
    token = os.getenv("PINBOARD_TOKEN")
    if not token:
        raise ValueError("PINBOARD_TOKEN environment variable required")
    return pinboard.Pinboard(token)

def test_connection():
    """Test Pinboard API connection."""
    try:
        pb = get_pinboard_client()
        # Test with a simple API call
        last_update = pb.posts.update()
        return {"connected": True, "last_update": last_update}
    except Exception as e:
        return {"connected": False, "error": str(e)}
```

---

## Core Data Structures

### Bookmark Structure
```python
# Complete bookmark data structure
bookmark_example = {
    "href": "https://example.com",           # URL (required)
    "description": "Example Website",        # Title/name (required, max 255 chars)
    "extended": "Longer description here",   # Description (max 65,536 chars)
    "tags": "reference useful web",          # Space-separated tags (max 255 chars total)
    "time": "2024-01-15T10:30:00Z",         # ISO 8601 timestamp
    "shared": "yes",                         # "yes" or "no" (public/private)
    "toread": "no",                          # "yes" or "no" (read later flag)
    "hash": "abc123...",                     # MD5 hash of URL
    "meta": "unique_id"                      # Optional metadata
}
```

### Tag Structure
```python
# Tag information from /tags/get
tag_example = {
    "programming": 145,    # tag_name: count
    "python": 89,
    "web-development": 67,
    "reference": 234
}
```

### Note Structure
```python
# Note data from /notes/list
note_example = {
    "id": "note_id_hash",
    "title": "My Important Note",
    "hash": "abc123...",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T15:45:00Z",
    "length": 1250  # Character count
}
```

---

## Bookmark Operations

### Add Bookmark
```python
def add_bookmark(
    pb, 
    url: str, 
    title: str, 
    description: str = "", 
    tags: list = None, 
    private: bool = False, 
    read_later: bool = False
):
    """Add a new bookmark to Pinboard."""
    # Validate URL
    if not url.startswith(('http://', 'https://')):
        raise ValueError("Invalid URL format")
    
    # Clean and validate title
    if len(title) > 255:
        title = title[:252] + "..."
    
    # Prepare tags
    if tags is None:
        tags = []
    
    # Add bookmark using pinboard library
    result = pb.posts.add(
        url=url,
        description=title,
        extended=description,
        tags=tags,
        shared=not private,
        toread=read_later
    )
    
    return result

def bulk_add_bookmarks(pb, bookmarks: list):
    """Add multiple bookmarks with rate limiting."""
    import time
    
    results = []
    failed = []
    
    for i, bookmark in enumerate(bookmarks):
        try:
            # Rate limiting: 1 call per 3 seconds
            if i > 0:
                time.sleep(3)
            
            pb.posts.add(
                url=bookmark["url"],
                description=bookmark.get("title", ""),
                extended=bookmark.get("description", ""),
                tags=bookmark.get("tags", []),
                shared=not bookmark.get("private", False),
                toread=bookmark.get("read_later", False)
            )
            results.append(bookmark["url"])
            
        except Exception as e:
            failed.append({"url": bookmark["url"], "error": str(e)})
    
    return {
        "added": len(results),
        "failed": len(failed),
        "results": results,
        "failures": failed
    }

# Example usage
pb = pinboard.Pinboard("username:API_TOKEN")

# Add single bookmark
add_bookmark(
    pb,
    url="https://example.com",
    title="Example Website",
    description="A great example site",
    tags=["example", "reference"],
    private=False,
    read_later=False
)

# Add multiple bookmarks
bookmarks_to_add = [
    {
        "url": "https://site1.com",
        "title": "Site 1",
        "tags": ["tag1", "tag2"]
    },
    {
        "url": "https://site2.com", 
        "title": "Site 2",
        "private": True
    }
]
result = bulk_add_bookmarks(pb, bookmarks_to_add)
```

### Retrieve Bookmarks
```python
def get_bookmarks(pb, tags=None, start=0, count=20, from_date=None):
    """Retrieve bookmarks with filtering options."""
    # Build parameters
    params = {}
    if tags:
        params["tag"] = tags if isinstance(tags, list) else tags.split()
    if from_date:
        params["dt"] = from_date
    if count != 20:
        params["results"] = min(count, 10000)  # API max is 10k
    
    # Get bookmarks
    if params:
        bookmarks = pb.posts.get(**params)
    else:
        bookmarks = pb.posts.recent(count=count)
    
    # Return slice of bookmarks
    return bookmarks[start:start + count]

def search_bookmarks(pb, query, search_in="all"):
    """Search bookmarks by title, description, or tags."""
    # Get all bookmarks
    all_bookmarks = pb.posts.all()
    
    # Search logic
    results = []
    query_lower = query.lower()
    
    for bookmark in all_bookmarks:
        match_found = False
        
        if search_in in ["all", "title"] and query_lower in bookmark.description.lower():
            match_found = True
        elif search_in in ["all", "description"] and query_lower in bookmark.extended.lower():
            match_found = True
        elif search_in in ["all", "tags"] and any(query_lower in tag.lower() for tag in bookmark.tags):
            match_found = True
        elif search_in in ["all", "url"] and query_lower in bookmark.url.lower():
            match_found = True
        
        if match_found:
            results.append(bookmark)
    
    return results

def format_bookmark(bookmark):
    """Convert bookmark object to dictionary."""
    return {
        "url": bookmark.url,
        "title": bookmark.description,
        "description": bookmark.extended,
        "tags": list(bookmark.tags),
        "time": bookmark.time.isoformat() if bookmark.time else None,
        "private": not bookmark.shared,
        "read_later": bookmark.toread,
        "hash": bookmark.hash
    }

# Example usage
pb = pinboard.Pinboard("username:API_TOKEN")

# Get recent bookmarks
recent = pb.posts.recent(count=10)

# Get bookmarks by tag
programming_bookmarks = get_bookmarks(pb, tags=["programming"], count=50)

# Search bookmarks
python_bookmarks = search_bookmarks(pb, "python", search_in="title")

# Format bookmarks for display
formatted = [format_bookmark(bookmark) for bookmark in recent]
```

### Update and Delete Bookmarks
```python
def update_bookmark(
    pb,
    url: str, 
    title: str = None, 
    description: str = None, 
    tags: list = None, 
    private: bool = None, 
    read_later: bool = None
):
    """Update an existing bookmark."""
        
        # Get current bookmark
        current = pb.posts.get(url=url)
        if not current:
            return {"error": "Bookmark not found", "success": False}
        
        bookmark = current[0]
        
    # Update with new values or keep existing
    new_title = title if title is not None else bookmark.description
    new_description = description if description is not None else bookmark.extended
    new_tags = tags if tags is not None else list(bookmark.tags)
    new_private = private if private is not None else not bookmark.shared
    new_read_later = read_later if read_later is not None else bookmark.toread
    
    # Delete old bookmark
    pb.posts.delete(url=url)
    
    # Add updated bookmark (Pinboard doesn't have update, only add/delete)
    import time
    time.sleep(1)  # Brief pause between delete and add
    
    pb.posts.add(
        url=url,
        description=new_title,
        extended=new_description,
        tags=new_tags,
        shared=not new_private,
        toread=new_read_later
    )
    
    return {
        "url": url,
        "changes": {
            "title": new_title,
            "description": new_description,
            "tags": new_tags,
            "private": new_private,
            "read_later": new_read_later
        }
    }

def delete_bookmark(pb, url: str):
    """Delete a bookmark."""
    # Check if bookmark exists
    existing = pb.posts.get(url=url)
    if not existing:
        raise ValueError("Bookmark not found")
    
    # Delete bookmark
    pb.posts.delete(url=url)
    
    return {"url": url, "message": "Bookmark deleted successfully"}

# Example usage
pb = pinboard.Pinboard("username:API_TOKEN")

# Update a bookmark
update_result = update_bookmark(
    pb,
    url="https://example.com",
    title="Updated Title",
    tags=["updated", "example"],
    private=True
)

# Delete a bookmark
delete_result = delete_bookmark(pb, "https://unwanted-site.com")
```

---

## Tag Management

### Tag Operations
```python
def get_all_tags(pb):
    """Get all tags with usage counts."""
    tags = pb.tags.get()
    
    # Format tags data
    tag_list = []
    for tag_name, count in tags.items():
        tag_list.append({
            "name": tag_name,
            "count": count
        })
    
    # Sort by usage count (descending)
    tag_list.sort(key=lambda x: x["count"], reverse=True)
    
    return tag_list

def suggest_tags(pb, url: str):
    """Get tag suggestions for a URL."""
    suggestions = pb.posts.suggest(url=url)
    
    return {
        "url": url,
        "popular": list(suggestions.get("popular", [])),
        "recommended": list(suggestions.get("recommended", []))
    }

def rename_tag(pb, old_tag: str, new_tag: str):
    """Rename a tag across all bookmarks."""
    # Validate new tag name
    if not new_tag or " " in new_tag or "," in new_tag:
        raise ValueError("Invalid tag name (no spaces or commas allowed)")
    
    # Check if old tag exists
    tags = pb.tags.get()
    if old_tag not in tags:
        raise ValueError(f"Tag '{old_tag}' not found")
    
    affected_count = tags[old_tag]
    
    # Rename tag
    pb.tags.rename(old=old_tag, new=new_tag)
    
    return {
        "old_tag": old_tag,
        "new_tag": new_tag,
        "affected_bookmarks": affected_count
    }

def delete_tag(pb, tag: str):
    """Delete a tag from all bookmarks."""
    # Check if tag exists
    tags = pb.tags.get()
    if tag not in tags:
        raise ValueError(f"Tag '{tag}' not found")
    
    affected_count = tags[tag]
    
    # Delete tag
    pb.tags.delete(tag=tag)
    
    return {
        "deleted_tag": tag,
        "affected_bookmarks": affected_count
    }

def get_popular_tags(pb, min_usage: int = 5):
    """Get popular tags above a usage threshold."""
    tags = pb.tags.get()
    
    # Filter popular tags
    popular = {
        tag: count for tag, count in tags.items() 
        if count >= min_usage
    }
    
    # Sort by usage
    sorted_tags = sorted(popular.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "min_usage": min_usage,
        "popular_tags": [{"name": tag, "count": count} for tag, count in sorted_tags],
        "total_popular": len(sorted_tags),
        "total_tags": len(tags)
    }

# Example usage
pb = pinboard.Pinboard("username:API_TOKEN")

# Get all tags
all_tags = get_all_tags(pb)

# Get tag suggestions 
suggestions = suggest_tags(pb, "https://python.org")

# Rename a tag
rename_result = rename_tag(pb, "old-tag", "new-tag")

# Delete a tag
delete_result = delete_tag(pb, "unwanted-tag")

# Get popular tags (used 10+ times)
popular = get_popular_tags(pb, min_usage=10)
```

---

## User & Account Operations

### Account Information
```python
def get_account_info(pb):
    """Get account information and statistics."""
    # Get last update time
    last_update = pb.posts.update()
    
    # Get total counts
    tags = pb.tags.get()
    
    # Get recent bookmarks to estimate total
    recent = pb.posts.recent(count=1)
    
    return {
        "last_update": last_update.isoformat() if last_update else None,
        "total_tags": len(tags),
        "has_bookmarks": len(recent) > 0,
        "most_used_tags": sorted(tags.items(), key=lambda x: x[1], reverse=True)[:10]
    }

def get_api_token_info():
    """Information about API token retrieval."""
    # Note: This requires username/password authentication via HTTP API
    return {
        "message": "API token retrieval requires password authentication.",
        "instructions": "Get your API token from https://pinboard.in/settings/password",
        "format": "username:TOKEN_STRING"
    }

def check_last_update(pb):
    """Check when bookmarks were last updated."""
    last_update = pb.posts.update()
    
    return {
        "last_update": last_update.isoformat() if last_update else None,
        "message": "Use this timestamp to check if bookmarks have changed"
    }

# Example usage
pb = pinboard.Pinboard("username:API_TOKEN")

# Get account information
account_info = get_account_info(pb)

# Check for updates
last_update = check_last_update(pb)

# API token information
token_info = get_api_token_info()
```

---

## Rate Limiting & Best Practices

### Rate Limiting Implementation
```python
import time
from datetime import datetime, timedelta
from typing import Dict, Any

class PinboardRateLimiter:
    """Rate limiter for Pinboard API (1 call per 3 seconds)."""
    
    def __init__(self):
        self.last_call = None
        self.min_interval = 3.0  # seconds
    
    def wait_if_needed(self):
        """Wait if necessary to respect rate limits."""
        if self.last_call:
            elapsed = time.time() - self.last_call
            if elapsed < self.min_interval:
                wait_time = self.min_interval - elapsed
                time.sleep(wait_time)
        
        self.last_call = time.time()

# Global rate limiter instance
rate_limiter = PinboardRateLimiter()

def rate_limited_bookmark_operation(pb, operation: str, **kwargs):
    """Perform bookmark operation with rate limiting."""
    rate_limiter.wait_if_needed()
    
    if operation == "add":
        result = pb.posts.add(**kwargs)
    elif operation == "delete":
        result = pb.posts.delete(url=kwargs["url"])
    elif operation == "get":
        result = pb.posts.get(**kwargs)
    else:
        raise ValueError(f"Unknown operation: {operation}")
    
    return {
        "operation": operation,
        "result": result,
        "rate_limited": True
    }
```

### Caching Strategy
```python
import json
import os
from datetime import datetime, timedelta

class PinboardCache:
    """Simple file-based cache for Pinboard data."""
    
    def __init__(self, cache_dir: str = "/tmp/pinboard_cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_cache_path(self, key: str) -> str:
        return os.path.join(self.cache_dir, f"{key}.json")
    
    def is_fresh(self, cache_path: str, max_age_minutes: int = 30) -> bool:
        """Check if cache is fresh enough."""
        if not os.path.exists(cache_path):
            return False
        
        mtime = os.path.getmtime(cache_path)
        age = datetime.now() - datetime.fromtimestamp(mtime)
        return age < timedelta(minutes=max_age_minutes)
    
    def get(self, key: str, max_age_minutes: int = 30) -> Any:
        """Get cached data if fresh."""
        cache_path = self.get_cache_path(key)
        
        if self.is_fresh(cache_path, max_age_minutes):
            with open(cache_path, 'r') as f:
                return json.load(f)
        return None
    
    def set(self, key: str, data: Any):
        """Cache data."""
        cache_path = self.get_cache_path(key)
        with open(cache_path, 'w') as f:
            json.dump(data, f)
    
    def clear(self, key: str = None):
        """Clear cache."""
        if key:
            cache_path = self.get_cache_path(key)
            if os.path.exists(cache_path):
                os.remove(cache_path)
        else:
            # Clear all cache
            for file in os.listdir(self.cache_dir):
                if file.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, file))

cache = PinboardCache()

def get_cached_bookmarks(pb, cache, rate_limiter, tags="", use_cache=True):
    """Get bookmarks with caching support."""
    cache_key = f"bookmarks_{tags.replace(' ', '_')}"
    
    if use_cache:
        cached = cache.get(cache_key, max_age_minutes=15)
        if cached:
            cached["from_cache"] = True
            return cached
    
    # Fetch fresh data
    rate_limiter.wait_if_needed()
    
    if tags:
        bookmarks = pb.posts.get(tag=tags.split())
    else:
        bookmarks = pb.posts.recent(count=100)
    
    formatted_bookmarks = []
    for bookmark in bookmarks:
        formatted_bookmarks.append({
            "url": bookmark.url,
            "title": bookmark.description,
            "description": bookmark.extended,
            "tags": list(bookmark.tags),
            "time": bookmark.time.isoformat() if bookmark.time else None,
            "private": not bookmark.shared,
            "read_later": bookmark.toread
        })
    
    result = {
        "count": len(formatted_bookmarks),
        "bookmarks": formatted_bookmarks,
        "tags_filter": tags,
        "from_cache": False,
        "cached_at": datetime.now().isoformat()
    }
    
    # Cache the result
    if use_cache:
        cache.set(cache_key, result)
    
    return result

# Example usage
pb = pinboard.Pinboard("username:API_TOKEN")
rate_limiter = PinboardRateLimiter()
cache = PinboardCache()

# Rate limited operations
result = rate_limited_bookmark_operation(pb, "add", 
    url="https://example.com",
    description="Example",
    tags=["example"]
)

# Cached bookmark retrieval
bookmarks = get_cached_bookmarks(pb, cache, rate_limiter, tags="python")
```

---

## HTTP API Direct Usage

### Direct HTTP API Requests
```python
import requests
import json
from datetime import datetime

class PinboardHTTPAPI:
    """Direct HTTP API client for Pinboard."""
    
    def __init__(self, auth_token):
        self.auth_token = auth_token
        self.base_url = "https://api.pinboard.in/v1"
        self.session = requests.Session()
        
    def _make_request(self, endpoint, params=None):
        """Make authenticated request to Pinboard API."""
        if params is None:
            params = {}
        
        # Add authentication and format
        params.update({
            "auth_token": self.auth_token,
            "format": "json"
        })
        
        response = self.session.get(f"{self.base_url}/{endpoint}", params=params)
        response.raise_for_status()
        return response.json()
    
    def add_bookmark(self, url, description, extended="", tags=None, shared=True, toread=False):
        """Add a bookmark via HTTP API."""
        params = {
            "url": url,
            "description": description,
            "extended": extended,
            "shared": "yes" if shared else "no",
            "toread": "yes" if toread else "no"
        }
        
        if tags:
            params["tags"] = " ".join(tags) if isinstance(tags, list) else tags
        
        return self._make_request("posts/add", params)
    
    def get_bookmarks(self, tag=None, dt=None, url=None, results=None):
        """Get bookmarks via HTTP API."""
        params = {}
        if tag:
            params["tag"] = " ".join(tag) if isinstance(tag, list) else tag
        if dt:
            params["dt"] = dt
        if url:
            params["url"] = url
        if results:
            params["results"] = results
        
        return self._make_request("posts/get", params)
    
    def delete_bookmark(self, url):
        """Delete bookmark via HTTP API."""
        return self._make_request("posts/delete", {"url": url})
    
    def get_recent(self, count=15):
        """Get recent bookmarks via HTTP API."""
        return self._make_request("posts/recent", {"count": count})
    
    def get_all_bookmarks(self):
        """Get all bookmarks via HTTP API."""
        return self._make_request("posts/all")
    
    def get_tags(self):
        """Get all tags via HTTP API."""
        return self._make_request("tags/get")
    
    def suggest_tags(self, url):
        """Get tag suggestions via HTTP API.""" 
        return self._make_request("posts/suggest", {"url": url})
    
    def rename_tag(self, old, new):
        """Rename tag via HTTP API."""
        return self._make_request("tags/rename", {"old": old, "new": new})
    
    def delete_tag(self, tag):
        """Delete tag via HTTP API."""
        return self._make_request("tags/delete", {"tag": tag})

# Example usage
api = PinboardHTTPAPI("username:API_TOKEN")

# Add bookmark
result = api.add_bookmark(
    url="https://example.com",
    description="Example Site",
    extended="A great example website",
    tags=["example", "reference"],
    shared=True,
    toread=False
)

# Get bookmarks by tag
bookmarks = api.get_bookmarks(tag=["python", "programming"])

# Get all tags
tags = api.get_tags()

# Suggest tags for URL
suggestions = api.suggest_tags("https://github.com/python/cpython")
```

### Browser Bookmark Import
```python
def import_browser_bookmarks(pb, browser_data: str, folder_filter: str = ""):
    """Import bookmarks from browser export (HTML format)."""
    import re
    from html.parser import HTMLParser
    
    class BookmarkParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.bookmarks = []
            self.current_bookmark = {}
            
        def handle_starttag(self, tag, attrs):
            if tag.lower() == 'a':
                attrs_dict = dict(attrs)
                if 'href' in attrs_dict:
                    self.current_bookmark = {
                        'url': attrs_dict['href'],
                        'title': '',
                        'tags': []
                    }
        
        def handle_data(self, data):
            if self.current_bookmark and 'url' in self.current_bookmark:
                self.current_bookmark['title'] = data.strip()
                if self.current_bookmark['title']:
                    self.bookmarks.append(self.current_bookmark.copy())
                    self.current_bookmark = {}
    
    try:
        # Parse HTML bookmarks
        parser = BookmarkParser()
        parser.feed(browser_data)
        
        # Filter by folder if specified
        if folder_filter:
            # Simple filtering - in practice, you'd parse folder structure
            filtered_bookmarks = [
                b for b in parser.bookmarks 
                if folder_filter.lower() in browser_data.lower()
            ]
        else:
            filtered_bookmarks = parser.bookmarks
        
        # Import with rate limiting
        import time
        imported = 0
        failed = []
        
        for i, bookmark in enumerate(filtered_bookmarks[:100]):  # Limit to prevent abuse
            try:
                # Rate limiting: 1 call per 3 seconds
                if i > 0:
                    time.sleep(3)
                
                pb.posts.add(
                    url=bookmark['url'],
                    description=bookmark['title'] or bookmark['url'],
                    tags=['imported', 'browser'],
                    shared=False  # Import as private by default
                )
                imported += 1
                
            except Exception as e:
                failed.append({
                    'url': bookmark['url'],
                    'error': str(e)
                })
        
        return {
            "total_found": len(parser.bookmarks),
            "filtered": len(filtered_bookmarks),
            "imported": imported,
            "failed": len(failed),
            "failures": failed[:10]  # Show first 10 failures
        }

# Example usage
pb = pinboard.Pinboard("username:API_TOKEN")

# Read browser export file
with open('bookmarks.html', 'r') as f:
    browser_html = f.read()

# Import bookmarks
result = import_browser_bookmarks(pb, browser_html, folder_filter="Programming")
```

---

## Error Handling

### Common Error Patterns
```python
class PinboardError(Exception):
    """Base exception for Pinboard operations."""
    pass

class RateLimitError(PinboardError):
    """Rate limit exceeded."""
    pass

class AuthenticationError(PinboardError):
    """Authentication failed."""
    pass

class BookmarkNotFoundError(PinboardError):
    """Bookmark not found."""
    pass

def handle_pinboard_errors(func):
    """Decorator for consistent error handling."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e).lower()
            
            if "rate" in error_msg or "limit" in error_msg:
                raise RateLimitError("Rate limit exceeded. Please wait and try again.")
            elif "auth" in error_msg or "token" in error_msg:
                raise AuthenticationError("Authentication failed. Check your API token.")
            elif "not found" in error_msg:
                raise BookmarkNotFoundError("Bookmark not found.")
            else:
                raise PinboardError(str(e))
    return wrapper

@handle_pinboard_errors
def robust_add_bookmark(pb, rate_limiter, url: str, title: str, **kwargs):
    """Add bookmark with comprehensive error handling."""
    rate_limiter.wait_if_needed()
    
    # Validate inputs
    if not url.startswith(('http://', 'https://')):
        raise ValueError("Invalid URL format")
    
    if len(title) > 255:
        raise ValueError("Title too long (max 255 characters)")
    
    # Add bookmark
    pb.posts.add(
        url=url,
        description=title,
        extended=kwargs.get('description', ''),
        tags=kwargs.get('tags', []),
        shared=not kwargs.get('private', False),
        toread=kwargs.get('read_later', False)
    )
    
    return {
        "url": url,
        "title": title,
        "message": "Bookmark added successfully"
    }

# Example usage
pb = pinboard.Pinboard("username:API_TOKEN")
rate_limiter = PinboardRateLimiter()

try:
    result = robust_add_bookmark(
        pb, rate_limiter,
        url="https://example.com",
        title="Example Site",
        description="A great example",
        tags=["example", "test"]
    )
    print(f"Added: {result}")
except RateLimitError:
    print("Rate limited, please wait")
except AuthenticationError:
    print("Check your API token")
except ValueError as e:
    print(f"Validation error: {e}")
```

### Network Error Handling
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_robust_session():
    """Create HTTP session with retry logic."""
    session = requests.Session()
    
    # Define retry strategy
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        backoff_factor=1,
        allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"]
    )
    
    # Mount adapter with retry strategy
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

def resilient_api_call(auth_token: str, endpoint: str, params: dict = None):
    """Make resilient API call with retry logic."""
    session = create_robust_session()
    
    # Add authentication
    if not params:
        params = {}
    params["auth_token"] = auth_token
    params["format"] = "json"
    
    response = session.get(
        f"https://api.pinboard.in/v1/{endpoint}",
        params=params,
        timeout=30
    )
    
    response.raise_for_status()
    return response.json()

# Example usage
import os

try:
    data = resilient_api_call(
        os.getenv("PINBOARD_TOKEN"),
        "posts/recent",
        {"count": 10}
    )
    print(f"Got {len(data.get('posts', []))} bookmarks")
except requests.exceptions.Timeout:
    print("Request timeout - please try again")
except requests.exceptions.ConnectionError:
    print("Connection error - check your internet")
except requests.exceptions.HTTPError as e:
    if e.response.status_code >= 500:
        print("Server error - retry later")
    else:
        print(f"HTTP error: {e.response.status_code}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Production Considerations

### Environment Configuration
```python
import os

# Environment variables for Pinboard applications
REQUIRED_ENV_VARS = [
    "PINBOARD_TOKEN",      # user:API_TOKEN format
    "CACHE_DIR",           # Cache directory path (optional)
    "LOG_LEVEL",           # Logging level (optional)
]

def validate_environment():
    """Validate required environment variables."""
    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing:
        raise ValueError(f"Missing required environment variables: {missing}")

def get_pinboard_config():
    """Get Pinboard application configuration."""
    return {
        "pinboard_token_configured": bool(os.getenv("PINBOARD_TOKEN")),
        "cache_dir": os.getenv("CACHE_DIR", "/tmp/pinboard_cache"),
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "rate_limit_seconds": float(os.getenv("RATE_LIMIT_SECONDS", "3.0")),
        "environment": os.getenv("ENVIRONMENT", "development")
    }
```

### Monitoring and Metrics
```python
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta

class PinboardMetrics:
    """Collect and track metrics for Pinboard operations."""
    
    def __init__(self):
        self.request_counts = defaultdict(int)
        self.response_times = defaultdict(list)
        self.error_counts = defaultdict(int)
        self.last_errors = deque(maxlen=100)
        
    def record_request(self, operation: str, response_time: float, success: bool, error: str = None):
        """Record a request metric."""
        self.request_counts[operation] += 1
        self.response_times[operation].append(response_time)
        
        if not success:
            self.error_counts[operation] += 1
            self.last_errors.append({
                'operation': operation,
                'error': error,
                'timestamp': datetime.now().isoformat()
            })
    
    def get_metrics(self):
        """Get current metrics."""
        return {
            'total_requests': sum(self.request_counts.values()),
            'requests_by_operation': dict(self.request_counts),
            'average_response_times': {
                op: sum(times) / len(times) if times else 0
                for op, times in self.response_times.items()
            },
            'error_rates': {
                op: self.error_counts[op] / self.request_counts[op] if self.request_counts[op] > 0 else 0
                for op in self.request_counts.keys()
            },
            'recent_errors': list(self.last_errors)[-10:]  # Last 10 errors
        }

metrics = PinboardMetrics()

def track_metrics(operation: str):
    """Decorator to track operation metrics."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                response_time = time.time() - start_time
                success = result.get('success', True)
                error = result.get('error') if not success else None
                
                metrics.record_request(operation, response_time, success, error)
                return result
                
            except Exception as e:
                response_time = time.time() - start_time
                metrics.record_request(operation, response_time, False, str(e))
                raise
        return wrapper
    return decorator

def get_application_metrics(metrics):
    """Get application performance metrics."""
    return {
        "metrics": metrics.get_metrics(),
        "timestamp": datetime.now().isoformat()
    }

# Example usage
metrics = PinboardMetrics()

@track_metrics("add_bookmark")  
def tracked_add_bookmark(pb, **kwargs):
    return pb.posts.add(**kwargs)

# Use the function
pb = pinboard.Pinboard("username:API_TOKEN")
result = tracked_add_bookmark(pb, url="https://example.com", description="Test")

# View metrics
current_metrics = get_application_metrics(metrics)
```

### Backup and Export
```python
def export_all_bookmarks(pb, rate_limiter, format_type="json", include_private=False):
    """Export all bookmarks for backup."""
    rate_limiter.wait_if_needed()
    
    # Get all bookmarks
    all_bookmarks = pb.posts.all()
    
    exported_bookmarks = []
    for bookmark in all_bookmarks:
        # Skip private bookmarks if not requested
        if not include_private and not bookmark.shared:
            continue
            
        bookmark_data = {
            "url": bookmark.url,
            "title": bookmark.description,
            "description": bookmark.extended,
            "tags": list(bookmark.tags),
            "time": bookmark.time.isoformat() if bookmark.time else None,
            "private": not bookmark.shared,
            "read_later": bookmark.toread,
            "hash": bookmark.hash
        }
        exported_bookmarks.append(bookmark_data)
    
    export_data = {
        "export_timestamp": datetime.now().isoformat(),
        "total_bookmarks": len(exported_bookmarks),
        "includes_private": include_private,
        "bookmarks": exported_bookmarks
    }
    
    if format_type == "json":
        return export_data
    else:
        raise ValueError("Unsupported export format")

# Example usage
import json

pb = pinboard.Pinboard("username:API_TOKEN")
rate_limiter = PinboardRateLimiter()

# Export all public bookmarks
export_data = export_all_bookmarks(pb, rate_limiter, include_private=False)

# Save to file
with open('bookmarks_backup.json', 'w') as f:
    json.dump(export_data, f, indent=2)

print(f"Exported {export_data['total_bookmarks']} bookmarks")
```

---

This comprehensive knowledge base provides everything needed to build a robust MCP server for Pinboard bookmark management, including authentication, CRUD operations, caching, rate limiting, error handling, and production considerations.