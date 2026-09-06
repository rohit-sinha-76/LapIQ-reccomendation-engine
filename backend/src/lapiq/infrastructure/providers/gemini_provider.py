"""ReasoningProvider — Gemini google-genai SDK implementation of ReasoningProviderInterface.

This is the ONLY file in the codebase permitted to call the Gemini SDK directly.
All other modules must inject ReasoningProviderInterface and call provider.stream_explanation().
Direct SDK calls outside this file violate architecture invariant 4.
"""

import logging
from typing import AsyncIterator

from google import genai

from lapiq.core.config import settings
from lapiq.domain.interfaces.provider import ReasoningProviderInterface

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.5-flash"


class GeminiReasoningProvider(ReasoningProviderInterface):
    """
    Gemini API implementation using google-genai SDK (not google-generativeai — deprecated).

    Streams natural-language explanation chunks via SSE to the frontend.
    """

    def __init__(self) -> None:
        self._client: genai.Client | None = None

    def _get_client(self) -> genai.Client:
        """Lazily initialize Gemini client from settings."""
        if self._client is None:
            self._client = genai.Client(api_key=settings.gemini_api_key)
        return self._client

    async def stream_explanation(self, prompt_context: str) -> AsyncIterator[str]:
        """
        Stream explanation text chunks from Gemini 2.5 Flash.

        Uses client.aio for non-blocking async streaming. Does not block
        the FastAPI event loop during token generation (invariant 7).

        Raises ProviderError on API failure so the API layer can trigger
        the deterministic fallback path without LapIQ recommendation logic changing.
        """
        client = self._get_client()
        try:
            response = await client.aio.models.generate_content_stream(
                model=GEMINI_MODEL,
                contents=prompt_context,
            )
            async for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as exc:
            logger.error(
                "Gemini stream failed",
                extra={"error": str(exc)},
            )
            raise
