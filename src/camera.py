"""
camera.py — V2 Phase 2: Camera Eyes

Rolex can see the real world through your laptop webcam.
Captures a frame from the camera, sends it to LLaVA via Ollama,
and returns a natural language answer about what it sees.

Requirements:
    pip install opencv-python
    ollama pull llava  (already needed for screen vision)

Trigger phrases (say any of these):
    "look at me", "what do you see in front of you",
    "scan this", "what's in front of you", "use the camera"
"""

import base64
import io
import time
import requests
from PIL import Image

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

# ─── Config ───────────────────────────────────────────────────────────────────

OLLAMA_URL      = "http://localhost:11434/api/chat"
VISION_MODEL    = "llava"
CAMERA_INDEX    = 0        # 0 = default webcam. Change to 1 if you have multiple cameras
CAMERA_QUALITY  = 92       # JPEG quality for encoding
WARMUP_FRAMES   = 5        # Discard first N frames — webcams need warmup time
                           # to adjust exposure before the image looks good
CAPTURE_WIDTH   = 1280     # Request HD from camera if supported
CAPTURE_HEIGHT  = 720

# Camera trigger phrases
CAMERA_TRIGGERS = [
    "look at me",
    "look at this",
    "what do you see in front",
    "what's in front of you",
    "what is in front of you",
    "use the camera",
    "use your camera",
    "camera",
    "scan this",
    "scan the room",
    "what's around me",
    "what is around me",
    "who am i",
    "can you see me",
    "look through the camera",
    "what's in front",
    "describe what you see",
    "take a look",
]

# ─── Camera class ─────────────────────────────────────────────────────────────

class Camera:
    """
    Captures a frame from the laptop webcam and sends it to LLaVA
    for natural language understanding of the real world.
    """

    def __init__(self):
        if not CV2_AVAILABLE:
            raise RuntimeError(
                "\n[Rolex] opencv-python not installed.\n"
                "  Run: pip install opencv-python\n"
            )
        self._test_camera()

    def _test_camera(self):
        """Check that a webcam is accessible."""
        cap = cv2.VideoCapture(CAMERA_INDEX)
        if not cap.isOpened():
            cap.release()
            raise RuntimeError(
                f"\n[Rolex] Could not open camera (index {CAMERA_INDEX}).\n"
                "  Make sure your webcam is connected and not used by another app.\n"
                "  If you have multiple cameras, change CAMERA_INDEX in camera.py\n"
            )
        cap.release()

    def capture_frame(self) -> Image.Image:
        """
        Capture a single frame from the webcam.
        Discards warmup frames so exposure/brightness is stable.
        Returns a PIL Image.
        """
        cap = cv2.VideoCapture(CAMERA_INDEX)

        # Request HD resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  CAPTURE_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAPTURE_HEIGHT)

        # Discard warmup frames — webcams need a moment to adjust
        for _ in range(WARMUP_FRAMES):
            cap.read()

        ret, frame = cap.read()
        cap.release()

        if not ret or frame is None:
            raise RuntimeError("Failed to capture frame from webcam.")

        # OpenCV uses BGR — convert to RGB for PIL
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(frame_rgb)

    def _encode_image(self, image: Image.Image) -> str:
        """Encode PIL Image to base64 JPEG string for Ollama."""
        buf = io.BytesIO()
        image.convert("RGB").save(buf, format="JPEG", quality=CAMERA_QUALITY)
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    def look_and_answer(self, question: str) -> str:
        """
        Capture a camera frame and ask LLaVA the question about it.
        Returns LLaVA's answer as a string.
        """
        # Capture frame
        try:
            image = self.capture_frame()
        except RuntimeError as e:
            return str(e)

        image_b64 = self._encode_image(image)

        # Structured prompt for camera context
        prompt = f"""You are Rolex, an AI assistant looking through the user's laptop webcam at the real world.

The user asked: "{question}"

Instructions:
- Answer directly based on what you see in front of the camera.
- If you see a person, describe them neutrally (posture, expression, what they're doing).
- If you see an object, identify it and describe it clearly.
- If you see text (document, whiteboard, book), read it accurately.
- If you see a scene or room, describe what's notable.
- Be concise but specific. Don't say "I see an image of" — just describe directly.
- If the image is dark, blurry, or unclear, say so honestly."""

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
            resp = requests.post(OLLAMA_URL, json=payload, timeout=90)
            resp.raise_for_status()
            return resp.json()["message"]["content"].strip()

        except requests.exceptions.Timeout:
            return "Camera vision took too long. Try again."
        except requests.exceptions.ConnectionError:
            return "Lost connection to Ollama. Is it still running?"
        except (KeyError, Exception) as e:
            return f"Unexpected error from camera vision: {e}"

    def save_snapshot(self, image: Image.Image, path: str):
        """Save a captured frame to disk (optional utility)."""
        image.save(path, format="JPEG", quality=CAMERA_QUALITY)


# ─── Trigger detection (called from main.py) ──────────────────────────────────

def is_camera_request(text: str) -> bool:
    """Returns True if the user's speech sounds like a camera/real-world request."""
    lowered = text.lower()
    return any(trigger in lowered for trigger in CAMERA_TRIGGERS)
