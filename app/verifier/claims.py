from enum import Enum
import re

class ClaimType(Enum):
    LINK_SENT = "link_sent"
    CLAIM_RAISED = "claim_raised"
    CLAIM_STATUS = "claim_status"
    POLICY_FACT = "policy_fact"
    PREMIUM_FACT = "premium_fact"
    PAYMENT_DONE = "payment_done"
    HANDOFF_DONE = "handoff_done"

EVIDENCE = {
    ClaimType.LINK_SENT: ("create_payment_link", None),
    ClaimType.CLAIM_RAISED: ("raise_claim", "claim_id"),
    ClaimType.HANDOFF_DONE: ("handoff_to_human", "ticket_id"),
    ClaimType.POLICY_FACT: ("get_policy", "expiry_date"),
    ClaimType.PREMIUM_FACT: ("get_renewal_quote", "total"),
    ClaimType.CLAIM_STATUS: ("get_claim_status", "status"),
}

PATTERNS = {
    ClaimType.LINK_SENT: [
        r"(payment )?link (bhej|send|sent|share)",  # EN / Hinglish
        r"link (bhej diya|bhej di|bhej raha)",
        r"\u0932\u093f\u0902\u0915.*(\u092d\u0947\u091c)",  # Hindi script
    ],
    ClaimType.CLAIM_RAISED: [r"claim (raise|register|file)d?", r"claim (kar diya|darj|ho gaya)"],
    ClaimType.PAYMENT_DONE: [r"payment (received|successful|mil gaya|ho gaya)", r"renew(ed| ho gaya)"],
    ClaimType.HANDOFF_DONE: [r"(connect|transfer)(ed)? (to|kar diya)", r"agent (se|ko) (connect|baat)"],
}

def scan_text_for_claims(text: str) -> list[ClaimType]:
    """Scan reply text with multilingual regex patterns to find undeclared claims."""
    found_claims = []
    text_lower = text.lower()
    for claim_type, regex_list in PATTERNS.items():
        for pattern in regex_list:
            if re.search(pattern, text_lower):
                if claim_type not in found_claims:
                    found_claims.append(claim_type)
                break
    return found_claims
