import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

# .env ফাইল থেকে environment variables লোড করো
load_dotenv()

from backend.app.api.routes import router as api_router
from backend.app.api.dashboard_routes import router as dashboard_router
from backend.app.api.facebook_webhook import router as fb_router
from backend.app.api.whatsapp_webhook import router as wa_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """App startup ও shutdown event।"""
    # ── Startup ──
    try:
        from backend.app.database.connection import init_db
        init_db()
    except Exception as e:
        logging.getLogger(__name__).warning(f"DB init skipped: {e}")
    yield
    # ── Shutdown ── (যদি কিছু cleanup করার থাকে)

app = FastAPI(
    title="BanglaMind API",
    description="Backend API for BanglaMind AI Chatbot",
    version="2.0.0",
    lifespan=lifespan,
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
app.include_router(fb_router, prefix="/api/facebook")

# Add health check for database
@app.get("/api/db-health")
async def db_health():
    from backend.app.database.connection import health_check
    return health_check()

# Serve the frontend directory as static files
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
