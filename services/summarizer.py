import json
import logging
from typing import Dict, Any
from core.llm import llm_service
from core.prompts import SUMMARIZER_SYSTEM_INSTRUCTION
from services.english_coach import _clean_json

logger = logging.getLogger(__name__)

class SummarizerService:
    def __init__(self):
        self.llm = llm_service

    def summarize_content(self, content: str) -> Dict[str, Any]:
        user_prompt = f"""Analyze and summarize the following thread, conversation, or meeting notes:

\"\"\"{content}\"\"\"

Extract:
1. High-level summary (2-3 sentences).
2. Key takeaways.
3. Decisions made.
4. Concrete action items (with owner and priority if discernible).
"""
        raw_response = self.llm.generate(
            prompt=user_prompt,
            system_instruction=SUMMARIZER_SYSTEM_INSTRUCTION,
            json_mode=True
        )

        try:
            cleaned = _clean_json(raw_response)
            data = json.loads(cleaned)
            return data
        except Exception as e:
            logger.error(f"Failed to parse Summarizer JSON response: {e}\nRaw output: {raw_response}")
            return {
                "summary": raw_response[:200] + "...",
                "key_takeaways": ["Review full thread above."],
                "decisions_made": [],
                "action_items": []
            }

summarizer_service = SummarizerService()
