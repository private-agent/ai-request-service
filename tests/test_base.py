import pytest
from unittest.mock import patch, mock_open

def test_empty_prompt(mock_settings, client):
    response = client.post(
        "/api/v1/chat/completions",
        json={"messages": [{"role": "user", "content": ""}]}
    )
    assert response.status_code == 422

def test_invalid_provider(mock_settings, client):
    response = client.post(
        "/api/v1/chat/completions",
        json={
            "messages": [{"role": "user", "content": "你是谁？请介绍一下你自己"}],
            "providers": ["invalid-provider"]
        }
    )
    assert response.status_code == 500

def test_invalid_config():
    invalid_config = """
    providers:
      test:
        type: openai
        model: gpt-4
    priority:
      - test
      - nonexistent
    """
    with pytest.raises(ValueError, match="优先级列表中存在未配置的提供商"):
        with patch('builtins.open', mock_open(read_data=invalid_config)):
            from app.config.settings import Settings
            Settings()