FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY pinboard_mcp.py .

RUN pip install --no-cache-dir .

CMD ["pinboard-mcp"]
