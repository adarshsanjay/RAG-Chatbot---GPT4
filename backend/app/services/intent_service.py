import re
import logging
from typing import List, Dict
from app.services.groq_service import groq_service

logger = logging.getLogger("intent_service")

VALID_INTENTS = [
    "faq",
    "product_question",
    "product_recommendation",
    "review_summary",
    "order_shipping",
    "returns_refunds",
    "general_support",
    "unknown"
]

INTENT_DETECTION_SYSTEM_PROMPT = """You are an intent detection classifier for an e-commerce customer support chatbot.
Analyze the user's input query and classify it into EXACTLY ONE of the following intent categories:

- faq: General questions about how the platform works, account setup, payment methods, security.
- product_question: Questions about specific product features, stock, warranty, size guides, authenticity, or specs.
- product_recommendation: Requests for product suggestions, best products in a category, or comparison between items.
- review_summary: Requests to summarize customer reviews, ratings, or feedback for a product.
- order_shipping: Questions about order placement, tracking order status, delivery times, shipping costs, or cancellation.
- returns_refunds: Questions about return window, refund policy, replacement, item condition for return, or auto-cancellation refunds.
- general_support: Contact info, support hours, customer care, store locations, or greetings.
- unknown: Completely off-topic, nonsensical, or queries outside e-commerce customer support context.

Respond ONLY with the single intent label from the list above. Do not include any extra words, punctuation, or explanation.
Example Output:
returns_refunds
"""

class IntentService:
    def detect_intent(self, message: str, history: List[Dict[str, str]] = None) -> str:
        if not message or not message.strip():
            return "unknown"

        cleaned_msg = message.strip()

        if groq_service.is_configured():
            try:
                user_content = f"User Query: {cleaned_msg}"
                if history:
                    recent = history[-2:]
                    history_str = " | ".join([f"{h['role']}: {h['content']}" for h in recent])
                    user_content = f"Recent History: {history_str}\nUser Query: {cleaned_msg}"

                raw_intent = groq_service.generate_chat_completion(
                    messages=[{"role": "user", "content": user_content}],
                    system_prompt=INTENT_DETECTION_SYSTEM_PROMPT,
                    temperature=0.0,
                    max_tokens=20
                ).strip().lower()

                # Clean output to match valid intents
                for valid_intent in VALID_INTENTS:
                    if valid_intent in raw_intent:
                        return valid_intent
            except Exception as e:
                logger.error(f"Groq intent detection error: {e}")

        # Heuristic fallback if Groq API call fails or is unconfigured
        return self._rule_based_fallback(cleaned_msg)

    def _rule_based_fallback(self, msg: str) -> str:
        msg_lower = msg.lower()

        if any(w in msg_lower for w in ["return", "refund", "exchange", "money back", "replacement"]):
            return "returns_refunds"
        if any(w in msg_lower for w in ["track", "ship", "delivery", "order", "cancel", "status", "courier", "package"]):
            return "order_shipping"
        if any(w in msg_lower for w in ["recommend", "suggest", "best", "which product", "compare"]):
            return "product_recommendation"
        if any(w in msg_lower for w in ["review", "rating", "feedback", "what people say", "stars"]):
            return "review_summary"
        if any(w in msg_lower for w in ["warranty", "size", "fit", "authentic", "genuine", "stock", "spec", "color"]):
            return "product_question"
        if any(w in msg_lower for w in ["payment", "tax", "gst", "account", "login", "faq"]):
            return "faq"
        if any(w in msg_lower for w in ["help", "contact", "support", "email", "phone", "hello", "hi", "hey"]):
            return "general_support"

        return "unknown"

intent_service = IntentService()
