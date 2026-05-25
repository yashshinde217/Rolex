# CAPSULE — Rolex AI Assistant
> Single source of truth for the Rolex project.
> Any AI or developer reading this can fully understand current state, goals, and history.
> Updated after every phase or significant change.

---

## Last Updated
**Timestamp:** 2026-05-24 03:00:00 UTC
**Version:** V2 | **Phase:** Phase 1 — Sharper Eyes ✅ Complete

---

## Project Identity

| Field        | Value                                          |
|--------------|------------------------------------------------|
| Project Name | Rolex                                          |
| Current Ver  | V2 Phase 1                                     |
| Platform     | Windows (VS Code)                              |
| Language     | Python 3.10+                                   |
| STT          | OpenAI Whisper — base model (local)            |
| LLM Brain    | Ollama — llama3.2 (local)                      |
| TTS          | Microsoft Edge TTS — en-US-GuyNeural (neural)  |
| Vision       | LLaVA via Ollama + Tesseract OCR (local)       |
| Cost         | 100% Free — all models run locally, no API keys |

---

## V1 Powers (Complete)

| Power    | Capability                              | Status |
|----------|-----------------------------------------|--------|
| Hearing  | Mic → Whisper STT → transcript          | ✅     |
| Speaking | LLaMA brain → Edge TTS neural voice     | ✅     |
| Seeing   | Screenshot → LLaVA → description        | ✅     |

## V2 Upgrades

| Phase | Name          | Capability                                      | Status |
|-------|---------------|-------------------------------------------------|--------|
| 1     | Sharper Eyes  | OCR + active window + region + smarter prompts  | ✅     |
| 2     | Camera Eyes   | Webcam → LLaVA → real-world vision              | ⏳     |
| 3     | Internet      | Web search, page reader, news, weather          | ⏳     |

---

## Tech Stack

| Layer          | Tool                    | Purpose                                  |
|----------------|-------------------------|------------------------------------------|
| STT            | OpenAI Whisper (local)  | Mic audio → text                         |
| LLM            | Ollama + llama3.2       | Reasoning, conversation                  |
| TTS            | Edge TTS GuyNeural      | Neural voice output                      |
| Screen Vision  | LLaVA via Ollama        | Understand screen layout & content       |
| OCR            | Tesseract + pytesseract | Read text from screen precisely          |
| Window Capture | pygetwindow             | Capture active window only               |
| Screenshot     | Pillow ImageGrab        | Full screen / region capture             |
| Audio          | sounddevice + soundfile | Mic input and TTS playback               |
| HTTP           | requests                | Ollama API calls                         |
| Version Ctrl   | Git                     | Full history, phase tags                 |

---

## Project Structure

```
rolex/
├── CAPSULE.md
├── README.md
├── requirements.txt
├── .gitignore
└── src/
    ├── listener.py   — Mic + Whisper STT
    ├── brain.py      — Ollama LLM + history
    ├── speaker.py    — Edge TTS neural voice
    ├── vision.py     — V2: OCR + LLaVA + active window + regions
    └── main.py       — Unified loop, dual-path vision routing
```

---

## Vision Routing Logic (V2 Phase 1)

```
User speaks
    │
    ├─ "read the error" / "read this" / "what does it say"
    │       └─→ OCR path (Tesseract) — fast, precise text extraction
    │
    └─ "look at my screen" / "what do you see" / "describe my screen"
            └─→ LLaVA path — understands layout, context, UI
```

Both paths support:
- Full screen (default)
- Active window ("this window", "current app")
- Region crop ("top half", "bottom right", "left side", "center")

---

## Voice Commands

| Say...                              | Effect                                    |
|-------------------------------------|-------------------------------------------|
| "look at my screen"                 | LLaVA describes full screen               |
| "read the error"                    | OCR reads text precisely                  |
| "describe the top half"             | LLaVA looks at top half only             |
| "read this window"                  | OCR on active window only                 |
| "what's on the right side"          | LLaVA on right region                    |
| "exit" / "quit"                     | Shut down                                 |
| "clear history" / "start over"      | Reset conversation memory                 |

---

## Phase History

### V1 Phase 1 — Ears | Date: 2026-05-24 | ✅ Tested
Mic + Whisper STT. Git tag: `phase-1`

### V1 Phase 2 — Voice | Date: 2026-05-24 | ✅ Tested
Ollama LLM + Edge TTS neural voice. Git tag: `phase-2`
Bugfix: pyttsx3 → Edge TTS (robotic → neural)

### V1 Phase 3 — Eyes | Date: 2026-05-24 | ✅ Tested
LLaVA screenshot vision. Git tag: `phase-3`

### V2 Phase 1 — Sharper Eyes | Date: 2026-05-24 | ✅ Complete
- Dual-path vision: OCR (text) vs LLaVA (understanding)
- Active window capture via pygetwindow
- Region capture: top/bottom/left/right/center
- Higher resolution pipeline (quality 92, max 1920px)
- OCR image pre-processing: upscale 2x, sharpen, contrast boost
- Smarter LLaVA prompt with explicit instructions
- Graceful fallback if Tesseract not installed
- main.py shows [Eyes:OCR] or [Eyes:LLAVA] per response
- Git tag: `v2-phase-1`

### V2 Phase 2 — Camera Eyes | ⏳ Not started
Webcam capture → LLaVA. Real-world vision.

### V2 Phase 3 — Internet | ⏳ Not started
DuckDuckGo search, page reader, weather, news.

---

## Setup — Full (Windows)

```bash
# Python environment
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Ollama models (one time)
ollama pull llama3.2    # ~2GB
ollama pull llava       # ~4GB

# Tesseract OCR (one time, optional but recommended)
# Download: https://github.com/UB-Mannheim/tesseract/wiki

# Run
ollama serve            # keep open in terminal 1
python src/main.py      # terminal 2
```

---

## Future (V2 Phase 2+)

- Webcam → LLaVA (real-world vision)
- DuckDuckGo web search
- Live webpage reading
- Weather, news, Wikipedia
- Smart routing: local vs internet

---

*Updated after every phase. Timestamp reflects last modification.*