from pydantic import BaseModel, Field
import httpx
from app.tools.base import Tool, TurnContext, registry
from app.config import settings

class GetRenewalQuoteArgs(BaseModel):
    policy_no: str = Field(pattern=r"^POL[0-9]{6}$", description="The policy number")

class GetRenewalQuoteTool(Tool):
    name = "get_renewal_quote"
    description = "Compute renewal premium. Returns premium, taxes, total, quote_id, validity."
    args_model = GetRenewalQuoteArgs
    
    async def run(self, args: GetRenewalQuoteArgs, ctx: TurnContext) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{settings.MOCK_BASE_URL}/pricing/quote", params={"policy_no": args.policy_no})
            resp.raise_for_status()
            return resp.json()

registry.register(GetRenewalQuoteTool())
