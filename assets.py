from PySide6.QtWidgets import QLabel, QProgressBar, QListWidget, QWidget
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QBrush, QPainterPath, QFontMetrics, QLinearGradient
from themes import get_theme


def _with_alpha(hex_color, alpha):
    color = QColor(hex_color)
    color.setAlpha(max(0, min(255, alpha)))
    return color


def _set_painter_quality(painter):
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.TextAntialiasing, True)
    painter.setRenderHint(QPainter.SmoothPixmapTransform, True)


class ScanlineOverlay(QWidget):
    """Transparent overlay — preserved for compatibility."""

    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        self.theme = theme or get_theme("light")
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def set_theme(self, theme):
        self.theme = theme
        self.update()

    def paintEvent(self, event):
        pass


class TerminalLog(QListWidget):
    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        self.theme = theme or get_theme("light")
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
            border-radius: 8px;
            color: {self.theme['text_muted']};
            font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace;
            font-size: 11px;
            padding: 4px;
            """
        )

    def add_entry(self, text, color=None):
        self.addItem(f"{text}")
        entry_color = QColor(color) if color else QColor(self.theme["text_muted"])
        self.item(self.count() - 1).setForeground(QBrush(entry_color))
        self.scrollToBottom()
        if self.count() > 60:
            self.takeItem(0)


class DecryptLabel(QLabel):
    """Clean heading label."""

    def __init__(self, text="", parent=None, size=18, theme=None):
        super().__init__(text, parent)
        self.theme = theme or get_theme("light")
        self.size = size
        self._apply_style()

    def set_theme(self, theme):
        self.theme = theme
        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet(
            f"color: {self.theme['text']};"
            " font-weight: 700;"
            f" font-size: {self.size}px;"
            f" font-family: '{self.theme['heading_font']}', 'Segoe UI', sans-serif;"
        )

    def setText(self, text):
        super().setText(text)


class HackerProgressBar(QProgressBar):
    """Smooth progress bar — clean emerald fill on dark track."""

    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        self.theme = theme or get_theme("light")
        self.setFixedHeight(6)
        self._display_value = 0.0
        self._target_value = 0.0
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._animate_step)
        self._anim_timer.start(16)

    def set_theme(self, theme):
        self.theme = theme
        self.update()

    def setValue(self, value):
        super().setValue(value)
        self._target_value = max(0.0, min(100.0, float(value)))

    def _animate_step(self):
        delta = self._target_value - self._display_value
        if abs(delta) < 0.3:
            self._display_value = self._target_value
        else:
            self._display_value += delta * 0.18
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        _set_painter_quality(painter)
        rect = self.rect().adjusted(0, 0, -1, -1)
        radius = 3

        # Track
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(self.theme["border"]))
        painter.drawRoundedRect(rect, radius, radius)

        # Fill
        progress = self._display_value / 100.0
        fill_w = int(rect.width() * progress)
        if fill_w > 0:
            fill_rect = QRectF(rect.x(), rect.y(), fill_w, rect.height())

            # Gradient: primary → accent
            grad = QLinearGradient(fill_rect.left(), 0, fill_rect.right(), 0)
            grad.setColorAt(0.0, QColor(self.theme["primary"]))
            grad.setColorAt(1.0, QColor(self.theme["accent"]))

            painter.setBrush(grad)
            painter.drawRoundedRect(fill_rect, radius, radius)

            # Subtle bright leading edge
            edge_x = fill_rect.right() - 1
            painter.setPen(QPen(_with_alpha("#ffffff", 80), 1.5))
            painter.drawLine(
                QPointF(edge_x, fill_rect.top() + 1),
                QPointF(edge_x, fill_rect.bottom() - 1),
            )


class CyberGraph(QWidget):
    """Minimal activity graph for download telemetry."""

    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        self.theme = theme or get_theme("light")
        self.values = [0] * 56

    def set_theme(self, theme):
        self.theme = theme
        self.update()

    def update_value(self, value):
        self.values.append(max(0, min(100, int(value))))
        self.values.pop(0)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        _set_painter_quality(painter)
        w = self.width()
        h = self.height()
        painter.fillRect(self.rect(), QColor(self.theme["surface_elevated"]))

        if len(self.values) < 2:
            return

        step = w / (len(self.values) - 1)
        line_path = QPainterPath()
        line_path.moveTo(0, h - (self.values[0] / 100.0 * h))
        for i, value in enumerate(self.values):
            line_path.lineTo(i * step, h - (value / 100.0 * h))

        area_path = QPainterPath(line_path)
        area_path.lineTo(w, h)
        area_path.lineTo(0, h)
        area_path.closeSubpath()

        painter.setPen(Qt.NoPen)
        painter.setBrush(_with_alpha(self.theme["primary"], 30))
        painter.drawPath(area_path)

        painter.setPen(QPen(_with_alpha(self.theme["primary"], 200), 1.5))
        painter.drawPath(line_path)


class MatrixLoader(QWidget):
    """Clean scan progress card — minimal, no matrix gimmicks."""

    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        self.theme = theme or get_theme("light")
        self.progress_phase = 0
        self.found_count = 0
        self.total_count = 0
        self.chat_name = ""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(30)

    def set_theme(self, theme):
        self.theme = theme
        self.update()

    def set_count(self, count):
        self.found_count = count
        self.update()

    def set_progress(self, count, total):
        self.found_count = max(0, int(count or 0))
        self.total_count = max(0, int(total or 0))
        self.update()

    def set_context(self, chat_name):
        self.chat_name = chat_name or ""
        self.update()

    def _tick(self):
        self.progress_phase = (self.progress_phase + 2) % 100
        self.update()

    def showEvent(self, event):
        if not self.timer.isActive():
            self.timer.start(30)
        super().showEvent(event)

    def hideEvent(self, event):
        if self.timer.isActive():
            self.timer.stop()
        super().hideEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        _set_painter_quality(p)
        p.fillRect(self.rect(), QColor(self.theme["panel"]))

        card_w = min(520, int(self.width() * 0.75))
        card_h = 160
        card_x = (self.width() - card_w) / 2
        card_y = max(80, int(self.height() * 0.30))
        card_rect = QRectF(card_x, card_y, card_w, card_h)

        # Card background
        p.setPen(QPen(QColor(self.theme["border"]), 1))
        p.setBrush(QColor(self.theme["surface_elevated"]))
        p.drawRoundedRect(card_rect, 12, 12)

        # Subtle accent glow (short, centered) to avoid a harsh full-width line.
        accent_w = card_rect.width() * 0.44
        accent_x = card_rect.x() + (card_rect.width() - accent_w) / 2
        accent_rect = QRectF(accent_x, card_rect.y() + 1, accent_w, 1.5)
        grad = QLinearGradient(accent_rect.left(), 0, accent_rect.right(), 0)
        grad.setColorAt(0.0, _with_alpha(self.theme["primary"], 90))
        grad.setColorAt(0.5, _with_alpha(self.theme["accent"], 140))
        grad.setColorAt(1.0, _with_alpha(self.theme["primary"], 90))
        p.setPen(Qt.NoPen)
        p.setBrush(grad)
        p.drawRoundedRect(accent_rect, 1, 1)

        inner_x = card_rect.x() + 28
        inner_w = card_rect.width() - 56

        # "Scanning" label
        p.setPen(QColor(self.theme["primary"]))
        scan_font = QFont(self.theme.get("body_font", "Segoe UI"), 8, QFont.Bold)
        p.setFont(scan_font)
        p.drawText(
            QRectF(inner_x, card_rect.y() + 16, inner_w, 16),
            Qt.AlignLeft | Qt.AlignVCenter,
            "SCANNING",
        )

        # Chat name
        display_name = self.chat_name or "Selected chat"
        title_font = QFont(self.theme.get("heading_font", "Segoe UI"), 14, QFont.DemiBold)
        chat_metrics = QFontMetrics(title_font)
        display_name = chat_metrics.elidedText(display_name, Qt.ElideRight, int(inner_w))
        p.setPen(QColor(self.theme["text"]))
        p.setFont(title_font)
        p.drawText(
            QRectF(inner_x, card_rect.y() + 36, inner_w, 30),
            Qt.AlignLeft | Qt.AlignVCenter,
            display_name,
        )

        # File count
        count_text = str(self.found_count)
        count_font = QFont(self.theme.get("heading_font", "Segoe UI"), 26, QFont.Bold)
        p.setPen(QColor(self.theme["primary"]))
        p.setFont(count_font)
        count_metrics = QFontMetrics(count_font)
        count_width = count_metrics.horizontalAdvance(count_text)
        p.drawText(
            QRectF(inner_x, card_rect.y() + 72, count_width + 4, 36),
            Qt.AlignLeft | Qt.AlignVCenter,
            count_text,
        )

        # "files found" label
        label_font = QFont(self.theme.get("body_font", "Segoe UI"), 10)
        p.setPen(QColor(self.theme["text_faint"]))
        p.setFont(label_font)
        p.drawText(
            QRectF(inner_x + count_width + 10, card_rect.y() + 82, 100, 18),
            Qt.AlignLeft | Qt.AlignVCenter,
            "files found",
        )

        # Progress rail
        rail_y = card_rect.y() + card_rect.height() - 22
        rail_rect = QRectF(inner_x, rail_y, inner_w, 4)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(self.theme["border"]))
        p.drawRoundedRect(rail_rect, 2, 2)

        # Percentage text beside the bar.
        if self.total_count > 0:
            pct = max(0.0, min(1.0, self.found_count / float(self.total_count)))
            percent_text = f"{int(round(pct * 100))}%"
            progress_text = f"{self.found_count} / {self.total_count}"
        else:
            pct = None
            percent_text = "0%"
            progress_text = f"{self.found_count} / ?"

        pct_font = QFont(self.theme.get("body_font", "Segoe UI"), 9, QFont.DemiBold)
        p.setFont(pct_font)
        p.setPen(QColor(self.theme["text_muted"]))
        p.drawText(
            QRectF(inner_x, rail_rect.y() - 16, inner_w, 12),
            Qt.AlignRight | Qt.AlignVCenter,
            percent_text,
        )

        p.drawText(
            QRectF(inner_x, rail_rect.y() - 16, inner_w, 12),
            Qt.AlignLeft | Qt.AlignVCenter,
            progress_text,
        )

        if pct is not None:
            fill_w = max(0.0, rail_rect.width() * pct)
            if fill_w > 0:
                fill_rect = QRectF(rail_rect.x(), rail_rect.y(), fill_w, rail_rect.height())
                fill_grad = QLinearGradient(fill_rect.left(), 0, fill_rect.right(), 0)
                fill_grad.setColorAt(0.0, QColor(self.theme["primary"]))
                fill_grad.setColorAt(1.0, QColor(self.theme["accent"]))
                p.setBrush(fill_grad)
                p.drawRoundedRect(fill_rect, 2, 2)
        else:
            # Fallback while the total count is still resolving.
            sweep_w = max(40.0, rail_rect.width() * 0.22)
            span = max(1.0, rail_rect.width() - sweep_w)
            sweep_x = rail_rect.x() + (self.progress_phase / 100.0) * span
            sweep_rect = QRectF(sweep_x, rail_rect.y(), sweep_w, rail_rect.height())

            sweep_grad = QLinearGradient(sweep_rect.left(), 0, sweep_rect.right(), 0)
            sweep_grad.setColorAt(0.0, QColor(self.theme["primary"]))
            sweep_grad.setColorAt(1.0, QColor(self.theme["accent"]))
            p.setBrush(sweep_grad)
            p.drawRoundedRect(sweep_rect, 2, 2)


class CyberLoadingOverlay(QWidget):
    """Clean loading overlay with a crisp spinner."""

    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        self.theme = theme or get_theme("light")
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.angle = 0
        self.text = "Loading..."
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.hide()

    def set_theme(self, theme):
        self.theme = theme
        self.update()

    def start(self, text):
        self.text = text
        self.show()
        self.raise_()
        self.timer.start(16)

    def stop(self):
        self.hide()
        self.timer.stop()

    def _tick(self):
        self.angle = (self.angle + 6) % 360
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        _set_painter_quality(p)

        # Dark backdrop
        p.fillRect(self.rect(), _with_alpha(self.theme["overlay"], self.theme["overlay_alpha"]))

        cx = self.width() / 2
        cy = self.height() / 2
        r = 20

        # Track ring
        p.setPen(QPen(QColor(self.theme["border"]), 2.5))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, cy), r, r)

        # Spinning arc — emerald
        pen = QPen(QColor(self.theme["primary"]), 2.5, Qt.SolidLine, Qt.RoundCap)
        p.setPen(pen)
        arc_rect = QRectF(cx - r, cy - r, r * 2, r * 2)
        p.drawArc(arc_rect, -self.angle * 16, 90 * 16)

        # Label
        p.setPen(QColor(self.theme["text_muted"]))
        p.setFont(QFont(self.theme.get("body_font", "Segoe UI"), 11))
        tw = p.fontMetrics().horizontalAdvance(self.text)
        p.drawText(cx - tw / 2, cy + r + 22, self.text)
