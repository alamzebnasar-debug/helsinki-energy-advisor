import asyncio
from typing import Any
from app.agent import compiled_agent

async def main():
    initial_state: Any = {"live_data": {}, "recommendation": ""}
    result = await compiled_agent.ainvoke(initial_state) # Or ainvoke
    
    print("\n--- Helsinki Energy Advisor Output ---")
    print(result.get("recommendation", "No recommendation generated."))

if __name__ == "__main__":
    asyncio.run(main())