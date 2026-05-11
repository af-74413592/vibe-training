"A Vibe Training - Automated Model Training Repository"
Based on https://github.com/NanmiCoder/cc-haha

# How To Use
1. ```bun install```

2. ```cp .env.example .env```

3. Edit .env (the example below uses Deepseek as the API provider — you can replace it with any compatible service):

```
# API authentication (choose one)
ANTHROPIC_API_KEY=sk-xxx          # Standard API key via x-api-key header
ANTHROPIC_AUTH_TOKEN=sk-xxx       # Bearer token via Authorization header

# API endpoint (optional, defaults to Anthropic)
ANTHROPIC_BASE_URL=	https://api.deepseek.com/anthropic

# Model configuration
ANTHROPIC_MODEL=deepseek-v4-pro
ANTHROPIC_DEFAULT_SONNET_MODEL=deepseek-v4-pro
ANTHROPIC_DEFAULT_HAIKU_MODEL=deepseek-v4-pro
ANTHROPIC_DEFAULT_OPUS_MODEL=deepseek-v4-pro

# Timeout in milliseconds
API_TIMEOUT_MS=3000000

# Disable telemetry and non-essential network traffic
DISABLE_TELEMETRY=1
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
```

4. Add the project's bin directory to your system environment variables.

5. Navigate to a new empty workspace directory

6. ```claude-haha```
