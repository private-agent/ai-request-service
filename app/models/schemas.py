from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal
from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam

ChatMessage = ChatCompletionMessageParam

class AIRequest(BaseModel):
    messages: List[ChatMessage]
    providers: Optional[List[str]] = None
    stream: Optional[bool] = False
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = None

    @field_validator("messages")
    @classmethod
    def validate_messages(cls, v):
        if not v:
            raise ValueError("消息列表不能为空")
        return v

class ChatChoice(BaseModel):
    finish_reason: str
    index: int
    message: ChatMessage

class ChatUsage(BaseModel):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int

class ExtendedChatCompletion(ChatCompletion):
    provider: str

AIResponse = ExtendedChatCompletion
