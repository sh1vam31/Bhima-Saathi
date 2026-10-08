from pydantic import BaseModel, Field
import httpx
from app.tools.base import Tool, TurnContext, registry
from app.config import settings

class RaiseClaimArgs(BaseModel):
    policy_no: str = Field(description="The policy number")
    incident_type: str = Field(description="Type of incident")
    incident_date: str = Field(description="Date of incident in ISO format")
    description: str = Field(description="Short description of damage or incident")

class RaiseClaimTool(Tool):
    name = "raise_claim"
    description = "Register a claim. Returns claim_id, status."
    args_model = RaiseClaimArgs
    
    async def run(self, args: RaiseClaimArgs, ctx: TurnContext) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{settings.MOCK_BASE_URL}/claims", json=args.model_dump())
            resp.raise_for_status()
            return resp.json()

class GetClaimStatusArgs(BaseModel):
    claim_id: str = Field(description="The claim ID")

class GetClaimStatusTool(Tool):
    name = "get_claim_status"
    description = "Retrieve claim progress. Returns status, last update, next step."
    args_model = GetClaimStatusArgs
    
    async def run(self, args: GetClaimStatusArgs, ctx: TurnContext) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{settings.MOCK_BASE_URL}/claims/{args.claim_id}")
            resp.raise_for_status()
            return resp.json()

registry.register(RaiseClaimTool())
registry.register(GetClaimStatusTool())
