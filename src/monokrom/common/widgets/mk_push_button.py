
from qtpyvcp.widgets import VCPButton

class MkPushButton(VCPButton):
    def __init__(self, parent=None):
        super(MkPushButton, self).__init__(parent)

        self.setText("MkPushButton")
