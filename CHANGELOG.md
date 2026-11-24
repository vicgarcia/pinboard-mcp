## v2.2.0
Server instructions: bookmarks stay private unless asked, reuse the user's existing tags, don't read
the whole list back, and confirm before renaming a tag. Every tool has annotations (read-only, adds,
or changes; none open world), a fuller description, and a schema description for every argument,
declared with `Field` so it no longer depends on the fastmcp version. Requires `fastmcp>=3.0.0` and
declares `pydantic>=2.0`.

## v2.1.0
New bookmarks are private by default. `add_bookmark` creates a private bookmark unless
`private=false` is passed. `update_bookmark` keeps the existing visibility when `private` is omitted.

## v2.0.0
Refactored to single-file module (`pinboard_mcp.py`). Removed src package structure.
Install via `uv tool install`. Docker uses pip install. Added `--token` arg and `--help`.

## v1.0.0
Initial release. Python package (src layout), deployed via Docker.
6 tools: get/add/update bookmarks, list/rename tags, suggest tags.
