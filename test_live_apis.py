#!/usr/bin/env python3
"""
Live API Test Script

Tests actual API calls to:
1. Perplexity API (sonar-deep-research)
2. XAI/Grok API (grok-beta)
3. Flowise API (all three chatflows)

This makes real API calls with minimal tokens to test connectivity.
"""

import os
import sys
import json
import requests
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_perplexity_api() -> bool:
    """Test actual Perplexity API call using new API structure."""
    print("\n🔍 Testing Perplexity API (Live Call)...")
    
    try:
        url = "https://api.perplexity.ai/chat/completions"
        
        # Updated payload structure according to new API documentation
        payload = {
            "model": "sonar-deep-research",
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a helpful AI assistant. Provide concise, factual information."
                },
                {
                    "role": "user", 
                    "content": "What is artificial intelligence? Give a brief 2-sentence answer."
                }
            ],
            "max_tokens": 100,  # Minimal tokens to save cost
            "temperature": 0.3,
            "top_p": 0.9,
            "reasoning_effort": "low",  # Use low effort for quick test
            "stream": False
        }
        
        # Updated headers according to official API documentation
        headers = {
            "Authorization": f"Bearer {os.getenv('PPLX_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        print(f"🔗 URL: {url}")
        print(f"📦 Model: {payload['model']}")
        print(f"⚡ Reasoning Effort: {payload['reasoning_effort']}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            citations = result.get('citations', [])
            search_results = result.get('search_results', [])
            
            print(f"✅ SUCCESS: Response received")
            print(f"📝 Sample content: {content[:100]}...")
            print(f"📚 Citations found: {len(citations)}")
            print(f"🔍 Search results: {len(search_results)}")
            
            # Test search_results field (new in API)
            if search_results:
                print(f"🌐 First source URL: {search_results[0].get('url', 'N/A')}")
            
            return True
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            try:
                error_detail = response.json().get('detail', response.text)
                print(f"📝 Error: {error_detail}")
            except (ValueError, KeyError, TypeError):
                print(f"📝 Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def test_grok_api() -> bool:
    """Test actual Grok API call."""
    print("\n🤖 Testing Grok API (Live Call)...")
    
    try:
        url = "https://api.x.ai/v1/chat/completions"
        
        # Try grok-4 first, then fallback to grok-beta
        for model in ["grok-4", "grok-beta"]:
            print(f"🔄 Trying model: {model}")
            
            payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": "What is reasoning? Give a brief 2-sentence answer."}
                ],
                "max_tokens": 50,  # Minimal tokens to save cost
                "temperature": 0.3
            }
            
            headers = {
                "Authorization": f"Bearer {os.getenv('XAI_API_KEY')}",
                "Content-Type": "application/json"
            }
            
            print(f"🔗 URL: {url}")
            print(f"📦 Model: {payload['model']}")
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                print(f"✅ SUCCESS with {model}: Response received")
                print(f"📝 Sample content: {content[:100]}...")
                return True
            else:
                print(f"⚠️ Model {model} failed: Status {response.status_code}")
                if model == "grok-4":
                    print(f"📝 Error: {response.text}")
                    print("🔄 Falling back to grok-beta...")
                    continue
                else:
                    print(f"❌ FAILED: Status {response.status_code}")
                    print(f"📝 Error: {response.text}")
                    return False
        
        return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def test_flowise_chatflow(chatflow_name: str, chatflow_id: str) -> bool:
    """Test a specific Flowise chatflow."""
    try:
        base_url = os.getenv("FLOWISE_API_URL", "https://cloud.flowiseai.com")
        url = f"{base_url}/api/v1/prediction/{chatflow_id}"
        
        payload = {
            "question": "What is health? Brief answer please.",
            "overrideConfig": {
                "sessionId": f"test-{chatflow_name}-session"
            }
        }
        
        headers = {
            "Authorization": f"Bearer {os.getenv('FLOWISE_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        print(f"📋 Testing {chatflow_name}...")
        print(f"🔗 URL: {url}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            # Flowise can return different response formats
            if isinstance(result, dict):
                content = result.get('text', result.get('answer', str(result)))
            else:
                content = str(result)
            
            print(f"✅ SUCCESS: {chatflow_name}")
            print(f"📝 Sample content: {str(content)[:100]}...")
            return True
        else:
            print(f"❌ FAILED: {chatflow_name} - Status {response.status_code}")
            print(f"📝 Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {chatflow_name} - {e}")
        return False

def test_flowise_api() -> Dict[str, bool]:
    """Test all Flowise chatflows."""
    print("\n🌊 Testing Flowise API (Live Calls)...")
    
    chatflows = {
        "Aeromedical Risk": os.getenv("CHATFLOW_AEROMEDICAL_RISK"),
        "Deep Research": os.getenv("CHATFLOW_DEEP_RESEARCH"), 
        "Aerospace Medicine RAG": os.getenv("CHATFLOW_AEROSPACE_MEDICINE_RAG")
    }
    
    results = {}
    for name, chatflow_id in chatflows.items():
        if chatflow_id:
            results[name] = test_flowise_chatflow(name, chatflow_id)
        else:
            print(f"❌ SKIPPED: {name} - No chatflow ID configured")
            results[name] = False
    
    return results

def main():
    """Run all live API tests."""
    print("🚀 Live API Testing Tool")
    print("=" * 50)
    print("⚠️  This script makes REAL API calls and may use your API quotas.")
    print("⚠️  It uses minimal tokens to reduce costs.")
    print("=" * 50)
    
    # Check if user wants to proceed
    response = input("\n🤔 Do you want to proceed with live API testing? (y/N): ").strip().lower()
    if response != 'y':
        print("❌ Testing cancelled by user.")
        return
    
    print("\n🔄 Starting live API tests...")
    
    # Test APIs
    perplexity_ok = test_perplexity_api()
    grok_ok = test_grok_api()
    flowise_results = test_flowise_api()
    
    print("\n" + "=" * 50)
    print("📊 LIVE API TEST SUMMARY")
    print("=" * 50)
    
    print(f"\n🔍 Perplexity API: {'✅ WORKING' if perplexity_ok else '❌ FAILED'}")
    print(f"🤖 Grok API: {'✅ WORKING' if grok_ok else '❌ FAILED'}")
    
    print("\n🌊 Flowise Chatflows:")
    for name, status in flowise_results.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {name}")
    
    # Overall status
    all_working = perplexity_ok and grok_ok and all(flowise_results.values())
    
    if all_working:
        print("\n🎉 ALL APIs ARE WORKING!")
        print("Your configuration is perfect and ready for production use.")
    else:
        print("\n⚠️  SOME APIs FAILED!")
        print("Check the error messages above for troubleshooting.")
        
    print("\n📝 Next Steps:")
    if all_working:
        print("✅ Your APIs are ready - you can use your application normally")
        print("✅ All API structures are validated and working")
    else:
        print("1. Check API keys are valid and not expired")
        print("2. Verify chatflow IDs in your Flowise dashboard")
        print("3. Check network connectivity and firewall settings")

if __name__ == "__main__":
    main() 