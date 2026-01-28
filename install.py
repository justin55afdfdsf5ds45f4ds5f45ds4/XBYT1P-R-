#!/usr/bin/env python3
"""
Global installation script for XBYT1P&%R$@
"""
import os
import sys
import shutil
from pathlib import Path


def install():
    """Install XBYT1P globally"""
    print("[*] Installing XBYT1P&%R$@ globally...")
    
    # Install package
    print("[*] Installing Python package...")
    os.system(f'"{sys.executable}" -m pip install -e .')
    
    # Create config directory in home
    home_config = Path.home() / ".xbyt1p"
    home_config.mkdir(exist_ok=True)
    
    # Copy .env.example to home config if .env doesn't exist
    home_env = home_config / ".env"
    if not home_env.exists():
        print(f"[*] Creating config at {home_env}")
        shutil.copy(".env.example", home_env)
        print(f"[!] Please edit {home_env} and add your API keys:")
        print("    - REPLICATE_API_TOKEN")
        print("    - E2B_API_KEY")
        print("    - ULTRACONTEXT_API_KEY (optional)")
    else:
        print(f"[+] Config already exists at {home_env}")
    
    print("\n[+] Installation complete!")
    print("\nUsage:")
    print("  xbyt1p <error_log_file>")
    print("  xbyt1p error.log")
    print("  xbyt1p 'Traceback (most recent call last)...'")
    print(f"\nConfig: {home_env}")


if __name__ == "__main__":
    install()
