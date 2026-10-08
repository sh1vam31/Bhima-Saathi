from dataclasses import dataclass
from typing import Literal, List, Optional
import json
import time

from app.db import models
from app.channels.base import InboundMessage
from app.llm.client import LLMClient
from app.tools.base import registry, TurnContext, ToolResult
from app.verifier.verifier import ActionVerifier
from app.conversation.manager import ConversationManager

@dataclass
class ClaimedAction:
    type: str
    tool_call_id: Optional[str]

@dataclass
class Draft:
    reply_text: str
    language: Literal["en", "hi", "hinglish"]
    claimed_actions: List[ClaimedAction]

@dataclass
class TurnResult:
    final_text: str
    state_updates: dict

MAX_TOOL_ITERATIONS = 4

class Orchestrator:
    def __init__(self, llm_client: LLMClient, verifier: ActionVerifier, manager: ConversationManager):
        self.llm = llm_client
        self.verifier = verifier
        self.manager = manager
        
    def _parse_draft(self, text: str) -> Draft:
        try:
            data = json.loads(text)
            claims = [ClaimedAction(**c) for c in data.get("claimed_actions", [])]
            return Draft(
                reply_text=data.get("reply_text", ""),
                language=data.get("language", "hinglish"),
                claimed_actions=claims
            )
        except Exception:
            # Fallback
            return Draft(reply_text=text, language="hinglish", claimed_actions=[])

    async def run_turn(self, conv: models.Conversation, msg: InboundMessage, turn_id: str) -> TurnResult:
        history = self.manager.get_history_window(conv)
        messages = history + [{"role": "user", "content": msg.text}]
        
        import app.llm.prompts as prompts
        system_prompt = prompts.build(
            version="v1",
            lang=conv.language,
            state=conv.state,
            context=conv.context_json
        )
        
        ctx = TurnContext(conversation_id=conv.conversation_id, turn_id=turn_id)
        
        # We need a way to log tool calls to the DB. For now, accumulate them in memory for the verifier.
        from app.verifier.verifier import ToolCallRecord
        tool_log_records = []
        
        for i in range(MAX_TOOL_ITERATIONS):
            resp = await self.llm.complete(system_prompt, messages, registry.schemas(), temperature=0.2)
            
            if not resp.tool_calls:
                draft = self._parse_draft(resp.text)
                break
                
            messages.append({"role": "assistant", "content": None, "tool_calls": [{"id": tc.id, "function": {"name": tc.name, "arguments": tc.arguments}, "type": "function"} for tc in resp.tool_calls]})
            
            for call in resp.tool_calls:
                tool = registry.get(call.name)
                start_time = time.time()
                
                status = "error"
                result_data = None
                error_code = None
                
                if tool:
                    try:
                        args = tool.args_model.model_validate_json(call.arguments)
                        result_data = await tool.run(args, ctx)
                        status = "success"
                    except Exception as e:
                        error_code = "TOOL_ERROR"
                else:
                    error_code = "TOOL_NOT_FOUND"
                    
                latency = int((time.time() - start_time) * 1000)
                
                tool_res = ToolResult(
                    status=status,
                    data=result_data,
                    error_code=error_code,
                    request_id=f"req_{call.id}",
                    latency_ms=latency
                )
                
                # Format response for the LLM
                tool_response_str = json.dumps(tool_res.model_dump())
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "name": call.name,
                    "content": tool_response_str
                })
                
                # Log for verifier
                tool_log_records.append(ToolCallRecord(
                    id=call.id,
                    tool=call.name,
                    status=status,
                    response=tool_response_str
                ))
        else:
            # Fallback if too many iterations
            return TurnResult(final_text="I need to check that. Please wait.", state_updates={})
            
        # Run Action Verifier
        for attempt in range(2):
            verdict = self.verifier.verify(draft, tool_log_records)
            if verdict.decision == "pass":
                return TurnResult(final_text=draft.reply_text, state_updates={})
                
            if attempt == 0:
                # Regenerate
                violation_msgs = [f"Violation: {v.claim_type} due to {v.reason}" for v in verdict.violations]
                messages.append({"role": "assistant", "content": json.dumps({"reply_text": draft.reply_text, "language": draft.language, "claimed_actions": [{"type": c.type, "tool_call_id": c.tool_call_id} for c in draft.claimed_actions]})})
                messages.append({"role": "user", "content": "Your previous response was rejected by the verifier: " + "; ".join(violation_msgs) + ". Please fix the claims and provide a new JSON response."})
                resp = await self.llm.complete(system_prompt, messages, tools=[], temperature=0.2)
                draft = self._parse_draft(resp.text)
                
        return TurnResult(final_text="There was an issue processing your request. Please try again.", state_updates={})
