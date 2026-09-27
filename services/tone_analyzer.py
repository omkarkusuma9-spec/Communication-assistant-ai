import json
import logging
from typing import Dict, Any, Optional
from core.llm import llm_service
from core.prompts import TONE_REFINER_SYSTEM_INSTRUCTION
from services.english_coach import _clean_json

logger = logging.getLogger(__name__)

class ToneAnalyzerService:
    def __init__(self):
        self.llm = llm_service

    def refine_tone(self, text: str, target_tone: str = "Professional & Executive") -> Dict[str, Any]:
        user_prompt = f"""Target Tone requested: {target_tone}

Analyze the tone of the message below and rewrite it to match the requested target tone.
Also provide 2 alternative versions in other contrasting tones (e.g. Friendly & Warm, or Ultra-Concise).

Input Message:
\"\"\"{text}\"\"\"
"""
        raw_response = self.llm.generate(
            prompt=user_prompt,
            system_instruction=TONE_REFINER_SYSTEM_INSTRUCTION,
            json_mode=True
        )

        try:
            cleaned = _clean_json(raw_response)
            data = json.loads(cleaned)
            return data
        except Exception as e:
            logger.error(f"Failed to parse Tone Refiner JSON response: {e}\nRaw output: {raw_response}")
            return {
                "original_tone": "Neutral",
                "target_tone": target_tone,
                "refined_text": raw_response,
                "alternative_versions": [],
                "key_changes_made": ["Rewrote text to align with desired tone."]
            }

tone_analyzer_service = ToneAnalyzerService()
