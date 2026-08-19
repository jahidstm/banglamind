"""
BanglaMind — Business API
===========================
Business registration, API Key management, profile endpoints.
"""
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import Optional

from backend.app.database.connection import DB_AVAILABLE, SessionLocal
from backend.app.database.db_service import (
    create_business, get_business_by_id, get_business_by_api_key,
    get_all_businesses, update_business
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ─── Pydantic Schemas ────────────────────────────────────────────

class BusinessCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    hours: Optional[str] = None
    email: Optional[str] = None

class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    hours: Optional[str] = None
    delivery_info: Optional[str] = None
    email: Optional[str] = None
    facebook: Optional[str] = None
    whatsapp: Optional[str] = None


# ─── Helper: API Key Authentication ─────────────────────────────

def get_current_business(x_api_key: str = Header(..., alias="X-API-Key")):
    """Header থেকে API Key নিয়ে Business খোঁজো।"""
    if not DB_AVAILABLE or not SessionLocal:
        raise HTTPException(status_code=503, detail="Database unavailable")
    db = SessionLocal()
    try:
        biz = get_business_by_api_key(db, x_api_key)
        if not biz or not biz.is_active:
            raise HTTPException(status_code=401, detail="Invalid or inactive API Key")
        return biz
    finally:
        db.close()


# ─── Endpoints ────────────────────────────────────────────────────

@router.post("/register", status_code=201)
def register_business(data: BusinessCreate):
    """
    নতুন Business register করো।
    Response-এ api_key পাওয়া যাবে — এটি সংরক্ষণ করুন!
    """
    if not DB_AVAILABLE or not SessionLocal:
        raise HTTPException(status_code=503, detail="Database unavailable")
    db = SessionLocal()
    try:
        biz = create_business(db, name=data.name, phone=data.phone,
                               address=data.address, hours=data.hours,
                               email=data.email)
        return {
            "message": "Business সফলভাবে তৈরি হয়েছে!",
            "business_id": biz.id,
            "business_name": biz.name,
            "api_key": biz.api_key,
            "note": "এই api_key টি গোপন রাখুন। এটি আপনার chatbot চালানোর জন্য দরকার।"
        }
    finally:
        db.close()


@router.get("/me")
def get_my_profile(business=Depends(get_current_business)):
    """নিজের Business profile দেখুন।"""
    return {
        "id": business.id,
        "name": business.name,
        "phone": business.phone,
        "address": business.address,
        "hours": business.hours,
        "email": business.email,
        "facebook": business.facebook,
        "whatsapp": business.whatsapp,
        "is_active": business.is_active,
        "created_at": business.created_at,
    }


@router.put("/me")
def update_my_profile(data: BusinessUpdate, business=Depends(get_current_business)):
    """নিজের Business profile আপডেট করুন।"""
    if not DB_AVAILABLE or not SessionLocal:
        raise HTTPException(status_code=503, detail="Database unavailable")
    db = SessionLocal()
    try:
        updated = update_business(db, business.id, **data.model_dump(exclude_none=True))
        return {"message": "Profile আপডেট হয়েছে!", "name": updated.name}
    finally:
        db.close()


@router.get("/usage")
def get_usage(business=Depends(get_current_business)):
    """এই মাসে কতটি মেসেজ ব্যবহার হয়েছে দেখুন।"""
    if not DB_AVAILABLE or not SessionLocal:
        return {"monthly_limit": 50, "used": 0, "remaining": 50}
    db = SessionLocal()
    try:
        from datetime import datetime
        from sqlalchemy import func
        from backend.app.database.models import Message
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        used = db.query(func.count(Message.id)).filter(
            Message.business_id == business.id,
            Message.created_at >= month_start
        ).scalar() or 0
        monthly_limit = 50  # Free tier
        return {
            "business_name": business.name,
            "plan": "free",
            "monthly_limit": monthly_limit,
            "used_this_month": used,
            "remaining": max(0, monthly_limit - used),
        }
    finally:
        db.close()