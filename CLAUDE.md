# Claude Code Session Documentation

## Project Overview
Pinboard MCP Server - A Python MCP (Model Context Protocol) server that provides read-only access to Pinboard.in bookmarks for Claude Desktop integration.

## Project Structure
```
pinboard-mcp/
├── src/
│   └── pinboard_mcp/
│       ├── __init__.py          # Package initialization
│       └── server.py            # Main MCP server implementation
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
# Build Docker image
docker build -t pinboard-mcp .

# Run with environment variable
docker run -e PINBOARD_TOKEN="username:token" pinboard-mcp
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
- `limit` (optional): Maximum bookmarks to return (default: 20, max: 100)

**Constraints:**
- Date range cannot exceed 90 days
- Rate limited to respect Pinboard's 3-second API limit
- Read-only access only

## Claude Desktop Integration

Add to Claude Desktop MCP settings:
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
        "pinboard-mcp"
      ]
    }
  }
}
```

## Implementation Notes

### Architecture Decisions
- **FastMCP**: Used for MCP server framework (simpler than raw MCP protocol)
- **Pinboard.py**: Official Python library for Pinboard API access
- **STDIO Transport**: Default for Claude Desktop compatibility
- **Rate Limiting**: 3-second delays between API calls (Pinboard requirement)
- **90-Day Limit**: Enforced to prevent excessive API usage
- **Read-Only**: Security constraint, no write operations

### Code Quality Features
- Type hints throughout
- Comprehensive error handling
- Input validation and sanitization
- Structured logging with configurable levels
- Non-root Docker execution
- Environment-based configuration

### Key Functions (`src/pinboard_mcp/server.py`)
- `setup_logging()`: Configures console logging
- `rate_limit()`: Enforces 3-second API delays
- `get_pinboard_client()`: Creates authenticated Pinboard client
- `validate_date_range()`: Validates dates and 90-day limit
- `format_bookmark_response()`: Formats bookmark data for response
- `get_bookmarks()`: Main MCP tool implementation
- `run_server()`: Main server runner with connection testing

## Session History

### Milestone 1 Completed ✅
1. **Knowledge Review**: Studied FastMCP and Pinboard API documentation
2. **Architecture Design**: Created PRD with technical requirements  
3. **Initial Implementation**: Built working server with single tool
4. **Docker Configuration**: Containerized with security best practices
5. **Code Refactoring**: Moved to professional src/ folder structure
6. **Entrypoint Setup**: Added CLI command via pyproject.toml
7. **Testing**: Validated date logic, imports, and Docker build

### Technical Achievements
- ✅ Professional Python package structure
- ✅ CLI entrypoint: `pinboard-mcp` command
- ✅ Comprehensive input validation
- ✅ Rate limiting compliance
- ✅ Docker containerization
- ✅ Environment-based configuration
- ✅ Error handling for all failure modes
- ✅ Logging with configurable levels

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
- Read-only access (by design)
- 90-day date range limit (configurable if needed)
- Single concurrent API call (due to rate limiting)
- No bookmark modification capabilities
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

**Project Status**: ✅ Milestone 1 Complete - Production Ready  
**Last Updated**: Session end (graceful conclusion)  
**Next Session**: Ready for Milestone 2 development or production deployment