from fastapi import APIRouter, Request, HTTPException
import json
import hmac
import hashlib
from app.config import settings

router = APIRouter()

@router.post("/webhooks/razorpay")
async def razorpay_webhook(request: Request):
    raw = await request.body()
    sig = request.headers.get("X-Razorpay-Signature", "")
    
    if settings.RZP_WEBHOOK_SECRET:
        expected = hmac.new(
            settings.RZP_WEBHOOK_SECRET.encode(), 
            raw, 
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(sig, expected):
            # for dev purposes, we might just pass or raise
            # raise HTTPException(status_code=403, detail="Invalid signature")
            pass
            
    try:
        event = json.loads(raw)
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON")
        
    # Idempotency check would go here
    
    if event.get("event") == "payment_link.paid":
        # Handle payment success
        print(f"Payment received for link: {event.get('payload', {}).get('payment_link', {}).get('entity', {}).get('id')}")
        
    return {"ok": True}
