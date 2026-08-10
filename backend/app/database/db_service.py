"""
BanglaMind — Database Service Layer
======================================
সব CRUD (Create, Read, Update, Delete) অপারেশন এখানে।
API routes শুধু এই সার্ভিস লেয়ার ব্যবহার করবে।
"""
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database.models import Business, Message, FAQ

logger = logging.getLogger(__name__)


# ─── Business CRUD ────────────────────────────────────────────

def create_business(db: Session, name: str, **kwargs) -> Business:
    """নতুন ব্যবসা তৈরি করো।"""
    biz = Business(name=name, **kwargs)
    db.add(biz)
    db.commit()
    db.refresh(biz)
    logger.info(f"Business তৈরি: {biz.name} (id={biz.id})")
    return biz


def get_business_by_id(db: Session, business_id: str) -> Business | None:
    return db.query(Business).filter(Business.id == business_id).first()


def get_business_by_api_key(db: Session, api_key: str) -> Business | None:
    return db.query(Business).filter(Business.api_key == api_key).first()


def get_all_businesses(db: Session) -> list[Business]:
    return db.query(Business).filter(Business.is_active == True).all()


def update_business(db: Session, business_id: str, **kwargs) -> Business | None:
    biz = get_business_by_id(db, business_id)
    if not biz:
        return None
    for key, val in kwargs.items():
        if hasattr(biz, key):
            setattr(biz, key, val)
    biz.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(biz)
    return biz


# ─── Message CRUD ─────────────────────────────────────────────

def save_message(
    db: Session,
    user_message: str,
    bot_reply: str,
    intent_tag: str,
    intent_source: str,
    confidence: str,
    score: float,
    language: str,
    business_id: str | None = None,
) -> Message:
    """একটি চ্যাট মেসেজ সেভ করো।"""
    msg = Message(
        business_id   = business_id,
        user_message  = user_message,
        bot_reply     = bot_reply,
        intent_tag    = intent_tag,
        intent_source = intent_source,
        confidence    = confidence,
        score         = score,
        language      = language,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_messages(
    db: Session,
    business_id: str | None = None,
    limit: int = 50,
) -> list[Message]:
    """চ্যাট মেসেজ হিস্ট্রি পড়ো।"""
    q = db.query(Message)
    if business_id:
        q = q.filter(Message.business_id == business_id)
    return q.order_by(Message.created_at.desc()).limit(limit).all()


def get_analytics_summary(db: Session, business_id: str | None = None) -> dict:
    """
    Analytics summary তৈরি করো।
    Returns total messages, top intents, source breakdown.
    """
    q = db.query(Message)
    if business_id:
        q = q.filter(Message.business_id == business_id)

    total = q.count()

    # Top intents
    intent_rows = (
        q.with_entities(Message.intent_tag, func.count(Message.id).label("cnt"))
        .group_by(Message.intent_tag)
        .order_by(func.count(Message.id).desc())
        .limit(5)
        .all()
    )

    # Source breakdown
    source_rows = (
        q.with_entities(Message.intent_source, func.count(Message.id).label("cnt"))
        .group_by(Message.intent_source)
        .all()
    )

    # Today's messages
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = q.filter(Message.created_at >= today_start).count()

    return {
        "total_messages": total,
        "today_messages": today_count,
        "top_intents": [{"intent": r.intent_tag, "count": r.cnt} for r in intent_rows],
        "source_counts": {r.intent_source: r.cnt for r in source_rows},
    }


# ─── FAQ CRUD ─────────────────────────────────────────────────

def create_faq(
    db: Session,
    question: str,
    answer: str,
    tags: list[str] | None = None,
    business_id: str | None = None,
) -> FAQ:
    """নতুন FAQ তৈরি করো।"""
    faq = FAQ(
        business_id = business_id,
        question    = question,
        answer      = answer,
        tags        = ",".join(tags) if tags else "",
    )
    db.add(faq)
    db.commit()
    db.refresh(faq)
    return faq


def get_faqs(db: Session, business_id: str | None = None) -> list[FAQ]:
    """সব সক্রিয় FAQ পড়ো।"""
    q = db.query(FAQ).filter(FAQ.is_active == True)
    if business_id:
        q = q.filter(FAQ.business_id == business_id)
    return q.order_by(FAQ.created_at.desc()).all()


def delete_faq(db: Session, faq_id: str) -> bool:
    """FAQ মুছো (soft delete)।"""
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        return False
    faq.is_active = False
    db.commit()
    return True
