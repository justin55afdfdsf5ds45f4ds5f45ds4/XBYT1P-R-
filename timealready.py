#!/usr/bin/env python3
"""
timealready - Paste your error, get the fix instantly
"""
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env
load_dotenv(override=True)
home_env = Path.home() / ".timealready" / ".env"
if home_env.exists():
    load_dotenv(home_env, override=True)

from core.memory import Memory
from core.llm import LLM


async def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: timealready <error_message_or_file>")
        print("\nExamples:")
        print('  timealready "IndexError: list index out of range"')
        print("  timealready error.log")
        sys.exit(1)
    
    error_input = sys.argv[1]
    
    # If it's a file, read it
    if Path(error_input).exists():
        # Try different encodings
        for encoding in ['utf-8', 'utf-16', 'cp1252', 'latin-1']:
            try:
                with open(error_input, encoding=encoding) as f:
                    error_input = f.read()
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
    
    # Clean up error (remove excessive whitespace)
    error_input = " ".join(error_input.split())
    
    print(f"[*] Error: {error_input[:100]}...")
    
    # Initialize
    memory = Memory()
    llm = LLM()
    
    # Check memory first
    print("[*] Checking memory...")
    fix = await memory.get(error_input)
    
    if fix:
        print("\n" + "="*60)
        print("FIX FOUND IN MEMORY (instant, $0)")
        print("="*60)
        print(f"\n{fix}\n")
        await memory.close()
        return
    
    # Not in memory - ask LLM
    print("[*] Not in memory. Asking LLM...")
    
    prompt = f"""You are a debugging expert. A developer has this error:

{error_input}

Provide a clear, concise fix. Include:
1. What caused the error
2. How to fix it (with code if applicable)
3. How to prevent it

Be direct and practical."""
    
    try:
        fix, cost = llm.ask(prompt)
        
        print("\n" + "="*60)
        print(f"FIX GENERATED (${cost:.6f})")
        print("="*60)
        print(f"\n{fix}\n")
        
        # Store in memory for next time
        await memory.store(error_input, fix)
        
    except Exception as e:
        print(f"\n[!] ERROR: {e}")
        sys.exit(1)
    
    finally:
        await memory.close()


def cli_entry():
    """Synchronous entry point for console script"""
    asyncio.run(main())


if __name__ == "__main__":
    cli_entry()
