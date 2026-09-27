import json
import os
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List

class UserPersona(BaseModel):
    user_name: str = Field(default="Friend", description="User's display or communication name")
    role_title: str = Field(default="Professional", description="Current profession or role")
    default_tone: str = Field(default="Professional & Friendly", description="Default communication tone")
    signature: str = Field(default="Best regards,\n{user_name}", description="Sign-off template")
    custom_rules: List[str] = Field(
        default_factory=lambda: [
            "Keep sentences clear and natural",
            "Avoid overly complex corporate jargon",
            "Be polite, constructive, and action-oriented"
        ],
        description="Personal style instructions"
    )
    english_level: str = Field(
        default="Intermediate",
        description="User's current English proficiency level: Beginner, Intermediate, or Advanced"
    )

class PersonaManager:
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            storage_path = "/tmp/persona.json" if os.getenv("VERCEL") else "persona.json"
        self.storage_path = Path(storage_path)
        self._persona = self._load()

    def _load(self) -> UserPersona:
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return UserPersona(**data)
            except Exception:
                return UserPersona()
        return UserPersona()

    def get_persona(self) -> UserPersona:
        return self._persona

    def update_persona(self, updated: UserPersona) -> UserPersona:
        self._persona = updated
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self._persona.model_dump(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save persona to disk: {e}")
        return self._persona

# Global singleton instance
persona_manager = PersonaManager()
