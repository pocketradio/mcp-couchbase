from langchain_aws import ChatBedrockConverse
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_mcp_adapters.tools import load_mcp_tools

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv
import os

load_dotenv()

model = ChatBedrockConverse(
    model="amazon.nova-lite-v1:0",
    region_name= os.getenv("AWS_REGION")
)

params = StdioServerParameters(
    command="uv",
    args=[
        "run",
        "mcp_server/server.py"
    ],
    env={
        "CB_CONNECTION_STRING": os.getenv("CB_CONNECTION_STRING"),
        "CB_USERNAME": os.getenv("CB_USERNAME"),
        "CB_PASSWORD": os.getenv("CB_PASSWORD"),
        "CB_BUCKET_NAME": os.getenv("CB_BUCKET_NAME")
    }
)


system_prompt = """
You are a travel assistant with access to a Couchbase database.

Database structure:
Bucket: `travel-sample`
Scope: `inventory`
Collections:
- `airline`
- `airport`
- `hotel`
- `landmark`
- `route`

When generating queries:
- ALWAYS fully qualify collections as:
`travel-sample`.`inventory`.`collection_name`
- ALWAYS use backticks.
- NEVER query outside the `inventory` scope.
- Always use LIMIT unless the user explicitly asks for all results.
"""

from contextlib import asynccontextmanager

@asynccontextmanager
async def build_agent():    
    async with stdio_client(params) as (read, write): # this is going to trigger the __aenter__(). and read & write needed for bidirn comms
    # above line is going to spawn an mcp server subprocess and connect to its stdin, stdout. then wraps them in async streams and yields a readstream, writestream
    
        async with ClientSession(read_stream=read, write_stream=write) as session:
            # client session creation. it wraps read write streams into a protocol aware mcp session that handles json rpc req and resp.
            await session.initialize()
            tools = await load_mcp_tools(session) 
            checkpt = InMemorySaver()
            agent = create_agent(
                model,
                tools,
                system_prompt=system_prompt,
                checkpointer = checkpt
            )
            
            yield agent # return from inside the "async with" would kill the session. yield will PAUSE, not exit so asynccontextmgr is better here.