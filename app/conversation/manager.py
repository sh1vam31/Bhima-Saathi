from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
import json

from app.db import models
from app.conversation.state import ConversationState

class ConversationManager:
    def __init__(self, db: Session):
        self.db = db
        
    def load_or_create(self, phone: str) -> models.Conversation:
        # Simplistic phone hashing for dev
        phone_hash = str(hash(phone)) 
        
        # Look for an active conversation (not ended and active in last 30 mins)
        cutoff = datetime.utcnow() - timedelta(minutes=30)
        conv = self.db.query(models.Conversation).filter(
            models.Conversation.phone_hash == phone_hash,
            models.Conversation.ended_at == None,
            models.Conversation.last_active_at > cutoff,
            models.Conversation.state != ConversationState.PAID.value,
            models.Conversation.state != ConversationState.CLAIM_RAISED.value,
            models.Conversation.state != ConversationState.HANDOFF.value
        ).first()
        
        if not conv:
            conv = models.Conversation(
                conversation_id=f"CONV{uuid.uuid4().hex[:12].upper()}",
                phone_hash=phone_hash,
                state=ConversationState.IDLE.value,
                language="hinglish",
                context_json="{}"
            )
            self.db.add(conv)
            self.db.commit()
            
        return conv
        
    def save(self, conv: models.Conversation):
        conv.last_active_at = datetime.utcnow()
        self.db.commit()
        
    def set_state(self, conv: models.Conversation, state: str):
        conv.state = state
        self.db.commit()
        
    def get_history_window(self, conv: models.Conversation, max_turns: int = 12) -> list[dict]:
        messages = self.db.query(models.Message).filter(
            models.Message.conversation_id == conv.conversation_id
        ).order_by(models.Message.created_at.asc()).limit(max_turns * 2).all()
        
        history = []
        for m in messages:
            history.append({
                "role": m.role,
                "content": m.text
            })
        return history
