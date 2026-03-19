# Claude Code Session Documentation

## Project Overview
Pinboard MCP Server - A Python MCP server for accessing Pinboard.in bookmarks in Claude Desktop. Built with FastMCP, implements 6 core tools: get/add/update bookmarks, list/rename tags, and suggest tags. Intentionally minimal to keep context usage low and let Claude handle interpretation.

Multi-file package installable via `uv tool install`.

## Project Structure
```
pinboard-mcp/
├── src/pinboard_mcp/
│   ├── __init__.py         # version and run() export
│   ├── schema.py           # Bookmark dataclass, tag utilities, response helpers
│   ├── pinboard_client.py  # PinboardClient context manager with rate limiting
│   └── server.py           # FastMCP server, tools, arg parsing, entry point
├── pyproject.toml          # package metadata and dependencies
├── Dockerfile              # docker deployment
├── README.md               # user-facing documentation
└── CLAUDE.md               # this file
```

## External Documentation

### Key References
- **FastMCP Documentation**: https://github.com/jlowin/fastmcp - Python framework for building MCP servers
- **Pinboard API**: https://pinboard.in/api/ - Official Pinboard API documentation
- **pinboard.py Library**: https://github.com/lionheart/pinboard.py - Python client library we use

## Quick Reference

### Development Commands
```bash
uv tool install --editable .                    # install in dev mode
PINBOARD_TOKEN=user:token pinboard-mcp          # run
docker build -t pinboard-mcp:local .            # build docker image
```

### Installation
```bash
uv tool install git+https://github.com/vicgarcia/pinboard-mcp
```

### Environment Variables
- `PINBOARD_TOKEN`: Required. Format: `username:API_TOKEN`
- `LOG_LEVEL`: Optional. DEBUG or INFO (default: INFO)

## Tools Overview
Six core MCP tools (see README.md for full documentation):
- `get_bookmarks` - Retrieve with date/tag filtering (90-day limit)
- `add_bookmark` - Create new bookmarks
- `update_bookmark` - Update by URL with change tracking
- `get_tags` - List all tags with usage counts
- `rename_tag` - Rename across all bookmarks
- `suggest_tags` - Get popular/recommended tags for URL

All tools respect Pinboard's 3-second rate limit.

## Implementation Notes

### Architecture Decisions
- **Multi-file package**: Clean separation of concerns following Python best practices
  - `schema.py`: Data models and utilities (no API dependencies)
  - `pinboard_client.py`: API client with context manager pattern
  - `server.py`: MCP tools and entry point
- **FastMCP**: Used for MCP server framework (simpler than raw MCP protocol)
- **Pinboard.py**: Official Python library for Pinboard API access
- **STDIO Transport**: Default for Claude Desktop compatibility
- **Rate Limiting**: 3-second delays between API calls (Pinboard requirement)
- **90-Day Limit**: Enforced to prevent excessive API usage
- **Selective Write Access**: Creation and update operations only (no deletion for safety)

### Code Quality Features
- Type hints throughout
- Consistent error handling patterns
- Dataclasses for structured data (Bookmark, TagInfo)
- Context manager pattern for API client
- Streamlined validation (trusting API where appropriate)
- Structured logging with configurable levels (all lowercase except proper names)

### Module Organization

**schema.py** — Data models and utilities
- `Bookmark` dataclass with `from_api()` and `to_dict()`
- `TagInfo` dataclass for tag/count pairs
- Tag parsing and normalization utilities
- Date validation with configurable max range
- Standardized response helpers

**pinboard_client.py** — API client
- `PinboardClient` context manager
- Built-in rate limiting (3 seconds between calls)
- All Pinboard API operations: bookmarks, tags
- `PinboardError` exception class

**server.py** — MCP server
- FastMCP instance with 6 tool definitions
- Argument parsing and entry point
- Error handling and response formatting

### Entry Point Flow
```python
run()
  → logging.basicConfig(...)
  → parse_args()
  → PinboardClient(token)
  → client.test_connection()
  → mcp.run()  # Start FastMCP server
```

## Design Decisions

### What We Built
- **Minimal tool set**: 6 core operations only (no deletion by design)
- **90-day limit**: Prevent excessive API usage
- **Rate limiting**: 3-second delays (Pinboard requirement)
- **Streamlined validation**: Trust API, validate essentials only
- **STDIO transport**: Claude Desktop compatibility

### What We Didn't Build
- No caching (future optimization)
- No batch operations (simplicity)
- No deletion tools (safety)
- No complex search (let Claude interpret)
- No bookmark notes/content (use description field)

## Code Conventions

### Naming & Style
- Descriptive variable names (`pinboard_client` not `pb`)
- Lowercase log messages except proper names (Pinboard, API, URL)
- Consistent error responses: `{"error": "message", "success": False}`
