"""Abstract interface for embedding generation providers."""

from abc import ABC, abstractmethod


class EmbeddingProviderInterface(ABC):
    """Abstract base class for text embedding generation. Prevents vendor lock-in."""

    @abstractmethod
    async def generate(self, text: str) -> list[float]:
        """
        Generate a 768-dimensional embedding vector for the given text string.

        Args:
            text: Input text string to embed.

        Returns:
            List of 768 float values representing vector embedding.
        """
        ...
