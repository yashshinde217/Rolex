# CAPSULE — Rolex AI Assistant
> This file is the single source of truth for the Rolex project.
> Any AI or developer reading this can fully understand the project's current state, goals, and history.
> Updated after every phase or significant change.

---

## Last Updated
**Timestamp:** 2026-05-24 01:00:00 UTC
**Phase:** Phase 2 — Voice (Speaking) ✅ Complete

---

## Project Identity

| Field        | Value                              |
|--------------|------------------------------------|
| Project Name | Rolex                              |
| Version      | V1                                 |
| Platform     | Windows (VS Code)                  |
| Language     | Python 3.10+                       |
| AI Brain     | Ollama — llama3.2 (local LLM)      |
| STT          | OpenAI Whisper — base model (local)|
| TTS          | pyttsx3 — Windows SAPI5 (offline)  |
| Vision       | LLaVA via Ollama — Phase 3         |
| Cost         | 100% Free — all models run locally, no API keys |
| Developer    | Solo project                       |

---

## Vision

Build a personal AI assistant named Rolex that runs entirely on the user's local machine — no cloud, no API costs, no subscriptions. Inspired by Jarvis (Iron Man). The assistant can hear, speak, and see. Eventually it will control the laptop and browse the internet autonomously.

---

## V1 Scope — Three Core Powers

| Power    | Capability                                 | Status      |
|----------|--------------------------------------------|-------------|
| Hearing  | Listen via microphone, transcribe speech   | ✅ Phase 1  |
| Speaking | Think via LLM, reply via TTS               | ✅ Phase 2  |
| Seeing   | Capture screen, understand visually        | ⏳ Phase 3  |

---

## Tech Stack

| Layer            | Tool / Library         | Purpose                              |
|------------------|------------------------|--------------------------------------|
| Speech-to-Text   | OpenAI Whisper (local) | Convert mic audio to text            |
| LLM Brain        | Ollama + LLaMA 3.2     | Local language model for reasoning   |
| Text-to-Speech   | pyttsx3 (SAPI5)        | Natural voice output, fully offline  |
| Vision           | LLaVA (via Ollama)     | Understand screenshots — Phase 3     |
| Audio Capture    | sounddevice + scipy    | Mic input, WAV recording             |
| HTTP Client      | requests               | Talk to Ollama's local API           |
| Backend          | Python 3.10+           | Core runtime                         |
| Version Control  | Git                    | Full history from day one            |

---

## Project Structure

```
rolex/
├── CAPSULE.md              ← You are here. Living project PRD.
├── README.md               ← Setup and run instructions
├── requirements.txt        ← All Python dependencies
├── .gitignore              ← Files excluded from git
├── src/
│   ├── listener.py         ← Phase 1: Mic input + Whisper STT
│   ├── brain.py            ← Phase 2: Ollama LLM integration ✅
│   ├── speaker.py          ← Phase 2: pyttsx3 TTS voice output ✅
│   ├── vision.py           ← Phase 3: Screenshot + LLaVA vision
│   └── main.py             ← Phase 2: Full loop entry point ✅
├── assets/                 ← Voice models, config files
└── logs/                   ← Session transcripts and debug logs
```

---

## How to Run

### Phase 1 only (listen + print)
```bash
python src/listener.py
```

### Phase 2 — Full conversation loop (current)
```bash
# Prerequisites: Ollama must be running
ollama serve          # in a separate terminal
ollama pull llama3.2  # one-time download ~2GB

# Then run Rolex
python src/main.py
```

---

## Phase History

### Phase 1 — Ears (Listening)
**Date:** 2026-05-24
**Status:** ✅ Complete & Tested

- Full project scaffolding (folders, git, .gitignore, requirements.txt)
- `src/listener.py` — mic capture, energy-based VAD, Whisper STT
- CAPSULE.md + README.md created
- **Git tag:** `phase-1`

---

### Phase 2 — Voice (Speaking)
**Date:** 2026-05-24
**Status:** ✅ Complete

**What was built:**
- `src/brain.py` — Ollama HTTP client with full conversation history. Uses llama3.2 by default. Handles connection errors gracefully. Keeps session context so Rolex remembers within a conversation.
- `src/speaker.py` — pyttsx3 TTS using Windows SAPI5. Auto-selects best voice (prefers Zira/David). No downloads needed — uses built-in Windows voices.
- `src/main.py` — Full conversation loop: listen → transcribe → think → speak → repeat. ASCII boot screen. Voice commands: say "exit" to quit, "clear history" to reset context.
- `requirements.txt` updated with `requests` and `pyttsx3`
- `CAPSULE.md` updated

**Voice commands:**
| Say...                          | Effect                        |
|---------------------------------|-------------------------------|
| "exit" / "quit" / "goodbye"     | Shuts Rolex down              |
| "clear history" / "start over"  | Wipes conversation memory     |

**Git tag:** `phase-2`

---

### Phase 3 — Eyes (Seeing)
**Date:** TBD
**Status:** ⏳ Not started

**Planned:**
- Screenshot capture (Pillow / pyautogui)
- LLaVA vision model via Ollama
- "What's on my screen?" capability
- Vision integrated into main conversation loop

---

## Key Decisions & Notes

- **Why fully local?** Zero cost, privacy, no internet dependency for core features.
- **Why pyttsx3 over Piper?** pyttsx3 uses Windows built-in voices — zero setup, works immediately. Piper gives better quality and can be swapped in later.
- **Why llama3.2?** Good reasoning, fast on mid-range hardware. Can switch to `mistral` in brain.py config if preferred.
- **Why requests over ollama SDK?** Fewer dependencies, easier to debug, Ollama's REST API is simple.
- **Conversation memory:** Full history sent each turn so Rolex remembers context. History can be cleared with voice command or `brain.clear_history()`.
- **Git strategy:** Each phase gets a commit + tag. Rollback is always one command away.

---

## Environment Setup (Windows)

```bash
# 1. Install Python 3.10+ from python.org
# 2. Install Ollama from https://ollama.com/download
# 3. Open project in VS Code
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 4. Pull the LLM (one time, ~2GB)
ollama pull llama3.2

# 5. Start Ollama in a terminal (keep it running)
ollama serve

# 6. Run Rolex
python src/main.py
```

---

## Future Phases (Post V1)

| Phase | Feature                        |
|-------|-------------------------------|
| V2    | Computer control (PyAutoGUI)  |
| V2    | Web search (DuckDuckGo)       |
| V2    | Persistent memory (ChromaDB)  |
| V3    | Browser automation (Playwright)|
| V3    | File & app management         |
| V3    | Custom wake word ("Hey Rolex")|

---

*This capsule is updated by the developer or AI assistant after each phase or significant change. Timestamp reflects last modification.*
