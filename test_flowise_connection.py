#!/usr/bin/env python3
"""
Simple test script to diagnose Flowise API connectivity issues.
This uses the exact structure provided by the user.
"""

import requests
import sys

def test_basic_connectivity():
    """Test basic network connectivity to cloud.flowiseai.com"""
    try:
        # Test basic connectivity
        response = requests.get("https://cloud.flowiseai.com", timeout=10)
        print(f"✅ Basic connectivity to cloud.flowiseai.com: {response.status_code}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to cloud.flowiseai.com: {e}")
        return False

def test_flowise_api():
    """Test the Flowise API using the exact structure provided by user"""
    API_URL = "https://cloud.flowiseai.com/api/v1/prediction/d0bf0d84-1343-4f3b-a887-780d20f9e3c6"
    headers = {"Authorization": "Bearer wDwjOLUaht_AkEgpyk1c8zw3ApNe7vdy69_uBbdeMCU"}

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()
    
    try:
        print("🧪 Testing Flowise API with exact user structure...")
        output = query({
            "question": "Hey, how are you?",
        })
        print("✅ Flowise API test successful!")
        print(f"Response: {output}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Flowise API test failed: {e}")
        return False

def main():
    print("🔍 Diagnosing Flowise API connectivity...")
    print("=" * 50)
    
    # Test 1: Basic connectivity
    connectivity_ok = test_basic_connectivity()
    
    if not connectivity_ok:
        print("\n💡 Network connectivity issue detected.")
        print("Possible solutions:")
        print("1. Check your internet connection")
        print("2. Try running: ipconfig /flushdns (Windows)")
        print("3. Check if a firewall/proxy is blocking the connection")
        print("4. Try using a different DNS server (8.8.8.8, 1.1.1.1)")
        return
    
    # Test 2: Flowise API
    print("\n" + "=" * 50)
    api_ok = test_flowise_api()
    
    if api_ok:
        print("\n✅ All tests passed! The API structure is working correctly.")
    else:
        print("\n❌ API test failed even with basic connectivity working.")
        print("This suggests an authentication or API key issue.")

if __name__ == "__main__":
    main() 