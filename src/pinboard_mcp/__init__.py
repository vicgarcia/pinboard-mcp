'''
pinboard-mcp: MCP server for Pinboard.in bookmarks.
'''

__version__ = '2.0.0'

from pinboard_mcp.server import run

__all__ = ['run', '__version__']
