#!/usr/bin/env python3
"""
XBYT1P&%R$@ - Autonomous Code Debugging Agent
Fixes bugs by analyzing stack traces, understanding file relations, and testing in sandbox.
"""
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from current directory first, then from home directory
load_dotenv()
home_env = Path.home() / ".xbyt1p" / ".env"
if home_env.exists():
    load_dotenv(home_env)

from core.error_analyzer import ErrorAnalyzer
from core.relation_mapper import RelationMapper
from core.sandbox_executor import SandboxExecutor
from core.fix_generator import FixGenerator
from core.memory_manager import MemoryManager
from models import ErrorReport, FixResult


class CodeHealer:
    """
    Main orchestrator for autonomous code healing.
    (Internal class name kept as CodeHealer for code compatibility)
    """
    
    def __init__(self, codebase_path: str = "."):
        self.codebase_path = Path(codebase_path).resolve()
        self.error_analyzer = ErrorAnalyzer()
        self.relation_mapper = RelationMapper(self.codebase_path)
        self.sandbox = SandboxExecutor()
        self.fix_generator = FixGenerator()
        self.memory = MemoryManager()
        
    async def heal(self, error_input: str) -> FixResult:
        """
        Main healing flow:
        1. Analyze error (parse stack trace)
        2. Map file relations (what depends on what)
        3. Check memory for similar fixes
        4. Generate fix with cheap model + memory
        5. Test in sandbox
        6. If fails, escalate to smart model
        7. Store successful fix in memory
        """
        print("[*] Analyzing error...")
        error_report = self.error_analyzer.parse(error_input, self.codebase_path)
        
        if not error_report:
            return FixResult(success=False, message="Could not parse error")
        
        print(f"[!] Error: {error_report.error_type} in {error_report.file_path}:{error_report.line_number}")
        
        # Map relations from stack trace
        print("[*] Mapping file relations...")
        relations = self.relation_mapper.map_from_stacktrace(error_report.stack_trace)
        error_report.related_files = relations
        
        print(f"[+] Related files: {len(relations)}")
        for rel in relations[:3]:
            print(f"    -> {rel.file}:{rel.line}")
        
        # Check memory for similar fixes
        print("[*] Checking memory for similar fixes...")
        similar_fixes = await self.memory.retrieve_similar(error_report)
        
        if similar_fixes:
            print(f"[+] Found {len(similar_fixes)} similar fix(es) in memory")
        
        # Generate fix (cheap model first)
        print("[*] Generating fix with cheap model...")
        fix_result = await self.fix_generator.generate_fix(
            error_report=error_report,
            learned_fixes=similar_fixes,
            use_smart=False
        )
        
        # Test in sandbox
        print("[*] Testing fix in sandbox...")
        if fix_result.fixed_code:
            print(f"    Generated {len(fix_result.fixed_code)} chars of code")
        test_result = await self.sandbox.test_fix(
            error_report=error_report,
            fix_code=fix_result.fixed_code or ""
        )
        
        if test_result.success:
            print("[+] Fix works! Storing in memory...")
            if test_result.output:
                print(f"    Output: {test_result.output[:200]}")
            await self.memory.store_fix(error_report, fix_result)
            return fix_result
        else:
            print(f"    Test failed: {test_result.error[:200] if test_result.error else 'Unknown'}")
        
        # Escalate to smart model
        print("[!] Cheap model fix failed. Escalating to smart model...")
        fix_result = await self.fix_generator.generate_fix(
            error_report=error_report,
            learned_fixes=similar_fixes,
            use_smart=True
        )
        
        # Test again
        print("[*] Testing smart model fix...")
        if fix_result.fixed_code:
            print(f"    Generated {len(fix_result.fixed_code)} chars of code")
        test_result = await self.sandbox.test_fix(
            error_report=error_report,
            fix_code=fix_result.fixed_code or ""
        )
        
        if test_result.success:
            print("[+] Smart model fix works! Storing in memory...")
            if test_result.output:
                print(f"    Output: {test_result.output[:200]}")
            await self.memory.store_fix(error_report, fix_result)
            return fix_result
        else:
            print(f"    Test failed: {test_result.error[:200] if test_result.error else 'Unknown'}")
            print("[-] Fix failed even with smart model")
            return FixResult(
                success=False,
                message=f"Could not generate working fix. Last error: {test_result.error}",
                error_report=error_report
            )


async def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: xbyt1p <error_log_or_file> [codebase_path]")
        print("\nExamples:")
        print("  xbyt1p error.log")
        print("  xbyt1p 'Traceback (most recent call last)...'")
        print("  xbyt1p error.log /path/to/project")
        sys.exit(1)
    
    error_input = sys.argv[1]
    
    # If it's a file, read it
    if Path(error_input).exists():
        with open(error_input) as f:
            error_input = f.read()
    
    # Initialize healer
    codebase_path = sys.argv[2] if len(sys.argv) > 2 else "."
    healer = CodeHealer(codebase_path)
    
    # Heal
    result = await healer.heal(error_input)
    
    if result.success:
        print("\n" + "="*60)
        print("SUCCESS - FIX GENERATED")
        print("="*60)
        print(f"\nFile: {result.error_report.file_path}")
        print(f"Line: {result.error_report.line_number}")
        print(f"\nDiff:")
        print(result.diff)
        print(f"\nCost: ${result.cost:.6f}")
        print(f"Model: {result.model_used}")
    else:
        print(f"\nFAILED: {result.message}")
        sys.exit(1)


def cli_entry():
    """Synchronous entry point for console script"""
    asyncio.run(main())


if __name__ == "__main__":
    cli_entry()
