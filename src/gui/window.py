"""
window.py — Rolex main floating window (Glassmorphism, square, top-right)

A single always-visible square panel containing:
  - Header (name + minimize button)
  - Orb (animated, state-aware)
  - Mic visualizer bars
  - Chat history (scrollable bubbles)
  - Status bar
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QScrollArea, QPushButton, QFrame, QSizePolicy,
                              QGraphicsDropShadowEffect)
from PyQt6.QtCore    import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui     import (QFont, QColor, QPainter, QBrush, QPen,
                              QLinearGradient, QRadialGradient)

from .theme      import *
from .orb        import OrbWidget
from .visualizer import VisualizerWidget
from .bubble     import BubbleWidget


class RolexWindow(QWidget):
    """
    The main Rolex floating window.
    Square, glassmorphism, always on top, top-right corner.
    """

    def __init__(self):
        super().__init__()
        self._state = "idle"
        self._setup_window()
        self._build_ui()
        self._position_window()
        self._apply_shadow()

    # ── Window setup ──────────────────────────────────────────────────────────

    def _setup_window(self):
        self.setFixedSize(WINDOW_SIZE, WINDOW_SIZE)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def _position_window(self):
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().availableGeometry()
        x = screen.right()  - WINDOW_SIZE - WINDOW_MARGIN
        y = screen.top()    + WINDOW_MARGIN
        self.move(x, y)

    def _apply_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(32)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.setGraphicsEffect(shadow)

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        # Root container — gives us the glass card with rounded corners
        self._root = QWidget(self)
        self._root.setGeometry(0, 0, WINDOW_SIZE, WINDOW_SIZE)
        self._root.setObjectName("root")
        self._root.setStyleSheet(f"""
            QWidget#root {{
                background-color: {GLASS_BG};
                border-radius: {WINDOW_RADIUS}px;
                border: 1px solid {GLASS_BORDER};
            }}
        """)

        layout = QVBoxLayout(self._root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_header())
        layout.addWidget(self._build_divider())
        layout.addWidget(self._build_orb_section())
        layout.addWidget(self._build_divider())
        layout.addWidget(self._build_visualizer_section())
        layout.addWidget(self._build_divider())
        layout.addWidget(self._build_chat_section(), stretch=1)
        layout.addWidget(self._build_divider())
        layout.addWidget(self._build_status_bar())

    def _build_divider(self) -> QWidget:
        line = QWidget()
        line.setFixedHeight(1)
        line.setStyleSheet(f"background-color: {GLASS_BORDER};")
        return line

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setFixedHeight(HEADER_HEIGHT)
        header.setStyleSheet(f"""
            background-color: {GLASS_HEADER};
            border-top-left-radius: {WINDOW_RADIUS}px;
            border-top-right-radius: {WINDOW_RADIUS}px;
        """)

        h = QHBoxLayout(header)
        h.setContentsMargins(14, 0, 10, 0)
        h.setSpacing(8)

        # Live state dot
        self._header_dot = QLabel("●")
        self._header_dot.setFont(QFont(FONT_MONO, 9))
        self._header_dot.setStyleSheet(
            f"color: {ORB_IDLE[0]}; background: transparent;")

        # Title
        title = QLabel("ROLEX")
        title.setFont(QFont(FONT_TITLE, SIZE_LG, QFont.Weight.Bold))
        title.setStyleSheet(
            f"color: {TEXT_PRIMARY}; background: transparent; letter-spacing: 4px;")

        sub = QLabel("personal ai  ·  local")
        sub.setFont(QFont(FONT_BODY, SIZE_SM - 1))
        sub.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")

        name_col = QVBoxLayout()
        name_col.setSpacing(0)
        name_col.addWidget(title)
        name_col.addWidget(sub)

        # Minimize button
        min_btn = QPushButton("—")
        min_btn.setFixedSize(26, 26)
        min_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        min_btn.setStyleSheet(f"""
            QPushButton {{
                color: {TEXT_SECONDARY}; background: transparent;
                border: 1px solid {GLASS_BORDER}; border-radius: 13px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                color: {TEXT_PRIMARY}; background: {GLASS_SECTION};
            }}
        """)
        min_btn.clicked.connect(self.showMinimized)

        h.addWidget(self._header_dot)
        h.addLayout(name_col)
        h.addStretch()
        h.addWidget(min_btn)

        return header

    def _build_orb_section(self) -> QWidget:
        section = QWidget()
        section.setFixedHeight(ORB_SECTION_H)
        section.setStyleSheet("background: transparent;")

        self._orb = OrbWidget()

        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._orb)

        return section

    def _build_visualizer_section(self) -> QWidget:
        section = QWidget()
        section.setFixedHeight(VIZ_HEIGHT + 8)
        section.setStyleSheet(f"background-color: {GLASS_SECTION};")

        self._viz = VisualizerWidget()

        layout = QVBoxLayout(section)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.addWidget(self._viz)

        return section

    def _build_chat_section(self) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{
                background: transparent; width: 3px; margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {GLASS_BORDER}; border-radius: 1px; min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """)

        self._chat_container = QWidget()
        self._chat_container.setStyleSheet("background: transparent;")
        self._chat_layout = QVBoxLayout(self._chat_container)
        self._chat_layout.setContentsMargins(0, 8, 0, 8)
        self._chat_layout.setSpacing(3)
        self._chat_layout.addStretch()

        scroll.setWidget(self._chat_container)
        self._scroll = scroll
        return scroll

    def _build_status_bar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(STATUS_HEIGHT)
        bar.setStyleSheet(f"""
            background-color: {GLASS_HEADER};
            border-bottom-left-radius: {WINDOW_RADIUS}px;
            border-bottom-right-radius: {WINDOW_RADIUS}px;
        """)

        h = QHBoxLayout(bar)
        h.setContentsMargins(14, 0, 14, 0)
        h.setSpacing(6)

        self._status_dot = QLabel("●")
        self._status_dot.setFont(QFont(FONT_MONO, 8))
        self._status_dot.setStyleSheet(
            f"color: {ORB_IDLE[0]}; background: transparent;")

        self._status_lbl = QLabel("Idle — ready")
        self._status_lbl.setFont(QFont(FONT_BODY, SIZE_SM))
        self._status_lbl.setStyleSheet(
            f"color: {TEXT_SECONDARY}; background: transparent;")

        # Transcript text (right side, italic)
        self._transcript_lbl = QLabel("")
        self._transcript_lbl.setFont(QFont(FONT_MONO, SIZE_SM - 1))
        self._transcript_lbl.setStyleSheet(
            f"color: {TEXT_DIM}; background: transparent;")
        self._transcript_lbl.setAlignment(Qt.AlignmentFlag.AlignRight |
                                          Qt.AlignmentFlag.AlignVCenter)

        h.addWidget(self._status_dot)
        h.addWidget(self._status_lbl)
        h.addStretch()
        h.addWidget(self._transcript_lbl)

        return bar

    # ── Public API (called from app.py via signals) ────────────────────────────

    def set_state(self, state: str):
        self._state = state
        self._orb.set_state(state)
        self._viz.set_state(state)
        self._update_status_bar(state)
        self._update_header_dot(state)

    def _update_status_bar(self, state: str):
        info = {
            "idle":      ("Idle — ready",       ORB_IDLE[0]),
            "listening": ("Listening...",        ORB_LISTENING[0]),
            "thinking":  ("Thinking...",         ORB_THINKING[0]),
            "speaking":  ("Speaking...",         ORB_SPEAKING[0]),
            "web":       ("Searching web...",    ORB_WEB[0]),
            "camera":    ("Camera active...",    ORB_CAMERA[0]),
            "vision":    ("Analysing screen...", ORB_VISION[0]),
            "error":     ("Error",               ORB_ERROR[0]),
        }
        label, colour = info.get(state, ("Idle", ORB_IDLE[0]))
        self._status_lbl.setText(label)
        self._status_dot.setStyleSheet(
            f"color: {colour}; background: transparent;")
        self._status_lbl.setStyleSheet(
            f"color: {colour}; background: transparent;")

    def _update_header_dot(self, state: str):
        colour = {
            "idle":      ORB_IDLE[0],
            "listening": ORB_LISTENING[0],
            "thinking":  ORB_THINKING[0],
            "speaking":  ORB_SPEAKING[0],
            "web":       ORB_WEB[0],
            "camera":    ORB_CAMERA[0],
            "vision":    ORB_VISION[0],
            "error":     ORB_ERROR[0],
        }.get(state, ORB_IDLE[0])
        self._header_dot.setStyleSheet(
            f"color: {colour}; background: transparent;")

    def set_transcript(self, text: str):
        if len(text) > 38:
            text = text[-35:] + "..."
        self._transcript_lbl.setText(text)

    def set_viz_levels(self, levels: list):
        self._viz.set_levels(levels)

    def add_message(self, text: str, is_user: bool, mode: str = "brain"):
        bubble = BubbleWidget(text, is_user, mode)
        count  = self._chat_layout.count()
        self._chat_layout.insertWidget(count - 1, bubble)
        # Scroll to bottom
        self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum())

    def clear_chat(self):
        while self._chat_layout.count() > 1:
            item = self._chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    # ── Drag to reposition ────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, '_drag_pos'):
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        if hasattr(self, '_drag_pos'):
            del self._drag_pos
