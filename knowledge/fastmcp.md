# FastMCP Comprehensive Knowledge Base

**Official Documentation**: https://fastmcp.com/  
**GitHub Repository**: https://github.com/jlowin/fastmcp

## Table of Contents
1. [Basic Server Creation](#basic-server-creation)
2. [Tools & Function Decoration](#tools--function-decoration)
3. [Resource Management](#resource-management)
4. [Prompt Templates](#prompt-templates)
5. [Transport Protocols](#transport-protocols)
6. [Context & Session Management](#context--session-management)
7. [Authentication & Security](#authentication--security)
8. [Testing & Development](#testing--development)
9. [Server Composition](#server-composition)
10. [Client Operations](#client-operations)
11. [Production Deployment](#production-deployment)
12. [Advanced Patterns](#advanced-patterns)
13. [FastAPI Integration](#fastapi-integration)

---

## Basic Server Creation

### Simple MCP Server
```python
from fastmcp import FastMCP

# Create server with name and emoji
mcp = FastMCP("Demo Server 🚀")

@mcp.tool
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

@mcp.tool
def greet_user(name: str, greeting: str = "Hello") -> str:
    """Greet a user with a custom greeting."""
    return f"{greeting}, {name}!"

# Run server (defaults to STDIO transport)
if __name__ == "__main__":
    mcp.run()
```

### Server with Configuration
```python
from fastmcp import FastMCP

# Advanced server configuration
mcp = FastMCP(
    name="Production API Server",
    version="1.0.0",
    description="Production-ready MCP server with advanced features"
)

# Configure server metadata
mcp.server_info.update({
    "author": "Your Name",
    "license": "MIT",
    "homepage": "https://your-server.com"
})
```

### Multi-Transport Server Setup
```python
from fastmcp import FastMCP
import asyncio

mcp = FastMCP("Multi-Transport Server")

@mcp.tool
def process_data(data: dict) -> dict:
    """Process incoming data."""
    return {"processed": True, "input": data}

# STDIO (default)
def run_stdio():
    mcp.run()

# HTTP Server
def run_http():
    mcp.run_http(host="0.0.0.0", port=8000)

# Server-Sent Events
def run_sse():
    mcp.run_sse(host="0.0.0.0", port=8001)

if __name__ == "__main__":
    # Choose transport method
    run_stdio()  # or run_http() or run_sse()
```

---

## Tools & Function Decoration

### Basic Tool Definition
```python
from typing import List, Optional
from fastmcp import FastMCP

mcp = FastMCP("Advanced Tools")

@mcp.tool
def calculate_statistics(numbers: List[float]) -> dict:
    """Calculate comprehensive statistics for a list of numbers."""
    if not numbers:
        return {"error": "Empty list provided"}
    
    return {
        "count": len(numbers),
        "sum": sum(numbers),
        "mean": sum(numbers) / len(numbers),
        "min": min(numbers),
        "max": max(numbers),
        "range": max(numbers) - min(numbers)
    }
```

### Tool with Complex Type Handling
```python
from dataclasses import dataclass
from typing import Union, Dict, Any
import json

@dataclass
class UserProfile:
    name: str
    age: int
    email: str
    preferences: Dict[str, Any]

@mcp.tool
def create_user_profile(
    name: str,
    age: int,
    email: str,
    preferences: Optional[str] = None
) -> dict:
    """Create a user profile with preferences."""
    prefs = json.loads(preferences) if preferences else {}
    
    profile = UserProfile(
        name=name,
        age=age,
        email=email,
        preferences=prefs
    )
    
    return {
        "profile_id": f"user_{hash(profile.email)}",
        "profile": {
            "name": profile.name,
            "age": profile.age, 
            "email": profile.email,
            "preferences": profile.preferences
        },
        "created": True
    }
```

### File Processing Tools
```python
import os
from pathlib import Path

@mcp.tool
def analyze_file(file_path: str) -> dict:
    """Analyze a file and return metadata."""
    path = Path(file_path)
    
    if not path.exists():
        return {"error": "File not found", "path": file_path}
    
    stat = path.stat()
    
    return {
        "path": str(path.absolute()),
        "name": path.name,
        "extension": path.suffix,
        "size_bytes": stat.st_size,
        "size_mb": round(stat.st_size / (1024 * 1024), 2),
        "modified": stat.st_mtime,
        "is_directory": path.is_dir(),
        "is_file": path.is_file()
    }

@mcp.tool
def read_text_file(file_path: str, encoding: str = "utf-8") -> dict:
    """Read and return the contents of a text file."""
    try:
        path = Path(file_path)
        content = path.read_text(encoding=encoding)
        
        return {
            "content": content,
            "lines": len(content.splitlines()),
            "characters": len(content),
            "encoding": encoding,
            "success": True
        }
    except Exception as e:
        return {"error": str(e), "success": False}
```

### API Integration Tools
```python
import httpx
import asyncio

@mcp.tool
def fetch_api_data(url: str, headers: Optional[str] = None) -> dict:
    """Fetch data from an external API."""
    try:
        parsed_headers = json.loads(headers) if headers else {}
        
        with httpx.Client() as client:
            response = client.get(url, headers=parsed_headers)
            response.raise_for_status()
            
            return {
                "status_code": response.status_code,
                "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                "headers": dict(response.headers),
                "success": True
            }
    except Exception as e:
        return {"error": str(e), "success": False}

@mcp.tool
def post_api_data(url: str, data: str, headers: Optional[str] = None) -> dict:
    """Post data to an external API."""
    try:
        parsed_headers = json.loads(headers) if headers else {}
        parsed_data = json.loads(data)
        
        with httpx.Client() as client:
            response = client.post(url, json=parsed_data, headers=parsed_headers)
            response.raise_for_status()
            
            return {
                "status_code": response.status_code,
                "response_data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                "success": True
            }
    except Exception as e:
        return {"error": str(e), "success": False}
```

---

## Resource Management

### Static Resource Providers
```python
@mcp.resource("config/database")
def get_database_config() -> str:
    """Provide database configuration."""
    config = {
        "host": "localhost",
        "port": 5432,
        "database": "production_db",
        "ssl_mode": "require"
    }
    return json.dumps(config, indent=2)

@mcp.resource("templates/email")
def get_email_templates() -> str:
    """Provide email template configurations."""
    templates = {
        "welcome": {
            "subject": "Welcome to {app_name}!",
            "body": "Hello {user_name}, welcome to our platform!"
        },
        "reset_password": {
            "subject": "Password Reset Request",
            "body": "Click here to reset your password: {reset_link}"
        }
    }
    return json.dumps(templates, indent=2)
```

### Dynamic Resource Generation
```python
from datetime import datetime, timedelta

@mcp.resource("system/status")
def get_system_status() -> str:
    """Get current system status information."""
    import psutil
    
    status = {
        "timestamp": datetime.now().isoformat(),
        "uptime": str(datetime.now() - datetime.fromtimestamp(psutil.boot_time())),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory": {
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available,
            "percent": psutil.virtual_memory().percent
        },
        "disk": {
            "total": psutil.disk_usage('/').total,
            "free": psutil.disk_usage('/').free,
            "percent": psutil.disk_usage('/').percent
        }
    }
    return json.dumps(status, indent=2)

@mcp.resource("logs/recent")
def get_recent_logs() -> str:
    """Get recent application logs."""
    # Simulate log retrieval
    logs = []
    for i in range(10):
        log_time = datetime.now() - timedelta(minutes=i*5)
        logs.append({
            "timestamp": log_time.isoformat(),
            "level": "INFO" if i % 3 != 0 else "WARNING",
            "message": f"Sample log message {i}",
            "module": f"module_{i % 3}"
        })
    
    return json.dumps({"logs": logs}, indent=2)
```

### File-Based Resources
```python
import os
from pathlib import Path

@mcp.resource("docs/api")
def get_api_documentation() -> str:
    """Load API documentation from file."""
    docs_path = Path("docs/api.md")
    if docs_path.exists():
        return docs_path.read_text()
    return "# API Documentation\n\nDocumentation not found."

@mcp.resource("config/environment")
def get_environment_config() -> str:
    """Get environment-specific configuration."""
    env = os.getenv("ENVIRONMENT", "development")
    config_path = Path(f"config/{env}.json")
    
    if config_path.exists():
        return config_path.read_text()
    
    # Default configuration
    default_config = {
        "environment": env,
        "debug": env == "development",
        "log_level": "DEBUG" if env == "development" else "INFO"
    }
    return json.dumps(default_config, indent=2)
```

---

## Prompt Templates

### Basic Prompt Templates
```python
@mcp.prompt("analyze_code")
def analyze_code_prompt() -> str:
    """Prompt for code analysis tasks."""
    return """You are a senior software engineer performing a code review.

Analyze the provided code for:
1. Code quality and best practices
2. Potential bugs or security issues
3. Performance considerations
4. Maintainability and readability

Provide specific, actionable feedback with examples where possible."""

@mcp.prompt("write_tests")
def write_tests_prompt() -> str:
    """Prompt for test writing assistance."""
    return """You are a test automation expert. 

Generate comprehensive unit tests for the provided code that:
1. Cover edge cases and error conditions
2. Follow testing best practices
3. Include proper setup and teardown
4. Use appropriate assertions
5. Are well-documented with clear test names

Include both positive and negative test cases."""
```

### Parameterized Prompts
```python
@mcp.prompt("review_pr")
def review_pull_request_prompt(
    language: str = "Python",
    focus_area: str = "general",
    severity: str = "standard"
) -> str:
    """Generate a pull request review prompt."""
    focus_mapping = {
        "security": "Focus primarily on security vulnerabilities and data protection",
        "performance": "Focus on performance optimization and efficiency",
        "architecture": "Focus on architectural patterns and design principles",
        "general": "Provide a comprehensive review covering all aspects"
    }
    
    severity_mapping = {
        "strict": "Be very thorough and strict in your review",
        "standard": "Apply standard review practices",
        "gentle": "Be constructive and encouraging in feedback"
    }
    
    return f"""You are reviewing a {language} pull request.

{focus_mapping.get(focus_area, focus_mapping["general"])}.
{severity_mapping.get(severity, severity_mapping["standard"])}.

Review the changes and provide:
1. Summary of changes
2. Potential issues or improvements
3. Code quality assessment
4. Suggestions for enhancement

Format your response clearly with sections for different types of feedback."""
```

### Context-Aware Prompts
```python
from datetime import datetime

@mcp.prompt("daily_standup")
def daily_standup_prompt(team_name: str = "Development Team") -> str:
    """Generate a daily standup meeting prompt."""
    today = datetime.now().strftime("%A, %B %d, %Y")
    
    return f"""Daily Standup for {team_name} - {today}

Please provide updates in the following format:

**Yesterday:**
- What did you accomplish yesterday?
- Any blockers or challenges faced?

**Today:**
- What are your main priorities for today?
- Any dependencies or support needed?

**Blockers:**
- Are there any impediments preventing your progress?
- How can the team help resolve them?

Keep updates concise and focus on items relevant to the team."""

@mcp.prompt("incident_response")
def incident_response_prompt(severity: str = "medium") -> str:
    """Generate an incident response prompt."""
    urgency_mapping = {
        "critical": "URGENT - System down or major functionality impacted",
        "high": "HIGH - Significant user impact or security concern", 
        "medium": "MEDIUM - Moderate impact on users or operations",
        "low": "LOW - Minor issue with minimal impact"
    }
    
    return f"""INCIDENT RESPONSE - {urgency_mapping.get(severity, urgency_mapping['medium'])}

Follow this incident response checklist:

**Immediate Actions:**
1. Assess the scope and impact
2. Determine if escalation is needed
3. Begin containment procedures

**Investigation:**
1. Gather relevant logs and metrics
2. Identify root cause
3. Document timeline of events

**Resolution:**
1. Implement fix or workaround
2. Verify resolution effectiveness
3. Monitor for additional issues

**Post-Incident:**
1. Conduct post-mortem review
2. Update documentation
3. Implement preventive measures

Please provide status updates throughout the process."""
```

---

## Transport Protocols

### STDIO Transport (Default)
```python
from fastmcp import FastMCP

mcp = FastMCP("STDIO Server")

@mcp.tool
def echo_message(message: str) -> str:
    """Echo back a message."""
    return f"Echo: {message}"

# STDIO is the default transport
if __name__ == "__main__":
    mcp.run()  # Communicates via stdin/stdout
```

### HTTP Server Transport
```python
from fastmcp import FastMCP
import uvicorn

mcp = FastMCP("HTTP API Server")

@mcp.tool
def get_server_time() -> dict:
    """Get current server time."""
    from datetime import datetime
    return {
        "server_time": datetime.now().isoformat(),
        "timezone": "UTC"
    }

@mcp.resource("api/docs")
def get_api_docs() -> str:
    """API documentation resource."""
    return """# HTTP MCP Server API
    
Available endpoints:
- GET /tools - List available tools
- POST /tools/{tool_name} - Execute a tool
- GET /resources - List available resources
- GET /resources/{resource_name} - Get a resource
"""

def run_http_server():
    """Run the server with HTTP transport."""
    # Configure HTTP server
    config = {
        "host": "0.0.0.0",
        "port": 8000,
        "log_level": "info",
        "access_log": True
    }
    
    mcp.run_http(**config)

if __name__ == "__main__":
    run_http_server()
```

### Server-Sent Events (SSE)
```python
from fastmcp import FastMCP
import asyncio
from datetime import datetime

mcp = FastMCP("SSE Real-time Server")

@mcp.tool
def start_monitoring(duration_seconds: int = 60) -> dict:
    """Start system monitoring for specified duration."""
    return {
        "monitoring_started": True,
        "duration": duration_seconds,
        "start_time": datetime.now().isoformat()
    }

@mcp.tool
def get_real_time_data() -> dict:
    """Get real-time system data."""
    import random
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu_usage": round(random.uniform(10, 90), 2),
        "memory_usage": round(random.uniform(30, 80), 2),
        "active_connections": random.randint(10, 100)
    }

def run_sse_server():
    """Run server with Server-Sent Events."""
    mcp.run_sse(
        host="0.0.0.0",
        port=8001,
        cors_origins=["*"]  # Configure CORS for web clients
    )

if __name__ == "__main__":
    run_sse_server()
```

### Custom Transport Configuration
```python
from fastmcp import FastMCP
from fastmcp.transports import StdioTransport, HttpTransport

mcp = FastMCP("Custom Transport Server")

# Configure custom STDIO transport with specific settings
stdio_transport = StdioTransport(
    buffer_size=8192,
    timeout=30.0
)

# Configure custom HTTP transport
http_transport = HttpTransport(
    host="127.0.0.1",
    port=9000,
    cors_enabled=True,
    cors_origins=["http://localhost:3000"],
    request_timeout=60.0,
    max_request_size=10 * 1024 * 1024  # 10MB
)

@mcp.tool
def health_check() -> dict:
    """Server health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "transport": "custom_configured"
    }

# Choose transport at runtime
def run_with_transport(transport_type: str = "stdio"):
    if transport_type == "http":
        mcp.run_with_transport(http_transport)
    else:
        mcp.run_with_transport(stdio_transport)
```

---

## Context & Session Management

### Context Access and Usage
```python
from fastmcp import FastMCP, Context

mcp = FastMCP("Context-Aware Server")

@mcp.tool
def log_user_action(action: str, details: dict) -> dict:
    """Log user action with context information."""
    # Access context within tool
    ctx = Context.current()
    
    log_entry = {
        "action": action,
        "details": details,
        "timestamp": datetime.now().isoformat(),
        "session_id": getattr(ctx, 'session_id', 'unknown'),
        "user_agent": getattr(ctx, 'user_agent', 'unknown')
    }
    
    # Use context's logging capability
    ctx.logger.info(f"User action: {action}", extra=log_entry)
    
    return {"logged": True, "log_id": f"log_{hash(str(log_entry))}"}

@mcp.tool  
def make_http_request(url: str, method: str = "GET") -> dict:
    """Make HTTP request using context's HTTP client."""
    ctx = Context.current()
    
    try:
        # Use context's HTTP client for requests
        if method.upper() == "GET":
            response = ctx.http.get(url)
        elif method.upper() == "POST":
            response = ctx.http.post(url)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "success": True
        }
    except Exception as e:
        ctx.logger.error(f"HTTP request failed: {e}")
        return {"error": str(e), "success": False}
```

### Session State Management
```python
from typing import Dict, Any

# Global session storage (in production, use proper session management)
SESSION_STORE: Dict[str, Dict[str, Any]] = {}

@mcp.tool
def store_session_data(key: str, value: str, session_id: str = None) -> dict:
    """Store data in user session."""
    ctx = Context.current()
    session_id = session_id or getattr(ctx, 'session_id', 'default')
    
    if session_id not in SESSION_STORE:
        SESSION_STORE[session_id] = {}
    
    SESSION_STORE[session_id][key] = value
    
    return {
        "stored": True,
        "session_id": session_id,
        "key": key,
        "session_size": len(SESSION_STORE[session_id])
    }

@mcp.tool
def get_session_data(key: str = None, session_id: str = None) -> dict:
    """Retrieve data from user session."""
    ctx = Context.current()
    session_id = session_id or getattr(ctx, 'session_id', 'default')
    
    if session_id not in SESSION_STORE:
        return {"error": "Session not found", "session_id": session_id}
    
    session_data = SESSION_STORE[session_id]
    
    if key:
        return {
            "value": session_data.get(key),
            "found": key in session_data,
            "key": key
        }
    else:
        return {
            "session_data": session_data,
            "keys": list(session_data.keys()),
            "size": len(session_data)
        }

@mcp.tool
def clear_session(session_id: str = None) -> dict:
    """Clear user session data."""
    ctx = Context.current()
    session_id = session_id or getattr(ctx, 'session_id', 'default')
    
    if session_id in SESSION_STORE:
        cleared_keys = len(SESSION_STORE[session_id])
        del SESSION_STORE[session_id]
        return {"cleared": True, "keys_removed": cleared_keys}
    
    return {"cleared": False, "message": "Session not found"}
```

### Context-Based Sampling and AI Integration
```python
@mcp.tool
def generate_smart_response(prompt: str, model: str = "gpt-3.5-turbo") -> dict:
    """Generate AI response using context's sampling capability."""
    ctx = Context.current()
    
    try:
        # Use context's sampling for AI generation
        response = ctx.sample(
            prompt=prompt,
            model=model,
            max_tokens=150,
            temperature=0.7
        )
        
        return {
            "response": response.text,
            "model_used": model,
            "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else None,
            "success": True
        }
    except Exception as e:
        ctx.logger.error(f"AI sampling failed: {e}")
        return {"error": str(e), "success": False}

@mcp.tool
def analyze_with_ai(text: str, analysis_type: str = "sentiment") -> dict:
    """Analyze text using AI with different analysis types."""
    ctx = Context.current()
    
    analysis_prompts = {
        "sentiment": f"Analyze the sentiment of this text: {text}",
        "summary": f"Provide a concise summary of this text: {text}",
        "keywords": f"Extract key terms and phrases from this text: {text}",
        "tone": f"Analyze the tone and style of this text: {text}"
    }
    
    prompt = analysis_prompts.get(analysis_type, f"Analyze this text: {text}")
    
    try:
        response = ctx.sample(
            prompt=prompt,
            model="gpt-3.5-turbo",
            max_tokens=100,
            temperature=0.3
        )
        
        return {
            "analysis": response.text,
            "type": analysis_type,
            "original_text_length": len(text),
            "success": True
        }
    except Exception as e:
        return {"error": str(e), "success": False}
```

---

## Authentication & Security

### Basic Authentication Setup
```python
from fastmcp import FastMCP
from fastmcp.security import require_auth, validate_token

mcp = FastMCP("Secure Server")

# Simple token-based authentication
VALID_TOKENS = {
    "admin_token_123": {"role": "admin", "user": "admin"},
    "user_token_456": {"role": "user", "user": "john_doe"}
}

def authenticate_request(token: str) -> dict:
    """Validate authentication token."""
    return VALID_TOKENS.get(token)

@mcp.tool
@require_auth
def admin_only_tool(action: str) -> dict:
    """Tool that requires admin authentication."""
    ctx = Context.current()
    user_info = getattr(ctx, 'user_info', {})
    
    if user_info.get('role') != 'admin':
        return {"error": "Admin access required", "authorized": False}
    
    return {
        "action_performed": action,
        "user": user_info.get('user'),
        "authorized": True
    }

@mcp.tool
def public_tool(message: str) -> dict:
    """Public tool accessible without authentication."""
    return {"message": f"Public response: {message}"}
```

### Role-Based Access Control
```python
from functools import wraps
from typing import List

def require_roles(required_roles: List[str]):
    """Decorator to require specific roles."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ctx = Context.current()
            user_info = getattr(ctx, 'user_info', {})
            user_role = user_info.get('role')
            
            if user_role not in required_roles:
                return {
                    "error": f"Access denied. Required roles: {required_roles}",
                    "user_role": user_role,
                    "authorized": False
                }
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

@mcp.tool
@require_roles(['admin', 'moderator'])
def manage_users(action: str, user_id: str) -> dict:
    """User management tool for admins and moderators."""
    ctx = Context.current()
    user_info = getattr(ctx, 'user_info', {})
    
    return {
        "action": action,
        "target_user": user_id,
        "performed_by": user_info.get('user'),
        "role": user_info.get('role'),
        "timestamp": datetime.now().isoformat()
    }

@mcp.tool
@require_roles(['user', 'admin', 'moderator'])
def authenticated_action(data: str) -> dict:
    """Tool requiring any authenticated user."""
    ctx = Context.current()
    user_info = getattr(ctx, 'user_info', {})
    
    return {
        "data_processed": data,
        "user": user_info.get('user'),
        "role": user_info.get('role')
    }
```

### API Key and Rate Limiting
```python
import time
from collections import defaultdict, deque

# Rate limiting storage
RATE_LIMITS = defaultdict(lambda: deque())
MAX_REQUESTS_PER_MINUTE = 60

def check_rate_limit(api_key: str) -> bool:
    """Check if API key has exceeded rate limit."""
    now = time.time()
    minute_ago = now - 60
    
    # Clean old requests
    requests = RATE_LIMITS[api_key]
    while requests and requests[0] < minute_ago:
        requests.popleft()
    
    # Check limit
    if len(requests) >= MAX_REQUESTS_PER_MINUTE:
        return False
    
    # Add current request
    requests.append(now)
    return True

@mcp.tool
def rate_limited_tool(data: str, api_key: str) -> dict:
    """Tool with rate limiting based on API key."""
    if not check_rate_limit(api_key):
        return {
            "error": "Rate limit exceeded",
            "limit": MAX_REQUESTS_PER_MINUTE,
            "window": "1 minute",
            "retry_after": 60
        }
    
    return {
        "processed_data": data,
        "api_key": api_key[:8] + "...",  # Partial key for logging
        "requests_remaining": MAX_REQUESTS_PER_MINUTE - len(RATE_LIMITS[api_key])
    }
```

### Secure Resource Access
```python
import hashlib
import hmac

SECRET_KEY = "your-secret-key-here"

def verify_signature(data: str, signature: str) -> bool:
    """Verify HMAC signature for secure resources."""
    expected_signature = hmac.new(
        SECRET_KEY.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)

@mcp.resource("secure/config")
def get_secure_config(signature: str = None) -> str:
    """Secure configuration resource with signature verification."""
    config_data = json.dumps({
        "database_url": "postgresql://secure-db:5432/prod",
        "api_keys": {"external_service": "sk-secret-key"},
        "encryption_key": "encrypted-key-data"
    })
    
    if not signature or not verify_signature(config_data, signature):
        return json.dumps({"error": "Invalid or missing signature"})
    
    return config_data

@mcp.tool
def access_secure_data(resource_id: str, access_token: str) -> dict:
    """Access secure data with proper authentication."""
    # Validate access token
    if not access_token.startswith("secure_"):
        return {"error": "Invalid access token format"}
    
    # Simulate secure data retrieval
    secure_data = {
        "resource_id": resource_id,
        "sensitive_info": "This is protected information",
        "access_level": "high_security",
        "accessed_at": datetime.now().isoformat()
    }
    
    return {
        "data": secure_data,
        "access_granted": True,
        "token_valid": True
    }
```

---

## Testing & Development

### In-Memory Testing Framework
```python
from fastmcp import FastMCP
from fastmcp.testing import create_test_client
import pytest

# Create server for testing
mcp = FastMCP("Test Server")

@mcp.tool
def add_numbers(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@mcp.tool
def divide_numbers(a: float, b: float) -> float:
    """Divide two numbers."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

@mcp.resource("test/data")
def get_test_data() -> str:
    """Test data resource."""
    return json.dumps({"test": True, "value": 42})

# Test cases
def test_add_numbers():
    """Test the add_numbers tool."""
    client = create_test_client(mcp)
    
    result = client.call_tool("add_numbers", {"a": 5, "b": 3})
    assert result == 8

def test_divide_numbers():
    """Test the divide_numbers tool."""
    client = create_test_client(mcp)
    
    # Test normal division
    result = client.call_tool("divide_numbers", {"a": 10.0, "b": 2.0})
    assert result == 5.0
    
    # Test division by zero
    with pytest.raises(ValueError):
        client.call_tool("divide_numbers", {"a": 10.0, "b": 0.0})

def test_resource_access():
    """Test resource retrieval."""
    client = create_test_client(mcp)
    
    resource = client.get_resource("test/data")
    data = json.loads(resource)
    assert data["test"] is True
    assert data["value"] == 42

if __name__ == "__main__":
    # Run tests
    test_add_numbers()
    test_divide_numbers()
    test_resource_access()
    print("All tests passed!")
```

### Mock and Stub Testing
```python
from unittest.mock import Mock, patch
from fastmcp.testing import MockContext

# Create server with external dependencies
mcp = FastMCP("External Dependencies Server")

@mcp.tool
def fetch_weather(city: str) -> dict:
    """Fetch weather data from external API."""
    import requests
    
    # External API call
    response = requests.get(f"http://api.weather.com/v1/weather/{city}")
    return response.json()

@mcp.tool
def send_email(to: str, subject: str, body: str) -> dict:
    """Send email using external service."""
    import smtplib
    
    # Email sending logic
    server = smtplib.SMTP('smtp.gmail.com', 587)
    # ... email sending code
    return {"sent": True, "to": to}

# Test with mocks
def test_fetch_weather_success():
    """Test weather fetching with mocked API."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "city": "New York",
        "temperature": 72,
        "condition": "sunny"
    }
    
    with patch('requests.get', return_value=mock_response):
        client = create_test_client(mcp)
        result = client.call_tool("fetch_weather", {"city": "New York"})
        
        assert result["city"] == "New York"
        assert result["temperature"] == 72

def test_send_email_mock():
    """Test email sending with mocked SMTP."""
    with patch('smtplib.SMTP') as mock_smtp:
        mock_server = Mock()
        mock_smtp.return_value = mock_server
        
        client = create_test_client(mcp)
        result = client.call_tool("send_email", {
            "to": "test@example.com",
            "subject": "Test",
            "body": "Test message"
        })
        
        assert result["sent"] is True
        mock_smtp.assert_called_once_with('smtp.gmail.com', 587)
```

### Integration Testing
```python
import asyncio
import httpx
from fastmcp import FastMCP

# Integration test server
mcp = FastMCP("Integration Test Server")

@mcp.tool
def database_operation(operation: str, data: dict) -> dict:
    """Simulate database operations."""
    # In real scenario, this would connect to actual database
    operations = {
        "create": {"id": 1, "created": True, "data": data},
        "read": {"id": 1, "data": {"name": "test", "value": 100}},
        "update": {"id": 1, "updated": True, "data": data},
        "delete": {"id": 1, "deleted": True}
    }
    return operations.get(operation, {"error": "Invalid operation"})

async def test_http_integration():
    """Test HTTP server integration."""
    # Start server in background
    import threading
    import time
    
    def run_server():
        mcp.run_http(host="127.0.0.1", port=8888)
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(2)  # Wait for server to start
    
    # Test HTTP endpoints
    async with httpx.AsyncClient() as client:
        # Test tool listing
        response = await client.get("http://127.0.0.1:8888/tools")
        assert response.status_code == 200
        tools = response.json()
        assert "database_operation" in [tool["name"] for tool in tools]
        
        # Test tool execution
        response = await client.post(
            "http://127.0.0.1:8888/tools/database_operation",
            json={"operation": "create", "data": {"name": "test"}}
        )
        assert response.status_code == 200
        result = response.json()
        assert result["created"] is True

if __name__ == "__main__":
    asyncio.run(test_http_integration())
```

### Performance and Load Testing
```python
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from fastmcp.testing import create_test_client

mcp = FastMCP("Performance Test Server")

@mcp.tool
def cpu_intensive_task(iterations: int = 1000) -> dict:
    """CPU intensive task for performance testing."""
    start_time = time.time()
    
    # Simulate CPU work
    result = 0
    for i in range(iterations):
        result += i ** 2
    
    end_time = time.time()
    return {
        "result": result,
        "iterations": iterations,
        "execution_time": end_time - start_time
    }

def test_performance():
    """Test tool performance."""
    client = create_test_client(mcp)
    
    # Single execution timing
    start_time = time.time()
    result = client.call_tool("cpu_intensive_task", {"iterations": 10000})
    execution_time = time.time() - start_time
    
    print(f"Single execution: {execution_time:.3f}s")
    assert execution_time < 1.0  # Performance assertion
    
def test_concurrent_load():
    """Test concurrent request handling."""
    client = create_test_client(mcp)
    
    def make_request():
        return client.call_tool("cpu_intensive_task", {"iterations": 1000})
    
    # Test with multiple concurrent requests
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(20)]
        results = [future.result() for future in futures]
    
    total_time = time.time() - start_time
    
    print(f"20 concurrent requests: {total_time:.3f}s")
    assert len(results) == 20
    assert all(r["iterations"] == 1000 for r in results)

if __name__ == "__main__":
    test_performance()
    test_concurrent_load()
```

---

## Server Composition

### Multi-Server Orchestration
```python
from fastmcp import FastMCP
from fastmcp.composition import ServerComposer

# Create individual specialized servers
auth_server = FastMCP("Authentication Server")
data_server = FastMCP("Data Processing Server")  
notification_server = FastMCP("Notification Server")

# Authentication server tools
@auth_server.tool
def authenticate_user(username: str, password: str) -> dict:
    """Authenticate user credentials."""
    # Simplified authentication logic
    valid_users = {"admin": "secret", "user": "password"}
    
    if valid_users.get(username) == password:
        return {
            "authenticated": True,
            "user_id": username,
            "token": f"token_{hash(username)}",
            "expires_in": 3600
        }
    return {"authenticated": False, "error": "Invalid credentials"}

@auth_server.tool
def validate_token(token: str) -> dict:
    """Validate authentication token."""
    # Simplified token validation
    if token.startswith("token_"):
        return {"valid": True, "user_id": "extracted_from_token"}
    return {"valid": False, "error": "Invalid token"}

# Data processing server tools
@data_server.tool
def process_user_data(user_data: dict, processing_type: str = "standard") -> dict:
    """Process user data with different algorithms."""
    processing_algorithms = {
        "standard": lambda data: {"processed": data, "algorithm": "standard"},
        "advanced": lambda data: {"processed": data, "algorithm": "advanced", "score": 95},
        "ml": lambda data: {"processed": data, "algorithm": "machine_learning", "confidence": 0.89}
    }
    
    processor = processing_algorithms.get(processing_type, processing_algorithms["standard"])
    result = processor(user_data)
    result["timestamp"] = datetime.now().isoformat()
    
    return result

@data_server.tool
def analyze_patterns(data_points: list) -> dict:
    """Analyze patterns in data points."""
    if not data_points:
        return {"error": "No data points provided"}
    
    analysis = {
        "count": len(data_points),
        "average": sum(data_points) / len(data_points),
        "min": min(data_points),
        "max": max(data_points),
        "trend": "increasing" if data_points[-1] > data_points[0] else "decreasing"
    }
    
    return analysis

# Notification server tools
@notification_server.tool
def send_notification(user_id: str, message: str, channel: str = "email") -> dict:
    """Send notification to user via specified channel."""
    channels = {
        "email": {"sent": True, "delivery_time": "immediate"},
        "sms": {"sent": True, "delivery_time": "immediate"},
        "push": {"sent": True, "delivery_time": "immediate"},
        "slack": {"sent": True, "delivery_time": "immediate"}
    }
    
    if channel not in channels:
        return {"error": f"Unsupported channel: {channel}"}
    
    result = channels[channel].copy()
    result.update({
        "user_id": user_id,
        "message": message,
        "channel": channel,
        "notification_id": f"notif_{hash(message)}",
        "timestamp": datetime.now().isoformat()
    })
    
    return result

@notification_server.tool
def get_notification_status(notification_id: str) -> dict:
    """Get status of a notification."""
    # Simulate notification tracking
    return {
        "notification_id": notification_id,
        "status": "delivered",
        "delivered_at": datetime.now().isoformat(),
        "read": False
    }

# Compose servers into unified service
composer = ServerComposer("Unified Service Platform")

# Add servers to composition
composer.add_server("auth", auth_server)
composer.add_server("data", data_server)  
composer.add_server("notifications", notification_server)

# Create orchestrated workflows
@composer.workflow
def complete_user_workflow(username: str, password: str, user_data: dict) -> dict:
    """Complete workflow combining authentication, processing, and notification."""
    # Step 1: Authenticate user
    auth_result = composer.call_tool("auth", "authenticate_user", {
        "username": username,
        "password": password
    })
    
    if not auth_result.get("authenticated"):
        return {"error": "Authentication failed", "step": "authentication"}
    
    # Step 2: Process user data
    processing_result = composer.call_tool("data", "process_user_data", {
        "user_data": user_data,
        "processing_type": "advanced"
    })
    
    # Step 3: Send notification
    notification_result = composer.call_tool("notifications", "send_notification", {
        "user_id": auth_result["user_id"],
        "message": f"Data processing completed with {processing_result['algorithm']} algorithm",
        "channel": "email"
    })
    
    return {
        "workflow_completed": True,
        "user_id": auth_result["user_id"],
        "processing_result": processing_result,
        "notification_sent": notification_result["sent"],
        "workflow_id": f"workflow_{hash(username + str(time.time()))}"
    }

if __name__ == "__main__":
    # Run composed server
    composer.run()
```

### Server Proxy and Load Balancing
```python
from fastmcp import FastMCP
from fastmcp.proxy import ServerProxy
import random

# Create multiple backend servers
backend_servers = []

for i in range(3):
    server = FastMCP(f"Backend Server {i+1}")
    
    @server.tool
    def process_request(data: str, server_id: int = i) -> dict:
        """Process request on backend server."""
        import time
        time.sleep(random.uniform(0.1, 0.3))  # Simulate processing time
        
        return {
            "processed_data": data,
            "server_id": server_id,
            "processing_time": random.uniform(0.1, 0.3),
            "timestamp": datetime.now().isoformat()
        }
    
    backend_servers.append(server)

# Create proxy server with load balancing
proxy = ServerProxy("Load Balanced Proxy")

# Configure load balancing strategies
class LoadBalancer:
    def __init__(self, servers):
        self.servers = servers
        self.current = 0
    
    def round_robin(self):
        """Round-robin load balancing."""
        server = self.servers[self.current]
        self.current = (self.current + 1) % len(self.servers)
        return server
    
    def least_connections(self):
        """Select server with least active connections."""
        # Simplified - in production, track actual connections
        return random.choice(self.servers)
    
    def random_selection(self):
        """Random server selection."""
        return random.choice(self.servers)

load_balancer = LoadBalancer(backend_servers)

@proxy.tool
def balanced_request(data: str, strategy: str = "round_robin") -> dict:
    """Make request with load balancing."""
    strategies = {
        "round_robin": load_balancer.round_robin,
        "least_connections": load_balancer.least_connections,
        "random": load_balancer.random_selection
    }
    
    if strategy not in strategies:
        return {"error": f"Unknown strategy: {strategy}"}
    
    # Select backend server
    selected_server = strategies[strategy]()
    
    # Forward request to selected server
    try:
        result = selected_server.call_tool("process_request", {"data": data})
        result["load_balancer_strategy"] = strategy
        result["proxy_timestamp"] = datetime.now().isoformat()
        return result
    except Exception as e:
        return {"error": str(e), "strategy": strategy}

if __name__ == "__main__":
    proxy.run()
```

---

## Client Operations

### Basic MCP Client Usage
```python
from fastmcp.client import MCPClient
import asyncio

# Synchronous client
def sync_client_example():
    """Example of synchronous MCP client usage."""
    client = MCPClient("http://localhost:8000")
    
    try:
        # Discover server capabilities
        server_info = client.get_server_info()
        print(f"Connected to: {server_info['name']}")
        
        # List available tools
        tools = client.list_tools()
        print(f"Available tools: {[tool['name'] for tool in tools]}")
        
        # List available resources
        resources = client.list_resources()
        print(f"Available resources: {[res['name'] for res in resources]}")
        
        # Execute a tool
        result = client.call_tool("add_numbers", {"a": 10, "b": 20})
        print(f"Tool result: {result}")
        
        # Get a resource
        resource_data = client.get_resource("config/database")
        print(f"Resource data: {resource_data}")
        
    finally:
        client.close()

# Asynchronous client
async def async_client_example():
    """Example of asynchronous MCP client usage."""
    from fastmcp.client import AsyncMCPClient
    
    client = AsyncMCPClient("http://localhost:8000")
    
    try:
        # Concurrent operations
        server_info_task = client.get_server_info()
        tools_task = client.list_tools()
        resources_task = client.list_resources()
        
        # Wait for all operations
        server_info, tools, resources = await asyncio.gather(
            server_info_task, tools_task, resources_task
        )
        
        print(f"Server: {server_info['name']}")
        print(f"Tools: {len(tools)}")
        print(f"Resources: {len(resources)}")
        
        # Execute multiple tools concurrently
        tasks = [
            client.call_tool("add_numbers", {"a": i, "b": i+1})
            for i in range(5)
        ]
        
        results = await asyncio.gather(*tasks)
        print(f"Concurrent results: {results}")
        
    finally:
        await client.close()

if __name__ == "__main__":
    # Run sync example
    sync_client_example()
    
    # Run async example
    asyncio.run(async_client_example())
```

### Multi-Server Client Management
```python
from fastmcp.client import MCPClient, MultiServerClient
import asyncio

class MultiServerManager:
    """Manage connections to multiple MCP servers."""
    
    def __init__(self, server_configs: dict):
        self.servers = {}
        self.clients = {}
        
        for name, config in server_configs.items():
            self.servers[name] = config
            self.clients[name] = MCPClient(config['url'])
    
    def get_server_capabilities(self) -> dict:
        """Get capabilities from all connected servers."""
        capabilities = {}
        
        for name, client in self.clients.items():
            try:
                capabilities[name] = {
                    'info': client.get_server_info(),
                    'tools': client.list_tools(),
                    'resources': client.list_resources()
                }
            except Exception as e:
                capabilities[name] = {'error': str(e)}
        
        return capabilities
    
    def call_tool_on_server(self, server_name: str, tool_name: str, params: dict) -> dict:
        """Call a specific tool on a specific server."""
        if server_name not in self.clients:
            return {'error': f'Server {server_name} not found'}
        
        try:
            return self.clients[server_name].call_tool(tool_name, params)
        except Exception as e:
            return {'error': str(e), 'server': server_name}
    
    def broadcast_tool_call(self, tool_name: str, params: dict) -> dict:
        """Call the same tool on all servers that support it."""
        results = {}
        
        for server_name, client in self.clients.items():
            try:
                # Check if server supports the tool
                tools = client.list_tools()
                tool_names = [tool['name'] for tool in tools]
                
                if tool_name in tool_names:
                    results[server_name] = client.call_tool(tool_name, params)
                else:
                    results[server_name] = {'error': f'Tool {tool_name} not supported'}
                    
            except Exception as e:
                results[server_name] = {'error': str(e)}
        
        return results
    
    def find_tool(self, tool_name: str) -> list:
        """Find which servers provide a specific tool."""
        supporting_servers = []
        
        for server_name, client in self.clients.items():
            try:
                tools = client.list_tools()
                tool_names = [tool['name'] for tool in tools]
                
                if tool_name in tool_names:
                    supporting_servers.append(server_name)
                    
            except Exception as e:
                continue
        
        return supporting_servers
    
    def close_all(self):
        """Close all client connections."""
        for client in self.clients.values():
            try:
                client.close()
            except Exception:
                pass

# Usage example
def multi_server_example():
    """Example of managing multiple MCP servers."""
    server_configs = {
        'auth_server': {'url': 'http://localhost:8001'},
        'data_server': {'url': 'http://localhost:8002'},
        'notification_server': {'url': 'http://localhost:8003'}
    }
    
    manager = MultiServerManager(server_configs)
    
    try:
        # Get all server capabilities
        capabilities = manager.get_server_capabilities()
        for server, caps in capabilities.items():
            print(f"{server}: {len(caps.get('tools', []))} tools, {len(caps.get('resources', []))} resources")
        
        # Find servers that support authentication
        auth_servers = manager.find_tool('authenticate_user')
        print(f"Authentication available on: {auth_servers}")
        
        # Call tool on specific server
        auth_result = manager.call_tool_on_server(
            'auth_server', 
            'authenticate_user',
            {'username': 'admin', 'password': 'secret'}
        )
        print(f"Authentication result: {auth_result}")
        
        # Broadcast health check to all servers
        health_results = manager.broadcast_tool_call('health_check', {})
        print(f"Health check results: {health_results}")
        
    finally:
        manager.close_all()

if __name__ == "__main__":
    multi_server_example()
```

### Client with Retry and Error Handling
```python
import time
import random
from typing import Optional, Dict, Any
from fastmcp.client import MCPClient

class RobustMCPClient:
    """MCP client with retry logic and error handling."""
    
    def __init__(self, url: str, max_retries: int = 3, retry_delay: float = 1.0):
        self.url = url
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.client: Optional[MCPClient] = None
        self._connect()
    
    def _connect(self):
        """Establish connection to MCP server."""
        for attempt in range(self.max_retries):
            try:
                self.client = MCPClient(self.url)
                # Test connection
                self.client.get_server_info()
                return
            except Exception as e:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(delay)
                    continue
                raise ConnectionError(f"Failed to connect after {self.max_retries} attempts: {e}")
    
    def call_tool_with_retry(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call tool with automatic retry on failure."""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                if not self.client:
                    self._connect()
                
                return self.client.call_tool(tool_name, params)
                
            except Exception as e:
                last_error = e
                
                # Check if error is retryable
                if self._is_retryable_error(e):
                    if attempt < self.max_retries - 1:
                        delay = self.retry_delay * (2 ** attempt)
                        time.sleep(delay)
                        
                        # Try to reconnect on connection errors
                        if self._is_connection_error(e):
                            self.client = None
                        continue
                
                # Non-retryable error or max retries reached
                break
        
        return {
            'error': f'Tool call failed after {self.max_retries} attempts',
            'last_error': str(last_error),
            'tool': tool_name,
            'params': params
        }
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """Check if error is retryable."""
        retryable_errors = [
            'timeout',
            'connection',
            'network',
            'temporary',
            '503',  # Service unavailable
            '502',  # Bad gateway
            '504'   # Gateway timeout
        ]
        
        error_str = str(error).lower()
        return any(err in error_str for err in retryable_errors)
    
    def _is_connection_error(self, error: Exception) -> bool:
        """Check if error is connection-related."""
        connection_errors = ['connection', 'network', 'timeout']
        error_str = str(error).lower()
        return any(err in error_str for err in connection_errors)
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on the server."""
        try:
            start_time = time.time()
            server_info = self.client.get_server_info() if self.client else None
            response_time = time.time() - start_time
            
            return {
                'healthy': True,
                'server_info': server_info,
                'response_time_ms': round(response_time * 1000, 2),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def close(self):
        """Close the client connection."""
        if self.client:
            try:
                self.client.close()
            except Exception:
                pass
            finally:
                self.client = None

# Usage example
def robust_client_example():
    """Example of using robust client with retry logic."""
    client = RobustMCPClient("http://localhost:8000", max_retries=3, retry_delay=1.0)
    
    try:
        # Health check
        health = client.health_check()
        print(f"Server health: {health}")
        
        # Tool calls with retry
        result1 = client.call_tool_with_retry("add_numbers", {"a": 10, "b": 20})
        print(f"Addition result: {result1}")
        
        result2 = client.call_tool_with_retry("nonexistent_tool", {"param": "value"})
        print(f"Non-existent tool result: {result2}")
        
    finally:
        client.close()

if __name__ == "__main__":
    robust_client_example()
```

---

## Production Deployment

### Production Server Configuration
```python
from fastmcp import FastMCP
import logging
import os
from pathlib import Path
import uvicorn

# Production server setup
mcp = FastMCP(
    name="Production MCP Server",
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="Production-ready MCP server with monitoring and security"
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/mcp/server.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Health monitoring
@mcp.tool
def health_check() -> dict:
    """Comprehensive health check endpoint."""
    import psutil
    import time
    
    try:
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": os.getenv("APP_VERSION", "1.0.0"),
            "uptime_seconds": time.time() - psutil.boot_time(),
            "system": {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent
            },
            "process": {
                "pid": os.getpid(),
                "memory_mb": psutil.Process().memory_info().rss / 1024 / 1024,
                "cpu_percent": psutil.Process().cpu_percent()
            }
        }
        
        # Check critical thresholds
        if health_data["system"]["memory_percent"] > 90:
            health_data["status"] = "degraded"
            health_data["warnings"] = ["High memory usage"]
        
        if health_data["system"]["cpu_percent"] > 95:
            health_data["status"] = "degraded" 
            health_data.setdefault("warnings", []).append("High CPU usage")
        
        return health_data
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool
def get_metrics() -> dict:
    """Get server metrics for monitoring."""
    # In production, integrate with proper metrics system
    return {
        "requests_total": 1000,
        "requests_per_second": 10.5,
        "average_response_time_ms": 150,
        "error_rate_percent": 0.1,
        "active_connections": 25,
        "timestamp": datetime.now().isoformat()
    }

# Configuration management
@mcp.resource("config/production")
def get_production_config() -> str:
    """Get production configuration."""
    config = {
        "database": {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "5432")),
            "name": os.getenv("DB_NAME", "production"),
            "ssl": True
        },
        "redis": {
            "host": os.getenv("REDIS_HOST", "localhost"),
            "port": int(os.getenv("REDIS_PORT", "6379")),
            "db": int(os.getenv("REDIS_DB", "0"))
        },
        "features": {
            "rate_limiting": True,
            "authentication": True,
            "logging": "INFO"
        }
    }
    return json.dumps(config, indent=2)

# Production deployment function
def deploy_production():
    """Deploy server in production mode."""
    # Environment validation
    required_env_vars = ["DB_HOST", "DB_PORT", "REDIS_HOST", "SECRET_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {missing_vars}")
    
    # Create log directory
    log_dir = Path("/var/log/mcp")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Production server configuration
    config = {
        "host": "0.0.0.0",
        "port": int(os.getenv("PORT", "8000")),
        "workers": int(os.getenv("WORKERS", "4")),
        "access_log": True,
        "log_level": "info",
        "timeout_keep_alive": 120,
        "timeout_graceful_shutdown": 30
    }
    
    logger.info(f"Starting production server with config: {config}")
    
    # Start server
    mcp.run_http(**config)

if __name__ == "__main__":
    if os.getenv("ENVIRONMENT") == "production":
        deploy_production()
    else:
        mcp.run()
```

### Docker Deployment
```dockerfile
# Dockerfile for FastMCP server
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash mcpuser
RUN chown -R mcpuser:mcpuser /app
USER mcpuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Expose port
EXPOSE 8000

# Run server
CMD ["python", "-m", "uvicorn", "main:mcp", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes Deployment
```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastmcp-server
  labels:
    app: fastmcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastmcp-server
  template:
    metadata:
      labels:
        app: fastmcp-server
    spec:
      containers:
      - name: fastmcp-server
        image: your-registry/fastmcp-server:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: DB_HOST
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: host
        - name: DB_PORT
          value: "5432"
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: secret-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: fastmcp-service
spec:
  selector:
    app: fastmcp-server
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Monitoring and Observability
```python
from fastmcp import FastMCP
import time
import logging
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Metrics collection
REQUEST_COUNT = Counter('mcp_requests_total', 'Total number of requests', ['tool', 'status'])
REQUEST_DURATION = Histogram('mcp_request_duration_seconds', 'Request duration', ['tool'])
ACTIVE_CONNECTIONS = Gauge('mcp_active_connections', 'Active connections')

mcp = FastMCP("Monitored MCP Server")

def track_metrics(func):
    """Decorator to track metrics for tools."""
    def wrapper(*args, **kwargs):
        tool_name = func.__name__
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            REQUEST_COUNT.labels(tool=tool_name, status='success').inc()
            return result
        except Exception as e:
            REQUEST_COUNT.labels(tool=tool_name, status='error').inc()
            raise
        finally:
            REQUEST_DURATION.labels(tool=tool_name).observe(time.time() - start_time)
    
    return wrapper

@mcp.tool
@track_metrics
def monitored_operation(data: str) -> dict:
    """Operation with monitoring."""
    # Simulate work
    time.sleep(0.1)
    return {"processed": data, "timestamp": datetime.now().isoformat()}

@mcp.tool
def get_prometheus_metrics() -> str:
    """Expose Prometheus metrics."""
    return generate_latest().decode('utf-8')

@mcp.resource("monitoring/dashboard")
def get_monitoring_dashboard() -> str:
    """Monitoring dashboard configuration."""
    dashboard_config = {
        "title": "FastMCP Server Monitoring",
        "panels": [
            {
                "title": "Request Rate",
                "metric": "rate(mcp_requests_total[5m])",
                "type": "graph"
            },
            {
                "title": "Request Duration",
                "metric": "histogram_quantile(0.95, mcp_request_duration_seconds)",
                "type": "graph"
            },
            {
                "title": "Error Rate",
                "metric": "rate(mcp_requests_total{status=\"error\"}[5m])",
                "type": "singlestat"
            }
        ]
    }
    return json.dumps(dashboard_config, indent=2)

if __name__ == "__main__":
    mcp.run()
```

---

## Advanced Patterns

### Server Middleware and Interceptors
```python
from fastmcp import FastMCP
from functools import wraps
import time
import uuid

mcp = FastMCP("Advanced Server with Middleware")

# Request tracking middleware
REQUEST_LOGS = {}

def request_interceptor(func):
    """Intercept and log all requests."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Log request start
        REQUEST_LOGS[request_id] = {
            "tool": func.__name__,
            "args": args,
            "kwargs": kwargs,
            "start_time": start_time,
            "status": "started"
        }
        
        try:
            result = func(*args, **kwargs)
            REQUEST_LOGS[request_id]["status"] = "completed"
            REQUEST_LOGS[request_id]["result"] = result
            return result
        except Exception as e:
            REQUEST_LOGS[request_id]["status"] = "failed"
            REQUEST_LOGS[request_id]["error"] = str(e)
            raise
        finally:
            REQUEST_LOGS[request_id]["duration"] = time.time() - start_time
    
    return wrapper

# Caching middleware
CACHE = {}

def cache_result(ttl_seconds: int = 300):
    """Cache tool results for specified TTL."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Check cache
            if cache_key in CACHE:
                cached_result, timestamp = CACHE[cache_key]
                if time.time() - timestamp < ttl_seconds:
                    return {"cached": True, "result": cached_result}
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            CACHE[cache_key] = (result, time.time())
            
            return result
        return wrapper
    return decorator

# Rate limiting middleware
RATE_LIMITS = {}

def rate_limit(max_calls: int = 10, window_seconds: int = 60):
    """Rate limit tool calls."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tool_name = func.__name__
            current_time = time.time()
            
            # Initialize rate limit tracking
            if tool_name not in RATE_LIMITS:
                RATE_LIMITS[tool_name] = []
            
            # Clean old entries
            RATE_LIMITS[tool_name] = [
                t for t in RATE_LIMITS[tool_name] 
                if current_time - t < window_seconds
            ]
            
            # Check rate limit
            if len(RATE_LIMITS[tool_name]) >= max_calls:
                return {
                    "error": "Rate limit exceeded",
                    "tool": tool_name,
                    "limit": max_calls,
                    "window": window_seconds,
                    "retry_after": window_seconds
                }
            
            # Record this call
            RATE_LIMITS[tool_name].append(current_time)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Apply middleware to tools
@mcp.tool
@request_interceptor
@cache_result(ttl_seconds=120)
@rate_limit(max_calls=5, window_seconds=60)
def expensive_computation(input_data: str, complexity: int = 1) -> dict:
    """Expensive computation with middleware protection."""
    import hashlib
    
    # Simulate expensive work
    time.sleep(complexity * 0.1)
    
    result = {
        "input": input_data,
        "complexity": complexity,
        "hash": hashlib.sha256(input_data.encode()).hexdigest(),
        "timestamp": datetime.now().isoformat()
    }
    
    return result

@mcp.tool
def get_request_logs(limit: int = 10) -> dict:
    """Get recent request logs."""
    recent_logs = dict(list(REQUEST_LOGS.items())[-limit:])
    return {
        "total_requests": len(REQUEST_LOGS),
        "recent_logs": recent_logs
    }
```

### Plugin Architecture
```python
from fastmcp import FastMCP
from abc import ABC, abstractmethod
from typing import Dict, Any
import importlib
import os

class MCPPlugin(ABC):
    """Base class for MCP plugins."""
    
    @abstractmethod
    def get_name(self) -> str:
        """Get plugin name."""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """Get plugin version."""
        pass
    
    @abstractmethod
    def register_tools(self, mcp: FastMCP):
        """Register plugin tools with MCP server."""
        pass
    
    @abstractmethod
    def register_resources(self, mcp: FastMCP):
        """Register plugin resources with MCP server."""
        pass

# Example plugins
class DatabasePlugin(MCPPlugin):
    """Database operations plugin."""
    
    def get_name(self) -> str:
        return "database"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def register_tools(self, mcp: FastMCP):
        @mcp.tool
        def db_query(query: str, params: dict = None) -> dict:
            """Execute database query."""
            # Simulate database operation
            return {
                "query": query,
                "params": params or {},
                "rows_affected": 1,
                "execution_time_ms": 50
            }
        
        @mcp.tool
        def db_health() -> dict:
            """Check database health."""
            return {
                "status": "healthy",
                "connections": 10,
                "max_connections": 100
            }
    
    def register_resources(self, mcp: FastMCP):
        @mcp.resource("database/schema")
        def get_schema() -> str:
            """Get database schema."""
            return json.dumps({
                "tables": ["users", "orders", "products"],
                "version": "1.2.3"
            })

class EmailPlugin(MCPPlugin):
    """Email operations plugin."""
    
    def get_name(self) -> str:
        return "email"
    
    def get_version(self) -> str:
        return "1.1.0"
    
    def register_tools(self, mcp: FastMCP):
        @mcp.tool
        def send_email(to: str, subject: str, body: str) -> dict:
            """Send email message."""
            return {
                "sent": True,
                "to": to,
                "subject": subject,
                "message_id": f"msg_{hash(to + subject)}",
                "timestamp": datetime.now().isoformat()
            }
        
        @mcp.tool
        def get_email_templates() -> dict:
            """Get available email templates."""
            return {
                "templates": [
                    {"name": "welcome", "subject": "Welcome!"},
                    {"name": "reset", "subject": "Password Reset"}
                ]
            }
    
    def register_resources(self, mcp: FastMCP):
        @mcp.resource("email/config")
        def get_email_config() -> str:
            """Get email configuration."""
            return json.dumps({
                "smtp_host": "smtp.example.com",
                "smtp_port": 587,
                "use_tls": True
            })

# Plugin manager
class PluginManager:
    """Manage MCP server plugins."""
    
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp
        self.plugins: Dict[str, MCPPlugin] = {}
    
    def register_plugin(self, plugin: MCPPlugin):
        """Register a plugin."""
        plugin_name = plugin.get_name()
        
        if plugin_name in self.plugins:
            raise ValueError(f"Plugin {plugin_name} already registered")
        
        # Register plugin tools and resources
        plugin.register_tools(self.mcp)
        plugin.register_resources(self.mcp)
        
        self.plugins[plugin_name] = plugin
        print(f"Registered plugin: {plugin_name} v{plugin.get_version()}")
    
    def load_plugin_from_file(self, plugin_path: str):
        """Load plugin from Python file."""
        if not os.path.exists(plugin_path):
            raise FileNotFoundError(f"Plugin file not found: {plugin_path}")
        
        # Dynamic import
        spec = importlib.util.spec_from_file_location("plugin_module", plugin_path)
        plugin_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin_module)
        
        # Find plugin class
        for attr_name in dir(plugin_module):
            attr = getattr(plugin_module, attr_name)
            if isinstance(attr, type) and issubclass(attr, MCPPlugin) and attr != MCPPlugin:
                plugin_instance = attr()
                self.register_plugin(plugin_instance)
                break
    
    def get_plugin_info(self) -> dict:
        """Get information about loaded plugins."""
        return {
            "loaded_plugins": {
                name: {
                    "name": plugin.get_name(),
                    "version": plugin.get_version()
                }
                for name, plugin in self.plugins.items()
            },
            "total_plugins": len(self.plugins)
        }

# Create server with plugin support
mcp = FastMCP("Extensible MCP Server")
plugin_manager = PluginManager(mcp)

# Register built-in plugins
plugin_manager.register_plugin(DatabasePlugin())
plugin_manager.register_plugin(EmailPlugin())

@mcp.tool
def list_plugins() -> dict:
    """List all loaded plugins."""
    return plugin_manager.get_plugin_info()

@mcp.tool
def load_plugin(plugin_path: str) -> dict:
    """Load plugin from file path."""
    try:
        plugin_manager.load_plugin_from_file(plugin_path)
        return {"loaded": True, "path": plugin_path}
    except Exception as e:
        return {"loaded": False, "error": str(e)}

if __name__ == "__main__":
    mcp.run()
```

### Event-Driven Architecture
```python
from fastmcp import FastMCP
from typing import Callable, Dict, List
import asyncio
from datetime import datetime
import json

# Event system
class EventBus:
    """Simple event bus for MCP server."""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_history: List[Dict] = []
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to an event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
    
    def publish(self, event_type: str, data: Dict):
        """Publish an event."""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "id": len(self.event_history)
        }
        
        self.event_history.append(event)
        
        # Notify subscribers
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    print(f"Event handler error: {e}")
    
    def get_events(self, event_type: str = None, limit: int = 100) -> List[Dict]:
        """Get event history."""
        events = self.event_history
        
        if event_type:
            events = [e for e in events if e["type"] == event_type]
        
        return events[-limit:]

# Create server with event system
mcp = FastMCP("Event-Driven MCP Server")
event_bus = EventBus()

# Event handlers
def log_user_action(event):
    """Log user actions."""
    print(f"User action logged: {event['data']}")

def send_notification(event):
    """Send notifications for important events."""
    if event["data"].get("priority") == "high":
        print(f"High priority notification: {event['data']['message']}")

def update_metrics(event):
    """Update system metrics based on events."""
    print(f"Metrics updated for event: {event['type']}")

# Subscribe to events
event_bus.subscribe("user.action", log_user_action)
event_bus.subscribe("user.action", update_metrics)
event_bus.subscribe("system.alert", send_notification)
event_bus.subscribe("system.alert", update_metrics)

# Tools that publish events
@mcp.tool
def create_user(username: str, email: str) -> dict:
    """Create a new user and publish event."""
    user_data = {
        "username": username,
        "email": email,
        "created_at": datetime.now().isoformat(),
        "id": hash(username + email)
    }
    
    # Publish user creation event
    event_bus.publish("user.created", {
        "user": user_data,
        "action": "create_user",
        "priority": "normal"
    })
    
    return {"user_created": True, "user": user_data}

@mcp.tool
def process_order(order_id: str, user_id: str, amount: float) -> dict:
    """Process an order and publish events."""
    order_data = {
        "order_id": order_id,
        "user_id": user_id,
        "amount": amount,
        "status": "processed",
        "processed_at": datetime.now().isoformat()
    }
    
    # Publish multiple events
    event_bus.publish("order.processed", {
        "order": order_data,
        "priority": "high" if amount > 1000 else "normal"
    })
    
    event_bus.publish("user.action", {
        "user_id": user_id,
        "action": "order_processed",
        "order_id": order_id,
        "amount": amount
    })
    
    return {"order_processed": True, "order": order_data}

@mcp.tool
def trigger_system_alert(message: str, severity: str = "medium") -> dict:
    """Trigger a system alert event."""
    alert_data = {
        "message": message,
        "severity": severity,
        "priority": "high" if severity in ["high", "critical"] else "normal",
        "triggered_at": datetime.now().isoformat()
    }
    
    event_bus.publish("system.alert", alert_data)
    
    return {"alert_triggered": True, "alert": alert_data}

@mcp.tool
def get_event_history(event_type: str = None, limit: int = 50) -> dict:
    """Get event history."""
    events = event_bus.get_events(event_type, limit)
    
    return {
        "events": events,
        "total_events": len(event_bus.event_history),
        "filtered_by": event_type,
        "limit": limit
    }

@mcp.resource("events/types")
def get_event_types() -> str:
    """Get available event types."""
    event_types = set(event["type"] for event in event_bus.event_history)
    
    return json.dumps({
        "event_types": list(event_types),
        "total_types": len(event_types),
        "subscribers": {
            event_type: len(handlers) 
            for event_type, handlers in event_bus.subscribers.items()
        }
    })

if __name__ == "__main__":
    mcp.run()
```

---

## FastAPI Integration

FastMCP provides seamless integration with FastAPI for building hybrid servers that support both MCP protocol and HTTP REST APIs. This enables creating unified applications that serve AI agents via MCP while also providing direct HTTP access.

### Mounting FastMCP into FastAPI

The official pattern mounts FastMCP as a sub-application within FastAPI:

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastmcp import FastMCP
import uvicorn

# Create FastAPI app for HTTP endpoints
app = FastAPI(title="Hybrid Server", version="1.0.0")

# Create FastMCP server for AI agent tools
mcp = FastMCP("AI Tools Server", version="1.0.0")

# Register MCP tools
@mcp.tool
def process_data(data: str) -> dict:
    """Process data via MCP protocol."""
    return {"processed": data, "method": "mcp"}

# Add FastAPI HTTP endpoints
@app.get("/api/process/{data}")
async def http_process_data(data: str):
    """Process data via HTTP REST API."""
    return {"processed": data, "method": "http"}

# Mount FastMCP into FastAPI
mcp_app = mcp.http_app(path='/mcp')
app = FastAPI(lifespan=mcp_app.lifespan, title="Hybrid Server")
app.mount("/mcp", mcp_app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

### Shared Data Services Pattern

Create unified data services that both MCP tools and FastAPI endpoints can use:

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastmcp import FastMCP
import asyncio
import logging

logger = logging.getLogger(__name__)

class UnifiedDataService:
    """Shared data service for both MCP and HTTP operations."""
    
    def __init__(self):
        self.cache = {}
        self.logger = logging.getLogger(__name__)
    
    async def get_data(self, key: str) -> dict:
        """Common data fetching logic."""
        if key in self.cache:
            self.logger.info(f"cache hit for key: {key}")
            return self.cache[key]
        
        # Simulate async data fetching
        await asyncio.sleep(0.1)
        data = {"key": key, "value": f"processed_{key}", "source": "database"}
        
        self.cache[key] = data
        self.logger.info(f"data cached for key: {key}")
        return data
    
    async def process_data(self, data: str) -> dict:
        """Common data processing logic."""
        processed = await self.get_data(data)
        return {
            "original": data,
            "processed": processed,
            "timestamp": "2025-08-03T05:30:00Z"
        }

# Initialize shared service
data_service = UnifiedDataService()

# FastAPI application
app = FastAPI(title="Hybrid Server", version="1.0.0")

# HTTP endpoints using shared service
@app.get("/api/data/{key}")
async def get_data_endpoint(key: str):
    """HTTP endpoint for data retrieval."""
    try:
        result = await data_service.get_data(key)
        return {"success": True, "data": result, "method": "http"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process")
async def process_data_endpoint(data: dict):
    """HTTP endpoint for data processing."""
    try:
        result = await data_service.process_data(data.get("input", ""))
        return {"success": True, "result": result, "method": "http"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# FastMCP server using shared service
mcp = FastMCP("Data Processing MCP", version="1.0.0")

@mcp.tool
async def get_data_tool(key: str) -> dict:
    """MCP tool for data retrieval using shared service."""
    logger.info(f"mcp data request for key: {key}")
    result = await data_service.get_data(key)
    return {"success": True, "data": result, "method": "mcp"}

@mcp.tool
async def process_data_tool(input_data: str) -> dict:
    """MCP tool for data processing using shared service."""
    logger.info(f"mcp processing request for: {input_data}")
    result = await data_service.process_data(input_data)
    return {"success": True, "result": result, "method": "mcp"}

# Mount MCP into FastAPI
mcp_app = mcp.http_app(path='/mcp')
app = FastAPI(lifespan=mcp_app.lifespan, title="Hybrid Data Server")
app.mount("/mcp", mcp_app)
```

### Media Serving Pattern

Perfect for serving visual content like images, charts, or files where MCP returns URLs to HTTP endpoints:

```python
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
from fastmcp import FastMCP
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import io
import base64

app = FastAPI(title="Media Server", version="1.0.0")

class MediaService:
    """Shared media generation service."""
    
    def __init__(self):
        self.cache = {}
    
    def generate_image(self, identifier: str, media_type: str) -> bytes:
        """Generate image data."""
        cache_key = f"{identifier}_{media_type}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Create matplotlib image
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot([1, 2, 3, 4, 5], [1, 4, 2, 3, 5], 'b-', linewidth=2)
        ax.set_title(f"{identifier} {media_type.title()}")
        ax.set_xlabel("X Axis")
        ax.set_ylabel("Y Axis")
        ax.grid(True, alpha=0.3)
        
        # Convert to PNG bytes
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        png_data = buffer.getvalue()
        plt.close(fig)
        
        # Cache the result
        self.cache[cache_key] = png_data
        return png_data

media_service = MediaService()

# HTTP endpoint for serving images
@app.get("/media/{media_type}/{identifier}")
async def serve_media(
    identifier: str,
    media_type: str,
    width: int = Query(800, ge=400, le=1200),
    height: int = Query(600, ge=300, le=800)
):
    """Serve image via HTTP."""
    try:
        image_data = media_service.generate_image(identifier, media_type)
        
        return Response(
            content=image_data,
            media_type="image/png",
            headers={
                "Cache-Control": "public, max-age=3600",
                "Content-Disposition": f"inline; filename={identifier}_{media_type}.png"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# FastMCP server
mcp = FastMCP("Media Generator MCP", version="1.0.0")

@mcp.tool
def generate_media_url(identifier: str, media_type: str = "chart") -> dict:
    """Generate media URL for visualization."""
    base_url = "http://localhost:8080"
    media_url = f"{base_url}/media/{media_type}/{identifier}"
    
    return {
        "type": "text",
        "text": f"![{identifier} {media_type.title()}]({media_url})",
        "media_url": media_url,
        "identifier": identifier,
        "media_type": media_type
    }

@mcp.tool
def create_visualization_url(name: str, viz_type: str = "graph") -> dict:
    """Create visualization URL."""
    base_url = "http://localhost:8080"
    viz_url = f"{base_url}/media/{viz_type}/{name}"
    
    return {
        "type": "text", 
        "text": f"![{name} {viz_type.title()}]({viz_url})",
        "visualization_url": viz_url,
        "name": name,
        "type": viz_type
    }

# Mount MCP into FastAPI
mcp_app = mcp.http_app(path='/mcp')
app = FastAPI(lifespan=mcp_app.lifespan, title="Media Hybrid Server")
app.mount("/mcp", mcp_app)
```

### Multi-Transport Support

Support both MCP protocols (STDIO for Claude Desktop) and HTTP simultaneously:

```python
from fastapi import FastAPI, HTTPException
from fastmcp import FastMCP
import uvicorn
import os
import logging

logger = logging.getLogger(__name__)

# Shared business logic
class BusinessService:
    def __init__(self):
        self.data_store = {}
    
    def create_item(self, name: str, value: str) -> dict:
        item_id = f"item_{len(self.data_store) + 1}"
        item = {
            "id": item_id,
            "name": name,
            "value": value,
            "created_at": "2025-08-03T05:30:00Z"
        }
        self.data_store[item_id] = item
        return item
    
    def get_item(self, item_id: str) -> dict:
        return self.data_store.get(item_id)
    
    def list_items(self) -> list:
        return list(self.data_store.values())

service = BusinessService()

# FastAPI for HTTP clients
app = FastAPI(title="Multi-Transport Server", version="1.0.0")

@app.post("/api/items")
async def create_item_http(item: dict):
    result = service.create_item(item["name"], item["value"])
    return {"success": True, "item": result, "transport": "http"}

@app.get("/api/items/{item_id}")
async def get_item_http(item_id: str):
    item = service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"success": True, "item": item, "transport": "http"}

@app.get("/api/items")
async def list_items_http():
    items = service.list_items()
    return {"success": True, "items": items, "count": len(items), "transport": "http"}

# FastMCP for AI agents
mcp = FastMCP("Business Logic MCP", version="1.0.0")

@mcp.tool
def create_item_mcp(name: str, value: str) -> dict:
    """Create a new item via MCP."""
    logger.info(f"creating item via mcp: {name}")
    result = service.create_item(name, value)
    return {"success": True, "item": result, "transport": "mcp"}

@mcp.tool
def get_item_mcp(item_id: str) -> dict:
    """Get an item by ID via MCP."""
    logger.info(f"retrieving item via mcp: {item_id}")
    item = service.get_item(item_id)
    if not item:
        return {"success": False, "error": "Item not found", "transport": "mcp"}
    return {"success": True, "item": item, "transport": "mcp"}

@mcp.tool
def list_items_mcp() -> dict:
    """List all items via MCP."""
    logger.info("listing all items via mcp")
    items = service.list_items()
    return {"success": True, "items": items, "count": len(items), "transport": "mcp"}

def start_server():
    """Start server in appropriate mode based on environment."""
    transport = os.environ.get("MCP_TRANSPORT", "stdio").lower()
    
    if transport == "stdio":
        # STDIO mode for Claude Desktop
        logger.info("starting mcp server in stdio mode")
        mcp.run()
    elif transport == "http":
        # HTTP mode with both FastAPI and MCP endpoints
        logger.info("starting hybrid server in http mode")
        mcp_app = mcp.http_app(path='/mcp')
        app = FastAPI(lifespan=mcp_app.lifespan, title="Multi-Transport Server")
        app.mount("/mcp", mcp_app)
        uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
    else:
        raise ValueError(f"unsupported transport: {transport}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_server()
```

### Docker Configuration for Hybrid Servers

Docker setup supporting both STDIO and HTTP modes:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose HTTP port (used when MCP_TRANSPORT=http)
EXPOSE 8080

# Default to STDIO mode for Claude Desktop
ENV MCP_TRANSPORT=stdio

# Start server based on transport mode
CMD ["python", "-m", "your_package.hybrid_server"]
```

### Claude Desktop Configuration

Configuration for hybrid servers supporting both STDIO and HTTP:

```json
{
  "mcpServers": {
    "hybrid-server": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i", "-p", "8080:8080",
        "-e", "MCP_TRANSPORT=stdio",
        "-v", "hybrid-cache:/app/cache",
        "hybrid-server"
      ]
    }
  }
}
```

### Production Deployment Considerations

- **CORS Configuration**: Enable CORS for browser access to HTTP endpoints
- **Authentication**: Implement proper auth for both MCP and HTTP routes
- **Rate Limiting**: Apply rate limits to prevent abuse
- **Monitoring**: Track both MCP tool calls and HTTP requests
- **Caching**: Implement shared caching for both protocols
- **Health Checks**: Provide health endpoints for load balancers

This FastAPI integration pattern enables building powerful hybrid servers that serve both AI agents via MCP and traditional clients via HTTP REST APIs, sharing common business logic and data services.

```

This comprehensive FastMCP knowledge base provides deep insights into building production-ready MCP servers with advanced features, following the same depth and practical approach as the yfinance example.