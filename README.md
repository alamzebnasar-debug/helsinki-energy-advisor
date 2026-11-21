# Helsinki Smart Energy & Weather Advisor

An AI-powered backend microservice that combines real-time **Finnish Meteorological Institute (FMI)** weather forecasts and **Nord Pool** electricity spot prices to generate actionable home energy optimization advice in Helsinki.

## Architecture & Key Features
- **Agentic Workflow (`LangGraph`):** Orchestrates multi-step tool calls to fetch live weather and hourly electricity pricing before synthesizing recommendations.
- **Hybrid Local + Cloud Inference:** Runs private, zero-cost local inference via **Ollama (`llama3.2`)** with automatic failover to **Google Gemini (`gemini-3.5-flash-lite`)** for high availability.
- **Production-Ready API (`FastAPI` & `Docker`):** Containerized backend with clean REST endpoints and environment-based configuration.

## Quickstart

1. **Clone & configure environment:**
   ```bash
   cp .env.example .env
   # Add your GEMINI_API_KEY in .env