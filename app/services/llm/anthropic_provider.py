"""Anthropic provider implementation."""

import logging
from typing import Dict, List, Optional, Union

import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.services.llm.base import LLMProvider


class AnthropicProvider(LLMProvider):
    """
    Anthropic LLM provider implementation.
    
    Uses the Anthropic API to generate text using Claude models.
    """
    
    def __init__(self):
        """Initialize the Anthropic provider with API key from settings."""
        super().__init__()
        self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.default_model = "claude-3-opus-20240229"
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = 2000,
        temperature: Optional[float] = 0.7,
        model: Optional[str] = None
    ) -> str:
        """
        Generate text using Anthropic's Claude models.
        
        Args:
            prompt: The input prompt for text generation
            max_tokens: Maximum number of tokens to generate
            temperature: Controls randomness, higher values = more random
            model: Specific Claude model to use
        
        Returns:
            Generated text response
        """
        self.logger.info(f"Generating text with Anthropic Claude, model: {model or self.default_model}")
        
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
        Internal method to call Anthropic API.
        
        Args:
            prompt: The input prompt for text generation
            max_tokens: Maximum number of tokens to generate
            temperature: Controls randomness
            model: Specific Claude model to use
        
        Returns:
            Generated text from the model
        """
        try:
            message = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system="You are a professional product manager helping create detailed PRD documents.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text
        except Exception as e:
            self.logger.error(f"Anthropic API call failed: {str(e)}")
            raise
