from LLMCPClient.HTTPClient import MCPClient  
import asyncio

async def main():
    client = MCPClient()
    try:
        await client.connect_to_http_server("http://localhost:8000/mcp")

        while True:

            print ("\n","-"*50)
            print("Type your queries or 'quit' to exit.")

            # Get user input for the query 
            query = input("\nQuery: ").strip()
            if query.lower() == 'quit':
                break
            # Call the tool with the user input
            response = await client.chat(query)
            
            
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())