# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy essential files
COPY pyproject.toml ./
COPY src/ ./src/

# Install the package
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Set environment variables
ENV LOG_LEVEL=INFO

# Run the MCP server directly
CMD ["pinboard-mcp"]