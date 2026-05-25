"""
main.py — Rolex Entry Point (V2 Phase 1)

Upgrades over V1:
  - Vision now auto-routes: OCR for text, LLaVA for understanding
  - Shows which vision mode was used ([OCR] or [LLaVA])
  - Active window and region capture support

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
    CYAN, GREEN, GRAY, RESET, BOLD
)
from brain   import Brain
from speaker import Speaker
from vision  import Vision, is_vision_request
import whisper

# ─── Config ───────────────────────────────────────────────────────────────────

EXIT_COMMANDS  = {"exit", "quit", "stop", "goodbye", "bye", "shut down", "shutdown"}
CLEAR_COMMANDS = {"clear history", "forget everything", "start over", "new conversation"}

# ─── Helpers ──────────────────────────────────────────────────────────────────

YELLOW = "\033[93m"
ORANGE = "\033[38;5;208m"

def is_exit_command(text: str) -> bool:
    return any(cmd in text.lower() for cmd in EXIT_COMMANDS)

def is_clear_command(text: str) -> bool:
    return any(cmd in text.lower() for cmd in CLEAR_COMMANDS)

def print_divider():
    print(f"{GRAY}{'─' * 50}{RESET}")

def print_vision(message: str, mode: str = ""):
    label = f"[Eyes:{mode.upper()}]" if mode else "[Eyes]"
    color = ORANGE if mode == "ocr" else YELLOW
    print(f"{color}{label}{RESET} {message}")

# ─── Boot ─────────────────────────────────────────────────────────────────────

def main():
    print()
    print(f"{CYAN}{BOLD}  ██████╗  ██████╗ ██╗     ███████╗██╗  ██╗{RESET}")
    print(f"{CYAN}{BOLD}  ██╔══██╗██╔═══██╗██║     ██╔════╝╚██╗██╔╝{RESET}")
    print(f"{CYAN}{BOLD}  ██████╔╝██║   ██║██║     █████╗   ╚███╔╝ {RESET}")
    print(f"{CYAN}{BOLD}  ██╔══██╗██║   ██║██║     ██╔══╝   ██╔██╗ {RESET}")
    print(f"{CYAN}{BOLD}  ██║  ██║╚██████╔╝███████╗███████╗██╔╝ ██╗{RESET}")
    print(f"{CYAN}{BOLD}  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝{RESET}")
    print(f"{GRAY}  Personal AI Assistant — V2 Phase 1{RESET}")
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

    # ── Vision ──
    print_rolex("Loading vision (LLaVA + OCR)...")
    try:
        vision = Vision()
        vision_available = True
        print_status("  Vision ready.")
    except RuntimeError as e:
        print_status(f"  Vision unavailable: {e}")
        vision = None
        vision_available = False

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
    print_rolex("Vision commands: 'look at my screen', 'read the error', 'describe top half'")
    print_rolex("Say 'exit' to quit. Say 'clear history' to reset.\n")

    if speaker:
        speaker.speak("Rolex V2 online. Vision is sharper now. How can I help?")

    # ── Main loop ──
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

            # STEP 4 — Route: vision or brain?
            if vision_available and is_vision_request(transcript):

                # Auto-routes internally to OCR or LLaVA
                print_vision("Capturing screen...")
                reply, mode = vision.process(transcript)
                print_vision(f"Done. ({mode.upper()} path)", mode)
                print_rolex(reply)

                # Store in brain history for follow-up questions
                brain.history.append({
                    "role": "user",
                    "content": f"[Vision/{mode.upper()}] {transcript}"
                })
                brain.history.append({
                    "role": "assistant",
                    "content": reply
                })

            else:
                # Brain path
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