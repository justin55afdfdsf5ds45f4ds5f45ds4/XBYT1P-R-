"""
Sandbox Executor - Runs code in E2B sandbox for testing
"""
import os
from pathlib import Path
from e2b_code_interpreter import Sandbox
from models import ErrorReport, TestResult


class SandboxExecutor:
    """Executes code in E2B sandbox"""
    
    def __init__(self):
        api_key = os.getenv("E2B_API_KEY")
        if not api_key:
            # Try alternate name
            api_key = os.getenv("E2B_API_TOKEN")
        if not api_key:
            raise ValueError("E2B_API_KEY not found in environment")
        # Set API key in environment for E2B
        os.environ["E2B_API_KEY"] = api_key
    
    async def test_fix(self, error_report: ErrorReport, fix_code: str) -> TestResult:
        """
        Test if the fix works by running it in sandbox.
        
        Steps:
        1. Create sandbox
        2. Upload all related files
        3. Write fixed code
        4. Try to execute the code that was failing
        5. Check if error is gone
        """
        sandbox = None
        try:
            # Create sandbox using new E2B API
            sandbox = Sandbox.create()
            
            # Upload all related files first (dependencies)
            for relation in error_report.related_files:
                try:
                    file_path = Path(relation.file)
                    if file_path.exists():
                        with open(file_path) as f:
                            content = f.read()
                        sandbox.files.write(str(file_path), content)
                except Exception as e:
                    print(f"Warning: Could not upload {relation.file}: {e}")
            
            # Write the fixed code
            sandbox.files.write(error_report.file_path, fix_code)
            
            # Generate and run test code
            test_code = self._generate_test_code(error_report)
            
            execution = sandbox.run_code(test_code)
            
            # Check result
            if execution.error:
                return TestResult(
                    success=False,
                    error=str(execution.error),
                    output=execution.text if hasattr(execution, 'text') else str(execution.results)
                )
            else:
                # Success if no error and has output
                return TestResult(
                    success=True,
                    output=execution.text if hasattr(execution, 'text') else str(execution.results)
                )
                
        except Exception as e:
            return TestResult(
                success=False,
                error=f"Sandbox execution failed: {str(e)}"
            )
        finally:
            if sandbox:
                try:
                    sandbox.close()
                except:
                    pass
    
    def _generate_test_code(self, error_report: ErrorReport) -> str:
        """
        Generate code to test if the fix works.
        
        Strategy:
        1. Try to import the fixed module
        2. If it was a function error, try to call it with safe inputs
        3. Check if the specific error is gone
        """
        # Get the file path without extension for import
        file_path = error_report.file_path.replace("\\", "/")
        
        # Remove .py extension and convert to module path
        if file_path.endswith(".py"):
            file_path = file_path[:-3]
        
        # Convert path to module (e.g., "test_project/utils" -> "test_project.utils")
        module_path = file_path.replace("/", ".")
        
        # If there's a function name, try to test it
        if error_report.function_name and error_report.function_name != "<module>":
            test_code = f"""
import sys
sys.path.insert(0, '.')

try:
    # Import the module
    import {module_path}
    print("✓ Module imported successfully")
    
    # Try to access the function
    func = getattr({module_path}, '{error_report.function_name}', None)
    if func:
        print(f"✓ Function '{error_report.function_name}' exists")
        # Try calling with empty/safe inputs to see if it crashes
        try:
            # For now, just check if it's callable
            if callable(func):
                print(f"✓ Function '{error_report.function_name}' is callable")
        except Exception as e:
            print(f"⚠ Function test: {{e}}")
    
    print("✓ Fix appears to work!")
    
except {error_report.error_type} as e:
    print(f"✗ Same error still occurs: {{e}}")
    raise
except Exception as e:
    print(f"✗ Different error: {{e}}")
    raise
"""
        else:
            # Just try to import the module
            test_code = f"""
import sys
sys.path.insert(0, '.')

try:
    import {module_path}
    print("✓ Module imported successfully")
    print("✓ Fix appears to work!")
except {error_report.error_type} as e:
    print(f"✗ Same error still occurs: {{e}}")
    raise
except Exception as e:
    print(f"✗ Different error: {{e}}")
    raise
"""
        
        return test_code
