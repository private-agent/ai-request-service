from typing import Dict, Any
from .ai_provider import (
    AIProvider,
    OpenAIFormatProvider,
    AnthropicProvider,
    OllamaProvider
)
from ..config.settings import get_settings
from ..utils.logger import logger

class AIFactory:
    @staticmethod
    def create_provider(provider_name: str) -> AIProvider:
        settings = get_settings()
        logger.info(f"正在创建AI提供商: {provider_name}")

        provider_config = settings.get_provider_config(provider_name)

        if not provider_config:
            error_msg = f"未找到提供商配置: {provider_name}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        provider_type = provider_config.type
        logger.debug(f"提供商 {provider_name} 的类型为: {provider_type}")

        try:
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
                    max_tokens=provider_config.max_tokens,
                    provider_name=provider_name
                )

            else:
                error_msg = f"不支持的提供商类型: {provider_type}"
                logger.error(error_msg)
                raise ValueError(error_msg)

        except Exception as e:
            logger.error(f"创建提供商 {provider_name} 时发生错误: {str(e)}", exc_info=True)
            raise