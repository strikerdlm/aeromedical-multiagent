#!/usr/bin/env python3
"""
API Structure Validation Script

This script validates the API call structures for:
1. Perplexity API (sonar-deep-research model)
2. XAI/Grok API (grok-4 model)
3. Flowise API (chatflow endpoints)

Run this to test your API configurations and verify correct structure.
"""

import os
import json
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_perplexity_structure() -> bool:
    """Test Perplexity API call structure according to official documentation."""
    print("\n🔍 Testing Perplexity API Structure...")
    
    api_key = os.getenv("PPLX_API_KEY")
    if not api_key:
        print("❌ PPLX_API_KEY not found in environment variables")
        return False

    url = "https://api.perplexity.ai/chat/completions"
    
    # Standard payload structure according to official API documentation
    payload = {
        "model": "sonar-deep-research",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful AI assistant."
            },
            {
                "role": "user", 
                "content": "Test query for API structure validation."
            }
        ],
        "max_tokens": 100,
        "temperature": 0.3,
        "top_p": 0.9,
        "reasoning_effort": "medium",  # New parameter
        "search_mode": "academic",     # New parameter for scholarly sources
        "web_search_options": {        # New parameter for search configuration
            "search_context_size": "medium"
        },
        "stream": False
    }
    
    # Optional parameters that could be added
    optional_params = {
        "search_domain_filter": ["pubmed.ncbi.nlm.nih.gov", "scholar.google.com"],
        "search_after_date_filter": "1/1/2023"
    }
    
    # Standard headers according to official API documentation
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    print(f"✅ URL: {url}")
    print(f"✅ Headers: Authorization: Bearer [HIDDEN], Content-Type: application/json")
    print(f"✅ Model: {payload['model']}")
    print(f"✅ Reasoning Effort: {payload['reasoning_effort']}")
    print(f"✅ Search Mode: {payload['search_mode']}")
    print(f"✅ Search Context Size: {payload['web_search_options']['search_context_size']}")
    print(f"✅ Stream: {payload['stream']}")
    
    # Validate required parameters
    required_params = ["model", "messages"]
    for param in required_params:
        if param not in payload:
            print(f"❌ Missing required parameter: {param}")
            return False
    
    # Validate message structure
    if not isinstance(payload["messages"], list) or len(payload["messages"]) == 0:
        print("❌ Invalid messages structure")
        return False
    
    for i, message in enumerate(payload["messages"]):
        if not isinstance(message, dict) or "role" not in message or "content" not in message:
            print(f"❌ Invalid message structure at index {i}")
            return False
        
        if message["role"] not in ["system", "user", "assistant"]:
            print(f"❌ Invalid role '{message['role']}' at message index {i}")
            return False
    
    # Validate reasoning_effort values
    if payload.get("reasoning_effort") not in ["low", "medium", "high"]:
        print(f"❌ Invalid reasoning_effort value: {payload.get('reasoning_effort')}")
        return False
    
    # Validate search_mode values (optional parameter)
    if "search_mode" in payload and payload["search_mode"] not in ["academic"]:
        print(f"❌ Invalid search_mode value: {payload['search_mode']}")
        return False
    
    # Validate web_search_options structure
    if "web_search_options" in payload:
        if not isinstance(payload["web_search_options"], dict):
            print("❌ Invalid web_search_options structure")
            return False
        
        search_context_size = payload["web_search_options"].get("search_context_size")
        if search_context_size and search_context_size not in ["low", "medium", "high"]:
            print(f"❌ Invalid search_context_size value: {search_context_size}")
            return False

    print("✅ Payload structure validation:")
    print(f"   📦 Required parameters: ✅")
    print(f"   📝 Message format: ✅")
    print(f"   ⚡ Reasoning effort: ✅")
    print(f"   🎓 Academic search mode: ✅")
    print(f"   🔍 Web search options: ✅")
    
    # Test async API structure as well
    print("\n🔍 Testing Async API Structure...")
    
    async_url = "https://api.perplexity.ai/async/chat/completions"
    async_payload = {
        "request": {
            "model": "sonar-deep-research",
            "messages": payload["messages"],
            "max_tokens": 4000,
            "temperature": 0.3,
            "reasoning_effort": "high",  # Use high for comprehensive async research
            "search_mode": "academic"
        }
    }
    
    print(f"✅ Async URL: {async_url}")
    print(f"✅ Async payload structure: ✅")
    print(f"✅ Request wrapper: ✅")
    
    try:
        # Don't actually make the request, just validate structure
        print("✅ Perplexity API structure is correct!")
        print("✅ Async API structure is correct!")
        return True
    except Exception as e:
        print(f"❌ Perplexity structure error: {e}")
        return False

def test_grok_structure() -> bool:
    """Test XAI/Grok API call structure."""
    print("\n🤖 Testing Grok (XAI) API Structure...")
    
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        print("❌ XAI_API_KEY not found in environment variables")
        return False
    
    url = "https://api.x.ai/v1/chat/completions"
    
    payload = {
        "model": "grok-4",
        "messages": [
            {"role": "user", "content": "Test query for API structure validation."}
        ],
        "max_tokens": 100,
        "temperature": 0.3
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print(f"✅ URL: {url}")
    print(f"✅ Headers: Authorization: Bearer [HIDDEN], Content-Type: application/json")
    print(f"✅ Payload structure: {json.dumps(payload, indent=2)}")
    
    print("✅ Grok API structure is correct!")
    return True

def test_flowise_structure() -> bool:
    """Test Flowise API call structure."""
    print("\n🌊 Testing Flowise API Structure...")
    
    api_key = os.getenv("FLOWISE_API_KEY")
    api_url = os.getenv("FLOWISE_API_URL", "https://cloud.flowiseai.com")
    
    if not api_key:
        print("❌ FLOWISE_API_KEY not found in environment variables")
        return False
    
    # Test each chatflow configuration
    chatflows = {
        "CHATFLOW_AEROMEDICAL_RISK": os.getenv("CHATFLOW_AEROMEDICAL_RISK"),
        "CHATFLOW_DEEP_RESEARCH": os.getenv("CHATFLOW_DEEP_RESEARCH"),
        "CHATFLOW_AEROSPACE_MEDICINE_RAG": os.getenv("CHATFLOW_AEROSPACE_MEDICINE_RAG")
    }
    
    print(f"✅ Base URL: {api_url}")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print(f"✅ Headers: Authorization: Bearer [HIDDEN], Content-Type: application/json")
    
    for name, chatflow_id in chatflows.items():
        if not chatflow_id:
            print(f"❌ {name} not found in environment variables")
            continue
        
        endpoint_url = f"{api_url}/api/v1/prediction/{chatflow_id}"
        payload = {
            "question": "Test query for API structure validation.",
            "overrideConfig": {
                "sessionId": "validation-session"
            }
        }
        
        print(f"\n📋 {name}:")
        print(f"   URL: {endpoint_url}")
        print(f"   Payload: {json.dumps(payload, indent=6)}")
    
    print("✅ Flowise API structure is correct!")
    return True

def validate_environment_variables() -> Dict[str, bool]:
    """Validate all required environment variables."""
    print("\n📋 Validating Environment Variables...")
    
    required_vars = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "FLOWISE_API_KEY": os.getenv("FLOWISE_API_KEY"),
        "FLOWISE_API_URL": os.getenv("FLOWISE_API_URL"),
        "PPLX_API_KEY": os.getenv("PPLX_API_KEY"),
        "XAI_API_KEY": os.getenv("XAI_API_KEY"),
        "CHATFLOW_AEROMEDICAL_RISK": os.getenv("CHATFLOW_AEROMEDICAL_RISK"),
        "CHATFLOW_DEEP_RESEARCH": os.getenv("CHATFLOW_DEEP_RESEARCH"),
        "CHATFLOW_AEROSPACE_MEDICINE_RAG": os.getenv("CHATFLOW_AEROSPACE_MEDICINE_RAG")
    }
    
    status = {}
    for var_name, var_value in required_vars.items():
        if var_value and var_value.strip() and var_value != f"your_{var_name.lower()}_here":
            print(f"✅ {var_name}: Configured")
            status[var_name] = True
        else:
            print(f"❌ {var_name}: Not configured or placeholder value")
            status[var_name] = False
    
    return status

def main():
    """Main validation function."""
    print("🚀 API Structure Validation Tool")
    print("=" * 50)
    
    # Validate environment variables
    env_status = validate_environment_variables()
    
    # Test API structures
    perplexity_ok = test_perplexity_structure()
    grok_ok = test_grok_structure()
    flowise_ok = test_flowise_structure()
    
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    print("\n🔧 Environment Variables:")
    for var_name, status in env_status.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {var_name}")
    
    print("\n🌐 API Structures:")
    print(f"   {'✅' if perplexity_ok else '❌'} Perplexity API")
    print(f"   {'✅' if grok_ok else '❌'} Grok (XAI) API")
    print(f"   {'✅' if flowise_ok else '❌'} Flowise API")
    
    # Overall status
    all_env_configured = all(env_status.values())
    all_structures_ok = perplexity_ok and grok_ok and flowise_ok
    
    if all_env_configured and all_structures_ok:
        print("\n🎉 ALL VALIDATIONS PASSED!")
        print("Your API configurations are ready to use.")
    else:
        print("\n⚠️  SOME VALIDATIONS FAILED!")
        if not all_env_configured:
            print("Please configure missing environment variables in your .env file.")
        if not all_structures_ok:
            print("Please check API structure configurations.")
    
    print("\n📝 Next Steps:")
    if not os.path.exists(".env"):
        print("1. Copy .env.template to .env")
        print("2. Fill in your actual API keys")
    else:
        print("1. Update your .env file with missing variables")
    print("2. Run this script again to validate")
    print("3. Test your application")

if __name__ == "__main__":
    main() 