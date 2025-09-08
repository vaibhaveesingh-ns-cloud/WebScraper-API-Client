#!/usr/bin/env python3
"""
Test script to verify Scenario API authentication and check account status.
"""

import os
import base64
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SCENARIO_BASE = "https://api.cloud.scenario.com/v1"

def test_api_key():
    api_key = os.getenv("SCENARIO_API_KEY")
    api_secret = os.getenv("SCENARIO_API_SECRET")
    
    if not api_key:
        print("❌ No API key found in environment variables")
        return False
    
    print(f"✅ API Key loaded: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else api_key}")
    
    if not api_secret:
        print("❌ No API secret found in environment variables")
        print("💡 Scenario API requires both API_KEY and API_SECRET for Basic Authentication")
        print("   Please add SCENARIO_API_SECRET to your .env file")
        return False
    
    print(f"✅ API Secret loaded: {api_secret[:4]}...{api_secret[-4:] if len(api_secret) > 8 else '****'}")
    
    # Create Basic Auth header
    credentials = f"{api_key}:{api_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    
    print(f"🔐 Using Basic Auth: Basic {encoded_credentials[:20]}...")

    # Test 1: Check if we can access the API with a simple endpoint
    # Try to get account info or models (common endpoints that should work with valid auth)
    test_endpoints = [
        f"{SCENARIO_BASE}/models",
        f"{SCENARIO_BASE}/account",
        f"{SCENARIO_BASE}/users/me"
    ]
    
    for endpoint in test_endpoints:
        print(f"\n🔍 Testing endpoint: {endpoint}")
        try:
            response = requests.get(endpoint, headers=headers)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Authentication successful!")
                print("Response preview:", str(response.json())[:200] + "..." if len(str(response.json())) > 200 else response.json())
                return True
            elif response.status_code == 401:
                print("❌ Unauthorized - API key is invalid")
                print("Response:", response.text)
            elif response.status_code == 403:
                print("❌ Forbidden - API key doesn't have required permissions")
                print("Response:", response.text)
            else:
                print(f"⚠️  Unexpected status code: {response.status_code}")
                print("Response:", response.text)
                
        except requests.RequestException as e:
            print(f"❌ Request failed: {e}")
    
    # Test 2: Try a simple text-to-image generation request
    print(f"\n🔍 Testing text-to-image endpoint with minimal payload")
    txt2img_endpoint = f"{SCENARIO_BASE}/generate/txt2img"
    
    minimal_payload = {
        "prompt": "test",
        "numSamples": 1,
        "modelId": "flux.1-dev"
    }
    
    try:
        response = requests.post(txt2img_endpoint, json=minimal_payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Response:", response.text)
        
        if response.status_code == 200:
            print("✅ Text-to-image endpoint accessible!")
            return True
        elif response.status_code == 403:
            print("❌ Forbidden - Your account may not have access to this model or feature")
            
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    return False

if __name__ == "__main__":
    print("🧪 Testing Scenario API Authentication\n")
    success = test_api_key()
    
    if not success:
        print("\n💡 Troubleshooting suggestions:")
        print("1. Verify your API key is correct in the .env file")
        print("2. Check if your Scenario account has the necessary permissions")
        print("3. Ensure your account has credits/quota remaining")
        print("4. Try using a different model ID if available")
        print("5. Contact Scenario support if the issue persists")
