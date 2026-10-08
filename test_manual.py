import asyncio
import os
import sys
from datetime import datetime

# Setup paths and environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.db.session import engine, SessionLocal
from app.db import models
from app.conversation.manager import ConversationManager
from app.llm.client import OpenAIClient
from app.verifier.verifier import ActionVerifier
from app.llm.orchestrator import Orchestrator
from app.channels.base import InboundMessage
import app.llm.prompts as prompts

async def run_manual_test():
    # Make sure DB is ready
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    manager = ConversationManager(db)
    client = OpenAIClient()
    verifier = ActionVerifier()
    
    # We patch orchestrator to use our new prompts module
    orchestrator = Orchestrator(client, verifier, manager)
    
    # Simple phone number for testing
    phone = "+919876543210"
    
    print("--- Bima Saathi Manual Test ---")
    print("Type 'exit' or 'quit' to stop.")
    print("Mock services must be running on port 8100!")
    print("-------------------------------")
    
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break
            
        conv = manager.load_or_create(phone)
        turn_id = f"turn_{int(datetime.utcnow().timestamp())}"
        
        msg = InboundMessage(
            provider_msg_id=f"msg_{turn_id}",
            phone=phone,
            text=user_input,
            media_type=None,
            received_at=datetime.utcnow()
        )
        
        # Save user message
        db_msg = models.Message(
            message_id=msg.provider_msg_id,
            conversation_id=conv.conversation_id,
            turn_id=turn_id,
            role="user",
            text=msg.text,
            language_detected="hinglish"
        )
        db.add(db_msg)
        db.commit()
        
        # We manually inject the prompt building into the Orchestrator for this test script
        orchestrator_old_run = orchestrator.run_turn
        
        # Run orchestrator
        try:
            print("Bot is thinking...")
            result = await orchestrator.run_turn(conv, msg, turn_id)
            print(f"Bot: {result.final_text}")
            
            # Save bot message
            bot_msg = models.Message(
                message_id=f"bot_{turn_id}",
                conversation_id=conv.conversation_id,
                turn_id=turn_id,
                role="assistant",
                text=result.final_text,
                language_detected="hinglish" # simplifying
            )
            db.add(bot_msg)
            db.commit()
            manager.save(conv)
            
        except Exception as e:
            print(f"Error during turn: {e}")
            
    db.close()

if __name__ == "__main__":
    asyncio.run(run_manual_test())
