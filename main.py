import asyncio
from agent.agent import build_agent

async def main():
    async with build_agent() as agent: # buildagent is an ACM now. so async with -> enter it and get yielded agent whilst keeping its resources alive
        config = {"configurable" : {"thread_id" : "1"}}
        
        while True:
            userinput = input("\nYou: ")
            if userinput.lower() == "exit":
                break
            
            result = await agent.ainvoke({"messages" : userinput}, config)
            print(f"\nAgent: {result['messages'][-1].content}")

if __name__ == "__main__":
    asyncio.run(main())
