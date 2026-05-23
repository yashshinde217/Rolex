"""
listener.py — Phase 1: Ears

Rolex listens through your microphone, detects when you're speaking,
records your voice, and transcribes it using OpenAI Whisper (runs locally).

Run:
    python src/listener.py

Press Ctrl+C to stop.
"""

import os
import sys
import tempfile
import time
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write as write_wav
import whisper

# ─── Config ───────────────────────────────────────────────────────────────────

SAMPLE_RATE = 16000        # Hz — Whisper expects 16kHz
CHANNELS = 1               # Mono
BLOCK_DURATION = 0.5       # Seconds per audio block read from mic
SILENCE_THRESHOLD = 0.01   # Energy level below which audio is considered silence
SILENCE_TIMEOUT = 1.5      # Seconds of silence before ending recording
MIN_RECORD_SECONDS = 0.5   # Minimum speech length to bother transcribing
WHISPER_MODEL = "base"     # Options: tiny, base, small, medium, large
                           # base = good speed/accuracy balance (~140MB download)

# ─── Colors for terminal output ───────────────────────────────────────────────

CYAN  = "\033[96m"
GREEN = "\033[92m"
GRAY  = "\033[90m"
RESET = "\033[0m"
BOLD  = "\033[1m"


def print_rolex(message: str):
    """Print a message styled as Rolex speaking."""
    print(f"{CYAN}{BOLD}[Rolex]{RESET} {message}")


def print_user(message: str):
    """Print transcribed user speech."""
    print(f"{GREEN}{BOLD}[You]  {RESET} {message}")


def print_status(message: str):
    """Print a dim status/debug message."""
    print(f"{GRAY}{message}{RESET}")


# ─── Audio helpers ────────────────────────────────────────────────────────────

def get_audio_energy(audio_block: np.ndarray) -> float:
    """Return RMS energy of an audio block (0.0 to ~1.0)."""
    return float(np.sqrt(np.mean(audio_block ** 2)))


def record_until_silence() -> np.ndarray | None:
    """
    Listen to the mic. Start recording when speech is detected.
    Stop and return the audio when silence lasts longer than SILENCE_TIMEOUT.
    Returns None if no meaningful speech was captured.
    """
    print_status("  Listening... (speak now)")

    recorded_blocks = []
    silent_duration = 0.0
    speaking = False
    block_size = int(SAMPLE_RATE * BLOCK_DURATION)

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS,
                        dtype="float32", blocksize=block_size) as stream:

        while True:
            block, _ = stream.read(block_size)
            block = block.flatten()
            energy = get_audio_energy(block)

            if energy > SILENCE_THRESHOLD:
                # Sound detected
                if not speaking:
                    print_status("  Recording...")
                    speaking = True
                silent_duration = 0.0
                recorded_blocks.append(block)

            elif speaking:
                # Was speaking, now quiet
                recorded_blocks.append(block)
                silent_duration += BLOCK_DURATION

                if silent_duration >= SILENCE_TIMEOUT:
                    print_status("  Done recording.")
                    break

    if not recorded_blocks:
        return None

    audio = np.concatenate(recorded_blocks)

    # Check if recording is long enough to bother with
    duration = len(audio) / SAMPLE_RATE
    if duration < MIN_RECORD_SECONDS:
        return None

    return audio


def save_audio_to_temp(audio: np.ndarray) -> str:
    """Save a numpy float32 audio array to a temp WAV file. Returns file path."""
    # Whisper expects int16 WAV
    audio_int16 = (audio * 32767).astype(np.int16)
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    write_wav(tmp.name, SAMPLE_RATE, audio_int16)
    return tmp.name


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print()
    print_rolex(f"Loading Whisper ({WHISPER_MODEL} model)...")
    print_status("  First run will download the model. Sit tight.")
    print()

    model = whisper.load_model(WHISPER_MODEL)

    print_rolex("I'm listening. Speak whenever you're ready.")
    print_rolex("Press Ctrl+C to stop.\n")

    while True:
        try:
            # Step 1: Record
            audio = record_until_silence()

            if audio is None:
                print_status("  (no speech detected, listening again...)\n")
                continue

            # Step 2: Transcribe
            print_status("  Transcribing...")
            tmp_path = save_audio_to_temp(audio)

            result = model.transcribe(tmp_path, fp16=False, language="en")
            transcript = result["text"].strip()

            # Clean up temp file
            os.unlink(tmp_path)

            # Step 3: Output
            if transcript:
                print_user(transcript)
            else:
                print_status("  (couldn't understand that, try again)\n")

            print()  # spacing between turns

        except KeyboardInterrupt:
            print()
            print_rolex("Shutting down. Goodbye.")
            sys.exit(0)

        except Exception as e:
            print_status(f"  Error: {e}")
            time.sleep(1)


if __name__ == "__main__":
    main()
