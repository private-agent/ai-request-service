from typing import Dict, Any
from .ai_provider import (
    AIProvider,
    OpenAIFormatProvider,
    AnthropicProvider,
    OllamaProvider
)
from ..config.settings import get_settings

class AIFactory:
    @staticmethod
    def create_provider(provider_name: str) -> AIProvider:
        settings = get_settings()
        provider_config = settings.get_provider_config(provider_name)

        if not provider_config:
            raise ValueError(f"未找到提供商配置: {provider_name}")

        provider_type = provider_config.type

        if provider_type == "openai":
            return OpenAIFormatProvider(
                api_key=provider_config.api_key,
                base_url=provider_config.base_url,
                model=provider_config.model,
                max_tokens=provider_config.max_tokens,
                provider_name=provider_name
            )

        elif provider_type == "anthropic":
            return AnthropicProvider(
                api_key=provider_config.api_key,
                model=provider_config.model,
                max_tokens=provider_config.max_tokens
            )

        elif provider_type == "ollama":
            return OllamaProvider(
                base_url=provider_config.base_url,
                model=provider_config.model,
                max_tokens=provider_config.max_tokens
            )

        else:
            raise ValueError(f"不支持的提供商类型: {provider_type}")