// Client-side controller for Communication Assistant & English Coach AI

const tabs = ['coach', 'chat', 'vocab', 'drafter', 'tone', 'reply', 'summarize', 'settings'];

function switchTab(tabName) {
  tabs.forEach(t => {
    const view = document.getElementById(`view-${t}`);
    const btn = document.getElementById(`tab-btn-${t}`);
    if (view && btn) {
      if (t === tabName) {
        view.classList.remove('hidden');
        btn.classList.add('bg-indigo-600', 'text-white', 'shadow-md');
        btn.classList.remove('text-slate-300', 'hover:bg-slate-800');
      } else {
        view.classList.add('hidden');
        btn.classList.remove('bg-indigo-600', 'text-white', 'shadow-md');
        btn.classList.add('text-slate-300', 'hover:bg-slate-800');
      }
    }
  });

  const titles = {
    coach: "🎓 English Coach & Grammar Explainer",
    chat: "🎙️ Chat & Speaking Roleplay Practice",
    vocab: "📚 Vocabulary Builder & Word Explorer",
    drafter: "✍️ Smart Message & Email Drafter",
    tone: "🔄 Tone Transformer",
    reply: "💬 Quick Reply Generator",
    summarize: "📋 Thread & Meeting Summarizer",
    settings: "⚙️ Persona & API Settings"
  };
  document.getElementById('page-title').innerText = titles[tabName] || "Communication AI";

  if (tabName === 'chat' && chatHistory.length === 0) {
    initChatConversation();
  }
  if (tabName === 'vocab' && !currentVocabTopic) {
    loadVocabTopics();
  }
}

// Toast helper
function showToast(message, isSuccess = true) {
  const toast = document.getElementById('toast');
  const msgEl = document.getElementById('toast-message');
  const icon = document.getElementById('toast-icon');

  msgEl.innerText = message;
  icon.className = isSuccess
    ? 'fa-solid fa-check text-emerald-400'
    : 'fa-solid fa-circle-exclamation text-amber-400';

  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
  }, 2800);
}

// Copy to clipboard helper
function copyToClipboard(elementIdOrText) {
  let text = '';
  const el = document.getElementById(elementIdOrText);
  if (el) {
    text = el.innerText || el.value;
  } else {
    try {
      text = decodeURIComponent(elementIdOrText);
    } catch {
      text = elementIdOrText;
    }
  }

  if (!text) {
    showToast("Nothing to copy", false);
    return;
  }

  navigator.clipboard.writeText(text).then(() => {
    showToast("Copied to clipboard!");
  }).catch(() => {
    showToast("Failed to copy", false);
  });
}

// ----------------------------------------------------
// AUDIO & SPEECH ENGINE (Web Speech API STT & TTS)
// ----------------------------------------------------
let activeRecognition = null;
let activeMicButton = null;

function toggleSpeechRecognition(targetInputId, buttonEl) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    showToast("Speech recognition is not supported in this browser. Try Chrome or Edge.", false);
    return;
  }

  if (activeRecognition) {
    activeRecognition.stop();
    activeRecognition = null;
    if (activeMicButton) {
      activeMicButton.classList.remove('mic-active');
      activeMicButton = null;
    }
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.lang = 'en-US';
  recognition.continuous = false;
  recognition.interimResults = false;

  recognition.onstart = () => {
    activeRecognition = recognition;
    activeMicButton = buttonEl;
    if (buttonEl) buttonEl.classList.add('mic-active');
    showToast("Listening... Speak in English now.");
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    const inputEl = document.getElementById(targetInputId);
    if (inputEl) {
      inputEl.value = inputEl.value ? `${inputEl.value} ${transcript}` : transcript;
      inputEl.focus();
    }
    showToast("Speech captured!");
  };

  recognition.onerror = (event) => {
    console.warn("Speech recognition error:", event.error);
    showToast("Mic note: " + event.error, false);
  };

  recognition.onend = () => {
    if (activeMicButton) {
      activeMicButton.classList.remove('mic-active');
    }
    activeRecognition = null;
    activeMicButton = null;
  };

  recognition.start();
}

function speakText(text, rate = 0.95) {
  if (!('speechSynthesis' in window)) {
    showToast("Text-to-Speech not supported in your browser.", false);
    return;
  }

  window.speechSynthesis.cancel(); // Stop any ongoing speech
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'en-US';
  utterance.rate = rate;

  const voices = window.speechSynthesis.getVoices();
  const enVoice = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('Samantha')));
  if (enVoice) {
    utterance.voice = enVoice;
  }

  window.speechSynthesis.speak(utterance);
}

function speakElementText(elementId) {
  const el = document.getElementById(elementId);
  if (el) {
    speakText(el.innerText || el.value);
  }
}

// ----------------------------------------------------
// STATUS & PERSONA MANAGEMENT
// ----------------------------------------------------
async function checkStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    const badge = document.getElementById('engine-status-badge');
    const modelText = document.getElementById('engine-model-text');

    if (data.api_key_configured) {
      badge.innerText = "🟢 Live AI";
      badge.className = "px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-300";
    } else {
      badge.innerText = "🟡 Demo Mode";
      badge.className = "px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/20 text-amber-300 cursor-pointer";
      badge.title = "Click Settings tab to enter your Gemini API key";
    }
    modelText.innerText = `Model: ${data.model}`;
  } catch (err) {
    console.error("Status check failed:", err);
  }
}

async function loadPersona() {
  try {
    const res = await fetch('/api/persona');
    const data = await res.json();
    
    document.getElementById('persona-name').value = data.user_name || '';
    document.getElementById('persona-role').value = data.role_title || '';
    document.getElementById('persona-level').value = data.english_level || 'Intermediate';
    document.getElementById('persona-tone').value = data.default_tone || 'Professional & Friendly';
    document.getElementById('persona-signature').value = data.signature || '';
    document.getElementById('persona-rules').value = (data.custom_rules || []).join('\n');

    document.getElementById('coach-level-display').innerText = data.english_level || 'Intermediate';
    document.getElementById('user-greeting').innerText = data.user_name ? `Hi, ${data.user_name}` : 'Welcome!';
  } catch (err) {
    console.error("Load persona failed:", err);
  }
}

async function savePersona() {
  const payload = {
    user_name: document.getElementById('persona-name').value.trim() || 'User',
    role_title: document.getElementById('persona-role').value.trim() || 'Professional',
    english_level: document.getElementById('persona-level').value,
    default_tone: document.getElementById('persona-tone').value,
    signature: document.getElementById('persona-signature').value.trim(),
    custom_rules: document.getElementById('persona-rules').value
      .split('\n')
      .map(r => r.trim())
      .filter(r => r.length > 0)
  };

  try {
    const res = await fetch('/api/persona', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      showToast("Profile & English Level saved!");
      loadPersona();
    } else {
      showToast("Failed to save profile", false);
    }
  } catch (err) {
    showToast("Network error saving profile", false);
  }
}

async function saveApiKey() {
  const key = document.getElementById('settings-api-key').value.trim();
  if (!key) {
    showToast("Please enter an API key", false);
    return;
  }

  try {
    const res = await fetch('/api/settings/key', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ api_key: key })
    });
    const data = await res.json();
    if (res.ok) {
      showToast("Gemini API Key activated!");
      document.getElementById('settings-api-key').value = '';
      checkStatus();
    } else {
      showToast(data.detail || "Error saving key", false);
    }
  } catch (err) {
    showToast("Failed to connect to server", false);
  }
}

// ----------------------------------------------------
// 1. ENGLISH COACH (Grammar & Writing)
// ----------------------------------------------------
function fillCoachSample(sampleText) {
  document.getElementById('coach-input').value = sampleText;
}

async function runEnglishCoach() {
  const text = document.getElementById('coach-input').value.trim();
  const focus = document.getElementById('coach-focus').value;

  if (!text) {
    showToast("Please enter a sentence or message to review.", false);
    return;
  }

  const placeholder = document.getElementById('coach-placeholder');
  const loading = document.getElementById('coach-loading');
  const results = document.getElementById('coach-results');

  placeholder.classList.add('hidden');
  results.classList.add('hidden');
  loading.classList.remove('hidden');

  try {
    const res = await fetch('/api/english-coach', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, focus_area: focus })
    });

    const data = await res.json();
    loading.classList.add('hidden');
    results.classList.remove('hidden');

    document.getElementById('coach-natural-text').innerText = data.corrected_natural || text;
    document.getElementById('coach-advanced-text').innerText = data.advanced_professional || data.corrected_natural || text;

    const encText = document.getElementById('coach-encouragement-text');
    if (data.coach_encouragement) {
      encText.innerText = data.coach_encouragement;
      document.getElementById('coach-encouragement-card').classList.remove('hidden');
    } else {
      document.getElementById('coach-encouragement-card').classList.add('hidden');
    }

    const corrContainer = document.getElementById('coach-corrections-list');
    corrContainer.innerHTML = '';
    const corrections = data.corrections || [];

    if (corrections.length === 0) {
      corrContainer.innerHTML = `
        <div class="p-3 bg-emerald-50 text-emerald-800 rounded-xl text-sm flex items-center gap-2">
          <i class="fa-solid fa-circle-check text-emerald-600"></i>
          <span>Great job! No major grammatical errors detected. Your message is clear and natural.</span>
        </div>`;
    } else {
      corrections.forEach(c => {
        const item = document.createElement('div');
        item.className = 'p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-1.5';
        item.innerHTML = `
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700 uppercase tracking-wider">
              ${c.rule_type || 'Grammar'}
            </span>
          </div>
          <div class="text-sm font-medium flex items-center gap-2 flex-wrap">
            <span class="line-through text-rose-500 bg-rose-50 px-2 py-0.5 rounded">${c.original || ''}</span>
            <i class="fa-solid fa-arrow-right text-xs text-slate-400"></i>
            <span class="text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded font-semibold">${c.replacement || ''}</span>
          </div>
          <p class="text-xs text-slate-600 mt-1">${c.explanation || ''}</p>
        `;
        corrContainer.appendChild(item);
      });
    }

    const vocabContainer = document.getElementById('coach-vocab-list');
    vocabContainer.innerHTML = '';
    const vocabList = data.vocabulary_boost || [];

    if (vocabList.length === 0) {
      document.getElementById('coach-vocab-card').classList.add('hidden');
    } else {
      document.getElementById('coach-vocab-card').classList.remove('hidden');
      vocabList.forEach(v => {
        const card = document.createElement('div');
        card.className = 'p-3 bg-purple-50/70 border border-purple-100 rounded-xl space-y-1';
        card.innerHTML = `
          <div class="flex items-center justify-between">
            <span class="font-bold text-sm text-purple-900">${v.word_or_phrase || ''}</span>
            <button onclick="speakText('${encodeURIComponent(v.word_or_phrase || '')}')" class="btn-speaker text-purple-500 hover:text-purple-800 text-xs"><i class="fa-solid fa-volume-high"></i></button>
          </div>
          <p class="text-xs text-purple-700">${v.meaning || ''}</p>
          <div class="text-[11px] italic text-purple-600 pt-1 border-t border-purple-100">"${v.example || ''}"</div>
        `;
        vocabContainer.appendChild(card);
      });
    }

  } catch (err) {
    loading.classList.add('hidden');
    placeholder.classList.remove('hidden');
    showToast("Error analyzing English: " + err.message, false);
  }
}

// ----------------------------------------------------
// 2. CHAT & SPEAKING PRACTICE (Roleplay)
// ----------------------------------------------------
let chatHistory = [];

const SCENARIO_GREETINGS = {
  "Job Interview": "Hello! Welcome to our interview. It's a pleasure to connect with you today. Could you briefly introduce yourself and tell me what brings you to this role?",
  "Workplace Meeting & Updates": "Hi there! Thanks for joining today's project check-in. Could you share a quick status update on what you've been working on?",
  "Coffee Chat & Small Talk": "Hey! Great to see you. How has your week been treating you so far?",
  "Polite Negotiation & Pushback": "Hello. Regarding the deadline we discussed earlier—the leadership team is requesting we deliver it 3 days earlier. How does that look from your side?",
  "Casual Daily English": "Hey friend! How's your day going? Doing anything fun today?"
};

function initChatConversation() {
  const scenario = document.getElementById('chat-scenario-select').value;
  chatHistory = [];
  const container = document.getElementById('chat-messages-container');
  container.innerHTML = '';

  const initialGreeting = SCENARIO_GREETINGS[scenario] || "Hello! How can I help you practice today?";
  
  // Add partner greeting
  chatHistory.push({ role: 'partner', text: initialGreeting });
  renderPartnerBubble(initialGreeting, null);

  const autoSpeak = document.getElementById('chat-auto-tts').checked;
  if (autoSpeak) {
    speakText(initialGreeting);
  }
}

function resetChatConversation() {
  initChatConversation();
}

function toggleChatMic() {
  const micBtn = document.getElementById('chat-mic-btn');
  toggleSpeechRecognition('chat-user-input', micBtn);
}

function handleChatInputKeyDown(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    sendChatMessage();
  }
}

async function sendChatMessage() {
  const inputEl = document.getElementById('chat-user-input');
  const userText = inputEl.value.trim();
  const scenario = document.getElementById('chat-scenario-select').value;

  if (!userText) return;

  inputEl.value = '';
  renderUserBubble(userText);
  chatHistory.push({ role: 'user', text: userText });

  const container = document.getElementById('chat-messages-container');
  const loadingIndicator = document.createElement('div');
  loadingIndicator.id = 'chat-loading-turn';
  loadingIndicator.className = 'text-xs text-slate-400 italic flex items-center gap-1.5 py-2';
  loadingIndicator.innerHTML = '<i class="fa-solid fa-circle-notch animate-spin text-rose-500"></i> Partner is typing...';
  container.appendChild(loadingIndicator);
  container.scrollTop = container.scrollHeight;

  try {
    const res = await fetch('/api/chat-practice', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        scenario: scenario,
        history: chatHistory,
        user_message: userText
      })
    });
    const data = await res.json();

    const loader = document.getElementById('chat-loading-turn');
    if (loader) loader.remove();

    const partnerReply = data.partner_reply || "I see. Tell me more.";
    chatHistory.push({ role: 'partner', text: partnerReply });

    renderPartnerBubble(partnerReply, data.coach_feedback);

    const autoSpeak = document.getElementById('chat-auto-tts').checked;
    if (autoSpeak) {
      speakText(partnerReply);
    }
  } catch (err) {
    const loader = document.getElementById('chat-loading-turn');
    if (loader) loader.remove();
    showToast("Chat error: " + err.message, false);
  }
}

function renderUserBubble(text) {
  const container = document.getElementById('chat-messages-container');
  const wrap = document.createElement('div');
  wrap.className = 'flex justify-end animate-fade-in';
  wrap.innerHTML = `
    <div class="max-w-[80%] chat-bubble-user p-3.5 rounded-2xl shadow-sm text-sm">
      <p class="whitespace-pre-line">${text}</p>
    </div>
  `;
  container.appendChild(wrap);
  container.scrollTop = container.scrollHeight;
}

function renderPartnerBubble(partnerReply, coachFeedback) {
  const container = document.getElementById('chat-messages-container');
  const wrap = document.createElement('div');
  wrap.className = 'space-y-2 max-w-[85%] animate-fade-in';

  let coachHtml = '';
  if (coachFeedback) {
    coachHtml = `
      <div class="chat-coach-note p-3 rounded-xl border border-emerald-200 text-xs space-y-1.5 shadow-xs">
        <div class="flex items-center justify-between">
          <span class="font-bold text-emerald-800 uppercase text-[10px] tracking-wider flex items-center gap-1">
            <i class="fa-solid fa-graduation-cap"></i> Coach Note
          </span>
          <span class="text-[10px] text-emerald-700">${coachFeedback.has_corrections ? 'Tweak suggested' : '✅ Clear phrasing'}</span>
        </div>
        <p class="text-slate-700"><strong>Grammar:</strong> ${coachFeedback.grammar_check || 'Looks great!'}</p>
        ${coachFeedback.more_natural_way ? `
          <div class="flex items-start justify-between gap-2 pt-1 border-t border-emerald-100">
            <p class="text-slate-800"><strong>More Natural:</strong> "${coachFeedback.more_natural_way}"</p>
            <button onclick="speakText('${encodeURIComponent(coachFeedback.more_natural_way)}')" class="btn-speaker text-emerald-600 hover:text-emerald-800 flex-shrink-0" title="Listen"><i class="fa-solid fa-volume-high"></i></button>
          </div>
        ` : ''}
        ${coachFeedback.speaking_tip ? `
          <p class="text-emerald-900 text-[11px] pt-1"><i class="fa-solid fa-microphone-lines text-emerald-600"></i> <em>Speaking tip: ${coachFeedback.speaking_tip}</em></p>
        ` : ''}
      </div>
    `;
  }

  wrap.innerHTML = `
    <div class="chat-bubble-partner p-4 rounded-2xl shadow-sm space-y-2">
      <div class="flex items-center justify-between text-xs text-slate-400 border-b border-slate-100 pb-1.5">
        <span class="font-bold text-slate-700 flex items-center gap-1.5">
          <i class="fa-solid fa-user text-indigo-500"></i> Partner
        </span>
        <button onclick="speakText('${encodeURIComponent(partnerReply)}')" class="btn-speaker text-slate-500 hover:text-rose-600 flex items-center gap-1" title="Listen to partner">
          <i class="fa-solid fa-volume-high"></i> Listen
        </button>
      </div>
      <p class="text-slate-800 text-sm leading-relaxed">${partnerReply}</p>
    </div>
    ${coachHtml}
  `;

  container.appendChild(wrap);
  container.scrollTop = container.scrollHeight;
}

// ----------------------------------------------------
// 3. VOCABULARY BUILDER & WORD EXPLORER
// ----------------------------------------------------
let currentVocabTopic = '';
let activeChallengeWord = '';

async function loadVocabTopics() {
  try {
    const res = await fetch('/api/vocabulary/topics');
    const data = await res.json();
    const container = document.getElementById('vocab-topic-chips');
    container.innerHTML = '';

    (data.topics || []).forEach((topic, idx) => {
      const chip = document.createElement('button');
      chip.className = `px-3.5 py-1.5 rounded-xl text-xs font-semibold transition border ${
        idx === 0
          ? 'bg-amber-500 text-slate-900 border-amber-500 shadow-sm'
          : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-amber-50 hover:border-amber-300'
      }`;
      chip.innerText = topic;
      chip.onclick = () => selectVocabTopic(topic, chip);
      container.appendChild(chip);
    });

    if (data.topics && data.topics.length > 0) {
      selectVocabTopic(data.topics[0], container.children[0]);
    }
    loadSavedWordsCount();
  } catch (err) {
    console.error("Failed to load vocab topics:", err);
  }
}

async function selectVocabTopic(topic, activeBtnEl) {
  currentVocabTopic = topic;
  const container = document.getElementById('vocab-topic-chips');
  Array.from(container.children).forEach(btn => {
    btn.className = 'px-3.5 py-1.5 rounded-xl text-xs font-semibold transition border bg-slate-50 text-slate-700 border-slate-200 hover:bg-amber-50 hover:border-amber-300';
  });
  if (activeBtnEl) {
    activeBtnEl.className = 'px-3.5 py-1.5 rounded-xl text-xs font-semibold transition border bg-amber-500 text-slate-900 border-amber-500 shadow-sm';
  }

  const grid = document.getElementById('vocab-cards-grid');
  const loading = document.getElementById('vocab-loading');
  grid.innerHTML = '';
  loading.classList.remove('hidden');

  try {
    const res = await fetch('/api/vocabulary/words', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic })
    });
    const data = await res.json();
    loading.classList.add('hidden');

    (data.words || []).forEach(w => {
      const card = document.createElement('div');
      card.className = 'vocab-card bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between space-y-3';
      
      const collocationsHtml = (w.collocations || []).map(c => `<span class="bg-slate-100 text-slate-700 text-[10px] font-medium px-2 py-0.5 rounded">${c}</span>`).join(' ');

      card.innerHTML = `
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="font-bold text-lg text-slate-900">${w.word}</span>
              <button onclick="speakText('${encodeURIComponent(w.word)}')" class="btn-speaker text-amber-500 hover:text-amber-700 text-sm" title="Listen to pronunciation"><i class="fa-solid fa-volume-high"></i></button>
            </div>
            <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 uppercase">${w.part_of_speech || 'word'}</span>
          </div>

          <p class="text-xs text-slate-500 font-mono">${w.phonetic || ''}</p>
          <p class="text-xs text-slate-700 font-medium">${w.definition || ''}</p>

          <div class="p-2.5 bg-slate-50 border border-slate-100 rounded-xl space-y-1">
            <div class="flex items-center justify-between text-[11px] text-slate-400">
              <span class="font-semibold uppercase tracking-wider text-[9px]">Example:</span>
              <button onclick="speakText('${encodeURIComponent(w.example || '')}')" class="btn-speaker text-slate-400 hover:text-amber-600"><i class="fa-solid fa-volume-high"></i></button>
            </div>
            <p class="text-xs text-slate-800 italic">"${w.example || ''}"</p>
          </div>

          ${collocationsHtml ? `<div class="pt-1 flex flex-wrap gap-1 items-center"><span class="text-[10px] text-slate-400 font-semibold mr-1">Pairs with:</span> ${collocationsHtml}</div>` : ''}
        </div>

        <div class="pt-2 border-t border-slate-100 flex items-center justify-between gap-2">
          <button onclick='saveVocabWord(${JSON.stringify(w).replace(/'/g, "&apos;")})' class="text-xs text-slate-500 hover:text-amber-600 font-medium flex items-center gap-1 px-2.5 py-1.5 rounded-lg hover:bg-amber-50 transition">
            <i class="fa-regular fa-bookmark"></i> Save
          </button>
          <button onclick="openSentenceChallenge('${w.word}')" class="text-xs bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-semibold px-3 py-1.5 rounded-xl transition flex items-center gap-1.5">
            <i class="fa-solid fa-pen-fancy"></i> Practice in Sentence
          </button>
        </div>
      `;
      grid.appendChild(card);
    });
  } catch (err) {
    loading.classList.add('hidden');
    showToast("Error loading vocabulary: " + err.message, false);
  }
}

function openSentenceChallenge(word) {
  activeChallengeWord = word;
  const section = document.getElementById('vocab-challenge-section');
  document.getElementById('challenge-target-word').innerText = word;
  document.getElementById('challenge-sentence-input').value = '';
  document.getElementById('challenge-feedback-card').classList.add('hidden');
  section.classList.remove('hidden');
  section.scrollIntoView({ behavior: 'smooth' });
}

function closeChallengeSection() {
  document.getElementById('vocab-challenge-section').classList.add('hidden');
}

async function submitSentenceChallenge() {
  const sentence = document.getElementById('challenge-sentence-input').value.trim();
  if (!sentence) {
    showToast("Please enter a sentence first.", false);
    return;
  }

  const submitBtn = document.getElementById('challenge-submit-btn');
  const feedbackCard = document.getElementById('challenge-feedback-card');
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<i class="fa-solid fa-circle-notch animate-spin"></i> Evaluating...';

  try {
    const res = await fetch('/api/vocabulary/practice', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        target_word: activeChallengeWord,
        sentence: sentence
      })
    });
    const data = await res.json();
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Evaluate My Sentence';

    feedbackCard.classList.remove('hidden');
    const isGood = data.is_correct;
    feedbackCard.className = isGood
      ? 'p-4 rounded-xl space-y-2 border bg-emerald-50 border-emerald-200'
      : 'p-4 rounded-xl space-y-2 border bg-amber-50 border-amber-200';

    feedbackCard.innerHTML = `
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold uppercase tracking-wider ${isGood ? 'text-emerald-800' : 'text-amber-800'}">
          ${isGood ? '✅ Accurate Usage' : '⚠️ Refinement Needed'} • ${data.accuracy_rating || ''}
        </span>
        <button onclick="speakText('${encodeURIComponent(data.suggested_improvement || sentence)}')" class="btn-speaker text-xs ${isGood ? 'text-emerald-600' : 'text-amber-600'} flex items-center gap-1">
          <i class="fa-solid fa-volume-high"></i> Listen
        </button>
      </div>
      <p class="text-xs ${isGood ? 'text-emerald-900' : 'text-amber-900'}">${data.feedback || ''}</p>
      ${data.suggested_improvement ? `
        <div class="pt-2 border-t border-slate-200/50">
          <span class="text-[10px] font-bold uppercase tracking-wider text-slate-500 block">Polished native alternative:</span>
          <p class="text-xs text-slate-800 font-medium">"${data.suggested_improvement}"</p>
        </div>
      ` : ''}
      <p class="text-[11px] italic text-slate-500 pt-1">${data.encouragement || ''}</p>
    `;
  } catch (err) {
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Evaluate My Sentence';
    showToast("Evaluation error: " + err.message, false);
  }
}

async function saveVocabWord(wordObj) {
  try {
    const res = await fetch('/api/vocabulary/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ word_data: wordObj })
    });
    if (res.ok) {
      showToast(`'${wordObj.word}' saved to your Word Bank!`);
      loadSavedWordsCount();
    }
  } catch (err) {
    showToast("Failed to save word", false);
  }
}

async function loadSavedWordsCount() {
  try {
    const res = await fetch('/api/vocabulary/saved');
    const data = await res.json();
    const count = (data.saved_words || []).length;
    document.getElementById('saved-words-count').innerText = count;
  } catch (err) {
    console.error("Count load error:", err);
  }
}

async function openSavedWordsModal() {
  const modal = document.getElementById('saved-words-modal');
  const list = document.getElementById('saved-words-list');
  list.innerHTML = '<div class="py-8 text-center text-slate-400 text-xs">Loading saved words...</div>';
  modal.classList.remove('hidden');

  try {
    const res = await fetch('/api/vocabulary/saved');
    const data = await res.json();
    const saved = data.saved_words || [];

    if (saved.length === 0) {
      list.innerHTML = '<div class="py-12 text-center text-slate-400 text-sm">No saved words yet. Bookmark words from the topic cards to review here!</div>';
      return;
    }

    list.innerHTML = '';
    saved.forEach(w => {
      const item = document.createElement('div');
      item.className = 'p-3.5 bg-slate-50 border border-slate-200 rounded-xl flex items-start justify-between gap-3';
      item.innerHTML = `
        <div class="space-y-1">
          <div class="flex items-center gap-2">
            <span class="font-bold text-sm text-slate-900">${w.word}</span>
            <span class="text-[10px] text-slate-400 font-mono">${w.phonetic || ''}</span>
            <button onclick="speakText('${encodeURIComponent(w.word)}')" class="btn-speaker text-amber-500 hover:text-amber-700 text-xs"><i class="fa-solid fa-volume-high"></i></button>
          </div>
          <p class="text-xs text-slate-600">${w.definition || ''}</p>
          <p class="text-[11px] italic text-slate-500">"${w.example || ''}"</p>
        </div>
        <button onclick="deleteSavedWord('${w.word}')" class="text-slate-400 hover:text-rose-600 text-xs p-1" title="Remove"><i class="fa-solid fa-trash-can"></i></button>
      `;
      list.appendChild(item);
    });
  } catch (err) {
    list.innerHTML = '<div class="py-4 text-center text-rose-500 text-xs">Failed to load saved words.</div>';
  }
}

function closeSavedWordsModal() {
  document.getElementById('saved-words-modal').classList.add('hidden');
}

async function deleteSavedWord(wordName) {
  try {
    const res = await fetch(`/api/vocabulary/save/${encodeURIComponent(wordName)}`, {
      method: 'DELETE'
    });
    if (res.ok) {
      showToast(`Removed '${wordName}'`);
      openSavedWordsModal();
      loadSavedWordsCount();
    }
  } catch (err) {
    showToast("Error removing word", false);
  }
}

// ----------------------------------------------------
// 4. SMART DRAFTER
// ----------------------------------------------------
async function runDrafter() {
  const notes = document.getElementById('drafter-notes').value.trim();
  const message_type = document.getElementById('drafter-type').value;
  const tone = document.getElementById('drafter-tone').value;
  const recipient_context = document.getElementById('drafter-recipient').value.trim();

  if (!notes) {
    showToast("Please provide bullet points or notes to draft.", false);
    return;
  }

  const loading = document.getElementById('drafter-loading');
  const resultArea = document.getElementById('drafter-result-area');
  loading.classList.remove('hidden');
  resultArea.classList.add('opacity-40');

  try {
    const res = await fetch('/api/draft', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ notes, message_type, tone, recipient_context })
    });
    const data = await res.json();
    loading.classList.add('hidden');
    resultArea.classList.remove('opacity-40');

    if (data.subject) {
      document.getElementById('drafter-subject-output').innerText = data.subject;
      document.getElementById('drafter-subject-container').classList.remove('hidden');
    } else {
      document.getElementById('drafter-subject-container').classList.add('hidden');
    }

    document.getElementById('drafter-body-output').innerText = data.body || '';

    const tipsContainer = document.getElementById('drafter-tips-container');
    const tipsList = document.getElementById('drafter-tips-list');
    tipsList.innerHTML = '';
    if (data.communication_tips && data.communication_tips.length > 0) {
      data.communication_tips.forEach(t => {
        const li = document.createElement('li');
        li.innerText = t;
        tipsList.appendChild(li);
      });
      tipsContainer.classList.remove('hidden');
    } else {
      tipsContainer.classList.add('hidden');
    }

    showToast("Draft ready!");
  } catch (err) {
    loading.classList.add('hidden');
    resultArea.classList.remove('opacity-40');
    showToast("Drafting error: " + err.message, false);
  }
}

// ----------------------------------------------------
// 5. TONE TRANSFORMER
// ----------------------------------------------------
async function runToneRefiner() {
  const text = document.getElementById('tone-input').value.trim();
  const target_tone = document.getElementById('tone-target').value;

  if (!text) {
    showToast("Please paste the message you want to transform.", false);
    return;
  }

  const loading = document.getElementById('tone-loading');
  const container = document.getElementById('tone-result-container');
  loading.classList.remove('hidden');
  container.classList.add('opacity-40');

  try {
    const res = await fetch('/api/refine-tone', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, target_tone })
    });
    const data = await res.json();
    loading.classList.add('hidden');
    container.classList.remove('opacity-40');

    document.getElementById('tone-output-text').innerText = data.refined_text || '';

    const altContainer = document.getElementById('tone-alternatives-container');
    const altList = document.getElementById('tone-alternatives-list');
    altList.innerHTML = '';

    if (data.alternative_versions && data.alternative_versions.length > 0) {
      data.alternative_versions.forEach(alt => {
        const card = document.createElement('div');
        card.className = 'p-3 bg-white border border-slate-200 rounded-xl space-y-1 shadow-sm';
        card.innerHTML = `
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-purple-700">${alt.tone_name}</span>
            <div class="flex items-center gap-1.5">
              <button onclick="speakText('${encodeURIComponent(alt.text)}')" class="btn-speaker text-[11px] text-slate-400 hover:text-purple-600"><i class="fa-solid fa-volume-high"></i></button>
              <button onclick="copyToClipboard('${encodeURIComponent(alt.text)}')" class="text-[11px] text-slate-500 hover:text-purple-600">Copy</button>
            </div>
          </div>
          <p class="text-xs text-slate-700">${alt.text}</p>
        `;
        altList.appendChild(card);
      });
      altContainer.classList.remove('hidden');
    } else {
      altContainer.classList.add('hidden');
    }

    showToast("Tone transformed!");
  } catch (err) {
    loading.classList.add('hidden');
    container.classList.remove('opacity-40');
    showToast("Error transforming tone: " + err.message, false);
  }
}

// ----------------------------------------------------
// 6. QUICK REPLY GENERATOR
// ----------------------------------------------------
async function runReplyGenerator() {
  const incoming = document.getElementById('reply-incoming').value.trim();
  const intent = document.getElementById('reply-intent').value.trim();

  if (!incoming) {
    showToast("Please paste the incoming message.", false);
    return;
  }

  const loading = document.getElementById('reply-loading');
  const grid = document.getElementById('reply-options-grid');
  loading.classList.remove('hidden');
  grid.innerHTML = '';

  try {
    const res = await fetch('/api/reply', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ incoming_message: incoming, user_intent_notes: intent })
    });
    const data = await res.json();
    loading.classList.add('hidden');

    (data.options || []).forEach(opt => {
      const card = document.createElement('div');
      card.className = 'bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between space-y-3 hover:border-blue-300 transition';
      card.innerHTML = `
        <div>
          <div class="flex items-center justify-between mb-2">
            <span class="font-bold text-sm text-slate-800">${opt.title || 'Response'}</span>
            <span class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700">${opt.tone || 'Option'}</span>
          </div>
          <p class="text-xs text-slate-700 whitespace-pre-line leading-relaxed">${opt.body || ''}</p>
        </div>
        <div class="flex items-center gap-2 pt-2 border-t border-slate-100">
          <button onclick="speakText('${encodeURIComponent(opt.body || '')}')" class="btn-speaker p-2 bg-slate-50 hover:bg-blue-50 text-slate-500 hover:text-blue-700 border border-slate-200 rounded-xl text-xs transition" title="Listen">
            <i class="fa-solid fa-volume-high"></i>
          </button>
          <button onclick="copyToClipboard('${encodeURIComponent(opt.body || '')}')" class="flex-1 py-2 bg-slate-50 hover:bg-blue-50 text-slate-700 hover:text-blue-700 border border-slate-200 rounded-xl text-xs font-semibold transition flex items-center justify-center gap-1.5">
            <i class="fa-regular fa-copy"></i> Copy Reply
          </button>
        </div>
      `;
      grid.appendChild(card);
    });

    showToast("Generated 3 options!");
  } catch (err) {
    loading.classList.add('hidden');
    showToast("Error generating replies: " + err.message, false);
  }
}

// ----------------------------------------------------
// 7. SUMMARIZER
// ----------------------------------------------------
async function runSummarizer() {
  const content = document.getElementById('summarize-content').value.trim();
  if (!content) {
    showToast("Please paste content to summarize.", false);
    return;
  }

  const loading = document.getElementById('summarize-loading');
  const results = document.getElementById('summarize-results');
  loading.classList.remove('hidden');
  results.classList.add('opacity-40');

  try {
    const res = await fetch('/api/summarize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content })
    });
    const data = await res.json();
    loading.classList.add('hidden');
    results.classList.remove('opacity-40');

    document.getElementById('summarize-overview').innerText = data.summary || '';

    const takeawaysEl = document.getElementById('summarize-takeaways');
    takeawaysEl.innerHTML = '';
    (data.key_takeaways || []).forEach(t => {
      const li = document.createElement('li');
      li.innerText = t;
      takeawaysEl.appendChild(li);
    });

    const actionsEl = document.getElementById('summarize-actions');
    actionsEl.innerHTML = '';
    (data.action_items || []).forEach(a => {
      const item = document.createElement('div');
      item.className = 'p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs flex items-center justify-between';
      item.innerHTML = `
        <span class="font-medium text-slate-800">${a.task}</span>
        <span class="px-2 py-0.5 rounded text-[10px] font-bold ${a.priority === 'High' ? 'bg-rose-100 text-rose-700' : 'bg-slate-200 text-slate-700'}">${a.assignee || 'Unassigned'} • ${a.priority || 'Normal'}</span>
      `;
      actionsEl.appendChild(item);
    });

    showToast("Summary created!");
  } catch (err) {
    loading.classList.add('hidden');
    results.classList.remove('opacity-40');
    showToast("Summarizer error: " + err.message, false);
  }
}

// Initialize on page load
window.addEventListener('DOMContentLoaded', () => {
  checkStatus();
  loadPersona();
});
