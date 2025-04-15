"""Base LLM provider interface."""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union

from tenacity import retry, stop_after_attempt, wait_exponential


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    This class defines the interface that all LLM providers must implement,
    providing a consistent way to interact with different AI models.
    """
    
    def __init__(self):
        """Initialize the LLM provider."""
        self.logger = logging.getLogger(f"app.services.llm.{self.__class__.__name__}")
    
    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = 2000,
        temperature: Optional[float] = 0.7,
        model: Optional[str] = None
    ) -> str:
        """
        Generate text from a prompt.
        
        Args:
            prompt: The input prompt for text generation
            max_tokens: Maximum number of tokens to generate
            temperature: Controls randomness, higher values = more random
            model: Specific model to use, provider-dependent
        
        Returns:
            Generated text response
        """
        pass
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _call_with_retry(self, func, *args, **kwargs):
        """
        Wrapper to call API with retry logic for transient failures.
        
        Args:
            func: The API function to call
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
        
        Returns:
            Result from the function call
        """
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"API call failed: {str(e)}")
            raise
