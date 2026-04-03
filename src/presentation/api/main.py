import sys
import asyncio
import os

# MANDATORY: Fix for Windows NotImplementedError (MUST be before any other imports)
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Fix path resolution
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
from src.presentation.api.error_handlers import global_exception_handler
from src.domain.exceptions.base import AppBaseException

app = FastAPI()

# Global Exception Handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(AppBaseException, global_exception_handler)

@app.on_event("startup")
async def startup():
    print(f"--- [STABLE] Backend Running on Port 8001 with {type(asyncio.get_event_loop()).__name__} ---")

from src.presentation.api.routers import automation, metrics
app.include_router(automation.router, prefix="/api/v1")
app.include_router(metrics.router, prefix="/api/v1")

@app.get("/", response_class=HTMLResponse)
async def get_landing():
    landing_path = os.path.join(project_root, "frontend/index.html")
    if not os.path.exists(landing_path):
        return HTMLResponse(content=f"Error: index.html not found", status_code=404)
    with open(landing_path, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    # Using 8001 to avoid conflicts during testing
    uvicorn.run(app, host="0.0.0.0", port=8001)