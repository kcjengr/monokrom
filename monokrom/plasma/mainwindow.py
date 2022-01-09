import os

import hal as cnchal
import linuxcnc
### Supports the @Slot decorator to solve property type issues.
from qtpy.QtCore import Qt, QItemSelectionModel, Slot
from qtpy.QtWidgets import QLabel, QListWidgetItem, QAbstractButton
from qtpyvcp.widgets.form_widgets.main_window import VCPMainWindow
from qtpyvcp.plugins import getPlugin
from qtpyvcp.utilities.info import Info
from qtpyvcp import hal
from qtpyvcp.actions.program_actions import load as loadProgram
from qtpyvcp.actions.machine_actions import issue_mdi
### mdi GCODE text created by JT from linuxcnc
import mdi_text as mdiText

#import pydevd;pydevd.settrace()


# Setup logging
from qtpyvcp.utilities import logger
LOG = logger.getLogger('qtpyvcp.' + __name__)
INFO = Info()
STATUS = getPlugin('status')
STAT = STATUS.stat
POS = getPlugin('position')
GCODEPROPS = getPlugin('gcode_properties')

INI = linuxcnc.ini(os.environ['INI_FILE_NAME'])
NGC_LOC = INI.find('DISPLAY', 'PROGRAM_PREFIX')
if NGC_LOC == None:
    NGC_LOC = '~/linuxcnc/nc_files'

USER_BUTTONS = 10

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
        'id':'param_process_id',
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
        
        # get min x and y travel
        self.min_x = float(INI.find('AXIS_X', 'MIN_LIMIT'))
        self.min_y = float(INI.find('AXIS_Y', 'MIN_LIMIT'))
        # get max x and y travel
        self.max_x = float(INI.find('AXIS_X', 'MAX_LIMIT'))
        self.max_y = float(INI.find('AXIS_Y', 'MAX_LIMIT'))
        
        
        if INFO.getIsMachineMetric():
            self._linear_setting = 'mm'
        else:
            self._linear_setting = 'inch'
        
        self._pressure_setting = INFO.ini.find('PLASMAC', 'PRESSURE')
        self._machine = INFO.ini.find('PLASMAC', 'MACHINE')
        
        # setup some default UI settings
        self.vtkbackplot.setViewZ()
        self.vtkbackplot.enable_panning(True)
        self.vtkbackplot.setProgramViewWhenLoadingProgram(True, 'z')
        self.widget_recovery.setEnabled(False)
        self.btn_reverse_run.setEnabled(False)
        self.mdiFrame.hide()
        self.cut_recovery_status = False
        
        # find and set all user buttons
        for user_i in range(1,USER_BUTTONS+1):
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
        self.btn_reverse_run.pressed.connect(lambda:self.cut_recovery_direction(-1))
        self.btn_reverse_run.released.connect(lambda:self.cut_recovery_direction(0))
        self.btn_cut_recover_rev.pressed.connect(lambda:self.cut_recovery_direction(-1))
        self.btn_cut_recover_fwd.pressed.connect(lambda:self.cut_recovery_direction(1))
        self.btn_cut_recover_rev.released.connect(lambda:self.cut_recovery_direction(0))
        self.btn_cut_recover_fwd.released.connect(lambda:self.cut_recovery_direction(0))
        self.btn_reset_rapid.clicked.connect(lambda:self.rapid_slider.setValue(100))
        self.btn_reset_feed.clicked.connect(lambda:self.feed_slider.setValue(100))
        self.btn_reset_jog.clicked.connect(lambda:self.jog_slider.setValue(100))
        self.btn_load_newest.clicked.connect(self.openLatest)
        self.single_cut_x.focusReceived.connect(self.single_cut_limits)
        self.btn_feed_hold.clicked.connect(self.cut_recovery)
        self.btn_cycle_start.clicked.connect(self.cut_recovery)
        self.btn_stop_abort.clicked.connect(self.cut_recovery)
        self.btn_feed_hold.clicked.connect(self.reverse_run)
        self.btn_cycle_start.clicked.connect(self.reverse_run)
        self.btn_stop_abort.clicked.connect(self.reverse_run)
        
        self.vtk_center.clicked.connect(lambda:self.vtkbackplot.setViewProgram('Z'))
        
        self.btnMdiParams.clicked.connect(self.btnParams_clicked)
        self.btnMdiBksp.clicked.connect(self.mdiBackSpace_clicked)
        self.btnMdiSpace.clicked.connect(self.mdiSpace_clicked)

        self.btn_save.clicked.connect(self.save_file)
        self.btn_frame_job.clicked.connect(self.frame_work)
        
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
        
        # setup default cut chart load.
        default_cut_chart = INFO.ini.find('PLASMAC', 'DEFAULT_CUTCHART')
        if default_cut_chart is not None:
            self.cutchart_pin_update(default_cut_chart)

    def cut_recovery_direction(self, direction):
        speed = self.cut_recovery_speed.value() * 0.01 * direction
        cnchal.set_p('plasmac.paused-motion-speed',str(speed))

    def cut_recovery(self):
        sender = self.sender()
        obj_name = sender.objectName()
        if obj_name == 'btn_stop_abort':
                self.widget_recovery.setEnabled(False)
                self.cut_recovery_status = False
                return

        if obj_name == 'btn_cycle_start':
                self.widget_recovery.setEnabled(False)
                self.cut_recovery_status = False
                return

        if obj_name == 'btn_feed_hold':
                self.widget_recovery.setEnabled(True)
                self.cut_recovery_status = True

    def reverse_run(self):
        sender = self.sender()
        obj_name = sender.objectName()
        if obj_name == 'btn_stop_abort':
                self.btn_reverse_run.setEnabled(False)
                return

        if obj_name == 'btn_cycle_start':
                self.btn_reverse_run.setEnabled(False)
                return

        if obj_name == 'btn_feed_hold':
                self.btn_reverse_run.setEnabled(True)
        

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

            # All fields have been set, update any slave displays
            ui_fld = getattr(self, 'param_name')
            self.lbl_process_name.setText(ui_fld.text())
        

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
                    ui_fld.setText(str(fld_data))
                else:
                    ui_fld.setValue(fld_data) 
        else:
            self.grp_filter_sub_list.hide()
            # set cut params to 0
            ui_fld = getattr(self, 'param_name')
            ui_fld.setText('NONE')
            ui_fld = getattr(self, 'param_process_id')
            ui_fld.setText('NONE')
            for v in MainWindow.param_fld_map.values():
                if v not in ('param_name', 'param_process_id'):
                    ui_fld = getattr(self, v)
                    ui_fld.setValue(0)
        # All fields have been set, update any slave displays
        ui_fld = getattr(self, 'param_name')
        self.lbl_process_name.setText(ui_fld.text())
    
    def filter_sub_list_select(self, item):
        data = self.get_filter_query()
        item_id = item.data(Qt.UserRole)
        for d in data:
            if d.id == item_id:
                for k in MainWindow.param_fld_map:
                    fld_data = getattr(d, k)
                    ui_fld = getattr(self, MainWindow.param_fld_map[k])
                    if isinstance(ui_fld, QLabel):
                        ui_fld.setText(str(fld_data))
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

    def openLatest(self):
        """Opens the latest file by date/time in the default ngc location"""
        search_dir = os.path.expanduser(NGC_LOC)
        newist = None
        with os.scandir(search_dir) as it:
            for entry in it:
                if not entry.name.startswith('.') and entry.is_file():
                    file_stat = entry.stat()
                    if newist is None:
                        newist = (entry.path, file_stat.st_mtime)
                    elif newist[1] < file_stat.st_mtime:
                        newist = (entry.path, file_stat.st_mtime)
        # should have a latest file from standard directory
        if newist is not None:
            loadProgram(newist[0])

    def single_cut_limits(self):
        # Assumes an axis sequence of x:0, y:1, z:2
        sender = self.sender()
        print(f'single_cut_limits:  {sender.objectName()}')
        min = 0
        max = 0
        if sender.objectName() == 'single_cut_x':
            x_pos = POS.Absolute.getValue()[0]
            min = self.min_x - x_pos
            max = self.max_x - x_pos
            #print(f'Absolute X position = {x_pos},  Min={min}, Max={max}, X-Max={self.max_x}')
        elif sender.objectName() == 'single_cut_y':
            y_pos = POS.Absolute.getValue()[1]
            #print(f'Absolute Y position = {y_pos},  Min={min}, Max={max}, X-Max={self.max_y}')
            min = self.min_y - y_pos
            max = self.max_y - y_pos
        # set the min/max ranges on the control
        sender.setMaximum(max)
        sender.setMinimum(min)


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


    #
    # MDI Panel
    #
    @Slot(QAbstractButton)
    def on_btngrpMdi_buttonClicked(self, button):
        char = str(button.text())
        text = self.mdiEntry.text() or 'null'
        if text != 'null':
            text += char
        else:
            text = char
        self.mdiEntry.setText(text)

    def btnParams_clicked(self):
        # get mdi entry
        text = self.mdiEntry.text() or 'null'
        print(text)
        if text != 'null':
            # we have something to check so get the gcode words
            words = mdiText.gcode_words()
            if text in words:
                # clear the mdi line
                self.mdiClear()
                for index, value in enumerate(words[text], start=1):
                    # search and populate the params available for that gcode word
                    print(value)
                    getattr(self, 'btnGcodeP' + str(index)).setText(value)
            else:
                self.mdiClear()
            # All help related so not used yet
            # titles = mdiText.gcode_titles()
            # if text in titles:
            #     self.lblGcodeHelp.setText(titles[text])
            # else:
            #     self.mdiClear()
            # self.lblGcodeHelp.setText(mdiText.gcode_descriptions(text))
        else:
            self.mdiClear()
            print('No Match')


    def mdiClear(self):
        for index in range(1,11):
            getattr(self, 'btnGcodeP' + str(index)).setText('')
        # All help related so not used yet
        # self.lblGcodeHelp.setText('')

    def mdiBackSpace_clicked(parent):
        if len(parent.mdiEntry.text()) > 0:
            text = parent.mdiEntry.text()[:-1]
            parent.mdiEntry.setText(text)

    def mdiSpace_clicked(parent):
        text = parent.mdiEntry.text() or 'null'
        # if no text then do not add a space
        if text != 'null':
            text += ' '
            parent.mdiEntry.setText(text)
            
    #
    # GCode Editor
    #
    def save_file(self):
        # Get the current loaded file per the recent file combo
        # and use that as the save name.
        # Need to do as the STATs  file name will be the temp file
        # generated as part of the filter program mechanic.
        # Once save trigger a linuxcnc level program reload to force
        # filter program reprocessing.
        real_file = self.gcode_recentfile.currentData()
        if real_file == None:
            return
        
        self.gcode_editor.saveFile(real_file)
        loadProgram(real_file)
    

    #
    # Frame prog on work piece
    #
    def frame_work(self):
        # hack into VTK to get at some internals ot get prog bounds
        vtk = self.vtkbackplot
        program_bounds = vtk.program_bounds_actors[vtk.active_wcs_index].GetBounds()
        LOG.debug(f'prog bounds = {program_bounds}')
        # sample bounds response: (5.659999976158142, 242.86000610351562, 6.462499976158142, 85.72250366210938, 0.0, 0.0)
        # in min/max pairs for X, Y and Z
        x_length = program_bounds[1] - program_bounds[0]
        y_length = program_bounds[3] - program_bounds[2]
        # ignore Z as we don't use it for bounding
        # get max z-height, x-current, y-current
        x_current = POS.abs(0)
        y_current = POS.abs(1)
        # boundaries for move
        min_max_x = INFO.getAxisMinMax('X')[0]
        min_max_y = INFO.getAxisMinMax('Y')[0]
        min_max_z = INFO.getAxisMinMax('Z')[0]
        
        if (y_current + y_length) > min_max_y[1]:
            LOG.error(f'FRAMING ERROR: Y will exceed Y-Max')
            return
        if (x_current + x_length) > min_max_x[1]:
            LOG.error(f'FRAMING ERROR: X will exceed X-Max')
            return
        if (y_current + y_length) < min_max_y[0]:
            LOG.error(f'FRAMING ERROR: Y will exceed Y-Min')
            return
        if (x_current + x_length) < min_max_x[0]:
            LOG.error(f'FRAMING ERROR: X will exceed X-Min')
            return
        
        feed_rate = self.framing_feed_rate.value()
        x_laser_offset = self.laser_offset_x.value()
        y_laser_offset = self.laser_offset_y.value()
        if not self.btn_laser.isChecked():
            x_laser_offset = 0
            y_laser_offset = 0

        move_cmd = (
            f"F{feed_rate};"
            f"G53 G0 Z{min_max_z[1]};"
            f"G53 G0 X{x_current + x_laser_offset} Y{y_current + y_laser_offset};"
            f"G53 G1 Y{y_current + y_laser_offset + y_length};"
            f"G53 G1 X{x_current + x_laser_offset + x_length};"
            f"G53 G1 Y{y_current + y_laser_offset};"
            f"G53 G1 X{x_current + x_laser_offset}"
        )
        issue_mdi(move_cmd)
