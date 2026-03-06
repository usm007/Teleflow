import random
import string
import math
from PySide6.QtWidgets import QLabel, QProgressBar, QListWidget, QFrame, QWidget
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF, QRect
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath, QFont, QBrush

# --- 1. SCANLINE OVERLAY ---
class ScanlineOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.offset = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._scroll)
        self.timer.start(30)

    def _scroll(self):
        self.offset = (self.offset + 2) % 4
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QColor(0, 0, 0, 40))
        for y in range(self.offset, self.height(), 4):
            painter.drawLine(0, y, self.width(), y)

# --- 2. TERMINAL LOG ---
class TerminalLog(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWordWrap(True)
        self.setStyleSheet("""
            background-color: #0d0d0d; border: 1px solid #333; 
            color: #00ff41; font-family: 'Consolas'; font-size: 10px;
        """)
    def add_entry(self, text, color=None):
        self.addItem(f">> {text}")
        if color: self.item(self.count()-1).setForeground(QBrush(QColor(color)))
        self.scrollToBottom()
        if self.count() > 50: self.takeItem(0)

# --- 3. CYBER HEX STREAM ---
class CyberHexStream(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lines = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update)
        self.timer.start(300) 
    def _update(self):
        chars = "0123456789ABCDEF"
        cols = max(1, self.width() // 28)
        max_lines = max(1, self.height() // 18)
        self.lines.append(" ".join(["".join(random.choices(chars, k=2)) for _ in range(cols)]))
        while len(self.lines) > max_lines: self.lines.pop(0)
        self.update()
    def paintEvent(self, event):
        painter = QPainter(self); painter.setFont(QFont("Consolas", 10, QFont.Bold))
        for i, line in enumerate(self.lines):
            alpha = int(255 * ((i + 1) / len(self.lines)))
            painter.setPen(QColor(76, 175, 80, alpha))
            painter.drawText(10, (i + 1) * 18, line)

# --- 4. DECRYPT LABEL ---
class DecryptLabel(QLabel):
    def __init__(self, text="", parent=None, size=18):
        super().__init__(text, parent); self.final_text = text; self.steps = 0
        self.setStyleSheet(f"color: #4caf50; font-weight: bold; font-size: {size}px; font-family: 'Consolas';")
        self.timer = QTimer(self); self.timer.timeout.connect(self._scramble)
    def setText(self, text): self.final_text = text; self.steps = 0; self.timer.start(30)
    def _scramble(self):
        self.steps += 1
        if self.steps > 20: self.timer.stop(); super().setText(self.final_text); return
        chars = string.ascii_uppercase + string.digits + "#%&"
        super().setText("".join(random.choice(chars) if self.final_text[i] != " " and i >= (self.steps // 2) else self.final_text[i] for i in range(len(self.final_text))))

# --- 5. PROGRESS BAR ---
class HackerProgressBar(QProgressBar):
    def __init__(self, parent=None): super().__init__(parent); self.setFixedHeight(35)
    def paintEvent(self, event):
        painter = QPainter(self); rect = self.rect(); painter.setBrush(QColor("#111")); painter.drawRect(rect)
        inner = rect.adjusted(3,3,-3,-3); val = self.value() / (self.maximum() or 100)
        painter.setBrush(QColor("#4caf50")); painter.drawRect(inner.x(), inner.y(), int(inner.width()*val), inner.height())
        painter.setPen(QColor("#fff")); painter.drawText(rect, Qt.AlignCenter, f"{int(val*100)}%")

# --- 6. CYBER GRAPH ---
class CyberGraph(QWidget):
    def __init__(self, parent=None): super().__init__(parent); self.values = [0] * 50
    def update_value(self, v): self.values.append(v); self.values.pop(0); self.update()
    def paintEvent(self, event):
        painter = QPainter(self); w, h = self.width(), self.height()
        path = QPainterPath(); step = w / (len(self.values)-1); path.moveTo(0, h-(self.values[0]/100*h))
        for i, v in enumerate(self.values): path.lineTo(i*step, h-(v/100*h))
        painter.setPen(QPen(QColor(76, 175, 80), 2)); painter.drawPath(path)

# --- 7. MATRIX LOADER (THE REACTOR) ---
class MatrixLoader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle_outer = 0
        self.angle_inner = 0
        self.pulse = 0
        self.found_count = 0
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(16) # ~60 FPS

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
        
        # 1. Background (Subtle radial gradient)
        # grad = QRadialGradient(self.rect().center(), self.width()/2)
        # grad.setColorAt(0, QColor(0, 30, 0))
        # grad.setColorAt(1, QColor(10, 10, 10))
        # painter.fillRect(self.rect(), QBrush(grad))
        painter.fillRect(self.rect(), QColor(10, 10, 10))

        center_x = self.width() / 2
        center_y = self.height() / 2
        anim_y = center_y - 40 # Shift animation up slightly
        
        # 2. Draw Animation (The Reactor)
        painter.save()
        painter.translate(center_x, anim_y)
        
        # Ring 1 (Static Track)
        painter.setPen(QPen(QColor(0, 255, 65, 30), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QPointF(0,0), 60, 60)
        
        # Ring 2 (Outer Rotating)
        painter.rotate(self.angle_outer)
        painter.setPen(QPen(QColor(0, 255, 65), 3, Qt.SolidLine, Qt.RoundCap))
        # Draw 3 arcs
        painter.drawArc(QRectF(-60, -60, 120, 120), 0, 100 * 16)
        painter.drawArc(QRectF(-60, -60, 120, 120), 120 * 16, 100 * 16)
        painter.drawArc(QRectF(-60, -60, 120, 120), 240 * 16, 100 * 16)
        
        # Ring 3 (Inner Rotating Counter)
        painter.rotate(-self.angle_outer - self.angle_inner) # Undo previous rotate, then rotate back
        painter.setPen(QPen(QColor(0, 255, 65, 180), 5, Qt.SolidLine, Qt.FlatCap))
        painter.drawArc(QRectF(-40, -40, 80, 80), 0, 270 * 16)
        
        # Core (Pulsing)
        painter.rotate(self.angle_inner) # Reset rotation
        pulse_size = 15 + math.sin(self.pulse) * 3
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 255, 65, 200))
        painter.drawEllipse(QPointF(0,0), pulse_size, pulse_size)
        
        painter.restore()

        # 3. Draw Count (Below Animation)
        painter.setPen(QColor(0, 255, 65))
        painter.setFont(QFont("Consolas", 48, QFont.Bold))
        
        count_str = f"{self.found_count}"
        fm = painter.fontMetrics()
        text_w = fm.horizontalAdvance(count_str)
        text_h = fm.height()
        
        # Position below animation
        text_y = anim_y + 80 + text_h 
        painter.drawText(center_x - text_w/2, text_y, count_str)
        
        # 4. Draw Label (Below Count)
        painter.setPen(QColor(0, 255, 65, 150)) # Dimmer green
        painter.setFont(QFont("Consolas", 12))
        lbl_str = "PAYLOADS DETECTED"
        fm2 = painter.fontMetrics()
        lbl_w = fm2.horizontalAdvance(lbl_str)
        
        painter.drawText(center_x - lbl_w/2, text_y + 20, lbl_str)

# --- 8. GLOBAL LOADING OVERLAY ---
class CyberLoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False) # Block inputs
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.angle = 0
        self.text = "PROCESSING..."
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.hide()

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
        p.fillRect(self.rect(), QColor(0, 0, 0, 220)) # Dark Overlay

        center = QPointF(self.width()/2, self.height()/2)
        radius = 45

        # Draw Spinning Arcs
        p.setPen(QPen(QColor("#4caf50"), 4, Qt.SolidLine, Qt.RoundCap))
        # Outer Ring
        p.drawArc(QRectF(center.x()-radius, center.y()-radius, radius*2, radius*2), -self.angle * 16, 120 * 16)
        p.drawArc(QRectF(center.x()-radius, center.y()-radius, radius*2, radius*2), -(self.angle + 180) * 16, 120 * 16)
        
        # Inner Ring
        radius_in = 30
        p.setPen(QPen(QColor("#00ff41"), 2, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(QRectF(center.x()-radius_in, center.y()-radius_in, radius_in*2, radius_in*2), (self.angle * 2) * 16, 260 * 16)

        # Draw Text
        p.setFont(QFont("Consolas", 14, QFont.Bold))
        p.setPen(QColor("white"))
        fm = p.fontMetrics()
        tw = fm.horizontalAdvance(self.text)
        p.drawText(center.x() - tw/2, center.y() + radius + 40, self.text)
