
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QPainter, QColor, QResizeEvent
from PySide6.QtWidgets import QWidget, QPushButton, QApplication
from qtpyvcp.utilities.pyside_ui_loader import PySide6Ui


class MkInputOverlay(QWidget):
    def __init__(self, ui_file=None, parent=None):
        super(MkInputOverlay, self).__init__(parent)

        # Make this a top-level window so the compositor handles stacking.
        # This prevents ghosting: when the overlay is hidden, the window
        # manager automatically restores the underlying MainWindow content.
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

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
        from monokrom.common.widgets.transparent_widget import MkTransparentWidget
        self.content_widget = MkTransparentWidget(self)
        form_class().setupUi(self.content_widget)

    # track main window resize events
    def eventFilter(self, obj, event):
        if obj == self._main_window and event.type() == QEvent.Resize:
            size = QResizeEvent.size(event)
            self.resize(size)

            if self.content_widget is not None:
                self.content_widget.move(
                    (self.width() - self.content_widget.width()) // 2,
                    (self.height() - self.content_widget.height()) // 2
                )

        return super(MkInputOverlay, self).eventFilter(obj, event)

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.fillRect(self.rect(), self.bg_color)

    def show(self, parent=None):
        win = QApplication.instance().activeWindow()
        self._main_window = win
        win.installEventFilter(self)

        # Position and size this overlay to match the main window
        self.setGeometry(win.geometry())
        self.btn.move(win.width() - 100, 20)

        # Center content widget within the overlay
        if self.content_widget is not None:
            self.content_widget.move(
                (self.width() - self.content_widget.width()) // 2,
                (self.height() - self.content_widget.height()) // 2
            )

        super(MkInputOverlay, self).show()

    def hide(self):
        super(MkInputOverlay, self).hide()
        if self._main_window:
            self._main_window.removeEventFilter(self)
            self._main_window = None
