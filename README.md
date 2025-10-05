I've been using [Pinboard](https://pinboard.in]) for years to save bookmarks. I've recently been working on a project to explore business operations data from Claude Desktop with an MCP server. Inspired by this, I've been experimenting with ideas for personal productivity tools to build for myself.

This MCP server implements a minimal set of tools for interacting with the [pinboard api](https://pinboard.in/api). There are tools to get/add/update bookmarks and list/rename tags.

Once set up, you can make queries like:

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

### get_tags

retrieve all tags with usage counts

**returns:**
- list of all tags sorted by usage count (descending)
- each tag includes name and count of bookmarks using it

**example usage in claude:**
> "show me all my tags and how often i use them"

### rename_tag

rename a tag across all bookmarks

**parameters:**
- `old_tag` (required): existing tag name to rename
- `new_tag` (required): new tag name

**validation:**
- both tags must be non-empty
- tags are normalized to lowercase
- old and new tags cannot be identical

**example usage in claude:**
> "rename the tag 'ppython' to 'python'"

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
