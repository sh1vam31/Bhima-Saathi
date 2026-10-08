from enum import Enum

class ConversationState(Enum):
    IDLE = "IDLE"
    AWAIT_POLICY_NO = "AWAIT_POLICY_NO"
    POLICY_VERIFIED = "POLICY_VERIFIED"
    QUOTE_SHOWN = "QUOTE_SHOWN"
    AWAIT_PAYMENT = "AWAIT_PAYMENT"
    PAID = "PAID"
    CLAIM_COLLECTING = "CLAIM_COLLECTING"
    CLAIM_CONFIRM = "CLAIM_CONFIRM"
    CLAIM_RAISED = "CLAIM_RAISED"
    HANDOFF = "HANDOFF"

class StateMachine:
    @staticmethod
    def get_allowed_tools(state: str) -> list[str]:
        mapping = {
            ConversationState.IDLE.value: [],
            ConversationState.AWAIT_POLICY_NO.value: [],
            ConversationState.POLICY_VERIFIED.value: ["get_policy", "get_renewal_quote", "raise_claim", "get_claim_status"],
            ConversationState.QUOTE_SHOWN.value: ["get_renewal_quote", "create_payment_link"],
            ConversationState.AWAIT_PAYMENT.value: ["get_policy"],
            ConversationState.PAID.value: [],
            ConversationState.CLAIM_COLLECTING.value: [],
            ConversationState.CLAIM_CONFIRM.value: ["raise_claim"],
            ConversationState.CLAIM_RAISED.value: ["get_claim_status"],
            ConversationState.HANDOFF.value: [],
        }
        # handoff_to_human is generally allowed in many states on failure, 
        # but let's stick to the PRD C7 strict map and handle handoff globally if needed.
        return mapping.get(state, [])
