from fastapi import APIRouter
from backend.app.api.schemas import ChatRequest, ChatResponse
from backend.app.chatbot.engine import engine
from backend.app.api.dashboard_routes import increment_analytics

router = APIRouter()

@router.get("/health", summary="Health Check")
async def health_check():
    """Check if the API is running correctly."""
    return {"status": "ok", "message": "BanglaMind API is running!", "version": "2.0.0"}

@router.post("/chat", response_model=ChatResponse, summary="Chat Endpoint")
async def chat(request: ChatRequest):
    """
    Process a user message and return the chatbot's response.
    Full pipeline: RAG → ML → Rule-based
    """
    result = engine.process_message(request.message)
    intent = result["intent"]

    # ── Analytics (JSON file) track করো ──
    try:
        increment_analytics(intent["tag"], intent["source"])
    except Exception:
        pass

    # ── Database-এ message save করো (optional) ──
    try:
        from backend.app.database.connection import DB_AVAILABLE, SessionLocal
        if DB_AVAILABLE and SessionLocal:
            from backend.app.database.db_service import save_message
            db = SessionLocal()
            try:
                save_message(
                    db           = db,
                    user_message = request.message,
                    bot_reply    = result["reply"],
                    intent_tag   = intent["tag"],
                    intent_source= intent["source"],
                    confidence   = intent["confidence"],
                    score        = float(intent["score"]),
                    language     = result.get("language", "unknown"),
                )
            finally:
                db.close()
    except Exception:
        pass  # DB save fail হলে chat বন্ধ হবে না

    return ChatResponse(
        reply    = result["reply"],
        intent   = intent,
        language = result.get("language", "unknown"),
    )
