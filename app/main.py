from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any
from app.agent import compiled_agent

# Initialize FastAPI application
app = FastAPI(
    title="Helsinki Smart Energy & Weather Advisor API",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    prompt: str

@app.post("/ask-advisor")
async def ask_energy_advisor(request: QueryRequest):
    """API endpoint to query our Helsinki energy agent asynchronously."""
    try:
        # Initialize state with the fields expected by app/agent.py
        initial_state: Any = {"live_data": {}, "recommendation": ""}
        result = await compiled_agent.ainvoke(initial_state)
        
        return {
            "status": "success",
            "city": "Helsinki",
            "recommendation": result.get("recommendation", "No recommendation generated.")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))