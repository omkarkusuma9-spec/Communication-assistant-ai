# 🚀 Personal Communication Assistant & English Coach AI

Your private, AI-powered communication companion and English learning suite. Built with **FastAPI**, **Google Gemini**, and a modern web dashboard equipped with **Speech-to-Text** voice input and **Text-to-Speech** audio pronunciation.

---

## ✨ Features

### 🎓 1. English Coach & Grammar Explainer
- **Grammar & Preposition Fixing**: Detects tense inconsistencies, awkward prepositions, and grammatical errors.
- **Rule Explanations ("Why It Changed")**: Understand *why* each adjustment was made so you continuously learn and improve your language skills.
- **Dual Output**:
  - **Natural & Fluent**: Native, everyday phrasing.
  - **Advanced & Executive**: Sophisticated phrasing for formal presentations and high-stakes emails.
- **Vocabulary & Idiom Booster**: Contextual synonyms and idiomatic phrases with definitions and examples.
- **Voice Pronunciation**: Listen to the native audio of any corrected sentence with 1 click.

### 🎙️ 2. Chat & Speaking Practice (Interactive Roleplay)
- **Voice Speaking (Speech-to-Text)**: Click the microphone button and speak in English—your browser transcribes your speech in real time.
- **Listening (Text-to-Speech)**: Native audio playback for conversation partners and coach feedback.
- **Realistic Practice Scenarios**:
  - *Job Interview* (Practice answering common interview questions with poise)
  - *Workplace Meeting & Updates* (Giving project status updates and asking questions)
  - *Casual Coffee Chat & Small Talk* (Natural social banter, weekend plans)
  - *Polite Negotiation & Pushback* (Disagreeing diplomatically, negotiating deadlines)
  - *Casual Everyday English* (Everyday conversation with a supportive coach)
- **Inline Coaching Notes**: Every turn provides a partner response to keep the conversation flowing, alongside an instant **Coach Note** showing a more natural way to phrase your thoughts, grammar feedback, and a vocal speaking/intonation tip.

### 📚 3. Vocabulary Builder & Word Bank
- **Curated Topic Explorer**:
  - *Workplace & Leadership*
  - *Everyday Idioms & Phrasal Verbs*
  - *Casual Fluency & Social Small Talk*
  - *Persuasive & Diplomatic Language*
  - *Meetings & Negotiations*
- **Word Cards**: Phonetic guides (IPA), definitions, real-world examples, companion collocations, and audio pronunciation.
- **"Use It In A Sentence" Challenge**: Practice composing your own sentence using any target word. The AI instantly grades your sentence, explains usage nuances, and provides an elevated alternative.
- **Personal Word Bank**: Bookmark favorite words to review anytime.

### ✍️ 4. Smart Message & Email Drafter
- Turn quick bullet points or shorthand notes into structured, compelling emails, Slack/Teams messages, or announcements.
- Automatically adheres to your persona, default tone, and personal sign-off signature.

### 🔄 5. Tone Transformer
- Rewrite messages across 5 tones:
  - *Professional & Executive*
  - *Friendly & Warm*
  - *Assertive & Direct*
  - *Diplomatic & Empathetic*
  - *Ultra-Concise*
- Compare side-by-side alternative variations with audio playback.

### 💬 6. Quick Reply Generator
- Paste any incoming message or email to receive 3 distinct, strategic reply options:
  1. *Affirmative / Agree & Confirm*
  2. *Polite Decline / Reschedule*
  3. *Clarification / Request More Info*

### 📋 7. Thread & Meeting Summarizer
- Distill lengthy email chains, meeting notes, or chat discussions into a 3-part digest: **Overview**, **Key Takeaways**, and **Action Items** (with owners and priorities).

### ⚙️ 8. Personal Communication Profile
- Set your name, professional title, communication guidelines, and English proficiency level (*Beginner*, *Intermediate*, *Advanced*).

---

## 🛠️ Quickstart & Installation

### 1. Install Dependencies
Open your terminal in this directory (`f:/My_Ai`) and run:
```bash
pip install -r requirements.txt
```

### 2. Configure Your API Key (Optional but Recommended)
To enable live AI responses, obtain a free Google Gemini API key from [Google AI Studio](https://aistudio.google.com/).

You can configure it in one of two easy ways:
- **Option A (In the UI)**: Open the web dashboard, go to the **Persona & API** tab, paste your key, and click **Save Key**.
- **Option B (In `.env`)**: Copy `.env.example` to `.env` and set your key:
  ```env
  GEMINI_API_KEY=your_gemini_api_key_here
  GEMINI_MODEL=gemini-2.5-flash
  ```

*(Note: Even without an API key, the app runs in **Demo Mode** with simulated outputs so you can test all UI flows, speaking, audio, and vocabulary quizzes instantly!)*

### 3. Launch the Application
Start the server by running:
```bash
python app.py
```
or with Uvicorn:
```bash
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

### 4. Open in Your Browser
Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) to start practicing your speaking, chatting, and vocabulary!

---

## 📁 Project Structure

```
f:/My_Ai/
├── config/
│   ├── __init__.py
│   └── settings.py              # Configuration and environment variables
├── core/
│   ├── __init__.py
│   ├── llm.py                  # Gemini API client with fallback demo mode
│   ├── persona.py              # Persona management & persona.json persistence
│   └── prompts.py              # System instructions & prompts for all features
├── services/
│   ├── __init__.py
│   ├── english_coach.py        # Grammar analysis & vocabulary booster
│   ├── chat_practice.py        # Scenario roleplays & conversational coaching
│   ├── vocabulary_service.py   # Word cards, sentence challenge & word bank
│   ├── drafter.py              # Smart drafting engine
│   ├── tone_analyzer.py        # Tone rewriting and comparison
│   ├── reply_assistant.py      # Incoming message reply options
│   └── summarizer.py           # Thread & meeting notes summarizer
├── static/
│   ├── index.html              # Clean, modern single-page dashboard
│   ├── styles.css              # Custom styling, badges, animations & mic pulse
│   └── app.js                  # Frontend controller, Web Speech API & audio TTS
├── app.py                      # FastAPI application entry point
├── requirements.txt            # Python package dependencies
├── test_services.py            # Automated unit test suite
├── .env.example                # Environment variables template
└── README.md                   # Documentation & setup guide
```
