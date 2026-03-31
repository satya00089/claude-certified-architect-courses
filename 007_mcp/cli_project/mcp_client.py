"""
This module defines the MCPClient class, which provides an interface for connecting to an MCP server using
standard input and output as the transport layer. The client can list available tools and prompts on the server,
call tools with specified input, and read resources from the server using their URIs. The client is designed
"""


import sys
import asyncio
import json
from typing import Optional, Any
from contextlib import AsyncExitStack

from pydantic import AnyUrl

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client


class MCPClient:
    """A client for connecting to an MCP server using standard input and output as the transport layer."""
    def __init__(
        self,
        command: str,
        args: list[str],
        env: Optional[dict] = None,
    ):
        self._command = command
        self._args = args
        self._env = env
        self._session: Optional[ClientSession] = None
        self._exit_stack: AsyncExitStack = AsyncExitStack()

    async def connect(self):
        """Connect to the MCP server using the specified command and arguments."""
        server_params = StdioServerParameters(
            command=self._command,
            args=self._args,
            env=self._env,
        )
        stdio_transport = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        _stdio, _write = stdio_transport
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(_stdio, _write)
        )
        await self._session.initialize()

    def session(self) -> ClientSession:
        """Get the current client session."""
        if self._session is None:
            raise ConnectionError(
                "Client session not initialized or cache not populated. Call connect_to_server first."
            )
        return self._session

    async def list_tools(self) -> list[types.Tool]:
        """List all tools available on the MCP server."""

        result = await self.session().list_tools()
        return result.tools

    async def call_tool(
        self, tool_name: str, tool_input: dict
    ) -> types.CallToolResult | None:
        """Call a tool on the MCP server with the specified name and input."""
        return await self.session().call_tool(tool_name, tool_input)

    async def list_prompts(self) -> list[types.Prompt]:
        """List all prompts available on the MCP server."""
        result = await self.session().list_prompts()
        return result.prompts

    async def get_prompt(self, prompt_name, args: dict[str, str]):
        """Get a particular prompt defined by the MCP server."""
        result = await self.session().get_prompt(prompt_name, args)
        return result.messages

    async def read_resource(self, uri: str) -> Any:
        """Read a resource from the MCP server using its URI."""
        result = await self.session().read_resource(AnyUrl(uri))
        resource = result.contents[0]

        if isinstance(resource, types.TextResourceContents):
            if resource.mimeType == "application/json":
                return json.loads(resource.text)
        return resource.text

    async def cleanup(self):
        """Clean up the client session and close the connection to the MCP server."""
        await self._exit_stack.aclose()
        self._session = None

    async def __aenter__(self):
        """Enter the asynchronous context manager and connect to the MCP server."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the asynchronous context manager and clean up the client session."""
        await self.cleanup()


# For testing
async def main():
    """Example usage of the MCPClient to connect to the MCP server and list available tools."""
    async with MCPClient(
        # If using Python without UV, update command to 'python' and remove "run" from args.
        command="uv",
        args=["run", "mcp_server.py"],
    ) as _client:
        result = await _client.list_tools()
        print(result)


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
