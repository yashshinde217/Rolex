"""
main.py — Rolex Entry Point (V2 Phase 2)

Routing logic:
  You speak
    ├─ camera trigger  → webcam frame → LLaVA → speak
    ├─ screen trigger  → screenshot (OCR or LLaVA) → speak
    ├─ control command → exit / clear history
    └─ everything else → Ollama brain → speak

Run:
    python src/main.py

Press Ctrl+C to stop.
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

from listener import (
    record_until_silence,
    save_audio_to_temp,
    WHISPER_MODEL,
    print_rolex,
    print_user,
    print_status,
    CYAN, GRAY, RESET, BOLD
)
from brain   import Brain
from speaker import Speaker
from vision  import Vision,  is_vision_request
from camera  import Camera,  is_camera_request
import whisper

# ─── Config ───────────────────────────────────────────────────────────────────

EXIT_COMMANDS  = {"exit", "quit", "stop", "goodbye", "bye", "shut down", "shutdown"}
CLEAR_COMMANDS = {"clear history", "forget everything", "start over", "new conversation"}

# ─── Terminal colours ─────────────────────────────────────────────────────────

YELLOW = "\033[93m"
ORANGE = "\033[38;5;208m"
PURPLE = "\033[95m"

def print_divider():
    print(f"{GRAY}{'─' * 50}{RESET}")

def print_vision(message: str, mode: str = ""):
    label = f"[Eyes:{mode.upper()}]" if mode else "[Eyes]"
    color = ORANGE if mode == "ocr" else YELLOW
    print(f"{color}{label}{RESET} {message}")

def print_camera(message: str):
    print(f"{PURPLE}[Camera]{RESET} {message}")

# ─── Command helpers ──────────────────────────────────────────────────────────

def is_exit_command(text: str) -> bool:
    return any(cmd in text.lower() for cmd in EXIT_COMMANDS)

def is_clear_command(text: str) -> bool:
    return any(cmd in text.lower() for cmd in CLEAR_COMMANDS)

# ─── Boot ─────────────────────────────────────────────────────────────────────

def main():
    print()
    print(f"{CYAN}{BOLD}  ██████╗  ██████╗ ██╗     ███████╗██╗  ██╗{RESET}")
    print(f"{CYAN}{BOLD}  ██╔══██╗██╔═══██╗██║     ██╔════╝╚██╗██╔╝{RESET}")
    print(f"{CYAN}{BOLD}  ██████╔╝██║   ██║██║     █████╗   ╚███╔╝ {RESET}")
    print(f"{CYAN}{BOLD}  ██╔══██╗██║   ██║██║     ██╔══╝   ██╔██╗ {RESET}")
    print(f"{CYAN}{BOLD}  ██║  ██║╚██████╔╝███████╗███████╗██╔╝ ██╗{RESET}")
    print(f"{CYAN}{BOLD}  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝{RESET}")
    print(f"{GRAY}  Personal AI Assistant — V2 Phase 2{RESET}")
    print()
    print_divider()

    # ── Whisper ──
    print_rolex(f"Loading Whisper ({WHISPER_MODEL})...")
    whisper_model = whisper.load_model(WHISPER_MODEL)
    print_status("  Whisper ready.")

    # ── Brain ──
    print_rolex("Connecting to Ollama brain...")
    try:
        brain = Brain()
        print_status("  Brain ready.")
    except RuntimeError as e:
        print(str(e))
        sys.exit(1)

    # ── Screen vision ──
    print_rolex("Loading screen vision (LLaVA + OCR)...")
    try:
        vision = Vision()
        vision_available = True
        print_status("  Screen vision ready.")
    except RuntimeError as e:
        print_status(f"  Screen vision unavailable: {e}")
        vision = None
        vision_available = False

    # ── Camera ──
    print_rolex("Initializing camera...")
    try:
        camera = Camera()
        camera_available = True
        print_status("  Camera ready.")
    except RuntimeError as e:
        print_status(f"  Camera unavailable: {e}")
        print_status("  Run: pip install opencv-python  to enable camera.")
        camera = None
        camera_available = False

    # ── Speaker ──
    print_rolex("Initializing voice...")
    try:
        speaker = Speaker()
        print_status("  Voice ready.")
    except RuntimeError as e:
        print_status(f"  Voice unavailable ({e}). Text-only mode.")
        speaker = None

    print_divider()
    print_rolex("All systems ready.")
    print_rolex("Screen : 'look at my screen', 'read the error', 'top half'")
    print_rolex("Camera : 'look at me', 'scan this', 'what's in front of you'")
    print_rolex("Control: 'exit' to quit · 'clear history' to reset\n")

    greeting = "Rolex V2 online. I can now see through your camera too. How can I help?"
    if speaker:
        speaker.speak(greeting)
    print_rolex(greeting)
    print()

    # ── Main loop ──────────────────────────────────────────────────────────────
    while True:
        try:
            # STEP 1 — Listen
            audio = record_until_silence()
            if audio is None:
                print_status("  (silence, listening again...)\n")
                continue

            # STEP 2 — Transcribe
            print_status("  Transcribing...")
            tmp_path = save_audio_to_temp(audio)
            result   = whisper_model.transcribe(tmp_path, fp16=False, language="en")
            os.unlink(tmp_path)

            transcript = result["text"].strip()
            if not transcript:
                print_status("  (couldn't understand, try again)\n")
                continue

            print_user(transcript)

            # STEP 3 — Control commands
            if is_exit_command(transcript):
                print_rolex("Goodbye! Shutting down.")
                if speaker:
                    speaker.speak("Goodbye!")
                sys.exit(0)

            if is_clear_command(transcript):
                brain.clear_history()
                reply = "History cleared. Fresh start!"
                print_rolex(reply)
                if speaker:
                    speaker.speak(reply)
                print()
                continue

            # STEP 4 — Route to the right power
            # Camera takes priority over screen if both triggers match
            if camera_available and is_camera_request(transcript):
                # ── Camera path ──
                print_camera("Capturing from webcam...")
                reply = camera.look_and_answer(transcript)
                print_camera("Done.")
                print_rolex(reply)

                brain.history.append({"role": "user",      "content": f"[Camera] {transcript}"})
                brain.history.append({"role": "assistant", "content": reply})

            elif vision_available and is_vision_request(transcript):
                # ── Screen vision path ──
                print_vision("Capturing screen...")
                reply, mode = vision.process(transcript)
                print_vision(f"Done. ({mode.upper()} path)", mode)
                print_rolex(reply)

                brain.history.append({"role": "user",      "content": f"[Vision/{mode.upper()}] {transcript}"})
                brain.history.append({"role": "assistant", "content": reply})

            else:
                # ── Brain path ──
                print_status("  Thinking...")
                reply = brain.think(transcript)
                print_rolex(reply)

            # STEP 5 — Speak
            if speaker:
                speaker.speak(reply)

            print()

        except KeyboardInterrupt:
            print()
            print_rolex("Shutting down. Goodbye.")
            if speaker:
                try:
                    speaker.speak("Goodbye!")
                except Exception:
                    pass
            sys.exit(0)

        except Exception as e:
            print_status(f"  Unexpected error: {e}")
            time.sleep(1)


if __name__ == "__main__":
    main()