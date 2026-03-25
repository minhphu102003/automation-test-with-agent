from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import os

app = FastAPI(title="Automation Suite Dashboard (Clean Arch)")

@app.get("/", response_class=HTMLResponse)
async def get_landing():
    # Adjusted path relative to the new location src/presentation/api/main.py
    # Root is ../../../
    landing_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../frontend/index.html"))
    if not os.path.exists(landing_path):
        return HTMLResponse(content=f"Error: index.html not found at {landing_path}", status_code=404)
        
    with open(landing_path, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
