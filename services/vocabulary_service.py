import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from core.llm import llm_service
from core.prompts import VOCABULARY_GENERATOR_SYSTEM_INSTRUCTION, VOCABULARY_QUIZ_SYSTEM_INSTRUCTION
from core.persona import persona_manager
from services.english_coach import _clean_json

logger = logging.getLogger(__name__)

TOPICS = [
    "Workplace & Leadership",
    "Everyday Idioms & Phrasal Verbs",
    "Casual Fluency & Social Small Talk",
    "Persuasive & Diplomatic Language",
    "Meetings & Negotiations"
]

class VocabularyService:
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            storage_path = "/tmp/saved_words.json" if os.getenv("VERCEL") else "saved_words.json"
        self.llm = llm_service
        self.storage_path = Path(storage_path)

    def get_topics(self) -> List[str]:
        return TOPICS

    def get_words_for_topic(self, topic: str) -> Dict[str, Any]:
        persona = persona_manager.get_persona()
        level = persona.english_level or "Intermediate"

        prompt = f"""Topic: {topic}
User English Level: {level}

Select 5 practical, high-value vocabulary words, idioms, or phrasal verbs for this topic that will noticeably improve fluency and confidence.
Include phonetic pronunciation, definition, realistic workplace/conversational example, collocations, and when to use.
"""
        raw_response = self.llm.generate(
            prompt=prompt,
            system_instruction=VOCABULARY_GENERATOR_SYSTEM_INSTRUCTION,
            json_mode=True
        )

        try:
            cleaned = _clean_json(raw_response)
            data = json.loads(cleaned)
            return data
        except Exception as e:
            logger.error(f"Failed to parse Vocabulary JSON: {e}\nRaw output: {raw_response}")
            return {
                "topic": topic,
                "words": [
                    {
                        "word": "collaborate",
                        "phonetic": "/kəˈlæb.ə.reɪt/",
                        "part_of_speech": "verb",
                        "definition": "To work together on a common goal or project.",
                        "example": "We can collaborate on this task to finish ahead of schedule.",
                        "collocations": ["collaborate on", "collaborate with"],
                        "when_to_use": "Use when highlighting teamwork."
                    }
                ]
            }

    def evaluate_practice_sentence(self, target_word: str, sentence: str) -> Dict[str, Any]:
        persona = persona_manager.get_persona()
        level = persona.english_level or "Intermediate"

        prompt = f"""Target Vocabulary Word: '{target_word}'
User's English Level: '{level}'
User's Practice Sentence:
\"\"\"{sentence}\"\"\"

Check if the user used '{target_word}' accurately in context and with proper grammar and prepositions.
Provide constructive feedback and a suggested polish.
"""
        raw_response = self.llm.generate(
            prompt=prompt,
            system_instruction=VOCABULARY_QUIZ_SYSTEM_INSTRUCTION,
            json_mode=True
        )

        try:
            cleaned = _clean_json(raw_response)
            data = json.loads(cleaned)
            return data
        except Exception as e:
            logger.error(f"Failed to parse Sentence Evaluation JSON: {e}\nRaw output: {raw_response}")
            return {
                "target_word": target_word,
                "is_correct": True,
                "accuracy_rating": "Good",
                "feedback": "Your sentence communicates the idea clearly.",
                "suggested_improvement": sentence,
                "encouragement": "Nice effort putting new vocabulary into real practice!"
            }

    # Saved Word Bank Management
    def get_saved_words(self) -> List[Dict[str, Any]]:
        if not self.storage_path.exists():
            return []
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def save_word(self, word_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        saved = self.get_saved_words()
        word_text = word_data.get("word", "").lower()
        # Avoid duplicates
        filtered = [w for w in saved if w.get("word", "").lower() != word_text]
        filtered.insert(0, word_data)
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(filtered, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save word: {e}")
        return filtered

    def remove_saved_word(self, word_text: str) -> List[Dict[str, Any]]:
        saved = self.get_saved_words()
        filtered = [w for w in saved if w.get("word", "").lower() != word_text.lower()]
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(filtered, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to remove word: {e}")
        return filtered

vocabulary_service = VocabularyService()
