from fastapi import APIRouter
from backend.app.api.schemas import ChatRequest, ChatResponse
from backend.app.chatbot.engine import engine
from backend.app.api.dashboard_routes import increment_analytics

router = APIRouter()

@router.get("/health", summary="Health Check")
async def health_check():
    """Check if the API is running correctly."""
    return {"status": "ok", "message": "BanglaMind API is running!"}

@router.post("/chat", response_model=ChatResponse, summary="Chat Endpoint")
async def chat(request: ChatRequest):
    """
    Process a user message and return the chatbot's response.
    """
    result = engine.process_message(request.message)

    # Analytics track করো (background-এ)
    try:
        increment_analytics(
            intent=result["intent"]["tag"],
            source=result["intent"]["source"],
        )
    except Exception:
        pass  # analytics fail হলে chat বন্ধ হবে না

    return ChatResponse(
        reply=result["reply"],
        intent=result["intent"],
        language=result["language"]
    )

