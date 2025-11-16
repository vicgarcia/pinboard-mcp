# Claude Code Session Documentation

## Project Overview
Pinboard MCP Server - A minimal Python MCP server for accessing Pinboard.in bookmarks in Claude Desktop. Built with FastMCP, implements 6 core tools: get/add/update bookmarks, list/rename tags, and suggest tags. Intentionally minimal to keep context usage low and let Claude handle interpretation.

## Project Structure
```
pinboard-mcp/
├── src/pinboard_mcp/
│   ├── __init__.py          # Package marker
│   ├── server.py            # MCP tools + run() entry point
│   ├── pinboard.py          # API client and formatting helpers
│   └── utils.py             # Validation functions
├── pyproject.toml           # Entry point: pinboard_mcp.server:run
├── Dockerfile               # Container configuration
└── README.md                # User-facing documentation
```

## External Documentation

### Key References
- **FastMCP Documentation**: https://github.com/jlowin/fastmcp - Python framework for building MCP servers
- **Pinboard API**: https://pinboard.in/api/ - Official Pinboard API documentation
- **pinboard.py Library**: https://github.com/lionheart/pinboard.py - Python client library we use

## Quick Reference

### Development Commands
```bash
pip install -e .                    # Install in dev mode
pinboard-mcp                        # Run server (requires PINBOARD_TOKEN)
docker build -t pinboard-mcp:local . # Build Docker image
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
- **FastMCP**: Used for MCP server framework (simpler than raw MCP protocol)
- **Pinboard.py**: Official Python library for Pinboard API access
- **STDIO Transport**: Default for Claude Desktop compatibility
- **Rate Limiting**: 3-second delays between API calls (Pinboard requirement)
- **90-Day Limit**: Enforced to prevent excessive API usage
- **Selective Write Access**: Creation and update operations only (no deletion for safety)

### Code Quality Features
- Type hints throughout
- Consistent error handling patterns
- Streamlined validation (trusting API where appropriate)
- Structured logging with configurable levels (all lowercase except proper names)
- Consistent variable naming (`pinboard_client` for clarity)
- Harmonized code patterns across all functions
- Non-root Docker execution
- Environment-based configuration
- **Helper functions in pinboard.py**: All formatting/normalization logic centralized for reusability
- **Clean separation of concerns**: MCP orchestration in server.py, Pinboard-specific logic in pinboard.py

### Module Organization

**`server.py`** - MCP tool definitions and orchestration
- 6 tool functions decorated with `@mcp.tool()`
- `run()` entry point: logging setup, auth validation, server start

**`pinboard.py`** - API client and formatting helpers
- `get_pinboard_client()` - Auth client creation
- `rate_limit()` - 3-second delay enforcement
- Helper formatters: `format_bookmark_response()`, `format_tags_response()`, `format_suggest_response()`
- Tag utilities: `parse_tags()`, `normalize_tag()`

**`utils.py`** - Validation functions
- `validate_date_range()` - Date parsing and 90-day limit
- `validate_url()` - Unused after streamlining validation

## Design Decisions

### What We Built
- **Minimal tool set**: 6 core operations only (no deletion by design)
- **90-day limit**: Prevent excessive API usage
- **Rate limiting**: 3-second delays (Pinboard requirement)
- **Streamlined validation**: Trust API, validate essentials only
- **Helper functions**: Formatting logic in pinboard.py, not server.py
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

### Module Patterns
- **server.py**: MCP tool orchestration, minimal logic
- **pinboard.py**: API client, formatting, normalization
- **utils.py**: Standalone validation functions
- **DRY principle**: Extract formatters as helpers, reuse across tools

### Entry Point Flow
```python
run()  # server.py
  → logging.basicConfig(...)
  → get_pinboard_client()  # Validate auth
  → mcp.run()  # Start FastMCP server
```

---

**Status**: ✅ Production Ready - Deployed to ghcr.io
**Last Updated**: 2025-01-15 - README aligned with public registry workflow