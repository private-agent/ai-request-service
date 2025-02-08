from contextlib import asynccontextmanager
from fastapi import FastAPI
from .api.endpoints import ai_request
from .config.settings import get_settings
from .utils.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    # 启动时执行
    get_settings()
    logger.info("应用启动")
    yield
    # 关闭时执行
    # 清理代码（如果需要）可以放在这里
    logger.info("应用关闭")

app = FastAPI(
    title="AI Request Service",
    description="A proxy service for multiple AI providers",
    lifespan=lifespan
)

app.include_router(ai_request.router, prefix="/api/v1")