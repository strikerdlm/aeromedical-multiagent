#!/usr/bin/env python3
"""
Debug script to check configuration values
"""

import os
from src.config import FlowiseConfig

def main():
    print("🔍 Debugging Flowise Configuration...")
    print("=" * 50)
    
    print(f"BASE_URL: {FlowiseConfig.BASE_URL}")
    print(f"API_KEY: {FlowiseConfig.API_KEY[:20]}..." if FlowiseConfig.API_KEY else "API_KEY: NOT SET")
    
    print("\nChatflow IDs:")
    for name, chatflow_id in FlowiseConfig.CHATFLOW_IDS.items():
        print(f"  {name}: {chatflow_id}")
    
    print("\nEnvironment Variables:")
    print(f"  FLOWISE_API_URL: {os.getenv('FLOWISE_API_URL', 'NOT SET')}")
    print(f"  FLOWISE_API_KEY: {'SET' if os.getenv('FLOWISE_API_KEY') else 'NOT SET'}")
    
    print(f"\nHeaders that would be used:")
    headers = FlowiseConfig.get_headers()
    print(f"  Authorization: {headers.get('Authorization', 'NOT SET')[:30]}...")
    print(f"  Content-Type: {headers.get('Content-Type', 'NOT SET')}")

if __name__ == "__main__":
    main() 