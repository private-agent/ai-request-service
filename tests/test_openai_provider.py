import pytest
from tests.conftest import format_response

def test_openai_generate_success(mock_settings, client):
    response = client.post(
        "/api/v1/generate",
        json={
            "prompt": "你是谁？请介绍一下你自己",
            "providers": ["deepseek-test"]  # 使用 DeepSeek 测试
        }
    )

    print("\n响应内容:")
    print(format_response(response))

    assert response.status_code == 200
    assert response.json()["provider"] == "deepseek-test"
    assert "content" in response.json()

def test_openai_error_fallback(mock_settings, client):
    response = client.post(
        "/api/v1/generate",
        json={
            "prompt": "你是谁？请介绍一下你自己",
            "providers": ["openai-test", "deepseek-test"]  # openai-test 会失败，fallback 到 deepseek
        }
    )

    print("\n故障转移响应:")
    print(format_response(response))

    assert response.status_code == 200
    assert response.json()["provider"] == "deepseek-test"