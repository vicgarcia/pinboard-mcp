'''
tests for what clients see about each tool: annotations, descriptions and server instructions.
'''

import asyncio

import pytest

from pinboard_mcp import server


READ_ONLY = {'get_bookmarks', 'get_tags', 'suggest_tags'}
ADDS = {'add_bookmark'}
CHANGES = {'update_bookmark', 'rename_tag'}


@pytest.fixture(scope='module')
def tools():
    return asyncio.run(server.mcp.list_tools())


def annotations(tool):
    ''' the annotations as clients receive them; the python field names differ between mcp sdk versions '''
    return tool.to_mcp_tool().model_dump(by_alias=True, exclude_none=True, mode='json').get('annotations')


def test_every_tool_is_annotated(tools):
    assert {tool.name for tool in tools} == READ_ONLY | ADDS | CHANGES
    for tool in tools:
        hints = annotations(tool)
        assert hints, tool.name
        assert hints['openWorldHint'] is False, tool.name
        if tool.name in READ_ONLY:
            assert hints['readOnlyHint'] is True, tool.name
        else:
            assert hints['readOnlyHint'] is False, tool.name
            assert hints['destructiveHint'] is (tool.name in CHANGES), tool.name


def test_every_argument_is_described_in_the_schema(tools):
    # declared with Field, so it doesn't depend on the fastmcp version parsing docstrings
    for tool in tools:
        for name, prop in tool.parameters.get('properties', {}).items():
            assert prop.get('description'), f'{tool.name}.{name}'


def test_descriptions_skip_args_blocks(tools):
    # argument text lives in the schema; an args: block in the docstring would send it twice
    for tool in tools:
        assert 'args:' not in tool.description.lower(), tool.name


def test_instructions_name_only_real_tools(tools):
    instructions = server.mcp.instructions
    assert instructions == server.INSTRUCTIONS
    names = {tool.name for tool in tools}
    for word in instructions.replace(',', ' ').replace('.', ' ').replace(':', ' ').split():
        if word.startswith(('get_', 'create_', 'update_', 'delete_', 'complete_', 'add_', 'rename_', 'suggest_')):
            assert word.split('=')[0] in names, word


def test_instructions_cover_privacy_tags_and_renames():
    instructions = server.mcp.instructions
    assert 'private=false' in instructions
    for tool in ('get_tags', 'suggest_tags', 'rename_tag', 'update_bookmark'):
        assert tool in instructions


def test_descriptions_say_what_each_tool_returns(tools):
    # in prose, not a Returns: section, which fastmcp 4 strips from descriptions
    for tool in tools:
        assert 'Returns ' in tool.description, tool.name


def test_a_failed_call_reaches_the_client_as_an_error():
    # an error, not a normal result holding {error, success: false}
    from fastmcp import Client

    async def run():
        async with Client(server.mcp) as client:
            return await client.call_tool('get_bookmarks', {'limit': 0}, raise_on_error=False)
    result = asyncio.run(run())
    assert result.is_error is True
    assert result.content[0].text == 'limit must be between 1 and 500'
