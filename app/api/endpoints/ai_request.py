import json
from fastapi import APIRouter, HTTPException
from ...models.schemas import AIRequest, AIResponse, ChatMessage
from ...core.ai_factory import AIFactory
from ...config.settings import get_settings
from ...utils.logger import logger

router = APIRouter()


@router.post("/chat/completions", response_model=AIResponse)
async def generate_response(request: AIRequest):
    settings = get_settings()
    # 解析用户请求中的分组
    raw_model = request.model
    providers = settings.resolve_providers(raw_model)

    logger.info(f"开始处理AI请求，解析后的提供商顺序: {providers}")
    logger.info(
        "对话内容（已过滤system角色）: \n"
        + "\n".join(
            [
                f"  角色: {message.get('role')}, 内容: {message.get('content')}"
                for message in request.messages
                if message.get("role") != "system"
            ]
        )
    )

    last_error = None
    for provider_name in providers:
        try:
            logger.info(f"尝试使用AI提供商: {provider_name}")
            provider = AIFactory.create_provider(provider_name)
            response = await provider.generate_response(
                messages=request.messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
            )
            logger.info(f"AI提供商 {provider_name} 成功生成响应")
            logger.debug(f"AI响应: \n{json.dumps(response.model_dump(), ensure_ascii=False, indent=2)}")
            return response
        except Exception as e:
            last_error = str(e)
            logger.error(f"AI提供商 {provider_name} 失败: {last_error}", exc_info=True)
            continue

    error_msg = f"所有AI提供商都失败了。最后的错误: {last_error}"
    logger.error(error_msg)
    raise HTTPException(status_code=500, detail=error_msg)
