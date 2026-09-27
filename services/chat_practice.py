import json
import logging
from typing import Dict, Any, List, Optional
from core.llm import llm_service
from core.prompts import CHAT_PRACTICE_SYSTEM_INSTRUCTION
from core.persona import persona_manager
from services.english_coach import _clean_json

logger = logging.getLogger(__name__)

SCENARIO_PROFILES = {
    "Job Interview": {
        "partner_role": "A professional and friendly hiring manager conducting an interview",
        "context": "You are interviewing the candidate for a role relevant to their background. Ask realistic, conversational questions, listen to their answers, and respond authentically."
    },
    "Workplace Meeting & Updates": {
        "partner_role": "A collaborative team lead or colleague in a project sync meeting",
        "context": "You are discussing project timelines, blockers, team priorities, and collaborative tasks in a professional workplace setting."
    },
    "Coffee Chat & Small Talk": {
        "partner_role": "A friendly coworker or new acquaintance during a coffee break",
        "context": "Casual, warm, and natural everyday conversational English. Topics include hobbies, weekend plans, work-life balance, and current interests."
    },
    "Polite Negotiation & Pushback": {
        "partner_role": "A client or partner discussing deadlines and requirements",
        "context": "Practicing assertive yet diplomatic communication: negotiating deadlines, managing scope changes, or politely declining unreasonable requests."
    },
    "Casual Daily English": {
        "partner_role": "A supportive English-speaking friend",
        "context": "Relaxed everyday dialogue covering daily life, ordering food, travel plans, or sharing stories."
    }
}

class ChatPracticeService:
    def __init__(self):
        self.llm = llm_service

    def continue_conversation(
        self,
        scenario: str,
        history: List[Dict[str, str]],
        user_message: str
    ) -> Dict[str, Any]:
        persona = persona_manager.get_persona()
        level = persona.english_level or "Intermediate"
        scenario_info = SCENARIO_PROFILES.get(scenario, SCENARIO_PROFILES["Workplace Meeting & Updates"])

        # Format past conversation history
        dialogue_text = ""
        for msg in history[-8:]:  # keep last 8 turns for sharp context
            speaker = "User" if msg.get("role") == "user" else "Partner"
            dialogue_text += f"{speaker}: {msg.get('text', '')}\n"

        prompt = f"""Scenario: {scenario}
Partner Role: {scenario_info['partner_role']}
Setting / Context: {scenario_info['context']}

User Profile:
- Name: {persona.user_name}
- English Level: {level}

Conversation Transcript so far:
{dialogue_text if dialogue_text else '(Beginning of conversation)'}
User (latest input): \"\"\"{user_message}\"\"\"

Generate:
1. 'partner_reply': Your natural, in-character spoken response to the user's latest statement (1-3 conversational sentences).
2. 'coach_feedback': Comprehensive educational feedback on the user's sentence:
   - 'has_corrections': Boolean
   - 'grammar_check': Note any tense, preposition, or sentence structure fixes.
   - 'more_natural_way': A more native, fluid way to say what the user meant.
   - 'vocabulary_tip': 1 great vocabulary word or idiom suited for this moment.
   - 'speaking_tip': A pronunciation, rhythm, or intonation tip for vocal practice.
"""
        raw_response = self.llm.generate(
            prompt=prompt,
            system_instruction=CHAT_PRACTICE_SYSTEM_INSTRUCTION,
            json_mode=True
        )

        try:
            cleaned = _clean_json(raw_response)
            data = json.loads(cleaned)
            return data
        except Exception as e:
            logger.error(f"Failed to parse Chat Practice JSON: {e}\nRaw output: {raw_response}")
            return {
                "partner_reply": "That makes sense! Tell me more about that.",
                "coach_feedback": {
                    "has_corrections": False,
                    "grammar_check": "Your message was clear and understandable!",
                    "more_natural_way": user_message,
                    "vocabulary_tip": "Keep sentences concise for conversational confidence.",
                    "speaking_tip": "Speak with steady pace and emphasize key verbs."
                }
            }

chat_practice_service = ChatPracticeService()
