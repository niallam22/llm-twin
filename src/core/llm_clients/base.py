from abc import ABC, abstractmethod
from typing import Any, Dict, List


class LLMClientInterface(ABC):
    @abstractmethod
    async def generate(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        """
        Generates a text response based on the provided message history.

        Args:
            messages: A list of message dictionaries, where each dictionary
                      has 'role' (e.g., 'user', 'assistant') and 'content' keys.
            **kwargs: Additional keyword arguments to pass to the underlying LLM API.

        Returns:
            The generated text response from the LLM.
        """
        pass
