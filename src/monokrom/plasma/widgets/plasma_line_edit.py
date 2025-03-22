
from PySide6.QtWidgets import QLineEdit


class PlasmaLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super(PlasmaLineEdit, self).__init__(parent)

        self.setText("PlasmaLineEdit")
