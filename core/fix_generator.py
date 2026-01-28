"""
Fix Generator - Uses RLMs to generate code fixes
"""
import replicate
import os
from typing import List
from models import ErrorReport, FixResult, LearnedFix


class FixGenerator:
    """Generates code fixes using cheap/smart models"""
    
    def __init__(self):
        self.cheap_model = "deepseek-ai/deepseek-v3"
        self.smart_model = "anthropic/claude-4.5-sonnet"
        # Get API token from environment
        api_token = os.getenv("REPLICATE_API_TOKEN")
        if not api_token:
            raise ValueError("REPLICATE_API_TOKEN not found in environment")
        # Create Replicate client with token
        self.client = replicate.Client(api_token=api_token)
    
    async def generate_fix(
        self,
        error_report: ErrorReport,
        learned_fixes: List[LearnedFix],
        use_smart: bool = False
    ) -> FixResult:
        """
        Generate a fix for the error.
        
        Args:
            error_report: The error to fix
            learned_fixes: Previously learned fixes for similar errors
            use_smart: If True, use expensive model
        """
        model = self.smart_model if use_smart else self.cheap_model
        
        # Build prompt
        prompt = self._build_fix_prompt(error_report, learned_fixes)
        
        try:
            # Call model using client
            if use_smart:
                output = self.client.run(
                    model,
                    input={
                        "prompt": prompt,
                        "system_prompt": "You are an expert debugger. Fix the code and return ONLY the fixed code, no explanations.",
                        "max_tokens": 8192
                    }
                )
            else:
                output = self.client.run(
                    model,
                    input={
                        "prompt": prompt,
                        "max_tokens": 2048,
                        "temperature": 0.1
                    }
                )
            
            # Collect output
            fixed_code = "".join(str(chunk) for chunk in output)
            
            # Extract just the code (remove markdown if present)
            fixed_code = self._extract_code(fixed_code)
            
            # Generate diff
            diff = self._generate_diff(error_report.file_content, fixed_code)
            
            return FixResult(
                success=True,
                error_report=error_report,
                fixed_code=fixed_code,
                diff=diff,
                cost=0.0002 if not use_smart else 0.006,
                model_used=model
            )
            
        except Exception as e:
            return FixResult(
                success=False,
                message=f"Fix generation failed: {str(e)}",
                error_report=error_report
            )
    
    def _build_fix_prompt(self, error_report: ErrorReport, learned_fixes: List[LearnedFix]) -> str:
        """Build prompt for fix generation"""
        
        # Detect language from file extension
        file_ext = error_report.file_path.split('.')[-1] if '.' in error_report.file_path else 'txt'
        lang_map = {
            'py': 'Python',
            'js': 'JavaScript',
            'ts': 'TypeScript',
            'java': 'Java',
            'cs': 'C#',
            'go': 'Go',
            'rs': 'Rust',
            'php': 'PHP',
            'rb': 'Ruby',
            'cpp': 'C++',
            'c': 'C',
            'swift': 'Swift',
            'kt': 'Kotlin',
        }
        language = lang_map.get(file_ext, 'code')
        
        prompt = f"""Fix this {language} error:

Error Type: {error_report.error_type}
Error Message: {error_report.error_message}
File: {error_report.file_path}
Line: {error_report.line_number}
"""
        
        if error_report.function_name:
            prompt += f"Function: {error_report.function_name}\n"
        
        # Add stack trace context
        if error_report.stack_trace and len(error_report.stack_trace) > 1:
            prompt += "\nCall chain (how we got here):\n"
            for frame in error_report.stack_trace[-3:]:  # Last 3 frames
                prompt += f"  {frame.file}:{frame.line}"
                if frame.function:
                    prompt += f" in {frame.function}()"
                prompt += "\n"
                if frame.code:
                    prompt += f"    Code: {frame.code}\n"
        
        # Add learned fixes
        if learned_fixes:
            prompt += "\nPreviously learned fixes for similar errors:\n"
            for i, fix in enumerate(learned_fixes[:3], 1):  # Top 3
                prompt += f"{i}. {fix.fix_strategy}\n"
            prompt += "\nApply these principles to fix the current error.\n"
        
        # Add the actual code
        if error_report.file_content:
            prompt += f"\nCurrent code in {error_report.file_path}:\n```{file_ext}\n{error_report.file_content}\n```\n"
        else:
            prompt += f"\nError occurred at line {error_report.line_number}\n"
        
        prompt += f"\nProvide the COMPLETE fixed file content. Return ONLY the {language} code, no explanations, no markdown:"
        
        return prompt
    
    def _extract_code(self, output: str) -> str:
        """Extract code from markdown if present"""
        # Remove markdown code blocks
        if "```python" in output:
            start = output.find("```python") + 9
            end = output.find("```", start)
            return output[start:end].strip()
        elif "```" in output:
            start = output.find("```") + 3
            end = output.find("```", start)
            return output[start:end].strip()
        return output.strip()
    
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
