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

        candidate_models = [self.model, "qwen/qwen3.6-27b", "groq/compound-mini", "openai/gpt-oss-20b", "llama-3.3-70b-versatile"]
        # Deduplicate preserving order
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
                raw_content = response.choices[0].message.content.strip()
                # Strip internal reasoning/thinking tags if present
                clean_content = re.sub(r'<think>.*?</think>', '', raw_content, flags=re.DOTALL).strip()
                return clean_content
            except Exception as e:
                last_error = e
                logger.warning(f"Error calling Groq API model '{target_model}': {e}. Retrying with fallback model...")

        logger.error(f"All Groq models failed: {last_error}")
        return f"Error communicating with Groq API: {str(last_error)}"

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
