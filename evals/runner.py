import yaml
import os
import asyncio
from typing import Dict, Any, List
import json
import uuid

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.llm.client import OpenAIClient
from app.verifier.verifier import ActionVerifier
from app.conversation.manager import ConversationManager
from app.db.session import SessionLocal
from app.db import models
from app.llm.orchestrator import Orchestrator
from app.channels.base import InboundMessage

class EvalRunner:
    def __init__(self, scenarios_dir: str):
        self.scenarios_dir = scenarios_dir
        self.scenarios = self._load_scenarios()
        
    def _load_scenarios(self) -> List[Dict[Any, Any]]:
        scenarios = []
        if not os.path.exists(self.scenarios_dir):
            return scenarios
            
        for file in os.listdir(self.scenarios_dir):
            if file.endswith(".yaml"):
                with open(os.path.join(self.scenarios_dir, file), "r") as f:
                    scenarios.append(yaml.safe_load(f))
        return scenarios
        
    async def run_scenario(self, scenario: Dict[Any, Any]):
        print(f"Running scenario: {scenario.get('id')}")
        db = SessionLocal()
        manager = ConversationManager(db)
        
        # Fresh conversation for eval
        phone = f"+91000000{uuid.uuid4().hex[:4]}"
        conv = manager.load_or_create(phone)
        
        client = OpenAIClient()
        verifier = ActionVerifier()
        orchestrator = Orchestrator(client, verifier, manager)
        
        passed = True
        
        for turn in scenario.get("turns", []):
            user_text = turn.get("user")
            expect = turn.get("expect", {})
            
            msg = InboundMessage(
                provider_msg_id=f"eval_{uuid.uuid4().hex[:8]}",
                phone=phone,
                text=user_text,
                media_type=None,
                received_at=None
            )
            
            # Since this is an eval, we want to mock the tools based on scenario['mock_tools']
            # For this MVP runner, we'll just run the real tools against the mock services.
            # A full implementation would dynamically inject mock responses into the tool registry.
            
            turn_id = f"turn_{uuid.uuid4().hex[:8]}"
            
            db_msg = models.Message(
                message_id=msg.provider_msg_id, conversation_id=conv.conversation_id,
                turn_id=turn_id, role="user", text=user_text, language_detected="hinglish"
            )
            db.add(db_msg)
            db.commit()
            
            result = await orchestrator.run_turn(conv, msg, turn_id)
            
            # Save assistant message to advance history
            bot_msg = models.Message(
                message_id=f"bot_{turn_id}", conversation_id=conv.conversation_id,
                turn_id=turn_id, role="assistant", text=result.final_text, language_detected="hinglish"
            )
            db.add(bot_msg)
            db.commit()
            
            # Simple check
            if expect.get("reply_asks_for") == "policy_number" and "policy" not in result.final_text.lower():
                passed = False
                print(f"Failed expected policy ask. Got: {result.final_text}")
                
        db.close()
        
        return {
            "id": scenario.get("id"),
            "passed": passed,
            "metrics": {
                "task_completion": passed,
                "tool_call_accuracy": passed # placeholder
            }
        }
        
    async def run_all(self):
        tasks = [self.run_scenario(s) for s in self.scenarios]
        results = await asyncio.gather(*tasks)
        return results

if __name__ == "__main__":
    runner = EvalRunner("evals/scenarios")
    results = asyncio.run(runner.run_all())
    print("Eval Results:", results)
