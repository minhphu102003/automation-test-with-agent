# Browser Testing Automation Suite

**Version**: `1.1.0` | **License**: MIT | **Status**: Active (Full Stack Clean Architecture)

This project is a complete automation testing suite designed for robust, AI-driven browser automation. It leverages `browser-use` alongside a comprehensive full-stack ecosystem to queue, process, and present automation executions.

## 🏗️ System Architecture

The project consists of multiple interacting services:

1. **Frontend (Next.js)**: A modular React application built with Atomic Design principles, serving the dashboard on port `3000`.
2. **Backend (FastAPI)**: Serves core APIs adhering to Clean Architecture on port `8001`.
3. **Worker**: Background execution environment handling long-running `browser-use` automation tasks.
4. **Redis**: In-memory message broker to facilitate async task queuing between the Backend and Worker.
5. **MinIO**: S3-compatible local object storage serving test artifacts, screenshots, and logs on port `9000` (Console on `9001`).

```text
/
  ├── frontend/       # Next.js web application built with Atomic Design.
  ├── src/            # Backend Clean Architecture (FastAPI + Workers).
  │    ├── domain/         # Core logic, entities, interfaces.
  │    ├── application/    # Use Cases, QA test logic, orchestrator.
  │    ├── infrastructure/ # External dependencies (MinIO, Redis, Langfuse, Playwright).
  │    ├── presentation/   # FastAPI application, routers, schemas. 
  │    └── prompts/        # Centralized LLM prompts.
  └── docker/         # Dockerfiles for respective services.
```

## 🚀 Quick Start (Docker - Recommended)

The simplest way to orchestrate the entire stack (Backend, Frontend, Setup, Redis, and MinIO) is using Docker Compose.

```powershell
docker compose up --build -d
```
Upon successful start, you can access:
- **Dashboard (Frontend)**: [http://localhost:3000](http://localhost:3000)
- **Backend API (Swagger)**: [http://localhost:8001/docs](http://localhost:8001/docs)
- **MinIO Console**: [http://localhost:9001](http://localhost:9001)

*(Note: Provide valid `.env` keys for OpenAI/Langfuse prior to spinning up containers).*

## 💻 Manual Developer Setup (Local)

If you need to develop specific layers without Docker:

### 1. Backend / Worker Stack
```powershell
uv sync
uv run playwright install

# Run FastAPI Server (Terminal 1)
uv run python src/presentation/api/main.py

# (Assuming external Redis & MinIO are available for the worker queue)
```

### 2. Frontend Stack
Navigate to the frontend folder and install dependencies:
```bash
cd frontend
npm install
npm run dev
```

## 🤖 Core Capabilities

- **GPT Bridge Generation**: Convert raw textual QA instructions into formal 13-column test scenarios dynamically using standard prompt techniques.
- **Browser Automation Agent**: Dynamically executes test sequences via `browser-use`. Extracted elements and trace recordings are piped back to the user via background workers.
- **Cost Profiling**: Comprehensive Langfuse integration tracks and scopes every test trace, reporting execution times, and monitoring tokens usage to evaluate LLM costs.
- **Distributed Architecture**: Uses Redis & MinIO to asynchronously perform high-intensity AI Web navigation without blocking API clients.

## 🤖 AI Agent Setup (CRITICAL)

To optimally assist in this codebase, configure your AI IDE context with the **Context7 MCP server** for real-time external library resolutions (`playwright`, `browser-use`, `next.js`, `fastapi`).

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"],
      "env": {
        "CONTEXT7_API_KEY": "YOUR_UPSTASH_CONTEXT7_TOKEN"
      }
    }
  }
}
```

## 📁 Agentic Guidelines
All tasks strictly enforce modular rules mapped out in the `.agents/` folder:
- **Clean Architecture Rules**: `.agents/rules/backend_clean_architecture.md`
- **Frontend Guidelines**: `.agents/rules/frontend_atomic_design.md` 
- **Context7 Usage**: `.agents/rules/context7_mcp.md`
