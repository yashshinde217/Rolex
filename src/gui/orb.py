"""
orb.py — Orb widget (lives inside the main window, not standalone)

Draws the animated orb and state label.
All animations run at 60fps via a QTimer.
"""

import math
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore    import Qt, QTimer, QRectF
from PyQt6.QtGui     import QPainter, QColor, QRadialGradient, QPen, QBrush, QFont
from .theme import *


class OrbWidget(QWidget):
    """Animated orb + state label — embedded inside the main window."""

    def __init__(self):
        super().__init__()
        self.state       = "idle"
        self._tick       = 0.0
        self._spin_angle = 0.0
        self._ripples    = []        # [(progress, opacity), ...]
        self._viz_levels = [0.0] * VIZ_BAR_COUNT   # mic bar heights

        self.setFixedHeight(ORB_SECTION_H)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # State label below orb
        self._label = QLabel("Idle")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setFont(QFont(FONT_MONO, SIZE_SM))
        self._label.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 4)
        layout.addStretch()
        layout.addWidget(self._label)

        # 60fps timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_tick)
        self._timer.start(16)

        # Ripple spawner
        self._ripple_timer = QTimer(self)
        self._ripple_timer.timeout.connect(self._spawn_ripple)
        self._ripple_timer.start(550)

    def set_state(self, state: str):
        self.state = state
        if state != "listening":
            self._ripples = []
        labels = {
            "idle":      "Idle",
            "listening": "Listening...",
            "thinking":  "Thinking...",
            "speaking":  "Speaking...",
            "web":       "Searching web...",
            "camera":    "Camera active...",
            "vision":    "Analysing screen...",
            "error":     "Error",
        }
        self._label.setText(labels.get(state, "Idle"))
        colour = self._get_primary()
        self._label.setStyleSheet(f"color: {colour}; background: transparent;")

    def set_viz_levels(self, levels: list):
        """Update mic visualizer bar heights (0.0–1.0 each)."""
        self._viz_levels = levels
        self.update()

    def _get_primary(self):
        return {
            "idle":      ORB_IDLE[0],
            "listening": ORB_LISTENING[0],
            "thinking":  ORB_THINKING[0],
            "speaking":  ORB_SPEAKING[0],
            "web":       ORB_WEB[0],
            "camera":    ORB_CAMERA[0],
            "vision":    ORB_VISION[0],
            "error":     ORB_ERROR[0],
        }.get(self.state, ORB_IDLE[0])

    def _get_colours(self):
        return {
            "idle":      ORB_IDLE,
            "listening": ORB_LISTENING,
            "thinking":  ORB_THINKING,
            "speaking":  ORB_SPEAKING,
            "web":       ORB_WEB,
            "camera":    ORB_CAMERA,
            "vision":    ORB_VISION,
            "error":     ORB_ERROR,
        }.get(self.state, ORB_IDLE)

    def _on_tick(self):
        dt = 0.016
        self._tick = (self._tick + dt / (ANIM_PULSE_MS / 1000)) % 1.0
        if self.state == "thinking":
            self._spin_angle = (self._spin_angle + 2.8) % 360
        new_r = []
        for p, o in self._ripples:
            p += dt / (ANIM_RIPPLE_MS / 1000)
            if p < 1.0:
                new_r.append((p, max(0.0, 1.0 - p)))
        self._ripples = new_r
        self.update()

    def _spawn_ripple(self):
        if self.state == "listening":
            self._ripples.append((0.0, 1.0))

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Centre point — upper portion of widget (leave room for label)
        cx = self.width() / 2
        cy = (self.height() - 24) / 2   # 24px for label
        r  = ORB_SIZE / 2

        primary, glow = self._get_colours()

        # Glow
        pulse = 0.35 + 0.25 * math.sin(self._tick * 2 * math.pi)
        gr = QRadialGradient(cx, cy, r * 1.9)
        gc = QColor(glow); gc.setAlphaF(pulse * 0.6)
        gc2 = QColor(glow); gc2.setAlphaF(0.0)
        gr.setColorAt(0.0, gc); gr.setColorAt(1.0, gc2)
        p.setBrush(QBrush(gr)); p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QRectF(cx - r*1.9, cy - r*1.9, r*3.8, r*3.8))

        # Ripples
        for prog, opac in self._ripples:
            rr = r * (1.0 + prog * 1.4)
            rc = QColor(primary); rc.setAlphaF(opac * 0.35)
            pen = QPen(rc); pen.setWidthF(1.2)
            p.setPen(pen); p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QRectF(cx-rr, cy-rr, rr*2, rr*2))

        # Orb body
        scale = 1.0 + (0.025 * math.sin(self._tick * 2 * math.pi)
                        if self.state == "idle" else 0)
        rs = r * scale
        bg = QRadialGradient(cx - r*0.2, cy - r*0.25, rs * 1.1)
        bg.setColorAt(0.0, QColor(primary).lighter(170))
        bg.setColorAt(0.5, QColor(primary))
        bg.setColorAt(1.0, QColor(glow))
        p.setBrush(QBrush(bg)); p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QRectF(cx-rs, cy-rs, rs*2, rs*2))

        # Spinner (thinking)
        if self.state == "thinking":
            ar = r * 1.22
            sc = QColor(primary).lighter(200); sc.setAlphaF(0.9)
            pen = QPen(sc); pen.setWidthF(2.2)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen); p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawArc(QRectF(cx-ar, cy-ar, ar*2, ar*2),
                      int(self._spin_angle * 16), 100 * 16)
            sc2 = QColor(primary); sc2.setAlphaF(0.25)
            pen2 = QPen(sc2); pen2.setWidthF(1.4)
            p.setPen(pen2)
            p.drawArc(QRectF(cx-ar, cy-ar, ar*2, ar*2),
                      int(self._spin_angle * 16) + 140*16, 55*16)

        # Speaking rings
        if self.state == "speaking":
            for i in range(3):
                off = (self._tick + i / 3.0) % 1.0
                rr  = r * (1.05 + off * 0.55)
                rc  = QColor(primary); rc.setAlphaF((1.0 - off) * 0.45)
                pen = QPen(rc); pen.setWidthF(1.1)
                p.setPen(pen); p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawEllipse(QRectF(cx-rr, cy-rr, rr*2, rr*2))

        # Highlight
        hr = r * 0.32
        hx, hy = cx - r*0.16, cy - r*0.2
        hg = QRadialGradient(hx, hy, hr)
        hg.setColorAt(0.0, QColor(255, 255, 255, 55))
        hg.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setBrush(QBrush(hg)); p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QRectF(hx-hr, hy-hr, hr*2, hr*2))

        p.end()