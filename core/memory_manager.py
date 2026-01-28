"""
Memory Manager - Stores and retrieves fixes using UltraContext
"""
import os
import hashlib
import json
from typing import List, Optional
from models import ErrorReport, FixResult, LearnedFix
from datetime import datetime


class MemoryManager:
    """Manages learned fixes in UltraContext"""
    
    def __init__(self):
        self.api_key = os.getenv("ULTRACONTEXT_API_KEY")
        if not self.api_key:
            print("[!] WARNING: ULTRACONTEXT_API_KEY not found!")
            print("[!] UltraContext is REQUIRED for memory persistence and RLM scaling.")
            print("[!] Get your key at: https://ultracontext.ai")
            print("[!] System will use local storage (limited functionality)")
        
        # Local storage as fallback (limited functionality)
        self.local_storage = {}
        
        # Try to initialize UltraContext
        self.use_ultracontext = False
        if self.api_key:
            try:
                # TODO: Initialize UltraContext SDK when available
                # For now, use local storage with persistence
                self.use_ultracontext = False
                print("[*] UltraContext: Using local storage (SDK integration pending)")
                print("[!] For production use, UltraContext API is REQUIRED")
            except Exception as e:
                print(f"[!] UltraContext init failed: {e}")
    
    async def retrieve_similar(self, error_report: ErrorReport) -> List[LearnedFix]:
        """
        Retrieve similar fixes from memory.
        
        Matches by:
        1. Error type (exact)
        2. File pattern (similar paths)
        3. Success rate (prefer fixes that worked)
        """
        signature = self._generate_signature(error_report)
        
        # TODO: Use UltraContext API for semantic search
        # For now, simple local lookup
        matches = []
        for key, fix in self.local_storage.items():
            if fix.error_type == error_report.error_type:
                matches.append(fix)
        
        # Sort by success rate
        matches.sort(key=lambda f: f.success_rate, reverse=True)
        
        return matches[:5]  # Top 5
    
    async def apply_learned_fix(self, error_report: ErrorReport) -> Optional[FixResult]:
        """
        Try to apply a learned fix directly from memory.
        Used as fallback when Replicate API fails.
        
        Returns:
            FixResult if similar fix found, None otherwise
        """
        similar_fixes = await self.retrieve_similar(error_report)
        
        if not similar_fixes:
            return None
        
        # Use the best matching fix
        best_fix = similar_fixes[0]
        
        print(f"[+] Applying learned fix from memory (success rate: {best_fix.success_rate:.0%})")
        print(f"    Strategy: {best_fix.fix_strategy}")
        
        # Try to reconstruct the fix from the learned strategy
        # This is a simple heuristic - in production, store actual code diffs
        fixed_code = self._apply_fix_strategy(error_report, best_fix)
        
        if not fixed_code:
            return None
        
        return FixResult(
            success=True,
            error_report=error_report,
            fixed_code=fixed_code,
            diff=self._generate_diff(error_report.file_content, fixed_code),
            fix_strategy=best_fix.fix_strategy,
            cost=0.0,  # Free from memory!
            model_used="memory"
        )
    
    def _apply_fix_strategy(self, error_report: ErrorReport, learned_fix: LearnedFix) -> Optional[str]:
        """
        Apply learned fix strategy to current error.
        
        If we have the actual fixed code stored, return it directly.
        """
        if learned_fix.fixed_code:
            # We have the actual fix stored - return it
            return learned_fix.fixed_code
        
        # No stored code - can't apply
        return None
    
    async def store_fix(self, error_report: ErrorReport, fix_result: FixResult):
        """Store successful fix in memory with the actual code"""
        signature = self._generate_signature(error_report)
        
        # Check if we already have this fix
        if signature in self.local_storage:
            # Increment success count
            self.local_storage[signature].success_count += 1
            self.local_storage[signature].success_rate = min(
                1.0, 
                self.local_storage[signature].success_count / (self.local_storage[signature].success_count + 1)
            )
            print(f"💾 Updated fix: {signature[:16]}... (success count: {self.local_storage[signature].success_count})")
        else:
            # Create new learned fix with actual code
            learned_fix = LearnedFix(
                error_signature=signature,
                error_type=error_report.error_type,
                file_pattern=self._extract_pattern(error_report.file_path),
                fix_strategy=fix_result.fix_strategy or f"Fixed {error_report.error_type}",
                fixed_code=fix_result.fixed_code,  # Store actual fix
                success_count=1,
                created_at=datetime.utcnow()
            )
            
            self.local_storage[signature] = learned_fix
            print(f"💾 Stored fix: {signature[:16]}...")
        
        # TODO: Store in UltraContext for persistence across sessions
        # await self._store_to_ultracontext(signature, learned_fix)
    
    def _generate_signature(self, error_report: ErrorReport) -> str:
        """Generate unique signature for error"""
        # Combine error type + file pattern + error message pattern
        # Use file pattern instead of exact path for better matching
        file_pattern = self._extract_pattern(error_report.file_path)
        context = f"{error_report.error_type}:{file_pattern}:{error_report.error_message}"
        return hashlib.md5(context.encode()).hexdigest()
    
    def _extract_pattern(self, file_path: str) -> str:
        """Extract file pattern (e.g., 'api/*.py')"""
        # Normalize path
        file_path = file_path.replace('\\', '/')
        parts = file_path.split('/')
        
        # Get file extension
        ext = file_path.split('.')[-1] if '.' in file_path else 'txt'
        
        if len(parts) > 1:
            return f"{parts[0]}/*.{ext}"
        return f"*.{ext}"
    
    def _generate_diff(self, original: str, fixed: str) -> str:
        """Generate simple diff"""
        if not original:
            return fixed
        
        orig_lines = original.split('\n')
        fixed_lines = fixed.split('\n')
        
        diff = []
        for i, (orig, fix) in enumerate(zip(orig_lines, fixed_lines), 1):
            if orig != fix:
                diff.append(f"Line {i}:")
                diff.append(f"- {orig}")
                diff.append(f"+ {fix}")
        
        return '\n'.join(diff) if diff else "No changes"
