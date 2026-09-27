import json
import logging
import urllib.request
import urllib.error
from typing import Optional, Dict, Any
from config.settings import get_settings

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.settings = get_settings()

    @property
    def api_key(self) -> str:
        return self.settings.gemini_api_key

    @property
    def model_name(self) -> str:
        return self.settings.gemini_model or "gemini-2.5-flash"

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip() and self.api_key != "your_gemini_api_key_here")

    def generate(self, prompt: str, system_instruction: Optional[str] = None, json_mode: bool = False) -> str:
        """Generates content using the Gemini API. Falls back to smart mock if not configured."""
        if not self.is_configured():
            logger.info("Gemini API key not set; falling back to demo mode response.")
            return self._demo_response(prompt, json_mode)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        
        payload: Dict[str, Any] = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 2048,
            }
        }

        if json_mode:
            payload["generationConfig"]["responseMimeType"] = "application/json"

        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        try:
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=req_data,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
                
                candidates = result.get("candidates", [])
                if not candidates:
                    raise RuntimeError("No generation candidates returned from Gemini.")
                
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                if not parts:
                    raise RuntimeError("Empty response content from Gemini.")
                
                return parts[0].get("text", "")

        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8")
            logger.error(f"Gemini API HTTP Error {e.code}: {err_msg}")
            raise RuntimeError(f"Gemini API Error ({e.code}): {err_msg}")
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            raise RuntimeError(f"Failed to communicate with Gemini API: {str(e)}")

    def _demo_response(self, prompt: str, json_mode: bool) -> str:
        """Provides rich, realistic demo outputs when no API key is provided."""
        lower_prompt = prompt.lower()
        if json_mode:
            if "roleplay" in lower_prompt or "conversation partner" in lower_prompt or "scenario" in lower_prompt:
                return json.dumps({
                    "partner_reply": "That's a very interesting point! In our team, we always value clear updates and initiative. How do you plan to handle the next milestone?",
                    "coach_feedback": {
                        "has_corrections": True,
                        "grammar_check": "Your message was clear! Minor check: ensure your verb tenses remain consistent when describing past actions.",
                        "more_natural_way": "You could also say: 'I'd love to walk you through our recent progress on this project.'",
                        "vocabulary_tip": "Try using the phrase 'spearhead an initiative' to describe leading a task.",
                        "speaking_tip": "When speaking this aloud, pause briefly before your key proposal to build anticipation."
                    }
                })
            elif "target vocabulary word" in lower_prompt or "evaluating a user's practice sentence" in lower_prompt:
                return json.dumps({
                    "target_word": "collaborate",
                    "is_correct": True,
                    "accuracy_rating": "Excellent",
                    "feedback": "You used the word accurately with a natural preposition ('collaborate with'). The sentence conveys your message effectively.",
                    "suggested_improvement": "To make it even punchier, you can say: 'Our teams frequently collaborate on product releases.'",
                    "encouragement": "Superb work! Using new vocabulary in your own sentences is the fastest way to master it."
                })
            elif "vocabulary curator" in lower_prompt or "words, idioms, or phrasal verbs" in lower_prompt:
                return json.dumps({
                    "topic": "Workplace Communication",
                    "words": [
                        {
                            "word": "collaborate",
                            "phonetic": "/kəˈlæb.ə.reɪt/",
                            "part_of_speech": "verb",
                            "definition": "To work jointly with others on an activity or project.",
                            "example": "We need to collaborate closely with the design team before launch.",
                            "collocations": ["collaborate closely", "collaborate with", "collaborate on a project"],
                            "when_to_use": "Use when discussing teamwork and cross-functional efforts."
                        },
                        {
                            "word": "touch base",
                            "phonetic": "/tʌtʃ beɪs/",
                            "part_of_speech": "idiom / phrasal verb",
                            "definition": "To briefly make contact or communicate with someone to check in.",
                            "example": "Let's touch base on Thursday to review our deliverables.",
                            "collocations": ["touch base with someone", "touch base later"],
                            "when_to_use": "Great for quick, friendly workplace check-ins without sounding overly formal."
                        },
                        {
                            "word": "streamline",
                            "phonetic": "/ˈstriːm.laɪn/",
                            "part_of_speech": "verb",
                            "definition": "To make a system or organization more efficient and simpler.",
                            "example": "We adopted this new tool to streamline our email communication.",
                            "collocations": ["streamline processes", "streamline workflow", "streamline operations"],
                            "when_to_use": "Ideal for business proposals, presentations, and process improvements."
                        },
                        {
                            "word": "on the same page",
                            "phonetic": "/ɒn ðə seɪm peɪdʒ/",
                            "part_of_speech": "idiom",
                            "definition": "Having the same understanding or agreement about a topic.",
                            "example": "I wanted to call a quick meeting to ensure we are all on the same page.",
                            "collocations": ["get on the same page", "stay on the same page"],
                            "when_to_use": "Essential for alignment in meetings and project handovers."
                        },
                        {
                            "word": "proactive",
                            "phonetic": "/prəʊˈæk.tɪv/",
                            "part_of_speech": "adjective",
                            "definition": "Controlling a situation rather than just reacting to it after it happens.",
                            "example": "Taking a proactive approach to communication prevents misunderstandings.",
                            "collocations": ["proactive approach", "proactive steps", "proactive communication"],
                            "when_to_use": "Use in job interviews, performance reviews, and status reports."
                        }
                    ]
                })
            elif "coach" in lower_prompt or "grammar" in lower_prompt or "english" in lower_prompt:
                return json.dumps({
                    "original_text": "Sample text provided for English improvement.",
                    "corrected_natural": "Here is the natural, grammatically polished version of your sentence.",
                    "advanced_professional": "Here is an executive-level, articulate phrasing of your thoughts.",
                    "corrections": [
                        {
                            "original": "sample phrase",
                            "replacement": "improved phrase",
                            "explanation": "Corrected tense agreement and selected a more natural preposition for fluent English.",
                            "rule_type": "Grammar & Preposition"
                        }
                    ],
                    "vocabulary_boost": [
                        {
                            "word_or_phrase": "collaborate effectively",
                            "meaning": "work together smoothly toward a common goal",
                            "example": "We can collaborate effectively on this upcoming launch."
                        }
                    ],
                    "coach_encouragement": "Great foundation! Keep practicing your prepositions and sentence structure. Connect your Gemini API key in settings for real-time personalized analysis on your exact sentences."
                })
            elif "reply" in lower_prompt:
                return json.dumps({
                    "sender_intent_summary": "The sender is asking for an update or scheduling confirmation.",
                    "options": [
                        {
                            "title": "Positive & Confirming",
                            "tone": "Warm & Enthusiastic",
                            "body": "Hi there,\n\nThanks for reaching out! Everything is right on track. I'd be glad to confirm this and coordinate the next steps.\n\nBest regards,\n[Your Name]"
                        },
                        {
                            "title": "Polite Decline / Reschedule",
                            "tone": "Professional & Diplomatic",
                            "body": "Hi,\n\nThank you for the note. Unfortunately, I have a conflict at that time, but I would be happy to connect later this week or discuss asynchronously.\n\nBest regards,\n[Your Name]"
                        },
                        {
                            "title": "Need More Information",
                            "tone": "Direct & Inquiring",
                            "body": "Hi,\n\nThanks for the update. Could you please share a few additional details or context regarding the agenda before we proceed?\n\nBest,\n[Your Name]"
                        }
                    ]
                })
            elif "summar" in lower_prompt:
                return json.dumps({
                    "summary": "Demo summary: Key discussions centered around project timelines, communication improvements, and setting up the AI assistant.",
                    "key_takeaways": [
                        "The assistant helps both with message composition and English language improvement.",
                        "Direct feedback on grammar, idioms, and natural tone boosts daily fluency."
                    ],
                    "action_items": [
                        {"task": "Configure GEMINI_API_KEY in .env file or Settings UI", "assignee": "User", "priority": "High"},
                        {"task": "Try drafting an email or checking a sentence in the English Coach", "assignee": "User", "priority": "Medium"}
                    ]
                })
            else:
                return json.dumps({
                    "subject": "Quick Update: Project Milestones",
                    "body": "Hi team,\n\nI wanted to share a quick update regarding our project progress. Everything is proceeding smoothly, and we look forward to the upcoming review.\n\nPlease let me know if you have any questions.\n\nBest regards,\n[Your Name]",
                    "tips": ["Tip: Add your Gemini API key in Settings to generate custom drafts tailored specifically to your prompt."]
                })
        else:
            return (
                "[Demo Mode] Here is your simulated AI response. "
                "To get live, personalized AI responses, enter your free Gemini API key in the Settings tab or in your .env file."
            )

llm_service = LLMService()
