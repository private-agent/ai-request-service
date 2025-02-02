from fastapi import APIRouter, HTTPException
from ...models.schemas import AIRequest, AIResponse
from ...core.ai_factory import AIFactory
from ...config.settings import get_settings

router = APIRouter()

@router.post("/generate", response_model=AIResponse)
async def generate_response(request: AIRequest):
    settings = get_settings()

    # 使用用户指定的提供商列表或默认优先级
    providers = request.providers or settings.AI_PRIORITY

    last_error = None
    # 按优先级尝试不同的AI提供商
    for provider_name in providers:
        try:
            provider = AIFactory.create_provider(provider_name)
            response = await provider.generate_response(request.prompt)
            print(response)
            return AIResponse(**response)
        except Exception as e:
            last_error = str(e)
            continue

    # 如果所有提供商都失败，则抛出异常
    raise HTTPException(
        status_code=500,
        detail=f"All AI providers failed. Last error: {last_error}"
    )