"""
vision.py — V2 Phase 1: Sharper Eyes

Major upgrades over V1:
  1. Dual-path routing — text on screen → OCR (fast, precise)
                        understanding screen → LLaVA (smart, contextual)
  2. Active window capture — grabs only the focused window, not full screen
  3. Full resolution — no aggressive downscaling, crisp image for LLaVA
  4. Smarter LLaVA prompting — richer context, better structured answers
  5. Region capture — user can say "top half", "left side" etc.

Requirements:
    pip install -r requirements.txt
    ollama pull llava
    Install Tesseract OCR:
        Download: https://github.com/UB-Mannheim/tesseract/wiki
        Install to: C:\\Program Files\\Tesseract-OCR\\
        Add to PATH or set TESSERACT_CMD below
"""

import base64
import io
import os
import json
import subprocess
import requests
from PIL import ImageGrab, Image, ImageEnhance, ImageFilter

# Try importing OCR — graceful fallback if Tesseract not installed
try:
    import pytesseract
    # Point to Tesseract if not in PATH (common on Windows)
    TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(TESSERACT_CMD):
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# Try importing pygetwindow for active window capture
try:
    import pygetwindow as gw
    WINDOW_CAPTURE_AVAILABLE = True
except ImportError:
    WINDOW_CAPTURE_AVAILABLE = False

# ─── Config ───────────────────────────────────────────────────────────────────

OLLAMA_URL         = "http://localhost:11434/api/chat"
VISION_MODEL       = "llava"
SCREENSHOT_QUALITY = 92          # Higher than V1 (was 85) — better LLaVA accuracy
MAX_IMAGE_WIDTH    = 1920        # Full HD — no aggressive downscaling anymore

# ─── Trigger phrases ──────────────────────────────────────────────────────────

# Routes to LLaVA — understanding, context, layout
SCREEN_VISION_TRIGGERS = [
    "what do you see",
    "what's on my screen",
    "what is on my screen",
    "look at my screen",
    "describe my screen",
    "what's open",
    "what am i looking at",
    "analyze my screen",
    "check my screen",
    "what's happening on screen",
    "look at this",
    "what's this",
]

# Routes to OCR — reading text accurately
OCR_TRIGGERS = [
    "read my screen",
    "read this",
    "what does it say",
    "read the text",
    "what's written",
    "what is written",
    "read that",
    "read the error",
    "read the message",
    "what's the error",
    "what does the error say",
    "read the code",
]

# Region keywords — crop screenshot to a part of the screen
REGION_MAP = {
    "top":          lambda w, h: (0,     0,     w,   h//2),
    "bottom":       lambda w, h: (0,     h//2,  w,   h),
    "left":         lambda w, h: (0,     0,     w//2, h),
    "right":        lambda w, h: (w//2,  0,     w,   h),
    "top left":     lambda w, h: (0,     0,     w//2, h//2),
    "top right":    lambda w, h: (w//2,  0,     w,   h//2),
    "bottom left":  lambda w, h: (0,     h//2,  w//2, h),
    "bottom right": lambda w, h: (w//2,  h//2,  w,   h),
    "center":       lambda w, h: (w//4,  h//4,  3*w//4, 3*h//4),
}

# ─── Vision class ─────────────────────────────────────────────────────────────

class Vision:
    """
    V2 upgraded vision: dual-path (OCR vs LLaVA), active window capture,
    region cropping, smarter prompting.
    """

    def __init__(self):
        self._check_llava()

    def _check_llava(self):
        """Verify LLaVA is available in Ollama."""
        try:
            resp = requests.get("http://localhost:11434/api/tags", timeout=3)
            resp.raise_for_status()
            models = [m["name"] for m in resp.json().get("models", [])]
            if not any("llava" in m.lower() for m in models):
                raise RuntimeError(
                    "\n[Rolex] LLaVA not found.\n"
                    "  Run: ollama pull llava\n"
                )
        except requests.exceptions.ConnectionError:
            raise RuntimeError("\n[Rolex] Ollama not running. Run: ollama serve\n")

    # ── Screenshot methods ────────────────────────────────────────────────────

    def take_fullscreen(self) -> Image.Image:
        """Capture the entire screen at full resolution."""
        return ImageGrab.grab(all_screens=False)

    def take_active_window(self) -> Image.Image:
        """
        Capture only the currently focused window.
        Falls back to full screen if pygetwindow not available.
        """
        if not WINDOW_CAPTURE_AVAILABLE:
            return self.take_fullscreen()

        try:
            win = gw.getActiveWindow()
            if win is None or win.width == 0:
                return self.take_fullscreen()

            # Add small padding around the window
            pad  = 4
            left = max(0, win.left - pad)
            top  = max(0, win.top  - pad)
            right  = win.left + win.width  + pad
            bottom = win.top  + win.height + pad

            return ImageGrab.grab(bbox=(left, top, right, bottom))
        except Exception:
            return self.take_fullscreen()

    def take_region(self, text: str) -> Image.Image:
        """
        Detect region keyword in the user's text and crop accordingly.
        Returns full screen if no region keyword found.
        """
        lowered = text.lower()
        full    = self.take_fullscreen()
        w, h    = full.size

        for keyword, bbox_fn in REGION_MAP.items():
            if keyword in lowered:
                bbox = bbox_fn(w, h)
                return full.crop(bbox)

        return full

    def _decide_capture(self, text: str) -> Image.Image:
        """
        Choose which screenshot method to use based on what the user said.
        - "active window" / "this window" / "current window" → active window
        - Region keyword (top, left, etc.) → region crop
        - Everything else → full screen
        """
        lowered = text.lower()

        window_hints = ["active window", "this window", "current window",
                        "focused window", "this app", "this program"]
        if any(h in lowered for h in window_hints):
            return self.take_active_window()

        for keyword in REGION_MAP:
            if keyword in lowered:
                return self.take_region(text)

        return self.take_fullscreen()

    # ── Image processing ──────────────────────────────────────────────────────

    def _prepare_for_llava(self, image: Image.Image) -> str:
        """Encode image to high-quality base64 JPEG for LLaVA."""
        # Downscale only if truly enormous (4K+)
        if image.width > MAX_IMAGE_WIDTH:
            ratio = MAX_IMAGE_WIDTH / image.width
            image = image.resize(
                (MAX_IMAGE_WIDTH, int(image.height * ratio)),
                Image.LANCZOS
            )
        buf = io.BytesIO()
        image.convert("RGB").save(buf, format="JPEG", quality=SCREENSHOT_QUALITY)
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    def _prepare_for_ocr(self, image: Image.Image) -> Image.Image:
        """
        Pre-process image for Tesseract OCR accuracy:
        scale up, sharpen, convert to grayscale, increase contrast.
        """
        # Scale up for OCR — more pixels = better character recognition
        scale  = 2
        w, h   = image.size
        image  = image.resize((w * scale, h * scale), Image.LANCZOS)

        # Grayscale → contrast → sharpness
        image = image.convert("L")
        image = ImageEnhance.Contrast(image).enhance(2.0)
        image = ImageEnhance.Sharpness(image).enhance(2.0)
        image = image.filter(ImageFilter.SHARPEN)

        return image

    # ── OCR path ──────────────────────────────────────────────────────────────

    def read_text_ocr(self, question: str) -> str:
        """
        Fast path: capture screen, run Tesseract OCR, return raw text.
        Best for: reading error messages, code, documents, UI labels.
        """
        if not OCR_AVAILABLE:
            return (
                "OCR is not available. Install Tesseract to enable text reading:\n"
                "  https://github.com/UB-Mannheim/tesseract/wiki\n"
                "Then: pip install pytesseract"
            )

        image     = self._decide_capture(question)
        processed = self._prepare_for_ocr(image)

        try:
            raw_text = pytesseract.image_to_string(
                processed,
                config="--psm 6"   # Assume uniform block of text
            ).strip()

            if not raw_text:
                return "I couldn't read any text from the screen. The content might be an image or the area is blank."

            # Pass OCR output through brain for a cleaner answer
            return f"Here's what I read from your screen:\n\n{raw_text}"

        except Exception as e:
            return f"OCR failed: {e}. Try asking me to look at your screen instead."

    # ── LLaVA path ────────────────────────────────────────────────────────────

    def look_and_answer(self, question: str) -> str:
        """
        Smart path: capture screen, ask LLaVA the question about it.
        Best for: understanding layout, describing UI, explaining what's happening.
        """
        image     = self._decide_capture(question)
        image_b64 = self._prepare_for_llava(image)

        # Richer, more structured prompt for better LLaVA responses
        prompt = f"""You are Rolex, an AI assistant looking at the user's computer screen.

The user asked: "{question}"

Instructions:
- Answer directly and specifically based on what you see.
- If there is text visible, read it accurately word for word.
- If it's an application, name it and describe what state it's in.
- If there's an error or warning, quote it exactly.
- Be concise but complete. Don't say "I can see an image of" — just describe it directly.
- If you cannot determine something clearly, say so honestly."""

        payload = {
            "model": VISION_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_b64]
                }
            ],
            "stream": False
        }

        try:
            resp  = requests.post(OLLAMA_URL, json=payload, timeout=90)
            resp.raise_for_status()
            return resp.json()["message"]["content"].strip()

        except requests.exceptions.Timeout:
            return "Vision took too long. Try again or ask about a specific region."
        except requests.exceptions.ConnectionError:
            return "Lost connection to Ollama. Is it still running?"
        except (KeyError, json.JSONDecodeError) as e:
            return f"Unexpected response from LLaVA: {e}"

    # ── Unified entry point ───────────────────────────────────────────────────

    def process(self, question: str) -> tuple[str, str]:
        """
        Main entry point called from main.py.
        Automatically routes to OCR or LLaVA based on the question.
        Returns (reply, mode) where mode is 'ocr' or 'llava'.
        """
        lowered = question.lower()

        if OCR_AVAILABLE and any(t in lowered for t in OCR_TRIGGERS):
            return self.read_text_ocr(question), "ocr"
        else:
            return self.look_and_answer(question), "llava"


# ─── Trigger detection (called from main.py) ──────────────────────────────────

def is_vision_request(text: str) -> bool:
    """Returns True if the user's speech is a screen/vision request."""
    lowered = text.lower()
    all_triggers = SCREEN_VISION_TRIGGERS + OCR_TRIGGERS
    return any(trigger in lowered for trigger in all_triggers)