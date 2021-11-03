from qtpyvcp.widgets.form_widgets.main_window import VCPMainWindow
from qtpyvcp.plugins import getPlugin

# Setup logging
from qtpyvcp.utilities import logger
LOG = logger.getLogger('qtpyvcp.' + __name__)

class MainWindow(VCPMainWindow):
    """Main window class for the VCP."""
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self._plasma_plugin = getPlugin('plasmaprocesses')
        
        # prepare widget data
        self.load_plasma_data()
        
    # add any custom methods here

    def load_plasma_data(self):
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
        
        # build up the starting position data for process filters
        # in the UI
        for k in fldmap:
            # get filter data and set
            setattr(self, '_'+k, getattr(self._plasma_plugin, k)())
            # with this key populate the data into UI fields
            ui_fld = getattr(self, fldmap[k])
            # clear down this combo list before adding starting data
            ui_fld.clear()
            for data in getattr(self, '_'+k):
                ui_fld.addItem(data.name)
        
    
    def setMode(self):
        print("main window initalise")
    
    
 
