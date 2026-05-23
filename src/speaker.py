"""
speaker.py — Phase 2: Voice (Edge TTS — Neural)

Uses Microsoft Edge TTS neural voices via the edge-tts library.
Same voices as Windows 11 Narrator and Microsoft Edge browser.
Sounds extremely natural — not robotic at all.

Voices to try (set VOICE below):
  en-US-GuyNeural          — natural American male (default)
  en-US-ChristopherNeural  — deeper American male
  en-US-EricNeural         — calm American male
  en-IN-PrabhatNeural      — Indian English male

Requires internet connection to stream audio from Microsoft's TTS servers.
No API key or account needed.
"""

import asyncio
import tempfile
import os
import edge_tts
import sounddevice as sd
import soundfile as sf

# ─── Config ───────────────────────────────────────────────────────────────────

VOICE  = "en-US-GuyNeural"   # Change this to try different voices
RATE   = "+0%"               # Speed: "+10%" faster, "-10%" slower
VOLUME = "+0%"               # Volume: "+10%" louder, "-10%" quieter
PITCH  = "+0Hz"              # Pitch: "+5Hz" higher, "-5Hz" deeper

# ─── Speaker ──────────────────────────────────────────────────────────────────

class Speaker:
    """
    Speaks text using Microsoft Edge neural TTS voices.
    Generates audio to a temp file, plays it via sounddevice, then cleans up.
    """

    def __init__(self):
        # Verify edge-tts is importable — actual connection tested on first speak
        try:
            import edge_tts as _test
        except ImportError:
            raise RuntimeError(
                "[Rolex] edge-tts not installed.\n"
                "  Run: pip install edge-tts soundfile"
            )
        self.voice = VOICE

    def speak(self, text: str):
        """Speak text using Edge neural TTS. Blocks until done."""
        if not text or not text.strip():
            return
        try:
            asyncio.run(self._speak_async(text))
        except RuntimeError:
            # If there's already an event loop (e.g. Jupyter), use this instead
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self._speak_async(text))
            finally:
                loop.close()

    async def _speak_async(self, text: str):
        """Async: generate audio with Edge TTS, save to temp file, play it."""
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        tmp_path = tmp.name
        tmp.close()

        try:
            # Generate speech and save to temp mp3
            communicate = edge_tts.Communicate(
                text,
                voice=self.voice,
                rate=RATE,
                volume=VOLUME,
                pitch=PITCH
            )
            await communicate.save(tmp_path)

            # Play the mp3 via sounddevice + soundfile
            data, samplerate = sf.read(tmp_path, dtype="float32")
            sd.play(data, samplerate)
            sd.wait()  # Block until playback finishes

        except Exception as e:
            print(f"  [speaker] TTS error: {e}")
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    def list_voices(self):
        """Print all available Edge TTS voices filtered to English."""
        async def _list():
            voices = await edge_tts.list_voices()
            english = [v for v in voices if v["Locale"].startswith("en-")]
            print(f"\nAvailable English voices ({len(english)} total):")
            for v in english:
                marker = " <- current" if v["ShortName"] == self.voice else ""
                gender = v.get("Gender", "")
                print(f"  {v['ShortName']:35s} {gender}{marker}")
            print()
        asyncio.run(_list())