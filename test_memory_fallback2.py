#!/usr/bin/env python3
"""
Test memory fallback - Run this AFTER running xbyt1p once to populate memory
"""
import asyncio
import os
import sys
from pathlib import Path

# Set invalid token BEFORE importing
os.environ["REPLICATE_API_TOKEN"] = "r8_INVALID_TOKEN_FOR_TESTING"

from dotenv import load_dotenv
load_dotenv(override=False)  # Don't override our test token

from codehealer import CodeHealer

async def test():
    """Test memory fallback"""
    error_log = Path("test_project/error.log").read_text()
    healer = CodeHealer("test_project")
    
    print("\n" + "="*60)
    print("TESTING MEMORY FALLBACK")
    print("Replicate API Token: INVALID (should fail)")
    print("="*60 + "\n")
    
    result = await healer.heal(error_log)
    
    if result.success:
        print("\n" + "="*60)
        if result.model_used == "memory":
            print("✅ SUCCESS - MEMORY FALLBACK WORKED!")
            print("="*60)
            print("\n[!] Fix was applied from memory (no API call needed)")
        else:
            print("SUCCESS - But used API (not memory)")
            print("="*60)
        print(f"\nFile: {result.error_report.file_path}")
        print(f"Line: {result.error_report.line_number}")
        print(f"\nCost: ${result.cost:.6f}")
        print(f"Model: {result.model_used}")
    else:
        print(f"\n❌ FAILED: {result.message}")
        print("\nThis is expected if memory is empty.")
        print("Run 'xbyt1p test_project/error.log test_project' first to populate memory.")

if __name__ == "__main__":
    asyncio.run(test())
