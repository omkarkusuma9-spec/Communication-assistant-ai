import json
import logging
from typing import Dict, Any, Optional
from core.llm import llm_service
from core.prompts import DRAFTER_SYSTEM_INSTRUCTION
from core.persona import persona_manager
from services.english_coach import _clean_json

logger = logging.getLogger(__name__)

class DrafterService:
    def __init__(self):
        self.llm = llm_service

    def draft_message(
        self,
        notes: str,
        message_type: str = "Email",
        tone: Optional[str] = None,
        recipient_context: Optional[str] = None
    ) -> Dict[str, Any]:
        persona = persona_manager.get_persona()
        selected_tone = tone or persona.default_tone
        signature_template = persona.signature.replace("{user_name}", persona.user_name)

        rules_str = "\n".join(f"- {rule}" for rule in persona.custom_rules)

        user_prompt = f"""Draft a high-quality {message_type} based on the following input:

User Persona:
- Name: {persona.user_name}
- Role: {persona.role_title}
- Target Tone: {selected_tone}
- Desired Sign-off: {signature_template}
- Communication Guidelines:
{rules_str}

Recipient Context / Audience: {recipient_context or 'General / Colleague'}

Raw Notes / Points to include:
\"\"\"{notes}\"\"\"

Generate a ready-to-send draft with a clear subject line (if applicable), greeting, well-structured paragraphs, and the desired sign-off.
"""
        raw_response = self.llm.generate(
            prompt=user_prompt,
            system_instruction=DRAFTER_SYSTEM_INSTRUCTION,
            json_mode=True
        )

        try:
            cleaned = _clean_json(raw_response)
            data = json.loads(cleaned)
            return data
        except Exception as e:
            logger.error(f"Failed to parse Drafter JSON response: {e}\nRaw output: {raw_response}")
            return {
                "subject": f"Draft: {notes[:30]}...",
                "body": raw_response,
                "tone_used": selected_tone,
                "word_count": len(raw_response.split()),
                "communication_tips": ["Draft generated successfully."]
            }

drafter_service = DrafterService()
