import random
import string
import math
from PySide6.QtWidgets import QLabel, QProgressBar, QListWidget, QFrame, QWidget
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath, QFont, QBrush
from themes import get_theme


def _with_alpha(hex_color, alpha):
    color = QColor(hex_color)
    color.setAlpha(max(0, min(255, alpha)))
    return color

# --- 1. SCANLINE OVERLAY ---
class ScanlineOverlay(QWidget):
    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        self.theme = theme or get_theme("dark")
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.offset = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._scroll)
        self.timer.start(30)

    def set_theme(self, theme):
        self.theme = theme
        self.update()

    def _scroll(self):
        self.offset = (self.offset + 2) % 4
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(_with_alpha(self.theme["text"], self.theme["scanline_alpha"]))
        for y in range(self.offset, self.height(), 4):
            painter.drawLine(0, y, self.width(), y)

# --- 2. TERMINAL LOG ---
class TerminalLog(QListWidget):
    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        self.theme = theme or get_theme("dark")
        self.setWordWrap(True)
        self._apply_style()

    def set_theme(self, theme):
        self.theme = theme
        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet(
            f"""
            background-color: {self.theme['terminal_bg']};
            border: 1px solid {self.theme['border']};
            color: {self.theme['success']};
            font-family: 'Consolas';
            font-size: 10px;
            """
        )

    def add_entry(self, text, color=None):
        self.addItem(f">> {text}")
        entry_color = QColor(color) if color else QColor(self.theme["success"])
        self.item(self.count() - 1).setForeground(QBrush(entry_color))
        self.scrollToBottom()
        if self.count() > 50:
            self.takeItem(0)

# --- 3. CYBER HEX STREAM ---
class CyberHexStream(QWidget):
    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        self.theme = theme or get_theme("dark")
        self.lines = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update)
        self.timer.start(300)

    def set_theme(self, theme):
        self.theme = theme
        self.update()

    def _update(self):
        chars = "0123456789ABCDEF"
        cols = max(1, self.width() // 28)
        max_lines = max(1, self.height() // 18)
        self.lines.append(" ".join(["".join(random.choices(chars, k=2)) for _ in range(cols)]))
        while len(self.lines) > max_lines:
            self.lines.pop(0)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(QFont("Consolas", 10, QFont.Bold))
        for i, line in enumerate(self.lines):
            alpha = int(255 * ((i + 1) / len(self.lines)))
            painter.setPen(_with_alpha(self.theme["success"], alpha))
            painter.drawText(10, (i + 1) * 18, line)

# --- 4. DECRYPT LABEL ---
class DecryptLabel(QLabel):
    def __init__(self, text="", parent=None, size=18, theme=None):
        super().__init__(text, parent)
        self.theme = theme or get_theme("dark")
        self.size = size
        self.final_text = text
        self.steps = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._scramble)
        self._apply_style()

    def set_theme(self, theme):
        self.theme = theme
        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet(
            (
                f"color: {self.theme['accent']};"
                f" font-weight: 700;"
                f" font-size: {self.size}px;"
                " font-family: 'Consolas';"
            )
        )

    def setText(self, text):
        self.final_text = text
        self.steps = 0
        self.timer.start(30)

    def _scramble(self):
        self.steps += 1
        if self.steps > 20:
            self.timer.stop()
            super().setText(self.final_text)
            return
        chars = string.ascii_uppercase + string.digits + "#%&"
        super().setText(
            "".join(
                random.choice(chars)
                if self.final_text[i] != " " and i >= (self.steps // 2)
                else self.final_text[i]
                for i in range(len(self.final_text))
            )
        )

# --- 5. PROGRESS BAR ---
class HackerProgressBar(QProgressBar):
    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        self.theme = theme or get_theme("dark")
        self.setFixedHeight(35)

    def set_theme(self, theme):
        self.theme = theme
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(self.theme["surface_soft"]))
        painter.drawRoundedRect(rect, 8, 8)

        inner = rect.adjusted(3, 3, -3, -3)
        val = self.value() / (self.maximum() or 100)
        painter.setBrush(QColor(self.theme["accent"]))
        painter.drawRoundedRect(inner.x(), inner.y(), int(inner.width() * val), inner.height(), 6, 6)

        painter.setPen(QColor(self.theme["text"]))
        painter.setFont(QFont("Consolas", 10, QFont.Bold))
        painter.drawText(rect, Qt.AlignCenter, f"{int(val * 100)}%")

# --- 6. CYBER GRAPH ---
class CyberGraph(QWidget):
    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        self.theme = theme or get_theme("dark")
        self.values = [0] * 50

    def set_theme(self, theme):
        self.theme = theme
        self.update()

    def update_value(self, v):
        self.values.append(v)
        self.values.pop(0)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        w, h = self.width(), self.height()
        painter.fillRect(self.rect(), QColor(self.theme["surface_elevated"]))

        path = QPainterPath()
        step = w / (len(self.values) - 1)
        path.moveTo(0, h - (self.values[0] / 100 * h))
        for i, v in enumerate(self.values):
            path.lineTo(i * step, h - (v / 100 * h))
        painter.setPen(QPen(_with_alpha(self.theme["accent"], 220), 2))
        painter.drawPath(path)

# --- 7. MATRIX LOADER (THE REACTOR) ---
class MatrixLoader(QWidget):
    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        self.theme = theme or get_theme("dark")
        self.angle_outer = 0
        self.angle_inner = 0
        self.pulse = 0
        self.found_count = 0
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(16)

    def set_theme(self, theme):
        self.theme = theme
        self.update()

    def set_count(self, c):
        self.found_count = c

    def _animate(self):
        self.angle_outer = (self.angle_outer + 2) % 360
        self.angle_inner = (self.angle_inner - 4) % 360
        self.pulse = (self.pulse + 0.1)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.fillRect(self.rect(), QColor(self.theme["surface_alt"]))

        center_x = self.width() / 2
        center_y = self.height() / 2
        anim_y = center_y - 40

        painter.save()
        painter.translate(center_x, anim_y)

        painter.setPen(QPen(_with_alpha(self.theme["accent"], 50), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QPointF(0, 0), 60, 60)

        painter.rotate(self.angle_outer)
        painter.setPen(QPen(QColor(self.theme["accent"]), 3, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(QRectF(-60, -60, 120, 120), 0, 100 * 16)
        painter.drawArc(QRectF(-60, -60, 120, 120), 120 * 16, 100 * 16)
        painter.drawArc(QRectF(-60, -60, 120, 120), 240 * 16, 100 * 16)

        painter.rotate(-self.angle_outer - self.angle_inner)
        painter.setPen(QPen(_with_alpha(self.theme["accent"], 180), 5, Qt.SolidLine, Qt.FlatCap))
        painter.drawArc(QRectF(-40, -40, 80, 80), 0, 270 * 16)

        painter.rotate(self.angle_inner)
        pulse_size = 15 + math.sin(self.pulse) * 3
        painter.setPen(Qt.NoPen)
        painter.setBrush(_with_alpha(self.theme["success"], 200))
        painter.drawEllipse(QPointF(0, 0), pulse_size, pulse_size)

        painter.restore()

        painter.setPen(QColor(self.theme["accent"]))
        painter.setFont(QFont("Consolas", 48, QFont.Bold))
        count_str = f"{self.found_count}"
        fm = painter.fontMetrics()
        text_w = fm.horizontalAdvance(count_str)
        text_h = fm.height()
        text_y = anim_y + 80 + text_h
        painter.drawText(center_x - text_w / 2, text_y, count_str)

        painter.setPen(_with_alpha(self.theme["text_muted"], 180))
        painter.setFont(QFont("Consolas", 12))
        lbl_str = "PAYLOADS DETECTED"
        fm2 = painter.fontMetrics()
        lbl_w = fm2.horizontalAdvance(lbl_str)

        painter.drawText(center_x - lbl_w / 2, text_y + 20, lbl_str)

# --- 8. GLOBAL LOADING OVERLAY ---
class CyberLoadingOverlay(QWidget):
    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        self.theme = theme or get_theme("dark")
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.angle = 0
        self.text = "PROCESSING..."
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.hide()

    def set_theme(self, theme):
        self.theme = theme
        self.update()

    def start(self, text):
        self.text = text
        self.show()
        self.raise_()
        self.timer.start(30)

    def stop(self):
        self.hide()
        self.timer.stop()

    def _animate(self):
        self.angle = (self.angle + 15) % 360
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), _with_alpha(self.theme["overlay"], self.theme["overlay_alpha"]))

        center = QPointF(self.width() / 2, self.height() / 2)
        radius = 45

        p.setPen(QPen(QColor(self.theme["accent"]), 4, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(QRectF(center.x()-radius, center.y()-radius, radius*2, radius*2), -self.angle * 16, 120 * 16)
        p.drawArc(QRectF(center.x()-radius, center.y()-radius, radius*2, radius*2), -(self.angle + 180) * 16, 120 * 16)

        radius_in = 30
        p.setPen(QPen(QColor(self.theme["success"]), 2, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(QRectF(center.x()-radius_in, center.y()-radius_in, radius_in*2, radius_in*2), (self.angle * 2) * 16, 260 * 16)

        p.setFont(QFont("Consolas", 14, QFont.Bold))
        p.setPen(QColor(self.theme["text"]))
        fm = p.fontMetrics()
        tw = fm.horizontalAdvance(self.text)
        p.drawText(center.x() - tw / 2, center.y() + radius + 40, self.text)
