# ruff: noqa: E402

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

import contextlib
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# --- Domain & Infrastructure ---
from src.infrastructure.external.auth_connector import HttpAuthConnector
from src.infrastructure.monitoring.langfuse_reader import LangfuseReader
from src.infrastructure.external.redis_stream_adapter import RedisStreamAdapter
from src.infrastructure.external.minio_storage import MinioStorageAdapter
from src.infrastructure.storage.json_profile_repository import JsonAuthProfileRepository
from src.presentation.api.error_handlers import global_exception_handler
from src.domain.exceptions.base import AppBaseException

# --- Routers ---
from src.presentation.api.routers import auth_profiles, automation, metrics

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages application startup and shutdown events."""
    print("--- [Backend] Starting up (Initializing shared adapters) ---")
    
    # 1. Initialize Adapters
    langfuse_reader = LangfuseReader()
    messaging = RedisStreamAdapter()
    storage = MinioStorageAdapter()
    auth_profile_repository = JsonAuthProfileRepository()
    auth_connector = HttpAuthConnector()
    
    # 2. Ensure resources are ready
    try:
        await storage.ensure_bucket_exists()
    except Exception as e:
        print(f"--- Warning: MinIO connection failed: {e} ---")
        
    # 3. Store in app state for DI providers
    app.state.langfuse_reader = langfuse_reader
    app.state.messaging = messaging
    app.state.storage = storage
    app.state.auth_profile_repository = auth_profile_repository
    app.state.auth_connector = auth_connector
    
    print(f"--- [STABLE] Backend Running on Port 8001 with {type(asyncio.get_event_loop()).__name__} ---")
    
    yield
    
    # 4. Cleanup
    print("--- [Backend] Shutting down (Closing shared adapters) ---")
    await messaging.close()
    await storage.close()

app = FastAPI(lifespan=lifespan)

# Global Exception Handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(AppBaseException, global_exception_handler)

app.include_router(automation.router, prefix="/api/v1")
app.include_router(auth_profiles.router, prefix="/api/v1")
app.include_router(metrics.router, prefix="/api/v1")

@app.get("/", response_class=HTMLResponse)
async def get_landing():
    landing_path = os.path.join(project_root, "frontend/index.html")
    if not os.path.exists(landing_path):
        return HTMLResponse(content="Error: index.html not found", status_code=404)
    with open(landing_path, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    # Using 8001 to avoid conflicts during testing
    uvicorn.run(app, host="0.0.0.0", port=8001)
