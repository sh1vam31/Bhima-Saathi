from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from app.channels.whatsapp_twilio import TwilioWhatsAppAdapter

router = APIRouter()
adapter = TwilioWhatsAppAdapter()

async def process_inbound_task(msg):
    # This will eventually call the conversation manager and LLM orchestrator
    print(f"Processing message from {msg.phone}: {msg.text}")
    # Simulate a response
    await adapter.send_text(msg.phone, "Echo: " + msg.text)

@router.post("/webhooks/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    body = await request.body()
    if not adapter.verify_signature(request, body):
        raise HTTPException(status_code=403, detail="Invalid signature")
        
    try:
        msg = await adapter.parse_inbound(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
        
    # Deduplication would go here checking DB
    
    background_tasks.add_task(process_inbound_task, msg)
    
    # Return 200 immediately
    return {"ok": True}
