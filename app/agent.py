from pathlib import Path
from typing import TypedDict, Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import asyncio
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import TextContent
class State(TypedDict):
    live_data: Dict[str, Any]
    recommendation: str

from mcp.types import TextContent

async def fetch_data_via_mcp_node(state: State) -> State:
    """Spawns the MCP server locally via stdio and fetches environment tools asynchronously."""
    server_script = str(Path(__file__).parent / "mcp_server.py")
    
    server_params = StdioServerParameters(
        command="python",
        args=[server_script]
    )
    
    temperature = 4.3
    condition = "Weather Code: 0"
    spot_price = "0.877 c/kWh (Inc. VAT)"

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                weather_result = await session.call_tool("get_helsinki_weather", arguments={})
                price_result = await session.call_tool("get_spot_price", arguments={})
                
                if weather_result.content:
                    block = weather_result.content[0]
                    if isinstance(block, TextContent) and block.text:
                        w_data = eval(block.text)
                        temperature = w_data.get("temperature_c", temperature)
                        condition = w_data.get("condition", condition)
                    
                if price_result.content:
                    block = price_result.content[0]
                    if isinstance(block, TextContent) and block.text:
                        spot_price = block.text
    except Exception as e:
        print(f"--> [Warning] MCP Server communication failed: {e}. Using fallback values.")

    live_data = {
        "temperature_c": temperature,
        "condition": condition,
        "spot_price_kwh": spot_price
    }
    return {"live_data": live_data, "recommendation": ""}

def ai_reasoning_node(state: State) -> State:
    """Reasoning node generating recommendations using local Ollama or cloud fallback."""
    live_data = state["live_data"]
    
    system_prompt = f"""
    You are an expert municipal energy and weather optimization advisor for Helsinki, Finland.
    Current Live Data (retrieved via MCP Server):
    - Temperature: {live_data.get('temperature_c')}°C
    - Weather Condition: {live_data.get('condition')}
    - Electricity Spot Price: {live_data.get('spot_price_kwh')}

    Provide a concise, highly practical 2-3 sentence recommendation for a Helsinki resident 
    on managing their heating or power consumption right now. You MUST explicitly mention both the current outdoor temperature and the exact electricity spot price.
    """
    
    response_content = ""
    try:
        llm = ChatOllama(
            model="llama3.2",
            temperature=0,
            base_url="http://host.docker.internal:11434"
        )
        response = llm.invoke([HumanMessage(content=system_prompt)])
        response_content = str(response.content)
    except Exception:
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            llm_fallback = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=0, google_api_key=api_key)
            response = llm_fallback.invoke([HumanMessage(content=system_prompt)])
            response_content = str(response.content)
        except Exception as e:
            response_content = f"[Error] All models failed: {e}"

    return {"live_data": live_data, "recommendation": response_content}

# Build LangGraph workflow
workflow = StateGraph(State)
workflow.add_node("fetch_data", fetch_data_via_mcp_node)
workflow.add_node("ai_reasoning", ai_reasoning_node)

workflow.set_entry_point("fetch_data")
workflow.add_edge("fetch_data", "ai_reasoning")
workflow.add_edge("ai_reasoning", END)

compiled_agent = workflow.compile()