I've been using pinboard for years to save bookmarks and wanted an easy way to access them directly in Claude Desktop.

The MCP server is intentionally minimal. I expose only the most basic bookmark operations (get, add, update) without any opinionated filtering or analysis features. This keeps the context usage low and lets claude do the interpretation work.

Once set up, you can ask Claude things like:

- "show me all my bookmarks from december 2023"
- "what were the main topics i was bookmarking last month?"
- "find bookmarks tagged with 'python' from this year"
- "analyze my bookmarking patterns over the last few weeks"

## setup

### clone the repo and build the docker image

clone the repo
```
git clone https://github.com/vicgarcia/pinboard-mcp.git
cd pinboard-mcp
```

build the docker image
```
docker build -t pinboard-mcp:local .
```

### get your pinboard api token

go to [pinboard settings](https://pinboard.in/settings/password) and copy your api token (format: `username:1234567890ABCDEF1234567890ABCDEF`)

### setup mcp server in claude desktop

add this to your claude desktop mcp settings:

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
        "pinboard-mcp:local"
      ]
    }
  }
}
```

replace `your-username:your-api-token` with your actual pinboard token

## features

### get_bookmarks

retrieve bookmarks within a date range

**parameters:**
- `start_date` (optional): start date in yyyy-mm-dd format
- `end_date` (optional): end date in yyyy-mm-dd format
- `tags` (optional): comma-separated tags to filter by
- `limit` (optional): max bookmarks to return (default: 200, max: 500)

**constraints:**
- date range cannot exceed 90 days
- rate limited to respect pinboard's 3-second api limit

**example usage in claude:**
> "get my bookmarks from last week with the tag 'python'"

### add_bookmark

create a new bookmark

**parameters:**
- `url` (required): web address to bookmark
- `title` (required): bookmark title
- `description` (optional): extended description
- `tags` (optional): comma-separated tags
- `private` (optional): true for private, false for public (default: false)
- `toread` (optional): mark as to-read (default: false)

**example usage in claude:**
> "bookmark https://example.com with title 'interesting article' and tags 'research, ai'"

### update_bookmark

update an existing bookmark by url

**parameters:**
- `url` (required): url of bookmark to update
- `title` (optional): new title
- `description` (optional): new description
- `tags` (optional): new tags (replaces existing)
- `private` (optional): change privacy setting
- `toread` (optional): change to-read status

**example usage in claude:**
> "update the bookmark for https://example.com to add the tag 'important'"

## dev

if you want to work on this locally:

```bash
git clone https://github.com/vicgarcia/pinboard-mcp
cd pinboard-mcp

# install dependencies
pip install -e .
```

### project structure

```
src/
  pinboard_mcp/
    __init__.py       # server startup and connection testing
    server.py         # mcp tools implementation
    pinboard.py       # pinboard api client and utilities
    utils.py          # validation helpers
```

### building docker image

```bash
./build.sh
```
