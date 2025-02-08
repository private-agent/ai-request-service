import time
from abc import ABC, abstractmethod
from typing import Optional, List
from openai import AsyncOpenAI
from openai.types.chat.chat_completion import ChatCompletion
from anthropic.types.message import Message as AnthropicMessage
from anthropic.types.text_block import TextBlock
from ollama import AsyncClient as AsyncOllama
from ollama import Options as OllamaOptions
from ollama import ChatResponse as OllamaChatCompletion
from ..models.schemas import ChatMessage, ExtendedChatCompletion
from ..utils.logger import logger

class AIProvider(ABC):
    @abstractmethod
    async def generate_response(
        self,
        messages: List[ChatMessage],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> ExtendedChatCompletion:
        """生成AI响应的抽象方法"""
        pass

class OpenAIFormatProvider(AIProvider):
    """通用的OpenAI API格式提供商"""

    def __init__(
        self,
        api_key: Optional[str],
        base_url: Optional[str],
        model: str,
        max_tokens: int,
        provider_name: str,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.max_tokens = max_tokens
        self.provider_name = provider_name

    async def generate_response(
        self,
        messages: List[ChatMessage],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> ExtendedChatCompletion:
        try:
            logger.info(f"[{self.provider_name}] 开始生成响应")
            logger.debug(f"[{self.provider_name}] 参数: model={self.model}, max_tokens={max_tokens or self.max_tokens}, temperature={temperature or 0.7}")

            client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or 0.7,
            )

            logger.info(f"[{self.provider_name}] 成功生成响应")
            return ExtendedChatCompletion(
                **response.model_dump(), provider=self.provider_name
            )
        except Exception as e:
            error_msg = f"{self.provider_name} API error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg)

class AnthropicProvider(AIProvider):
    def __init__(self, api_key: Optional[str], model: str, max_tokens: int):
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.provider_name = "anthropic"  # 添加provider名称

    def _convert_anthropic_to_openai_format(
        self, anthropic_response: AnthropicMessage
    ) -> ExtendedChatCompletion:
        """将Anthropic响应转换为OpenAI格式"""
        # 创建Choice对象
        choice = {
            "finish_reason": anthropic_response.stop_reason or "stop",  # 使用stop_reason
            "index": 0,
            "message": {
                "role": anthropic_response.role,
                "content": "".join(
                    [
                        block.text if isinstance(block, TextBlock) else ""  # 仅提取TextBlock的text
                        for block in anthropic_response.content
                    ]
                ),  # 合并内容块
            },
            "logprobs": None,  # 根据需要添加logprobs
        }

        # 创建ChatCompletion对象
        completion_data = ChatCompletion(
            **{
                "id": anthropic_response.id,
                "choices": [choice],
                "created": int(time.time()),
                "model": self.model,
                "object": "chat.completion",
                "usage": anthropic_response.usage,  # 使用原始的usage信息
            }
        )

        return ExtendedChatCompletion(
            **completion_data.model_dump(), provider=self.provider_name
        )

    async def generate_response(
        self,
        messages: List[ChatMessage],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> ExtendedChatCompletion:
        from anthropic import AsyncAnthropic

        logger.info(f"[{self.provider_name}] 开始生成响应")
        logger.debug(f"[{self.provider_name}] 参数: model={self.model}, max_tokens={max_tokens or self.max_tokens}, temperature={temperature or 0.7}")

        try:
            client = AsyncAnthropic(api_key=self.api_key)
            response = await client.messages.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": str(msg.get("content", ""))}
                    for msg in messages
                ],
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or 0.7,
            )

            logger.info(f"[{self.provider_name}] 成功生成响应")
            return self._convert_anthropic_to_openai_format(response)
        except Exception as e:
            error_msg = f"{self.provider_name} API error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg)

class OllamaProvider(AIProvider):
    def __init__(
        self, base_url: Optional[str], model: str, max_tokens: int, provider_name: str
    ):
        self.base_url = base_url.rstrip("/") if base_url else "http://localhost:11434"
        self.model = model
        self.max_tokens = max_tokens
        self.provider_name = provider_name

    def _convert_ollama_to_openai_format(
        self, ollama_response: OllamaChatCompletion
    ) -> ExtendedChatCompletion:

        # 判断是否有思维链
        if ollama_response.message.content and "</tink>" in ollama_response.message.content:
            reasoning_content = ollama_response.message.content.split("</tink>")[
                0
            ].replace("<tink>", "")
            message_content = ollama_response.message.content.split("</tink>")[1]
        else:
            reasoning_content = None
            message_content = ollama_response.message.content

        """将Ollama响应转换为OpenAI格式"""
        # 创建Choice对象
        choice = {
            "finish_reason": "stop",  # Ollama目前没有提供具体的finish_reason
            "index": 0,
            "message": {
                "role": ollama_response.message.role,
                "content": message_content,
                "reasoning_content": reasoning_content,
            },
            "logprobs": None,
        }

        # 创建ChatCompletion对象
        completion_data = ChatCompletion(
            **{
                "id": f"ollama-{int(time.time())}",  # 生成一个唯一ID
                "choices": [choice],
                "created": int(time.time()),
                "model": self.model,
                "object": "chat.completion",
                "usage": {
                    "prompt_tokens": ollama_response.prompt_eval_count or 0,
                    "completion_tokens": ollama_response.eval_count or 0,
                    "total_tokens": (ollama_response.prompt_eval_count or 0)
                    + (ollama_response.eval_count or 0),
                },
            }
        )

        return ExtendedChatCompletion(
            **completion_data.model_dump(), provider=self.provider_name
        )

    async def generate_response(
        self,
        messages: List[ChatMessage],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> ExtendedChatCompletion:
        try:
            logger.info(f"[{self.provider_name}] 开始生成响应")
            logger.debug(f"[{self.provider_name}] 参数: model={self.model}, base_url={self.base_url}, temperature={temperature or 0.7}")

            client = AsyncOllama(host=self.base_url)
            response = await client.chat(
                model=self.model,
                messages=[
                    {
                        "role": msg.get("role", "user"),
                        "content": str(msg.get("content", "")),
                    }
                    for msg in messages
                ],
                stream=False,
                options=OllamaOptions(temperature=temperature or 0.7),
            )

            logger.info(f"[{self.provider_name}] 成功生成响应")
            return self._convert_ollama_to_openai_format(response)
        except Exception as e:
            error_msg = f"{self.provider_name} API error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg)
