# Rolex — Personal AI Assistant

> Your local Jarvis. Hears you. Speaks back. Sees your screen. Runs 100% free on your machine.

---

## Current Version: V1 — Phase 1 (Ears)

Rolex can currently listen to your voice and transcribe what you say.

---

## Requirements

- Windows 10/11
- Python 3.10 or higher → [Download](https://python.org)
- VS Code → [Download](https://code.visualstudio.com)
- Microphone

---

## Setup

```bash
# 1. Open this folder in VS Code

# 2. Open the terminal (Ctrl + `) and create a virtual environment
python -m venv venv

# 3. Activate it
venv\Scripts\activate

# 4. Install all dependencies
pip install -r requirements.txt
```

> On first run, Whisper will automatically download the `base` model (~140 MB). This only happens once.

---

## Run — Phase 1

```bash
python src/listener.py
```

Speak into your microphone. Rolex will print what it heard.

Press `Ctrl+C` to stop.

---

## Project Structure

```
rolex/
├── CAPSULE.md        ← Full project PRD and history (read this first)
├── README.md         ← You are here
├── requirements.txt  ← Python dependencies
├── .gitignore
├── src/
│   ├── listener.py   ← Phase 1: Listening + transcription
│   ├── speaker.py    ← Phase 2: Voice output (coming soon)
│   ├── brain.py      ← Phase 2: LLM reasoning (coming soon)
│   ├── vision.py     ← Phase 3: Screen vision (coming soon)
│   └── main.py       ← Final combined entry point (coming soon)
├── assets/
└── logs/
```

---

## Git Tags

| Tag       | Description              |
|-----------|--------------------------|
| `phase-1` | Ears — listening working |
| `phase-2` | Voice — speaking working |
| `phase-3` | Eyes — vision working    |

---

## Read CAPSULE.md for the full story.
