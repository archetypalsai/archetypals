# AnythingLLM service

import httpx
from typing import Optional, Dict, Any
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class AnythingLLMService:
    def __init__(self):
        self.base_url = settings.ANYTHINGLLM_API_URL
        self.api_key = settings.ANYTHINGLLM_API_KEY
        self.timeout = httpx.Timeout(30.0)
        self.client = httpx.AsyncClient()
    
    async def get_response(self, query: str, workspace_id: str) -> str:
        """Get response from AnythingLLM"""
        try:
            response = await self.client.post(
                f"{self.base_url}/workspace/{workspace_id}/chat",
                json={
                    "message": query,
                    "mode": "query"
                },
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json().get("textResponse", "")
        except Exception as e:
            logger.error(f"Failed to get LLM response: {str(e)}")
            raise
    
    async def get_safe_response(self, query: str, violations: Dict[str, Any]) -> str:
        """Get a safety-modified response based on violations"""
        try:
            # Craft a prompt that explains the violations to the LLM
            prompt = (
                f"The original response to this query was rejected for safety reasons. "
                f"Violations detected: {str(violations)}\n\n"
                f"Please provide a helpful, safe alternative response to: {query}\n"
                f"Guidelines:\n"
                f"- Avoid all harmful, biased, or unethical content\n"
                f"- Be factual and cite sources when possible\n"
                f"- If unsure, offer to help in other ways"
            )
            
            response = await self.client.post(
                f"{self.base_url}/workspace/{settings.ANYTHINGLLM_WORKSPACE_ID}/chat",
                json={
                    "message": prompt,
                    "mode": "query"
                },
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json().get("textResponse", "I can't answer that question, but I'm happy to help with other topics.")
        except Exception as e:
            logger.error(f"Failed to get safe response: {str(e)}")
            return "I can't answer that question, but I'm happy to help with other topics."
    
    async def close(self):
        await self.client.aclose()