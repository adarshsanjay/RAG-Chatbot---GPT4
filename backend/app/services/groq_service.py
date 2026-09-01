import os
import re
import logging
from typing import List, Dict, Optional
from groq import Groq
from app.config import GROQ_API_KEY, GROQ_MODEL

logger = logging.getLogger("groq_service")

class GroqService:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY") or GROQ_API_KEY
        self.model = model or os.getenv("GROQ_MODEL") or GROQ_MODEL
        self.client = None
        if self.api_key and self.api_key != "your_groq_api_key_here":
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
                self.client = None

    def is_configured(self) -> bool:
        return self.client is not None

    def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024
    ) -> str:
        if not self.is_configured():
            logger.warning("Groq API key not set or client unavailable. Using fallback generation.")
            return self._fallback_answer(messages, system_prompt)

        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)

        # Priority list: standard chat models first (no think tags), reasoning models as fallback
        # Only models confirmed available on this Groq account
        candidate_models = [
            self.model,
            "openai/gpt-oss-20b",
            "openai/gpt-oss-120b",
            "groq/compound",
            "groq/compound-mini",
            "qwen/qwen3.8-27b",
            "qwen/qwen3.6-27b",
        ]
        # Deduplicate preserving order, skip empty values
        candidate_models = list(dict.fromkeys([m for m in candidate_models if m]))

        last_error = None
        for target_model in candidate_models:
            try:
                response = self.client.chat.completions.create(
                    model=target_model,
                    messages=formatted_messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                choice = response.choices[0]
                raw_content = (choice.message.content or "").strip()

                clean_content = self._strip_think_tags(raw_content)

                # If stripping produced empty string, the whole answer was inside <think>
                # Try to extract the final answer section from within
                if not clean_content and raw_content:
                    clean_content = self._extract_answer_from_think(raw_content)

                if clean_content:
                    logger.info(f"Got answer from model '{target_model}' ({len(clean_content)} chars)")
                    return clean_content

                # If still empty, try next model
                logger.warning(f"Model '{target_model}' returned empty content after processing. Trying next.")
            except Exception as e:
                last_error = e
                logger.warning(f"Error calling Groq API model '{target_model}': {e}. Retrying with fallback model...")

        logger.error(f"All Groq models failed: {last_error}")
        return f"Error communicating with Groq API: {str(last_error)}"

    def _strip_think_tags(self, text: str) -> str:
        """Remove <think>...</think> blocks, keeping only text AFTER them."""
        # Remove closed think blocks entirely
        result = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        # Remove unclosed think blocks (from <think> to end of string)
        result = re.sub(r'<think>.*$', '', result, flags=re.DOTALL)
        return result.strip()

    def _extract_answer_from_think(self, text: str) -> str:
        """
        When the entire response is inside <think> tags (qwen-style reasoning models),
        extract a clean final answer from the last substantive paragraph inside the block.
        """
        # Pull the content inside <think>
        match = re.search(r'<think>(.*?)(?:</think>|$)', text, flags=re.DOTALL)
        inner = match.group(1).strip() if match else text.strip()

        # Look for explicit 'Final Answer:' or 'Answer:' section markers
        final_match = re.search(
            r'(?:Final Answer|Final Response|Final Draft|Draft):\s*(.*)',
            inner, flags=re.DOTALL | re.IGNORECASE
        )
        if final_match:
            return final_match.group(1).strip()

        # Otherwise take the last non-empty paragraph (usually the answer draft)
        paragraphs = [p.strip() for p in re.split(r'\n{2,}', inner) if p.strip()]
        if paragraphs:
            return paragraphs[-1]

        return inner

    def _fallback_answer(self, messages: List[Dict[str, str]], system_prompt: Optional[str]) -> str:
        last_message = messages[-1]["content"] if messages else ""
        if "GROQ_API_KEY" not in os.environ and not GROQ_API_KEY:
            return (
                "⚠️ **Groq API Key missing**: Please configure `GROQ_API_KEY` in your `.env` file to enable AI answers.\n\n"
                f"**System Prompt Context Provided**:\n{system_prompt[:300]}..." if system_prompt else f"Question received: '{last_message}'"
            )
        return f"Unable to reach Groq API. Received question: '{last_message}'"

# Singleton instance
groq_service = GroqService()
