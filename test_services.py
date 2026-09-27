import os
import pytest
from core.persona import UserPersona, PersonaManager
from services.english_coach import EnglishCoachService
from services.chat_practice import ChatPracticeService
from services.vocabulary_service import VocabularyService
from services.drafter import DrafterService
from services.tone_analyzer import ToneAnalyzerService
from services.reply_assistant import ReplyAssistantService
from services.summarizer import SummarizerService

def test_persona_defaults():
    pm = PersonaManager(storage_path="test_persona.json")
    persona = pm.get_persona()
    assert persona.english_level in ["Beginner", "Intermediate", "Advanced"]
    assert len(persona.custom_rules) > 0

def test_english_coach_offline_demo():
    service = EnglishCoachService()
    result = service.analyze_and_improve("I am writing this email for asking update.")
    assert "corrected_natural" in result or "original_text" in result
    assert "corrections" in result or "coach_encouragement" in result

def test_chat_practice_offline_demo():
    service = ChatPracticeService()
    result = service.continue_conversation(
        scenario="Job Interview",
        history=[],
        user_message="I have five years of experience in software engineering."
    )
    assert "partner_reply" in result
    assert "coach_feedback" in result
    assert "grammar_check" in result["coach_feedback"]

def test_vocabulary_topics_and_words():
    service = VocabularyService(storage_path="test_saved_words.json")
    topics = service.get_topics()
    assert len(topics) >= 3
    
    result = service.get_words_for_topic(topics[0])
    assert "words" in result
    assert len(result["words"]) > 0
    first_word = result["words"][0]
    assert "word" in first_word
    assert "definition" in first_word

def test_vocabulary_sentence_evaluation():
    service = VocabularyService(storage_path="test_saved_words.json")
    result = service.evaluate_practice_sentence(
        target_word="collaborate",
        sentence="I collaborate with my colleagues every day."
    )
    assert "target_word" in result
    assert "feedback" in result

def test_vocabulary_save_and_remove():
    test_storage = "test_saved_words.json"
    if os.path.exists(test_storage):
        os.remove(test_storage)

    service = VocabularyService(storage_path=test_storage)
    sample_word = {
        "word": "streamline",
        "phonetic": "/ˈstriːm.laɪn/",
        "definition": "To make simpler and more efficient."
    }
    saved = service.save_word(sample_word)
    assert any(w["word"] == "streamline" for w in saved)

    updated = service.remove_saved_word("streamline")
    assert not any(w["word"] == "streamline" for w in updated)

    if os.path.exists(test_storage):
        os.remove(test_storage)

def test_drafter_offline_demo():
    service = DrafterService()
    result = service.draft_message(notes="Meeting on Friday 10am")
    assert "body" in result

def test_tone_refiner_offline_demo():
    service = ToneAnalyzerService()
    result = service.refine_tone("Hey, please check this out ASAP.")
    assert "refined_text" in result or "target_tone" in result

def test_reply_generator_offline_demo():
    service = ReplyAssistantService()
    result = service.generate_replies("Can you attend the demo tomorrow?")
    assert "options" in result
    assert len(result["options"]) > 0

def test_summarizer_offline_demo():
    service = SummarizerService()
    result = service.summarize_content("Discussed budget and launch date. Decided on Oct 1st.")
    assert "summary" in result
