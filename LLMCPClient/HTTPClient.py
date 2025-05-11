import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()

   # ---------- new Streamable-HTTP transport ----------
    async def connect_to_http_server(self, endpoint: str):
        """
        Connect to an already-running MCP server via the Streamable-HTTP transport.

        Args:
            endpoint: Full URL of the MCP endpoint, e.g. 'http://localhost:8000/mcp'
            
        """
        # The helper takes the endpoint and an optional flag for the extra SSE GET.
        stream_transport = await self.exit_stack.enter_async_context(
            streamablehttp_client(endpoint)
        )
        read_stream = stream_transport[0]
        write_stream = stream_transport[1]
        print()
        print ("Connected to server:", endpoint)
        print("Streamable HTTP transport established.")
        print (stream_transport)
        print()
        await self._initialize_session(read_stream, write_stream)
        
    # ---------- shared helpers ----------
    async def _initialize_session(self, read_stream, write_stream):

        """Initialize the MCP session with the given read and write streams."""


        self.session = await self.exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )

        print("\nConnected - session created. Now initializing...")
        print()

        try:
            # Initialize the session
            await self.session.initialize()
        except Exception as e:
            print(f"Error initializing session: {e}")
            return
        

        print()
        print("\nConnected - session initialized.")
        print()

        tools = (await self.session.list_tools()).tools
        print("\nConnected - tools available:", [t.name for t in tools])


    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools"""
        messages = [
            {
                "role": "assistant",
                "content": "today is {now}. Your role is to provide direct response of the tool. Do not add anything additional. Only when there is no need for tools, just be a helpful assistant."
            },
              {
                "role": "user",
                "content": query
            }
        ]

        response = await self.session.list_tools()
        available_tools = [{ 
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]
        

        print("\nAvailable tools:", available_tools)


        # Initial Claude API call
        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=messages,
            tools=available_tools
        )

        # Process response and handle tool calls
        tool_results = []
        final_text = []

        for content in response.content:
            if content.type == 'text':
                final_text.append(content.text)
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input
                
                # Execute tool call
                result = await self.session.call_tool(tool_name, tool_args)
                tool_results.append({"call": tool_name, "result": result})
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                # Continue conversation with tool results
                if hasattr(content, 'text') and content.text:
                    messages.append({
                      "role": "assistant",
                      "content": content.text
                    })
                messages.append({
                    "role": "user", 
                    "content": result.content
                })

                # Get next response from Claude
                response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=messages,
                )

                final_text.append(response.content[0].text)

        return "\n".join(final_text)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")
        
        while True:
            try:
                query = input("\nQuery: ").strip()
                
                if query.lower() == 'quit':
                    break
                    
                response = await self.process_query(query)
                print("\n" + response)
                    
            except Exception as e:
                print(f"\nError: {str(e)}")


    async def chat(self, query: str) -> str:
        """Process a query using the MCP server and print the response"""

        try:
            response = await self.process_query(query)
            print("\n" + response)
            return response
                
        except Exception as e:
            print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/mcp"

    client = MCPClient()

    # Connect to the server
    try:
        await client.connect_to_http_server(base_url)
        await client.chat_loop()
    finally:
        await client.cleanup()

def run():
    import sys
    asyncio.run(main())


if __name__ == "__main__":
    run()

    
# This code is a client for the MCP (Multi-Channel Protocol) server, which allows for communication with various AI models and tools.
# It uses the Anthropic API for AI interactions and supports both standard input/output and HTTP transport methods.
# The client can connect to a running MCP server, list available tools, and process user queries interactively.
# The code is designed to be run as a standalone script, and it includes error handling and resource cleanup.