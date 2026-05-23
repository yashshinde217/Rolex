"""
main.py — Rolex Entry Point (Phase 2)

Full conversation loop:
  You speak → Rolex hears → Rolex thinks → Rolex speaks back → repeat

Run:
    python src/main.py

Press Ctrl+C to stop.

Requirements for Phase 2:
  - pip install -r requirements.txt
  - Ollama installed and running: https://ollama.com/download
  - Model pulled: ollama pull llama3.2
"""

import os
import sys
import time
import tempfile

import numpy as np
from scipy.io.wavfile import write as write_wav

# ─── Import all three modules ─────────────────────────────────────────────────

# Add src to path so imports work when running from project root
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
import whisper

# ─── Config ───────────────────────────────────────────────────────────────────

# Special commands the user can say to control Rolex
EXIT_COMMANDS  = {"exit", "quit", "stop", "goodbye", "bye", "shut down", "shutdown"}
CLEAR_COMMANDS = {"clear history", "forget everything", "start over", "new conversation"}

# ─── Helpers ──────────────────────────────────────────────────────────────────

def is_exit_command(text: str) -> bool:
    return any(cmd in text.lower() for cmd in EXIT_COMMANDS)

def is_clear_command(text: str) -> bool:
    return any(cmd in text.lower() for cmd in CLEAR_COMMANDS)

def print_divider():
    print(f"{GRAY}{'─' * 50}{RESET}")

# ─── Main loop ────────────────────────────────────────────────────────────────

def main():
    print()
    print(f"{CYAN}{BOLD}  ██████╗  ██████╗ ██╗     ███████╗██╗  ██╗{RESET}")
    print(f"{CYAN}{BOLD}  ██╔══██╗██╔═══██╗██║     ██╔════╝╚██╗██╔╝{RESET}")
    print(f"{CYAN}{BOLD}  ██████╔╝██║   ██║██║     █████╗   ╚███╔╝ {RESET}")
    print(f"{CYAN}{BOLD}  ██╔══██╗██║   ██║██║     ██╔══╝   ██╔██╗ {RESET}")
    print(f"{CYAN}{BOLD}  ██║  ██║╚██████╔╝███████╗███████╗██╔╝ ██╗{RESET}")
    print(f"{CYAN}{BOLD}  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝{RESET}")
    print(f"{GRAY}  Personal AI Assistant — V1 Phase 2{RESET}")
    print()
    print_divider()

    # ── Step 1: Load Whisper ──
    print_rolex(f"Loading Whisper ({WHISPER_MODEL})...")
    whisper_model = whisper.load_model(WHISPER_MODEL)
    print_status("  Whisper ready.")

    # ── Step 2: Init Brain (Ollama) ──
    print_rolex("Connecting to Ollama brain...")
    try:
        brain = Brain()
        print_status("  Ollama connected.")
    except RuntimeError as e:
        print(str(e))
        sys.exit(1)

    # ── Step 3: Init Speaker ──
    print_rolex("Initializing voice...")
    try:
        speaker = Speaker()
        print_status("  Voice ready.")
    except RuntimeError as e:
        print_status(f"  Warning: TTS failed ({e}). Will run text-only mode.")
        speaker = None

    print_divider()
    print_rolex("I'm ready. Speak to me anytime.")
    print_rolex("Say 'exit' to quit. Say 'clear history' to start fresh.\n")

    if speaker:
        speaker.speak("Hello! I'm Rolex. How can I help you?")

    # ── Main conversation loop ──
    while True:
        try:
            # STEP 1: Listen
            audio = record_until_silence()

            if audio is None:
                print_status("  (silence detected, listening again...)\n")
                continue

            # STEP 2: Transcribe
            print_status("  Transcribing...")
            tmp_path = save_audio_to_temp(audio)
            result = whisper_model.transcribe(tmp_path, fp16=False, language="en")
            os.unlink(tmp_path)

            transcript = result["text"].strip()
            if not transcript:
                print_status("  (couldn't understand, try again)\n")
                continue

            print_user(transcript)

            # STEP 3: Check for control commands
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

            # STEP 4: Think
            print_status("  Thinking...")
            reply = brain.think(transcript)

            # STEP 5: Speak
            print_rolex(reply)
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
