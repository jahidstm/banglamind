from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.routes import router as api_router

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

# Include all API routes
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    # This allows running the file directly, though usually you'd use the command line
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
