#!/usr/bin/env python3
"""
Test Replicate API connection
"""
import os
from dotenv import load_dotenv
import replicate

load_dotenv()

api_token = os.getenv("REPLICATE_API_TOKEN")
print(f"[*] API Token: {api_token[:10]}...{api_token[-4:]}")

try:
    client = replicate.Client(api_token=api_token)
    print("[+] Client created successfully")
    
    # Try to list models (doesn't cost anything)
    print("[*] Testing API connection by listing account info...")
    
    # Try a simple prediction
    print("[*] Attempting to run a model...")
    output = client.run(
        "deepseek-ai/deepseek-v3",
        input={
            "prompt": "Say 'hello'",
            "max_tokens": 10,
            "temperature": 0.1
        }
    )
    
    result = "".join(str(chunk) for chunk in output)
    print(f"[+] SUCCESS! Model responded: {result[:100]}")
    
except Exception as e:
    print(f"[-] Error: {e}")
    print(f"    Type: {type(e).__name__}")
    
    # Check if it's a credit/rate limit issue
    if "402" in str(e) or "Insufficient credit" in str(e):
        print("\n[!] This is a CREDIT issue - you need to add payment method to Replicate")
        print("    Go to: https://replicate.com/account/billing")
    elif "429" in str(e) or "throttled" in str(e):
        print("\n[!] This is a RATE LIMIT issue - add payment method to increase limits")
        print("    Go to: https://replicate.com/account/billing")
    else:
        print("\n[!] This is an API CONNECTION issue - check your token")
