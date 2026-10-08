from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Protocol
from fastapi import Request

@dataclass
class InboundMessage:
    provider_msg_id: str
    phone: str # E.164
    text: Optional[str]
    media_type: Optional[str] # image, audio, None
    received_at: datetime

class ChannelAdapter(Protocol):
    async def parse_inbound(self, request: Request) -> InboundMessage:
        ...
        
    def verify_signature(self, request: Request, raw_body: bytes) -> bool:
        ...
        
    async def send_text(self, phone: str, text: str) -> str:
        """Returns provider id of sent message"""
        ...
