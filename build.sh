#!/bin/bash
# Build script for Pinboard MCP Server Docker image

echo "🐳 Building Pinboard MCP Server Docker Image"
echo "============================================="

docker build -t pinboard-mcp:local .