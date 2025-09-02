#!/bin/bash

echo "🐳 Building Pinboard MCP Server Docker Image"
echo "============================================="

docker build -t pinboard-mcp:local .
