# Dockerfile for Glama's automated safety/quality checks.
# Glama builds this image, starts the MCP server over stdio, and runs
# introspection (initialize + tools/list). Tools are registered at import time,
# so introspection succeeds with no network or secrets. Live signal data is
# fetched lazily from the public coinbucha.com snapshots only when a tool is
# actually called.
FROM python:3.12-slim

WORKDIR /app

# Install deps first for layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App: the stdio MCP server + the public methodology it serves as a resource.
COPY server.py .
COPY docs ./docs

# FastMCP speaks stdio by default; Glama's inspector connects over stdio.
CMD ["python", "server.py"]
