#!/usr/bin/env python3
"""
Test memory fallback when Replicate fails
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

# Temporarily break Replicate API
os.environ["REPLICATE_API_TOKEN"] = "invalid_token_to_test_fallback"

from codehealer import CodeHealer

async def test():
    """Test memory fallback"""
    error_log = Path("test_project/error.log").read_text()
    healer = CodeHealer("test_project")
    
    print("\n" + "="*60)
    print("TESTING MEMORY FALLBACK (Replicate API disabled)")
    print("="*60 + "\n")
    
    result = await healer.heal(error_log)
    
    if result.success:
        print("\n" + "="*60)
        print("SUCCESS - MEMORY FALLBACK WORKED!")
        print("="*60)
        print(f"\nFile: {result.error_report.file_path}")
        print(f"Line: {result.error_report.line_number}")
        print(f"\nDiff:")
        print(result.diff)
        print(f"\nCost: ${result.cost:.6f}")
        print(f"Model: {result.model_used}")
    else:
        print(f"\nFAILED: {result.message}")

if __name__ == "__main__":
    asyncio.run(test())
