from abc import ABC, abstractmethod

class LLMProvider(ABC):
    """Base interface for all LLM providers."""
    
    @abstractmethod
    def generate_content(self, prompt: str, schema=None, **kwargs):
        """
        Generates content from the LLM provider.
        
        Args:
            prompt: The instruction for the model.
            schema: Optional Pydantic BaseModel class to enforce JSON schema output.
            **kwargs: Additional provider-specific kwargs.
            
        Returns:
            The parsed result (either the pydantic model instance or raw text depending on schema).
        """
        pass
