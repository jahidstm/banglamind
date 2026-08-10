from pydantic import BaseModel, Field
from typing import Optional, List

class ChatRequest(BaseModel):
    message: str = Field(..., title="User Message", description="The text message from the user")
    user_id: Optional[str] = Field(None, description="Optional user ID for tracking context")
    business_id: Optional[str] = Field("default", description="Business ID (for multi-tenant support later)")

class IntentInfo(BaseModel):
    tag: str
    confidence: str
    score: float
    source: str = "rule"  # "ml" or "rule"

class ChatResponse(BaseModel):
    reply: str = Field(..., description="The chatbot's reply")
    intent: IntentInfo = Field(..., description="Details about the matched intent")
    language: str = Field(..., description="Detected language (bengali, banglish, english)")
