import json
import re
import logging
from typing import Dict, Any, Optional
from core.llm import llm_service
from core.prompts import ENGLISH_COACH_SYSTEM_INSTRUCTION
from core.persona import persona_manager

logger = logging.getLogger(__name__)

def _clean_json(raw: str) -> str:
    """Strips markdown code fences and whitespace from LLM output."""
    raw = raw.strip()
    if raw.startswith("```json"):
        raw = raw[7:]
    elif raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    return raw.strip()

class EnglishCoachService:
    def __init__(self):
        self.llm = llm_service

    def analyze_and_improve(self, text: str, focus_area: Optional[str] = None) -> Dict[str, Any]:
        """Analyzes text for grammar, phrasing, vocabulary, and provides educational feedback."""
        persona = persona_manager.get_persona()
        level = persona.english_level or "Intermediate"
        focus = focus_area or "Grammar & Natural Fluency"

        user_prompt = f"""The user is an English language learner at the '{level}' level.
Their current learning focus is: '{focus}'.

Please analyze and improve the following text:
\"\"\"{text}\"\"\"

Provide:
1. A natural, corrected version.
2. An advanced, professional/executive version.
3. Detailed line-by-line or phrase-by-phrase explanations of what was changed and why (mentioning grammar rules, prepositions, tenses, or natural collocations).
4. Useful vocabulary boosts or idioms that fit this context.
5. An encouraging coaching tip for the user.
"""
        raw_response = self.llm.generate(
            prompt=user_prompt,
            system_instruction=ENGLISH_COACH_SYSTEM_INSTRUCTION,
            json_mode=True
        )

        try:
            cleaned = _clean_json(raw_response)
            data = json.loads(cleaned)
            return data
        except Exception as e:
            logger.error(f"Failed to parse English Coach JSON response: {e}\nRaw output: {raw_response}")
            # Fallback structure
            return {
                "original_text": text,
                "corrected_natural": raw_response,
                "advanced_professional": "See natural version above.",
                "corrections": [],
                "vocabulary_boost": [],
                "coach_encouragement": "Keep practicing! Every message you write helps you become more fluent."
            }

english_coach_service = EnglishCoachService()
