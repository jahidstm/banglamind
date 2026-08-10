from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.routes import router as api_router
from backend.app.api.dashboard_routes import router as dashboard_router

app = FastAPI(
    title="BanglaMind API",
    description="Backend API for BanglaMind AI Chatbot",
    version="1.0.0"
)

# CORS configuration (allows the frontend to make requests to this backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for now (can restrict in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Include all API routes
app.include_router(api_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api/dashboard")

# Serve the frontend directory as static files
# __file__ is backend/app/main.py -> dirname is app -> dirname is backend -> dirname is root
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
frontend_path = os.path.join(base_dir, "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def serve_landing_page():
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/demo.html")
async def serve_demo_page():
    return FileResponse(os.path.join(frontend_path, "demo.html"))

@app.get("/dashboard.html")
async def serve_dashboard():
    return FileResponse(os.path.join(frontend_path, "dashboard.html"))


if __name__ == "__main__":
    import uvicorn
    # This allows running the file directly, though usually you'd use the command line
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
