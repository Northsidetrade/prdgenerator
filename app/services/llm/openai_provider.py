"""OpenAI provider implementation."""

import logging
from typing import Dict, List, Optional, Union

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.services.llm.base import LLMProvider


class OpenAIProvider(LLMProvider):
    """
    OpenAI LLM provider implementation.
    
    Uses the OpenAI API to generate text using models like GPT-4, GPT-3.5, etc.
    """
    
    def __init__(self):
        """Initialize the OpenAI provider with API key from settings."""
        super().__init__()
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.default_model = "gpt-4"
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = 2000,
        temperature: Optional[float] = 0.7,
        model: Optional[str] = None
    ) -> str:
        """
        Generate text using OpenAI's models.
        
        Args:
            prompt: The input prompt for text generation
            max_tokens: Maximum number of tokens to generate
            temperature: Controls randomness, higher values = more random
            model: Specific OpenAI model to use (defaults to gpt-4)
        
        Returns:
            Generated text response
        """
        self.logger.info(f"Generating text with OpenAI, model: {model or self.default_model}")
        
        response = await self._call_with_retry(
            self._generate,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            model=model or self.default_model
        )
        
        return response
    
    async def _generate(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        model: str
    ) -> str:
        """
        Internal method to call OpenAI API.
        
        Args:
            prompt: The input prompt for text generation
            max_tokens: Maximum number of tokens to generate
            temperature: Controls randomness
            model: Specific OpenAI model to use
        
        Returns:
            Generated text from the model
        """
        try:
            completion = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional product manager helping create detailed PRD documents."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return completion.choices[0].message.content
        except Exception as e:
            self.logger.error(f"OpenAI API call failed: {str(e)}")
            raise
