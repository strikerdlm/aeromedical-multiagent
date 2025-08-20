# API Configuration Guide

This guide shows the correct API call structures and environment variable setup for all integrated APIs.

## 🔧 Environment Variables Setup

Create a `.env` file in your project root with these variables:

```bash
# REQUIRED: OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# REQUIRED: Flowise API Configuration
FLOWISE_API_URL=https://cloud.flowiseai.com
FLOWISE_API_KEY=your_flowise_api_key_here

# REQUIRED: Perplexity API Configuration (for PRISMA deep research)
PPLX_API_KEY=your_perplexity_api_key_here

# REQUIRED: XAI (Grok) API Configuration (for Grok 4 model)
XAI_API_KEY=your_xai_grok_api_key_here

# REQUIRED: Flowise Chatflow IDs
CHATFLOW_AEROMEDICAL_RISK=your_aeromedical_risk_chatflow_id_here
CHATFLOW_DEEP_RESEARCH=your_deep_research_chatflow_id_here
CHATFLOW_AEROSPACE_MEDICINE_RAG=your_aerospace_medicine_rag_chatflow_id_here

# Application Settings
MAX_RETRIES=3
RETRY_DELAY=1.0
TIMEOUT=120
LOG_LEVEL=INFO
ENABLE_PERPLEXITY_RESEARCH=true
PERPLEXITY_TIMEOUT=15
```

## 🌐 API Call Structures

### 1. Perplexity API (✅ Your structure is correct!)

```python
import requests

url = "https://api.perplexity.ai/chat/completions"

payload = {
    "model": "sonar-deep-research",
    "messages": [
        {"role": "user", "content": "Your query here"}
    ],
    "max_tokens": 500,
    "temperature": 0.3
}

headers = {
    "Authorization": f"Bearer {os.getenv('PPLX_API_KEY')}",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

**Key Points:**
- ✅ URL: `https://api.perplexity.ai/chat/completions`
- ✅ Model: `sonar-deep-research`
- ✅ Headers: `Authorization: Bearer <token>`, `Content-Type: application/json`
- ✅ Environment Variable: `PPLX_API_KEY`

### 2. Grok (XAI) API

```python
import requests
import os

url = "https://api.x.ai/v1/chat/completions"

payload = {
    "model": "grok-beta",
    "messages": [
        {"role": "user", "content": "Your query here"}
    ],
    "max_tokens": 500,
    "temperature": 0.3
}

headers = {
    "Authorization": f"Bearer {os.getenv('XAI_API_KEY')}",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

**Key Points:**
- ✅ URL: `https://api.x.ai/v1/chat/completions`
- ✅ Model: `grok-beta`
- ✅ Headers: `Authorization: Bearer <token>`, `Content-Type: application/json`
- ✅ Environment Variable: `XAI_API_KEY`

### 3. Flowise API

```python
import requests
import os

# Example for Deep Research Chatflow
chatflow_id = os.getenv("CHATFLOW_DEEP_RESEARCH")
url = f"https://cloud.flowiseai.com/api/v1/prediction/{chatflow_id}"

payload = {
    "question": "Your query here",
    "overrideConfig": {
        "sessionId": "your-session-id"
    }
}

headers = {
    "Authorization": f"Bearer {os.getenv('FLOWISE_API_KEY')}",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

**Key Points:**
- ✅ Base URL: `https://cloud.flowiseai.com`
- ✅ Endpoint Pattern: `/api/v1/prediction/{chatflow_id}`
- ✅ Headers: `Authorization: Bearer <token>`, `Content-Type: application/json`
- ✅ Environment Variables: `FLOWISE_API_KEY`, `FLOWISE_API_URL`

## 🎯 Chatflow Configuration

Your application uses three specialized chatflows:

### 1. Aeromedical Risk Assessment
- **Environment Variable**: `CHATFLOW_AEROMEDICAL_RISK`
- **Purpose**: Aviation medicine risk assessment
- **Speed**: ⚡ Fast response (as you mentioned)

### 2. Deep Research
- **Environment Variable**: `CHATFLOW_DEEP_RESEARCH`
- **Purpose**: Comprehensive research analysis
- **Speed**: ⚡ Fast response

### 3. Aerospace Medicine RAG
- **Environment Variable**: `CHATFLOW_AEROSPACE_MEDICINE_RAG`
- **Purpose**: Scientific articles and textbooks in aerospace medicine
- **Speed**: ⚡⚡ Very fast response (as you mentioned)

## 🔍 How Your Application Uses These APIs

### Current Integration Points

1. **Perplexity Client** (`src/perplexity_client.py`):
   - Used for PRISMA systematic reviews
   - Literature searches and research analysis
   - Configured in `PRISMAConfig.PERPLEXITY_BASE_URL`

2. **Grok Client** (`src/grok_client.py`):
   - Used for critical analysis and reasoning
   - Methodology reviews and bias detection
   - Configured in `PRISMAConfig.GROK_BASE_URL`

3. **Flowise Client** (`src/flowise_client.py`):
   - Used for medical and research-focused queries
   - Three specialized chatflows for different purposes
   - Configured in `FlowiseConfig`

## 🚀 Quick Setup Steps

1. **Create your .env file**:
   ```bash
   cp .env.template .env  # If template exists, or create manually
   ```

2. **Fill in your API keys**:
   - Get your Perplexity API key from https://www.perplexity.ai/
   - Get your XAI API key from https://x.ai/
   - Get your Flowise API key and chatflow IDs from your Flowise instance

3. **Validate your configuration**:
   ```bash
   python validate_api_structure.py
   ```

4. **Test your application**:
   ```bash
   python run.py
   ```

## ⚠️ Common Issues and Solutions

### Issue 1: "API key not configured"
**Solution**: Make sure your .env file exists and contains all required variables

### Issue 2: "Chatflow not found"
**Solution**: Verify your chatflow IDs are correct in Flowise dashboard

### Issue 3: "Authentication failed"
**Solution**: Check that your API keys are valid and not expired

### Issue 4: "Request timeout"
**Solution**: Increase TIMEOUT value in .env or check your network connection

## 📊 Validation

Run the validation script to check everything is configured correctly:

```bash
python validate_api_structure.py
```

This will verify:
- ✅ All environment variables are set
- ✅ API structures are correct
- ✅ Chatflow configurations are valid 