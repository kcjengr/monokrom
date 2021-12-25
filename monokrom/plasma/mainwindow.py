import os

import hal as cnchal

from qtpy.QtCore import Qt, QItemSelectionModel
from qtpy.QtWidgets import QLabel, QListWidgetItem
from qtpyvcp.widgets.form_widgets.main_window import VCPMainWindow
from qtpyvcp.plugins import getPlugin
from qtpyvcp.utilities.info import Info
from qtpyvcp import hal

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
    
    # field map of <plugin data getter>:<ui obj name>
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

    # field map of <plugin data getter>:<cutchart orm relationship field>
    relationship_fld_map = {
        'gases':'gas',
        'machines':'machine',
        'materials':'material',
        'thicknesses':'thickness',
        'linearsystems':'linearsystem',
        'pressuresystems':'pressuresystem',
        'operations':'operation',
        'qualities':'quality',
        'consumables':'consumable'
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
        self.filter_cutchart_id = None
        
        
        if INFO.getIsMachineMetric():
            self._linear_setting = 'mm'
        else:
            self._linear_setting = 'inch'
        
        self._pressure_setting = INFO.ini.find('PLASMAC', 'PRESSURE')
        self._machine = INFO.ini.find('PLASMAC', 'MACHINE') 
        
        # setup some default UI settings
        self.vtkbackplot.setViewZ()
        self.vtkbackplot.enable_panning(True)
        
        # find and set all user buttons
        for user_i in range(1,17):
            user_btn_txt = f"user{user_i}"
            user_name_key = f"USER{user_i}_NAME"
            user_action_key = f"USER{user_i}_ACTION"
            user_name = INFO.ini.find('DISPLAY', user_name_key)
            user_action = INFO.ini.find('DISPLAY', user_action_key)
            user_btn = getattr(self, user_btn_txt)
            if user_btn is not None:
                if user_name:
                    user_btn.setText(user_name)
                    user_btn.filename = user_action
        
        # need to hold linear setting ID so can filter thicknesses based on measurement system
        for s in self._plasma_plugin.linearsystems():
            if s.name == self._linear_setting:
                self._linear_setting_id = s.id 
        
        self.grp_filter_sub_list.hide()

        # link in UI signals for buttons back to Mainwindow methods
        self.btn_save_run_process.clicked.connect(self.update_cut)
        self.btn_run_reload.clicked.connect(self.param_update_from_filters)
        self.filter_sub_list.itemClicked.connect(self.filter_sub_list_select)
        self.btn_seed_db.clicked.connect(self.seed_database)
        self.btn_cut_recover_rev.pressed.connect(lambda:self.cut_recovery_direction(-1))
        self.btn_cut_recover_fwd.pressed.connect(lambda:self.cut_recovery_direction(1))
        self.btn_cut_recover_rev.released.connect(lambda:self.cut_recovery_direction(0))
        self.btn_cut_recover_fwd.released.connect(lambda:self.cut_recovery_direction(0))
        
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

        # create the cutchart hal pin for feedback loop from filter prog
        comp = hal.getComponent()
        self.hal_cutchart_id = comp.addPin('cutchart-id', 'u32', 'in')
        comp.addListener('cutchart-id', self.cutchart_pin_update)

    def cut_recovery_direction(self, direction):
        speed = self.cut_recovery_speed.value() * 0.01 * direction
        cnchal.set_p('plasmac.paused-motion-speed',str(speed))

    def cutchart_pin_update(self, value):
        LOG.debug(f"Cutchart_ID Pin = {value}")
        self.filter_cutchart_id = value
        try:
            # Get the cutchart record based on the pin value.
            cut = self._plasma_plugin.cut_by_id(value)[0]
        except NoneType:
            LOG.warn('No Tool / Cutchart found')
        else:
            # Cycle through all the filters and set them to the correct value
            for k in MainWindow.relationship_fld_map:
                # get handle to UI field
                ui_fld = getattr(self, MainWindow.filter_fld_map[k])
                new_index = ui_fld.findData(getattr(cut, MainWindow.relationship_fld_map[k]).id)
                ui_fld.setCurrentIndex(new_index)
            # check to see if there is a sub select required, if so select it
        

    def load_plasma_ui_filter_data(self):
        # build up the starting position data for process filters
        # in the UI
        for k in MainWindow.filter_fld_map:
            # get filter data and set to self
            if k == 'thicknesses':
                setattr(self, '_'+k, getattr(self._plasma_plugin, k)(self._linear_setting_id))
            else:
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
            select_row = 0
            if len(data) > 1:
                self.grp_filter_sub_list.show()
                # if there is more than one item in the list then do special processing
                self.filter_sub_list.clear()
                for nm in data:
                    item = QListWidgetItem(nm.name)
                    item.setData(Qt.UserRole, nm.id)
                    self.filter_sub_list.addItem(item)
                    if nm.id == self.filter_cutchart_id:
                        select_row = self.filter_sub_list.row(item)
                    self.filter_sub_list.setCurrentRow(select_row, QItemSelectionModel.ClearAndSelect)
            else:
                self.grp_filter_sub_list.hide()

            data = data[select_row]
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
        
    def seed_database(self):
        # get db source file and initiate seed
        src = self.lne_seed_source.text()

        if not os.path.isfile(src):
            LOG.debug('DB seed file not found')
            self.lbl_seed_status.setText('DB seed file not found.')
            return

        self.lbl_seed_status.setText('DB seeding started.')        
        # file exists. Assume is correct format else things will fail
        self._plasma_plugin.seed_data_base(src)
        self.lbl_seed_status.setText('DB seeding Done.')
