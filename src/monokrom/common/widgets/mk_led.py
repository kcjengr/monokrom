from qtpy.QtCore import Qt, QTimer
from qtpy.QtGui import QColor, QPainter, QBrush
from qtpyvcp.widgets.display_widgets.status_led import StatusLED

class MkLedIndicator(StatusLED):
    def __init__(self, parent=None):
        super(MkLedIndicator, self).__init__(parent)

    # Override paint to implement monokrom visual
    def paintEvent(self, event):
        painter = QPainter()
        x = 0
        y = 0
        if self._alignment & Qt.AlignLeft:
            x = 0
        elif self._alignment & Qt.AlignRight:
            x = self.width() - self._diameter
        elif self._alignment & Qt.AlignHCenter:
            x = (self.width() - self._diameter) / 2
        elif self._alignment & Qt.AlignJustify:
            x = 0

        if self._alignment & Qt.AlignTop:
            y = 0
        elif self._alignment & Qt.AlignBottom:
            y = self.height() - self._diameter
        elif self._alignment & Qt.AlignVCenter:
            y = (self.height() - self._diameter) / 2

        # get the fill draw color set from QTDesigner
        draw_color = QColor(self._color)
        # set the pen color, we want to use this even if the state is OFF
        pen_color = draw_color

        if not self._state:
            # LED state is OFF, set fill
            draw_color = QColor(Qt.black)

        # dim if control is not enabled
        if not self.isEnabled():
            draw_color.setAlpha(30)

        # Start actual painting process
        painter.begin(self)
        brush = QBrush(draw_color)
        painter.setPen(pen_color)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setBrush(brush)
        painter.drawEllipse(int(x + 1), int(y + 1), int(self._diameter - 2), int(self._diameter - 2))

        # Does flashing make sense for Monokrom style?
        if self._flashRate > 0 and self._flashing:
            self._timer.start(self._flashRate)
        else:
            self._timer.stop()

        painter.end()
