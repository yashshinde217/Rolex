"""
app.py — Rolex GUI Application

Owns the Qt app, the main window, and the worker thread.
Worker runs all AI logic in background — UI never blocks.
"""

import os
import sys
import time

# ── Path fix ──────────────────────────────────────────────────────────────────
_src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore    import QThread, pyqtSignal, QObject

from gui.window import RolexWindow


# ─── Worker signals ───────────────────────────────────────────────────────────

class WorkerSignals(QObject):
    state_changed    = pyqtSignal(str)       # orb/window state
    transcript_ready = pyqtSignal(str)       # live speech text
    reply_ready      = pyqtSignal(str, str)  # (reply, mode)
    user_said        = pyqtSignal(str)       # user message bubble
    viz_levels       = pyqtSignal(list)      # mic bar levels


# ─── Worker thread ────────────────────────────────────────────────────────────

class RolexWorker(QThread):
    """All heavy AI work runs here. Never touches UI directly."""

    def __init__(self):
        super().__init__()
        self.signals  = WorkerSignals()
        self._running = True
        self._load_modules()

    def _load_modules(self):
        self.signals.state_changed.emit("thinking")

        import whisper
        from listener import record_until_silence, save_audio_to_temp, WHISPER_MODEL
        from brain    import Brain
        from speaker  import Speaker
        from vision   import Vision,   is_vision_request
        from camera   import Camera,   is_camera_request
        from internet import Internet, is_internet_request

        self._record      = record_until_silence
        self._save_audio  = save_audio_to_temp
        self._is_vision   = is_vision_request
        self._is_camera   = is_camera_request
        self._is_internet = is_internet_request

        EXIT_CMDS  = {"exit","quit","stop","goodbye","bye","shut down","shutdown"}
        CLEAR_CMDS = {"clear history","forget everything","start over","new conversation"}
        self._is_exit  = lambda t: any(c in t.lower() for c in EXIT_CMDS)
        self._is_clear = lambda t: any(c in t.lower() for c in CLEAR_CMDS)

        self._whisper = whisper.load_model(WHISPER_MODEL)
        self._brain   = Brain()
        self._speaker = Speaker()

        try:
            self._vision    = Vision();  self._vision_ok = True
        except RuntimeError:
            self._vision    = None;      self._vision_ok = False

        try:
            self._camera    = Camera();  self._camera_ok = True
        except RuntimeError:
            self._camera    = None;      self._camera_ok = False

        self._internet = Internet()
        self.signals.state_changed.emit("idle")

    def run(self):
        greeting = "Rolex online. How can I help?"
        self.signals.reply_ready.emit(greeting, "brain")
        self._speaker.speak(greeting)
        self.signals.state_changed.emit("idle")

        while self._running:
            try:
                # Listen
                self.signals.state_changed.emit("listening")
                self.signals.transcript_ready.emit("Listening...")
                audio = self._record()

                if audio is None:
                    self.signals.state_changed.emit("idle")
                    continue

                # Transcribe
                self.signals.state_changed.emit("thinking")
                self.signals.transcript_ready.emit("Transcribing...")
                tmp    = self._save_audio(audio)
                result = self._whisper.transcribe(tmp, fp16=False, language="en")
                os.unlink(tmp)

                transcript = result["text"].strip()
                if not transcript:
                    self.signals.state_changed.emit("idle")
                    continue

                self.signals.transcript_ready.emit(transcript)
                self.signals.user_said.emit(transcript)

                # Control commands
                if self._is_exit(transcript):
                    self.signals.reply_ready.emit("Goodbye!", "brain")
                    self._speaker.speak("Goodbye!")
                    self._running = False
                    QApplication.quit()
                    return

                if self._is_clear(transcript):
                    self._brain.clear_history()
                    reply = "History cleared. Fresh start!"
                    self.signals.reply_ready.emit(reply, "brain")
                    self.signals.state_changed.emit("speaking")
                    self._speaker.speak(reply)
                    self.signals.state_changed.emit("idle")
                    continue

                # Route
                if self._camera_ok and self._is_camera(transcript):
                    self.signals.state_changed.emit("camera")
                    reply = self._camera.look_and_answer(transcript)
                    self._brain.history.append({"role":"user",      "content":f"[Camera] {transcript}"})
                    self._brain.history.append({"role":"assistant",  "content":reply})
                    mode = "camera"

                elif self._vision_ok and self._is_vision(transcript):
                    self.signals.state_changed.emit("vision")
                    reply, ocr_mode = self._vision.process(transcript)
                    self._brain.history.append({"role":"user",      "content":f"[Vision] {transcript}"})
                    self._brain.history.append({"role":"assistant",  "content":reply})
                    mode = ocr_mode

                elif self._is_internet(transcript):
                    self.signals.state_changed.emit("web")
                    raw, intent = self._internet.process(transcript)
                    reply = self._brain.think_with_context(transcript, raw)
                    mode  = intent

                else:
                    self.signals.state_changed.emit("thinking")
                    reply = self._brain.think(transcript)
                    mode  = "brain"

                # Speak
                self.signals.state_changed.emit("speaking")
                self.signals.reply_ready.emit(reply, mode)
                self._speaker.speak(reply)
                self.signals.state_changed.emit("idle")
                self.signals.transcript_ready.emit("")

            except Exception as e:
                self.signals.state_changed.emit("error")
                self.signals.transcript_ready.emit(f"Error: {e}")
                time.sleep(1)
                self.signals.state_changed.emit("idle")

    def stop(self):
        self._running = False


# ─── App ──────────────────────────────────────────────────────────────────────

class RolexApp:
    def __init__(self):
        self._qt = QApplication.instance() or QApplication(sys.argv)
        self._qt.setQuitOnLastWindowClosed(False)

        self._window = RolexWindow()
        self._worker = RolexWorker()

        sig = self._worker.signals
        sig.state_changed.connect(self._window.set_state)
        sig.transcript_ready.connect(self._window.set_transcript)
        sig.reply_ready.connect(lambda t, m: self._window.add_message(t, False, m))
        sig.user_said.connect(lambda t: self._window.add_message(t, True))
        sig.viz_levels.connect(self._window.set_viz_levels)

        # Settings signals
        self._window._settings.voice_changed.connect(self._on_voice_changed)
        self._window._settings.model_changed.connect(self._on_model_changed)

    def _on_voice_changed(self, voice: str):
        """Hot-swap TTS voice without restarting."""
        try:
            from speaker import Speaker
            import gui.theme as theme
            self._worker._speaker = Speaker.__new__(Speaker)
            self._worker._speaker.voice_id = None
            self._worker._speaker.voice = voice
        except Exception:
            pass

    def _on_model_changed(self, model: str):
        """Update Ollama model used by brain."""
        try:
            self._worker._brain.history = []
            import brain as brain_mod
            brain_mod.OLLAMA_MODEL = model
            self._worker._brain = self._worker._brain.__class__.__new__(
                self._worker._brain.__class__)
            self._worker._brain.__init__()
        except Exception:
            pass

    def run(self):
        self._window.show()
        self._worker.start()
        sys.exit(self._qt.exec())