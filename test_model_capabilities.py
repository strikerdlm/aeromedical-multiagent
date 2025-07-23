#!/usr/bin/env python3
"""
Test script to validate grok-4 and sonar-deep-research model capabilities.
This script tests the enhanced model support and ensures proper fallback mechanisms.
"""

import os
import requests
import json
import time
from typing import Dict, Any, Optional

def test_grok_models() -> Dict[str, bool]:
    """Test Grok models with fallback support."""
    print("🤖 Testing Grok Models...")
    
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        print("❌ XAI_API_KEY not found in environment variables")
        return {"grok-4": False, "grok-beta": False}
    
    url = "https://api.x.ai/v1/chat/completions"
    results = {}
    
    for model in ["grok-4", "grok-beta"]:
        print(f"\n🔄 Testing {model}...")
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": "Explain the concept of systematic review in 2 sentences."}
            ],
            "max_tokens": 100,
            "temperature": 0.3
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                print(f"✅ {model} SUCCESS")
                print(f"📝 Response: {content[:150]}...")
                results[model] = True
            else:
                print(f"❌ {model} FAILED: Status {response.status_code}")
                print(f"📝 Error: {response.text[:200]}...")
                results[model] = False
                
        except Exception as e:
            print(f"❌ {model} EXCEPTION: {e}")
            results[model] = False
    
    return results

def test_sonar_deep_research() -> bool:
    """Test Perplexity sonar-deep-research model."""
    print("\n🔍 Testing Sonar Deep Research Model...")
    
    api_key = os.getenv("PPLX_API_KEY")
    if not api_key:
        print("❌ PPLX_API_KEY not found in environment variables")
        return False
    
    url = "https://api.perplexity.ai/chat/completions"
    
    payload = {
        "model": "sonar-deep-research",
        "messages": [
            {"role": "user", "content": "What are the key components of a PRISMA systematic review?"}
        ],
        "max_tokens": 200,
        "temperature": 0.3,
        "search_domain_filter": ["pubmed.ncbi.nlm.nih.gov", "scholar.google.com"]
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=45)
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            print(f"✅ sonar-deep-research SUCCESS")
            print(f"📝 Response: {content[:200]}...")
            return True
        else:
            print(f"❌ sonar-deep-research FAILED: Status {response.status_code}")
            print(f"📝 Error: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ sonar-deep-research EXCEPTION: {e}")
        return False

def test_model_integration() -> None:
    """Test integration between grok and sonar models for PRISMA workflow."""
    print("\n🔬 Testing Model Integration for PRISMA Workflow...")
    
    # Test sonar for literature search
    print("1️⃣ Testing literature search with sonar-deep-research...")
    sonar_result = test_sonar_deep_research()
    
    # Test grok for critical analysis
    print("2️⃣ Testing critical analysis with Grok models...")
    grok_results = test_grok_models()
    
    # Summary
    print("\n📊 INTEGRATION TEST SUMMARY:")
    print(f"🔍 Literature Search (sonar-deep-research): {'✅ PASS' if sonar_result else '❌ FAIL'}")
    print(f"🤖 Critical Analysis (grok-4): {'✅ PASS' if grok_results.get('grok-4', False) else '❌ FAIL'}")
    print(f"🤖 Fallback Analysis (grok-beta): {'✅ PASS' if grok_results.get('grok-beta', False) else '❌ FAIL'}")
    
    # Overall status
    has_grok = any(grok_results.values())
    overall_success = sonar_result and has_grok
    
    print(f"\n🎯 OVERALL PRISMA CAPABILITY: {'✅ READY' if overall_success else '❌ INCOMPLETE'}")
    
    if overall_success:
        print("✨ The system is ready for PRISMA systematic reviews!")
        print("📚 Literature search: sonar-deep-research")
        preferred_grok = "grok-4" if grok_results.get('grok-4', False) else "grok-beta"
        print(f"🔍 Critical analysis: {preferred_grok}")
    else:
        print("⚠️ Some components need attention:")
        if not sonar_result:
            print("  - Configure PPLX_API_KEY for literature search")
        if not has_grok:
            print("  - Configure XAI_API_KEY for critical analysis")

def main():
    """Main test function."""
    print("🧪 Model Capabilities Test Suite")
    print("=" * 50)
    
    # Check environment
    print("🔧 Checking Environment Variables...")
    xai_key = "✅ SET" if os.getenv("XAI_API_KEY") else "❌ MISSING"
    pplx_key = "✅ SET" if os.getenv("PPLX_API_KEY") else "❌ MISSING"
    
    print(f"XAI_API_KEY: {xai_key}")
    print(f"PPLX_API_KEY: {pplx_key}")
    
    if xai_key == "❌ MISSING" and pplx_key == "❌ MISSING":
        print("\n⚠️ No API keys found. Please set environment variables:")
        print("export XAI_API_KEY='your_xai_grok_api_key'")
        print("export PPLX_API_KEY='your_perplexity_api_key'")
        return
    
    # Run integration test
    test_model_integration()

if __name__ == "__main__":
    main()