import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from config.settings import get_settings
from core.llm import llm_service
from core.persona import persona_manager, UserPersona
from services.english_coach import english_coach_service
from services.chat_practice import chat_practice_service
from services.vocabulary_service import vocabulary_service
from services.drafter import drafter_service
from services.tone_analyzer import tone_analyzer_service
from services.reply_assistant import reply_assistant_service
from services.summarizer import summarizer_service

app = FastAPI(
    title="Communication Assistant & English Coach AI",
    description="Your personal assistant for professional communication, speaking practice, and English mastery.",
    version="1.1.0"
)

# Static directory setup
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Request Models
class EnglishCoachRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to analyze and improve")
    focus_area: Optional[str] = Field("Grammar & Natural Fluency", description="Area to focus on")

class ChatPracticeRequest(BaseModel):
    scenario: str = Field(..., description="Scenario name")
    history: List[Dict[str, str]] = Field(default_factory=list, description="Past conversation turns")
    user_message: str = Field(..., min_length=1, description="Latest message from user")

class VocabTopicRequest(BaseModel):
    topic: str = Field(..., description="Selected vocabulary topic")

class VocabSentencePracticeRequest(BaseModel):
    target_word: str = Field(..., description="Target vocabulary word")
    sentence: str = Field(..., min_length=1, description="User's practice sentence")

class VocabSaveRequest(BaseModel):
    word_data: Dict[str, Any] = Field(..., description="Word card object to save")

class DraftRequest(BaseModel):
    notes: str = Field(..., min_length=1, description="Raw bullet points or draft notes")
    message_type: str = Field("Email", description="Type of message (Email, Slack, Update, etc.)")
    tone: Optional[str] = Field(None, description="Target tone")
    recipient_context: Optional[str] = Field(None, description="Audience context")

class ToneRefineRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Message to refine")
    target_tone: str = Field("Professional & Executive", description="Desired tone")

class ReplyRequest(BaseModel):
    incoming_message: str = Field(..., min_length=1, description="Incoming message")
    user_intent_notes: Optional[str] = Field(None, description="Specific thoughts or instructions")

class SummarizeRequest(BaseModel):
    content: str = Field(..., min_length=1, description="Thread or notes to summarize")

class ApiKeyUpdateRequest(BaseModel):
    api_key: str = Field(..., min_length=1, description="Google Gemini API key")

# Routes
@app.get("/")
def serve_index():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return JSONResponse({"status": "API online", "message": "Static index.html not yet built."})

@app.get("/api/status")
def get_status():
    settings = get_settings()
    configured = llm_service.is_configured()
    return {
        "status": "online",
        "api_key_configured": configured,
        "model": settings.gemini_model,
        "mode": "Live AI" if configured else "Demo / Offline Mode"
    }

@app.post("/api/settings/key")
def update_api_key(req: ApiKeyUpdateRequest):
    key = req.api_key.strip()
    if not key:
        raise HTTPException(status_code=400, detail="API key cannot be empty.")
    
    settings = get_settings()
    settings.gemini_api_key = key
    
    # Save to .env file for persistence
    env_file = Path(__file__).parent / ".env"
    try:
        lines = []
        if env_file.exists():
            with open(env_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
        
        key_found = False
        new_lines = []
        for line in lines:
            if line.startswith("GEMINI_API_KEY="):
                new_lines.append(f"GEMINI_API_KEY={key}\n")
                key_found = True
            else:
                new_lines.append(line)
        if not key_found:
            new_lines.append(f"\nGEMINI_API_KEY={key}\n")
            
        with open(env_file, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
    except Exception as e:
        print(f"Warning: Could not write .env file: {e}")

    return {"status": "success", "message": "API key updated successfully!", "mode": "Live AI"}

@app.get("/api/persona")
def get_persona():
    return persona_manager.get_persona()

@app.post("/api/persona")
def update_persona(persona: UserPersona):
    saved = persona_manager.update_persona(persona)
    return {"status": "success", "persona": saved}

@app.post("/api/english-coach")
def improve_english(req: EnglishCoachRequest):
    try:
        result = english_coach_service.analyze_and_improve(req.text, req.focus_area)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Interactive Chat Practice & Speaking
@app.post("/api/chat-practice")
def chat_practice(req: ChatPracticeRequest):
    try:
        result = chat_practice_service.continue_conversation(
            scenario=req.scenario,
            history=req.history,
            user_message=req.user_message
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Vocabulary Builder & Word Bank
@app.get("/api/vocabulary/topics")
def get_vocab_topics():
    return {"topics": vocabulary_service.get_topics()}

@app.post("/api/vocabulary/words")
def get_vocab_words(req: VocabTopicRequest):
    try:
        return vocabulary_service.get_words_for_topic(req.topic)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/vocabulary/practice")
def practice_vocab_sentence(req: VocabSentencePracticeRequest):
    try:
        return vocabulary_service.evaluate_practice_sentence(req.target_word, req.sentence)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/vocabulary/saved")
def get_saved_words():
    return {"saved_words": vocabulary_service.get_saved_words()}

@app.post("/api/vocabulary/save")
def save_word(req: VocabSaveRequest):
    updated = vocabulary_service.save_word(req.word_data)
    return {"status": "success", "saved_words": updated}

@app.delete("/api/vocabulary/save/{word_name}")
def delete_saved_word(word_name: str):
    updated = vocabulary_service.remove_saved_word(word_name)
    return {"status": "success", "saved_words": updated}

# Communication Drafter, Tone, Reply, Summarize
@app.post("/api/draft")
def draft_message(req: DraftRequest):
    try:
        result = drafter_service.draft_message(
            notes=req.notes,
            message_type=req.message_type,
            tone=req.tone,
            recipient_context=req.recipient_context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/refine-tone")
def refine_tone(req: ToneRefineRequest):
    try:
        result = tone_analyzer_service.refine_tone(req.text, req.target_tone)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reply")
def generate_replies(req: ReplyRequest):
    try:
        result = reply_assistant_service.generate_replies(req.incoming_message, req.user_intent_notes)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/summarize")
def summarize(req: SummarizeRequest):
    try:
        result = summarizer_service.summarize_content(req.content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run("app:app", host=settings.host, port=settings.port, reload=settings.debug)
