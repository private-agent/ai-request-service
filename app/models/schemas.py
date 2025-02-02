from pydantic import BaseModel
from typing import Optional, List

class AIRequest(BaseModel):
    prompt: str
    providers: Optional[List[str]] = None  # 可选的提供商优先级列表

class AIResponse(BaseModel):
    provider: str
    model: str
    content: str