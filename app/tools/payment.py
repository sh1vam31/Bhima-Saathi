from pydantic import BaseModel, Field
import httpx
from app.tools.base import Tool, TurnContext, registry
from app.config import settings

class CreatePaymentLinkArgs(BaseModel):
    policy_no: str = Field(pattern=r"^POL[0-9]{6}$", description="The policy number")
    quote_id: str = Field(description="The quote ID obtained from get_renewal_quote")
    amount: float = Field(minimum=1, description="The total amount to pay")

class CreatePaymentLinkTool(Tool):
    name = "create_payment_link"
    description = "Create a Razorpay payment link for a confirmed renewal quote. Call only after get_policy and get_renewal_quote succeeded and the user agreed."
    args_model = CreatePaymentLinkArgs
    
    async def run(self, args: CreatePaymentLinkArgs, ctx: TurnContext) -> dict:
        # In a real app we'd call Razorpay. We'll just mock the response here.
        return {
            "payment_link_id": f"plink_{args.quote_id[-4:]}",
            "url": f"https://rzp.io/i/test_{args.quote_id[-4:]}",
            "expires_at": "2026-11-02T18:30:00+05:30"
        }

registry.register(CreatePaymentLinkTool())
