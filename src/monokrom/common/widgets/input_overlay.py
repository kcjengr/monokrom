
from PySide6.QtCore import QEvent
from PySide6.QtGui import QPainter, QColor, QResizeEvent
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QApplication
from qtpyvcp.utilities.pyside_ui_loader import PySide6Ui


class MkInputOverlay(QWidget):
    def __init__(self, ui_file=None, parent=None):
        super(MkInputOverlay, self).__init__(parent)

        self._parent = parent
        self.bg_color = QColor(22, 22, 14, 200)

        self.btn = QPushButton("CLOSE", parent=self)
        self.btn.setFixedSize(80, 30)
        self.btn.setStyleSheet("font-weight: bold")
        self.btn.pressed.connect(self.hide)

        if ui_file is not None:
            self.loadUiFile(ui_file)

    def loadUiFile(self, ui_file):
        form_class, base_class = PySide6Ui(ui_file).load()
        self.ui = form_class()
        self.ui.setupUi(self)
        # layout = QHBoxLayout(self)
        # layout.addWidget(form_class())
        # self.setLayout(layout)

    # track parent window resize events
    def eventFilter(self, obj, event):
        if obj == self.parent() and event.type() == QEvent.Resize:
            size = QResizeEvent.size(event)
            self.resize(size)
            self.btn.move(size.width() - 100, 20)

        return super(MkInputOverlay, self).eventFilter(obj, event)

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.fillRect(self.rect(), self.bg_color)
        qp.end()

    def show(self, parent=None):
        win = QApplication.instance().activeWindow()
        self.setParent(win)
        win.installEventFilter(self)

        super(MkInputOverlay, self).show()

        self.move(0, 0)
        self.resize(win.width(), win.height())
        self.btn.move(win.width() - 100, 20)

    def hide(self):
        super(MkInputOverlay, self).hide()
        self.parent().removeEventFilter(self)
