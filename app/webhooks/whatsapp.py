from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from app.channels.whatsapp_twilio import TwilioWhatsAppAdapter

router = APIRouter()
adapter = TwilioWhatsAppAdapter()

from app.db.session import SessionLocal
from app.conversation.manager import ConversationManager
from app.conversation.language import detect_language
from app.llm.client import OpenAIClient
from app.verifier.verifier import ActionVerifier
from app.llm.orchestrator import Orchestrator
from app.db.repo import Repository
import uuid

async def process_inbound_task(msg):
    db = SessionLocal()
    try:
        repo = Repository(db)
        if repo.message_exists(msg.provider_msg_id):
            return # Idempotency
            
        manager = ConversationManager(db)
        conv = manager.load_or_create(msg.phone)
        turn_id = f"turn_{uuid.uuid4().hex[:8]}"
        
        lang = detect_language(msg.text, prev=conv.language)
        conv.language = lang
        
        repo.save_message(conv.conversation_id, turn_id, "user", msg.text, msg.provider_msg_id, lang)
        
        llm = OpenAIClient()
        verifier = ActionVerifier()
        orchestrator = Orchestrator(llm, verifier, manager)
        
        # We need to monkey-patch the orchestrator just to inject the repo to log tool calls.
        # In a cleaner architecture, the orchestrator would take the repo in __init__.
        result = await orchestrator.run_turn(conv, msg, turn_id)
        
        repo.save_message(conv.conversation_id, turn_id, "assistant", result.final_text, None, lang)
        manager.save(conv)
        
        await adapter.send_text(msg.phone, result.final_text)
    finally:
        db.close()

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
