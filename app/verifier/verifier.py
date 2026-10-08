import json
import re
from typing import Literal, List, Dict, Any, Optional
from pydantic import BaseModel
from app.verifier.claims import ClaimType, EVIDENCE, scan_text_for_claims
from app.llm.orchestrator import Draft, ClaimedAction # Assuming we'll create this later

class ToolCallRecord(BaseModel):
    id: str
    tool: str
    status: str # "success" or "error"
    response: str # JSON string

class Violation(BaseModel):
    claim_type: str
    reason: str
    evidence_missing: str

class VerifierResult(BaseModel):
    decision: Literal["pass", "regenerate", "fallback"]
    violations: List[Violation]

def values_match(text: str, response_json: str, field: str) -> bool:
    """Basic value matching - extract numbers and compare."""
    try:
        response_data = json.loads(response_json)
        val = response_data.get("data", {}).get(field)
        if not val:
            return True # Not strict on values if missing in response for some reason
        
        # Simple number check
        if isinstance(val, (int, float)):
            # find numbers in text
            nums = re.findall(r'\d+(?:,\d+)*(?:\.\d+)?', text)
            normalized_nums = [float(n.replace(',', '')) for n in nums]
            if float(val) in normalized_nums:
                return True
            return False
        return True # Default to true for complex types for now
    except:
        return True

class ActionVerifier:
    def verify(self, draft: Draft, tool_log: List[ToolCallRecord]) -> VerifierResult:
        violations = []
        
        # 1. Collect declared claims
        claims_from_llm = [ClaimType(ca.type) for ca in draft.claimed_actions if ca.type in [e.value for e in ClaimType]]
        
        # 2. Scan reply text
        scanned_claims = scan_text_for_claims(draft.reply_text)
        
        # Dedupe
        all_claims = list(set(claims_from_llm + scanned_claims))
        
        for claim_type in all_claims:
            if claim_type == ClaimType.PAYMENT_DONE:
                violations.append(Violation(
                    claim_type=claim_type.value,
                    reason="llm_cannot_confirm_payment",
                    evidence_missing="webhook_only"
                ))
                continue
                
            if claim_type not in EVIDENCE:
                continue
                
            required_tool, required_field = EVIDENCE[claim_type]
            
            # Find a successful call for this tool
            successful_calls = [
                call for call in tool_log 
                if call.tool == required_tool and call.status == "success"
            ]
            
            # Optional: if claim came from LLM with a cited tool call ID
            cited_id = next((ca.tool_call_id for ca in draft.claimed_actions if ca.type == claim_type.value), None)
            
            if cited_id:
                call = next((c for c in successful_calls if c.id == cited_id), None)
            else:
                call = successful_calls[0] if successful_calls else None
                
            if not call:
                violations.append(Violation(
                    claim_type=claim_type.value,
                    reason=f"no_successful_{required_tool}_this_turn",
                    evidence_missing=required_tool
                ))
                continue
                
            if required_field and not values_match(draft.reply_text, call.response, required_field):
                violations.append(Violation(
                    claim_type=claim_type.value,
                    reason=f"value_mismatch_{required_field}",
                    evidence_missing=required_field
                ))
                
        decision: Literal["pass", "regenerate", "fallback"] = "pass"
        if violations:
            decision = "regenerate"
            
        return VerifierResult(decision=decision, violations=violations)
