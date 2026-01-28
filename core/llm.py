"""
LLM - Simple interface to Replicate API
DeepSeek (cheap) → Claude (smart) fallback
"""
import os
import replicate


class LLM:
    """Simple LLM interface"""
    
    def __init__(self):
        self.api_token = os.getenv("REPLICATE_API_TOKEN")
        if not self.api_token:
            raise ValueError("REPLICATE_API_TOKEN required")
        
        os.environ["REPLICATE_API_TOKEN"] = self.api_token
        
        self.cheap_model = "deepseek-ai/deepseek-v3"
        self.smart_model = "anthropic/claude-3.5-sonnet"
    
    def ask(self, prompt: str, use_smart: bool = False) -> tuple[str, float]:
        """
        Ask LLM a question
        
        Returns:
            (response, cost)
        """
        model = self.smart_model if use_smart else self.cheap_model
        
        try:
            response = replicate.run(
                model,
                input={
                    "prompt": prompt,
                    "max_tokens": 2000,
                    "temperature": 0.3
                }
            )
            
            # Collect response
            result = ""
            for chunk in response:
                result += str(chunk)
            
            # Estimate cost (rough)
            cost = 0.0002 if not use_smart else 0.003
            
            return result.strip(), cost
            
        except Exception as e:
            if not use_smart:
                # Try smart model as fallback
                print(f"[!] Cheap model failed: {e}")
                print("[*] Trying smart model...")
                return self.ask(prompt, use_smart=True)
            else:
                raise Exception(f"Both models failed: {e}")
