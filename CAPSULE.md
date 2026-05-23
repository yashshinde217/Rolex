# CAPSULE — Rolex AI Assistant
> This file is the single source of truth for the Rolex project.
> Any AI or developer reading this can fully understand the project's current state, goals, and history.
> Updated after every phase or significant change.

---

## Last Updated
**Timestamp:** 2026-05-24 00:00:00 UTC
**Phase:** Phase 1 — Ears (Listening) ✅ Complete

---

## Project Identity

| Field        | Value                              |
|--------------|------------------------------------|
| Project Name | Rolex                              |
| Version      | V1                                 |
| Platform     | Windows (VS Code)                  |
| Language     | Python 3.10+                       |
| AI Model     | Whisper (STT) · Ollama LLM · Piper TTS · LLaVA (Vision) |
| Cost         | 100% Free — all models run locally, no API keys, no subscriptions |
| Developer    | Solo project                       |

---

## Vision

Build a personal AI assistant named Rolex that runs entirely on the user's local machine — no cloud, no API costs, no subscriptions. Inspired by Jarvis (Iron Man). The assistant should be able to hear, speak, and see. Eventually it will control the laptop and browse the internet autonomously.

---

## V1 Scope — Three Core Powers

| Power    | Capability                                 | Status      |
|----------|--------------------------------------------|-------------|
| Hearing  | Listen via microphone, transcribe speech   | ✅ Phase 1  |
| Speaking | Think via LLM, reply via TTS               | ⏳ Phase 2  |
| Seeing   | Capture screen, understand visually        | ⏳ Phase 3  |

---

## Tech Stack

| Layer            | Tool / Library         | Purpose                              |
|------------------|------------------------|--------------------------------------|
| Speech-to-Text   | OpenAI Whisper (local) | Convert mic audio to text            |
| LLM Brain        | Ollama + LLaMA 3 / Mistral | Local language model for reasoning |
| Text-to-Speech   | Piper TTS              | Natural voice output, runs offline   |
| Vision           | LLaVA (via Ollama)     | Understand screenshots visually      |
| Audio Capture    | sounddevice + scipy    | Mic input, WAV recording             |
| VAD              | webrtcvad              | Voice Activity Detection             |
| Vector Memory    | ChromaDB               | Persistent memory across sessions    |
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
│   ├── speaker.py          ← Phase 2: Piper TTS voice output
│   ├── brain.py            ← Phase 2: Ollama LLM integration
│   ├── vision.py           ← Phase 3: Screenshot + LLaVA vision
│   └── main.py             ← Entry point, ties all phases together
├── assets/                 ← Voice models, config files
└── logs/                   ← Session transcripts and debug logs
```

---

## Phase History

### Phase 1 — Ears (Listening)
**Date:** 2026-05-24
**Goal:** Rolex can hear you and transcribe speech to text.

**What was built:**
- Full project scaffolding (folders, git, .gitignore, requirements.txt)
- `src/listener.py` — captures mic audio using `sounddevice`, detects voice activity via energy threshold, records until silence, saves to a temp WAV, then transcribes with OpenAI Whisper (local `base` model)
- `README.md` — full setup instructions for Windows + VS Code
- This `CAPSULE.md`

**How to run Phase 1:**
```bash
python src/listener.py
```
Expected output: Rolex prints exactly what you said in the terminal.

**Git tag:** `phase-1`

---

### Phase 2 — Voice (Speaking)
**Date:** TBD
**Status:** ⏳ Not started

**Planned:**
- Ollama integration (local LLM)
- Piper TTS voice output
- Full conversation loop (listen → think → speak)

---

### Phase 3 — Eyes (Seeing)
**Date:** TBD
**Status:** ⏳ Not started

**Planned:**
- Screenshot capture
- LLaVA vision model via Ollama
- "What's on my screen?" capability

---

## Key Decisions & Notes

- **Why fully local?** Zero cost, privacy, no internet dependency for core features.
- **Why Whisper `base` model?** Good balance of speed and accuracy for a first version. Can upgrade to `small` or `medium` later for better accuracy.
- **Why sounddevice over pyaudio?** Easier Windows installation, no PortAudio DLL issues.
- **Voice Activity Detection approach:** Energy-threshold based (no extra VAD library dependency for Phase 1). Can switch to `webrtcvad` in a later version for more precision.
- **Git strategy:** Each phase gets a commit + tag. Rollback is always one command away.

---

## Environment Setup (Windows)

```bash
# 1. Install Python 3.10+ from python.org
# 2. Clone / open project in VS Code
# 3. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Whisper will auto-download the model on first run (~140MB for base)
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
