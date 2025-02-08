from pydantic import Field, PrivateAttr
from pydantic_settings import BaseSettings
from typing import Dict, List, Optional
import yaml
from functools import lru_cache
import os

class ProviderConfig:
    """单个提供商的配置"""
    def __init__(self, **kwargs):
        self.type: str = kwargs['type']
        self.api_key: Optional[str] = kwargs.get('api_key')
        self.base_url: Optional[str] = kwargs.get('base_url')
        self.model: str = kwargs['model']
        self.max_tokens: int = kwargs.get('max_tokens', 2000)

class Settings(BaseSettings):
    """
    应用配置类，继承自 Pydantic 的 BaseSettings。
    BaseSettings 的特殊之处在于它会自动从环境变量中读取值：
    1. 如果环境变量中存在同名变量（大写），则使用环境变量的值
    2. 如果环境变量不存在，则使用这里定义的默认值
    3. 环境变量查找规则：
       - 先查找完全匹配的名称（如 OPENAI_API_KEY）
       - 然后查找小写名称（如 openai_api_key）
    """
    PROJECT_NAME: str = "AI Request Service"

    # 配置文件路径
    CONFIG_PATH: str = Field("config.yaml", alias="CONFIG_PATH")

    # 使用 PrivateAttr 声明私有属性
    _config: Dict = PrivateAttr(default_factory=dict)
    _providers: Dict[str, ProviderConfig] = PrivateAttr(default_factory=dict)
    _priority: List[str] = PrivateAttr(default_factory=list)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_config()

    def _load_config(self):
        """加载YAML配置文件"""
        # 优先使用环境变量中的配置路径
        config_path = os.getenv("CONFIG_PATH", self.CONFIG_PATH)

        # 如果是测试环境，使用测试配置文件
        if os.getenv("TESTING") == "true":
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "tests",
                "test_config.yaml"
            )

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)

        # 加载提供商配置
        providers_config = self._config.get('providers', {})
        for name, config in providers_config.items():
            self._providers[name] = ProviderConfig(**config)

        # 加载并验证优先级配置
        self._priority = self._config.get('priority', [])

        # 检查优先级列表中的所有提供商是否都已配置
        invalid_providers = [p for p in self._priority if p not in self._providers]
        if invalid_providers:
            raise ValueError(f"优先级列表中存在未配置的提供商: {', '.join(invalid_providers)}")

    @property
    def AI_PRIORITY(self) -> List[str]:
        """获取AI提供商优先级列表"""
        return self._priority

    @property
    def AI_MODELS(self) -> Dict[str, Dict]:
        """构建AI模型配置字典"""
        return {
            name: {
                "model": provider.model,
                "max_tokens": provider.max_tokens,
                "provider_type": provider.type
            }
            for name, provider in self._providers.items()
        }

    def get_provider_config(self, provider_name: str) -> Optional[ProviderConfig]:
        """获取指定提供商的配置"""
        return self._providers.get(provider_name)

    class Config:
        """
        Pydantic 配置类
        - env_file: 指定环境变量文件路径
        - case_sensitive: True 表示区分大小写
        """
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    """
    获取设置实例的函数
    使用 lru_cache 装饰器来缓存设置实例，避免重复读取环境变量
    """
    return Settings()