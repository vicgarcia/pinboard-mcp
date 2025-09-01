# Pinboard MCP Server - Product Requirements Document

## Project Overview
A Python MCP (Model Context Protocol) server that provides read-only access to Pinboard.in bookmarks via Claude Desktop integration. The server runs in Docker with stdio transport and uses environment variables for configuration.

## Milestone 1: Basic Bookmark Retrieval

### Objective
Implement a minimal viable MCP server with a single tool for retrieving Pinboard bookmarks with date range filtering.

### Technical Requirements

#### Core Components
- **Framework**: FastMCP for MCP server implementation
- **API Integration**: Pinboard.py library for Pinboard API access
- **Transport**: STDIO mode for Claude Desktop compatibility
- **Deployment**: Docker container with runtime environment variables
- **Access Level**: Read-only operations only

#### Environment Configuration
- `PINBOARD_TOKEN`: Pinboard API token (format: `username:API_TOKEN`)
- `LOG_LEVEL`: Logging level (default: INFO)
- `CACHE_DIR`: Optional cache directory path

#### Core Tool: `get_bookmarks`

**Purpose**: Retrieve bookmarks from Pinboard within a specified date range

**Parameters**:
- `start_date` (string, optional): Start date in YYYY-MM-DD format
- `end_date` (string, optional): End date in YYYY-MM-DD format  
- `tags` (string, optional): Comma-separated tags to filter by
- `limit` (integer, optional): Maximum bookmarks to return (default: 20, max: 100)

**Validation Rules**:
- Date range cannot exceed 90 days
- Dates must be valid ISO format (YYYY-MM-DD)
- If no dates provided, returns recent bookmarks
- `end_date` must be after `start_date`

**Response Format**:
```json
{
  "count": 15,
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-01-15"
  },
  "bookmarks": [
    {
      "url": "https://example.com",
      "title": "Example Site",
      "description": "Longer description...",
      "tags": ["example", "reference"],
      "time": "2024-01-10T15:30:00Z",
      "private": false,
      "read_later": false
    }
  ],
  "filters_applied": {
    "tags": "python,programming",
    "limit": 20
  }
}
```

#### Error Handling
- Invalid API token: Return authentication error
- Rate limit exceeded: Return rate limit error with retry guidance
- Invalid date format: Return validation error
- Date range > 90 days: Return validation error
- Network errors: Return connection error with retry guidance

#### Rate Limiting
- Implement 3-second delay between Pinboard API calls
- Cache responses for 15 minutes to reduce API calls
- Log rate limit compliance

### Technical Architecture

#### Project Structure
```
pinboard-mcp/
├── main.py              # MCP server entry point
├── pyproject.toml       # Python project configuration
├── Dockerfile          # Container configuration
├── PRD.md              # This document
├── README.md           # Usage instructions
└── knowledge/          # Documentation
```

#### Dependencies
- `fastmcp`: MCP server framework
- `pinboard`: Pinboard API client
- `python-dateutil`: Date parsing and validation
- `pydantic`: Data validation

### Deployment Requirements

#### Docker Configuration
- Base image: `python:3.11-slim`
- Working directory: `/app`
- Environment variables configurable at runtime
- STDIO transport for Claude Desktop integration
- Non-root user execution

#### Claude Desktop Integration
- Server communicates via stdin/stdout
- JSON-RPC protocol via FastMCP
- Environment variables passed from Claude Desktop config

### Success Criteria

#### Functional Requirements
- [x] Single `get_bookmarks` tool implemented
- [x] Date range validation (max 90 days)
- [x] Environment-based authentication
- [x] Rate limiting compliance
- [x] Docker containerization
- [x] STDIO transport working

#### Quality Requirements
- Error handling for all failure modes
- Input validation and sanitization
- Logging for troubleshooting
- Response time < 5 seconds for typical queries
- Memory usage < 100MB

### Future Milestones (Roadmap)

#### Milestone 2: Enhanced Search
- Tag-based filtering improvements
- Full-text search across bookmarks
- Bookmark sorting options
- Advanced date range queries

#### Milestone 3: Resource Providers
- Popular tags resource
- Account statistics resource
- Recent activity summary

#### Milestone 4: Performance & Caching
- Intelligent caching strategies
- Parallel API request handling
- Response compression

### Testing Strategy
- Unit tests for date validation logic
- Integration tests with Pinboard API
- Docker container testing
- Claude Desktop integration testing

### Security Considerations
- API token handled securely via environment variables
- No token logging or exposure
- Read-only access enforcement
- Input sanitization for all parameters

### Monitoring & Observability
- Structured logging with timestamps
- API call metrics tracking
- Error rate monitoring
- Response time tracking

---

*Document Version: 1.0*  
*Last Updated: 2024-01-15*  
*Next Review: Upon Milestone 1 completion*