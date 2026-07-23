import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

import config
from routers import auth, scan, market

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Create directories if they do not exist
os.makedirs(os.path.join(FRONTEND_DIR, "css"), exist_ok=True)
os.makedirs(os.path.join(FRONTEND_DIR, "js"), exist_ok=True)
os.makedirs(os.path.join(FRONTEND_DIR, "mock_storage"), exist_ok=True)

app = FastAPI(
    title="MandiGrown API",
    description="Backend API for crop quality grading and record keeping",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routers ---
app.include_router(auth.router)
app.include_router(scan.router)
app.include_router(market.router)

# --- API Endpoints ---
@app.get("/api/health")
def health_check():
    """Returns server and configuration status."""
    return {
        "status": "online",
        "mock_mode": config.IS_MOCK_MODE,
        "debug": config.DEBUG
    }

# --- Static Frontend Serving ---

# Static routes for stylesheets, scripts, and uploads
app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")
app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")

# Mount mock storage if we are in mock mode and it exists, so images can be served locally
@app.get("/mock_storage/{filename}")
def get_mock_image(filename: str):
    file_path = os.path.join(FRONTEND_DIR, "mock_storage", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"message": "Image not found"}

# Serve SPA homepage
@app.get("/{full_path:path}")
def serve_spa(full_path: str):
    # If the user targets files inside css or js, let FastAPI's StaticFiles handle it.
    # Otherwise, direct all browser routing to index.html for Single Page Application
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "MandiGrown Server is Online. Please create frontend/index.html."}

if __name__ == "__main__":
    uvicorn.run("main:app", host=config.HOST, port=config.PORT, reload=config.DEBUG)
