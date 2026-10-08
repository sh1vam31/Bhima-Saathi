from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    String,
    Integer,
    Numeric,
    Date,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"
    
    customer_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    phone_hash = Column(String, nullable=False)
    preferred_language = Column(String, default="hinglish")
    
    policies = relationship("Policy", back_populates="customer")

class Policy(Base):
    __tablename__ = "policies"
    
    policy_no = Column(String, primary_key=True)
    customer_id = Column(String, ForeignKey("customers.customer_id"))
    type = Column(String) # 'car','bike','health'
    start_date = Column(Date)
    expiry_date = Column(Date, nullable=False)
    status = Column(String) # 'ACTIVE','EXPIRED','RENEWED'
    premium = Column(Numeric(10, 2))
    
    customer = relationship("Customer", back_populates="policies")
    quotes = relationship("Quote", back_populates="policy")
    payments = relationship("Payment", back_populates="policy")
    claims = relationship("Claim", back_populates="policy")

class Quote(Base):
    __tablename__ = "quotes"
    
    quote_id = Column(String, primary_key=True)
    policy_no = Column(String, ForeignKey("policies.policy_no"))
    amount = Column(Numeric(10, 2))
    taxes = Column(Numeric(10, 2))
    total = Column(Numeric(10, 2))
    valid_until = Column(DateTime)
    
    policy = relationship("Policy", back_populates="quotes")
    payments = relationship("Payment", back_populates="quote")

class Payment(Base):
    __tablename__ = "payments"
    
    payment_link_id = Column(String, primary_key=True)
    policy_no = Column(String, ForeignKey("policies.policy_no"))
    quote_id = Column(String, ForeignKey("quotes.quote_id"))
    amount = Column(Numeric(10, 2))
    status = Column(String) # 'CREATED','PAID','FAILED','EXPIRED'
    razorpay_event_id = Column(String, unique=True)
    paid_at = Column(DateTime)
    
    policy = relationship("Policy", back_populates="payments")
    quote = relationship("Quote", back_populates="payments")

class Claim(Base):
    __tablename__ = "claims"
    
    claim_id = Column(String, primary_key=True)
    policy_no = Column(String, ForeignKey("policies.policy_no"))
    incident_type = Column(String)
    incident_date = Column(Date)
    description = Column(Text)
    status = Column(String)
    updated_at = Column(DateTime)
    
    policy = relationship("Policy", back_populates="claims")

class Conversation(Base):
    __tablename__ = "conversations"
    
    conversation_id = Column(String, primary_key=True)
    phone_hash = Column(String, nullable=False)
    state = Column(String, nullable=False)
    context_json = Column(Text)
    language = Column(String)
    started_at = Column(DateTime, default=datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    outcome = Column(String)
    
    messages = relationship("Message", back_populates="conversation")
    handoffs = relationship("Handoff", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"
    
    message_id = Column(String, primary_key=True)
    conversation_id = Column(String, ForeignKey("conversations.conversation_id"))
    turn_id = Column(String, nullable=False)
    role = Column(String) # 'user','assistant','system'
    text = Column(Text)
    provider_msg_id = Column(String, unique=True)
    language_detected = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="messages")

class ToolCall(Base):
    __tablename__ = "tool_calls"
    
    call_id = Column(String, primary_key=True)
    turn_id = Column(String, index=True, nullable=False)
    tool = Column(String, nullable=False)
    request_json = Column(Text)
    response_json = Column(Text)
    status = Column(String)
    error_code = Column(String)
    latency_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class VerifierEvent(Base):
    __tablename__ = "verifier_events"
    
    event_id = Column(String, primary_key=True)
    turn_id = Column(String, index=True, nullable=False)
    claims_found = Column(Text)
    decision = Column(String) # 'pass','regenerate','fallback'
    reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Handoff(Base):
    __tablename__ = "handoffs"
    
    ticket_id = Column(String, primary_key=True)
    conversation_id = Column(String, ForeignKey("conversations.conversation_id"))
    reason = Column(Text)
    summary = Column(Text)
    status = Column(String, default='OPEN')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="handoffs")

class EvalRun(Base):
    __tablename__ = "eval_runs"
    
    run_id = Column(String, primary_key=True)
    prompt_version = Column(String)
    model = Column(String)
    git_sha = Column(String)
    metrics_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
