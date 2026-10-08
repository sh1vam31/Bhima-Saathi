from sqlalchemy.orm import Session
from datetime import datetime
import json
from app.db import models

class Repository:
    def __init__(self, db: Session):
        self.db = db
        
    def message_exists(self, provider_msg_id: str) -> bool:
        if not provider_msg_id:
            return False
        return self.db.query(models.Message).filter(models.Message.provider_msg_id == provider_msg_id).first() is not None

    def save_message(self, conv_id: str, turn_id: str, role: str, text: str, provider_msg_id: str = None, lang: str = None):
        msg = models.Message(
            message_id=provider_msg_id or f"msg_{turn_id}_{role}",
            conversation_id=conv_id,
            turn_id=turn_id,
            role=role,
            text=text,
            provider_msg_id=provider_msg_id,
            language_detected=lang,
            created_at=datetime.utcnow()
        )
        self.db.add(msg)
        self.db.commit()

    def save_tool_calls(self, turn_id: str, tool_records: list):
        for rec in tool_records:
            tc = models.ToolCall(
                call_id=rec.id,
                turn_id=turn_id,
                tool=rec.tool,
                request_json="{}", # Would log actual request args here
                response_json=rec.response,
                status=rec.status,
                created_at=datetime.utcnow()
            )
            self.db.add(tc)
        self.db.commit()

    def save_verifier_event(self, turn_id: str, verdict):
        violations_str = json.dumps([v.model_dump() for v in verdict.violations])
        ve = models.VerifierEvent(
            event_id=f"ve_{turn_id}_{datetime.utcnow().timestamp()}",
            turn_id=turn_id,
            claims_found="[]", # Would extract from draft
            decision=verdict.decision,
            reason=violations_str,
            created_at=datetime.utcnow()
        )
        self.db.add(ve)
        self.db.commit()
