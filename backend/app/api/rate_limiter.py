"""
BanglaMind — Rate Limiter Middleware (Dependency)
==================================================
Free tier: মাসে সর্বোচ্চ 50টি মেসেজ।
এটি একটি FastAPI Dependency হিসেবে কাজ করে।
"""
import logging
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database.models import Message

logger = logging.getLogger(__name__)

FREE_TIER_LIMIT = 50  # মাসিক মেসেজ সীমা


def check_rate_limit(business_id: str, db: Session):
    """
    এই মাসে business-টি কতটি মেসেজ পাঠিয়েছে তা চেক করে।
    সীমা অতিক্রম করলে HTTPException (429) raise করে।
    """
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    used = db.query(func.count(Message.id)).filter(
        Message.business_id == business_id,
        Message.created_at >= month_start
    ).scalar() or 0

    if used >= FREE_TIER_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=(
                f"মাসিক বার্তার সীমা ({FREE_TIER_LIMIT}টি) শেষ হয়ে গেছে। "
                "সীমা বাড়াতে আপনার প্ল্যান আপগ্রেড করুন।"
            )
        )

    remaining = FREE_TIER_LIMIT - used
    logger.debug(f"Rate limit check — business={business_id}, used={used}, remaining={remaining}")
    return {"used": used, "remaining": remaining}