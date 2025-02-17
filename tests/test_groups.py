def test_group_resolution(client):
    response = client.post(
        "/api/v1/chat/completions",
        json={
            "messages": [{"role": "user", "content": "test"}],
            "providers": ["primary"]
        }
    )
    assert response.status_code == 200

def test_mixed_providers(client):
    response = client.post(
        "/api/v1/chat/completions",
        json={
            "messages": [{"role": "user", "content": "test"}],
            "providers": ["primary", "openai-test"]
        }
    )
    assert response.status_code == 200