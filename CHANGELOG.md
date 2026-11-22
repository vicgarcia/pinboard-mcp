## v2.1.0
New bookmarks are private by default. `add_bookmark` creates a private bookmark unless
`private=false` is passed. `update_bookmark` keeps the existing visibility when `private` is omitted.

## v2.0.0
Refactored to single-file module (`pinboard_mcp.py`). Removed src package structure.
Install via `uv tool install`. Docker uses pip install. Added `--token` arg and `--help`.

## v1.0.0
Initial release. Python package (src layout), deployed via Docker.
6 tools: get/add/update bookmarks, list/rename tags, suggest tags.
