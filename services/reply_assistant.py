import json
import logging
from typing import Dict, Any, Optional
from core.llm import llm_service
from core.prompts import REPLY_GENERATOR_SYSTEM_INSTRUCTION
from core.persona import persona_manager
from services.english_coach import _clean_json

logger = logging.getLogger(__name__)

class ReplyAssistantService:
    def __init__(self):
        self.llm = llm_service

    def generate_replies(self, incoming_message: str, user_intent_notes: Optional[str] = None) -> Dict[str, Any]:
        persona = persona_manager.get_persona()
        signature = persona.signature.replace("{user_name}", persona.user_name)

        user_prompt = f"""Generate 3 contextual reply options to the incoming message below.

User Name: {persona.user_name}
Sign-off to use: {signature}
Specific instructions from user (if any): {user_intent_notes or 'None provided'}

Incoming Message received:
\"\"\"{incoming_message}\"\"\"

Generate 3 diverse options:
1. Affirmative / Positive agreement
2. Polite Decline / Alternative suggestion
3. Clarification / More information needed
"""
        raw_response = self.llm.generate(
            prompt=user_prompt,
            system_instruction=REPLY_GENERATOR_SYSTEM_INSTRUCTION,
            json_mode=True
        )

        try:
            cleaned = _clean_json(raw_response)
            data = json.loads(cleaned)
            return data
        except Exception as e:
            logger.error(f"Failed to parse Reply Assistant JSON response: {e}\nRaw output: {raw_response}")
            return {
                "sender_intent_summary": "General inquiry or message.",
                "options": [
                    {
                        "title": "Quick Reply",
                        "tone": "Professional",
                        "body": raw_response
                    }
                ]
            }

reply_assistant_service = ReplyAssistantService()
