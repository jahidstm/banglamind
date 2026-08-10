from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.app.api.routes import router as api_router
import os

app = FastAPI(
    title="BanglaMind API",
    description="Backend API for BanglaMind AI Chatbot",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the frontend directory to serve static files (HTML, CSS, JS)
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend")
app.mount("/app", StaticFiles(directory=frontend_path, html=True), name="frontend")

# Include all API routes
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    # This allows running the file directly, though usually you'd use the command line
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
