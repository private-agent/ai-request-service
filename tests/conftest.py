import pytest
import os
import sys
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, mock_open
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 设置测试环境标志
os.environ["TESTING"] = "true"

# 延迟导入 app，确保环境变量已设置
from app.main import app

@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)

@pytest.fixture
def test_config_path():
    return os.path.join(os.path.dirname(__file__), 'test_config.yaml')

@pytest.fixture
def mock_settings(test_config_path):
    from app.config.settings import get_settings
    settings = get_settings()
    yield settings

def format_response(response):
    """格式化响应内容"""
    try:
        return json.dumps(response.json(), ensure_ascii=False, indent=2)
    except:
        return response.text