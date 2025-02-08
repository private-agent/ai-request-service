import pytest
from tests.conftest import format_response

def test_anthropic_generate_success(mock_settings, client):
    response = client.post(
        "/api/v1/chat/completions",
        json={
            "messages": [{"role": "user", "content": "你是谁？请介绍一下你自己"}],
            "providers": ["anthropic-test"]
        }
    )

    print("\n响应内容:")
    print(format_response(response))

    assert response.status_code == 200
    assert response.json()["provider"] == "anthropic-test"
    assert "choices" in response.json()