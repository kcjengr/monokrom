from qtpy.QtCore import Qt
from qtpyvcp.widgets.form_widgets.main_window import VCPMainWindow
from qtpyvcp.plugins import getPlugin

# Setup logging
from qtpyvcp.utilities import logger
LOG = logger.getLogger('qtpyvcp.' + __name__)

class MainWindow(VCPMainWindow):
    """Main window class for the VCP."""

    # field map of <plugin data getter>:<ui obj name>
    fldmap = {
        'gases':'filter_gas',
        'machines':'filter_machine',
        'materials':'filter_material',
        'thicknesses':'filter_thickness',
        'linearsystems':'filter_distance_system',
        'pressuresystems':'filter_pressure_system',
        'operations':'filter_operation',
        'qualities':'filter_quality',
        'consumables':'filter_consumable'
        }
    
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self._plasma_plugin = getPlugin('plasmaprocesses')
        
        # prepare widget filter data
        self.load_plasma_ui_filter_data()
        
        # create filter signals
        for val in MainWindow.fldmap.values():
            filter_widget = getattr(self, val)
            filter_widget.currentIndexChanged.connect(self.param_update_from_filters)
        
    # add any custom methods here

    def load_plasma_ui_filter_data(self):
        
        # build up the starting position data for process filters
        # in the UI
        for k in MainWindow.fldmap:
            # get filter data and set to self
            setattr(self, '_'+k, getattr(self._plasma_plugin, k)())
            # with this key populate the data into UI fields
            ui_fld = getattr(self, MainWindow.fldmap[k])
            # clear down this combo list before adding starting data
            ui_fld.clear()
            for data in getattr(self, '_'+k):
                # add the str name, and the ID as part of user_role data
                ui_fld.addItem(data.name, data.id)

    # Filter content has changed
    def param_update_from_filters(self, index):
        sender = self.sender()
        print("Update params '{}' '{}'".format(index, sender.currentText()))
        arglist = []
        for v in MainWindow.fldmap.values():
            uifld = getattr(self, v)
            arglist.append(uifld.currentData())
        data = self._plasma_plugin.cut(arglist)[0]
    
    
    def setMode(self):
        print("main window initalise")
    
    
 
