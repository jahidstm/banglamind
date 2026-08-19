"""
BanglaMind -- WhatsApp Webhook (Twilio Sandbox)
================================================
WhatsApp থেকে মেসেজ গ্রহণ করে এবং AI-এর উত্তর Twilio API-এর মাধ্যমে পাঠায়।
"""
import logging
from fastapi import APIRouter, Form, Response, Request
from twilio.twiml.messaging_response import MessagingResponse

from backend.app.chatbot.engine import engine
from backend.app.database.connection import DB_AVAILABLE, SessionLocal

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/webhook")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...),
):
    """
    Twilio থেকে WhatsApp মেসেজ আসলে এই endpoint কল হবে।
    """
    sender_id = From
    message_text = Body.strip()
    
    logger.info(f"📱 WhatsApp থেকে মেসেজ এসেছে ({sender_id}): {message_text}")
    
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
                    business_id="whatsapp_test", # আপাতত ডিফল্ট আইডি
                )
            except Exception as db_e:
                logger.warning(f"DB Save error ignored: {db_e}")
            finally:
                db.close()
                
    except Exception as e:
        logger.error(f"Error processing WhatsApp message: {e}")
        reply_text = "দুঃখিত, কোনো একটি সমস্যা হয়েছে। একটু পর আবার চেষ্টা করুন।"
        
    # ৩. Twilio TwiML রেসপন্স তৈরি করো
    twiml_response = MessagingResponse()
    twiml_response.message(reply_text)
    
    # Twilio Expects XML response
    return Response(content=str(twiml_response), media_type="application/xml")