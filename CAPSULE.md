# CAPSULE — Rolex AI Assistant
> Single source of truth for the Rolex project.
> Any AI or developer reading this can fully understand current state, goals, and history.
> Updated after every phase or significant change.

---

## Last Updated
**Timestamp:** 2026-05-24 06:00:00 UTC
**Version:** GUI Phase 1 — Orb + Chat Panel ✅ Complete

---

## Project Identity

| Field         | Value                                          |
|---------------|------------------------------------------------|
| Project Name  | Rolex                                          |
| Current Ver   | GUI Phase 1                                    |
| Platform      | Windows (VS Code)                              |
| Language      | Python 3.10+                                   |
| GUI Framework | PyQt6                                          |
| STT           | OpenAI Whisper — base model (local)            |
| LLM Brain     | Ollama — llama3.2 (local)                      |
| TTS           | Microsoft Edge TTS — en-US-GuyNeural           |
| Screen Vision | LLaVA via Ollama + Tesseract OCR               |
| Camera Vision | OpenCV webcam + LLaVA via Ollama               |
| Internet      | DuckDuckGo · wttr.in · Google News · Wikipedia · BS4 · YouTube |
| Cost          | 100% Free — no API keys, no subscriptions      |

---

## Project Structure

```
rolex/
├── CAPSULE.md
├── README.md
├── requirements.txt
├── .gitignore
└── src/
    ├── main.py          ← Entry point — launches GUI
    ├── listener.py      ← Mic + Whisper STT
    ├── brain.py         ← Ollama LLM + context injection
    ├── speaker.py       ← Edge TTS neural voice
    ├── vision.py        ← Screen: OCR + LLaVA + window + regions
    ├── camera.py        ← Webcam: OpenCV + LLaVA
    ├── internet.py      ← Web: search, weather, news, wiki, URL, YT
    └── gui/
        ├── __init__.py
        ├── app.py       ← Qt app, worker thread, signal wiring
        ├── orb.py       ← Floating animated orb widget
        ├── panel.py     ← Expanded chat panel
        ├── bubble.py    ← Individual message bubble widget
        └── theme.py     ← All colours, fonts, sizes
```

---

## GUI Architecture

```
Main thread                     Background thread (RolexWorker)
──────────────────              ───────────────────────────────
QApplication                    record_until_silence()
  │                             whisper.transcribe()
  ├── OrbWidget                 Brain.think()
  │     animations              Vision.process()
  │     click → toggle panel    Camera.look_and_answer()
  │                             Internet.process()
  └── ChatPanel                 Speaker.speak()
        bubbles                        │
        transcript bar                 │ Qt signals
        status bar          ←──────────┘
                            state_changed
                            transcript_ready
                            reply_ready
                            user_said
```

Heavy AI work runs on a background QThread.
UI only receives signals — never blocks, never freezes.

---

## Orb States & Colours

| State     | Colour  | Animation              | Trigger                  |
|-----------|---------|------------------------|--------------------------|
| idle      | Blue    | Slow gentle pulse      | Waiting for speech       |
| listening | Cyan    | Expanding ripple rings | Mic active               |
| thinking  | Silver  | Rotating arc spinner   | Whisper / Ollama working |
| speaking  | Green   | Concentric rings       | TTS playing              |
| web       | Orange  | Pulse                  | Internet request         |
| camera    | Purple  | Pulse                  | Webcam active            |
| vision    | Amber   | Pulse                  | Screen vision active     |
| error     | Red     | Single flash           | Any error                |

---

## Chat Panel

- Click orb → panel appears above it
- Click orb again or ✕ → panel hides
- Message bubbles: user (right, muted) · Rolex (left, dark card)
- Mode tag on every Rolex reply: 🧠 Brain · 🌐 Web · 📷 Camera · 👁 Vision · 📄 OCR
- Live transcript bar: shows speech in real time
- Status bar: dot + label matches current orb state

---

## Phase History

| Tag              | Phase                   | Status |
|------------------|-------------------------|--------|
| phase-1          | V1 Ears                 | ✅     |
| phase-2          | V1 Voice                | ✅     |
| phase-3          | V1 Eyes                 | ✅     |
| v2-phase-1       | Sharper Eyes            | ✅     |
| v2-phase-2       | Camera Eyes             | ✅     |
| v2-phase-3       | Internet                | ✅     |
| gui-phase-1      | Orb + Chat Panel        | ✅     |
| gui-phase-2      | Polish + Tray (planned) | ⏳     |

---

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

ollama pull llama3.2
ollama pull llava

ollama serve            # terminal 1
python src/main.py      # terminal 2
```

---

## GUI Phase 2 (Next)

- Smooth morph animation (orb stretches into panel)
- Drag orb to reposition anywhere on screen
- System tray icon — right-click to show/quit
- Startup on boot option
- Settings panel — voice, model, corner position

---

*Updated after every phase. Timestamp reflects last modification.*