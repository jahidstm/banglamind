"""
BanglaMind -- Facebook Messenger Webhook
=========================================
ফেসবুক পেজ থেকে মেসেজ গ্রহণ করে এবং AI-এর উত্তর ফেসবুকে পাঠায়।
"""
import os
import httpx
import logging
from fastapi import APIRouter, Request, HTTPException, Query, BackgroundTasks
from backend.app.chatbot.engine import engine
from backend.app.database.connection import DB_AVAILABLE, SessionLocal

logger = logging.getLogger(__name__)

router = APIRouter()

# Environment Variables (আমরা পরে সেট করবো)
FB_VERIFY_TOKEN = os.getenv("FB_VERIFY_TOKEN", "banglamind_secure_token_123")
FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN", "")

# ─── Webhook Verification (GET) ──────────────────────────────
@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    """
    Facebook যখন প্রথমবার Webhook কানেক্ট করবে, তখন এই endpoint-এ GET request পাঠাবে।
    আমাদের verify_token মিললে তবেই কানেকশন সফল হবে।
    """
    if hub_mode == "subscribe" and hub_verify_token == FB_VERIFY_TOKEN:
        logger.info("✅ Facebook Webhook Verified Successfully!")
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification token mismatch")


# ─── Receive Messages (POST) ─────────────────────────────────
@router.post("/webhook")
async def receive_message(request: Request, background_tasks: BackgroundTasks):
    """
    ফেসবুক পেজে কেউ মেসেজ দিলে ফেসবুক এই endpoint-এ POST request পাঠাবে।
    """
    data = await request.json()
    
    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                # কেউ মেসেজ পাঠালে
                if "message" in messaging_event and "text" in messaging_event["message"]:
                    sender_id = messaging_event["sender"]["id"]
                    message_text = messaging_event["message"]["text"]
                    
                    logger.info(f"📩 Facebook থেকে মেসেজ এসেছে: {message_text}")
                    
                    # Background-এ উত্তর তৈরি করে পাঠানোর জন্য টাস্ক দিলাম
                    # যাতে ফেসবুকের রিকোয়েস্ট সাথে সাথে 200 OK রেসপন্স পায়
                    background_tasks.add_task(process_and_reply, sender_id, message_text)
                    
        return {"status": "ok"}
    
    raise HTTPException(status_code=404, detail="Not Found")


# ─── Process & Send Reply ────────────────────────────────────
async def process_and_reply(sender_id: str, message_text: str):
    """AI দিয়ে উত্তর তৈরি করে ফেসবুক API-এর মাধ্যমে রিপ্লাই পাঠায়।"""
    try:
        # ১. AI দিয়ে উত্তর তৈরি করো
        result = engine.process_message(message_text)
        reply_text = result["reply"]
        intent = result["intent"]
        
        # ২. Database-এ সেভ করো (ঐচ্ছিক)
        if DB_AVAILABLE and SessionLocal:
            from backend.app.database.db_service import save_message
            db = SessionLocal()
            try:
                save_message(
                    db=db,
                    user_message=message_text,
                    bot_reply=reply_text,
                    intent_tag=intent["tag"],
                    intent_source=intent["source"],
                    confidence=intent["confidence"],
                    score=float(intent["score"]),
                    language=result.get("language", "unknown"),
                    business_id="facebook_test", # আপাতত ডিফল্ট আইডি
                )
            finally:
                db.close()
                
        # ৩. ফেসবুকে রিপ্লাই পাঠাও
        await send_facebook_message(sender_id, reply_text)
        
    except Exception as e:
        logger.error(f"Error processing FB message: {e}")


async def send_facebook_message(recipient_id: str, text: str):
    """Facebook Graph API ব্যবহার করে কাস্টমারকে মেসেজ পাঠায়।"""
    if not FB_PAGE_ACCESS_TOKEN:
        logger.warning("⚠️ FB_PAGE_ACCESS_TOKEN নেই! ফেসবুকে মেসেজ পাঠানো যাচ্ছে না।")
        return

    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={FB_PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        if response.status_code == 200:
            logger.info("✅ ফেসবুকে সফলভাবে উত্তর পাঠানো হয়েছে!")
        else:
            logger.error(f"❌ ফেসবুকে মেসেজ পাঠাতে ব্যর্থ: {response.text}")
