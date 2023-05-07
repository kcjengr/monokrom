
from qtpy.QtCore import Slot, Property, Signal

from qtpy.QtWidgets import QLineEdit, QApplication
from qtpyvcp.utilities.logger import getLogger
from qtpyvcp.widgets.dialogs import hideActiveDialog

LOG = getLogger(__name__)


class PlasmaAddProcess(QLineEdit):
    def __init__(self, parent=None):
        super(PlasmaAddProcess, self).__init__(parent)
        self._parent = parent

        self.setText("PlasmaAddProcess")

    @Slot()
    def addCutProcess(self):
        # only add anything if we have some text to add
        if len(self.text()) == 0:
            # do nothing, as nothing to do
            LOG.debug('Zero length string. Nothing added.')
            return 
        
        name = self.text()
        qapp = QApplication.instance()
        main_window = qapp.activeWindow()
        LOG.debug(f'Starting to add new cut process: {name}')
        main_window.add_new_cut_process(name)
        #close dialog after add
        hideActiveDialog()