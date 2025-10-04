# Claude Code Session Documentation

## Project Overview
Pinboard MCP Server - A minimal Python MCP (Model Context Protocol) server for accessing Pinboard.in bookmarks directly in Claude Desktop. Intentionally focused on basic bookmark operations (get, add, update, tags) to keep context usage low and let Claude handle the interpretation work.

## Project Structure
```
pinboard-mcp/
├── src/
│   └── pinboard_mcp/
│       ├── __init__.py          # Package initialization
│       ├── server.py            # Main MCP server implementation with 4 core tools
│       ├── pinboard.py          # Pinboard API client and utilities
│       └── utils.py             # Validation and helper functions
├── pyproject.toml              # Python project configuration
├── Dockerfile                  # Container configuration
├── .dockerignore              # Docker ignore patterns
├── .gitignore                 # Git ignore patterns
├── README.md                  # Project documentation
├── PRD.md                     # Product Requirements Document
└── CLAUDE.md                  # This file
```

## External Documentation

### Key References
- **FastMCP Documentation**: https://github.com/jlowin/fastmcp - Python framework for building MCP servers
- **Pinboard API**: https://pinboard.in/api/ - Official Pinboard API documentation
- **pinboard.py Library**: https://github.com/lionheart/pinboard.py - Python client library we use

## Key Commands

### Development
```bash
# Install in development mode
pip install -e .

# Run the server locally (requires PINBOARD_TOKEN env var)
pinboard-mcp

# Test basic functionality
python -c "from pinboard_mcp.server import validate_date_range; print('✓ Import successful')"
```

### Docker
```bash
# Build Docker image using build script
./build.sh

# Or manually:
docker build -t pinboard-mcp:local .
```

### Testing & Validation
```bash
# Test date validation
python -c "
from pinboard_mcp.server import validate_date_range
start, end = validate_date_range('2024-01-01', '2024-01-15')
print(f'✓ Valid date range: {start} to {end}')
"
```

## Environment Variables
- `PINBOARD_TOKEN`: Required. Format: `username:API_TOKEN` (get from https://pinboard.in/settings/password)
- `LOG_LEVEL`: Optional. Default: INFO (DEBUG, INFO, WARNING, ERROR)

## Available Tools

### `get_bookmarks`
Retrieve bookmarks from Pinboard within a specified date range.

**Parameters:**
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format  
- `tags` (optional): Comma-separated tags to filter by
- `limit` (optional): Maximum bookmarks to return (default: 200, max: 500)

**Constraints:**
- Date range cannot exceed 90 days
- Rate limited to respect Pinboard's 3-second API limit

### `update_bookmark`
Update a bookmark's properties by URL.

**Parameters:**
- `url` (required): The URL of the bookmark to update
- `title` (optional): New bookmark title
- `description` (optional): New bookmark description
- `tags` (optional): Comma-separated tags to set
- `private` (optional): Boolean - true for private, false for public
- `toread` (optional): Boolean - mark as to-read (true/false)

**Usage Notes:**
- URL serves as the unique identifier for the bookmark
- At least one optional parameter must be provided
- Returns the updated bookmark data and list of changes applied
- Rate limited to respect Pinboard's 3-second API limit

### `add_bookmark`
Create a new bookmark in Pinboard.

**Parameters:**
- `url` (required): The web address to bookmark
- `title` (required): The bookmark title/name
- `description` (optional): Extended description or notes
- `tags` (optional): Comma-separated tags to set
- `private` (optional): Boolean - true for private, false for public (default: false)
- `toread` (optional): Boolean - mark as to-read (default: false)

**Validation Features:**
- Streamlined validation trusting Pinboard API for complex checks
- Basic required field validation (URL and title)
- Tag parsing and normalization to lowercase
- Rate limited to respect Pinboard's 3-second API limit

**Returns:** Created bookmark data with success confirmation

### `get_tags`
Retrieve all tags from Pinboard with usage counts.

**Parameters:** None

**Returns:**
- List of all tags sorted by usage count (descending), then alphabetically
- Each tag includes name and count of bookmarks using it
- Full response includes total tag count and success status

**Usage Notes:**
- Returns all tags with no filtering
- Sorting prioritizes most-used tags first
- Rate limited to respect Pinboard's 3-second API limit

## Claude Desktop Integration

### Local Build Setup

First, clone and build the Docker image:
```bash
git clone https://github.com/vicgarcia/pinboard-mcp
cd pinboard-mcp
docker build -t pinboard-mcp:local .
```

Then add to Claude Desktop MCP settings:
```json
{
  "mcpServers": {
    "pinboard": {
      "command": "docker",
      "args": [
        "run", 
        "-i",
        "--rm",
        "-e", "PINBOARD_TOKEN=your-username:your-api-token",
        "pinboard-mcp:local"
      ]
    }
  }
}
```

Replace `your-username:your-api-token` with your actual Pinboard token from [settings](https://pinboard.in/settings/password).

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

### Key Functions
**`src/pinboard_mcp/pinboard.py`:**
- `get_pinboard_client()`: Creates authenticated Pinboard client
- `rate_limit()`: Enforces 3-second API delays
- `format_bookmark_response()`: Formats bookmark data for response

**`src/pinboard_mcp/server.py`:**
- `get_bookmarks()`: Retrieves bookmarks with filtering and date range validation
- `add_bookmark()`: Creates new bookmarks with streamlined validation
- `update_bookmark()`: Updates bookmark properties by URL with change tracking
- `get_tags()`: Retrieves all tags with usage counts, sorted by popularity

**`src/pinboard_mcp/utils.py`:**
- `validate_url()`: Comprehensive URL validation and normalization (available but unused after streamlining)
- `validate_date_range()`: Validates dates and enforces 90-day limit

## Session History

### Milestone 1 Completed ✅
1. **Knowledge Review**: Studied FastMCP and Pinboard API documentation
2. **Architecture Design**: Created PRD with technical requirements  
3. **Initial Implementation**: Built working server with comprehensive bookmark tools
4. **Docker Configuration**: Containerized with security best practices
5. **Code Refactoring**: Moved to professional src/ folder structure
6. **Entrypoint Setup**: Added CLI command via pyproject.toml
7. **Portfolio Optimization**: Harmonized code patterns, consistent naming, streamlined validation
8. **Testing**: Validated date logic, imports, and Docker build

### Technical Achievements
- ✅ Professional Python package structure
- ✅ CLI entrypoint: `pinboard-mcp` command
- ✅ Comprehensive input validation
- ✅ Rate limiting compliance
- ✅ Docker containerization
- ✅ Environment-based configuration
- ✅ Error handling for all failure modes
- ✅ Logging with configurable levels
- ✅ Bookmark update functionality with URL-based identification
- ✅ Multi-property updates (title, description, tags, privacy, to-read)
- ✅ Detailed change tracking and response formatting
- ✅ Bookmark creation with streamlined validation
- ✅ Portfolio-ready code with consistent patterns and naming
- ✅ Harmonized error handling and response formatting
- ✅ Clean, readable codebase optimized for professional presentation
- ✅ Tag retrieval functionality with usage statistics and smart sorting

## Future Development

### Planned Milestones
- **Milestone 2**: Enhanced search and filtering capabilities
- **Milestone 3**: Resource providers (tags, statistics)
- **Milestone 4**: Performance optimizations and caching

### Potential Improvements
- Response caching to reduce API calls
- Batch bookmark operations
- Tag suggestion functionality
- Bookmark search across title/description
- Connection pooling for better performance

## Known Limitations
- No bookmark deletion (by design - prevents accidental data loss)
- 90-day date range limit for retrieval (configurable if needed)
- Single concurrent API call (due to rate limiting)
- URL-based identification required for updates
- Requires valid Pinboard account and API token

## Troubleshooting

### Common Issues
1. **"PINBOARD_TOKEN required"**: Set environment variable with format `username:token`
2. **"Authentication failed"**: Verify token from Pinboard settings page
3. **"Rate limit exceeded"**: Server automatically handles this, wait briefly
4. **Docker build fails**: Ensure src/ directory structure is correct

### Debug Mode
Set `LOG_LEVEL=DEBUG` for detailed logging including API calls and rate limiting.

---

## Code Conventions Established

### Naming Conventions
- **Variable naming**: Descriptive names (`pinboard_client` not `pb` or `client`)
- **Function organization**: Consistent patterns across all MCP tools
- **Response formatting**: Unified structure for all API responses

### Logging Standards
- **Message format**: All log messages start lowercase except proper names (Pinboard, API, URL, MCP)
- **Log levels**: DEBUG for detailed API calls, INFO for operations, ERROR for failures
- **Consistency**: Same logging pattern across all modules

### Error Handling Philosophy
- **Streamlined validation**: Trust Pinboard API for complex validation, validate only essentials
- **Consistent responses**: All errors return `{"error": "message", "success": False}`
- **Graceful failures**: Detailed error messages without exposing internals

### Code Organization
- **Four core tools**: `get_bookmarks`, `add_bookmark`, `update_bookmark`, `get_tags`
- **Focused functionality**: Essential bookmark and tag operations only
- **Harmonized patterns**: Same structure and error handling across all functions

---

**Project Status**: ✅ Milestone 1 Complete - Portfolio Ready  
**Last Updated**: Production-ready with streamlined README and local Docker build workflow  
**Next Session**: Ready for deployment and real-world usage analysis