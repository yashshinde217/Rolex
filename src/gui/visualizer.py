"""
visualizer.py — Mic audio visualizer bar widget

Draws animated vertical bars that react to microphone input level.
When not listening, bars animate in a gentle idle wave.
"""

import math
import random
from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtCore    import Qt, QTimer, QRectF
from PyQt6.QtGui     import QPainter, QColor, QLinearGradient, QBrush
from .theme import *


class VisualizerWidget(QWidget):
    """Animated mic level bar visualizer."""

    def __init__(self):
        super().__init__()
        self.setFixedHeight(VIZ_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._state      = "idle"
        self._levels     = [0.0] * VIZ_BAR_COUNT   # 0.0 – 1.0 per bar
        self._targets    = [0.0] * VIZ_BAR_COUNT   # smoothing targets
        self._phase      = 0.0                      # idle wave phase

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(30)   # ~33fps is enough for bars

    def set_state(self, state: str):
        self._state = state

    def set_levels(self, levels: list):
        """Feed raw mic bar levels (list of floats 0–1)."""
        self._targets = list(levels)[:VIZ_BAR_COUNT]
        while len(self._targets) < VIZ_BAR_COUNT:
            self._targets.append(0.0)

    def _tick(self):
        self._phase += 0.06

        if self._state == "listening":
            # Smooth current levels toward targets
            for i in range(VIZ_BAR_COUNT):
                diff = self._targets[i] - self._levels[i]
                self._levels[i] += diff * 0.35
        else:
            # Gentle idle sine wave
            for i in range(VIZ_BAR_COUNT):
                wave = math.sin(self._phase + i * 0.5) * 0.5 + 0.5
                self._levels[i] = 0.06 + wave * 0.08

        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        n = VIZ_BAR_COUNT

        bar_w     = max(2, (w - (n + 1) * 3) / n)
        gap       = (w - n * bar_w) / (n + 1)
        max_bar_h = h - 12
        cy        = h / 2

        # Pick colour from current state
        colour_map = {
            "idle":      ORB_IDLE[0],
            "listening": ORB_LISTENING[0],
            "thinking":  ORB_THINKING[0],
            "speaking":  ORB_SPEAKING[0],
            "web":       ORB_WEB[0],
            "camera":    ORB_CAMERA[0],
            "vision":    ORB_VISION[0],
            "error":     ORB_ERROR[0],
        }
        base_colour = colour_map.get(self._state, ORB_IDLE[0])

        for i in range(n):
            level  = max(0.04, min(1.0, self._levels[i]))
            bar_h  = max_bar_h * level
            x      = gap + i * (bar_w + gap)
            y      = cy - bar_h / 2

            # Gradient per bar: bright top, dim bottom
            grad = QLinearGradient(x, y, x, y + bar_h)
            top  = QColor(base_colour)
            top.setAlphaF(0.9)
            bot  = QColor(base_colour)
            bot.setAlphaF(0.25)
            grad.setColorAt(0.0, top)
            grad.setColorAt(1.0, bot)

            p.setBrush(QBrush(grad))
            p.setPen(Qt.PenStyle.NoPen)
            radius = bar_w / 2
            p.drawRoundedRect(QRectF(x, y, bar_w, bar_h), radius, radius)

        p.end()
