# AI Request Service

一个灵活的 AI 请求代理服务，支持多个 AI 提供商的故障转移和优先级配置。

## 功能特点

- 支持多种类型的 AI 提供商（OpenAI 兼容接口、Anthropic、Ollama 等）
- 通过 YAML 配置文件灵活配置提供商
- 可配置的提供商优先级顺序
- 自动故障转移机制
- Docker 部署支持

## 支持的提供商类型

- OpenAI 兼容接口 (OpenAI、Azure OpenAI、DeepSeek 等)
- Anthropic Claude
- Ollama（本地模型）

## 快速开始

### 1. 配置准备

复制配置文件示例并修改：

```bash
cp config.example.yaml config.yaml
# 编辑 config.yaml 文件，配置您的提供商信息
```

配置文件示例：
```yaml
# AI提供商配置
providers:
  gpt4:  # 提供商标识符，用户自定义
    type: openai  # 提供商类型
    api_key: your_gpt4_api_key
    base_url: https://api.openai.com/v1
    model: gpt-4-turbo-preview
    max_tokens: 2000

  local-deepseek:  # 本地 Ollama 模型
    type: ollama
    base_url: http://localhost:11434
    model: deepseek-r1:14b
    max_tokens: 2000

  deepseek-api:  # DeepSeek API
    type: openai  # 使用 OpenAI 兼容接口
    api_key: your_deepseek_api_key
    base_url: https://api.deepseek.com/chat/completions
    model: deepseek-chat
    max_tokens: 2000

# 默认的提供商优先级顺序
priority:
  - local-deepseek
  - deepseek-api
  - gpt4
```

### 2. Docker 部署

```bash
# 构建并启动服务
docker compose up -d

# 查看日志
docker compose logs -f

# 或者
docker-up.sh -d
```

### 3. 本地开发

```bash
# 创建虚拟环境，基于miniconda
conda create -n ars python=3.10
conda activate ars

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload
```

## API 使用

### 生成 AI 响应

```bash
curl -X POST "http://localhost:8000/api/chat/completions" \
-H "Content-Type: application/json" \
-d '{
    "messages": [{"role": "user", "content": "你好，请介绍一下你自己"}],
    "providers": ["local-deepseek", "deepseek-api"]
}'
```

参数说明：
- `messages`: 要发送给 AI 的消息列表，包含角色和内容
- `providers`: （可选）指定使用的 AI 提供商及其优先级顺序，不指定则使用配置文件中的默认顺序

响应示例：
```json
{
    "provider": "local-deepseek",
    "model": "deepseek-r1:14b",
    "content": "AI的回复内容..."
}
```

## 配置说明

### 提供商类型

1. OpenAI 兼容接口 (`type: openai`)
   - 适用于 OpenAI、Azure OpenAI、DeepSeek 等使用 OpenAI 兼容接口的服务
   - 必需参数：`api_key`, `base_url`, `model`

2. Anthropic (`type: anthropic`)
   - 适用于 Anthropic Claude 服务
   - 必需参数：`api_key`, `model`

3. Ollama (`type: ollama`)
   - 适用于本地部署的 Ollama 服务
   - 必需参数：`base_url`, `model`

### 配置参数

每个提供商可配置的参数：
- `type`: 提供商类型（必需）
- `api_key`: API密钥（对于需要认证的服务）
- `base_url`: API基础URL
- `model`: 使用的模型名称（必需）
- `max_tokens`: 最大生成token数（可选，默认2000）

## 运行测试

```bash
# 准备测试配置
cp tests/test_config.example.yaml tests/test_config.yaml
# 编辑 test_config.yaml 配置测试环境

# 运行所有测试
pytest tests/ -v -s

# 运行特定提供商的测试
pytest tests/test_ollama_provider.py -v -s
```

## 开发说明

### 项目结构

```
ai-request-service/
├── app/
│   ├── api/
│   │   └── endpoints/
│   │       └── ai_request.py
│   ├── core/
│   │   ├── ai_factory.py
│   │   └── ai_provider.py
│   ├── config/
│   │   └── settings.py
│   ├── models/
│   │   └── schemas.py
│   └── main.py
├── tests/
├── config.example.yaml
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### 添加新的提供商类型

1. 在 `ai_provider.py` 中创建新的提供商类
2. 在 `ai_factory.py` 中添加创建逻辑
3. 在配置文件中使用新的提供商类型

## 许可证

MIT License

## 贡献指南

欢迎提交 Issue 和 Pull Request！
