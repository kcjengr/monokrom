
from PySide6.QtCore import QEvent
from PySide6.QtGui import QPainter, QColor, QResizeEvent
from PySide6.QtWidgets import QWidget, QPushButton, QApplication
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

        self.content_widget = None

        if ui_file is not None:
            self.loadUiFile(ui_file)

    def loadUiFile(self, ui_file):
        form_class, base_class = PySide6Ui(ui_file).load()
        # Create the root widget (MkTransparentWidget from .ui) as a child of self.
        # setupUi(self) would treat self as the root and set its geometry to
        # 800x600, preventing the overlay from filling the window.
        # Instead we create a separate MkTransparentWidget and set up the UI on it.
        from monokrom.common.widgets.transparent_widget import MkTransparentWidget
        self.content_widget = MkTransparentWidget(self)
        form_class().setupUi(self.content_widget)

    # track parent window resize events
    def eventFilter(self, obj, event):
        if obj == self.parent() and event.type() == QEvent.Resize:
            size = QResizeEvent.size(event)
            self.resize(size)
            self.btn.move(size.width() - 100, 20)

            if self.content_widget is not None:
                self.content_widget.move(
                    (size.width() - self.content_widget.width()) // 2,
                    (size.height() - self.content_widget.height()) // 2
                )

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

        # Center content widget within the overlay
        if self.content_widget is not None:
            self.content_widget.move(
                (self.width() - self.content_widget.width()) // 2,
                (self.height() - self.content_widget.height()) // 2
            )

        # Raise CLOSE button to ensure it's on top of content
        self.btn.raise_()

    def hide(self):
        super(MkInputOverlay, self).hide()
        if self.parent():
            self.parent().removeEventFilter(self)
