from qtpy.QtCore import Qt, QItemSelectionModel
from qtpy.QtWidgets import QLabel, QListWidgetItem
from qtpyvcp.widgets.form_widgets.main_window import VCPMainWindow
from qtpyvcp.plugins import getPlugin
from qtpyvcp.utilities.info import Info

#import pydevd;pydevd.settrace()


# Setup logging
from qtpyvcp.utilities import logger
LOG = logger.getLogger('qtpyvcp.' + __name__)
INFO = Info()

class MainWindow(VCPMainWindow):
    """Main window class for the VCP."""

    # field map of <plugin data getter>:<ui obj name>
    locked_fld_map = {
        'machines':'filter_machine',
        'linearsystems':'filter_distance_system',
        'pressuresystems':'filter_pressure_system'
        }
    
    filter_fld_map = {
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
    
    param_fld_map = {
        'name':'param_name',
        'pierce_height':'param_pierceheight',
        'pierce_delay':'param_piercedelay',
        'cut_height':'param_cutheight',
        'cut_speed':'param_cutfeedrate',
        'plunge_rate':'param_plungefeedrate',
        'volts':'param_cutvolts',
        'kerf_width':'param_kirfwidth',
        'puddle_height':'param_puddlejumpheight',
        'puddle_delay':'param_puddlejumpdelay',
        'amps':'param_cutamps',
        'pause_at_end':'param_pauseatend',
        'pressure':'param_gaspressure'
        }
    
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self._plasma_plugin = getPlugin('plasmaprocesses')
        
        if INFO.getIsMachineMetric():
            self._linear_setting = 'mm'
        else:
            self._linear_setting = 'inch'
        self._pressure_setting = INFO.ini.find('PLASMAC', 'PRESSURE')
        self._machine = INFO.ini.find('PLASMAC', 'MACHINE') 
        
        self.grp_filter_sub_list.hide()

        # link in UI signals for buttons back to Mainwindow methods
        self.btn_save_run_process.clicked.connect(self.update_cut)
        self.btn_run_reload.clicked.connect(self.param_update_from_filters)
        self.filter_sub_list.itemClicked.connect(self.filter_sub_list_select)
        
        
        # prepare widget filter data
        self.load_plasma_ui_filter_data()
        
        # set the locked filters on settings page
        self.filter_machine.setCurrentText(self._machine)
        self.filter_distance_system.setCurrentText(self._linear_setting)
        self.filter_pressure_system.setCurrentText(self._pressure_setting)
        
        # create filter signals
        for val in MainWindow.filter_fld_map.values():
            filter_widget = getattr(self, val)
            filter_widget.currentIndexChanged.connect(self.param_update_from_filters)

    def load_plasma_ui_filter_data(self):
        # build up the starting position data for process filters
        # in the UI
        for k in MainWindow.filter_fld_map:
            # get filter data and set to self
            setattr(self, '_'+k, getattr(self._plasma_plugin, k)())
            # with this key populate the data into UI field
            ui_fld = getattr(self, MainWindow.filter_fld_map[k])
            # clear down this combo list before adding starting data
            ui_fld.clear()
            for data in getattr(self, '_'+k):
                # add the str name, and the ID as part of user_role data
                ui_fld.addItem(data.name, data.id)

    def get_filter_query(self):
        arglist = []
        for v in MainWindow.filter_fld_map.values():
            uifld = getattr(self, v)
            arglist.append(uifld.currentData())
        cutlist = self._plasma_plugin.cut(arglist)
        if len(cutlist) > 0:
            return cutlist
        else:
            return None

    # Filter content has changed
    def param_update_from_filters(self, index=0):
        sender = self.sender()
        if hasattr(sender, 'currentText'):
            LOG.debug("Update params '{}' '{}'".format(index, sender.currentText()))
        else:
            LOG.debug('Update params.')
        arglist = []
        for v in MainWindow.filter_fld_map.values():
            uifld = getattr(self, v)
            arglist.append(uifld.currentData())
        cutlist = self._plasma_plugin.cut(arglist)
        data = self.get_filter_query()
        if data != None:
            if len(data) > 1:
                self.grp_filter_sub_list.show()
                # if there is more than one item in the list then do special processing
                self.filter_sub_list.clear()
                for nm in data:
                    item = QListWidgetItem(nm.name)
                    item.setData(Qt.UserRole, nm.id)
                    self.filter_sub_list.addItem(item)
                    self.filter_sub_list.setCurrentRow(0, QItemSelectionModel.ClearAndSelect)
            else:
                self.grp_filter_sub_list.hide()

            data = data[0]
            for k in MainWindow.param_fld_map:
                fld_data = getattr(data, k)
                ui_fld = getattr(self, MainWindow.param_fld_map[k])
                if isinstance(ui_fld, QLabel):
                    ui_fld.setText(fld_data)
                else:
                    ui_fld.setValue(fld_data) 
        else:
            self.grp_filter_sub_list.hide()
            # set cut params to 0
            ui_fld = getattr(self, 'param_name')
            ui_fld.setText('NONE')
            for v in MainWindow.param_fld_map.values():
                if v != 'param_name':
                    ui_fld = getattr(self, v)
                    ui_fld.setValue(0)
    
    def filter_sub_list_select(self, item):
        data = self.get_filter_query()
        item_id = item.data(Qt.UserRole)
        for d in data:
            if d.id == item_id:
                for k in MainWindow.param_fld_map:
                    fld_data = getattr(d, k)
                    ui_fld = getattr(self, MainWindow.param_fld_map[k])
                    if isinstance(ui_fld, QLabel):
                        ui_fld.setText(fld_data)
                    else:
                        ui_fld.setValue(fld_data) 
                
    
    def setMode(self):
        print("main window initalise")
    
    def add_new_cut_process(self, name=None):
        if name == None:
            LOG.debug('No name set for cut process Add. Do nothing.')
            return
        
        # gather filter and cut params
        arglist = {}
        for k in MainWindow.filter_fld_map:
            uifld = getattr(self, MainWindow.filter_fld_map[k])
            arglist[k] = uifld.currentData()
        # get cut params
        for k in MainWindow.param_fld_map:
            uifld = getattr(self, MainWindow.param_fld_map[k])
            if hasattr(uifld, 'value'):
                arglist[k] = uifld.value()
            else:
                # must be a label
                arglist[k] = uifld.text()
        # correctly set the name
        arglist['name'] = name
        self._plasma_plugin.addCut(**arglist)
        # update the UI with the newly loaded item
        self.param_update_from_filters()

    def update_cut(self):
        q = self.get_filter_query()
        if q == None:
            return
        
        arglst = {}
        for k in MainWindow.param_fld_map:
            ui_fld = getattr(self, MainWindow.param_fld_map[k])
            if isinstance(ui_fld, QLabel):
                arglst[k] = ui_fld.text()
            else:
                arglst[k] = ui_fld.value() 
        
        self._plasma_plugin.updateCut(q, **arglst)