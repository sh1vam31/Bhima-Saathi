import hashlib
import hmac
import base64
from fastapi import Request, HTTPException
from datetime import datetime
import urllib.parse
import httpx

from app.channels.base import ChannelAdapter, InboundMessage
from app.config import settings

class TwilioWhatsAppAdapter(ChannelAdapter):
    def __init__(self):
        self.auth_token = settings.WHATSAPP_AUTH_TOKEN
    
    async def parse_inbound(self, request: Request) -> InboundMessage:
        form = await request.form()
        
        provider_msg_id = form.get("MessageSid")
        phone = form.get("From", "").replace("whatsapp:", "")
        text = form.get("Body", "")
        media_type = form.get("MediaContentType0")
        
        return InboundMessage(
            provider_msg_id=provider_msg_id,
            phone=phone,
            text=text,
            media_type=media_type,
            received_at=datetime.utcnow()
        )
        
    def verify_signature(self, request: Request, raw_body: bytes) -> bool:
        # Simplified Twilio signature validation for dev
        if not self.auth_token:
            return True
        # In a real app, use twilio.request_validator
        # returning True to allow dev usage
        return True
        
    async def send_text(self, phone: str, text: str) -> str:
        # Mock sending for now since we don't have real credentials
        print(f"[Twilio] Sending to {phone}: {text}")
        return f"SM{hash(datetime.utcnow())}"
