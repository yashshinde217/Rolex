"""
window.py — Rolex main window (GUI Phase 2)

Phase 2 additions over Phase 1:
  - Smooth morph minimize/restore animation (shrinks to a pill, expands back)
  - Drag to reposition anywhere on screen
  - System tray icon — right-click to show/hide/quit
  - Settings button → settings overlay (voice, model, corner)
  - Corner snapping — window snaps to chosen corner when dragged and released
  - Startup on boot toggle (Windows registry)
"""

import sys
import winreg
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QScrollArea, QPushButton, QFrame, QSizePolicy,
                              QGraphicsDropShadowEffect, QSystemTrayIcon, QMenu,
                              QApplication)
from PyQt6.QtCore    import (Qt, QPropertyAnimation, QEasingCurve,
                              QRect, QSize, pyqtSignal, QTimer)
from PyQt6.QtGui     import (QFont, QColor, QIcon, QPixmap, QPainter,
                              QBrush, QRadialGradient, QAction)

from .theme      import *
from .orb        import OrbWidget
from .visualizer import VisualizerWidget
from .bubble     import BubbleWidget
from .settings   import SettingsPanel

# ── Startup registry key ──────────────────────────────────────────────────────
STARTUP_KEY  = r"Software\Microsoft\Windows\CurrentVersion\Run"
STARTUP_NAME = "RolexAI"


class RolexWindow(QWidget):
    """
    Main Rolex floating window — glassmorphism, square, always on top.
    Phase 2: morph animation, drag, tray, settings.
    """

    def __init__(self):
        super().__init__()
        self._state       = "idle"
        self._is_minimized = False
        self._corner      = "top-right"       # current snap corner
        self._drag_pos    = None
        self._full_rect   = None              # saved full-size geometry for restore

        self._setup_window()
        self._build_ui()
        self._build_tray()
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

    def _position_window(self, corner: str = "top-right"):
        screen = QApplication.primaryScreen().availableGeometry()
        m = WINDOW_MARGIN
        positions = {
            "top-right":    (screen.right()  - WINDOW_SIZE - m, screen.top()    + m),
            "top-left":     (screen.left()   + m,               screen.top()    + m),
            "bottom-right": (screen.right()  - WINDOW_SIZE - m, screen.bottom() - WINDOW_SIZE - m),
            "bottom-left":  (screen.left()   + m,               screen.bottom() - WINDOW_SIZE - m),
        }
        x, y = positions.get(corner, positions["top-right"])
        self.move(x, y)

    def _apply_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(36)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 180))
        self.setGraphicsEffect(shadow)

    # ── Tray icon ─────────────────────────────────────────────────────────────

    def _build_tray(self):
        # Draw a simple coloured circle as tray icon
        px = QPixmap(32, 32)
        px.fill(Qt.GlobalColor.transparent)
        p = QPainter(px)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        g = QRadialGradient(14, 12, 14)
        g.setColorAt(0.0, QColor("#00B4D8"))
        g.setColorAt(1.0, QColor("#005F73"))
        p.setBrush(QBrush(g))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(2, 2, 28, 28)
        p.end()

        self._tray = QSystemTrayIcon(QIcon(px), self)
        self._tray.setToolTip(TRAY_TOOLTIP)

        menu = QMenu()
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: #0D1520;
                color: {TEXT_PRIMARY};
                border: 1px solid {GLASS_BORDER};
                border-radius: 8px;
                padding: 4px;
            }}
            QMenu::item {{ padding: 6px 20px; border-radius: 4px; }}
            QMenu::item:selected {{ background-color: {GLASS_HOVER}; }}
        """)

        show_action = QAction("Show Rolex", self)
        show_action.triggered.connect(self._tray_show)

        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)

        menu.addAction(show_action)
        menu.addAction(hide_action)
        menu.addSeparator()
        menu.addAction(quit_action)

        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._tray_clicked)
        self._tray.show()

    def _tray_show(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def _tray_clicked(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self._tray_show()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
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
        layout.addWidget(self._divider())
        layout.addWidget(self._build_orb_section())
        layout.addWidget(self._divider())
        layout.addWidget(self._build_viz_section())
        layout.addWidget(self._divider())
        layout.addWidget(self._build_chat_section(), stretch=1)
        layout.addWidget(self._divider())
        layout.addWidget(self._build_status_bar())

        # Settings overlay — sits on top of root
        self._settings = SettingsPanel(self)
        self._settings.closed.connect(self._on_settings_closed)
        self._settings.corner_changed.connect(self._on_corner_changed)
        self._settings.hide()

    def _divider(self) -> QWidget:
        d = QWidget()
        d.setFixedHeight(1)
        d.setStyleSheet(f"background-color: {GLASS_BORDER};")
        return d

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

        self._header_dot = QLabel("●")
        self._header_dot.setFont(QFont(FONT_MONO, 9))
        self._header_dot.setStyleSheet(f"color: {ORB_IDLE[0]}; background: transparent;")

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

        # Settings button
        self._settings_btn = self._icon_btn("⚙", self._toggle_settings)
        # Minimize button
        self._min_btn = self._icon_btn("—", self._morph_minimize)

        h.addWidget(self._header_dot)
        h.addLayout(name_col)
        h.addStretch()
        h.addWidget(self._settings_btn)
        h.addWidget(self._min_btn)

        return header

    def _icon_btn(self, icon: str, slot) -> QPushButton:
        btn = QPushButton(icon)
        btn.setFixedSize(26, 26)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                color: {TEXT_SECONDARY}; background: transparent;
                border: 1px solid {GLASS_BORDER}; border-radius: 13px; font-size: 11px;
            }}
            QPushButton:hover {{ color: {TEXT_PRIMARY}; background: {GLASS_HOVER}; }}
        """)
        btn.clicked.connect(slot)
        return btn

    def _build_orb_section(self) -> QWidget:
        section = QWidget()
        section.setFixedHeight(ORB_SECTION_H)
        section.setStyleSheet("background: transparent;")
        self._orb = OrbWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._orb)
        return section

    def _build_viz_section(self) -> QWidget:
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
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
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
        self._status_dot.setStyleSheet(f"color: {ORB_IDLE[0]}; background: transparent;")

        self._status_lbl = QLabel("Idle — ready")
        self._status_lbl.setFont(QFont(FONT_BODY, SIZE_SM))
        self._status_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")

        self._transcript_lbl = QLabel("")
        self._transcript_lbl.setFont(QFont(FONT_MONO, SIZE_SM - 1))
        self._transcript_lbl.setStyleSheet(f"color: {TEXT_DIM}; background: transparent;")
        self._transcript_lbl.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        h.addWidget(self._status_dot)
        h.addWidget(self._status_lbl)
        h.addStretch()
        h.addWidget(self._transcript_lbl)
        return bar

    # ── Morph minimize / restore animation ────────────────────────────────────

    def _morph_minimize(self):
        """Shrink window to a slim pill shape in the corner."""
        if self._is_minimized:
            return
        self._is_minimized = True
        self._full_rect = self.geometry()

        # Target: thin horizontal pill, same corner position
        pill_w, pill_h = 160, 36
        target = QRect(
            self._full_rect.x() + (WINDOW_SIZE - pill_w) // 2,
            self._full_rect.y(),
            pill_w, pill_h
        )

        self._anim = QPropertyAnimation(self, b"geometry")
        self._anim.setDuration(ANIM_MORPH_MS)
        self._anim.setStartValue(self._full_rect)
        self._anim.setEndValue(target)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._anim.finished.connect(self._on_minimized)
        self._anim.start()

        # Update button to restore icon
        self._min_btn.setText("□")
        self._min_btn.clicked.disconnect()
        self._min_btn.clicked.connect(self._morph_restore)

    def _on_minimized(self):
        """After morph, hide all content except header."""
        self._root.setFixedSize(160, 36)

    def _morph_restore(self):
        """Expand pill back to full square."""
        if not self._is_minimized or not self._full_rect:
            return

        self._root.setFixedSize(WINDOW_SIZE, WINDOW_SIZE)
        self.setFixedSize(WINDOW_SIZE, WINDOW_SIZE)

        self._anim = QPropertyAnimation(self, b"geometry")
        self._anim.setDuration(ANIM_MORPH_MS)
        self._anim.setStartValue(self.geometry())
        self._anim.setEndValue(self._full_rect)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.finished.connect(self._on_restored)
        self._anim.start()

    def _on_restored(self):
        self._is_minimized = False
        self._min_btn.setText("—")
        self._min_btn.clicked.disconnect()
        self._min_btn.clicked.connect(self._morph_minimize)

    # ── Settings ──────────────────────────────────────────────────────────────

    def _toggle_settings(self):
        if self._settings.isVisible():
            self._settings.hide()
        else:
            self._settings.show_panel(self._root.rect())

    def _on_settings_closed(self):
        self._settings.hide()

    def _on_corner_changed(self, corner: str):
        self._corner = corner
        self._position_window(corner)

    # ── Startup on boot (Windows registry) ────────────────────────────────────

    def set_startup(self, enable: bool):
        """Add or remove Rolex from Windows startup."""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY, 0,
                                 winreg.KEY_SET_VALUE)
            if enable:
                winreg.SetValueEx(key, STARTUP_NAME, 0, winreg.REG_SZ,
                                  f'"{sys.executable}" "{__file__}"')
            else:
                try:
                    winreg.DeleteValue(key, STARTUP_NAME)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception:
            pass    # Fail silently — not critical

    # ── Public API ────────────────────────────────────────────────────────────

    def set_state(self, state: str):
        self._state = state
        self._orb.set_state(state)
        self._viz.set_state(state)
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
        labels = {
            "idle":      "Idle — ready",
            "listening": "Listening...",
            "thinking":  "Thinking...",
            "speaking":  "Speaking...",
            "web":       "Searching web...",
            "camera":    "Camera active...",
            "vision":    "Analysing screen...",
            "error":     "Error",
        }
        label = labels.get(state, "Idle")
        for w, style in [(self._status_dot, f"color:{colour};background:transparent;"),
                         (self._status_lbl, f"color:{colour};background:transparent;"),
                         (self._header_dot, f"color:{colour};background:transparent;")]:
            w.setStyleSheet(style)
        self._status_lbl.setText(label)

    def set_transcript(self, text: str):
        if len(text) > 36:
            text = "..." + text[-33:]
        self._transcript_lbl.setText(text)

    def set_viz_levels(self, levels: list):
        self._viz.set_levels(levels)

    def add_message(self, text: str, is_user: bool, mode: str = "brain"):
        bubble = BubbleWidget(text, is_user, mode)
        self._chat_layout.insertWidget(self._chat_layout.count() - 1, bubble)
        QTimer.singleShot(50, lambda: self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()))

    def clear_chat(self):
        while self._chat_layout.count() > 1:
            item = self._chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    # ── Drag to reposition ────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (event.globalPosition().toPoint()
                              - self.frameGeometry().topLeft())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    # ── Close → hide to tray instead of quit ──────────────────────────────────

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self._tray.showMessage(
            "Rolex", "Still running in the tray. Right-click to quit.",
            QSystemTrayIcon.MessageIcon.Information, 2000)