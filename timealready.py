#!/usr/bin/env python3
"""
timealready - Autonomous Code Debugging Agent
Fixes bugs by analyzing stack traces, understanding file relations, and testing in sandbox.
"""
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from current directory first, then from home directory
# Use override=True to prioritize .env file over system environment variables
load_dotenv(override=True)
home_env = Path.home() / ".timealready" / ".env"
if home_env.exists():
    load_dotenv(home_env, override=True)

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
        1. Parse error message (minimal - just error type and message)
        2. Check UltraContext memory FIRST (no file scanning)
        3. If found in memory → Apply fix directly
        4. If NOT in memory → Then analyze files and generate fix
        """
        print("[*] Analyzing error message...")
        
        # Try to extract just error type and message (no file parsing yet)
        error_type, error_message = self._extract_error_basics(error_input)
        
        if error_type:
            print(f"[!] Error: {error_type}")
            print(f"    Message: {error_message[:100]}...")
            
            # Check memory FIRST before touching any files
            print("[*] Checking UltraContext for known fixes...")
            memory_fix = await self.memory.retrieve_by_error_type(error_type, error_message)
            
            if memory_fix:
                print(f"[+] Found fix in memory! (used {memory_fix.success_count} times before)")
                print(f"    Strategy: {memory_fix.fix_strategy}")
                print(f"    Cost: $0 (from memory)")
                
                return FixResult(
                    success=True,
                    message=f"Fix retrieved from memory: {memory_fix.fix_strategy}",
                    fixed_code=memory_fix.fixed_code,
                    diff=memory_fix.fix_strategy,
                    cost=0.0,
                    model_used="memory",
                    fix_strategy=memory_fix.fix_strategy
                )
        
        # Memory didn't have it - now do full analysis
        print("[*] Not found in memory. Analyzing full stack trace...")
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
        
        # Check memory for similar fixes (more detailed check)
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
        
        # Check if fix generation failed (API error, rate limit, etc.)
        if not fix_result.success:
            print(f"[-] Cheap model failed: {fix_result.message}")
            
            # Try to apply learned fix from memory as fallback
            if similar_fixes:
                print("[!] Attempting to apply learned fix from memory...")
                memory_fix = await self.memory.apply_learned_fix(error_report)
                
                if memory_fix and memory_fix.fixed_code:
                    print("[+] Applied fix from memory!")
                    # Test the memory fix
                    print("[*] Testing memory fix in sandbox...")
                    test_result = await self.sandbox.test_fix(
                        error_report=error_report,
                        fix_code=memory_fix.fixed_code
                    )
                    
                    if test_result.success:
                        print("[+] Memory fix works!")
                        return memory_fix
                    else:
                        print(f"[-] Memory fix failed: {test_result.error[:200] if test_result.error else 'Unknown'}")
            
            # If memory fallback didn't work, try smart model
            print("[!] Escalating to smart model...")
            fix_result = await self.fix_generator.generate_fix(
                error_report=error_report,
                learned_fixes=similar_fixes,
                use_smart=True
            )
            if not fix_result.success:
                return FixResult(
                    success=False,
                    message=f"Both models failed and no memory fix available. Last error: {fix_result.message}",
                    error_report=error_report
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
        print("[!] Cheap model fix didn't pass tests. Escalating to smart model...")
        fix_result = await self.fix_generator.generate_fix(
            error_report=error_report,
            learned_fixes=similar_fixes,
            use_smart=True
        )
        
        if not fix_result.success:
            return FixResult(
                success=False,
                message=f"Smart model failed: {fix_result.message}",
                error_report=error_report
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
    
    def _extract_error_basics(self, error_text: str) -> tuple:
        """Extract just error type and message without full parsing"""
        import re
        lines = error_text.strip().split('\n')
        
        # Look for error patterns
        for line in lines:
            # Match: ErrorType: message
            match = re.match(r'(\w+(?:Error|Exception)):\s*(.+)', line)
            if match:
                return match.group(1), match.group(2)
            
            # Match: title: ErrorType
            if 'title:' in line.lower():
                parts = line.split(':', 1)
                if len(parts) > 1:
                    error_type = parts[1].strip()
                    # Get detail from next lines
                    idx = lines.index(line)
                    message = ""
                    for next_line in lines[idx+1:idx+3]:
                        if 'detail:' in next_line.lower():
                            message = next_line.split(':', 1)[1].strip()
                            break
                    return error_type, message
        
        return None, None


async def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: timealready <error_log_or_file> [codebase_path]")
        print("\nExamples:")
        print("  timealready error.log")
        print("  timealready 'Traceback (most recent call last)...'")
        print("  timealready error.log /path/to/project")
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
