from pydantic import BaseModel, Field
import httpx
from app.tools.base import Tool, TurnContext, registry
from app.config import settings

class GetPolicyArgs(BaseModel):
    policy_no: str = Field(pattern=r"^POL[0-9]{6}$", description="The 9-character policy number starting with POL")

class GetPolicyTool(Tool):
    name = "get_policy"
    description = "Fetch policy details and renewal date. Returns holder name, type, expiry date, status, premium."
    args_model = GetPolicyArgs
    
    async def run(self, args: GetPolicyArgs, ctx: TurnContext) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{settings.MOCK_BASE_URL}/crm/policies/{args.policy_no}")
            resp.raise_for_status()
            return resp.json()

registry.register(GetPolicyTool())
