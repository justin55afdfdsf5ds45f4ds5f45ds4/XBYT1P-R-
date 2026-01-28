#!/usr/bin/env python3
"""
timealready installer
"""
import os
import sys
from pathlib import Path


def main():
    print("="*60)
    print("timealready - Paste your error, get the fix instantly")
    print("="*60)
    print()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("[!] Python 3.8+ required")
        sys.exit(1)
    
    print("[+] Python version OK")
    
    # Create config directory
    config_dir = Path.home() / ".timealready"
    config_dir.mkdir(exist_ok=True)
    print(f"[+] Config directory: {config_dir}")
    
    # Check for API keys
    env_file = config_dir / ".env"
    
    if not env_file.exists():
        print()
        print("="*60)
        print("API KEYS REQUIRED")
        print("="*60)
        print()
        print("Get free API keys:")
        print("1. Replicate: https://replicate.com")
        print("2. UltraContext: https://ultracontext.ai")
        print()
        
        replicate_key = input("Replicate API token (r8_...): ").strip()
        ultracontext_key = input("UltraContext API key (uc_live_...): ").strip()
        
        if not replicate_key or not ultracontext_key:
            print("[!] Both API keys required")
            sys.exit(1)
        
        # Save to .env
        with open(env_file, 'w') as f:
            f.write(f"REPLICATE_API_TOKEN={replicate_key}\n")
            f.write(f"ULTRACONTEXT_API_KEY={ultracontext_key}\n")
        
        print(f"[+] API keys saved to {env_file}")
    else:
        print(f"[+] API keys found in {env_file}")
    
    print()
    print("="*60)
    print("INSTALLATION COMPLETE")
    print("="*60)
    print()
    print("Try it:")
    print('  timealready "IndexError: list index out of range"')
    print()


if __name__ == "__main__":
    main()
