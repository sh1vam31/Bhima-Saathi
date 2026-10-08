from typing import Protocol, List, Dict, Any, Optional
from dataclasses import dataclass
import json
import openai
from app.config import settings

@dataclass
class ToolCallRequest:
    id: str
    name: str
    arguments: str # JSON string

@dataclass
class LLMResponse:
    tool_calls: List[ToolCallRequest]
    text: Optional[str]
    usage: dict

class LLMClient(Protocol):
    async def complete(self, system: str, messages: List[Dict], tools: List[Dict], temperature: float) -> LLMResponse:
        ...

class OpenAIClient(LLMClient):
    def __init__(self):
        # Point to Groq's OpenAI-compatible endpoint if LLM_PROVIDER is groq
        if settings.LLM_PROVIDER.lower() == "groq":
            self.client = openai.AsyncOpenAI(
                api_key=settings.GROQ_API_KEY or settings.LLM_API_KEY,
                base_url="https://api.groq.com/openai/v1"
            )
            self.model = "llama3-70b-8192" # or mixtral-8x7b-32768
        else:
            self.client = openai.AsyncOpenAI(api_key=settings.LLM_API_KEY)
            self.model = "gpt-4o-mini"
        
    async def complete(self, system: str, messages: List[Dict], tools: List[Dict], temperature: float = 0.2) -> LLMResponse:
        api_messages = [{"role": "system", "content": system}] + messages
        
        kwargs = {
            "model": self.model,
            "messages": api_messages,
            "temperature": temperature,
        }
        
        if tools:
            # Format for OpenAI
            openai_tools = [{"type": "function", "function": t} for t in tools]
            kwargs["tools"] = openai_tools
            
        # Groq's structured output parsing via json_object
        kwargs["response_format"] = {"type": "json_object"}
            
        response = await self.client.chat.completions.create(**kwargs)
        
        choice = response.choices[0].message
        
        tool_calls = []
        if choice.tool_calls:
            for tc in choice.tool_calls:
                tool_calls.append(ToolCallRequest(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=tc.function.arguments
                ))
                
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }
        
        return LLMResponse(
            tool_calls=tool_calls,
            text=choice.content,
            usage=usage
        )
