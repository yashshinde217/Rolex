"""
brain.py — Phase 2: Intelligence

Rolex thinks using a local LLM via Ollama.
Ollama runs models like LLaMA 3 and Mistral completely on your machine.

Requirements:
  1. Download and install Ollama: https://ollama.com/download
  2. Pull a model (run once in terminal):
       ollama pull llama3.2
  3. Ollama must be running before you start Rolex:
       ollama serve
"""

import requests
import json

# ─── Config ───────────────────────────────────────────────────────────────────

OLLAMA_URL    = "http://localhost:11434/api/chat"
OLLAMA_MODEL  = "llama3.2"       # Change to "mistral" if you prefer
SYSTEM_PROMPT = """You are Rolex, a personal AI assistant running locally on the user's computer.
You are smart, concise, and helpful. You speak in a natural, friendly tone — like a knowledgeable friend, not a robot.
Keep your answers short and to the point unless the user asks for detail.
You are NOT ChatGPT. You are Rolex. Never mention OpenAI or ChatGPT."""

# ─── Brain ────────────────────────────────────────────────────────────────────

class Brain:
    """
    Manages conversation history and communicates with the local Ollama LLM.
    Keeps full message history so Rolex remembers context within a session.
    """

    def __init__(self):
        self.history: list[dict] = []
        self._check_ollama()

    def _check_ollama(self):
        """Verify Ollama is running before we try to use it."""
        try:
            resp = requests.get("http://localhost:11434/api/tags", timeout=3)
            resp.raise_for_status()
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                "\n[Rolex] Cannot connect to Ollama.\n"
                "  Make sure Ollama is installed and running:\n"
                "    1. Download: https://ollama.com/download\n"
                "    2. Run in a terminal: ollama serve\n"
                "    3. Pull the model: ollama pull llama3.2\n"
            )

    def think(self, user_input: str) -> str:
        """
        Send user input to the LLM with full conversation history.
        Returns the assistant's response as a string.
        """
        # Add user message to history
        self.history.append({
            "role": "user",
            "content": user_input
        })

        # Build request payload
        payload = {
            "model": OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                *self.history
            ],
            "stream": False
        }

        try:
            resp = requests.post(OLLAMA_URL, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            reply = data["message"]["content"].strip()

        except requests.exceptions.Timeout:
            reply = "Sorry, I took too long to think. Try asking again."
        except requests.exceptions.ConnectionError:
            reply = "I lost connection to my brain. Is Ollama still running?"
        except (KeyError, json.JSONDecodeError):
            reply = "I got a strange response from my brain. Try again."

        # Add assistant reply to history so next turn has context
        self.history.append({
            "role": "assistant",
            "content": reply
        })

        return reply

    def clear_history(self):
        """Wipe conversation history — start a fresh session."""
        self.history = []
