"""
settings.py — Settings panel widget

A slide-in overlay inside the main window.
Lets the user change voice, model, orb corner position.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QComboBox, QSlider, QSizePolicy)
from PyQt6.QtCore    import Qt, pyqtSignal
from PyQt6.QtGui     import QFont
from .theme import *


class SettingsPanel(QWidget):
    """
    Overlay settings panel — shown/hidden over the main window content.
    Emits signals when settings change so app.py can apply them.
    """

    voice_changed  = pyqtSignal(str)    # Edge TTS voice name
    model_changed  = pyqtSignal(str)    # Ollama model name
    corner_changed = pyqtSignal(str)    # top-right / top-left / bottom-right / bottom-left
    closed         = pyqtSignal()

    # Available options
    VOICES = [
        ("Guy (US Male)",          "en-US-GuyNeural"),
        ("Christopher (US Male)",  "en-US-ChristopherNeural"),
        ("Eric (US Male)",         "en-US-EricNeural"),
        ("Prabhat (IN Male)",      "en-IN-PrabhatNeural"),
        ("Jenny (US Female)",      "en-US-JennyNeural"),
        ("Aria (US Female)",       "en-US-AriaNeural"),
    ]

    MODELS = [
        "llama3.2",
        "llama3.1",
        "mistral",
        "gemma2",
        "phi3",
    ]

    CORNERS = [
        ("Top Right",    "top-right"),
        ("Top Left",     "top-left"),
        ("Bottom Right", "bottom-right"),
        ("Bottom Left",  "bottom-left"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hide()
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {GLASS_SETTINGS};
                border-radius: {WINDOW_RADIUS}px;
                border: 1px solid {GLASS_BORDER};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        title = QLabel("Settings")
        title.setFont(QFont(FONT_TITLE, SIZE_LG, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent; border: none;")

        close = QPushButton("✕")
        close.setFixedSize(24, 24)
        close.setCursor(Qt.CursorShape.PointingHandCursor)
        close.setStyleSheet(f"""
            QPushButton {{
                color: {TEXT_SECONDARY}; background: transparent;
                border: 1px solid {GLASS_BORDER}; border-radius: 12px; font-size: 11px;
            }}
            QPushButton:hover {{ color: {TEXT_PRIMARY}; background: {GLASS_HOVER}; }}
        """)
        close.clicked.connect(self._on_close)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(close)
        layout.addLayout(header)

        layout.addWidget(self._divider())

        # Voice
        layout.addWidget(self._section_label("🎙  Voice"))
        self._voice_combo = self._make_combo([v[0] for v in self.VOICES])
        self._voice_combo.currentIndexChanged.connect(
            lambda i: self.voice_changed.emit(self.VOICES[i][1]))
        layout.addWidget(self._voice_combo)

        # Model
        layout.addWidget(self._section_label("🧠  LLM Model"))
        self._model_combo = self._make_combo(self.MODELS)
        self._model_combo.currentIndexChanged.connect(
            lambda i: self.model_changed.emit(self.MODELS[i]))
        layout.addWidget(self._model_combo)

        # Corner
        layout.addWidget(self._section_label("📌  Window Position"))
        self._corner_combo = self._make_combo([c[0] for c in self.CORNERS])
        self._corner_combo.currentIndexChanged.connect(
            lambda i: self.corner_changed.emit(self.CORNERS[i][1]))
        layout.addWidget(self._corner_combo)

        layout.addWidget(self._divider())
        layout.addStretch()

        # Version label
        ver = QLabel("Rolex  ·  V2  ·  100% local  ·  free forever")
        ver.setFont(QFont(FONT_MONO, SIZE_SM - 1))
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ver.setStyleSheet(f"color: {TEXT_DIM}; background: transparent; border: none;")
        layout.addWidget(ver)

    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setFont(QFont(FONT_BODY, SIZE_SM, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent; border: none;")
        return lbl

    def _make_combo(self, items: list) -> QComboBox:
        combo = QComboBox()
        combo.addItems(items)
        combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {GLASS_SECTION};
                color: {TEXT_PRIMARY};
                border: 1px solid {GLASS_BORDER};
                border-radius: 8px;
                padding: 5px 10px;
                font-family: {FONT_BODY};
                font-size: {SIZE_MD}px;
            }}
            QComboBox:hover {{ background-color: {GLASS_HOVER}; }}
            QComboBox::drop-down {{ border: none; width: 20px; }}
            QComboBox QAbstractItemView {{
                background-color: #0D1520;
                color: {TEXT_PRIMARY};
                border: 1px solid {GLASS_BORDER};
                selection-background-color: {GLASS_HOVER};
            }}
        """)
        return combo

    def _divider(self) -> QWidget:
        line = QWidget()
        line.setFixedHeight(1)
        line.setStyleSheet(f"background-color: {GLASS_BORDER}; border: none;")
        return line

    def _on_close(self):
        self.hide()
        self.closed.emit()

    def show_panel(self, geometry):
        """Show overlay filling the given QRect (parent window geometry)."""
        self.setGeometry(geometry)
        self.show()
        self.raise_()