"""
bubble.py — Chat message bubble widget (glassmorphism style)
"""

from PyQt6.QtWidgets import (QWidget, QLabel, QHBoxLayout,
                              QVBoxLayout, QSizePolicy)
from PyQt6.QtCore    import Qt
from PyQt6.QtGui     import QFont
from .theme import *


MODE_TAGS = {
    "brain":     ("🧠 Brain",   TAG_BRAIN),
    "web":       ("🌐 Web",     TAG_WEB),
    "search":    ("🌐 Search",  TAG_WEB),
    "weather":   ("🌤 Weather", TAG_WEB),
    "news":      ("📰 News",    TAG_WEB),
    "wikipedia": ("📖 Wiki",    TAG_WEB),
    "url":       ("🔗 Page",    TAG_WEB),
    "youtube":   ("▶ YouTube",  TAG_WEB),
    "camera":    ("📷 Camera",  TAG_CAMERA),
    "vision":    ("👁 Vision",  TAG_VISION),
    "ocr":       ("📄 OCR",     TAG_OCR),
    "llava":     ("👁 Vision",  TAG_VISION),
}


class BubbleWidget(QWidget):
    def __init__(self, text: str, is_user: bool = False, mode: str = "brain"):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self._build(text, is_user, mode)

    def _build(self, text: str, is_user: bool, mode: str):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(8, 2, 8, 2)
        outer.setSpacing(0)

        card = QWidget()
        card.setMaximumWidth(310)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(10, 7, 10, 7)
        card_layout.setSpacing(3)

        if is_user:
            card.setStyleSheet(f"""
                background-color: {GLASS_CARD_USER};
                border: 1px solid rgba(0,140,255,40);
                border-radius: 12px;
                border-top-right-radius: 3px;
            """)
            lbl = QLabel(text)
            lbl.setWordWrap(True)
            lbl.setFont(QFont(FONT_BODY, SIZE_MD))
            lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
            lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            card_layout.addWidget(lbl)
            outer.addStretch()
            outer.addWidget(card)
        else:
            card.setStyleSheet(f"""
                background-color: {GLASS_CARD};
                border: 1px solid {GLASS_BORDER};
                border-radius: 12px;
                border-top-left-radius: 3px;
            """)
            tag_text, (tag_bg, tag_fg) = MODE_TAGS.get(mode, MODE_TAGS["brain"])
            tag = QLabel(tag_text)
            tag.setFont(QFont(FONT_BODY, SIZE_SM - 1, QFont.Weight.Bold))
            tag.setStyleSheet(f"""
                color: {tag_fg};
                background-color: {tag_bg};
                border-radius: 5px;
                padding: 1px 6px;
            """)
            tag.setFixedHeight(16)
            tag.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

            lbl = QLabel(text)
            lbl.setWordWrap(True)
            lbl.setFont(QFont(FONT_BODY, SIZE_MD))
            lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
            lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

            card_layout.addWidget(tag)
            card_layout.addWidget(lbl)
            outer.addWidget(card)
            outer.addStretch()