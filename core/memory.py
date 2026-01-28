"""
Memory - Simple UltraContext interface
"""
import os
import httpx
import hashlib
from pathlib import Path
from typing import Optional
from datetime import datetime


class Memory:
    """Simple memory interface using UltraContext"""
    
    def __init__(self):
        self.api_key = os.getenv("ULTRACONTEXT_API_KEY")
        if not self.api_key:
            raise ValueError("ULTRACONTEXT_API_KEY required")
        
        self.base_url = "https://api.ultracontext.ai"
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
        
        # Load or create context ID
        self.storage_dir = Path.home() / ".timealready"
        self.storage_dir.mkdir(exist_ok=True)
        self.context_file = self.storage_dir / "context_id.txt"
        self.context_id = None
    
    async def _ensure_context(self):
        """Ensure we have a context ID"""
        if self.context_id:
            return
        
        # Try to load existing context ID
        if self.context_file.exists():
            self.context_id = self.context_file.read_text().strip()
            return
        
        # Create new context
        response = await self.client.post(f"{self.base_url}/contexts")
        if response.status_code == 201:
            data = response.json()
            self.context_id = data["id"]
            self.context_file.write_text(self.context_id)
        else:
            raise Exception(f"Failed to create context: {response.status_code}")
    
    async def get(self, error: str) -> Optional[str]:
        """
        Get fix for error from memory
        
        Returns:
            Fix string if found, None otherwise
        """
        await self._ensure_context()
        
        try:
            response = await self.client.get(f"{self.base_url}/contexts/{self.context_id}")
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            messages = data.get("data", [])
            
            # Simple matching - just check if error text is similar
            error_lower = error.lower()
            
            for msg in messages:
                if msg.get("error", "").lower() in error_lower or error_lower in msg.get("error", "").lower():
                    return msg.get("fix")
            
            return None
            
        except Exception as e:
            print(f"[!] Memory error: {e}")
            return None
    
    async def store(self, error: str, fix: str):
        """Store error and fix in memory"""
        await self._ensure_context()
        
        try:
            response = await self.client.post(
                f"{self.base_url}/contexts/{self.context_id}",
                json={
                    "error": error,
                    "fix": fix,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            if response.status_code == 201:
                print(f"[+] Stored in memory")
            
        except Exception as e:
            print(f"[!] Failed to store: {e}")
    
    async def close(self):
        """Close the client"""
        await self.client.aclose()
