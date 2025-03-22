
from PySide6.QtWidgets import QPushButton


class PlasmaPushButton(QPushButton):
    def __init__(self, parent=None):
        super(PlasmaPushButton, self).__init__(parent)

        self.setText("PlasmaPushButton")
