# CAPSULE — Rolex AI Assistant
> Single source of truth for the Rolex project.
> Any AI or developer reading this can fully understand current state, goals, and history.
> Updated after every phase or significant change.

---

## Last Updated
**Timestamp:** 2026-05-24 04:00:00 UTC
**Version:** V2 | **Phase:** Phase 2 — Camera Eyes ✅ Complete

---

## Project Identity

| Field        | Value                                          |
|--------------|------------------------------------------------|
| Project Name | Rolex                                          |
| Current Ver  | V2 Phase 2                                     |
| Platform     | Windows (VS Code)                              |
| Language     | Python 3.10+                                   |
| STT          | OpenAI Whisper — base model (local)            |
| LLM Brain    | Ollama — llama3.2 (local)                      |
| TTS          | Microsoft Edge TTS — en-US-GuyNeural           |
| Screen Vision| LLaVA via Ollama + Tesseract OCR (local)       |
| Camera Vision| OpenCV webcam + LLaVA via Ollama (local)       |
| Cost         | 100% Free — all models run locally, no API keys|

---

## Capabilities

| Power         | Capability                                       | Status |
|---------------|--------------------------------------------------|--------|
| Hearing       | Mic → Whisper STT → transcript                   | ✅ V1  |
| Speaking      | LLaMA → Edge TTS neural voice                    | ✅ V1  |
| Screen Vision | Screenshot → OCR or LLaVA → answer              | ✅ V1  |
| Sharper Eyes  | Active window, region crop, dual-path routing    | ✅ V2.1|
| Camera Eyes   | Webcam frame → LLaVA → real-world understanding  | ✅ V2.2|
| Internet      | Web search, page reader, news, weather           | ⏳ V2.3|

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
| Camera Capture | OpenCV (cv2)            | Webcam frame capture                     |
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
    ├── brain.py      — Ollama LLM + conversation history
    ├── speaker.py    — Edge TTS neural voice
    ├── vision.py     — Screen: OCR + LLaVA + active window + regions
    ├── camera.py     — Webcam: OpenCV capture + LLaVA (NEW)
    └── main.py       — Unified loop, three-way routing
```

---

## Routing Logic (V2 Phase 2)

```
User speaks
    │
    ├─ camera trigger  ("look at me", "scan this", "what's in front")
    │       └─→ OpenCV webcam frame → LLaVA → answer
    │
    ├─ screen trigger  ("look at my screen", "read the error")
    │       ├─ OCR trigger  → Tesseract text extraction
    │       └─ vision trigger → LLaVA screen understanding
    │
    └─ everything else → Ollama LLaMA brain → answer
```

Camera takes routing priority over screen vision if both triggers match.

---

## Voice Commands

| Say...                              | Routes to         | Effect                          |
|-------------------------------------|-------------------|---------------------------------|
| "look at me"                        | Camera            | Webcam → LLaVA                  |
| "scan this"                         | Camera            | Webcam → LLaVA                  |
| "what's in front of you"            | Camera            | Webcam → LLaVA                  |
| "can you see me"                    | Camera            | Webcam → LLaVA                  |
| "look at my screen"                 | Screen / LLaVA    | Screenshot → LLaVA              |
| "read the error"                    | Screen / OCR      | Screenshot → Tesseract          |
| "describe the top half"             | Screen / LLaVA    | Cropped screenshot → LLaVA      |
| "exit" / "quit"                     | Control           | Shut down                       |
| "clear history" / "start over"      | Control           | Reset conversation memory       |

---

## Phase History

### V1 Phase 1 — Ears | ✅ | tag: phase-1
### V1 Phase 2 — Voice | ✅ | tag: phase-2
### V1 Phase 3 — Eyes | ✅ | tag: phase-3
### V2 Phase 1 — Sharper Eyes | ✅ | tag: v2-phase-1
OCR + active window + region crop + smarter LLaVA prompts

### V2 Phase 2 — Camera Eyes | ✅ Complete | tag: v2-phase-2
- New file: `src/camera.py`
  - OpenCV webcam capture (configurable camera index)
  - WARMUP_FRAMES (5) discarded so exposure stabilises before capture
  - HD resolution request (1280×720)
  - Structured LLaVA prompt for real-world context
  - Graceful error if no webcam found
- `main.py` updated: three-way routing (camera > screen > brain)
  - Camera shown in purple [Camera] in terminal
  - Camera answers stored in brain history for follow-ups
  - Graceful fallback if opencv not installed
- `requirements.txt`: added opencv-python

### V2 Phase 3 — Internet | ⏳ Not started
DuckDuckGo search, page reader, weather, news, Wikipedia, YouTube summary.

---

## Setup — Full (Windows)

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Ollama models (one time)
ollama pull llama3.2
ollama pull llava

# Tesseract (optional, for OCR)
# https://github.com/UB-Mannheim/tesseract/wiki

# Run
ollama serve            # terminal 1
python src/main.py      # terminal 2
```

---

*Updated after every phase. Timestamp reflects last modification.*