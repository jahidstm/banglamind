"""
BanglaMind — SSLCommerz Payment Integration
============================================
পেমেন্ট flow:
1. POST /api/payment/initiate  → SSLCommerz session তৈরি → GatewayPageURL return
2. POST /api/payment/success   → SSLCommerz callback (payment সফল)
3. POST /api/payment/fail      → SSLCommerz callback (payment ব্যর্থ)
4. POST /api/payment/cancel    → SSLCommerz callback (user cancel করেছে)
5. GET  /api/payment/plans     → সব প্ল্যান দেখো
"""
import os
import uuid
import logging
import httpx
from datetime import datetime, timedelta
from fastapi import APIRouter, Request, Form, HTTPException, Header
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from typing import Optional

from backend.app.database.connection import DB_AVAILABLE, SessionLocal
from backend.app.database.models import Business, Subscription, PLANS
from backend.app.database.db_service import get_business_by_api_key

logger = logging.getLogger(__name__)
router = APIRouter()

# ─── SSLCommerz Config ─────────────────────────────────────────────
SSLC_STORE_ID   = os.getenv("SSLC_STORE_ID", "")
SSLC_STORE_PASS = os.getenv("SSLC_STORE_PASS", "")
SSLC_IS_SANDBOX = os.getenv("SSLC_SANDBOX", "true").lower() == "true"

SSLC_SESSION_URL = (
    "https://sandbox.sslcommerz.com/gwprocess/v4/api.php"
    if SSLC_IS_SANDBOX
    else "https://securepay.sslcommerz.com/gwprocess/v4/api.php"
)
SSLC_VALIDATE_URL = (
    "https://sandbox.sslcommerz.com/validator/api/validationserverAPI.php"
    if SSLC_IS_SANDBOX
    else "https://securepay.sslcommerz.com/validator/api/validationserverAPI.php"
)

BASE_URL = os.getenv("BASE_URL", "https://banglamind.onrender.com")


# ─── Schemas ──────────────────────────────────────────────────────

class PaymentInitiate(BaseModel):
    plan: str          # "basic" or "pro"
    customer_name: str
    customer_email: str
    customer_phone: str


# ─── Helper ───────────────────────────────────────────────────────

def _get_business_by_key(api_key: str, db):
    biz = get_business_by_api_key(db, api_key)
    if not biz or not biz.is_active:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return biz


# ─── Endpoints ────────────────────────────────────────────────────

@router.get("/plans")
def get_plans():
    """সব সাবস্ক্রিপশন প্ল্যান দেখো।"""
    return {
        "plans": [
            {
                "id": plan_id,
                "name": plan["name"],
                "price_bdt": plan["price"],
                "monthly_messages": plan["monthly_limit"],
                "features": _plan_features(plan_id),
            }
            for plan_id, plan in PLANS.items()
        ]
    }


def _plan_features(plan_id: str) -> list:
    features = {
        "free":  ["৫০টি মেসেজ/মাস", "Facebook Messenger", "বাংলা AI", "Basic Analytics"],
        "basic": ["১,০০০টি মেসেজ/মাস", "Facebook + WhatsApp", "বাংলা AI", "Full Analytics", "Priority Support"],
        "pro":   ["১০,০০০টি মেসেজ/মাস", "সব Channel", "BanglaBERT AI", "Advanced Analytics", "Dedicated Support", "Custom FAQ"],
    }
    return features.get(plan_id, [])


@router.post("/initiate")
async def initiate_payment(
    data: PaymentInitiate,
    x_api_key: str = Header(..., alias="X-API-Key"),
):
    """পেমেন্ট শুরু করো। SSLCommerz-এর Gateway URL ফেরত দেবে।"""
    if not SSLC_STORE_ID:
        raise HTTPException(
            status_code=503,
            detail="Payment gateway এখনো configure হয়নি। SSLCommerz credentials দরকার।"
        )

    plan = data.plan.lower()
    if plan not in PLANS or plan == "free":
        raise HTTPException(status_code=400, detail="Invalid plan. 'basic' বা 'pro' দিন।")

    plan_info = PLANS[plan]

    if not DB_AVAILABLE or not SessionLocal:
        raise HTTPException(status_code=503, detail="Database unavailable")

    db = SessionLocal()
    try:
        biz = _get_business_by_key(x_api_key, db)

        # Unique transaction ID তৈরি করো
        tran_id = f"BM-{biz.id[:8]}-{uuid.uuid4().hex[:8].upper()}"

        # Subscription record তৈরি করো (pending status)
        sub = Subscription(
            business_id=biz.id,
            plan=plan,
            amount=plan_info["price"],
            tran_id=tran_id,
            status="pending",
        )
        db.add(sub)
        db.commit()

        # SSLCommerz Session Request
        payload = {
            "store_id":          SSLC_STORE_ID,
            "store_passwd":      SSLC_STORE_PASS,
            "total_amount":      str(plan_info["price"]),
            "currency":          "BDT",
            "tran_id":           tran_id,
            "success_url":       f"{BASE_URL}/api/payment/success",
            "fail_url":          f"{BASE_URL}/api/payment/fail",
            "cancel_url":        f"{BASE_URL}/api/payment/cancel",
            "cus_name":          data.customer_name,
            "cus_email":         data.customer_email,
            "cus_phone":         data.customer_phone,
            "cus_add1":          "Bangladesh",
            "cus_city":          "Dhaka",
            "cus_country":       "Bangladesh",
            "shipping_method":   "NO",
            "product_name":      f"BanglaMind {plan_info['name']} Plan",
            "product_category":  "SaaS",
            "product_profile":   "general",
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(SSLC_SESSION_URL, data=payload)
            resp_data = resp.json()

        if resp_data.get("status") != "SUCCESS":
            logger.error(f"SSLCommerz session error: {resp_data}")
            raise HTTPException(status_code=502, detail="Payment gateway-এ সমস্যা হয়েছে।")

        gateway_url = resp_data.get("GatewayPageURL")
        return {
            "gateway_url": gateway_url,
            "tran_id": tran_id,
            "amount": plan_info["price"],
            "plan": plan,
            "message": f"নিচের URL-এ গিয়ে পেমেন্ট করুন।",
        }

    finally:
        db.close()


@router.post("/success")
async def payment_success(request: Request):
    """SSLCommerz payment সফল হলে এই endpoint call হবে।"""
    form = await request.form()
    tran_id     = form.get("tran_id", "")
    val_id      = form.get("val_id", "")
    ssl_tran_id = form.get("bank_tran_id", "")
    status      = form.get("status", "")

    logger.info(f"💳 Payment success callback: tran_id={tran_id}, val_id={val_id}")

    if not DB_AVAILABLE or not SessionLocal:
        return HTMLResponse("<h2>Payment recorded. Database unavailable for full update.</h2>")

    db = SessionLocal()
    try:
        # ১. Validate করো SSLCommerz-এর কাছে
        validated = await _validate_payment(val_id)
        if not validated:
            logger.error(f"Payment validation FAILED for tran_id={tran_id}")
            return HTMLResponse(_payment_page("failed", "Payment validation ব্যর্থ হয়েছে।"))

        # ২. Subscription আপডেট করো
        sub = db.query(Subscription).filter(Subscription.tran_id == tran_id).first()
        if not sub:
            return HTMLResponse(_payment_page("failed", "Transaction খুঁজে পাওয়া যায়নি।"))

        now = datetime.utcnow()
        sub.status      = "success"
        sub.ssl_tran_id = ssl_tran_id
        sub.valid_from  = now
        sub.valid_until = now + timedelta(days=30)
        sub.updated_at  = now

        # ৩. Business-এর plan আপডেট করো
        biz = db.query(Business).filter(Business.id == sub.business_id).first()
        if biz:
            biz.plan        = sub.plan
            biz.plan_expires = sub.valid_until
            biz.updated_at  = now

        db.commit()
        logger.info(f"✅ Subscription activated: business={sub.business_id}, plan={sub.plan}")

        return HTMLResponse(_payment_page("success", f"{sub.plan.capitalize()} Plan সক্রিয় হয়েছে!"))

    finally:
        db.close()


@router.post("/fail")
async def payment_fail(request: Request):
    """SSLCommerz payment ব্যর্থ হলে।"""
    form = await request.form()
    tran_id = form.get("tran_id", "")
    logger.warning(f"❌ Payment failed: tran_id={tran_id}")

    if DB_AVAILABLE and SessionLocal:
        db = SessionLocal()
        try:
            sub = db.query(Subscription).filter(Subscription.tran_id == tran_id).first()
            if sub:
                sub.status = "failed"
                sub.updated_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()

    return HTMLResponse(_payment_page("failed", "পেমেন্ট ব্যর্থ হয়েছে। আবার চেষ্টা করুন।"))


@router.post("/cancel")
async def payment_cancel(request: Request):
    """User পেমেন্ট cancel করলে।"""
    form = await request.form()
    tran_id = form.get("tran_id", "")
    logger.info(f"🚫 Payment cancelled: tran_id={tran_id}")
    return HTMLResponse(_payment_page("cancel", "পেমেন্ট বাতিল করা হয়েছে।"))


# ─── Internal helpers ─────────────────────────────────────────────

async def _validate_payment(val_id: str) -> bool:
    """SSLCommerz Order Validation API দিয়ে payment verify করো।"""
    if not val_id:
        return False
    try:
        params = {
            "val_id":       val_id,
            "store_id":     SSLC_STORE_ID,
            "store_passwd": SSLC_STORE_PASS,
            "format":       "json",
        }
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(SSLC_VALIDATE_URL, params=params)
            data = resp.json()
        return data.get("status") == "VALID"
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return False


def _payment_page(status: str, message: str) -> str:
    """Payment result HTML page।"""
    colors = {"success": "#22c55e", "failed": "#ef4444", "cancel": "#f59e0b"}
    icons  = {"success": "✅", "failed": "❌", "cancel": "🚫"}
    color  = colors.get(status, "#6b7280")
    icon   = icons.get(status, "ℹ️")
    return f"""<!DOCTYPE html>
<html lang="bn">
<head><meta charset="UTF-8"><title>BanglaMind — Payment {status.title()}</title>
<style>
  body {{ font-family: Arial, sans-serif; display: flex; align-items: center;
         justify-content: center; min-height: 100vh; margin: 0;
         background: #0f172a; color: #f1f5f9; }}
  .card {{ text-align: center; padding: 40px; border-radius: 16px;
           background: #1e293b; box-shadow: 0 25px 50px rgba(0,0,0,0.5); max-width: 400px; }}
  .icon {{ font-size: 64px; margin-bottom: 16px; }}
  h2 {{ color: {color}; margin: 0 0 12px; }}
  p {{ color: #94a3b8; margin: 0 0 24px; }}
  a {{ display: inline-block; padding: 12px 24px; background: #6366f1;
      color: white; text-decoration: none; border-radius: 8px; font-weight: bold; }}
  a:hover {{ background: #4f46e5; }}
</style></head>
<body>
  <div class="card">
    <div class="icon">{icon}</div>
    <h2>Payment {status.title()}</h2>
    <p>{message}</p>
    <a href="/">BanglaMind-এ ফিরে যান</a>
  </div>
</body></html>"""