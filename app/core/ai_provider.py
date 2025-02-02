from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import httpx
from openai import AsyncOpenAI

class AIProvider(ABC):
    @abstractmethod
    async def generate_response(self, prompt: str) -> Dict[str, Any]:
        """
        生成AI响应的抽象方法
        """
        pass

class OpenAIFormatProvider(AIProvider):
    """通用的OpenAI API格式提供商"""
    def __init__(self, api_key: Optional[str], base_url: Optional[str], model: str, max_tokens: int, provider_name: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.max_tokens = max_tokens
        self.provider_name = provider_name

    async def generate_response(self, prompt: str) -> Dict[str, Any]:
        try:
            client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )

            response = await client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens
            )

            return {
                "provider": self.provider_name,
                "model": self.model,
                "content": response.choices[0].message.content
            }
        except Exception as e:
            raise Exception(f"{self.provider_name} API error: {str(e)}")

class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str, model: str, max_tokens: int):
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens

    async def generate_response(self, prompt: str) -> Dict[str, Any]:
        try:
            # OpenAI API调用实现
            client = AsyncOpenAI(api_key=self.api_key)
            response = await client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens
            )

            return {
                "provider": "openai",
                "model": self.model,
                "content": response.choices[0].message.content
            }
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

class AnthropicProvider(AIProvider):
    def __init__(self, api_key: Optional[str], model: str, max_tokens: int):
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens

    async def generate_response(self, prompt: str) -> Dict[str, Any]:
        try:
            # Anthropic API调用实现
            from anthropic import AsyncAnthropic

            client = AsyncAnthropic(api_key=self.api_key)
            response = await client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )

            return {
                "provider": "anthropic",
                "model": self.model,
                "content": response.content
            }
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")

class OllamaProvider(AIProvider):
    def __init__(self, base_url: Optional[str], model: str, max_tokens: int):
        self.base_url = base_url.rstrip('/') if base_url else "http://localhost:11434"  # 提供默认值
        self.model = model
        self.max_tokens = max_tokens

    async def generate_response(self, prompt: str) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "num_predict": self.max_tokens,
                            "temperature": 0.7
                        }
                    },
                    timeout=60.0  # 设置较长的超时时间，因为本地模型可能需要更多时间
                )

                if response.status_code != 200:
                    raise Exception(f"HTTP {response.status_code}: {response.text}")

                result = response.json()

                return {
                    "provider": "ollama",
                    "model": self.model,
                    "content": result.get("response", "")
                }
        except Exception as e:
            raise Exception(f"Ollama API error: {str(e)}")