from pydantic import BaseModel, Field
import httpx
from app.tools.base import Tool, TurnContext, registry
from app.config import settings

class HandoffToHumanArgs(BaseModel):
    reason: str = Field(description="Reason for escalation")
    summary: str = Field(description="Summary of the user issue")

class HandoffToHumanTool(Tool):
    name = "handoff_to_human"
    description = "Escalate to an agent. Returns ticket_id."
    args_model = HandoffToHumanArgs
    
    async def run(self, args: HandoffToHumanArgs, ctx: TurnContext) -> dict:
        async with httpx.AsyncClient() as client:
            payload = args.model_dump()
            payload["conversation_id"] = ctx.conversation_id
            resp = await client.post(f"{settings.MOCK_BASE_URL}/handoff/tickets", json=payload)
            resp.raise_for_status()
            return resp.json()

registry.register(HandoffToHumanTool())
