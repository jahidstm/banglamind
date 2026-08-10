"""
BanglaMind — Dashboard API Routes
=====================================
Business owner-এর জন্য:
- FAQ Management (CRUD)
- Analytics
- Business Settings
"""
import os
import json
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.app.chatbot.rag_engine import rag_engine

router = APIRouter()

# ─── Data file paths ──────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
FAQ_PATH      = os.path.join(BASE_DIR, "data", "sample_faq.json")
SETTINGS_PATH = os.path.join(BASE_DIR, "data", "business_settings.json")
ANALYTICS_PATH= os.path.join(BASE_DIR, "data", "analytics.json")


# ─── Helper functions ─────────────────────────────────────────

def load_faq_data() -> dict:
    if os.path.exists(FAQ_PATH):
        with open(FAQ_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"business_name": "আমার দোকান", "faqs": []}


def save_faq_data(data: dict):
    with open(FAQ_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    rag_engine.reload()  # RAG engine refresh করো


def load_settings() -> dict:
    defaults = {
        "business_name": "রহিম স্টোর",
        "phone": "০১৭১২-৩৪৫৬৭৮",
        "address": "মিরপুর-১০, ঢাকা",
        "hours": "সকাল ৯টা – রাত ১০টা",
        "delivery": "হোম ডেলিভারি আছে",
        "email": "rahim.store@gmail.com",
        "facebook": "",
        "whatsapp": "",
    }
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, encoding="utf-8") as f:
            return {**defaults, **json.load(f)}
    return defaults


def save_settings(data: dict):
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_analytics() -> dict:
    defaults = {
        "total_messages": 0,
        "intent_counts": {},
        "source_counts": {"ml": 0, "rule": 0, "rag": 0},
        "daily_counts": {},
    }
    if os.path.exists(ANALYTICS_PATH):
        with open(ANALYTICS_PATH, encoding="utf-8") as f:
            return {**defaults, **json.load(f)}
    return defaults


def increment_analytics(intent: str, source: str):
    """প্রতিটি চ্যাট মেসেজে analytics আপডেট করে।"""
    data = load_analytics()
    data["total_messages"] = data.get("total_messages", 0) + 1
    ic = data.setdefault("intent_counts", {})
    ic[intent] = ic.get(intent, 0) + 1
    sc = data.setdefault("source_counts", {})
    sc[source] = sc.get(source, 0) + 1
    today = datetime.now().strftime("%Y-%m-%d")
    dc = data.setdefault("daily_counts", {})
    dc[today] = dc.get(today, 0) + 1
    with open(ANALYTICS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ─── Pydantic Models ──────────────────────────────────────────

class FAQItem(BaseModel):
    question: str
    answer: str
    tags: Optional[list[str]] = []


class BusinessSettings(BaseModel):
    business_name: str
    phone: Optional[str] = ""
    address: Optional[str] = ""
    hours: Optional[str] = ""
    delivery: Optional[str] = ""
    email: Optional[str] = ""
    facebook: Optional[str] = ""
    whatsapp: Optional[str] = ""


# ─── FAQ Routes ───────────────────────────────────────────────

@router.get("/faqs", summary="সব FAQ দেখাও")
async def get_all_faqs():
    data = load_faq_data()
    return {
        "business_name": data.get("business_name"),
        "total": len(data.get("faqs", [])),
        "faqs": data.get("faqs", []),
    }


@router.post("/faqs", summary="নতুন FAQ যুক্ত করো")
async def add_faq(item: FAQItem):
    data = load_faq_data()
    new_faq = {
        "id":       f"faq_{uuid.uuid4().hex[:6]}",
        "question": item.question,
        "answer":   item.answer,
        "tags":     item.tags or [],
        "created_at": datetime.now().isoformat(),
    }
    data["faqs"].append(new_faq)
    save_faq_data(data)
    return {"status": "ok", "faq": new_faq, "total": len(data["faqs"])}


@router.delete("/faqs/{faq_id}", summary="FAQ মুছে ফেলো")
async def delete_faq(faq_id: str):
    data = load_faq_data()
    original_len = len(data["faqs"])
    data["faqs"] = [f for f in data["faqs"] if f.get("id") != faq_id]
    if len(data["faqs"]) == original_len:
        raise HTTPException(status_code=404, detail="FAQ পাওয়া যায়নি")
    save_faq_data(data)
    return {"status": "ok", "deleted_id": faq_id, "total": len(data["faqs"])}


# ─── Settings Routes ──────────────────────────────────────────

@router.get("/settings", summary="Business তথ্য দেখাও")
async def get_settings():
    return load_settings()


@router.put("/settings", summary="Business তথ্য আপডেট করো")
async def update_settings(settings: BusinessSettings):
    data = settings.model_dump()
    save_settings(data)
    return {"status": "ok", "settings": data}


# ─── Analytics Routes ─────────────────────────────────────────

@router.get("/analytics", summary="Analytics দেখাও")
async def get_analytics():
    data = load_analytics()
    intent_counts = data.get("intent_counts", {})

    # Top 5 intents
    top_intents = sorted(intent_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    # Last 7 days
    daily = data.get("daily_counts", {})
    sorted_days = sorted(daily.items())[-7:]

    return {
        "total_messages": data.get("total_messages", 0),
        "source_counts":  data.get("source_counts", {}),
        "top_intents":    [{"intent": k, "count": v} for k, v in top_intents],
        "daily_counts":   [{"date": d, "count": c} for d, c in sorted_days],
    }
