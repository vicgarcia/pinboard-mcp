'''
pinboard-mcp: MCP server for Pinboard.in bookmarks.
'''

__version__ = '2.2.1'

from pinboard_mcp.server import run

__all__ = ['run', '__version__']
