import os
import math
import time
from tempfile import NamedTemporaryFile

import hal as cnchal
from qtpyvcp import hal as qthal
import linuxcnc
### Supports the @Slot decorator to solve property type issues.
from qtpy.QtCore import Qt, QItemSelectionModel, Slot, QTimer
from qtpy.QtWidgets import QLabel, QListWidgetItem, QAbstractButton
from qtpy.QtWidgets import QTableView, QListWidget
import qtpyvcp
from qtpyvcp.widgets.form_widgets.main_window import VCPMainWindow
from qtpyvcp.plugins import getPlugin
from qtpyvcp.utilities.info import Info
from qtpyvcp import hal
from qtpyvcp.actions.program_actions import load as loadProgram
from qtpyvcp.actions.machine_actions import issue_mdi
from qtpyvcp.actions.machine_actions import mode as set_mode
from qtpyvcp.actions.machine_actions import jog
### mdi GCODE text created by JT from linuxcnc
import mdi_text as mdiText
import quickshapes as qs

#import pydevd;pydevd.settrace()


# Setup logging
from qtpyvcp.utilities import logger
LOG = logger.getLogger('qtpyvcp.' + __name__)
INFO = Info()
STATUS = getPlugin('status')
STAT = STATUS.stat
POS = getPlugin('position')
CMD = linuxcnc.command()

#GCODEPROPS = getPlugin('gcode_properties')

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
        'tool_number':'param_process_id',
        #'id':'param_process_id',
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
        self.detail_index_num = 0
        self.latest_real_file=""
        
        # get min x and y travel
        self.min_x = float(INI.find('AXIS_X', 'MIN_LIMIT'))
        self.min_y = float(INI.find('AXIS_Y', 'MIN_LIMIT'))
        # get max x and y travel
        self.max_x = float(INI.find('AXIS_X', 'MAX_LIMIT'))
        self.max_y = float(INI.find('AXIS_Y', 'MAX_LIMIT'))
        # get min z travel
        self.min_z = INFO.getAxisMinMax('Z')[0]
        self.slat_top = float(INI.find('PLASMAC', 'SLAT_TOP'))
        # get max Z speed
        self.thc_feed_rate.setText(f"{float(INI.find('AXIS_Z', 'MAX_VELOCITY')) * 60 / 2}")
        cnchal.set_p('plasmac.thc-feed-rate',f"{float(INI.find('AXIS_Z', 'MAX_VELOCITY')) * 60 / 2}")
        
        if INFO.getIsMachineMetric():
            self._linear_setting = 'mm'
        else:
            self._linear_setting = 'inch'
        
        self.units_per_mm = cnchal.get_value('halui.machine.units-per-mm')
        
        self._pressure_setting = INFO.ini.find('PLASMAC', 'PRESSURE')
        self._machine = INFO.ini.find('PLASMAC', 'MACHINE')
        self._tool_number = 0
        self._material_thickness = 0
        
        # find handles to openfile and recentfiles dialogs
        for h in qtpyvcp.DIALOGS:
            LOG.debug(f"monokrom-Mainwindow:  dialog key = {h}, dialog handle ={qtpyvcp.DIALOGS[h]}")
        self.open_file_dialog_widget = qtpyvcp.DIALOGS['open_file'].findChild(QTableView)
        self.recent_files_dialog_widget = qtpyvcp.DIALOGS['recent_files'].findChild(QListWidget)
        self.open_file_dialog_widget.fileLoadFromDialog.connect(self.set_openfile)
        self.recent_files_dialog_widget.fileLoadFromDialog.connect(self.set_openfile)
        
        # probe timer and state
        self.probe_timer = QTimer()
        #self.probe_timer.setSingleShot(True)
        self.probe_timer.timeout.connect(self.probe_timeout)
        
        # Hide some in flight UI that is unfinished
        #self.mainTabWidget.setTabVisible(2, False)
        self.tabs_ctl_run_right.setTabVisible(2, False)
        self.tab_holes_and_slots.setTabVisible(1, False)
        # setup some default UI settings
        self.vtkbackplot.update_active_wcs(0)
        self.vtkbackplot.setViewZ()
        self.vtkbackplot.enable_panning(True)
        self.vtkbackplot.setProgramViewWhenLoadingProgram(True, 'z')
        self.vtk_qs.update_active_wcs(0)
        self.vtk_qs.setViewZ()
        self.vtk_qs.enable_panning(True)
        self.vtk_qs.setProgramViewWhenLoadingProgram(True, 'z')
        self.widget_recovery.setEnabled(False)
        self.btn_consumable_change.setEnabled(False)
        self.mdiFrame.hide()
        self.transformFrame.hide()
        self.cut_recovery_status = False
        self.consumable_offset_x.setMinimum(self.min_x + (10 * self.units_per_mm))
        self.consumable_offset_y.setMinimum(self.min_y + (10 * self.units_per_mm))
        self.consumable_offset_x.setMaximum(self.max_x - (10 * self.units_per_mm))
        self.consumable_offset_y.setMaximum(self.max_y - (10 * self.units_per_mm))
        self.sheet_align_p1 = None
        self.sheet_align_p2 = None
        self.sheet_align_p3 = None
        # set the jog buttons to the active settings on start
        jog.set_increment(1 * self.units_per_mm)
        jog.set_jog_continuous(True)

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
        self.btn_zero_xy.clicked.connect(self.zero_wcs_xy)
        self.btn_probe_test.toggled.connect(self.probe_test)
        self.vtk_no_lines.toggled.connect(self.breadcrumbs_tracked)
        #self.btn_transform.toggled.connect(self.tranformUI)
        self.grp_shape_btns.buttonClicked.connect(self.clicked_shape_btn)
        self.btn_qs_refresh.clicked.connect(self.clicked_qs_refresh)

        # cut recovery direction
        self.btn_cut_recover_rev.pressed.connect(lambda:self.cut_recovery_direction(-1))
        self.btn_cut_recover_fwd.pressed.connect(lambda:self.cut_recovery_direction(1))
        self.btn_cut_recover_rev.released.connect(lambda:self.cut_recovery_direction(0))
        self.btn_cut_recover_fwd.released.connect(lambda:self.cut_recovery_direction(0))
        self.btn_cut_recover_cancel.pressed.connect(lambda:self.cutrec_cancel_pressed(1))
        self.btn_recovery_n.pressed.connect(lambda:self.cutrec_move(1, 0, 1))
        self.btn_recovery_ne.pressed.connect(lambda:self.cutrec_move(1, 1, 1))
        self.btn_recovery_e.pressed.connect(lambda:self.cutrec_move(1, 1, 0))
        self.btn_recovery_se.pressed.connect(lambda:self.cutrec_move(1, 1, -1))
        self.btn_recovery_s.pressed.connect(lambda:self.cutrec_move(1, 0, -1))
        self.btn_recovery_sw.pressed.connect(lambda:self.cutrec_move(1, -1, -1))
        self.btn_recovery_w.pressed.connect(lambda:self.cutrec_move(1, -1, 0))
        self.btn_recovery_nw.pressed.connect(lambda:self.cutrec_move(1, -1, 1))

        # slider resets
        self.btn_reset_rapid.clicked.connect(lambda:self.rapid_slider.setValue(100))
        self.btn_reset_feed.clicked.connect(lambda:self.feed_slider.setValue(100))
        self.btn_reset_jog.clicked.connect(lambda:self.jog_slider.setValue(100))

        # load newest
        self.btn_load_newest.clicked.connect(self.openLatest)
        
        # reload
        self.btn_reload.clicked.connect(self.reload_file)
        self.btn_transform_apply.clicked.connect(self.reload_file)

        # single cut limits
        self.single_cut_x.focusReceived.connect(self.single_cut_limits)
        self.single_cut_y.focusReceived.connect(self.single_cut_limits)

        # cut recovery block
        self.btn_feed_hold.clicked.connect(self.cut_recovery)
        self.btn_cycle_start.clicked.connect(self.cut_recovery)
        self.btn_stop_abort.clicked.connect(self.cut_recovery)

        # consumable change block
        self.btn_feed_hold.clicked.connect(self.consumable_change)
        self.btn_cycle_start.clicked.connect(self.consumable_change)
        self.btn_stop_abort.clicked.connect(self.consumable_change)
        
        self.btn_consumable_change.toggled.connect(self.consumable_toggle)

        # VTK block
        self.vtk_center.clicked.connect(lambda:self.vtkbackplot.setViewProgram('Z'))

        # MDI        
        self.btnMdiParams.clicked.connect(self.btnParams_clicked)
        self.btnMdiBksp.clicked.connect(self.mdiBackSpace_clicked)
        self.btnMdiSpace.clicked.connect(self.mdiSpace_clicked)

        self.btn_save.clicked.connect(self.save_file)
        self.btn_frame_job.clicked.connect(self.frame_work)
        
        # Sheet Alignment
        self.btn_laser.toggled.connect(self.sheet_align_toggle)
        self.btn_sheet_align_pt1.toggled.connect(self.sheet_align_toggle)
        self.btn_sheet_align_pt2.toggled.connect(self.sheet_align_toggle)
        self.btn_sheet_doalign.clicked.connect(self.sheet_align_toggle)
        #self.btn_sheet_align_pt1.clicked.connect(self.sheet_align_set_p1)
        #self.btn_sheet_align_pt2.clicked.connect(self.sheet_align_set_p2)
        #self.btn_sheet_doalign.clicked.connect(self.sheet_align)
        
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
        # create a force-reload-cutchart for use by filter prog
        self.hal_cutchart_reload = comp.addPin('cutchart-reload', 'bit', 'in')
        comp.addListener('cutchart-reload', self.force_cutchart_reload)
        
        # create probe test error pin to watch
        self.hal_probe_test_error = comp.addPin('probe-test-error', 'bit', 'in')
        comp.addListener('probe-test-error', self.probe_test_error)
        
        # setup default cut chart load.
        default_cut_chart = INFO.ini.find('PLASMAC', 'DEFAULT_CUTCHART')
        if default_cut_chart is not None:
            self.cutchart_pin_update(default_cut_chart)

        # find the largest tool ID and store it
        tools = self._plasma_plugin.tool_list_for_lcnc()
        self.last_tool_num_assigned = -1
        for tool in tools:
            LOG.debug(f"tool = id: {tool.id}, num: {tool.tool_number}")
            if (tool.tool_number > self.last_tool_num_assigned and
                tool.tool_number != 99999
            ):
                self.last_tool_num_assigned = tool.tool_number
        
        comp = qthal.getComponent()
        # feed hold
        objName = str(self.btn_feed_hold.objectName()).replace('_', '-')
        self.btn_feed_hold_external_trigger_pin = comp.addPin(objName + ".external-trigger", "bit", "in")
        self.btn_feed_hold_external_trigger_pin.valueChanged.connect(lambda x :self.btn_feed_hold.click() if x else None)
        # stop/abort
        objName = str(self.btn_stop_abort.objectName()).replace('_', '-')
        self.btn_stop_abort_external_trigger_pin = comp.addPin(objName + ".external-trigger", "bit", "in")
        self.btn_stop_abort_external_trigger_pin.valueChanged.connect(lambda x :self.btn_stop_abort.click() if x else None)
        # laser
        objName = str(self.btn_laser.objectName()).replace('_', '-')
        self.btn_laser_external_trigger_pin = comp.addPin(objName + ".external-trigger", "bit", "in")
        self.btn_laser_external_trigger_pin.valueChanged.connect(lambda x :self.btn_laser.click() if x else None)
        # alignment btns
        objName = str(self.btn_sheet_align_pt1.objectName()).replace('_', '-')
        self.btn_sheet_align_pt1_trigger_pin = comp.addPin(objName + ".external-trigger", "bit", "in")
        self.btn_sheet_align_pt1_trigger_pin.valueChanged.connect(lambda x :self.btn_sheet_align_pt1.click() if x else None)
        objName = str(self.btn_sheet_align_pt2.objectName()).replace('_', '-')
        self.btn_sheet_align_pt2_trigger_pin = comp.addPin(objName + ".external-trigger", "bit", "in")
        self.btn_sheet_align_pt2_trigger_pin.valueChanged.connect(lambda x :self.btn_sheet_align_pt2.click() if x else None)
        objName = str(self.btn_sheet_doalign.objectName()).replace('_', '-')
        self.btn_sheet_doalign_trigger_pin = comp.addPin(objName + ".external-trigger", "bit", "in")
        self.btn_sheet_doalign_trigger_pin.valueChanged.connect(lambda x :self.btn_sheet_doalign.click() if x else None)
        
        # test svg

    def on_exitAppBtn_clicked(self):
      self.app.quit()

    def set_openfile(self, file_str):
        self.latest_real_file = file_str
        LOG.debug(f"set_openfile:  file_str = {file_str}")
        
    def clicked_shape_btn(self, btn):
        btn_name = btn.objectName()
        LOG.debug(f"shape button pushed: {btn_name} with index {int(btn_name[4:])}")
        self.detail_index_num = int(btn_name[4:])
        self.details_pages.setCurrentIndex(self.detail_index_num)

    def clicked_qs_refresh(self):
        LOG.debug("clicked_qs_refresh")
        tst = self.detail_index_num
        lines = []
        kerf = self.param_kirfwidth.value()
        leadin = 4
        qs.preamble(lines, metric=INFO.getIsMachineMetric())
        qs.magic_material(kw=kerf,
                       ph=self.param_pierceheight.value(),
                       pd=self.param_piercedelay.value(),
                       ch=self.param_cutheight.value(),
                       fr=self.param_cutfeedrate.value(),
                       mt=1,
                       th=0,
                       ca=self.param_cutamps.value(),
                       cv=self.param_cutvolts.value(),
                       pe=self.param_pauseatend.value(),
                       gp=0, cm=0, jh=0, jd=0,
                       lines=lines)
        match tst:
            case 0:
                diameter = self.id0_dbl_diam.value()
                qs.circle(diameter=diameter, kerf=kerf, leadin=leadin, conv=1, lines=lines)
            case 1:
                width = self.id1_dbl_width.value()
                height = self.id1_dbl_height.value()
                qs.rectangle(width, height, kerf=kerf, leadin=leadin, conv=1, lines=lines)
            case 2: 
                id = self.id2_dbl_inner_diam.value()
                od = self.id2_dbl_outer_diam.value()
                qs.donut(od=od, id=id, kerf=kerf, leadin=leadin, conv=1, lines=lines)
            case 3:
                width = self.id3_dbl_width.value()
                height = self.id3_dbl_height.value()
                qs.convex_rectangle(width, height, kerf=kerf, leadin=leadin, conv=1, lines=lines)
            case 4:
                w1 = self.id4_dbl_w1.value()
                d1 = self.id4_dbl_d1.value()
                h1 = self.id4_dbl_h1.value()
                h2 = self.id4_dbl_h2.value()
                d2 = self.id4_dbl_d2.value()
                rb = self.id4_dbl_rb.value()
                pair = self.id4_chk_pair.isChecked()
                separation = self.id4_dbl_separation.value()
                qs.lifting_lug(w1, d1, h1, h2, d2, rb, kerf=kerf, separation=separation, cutting_pair=pair, parent=self, leadin=leadin, conv=1, lines=lines)

        qs.postamble(lines)
        with NamedTemporaryFile(mode='w+' ,suffix=".ngc", delete=False) as temp_file:
            temp_name = temp_file.name
            temp_file.writelines(lines)
        # make sure hole processing it off as lead ins seem to cause it issus:
        self.chkb_hole_detect_enable.setCheckState(False)
        self.set_openfile(temp_name)
        loadProgram(temp_name, add_to_recents=False)
        self.vtkbackplot.setViewProgram('Z')
        self.vtk_qs.setViewProgram('Z')

    def zero_wcs_xy(self):
        #_current_pos = float(POS.Absolute(0))
        #_current_pos = float(POS.Absolute(1))
        if self.btn_laser.isChecked():
            laser_x = self.laser_offset_x.value()
            laser_y = self.laser_offset_y.value()
        else:
            laser_x = 0
            laser_y = 0            
        issue_mdi(f"G10L20P0X{laser_x}Y{laser_y};G0X0Y0")
        self.btn_laser.setChecked(False)

    def cut_recovery_direction(self, direction):
        #
        # Cut recovery is heavily based on the work done within QTPlasmac.
        # Credit to Phillip A Carter and Gregory D Carl.
        #
        speed = self.cut_recovery_speed.value() * 0.01 * direction
        cnchal.set_p('plasmac.paused-motion-speed',str(speed))

    def cut_recovery(self):
        sender = self.sender()
        obj_name = sender.objectName()
        if obj_name == 'btn_stop_abort':
                self.widget_recovery.setEnabled(False)
                self.cut_recovery_status = False
                self.jog_stack.setCurrentIndex(0)
                cnchal.set_p('plasmac.x-offset', f'{0:.0f}')
                cnchal.set_p('plasmac.y-offset', f'{0:.0f}')
                return

        if obj_name == 'btn_cycle_start':
                self.widget_recovery.setEnabled(False)
                self.cut_recovery_status = False
                self.jog_stack.setCurrentIndex(0)
                cnchal.set_p('plasmac.x-offset', f'{0:.0f}')
                cnchal.set_p('plasmac.y-offset', f'{0:.0f}')
                return

        if obj_name == 'btn_feed_hold':
                self.widget_recovery.setEnabled(True)
                self.cut_recovery_status = True
                self.jog_stack.setCurrentIndex(1)
                self.xOrig = cnchal.get_value('axis.x.eoffset-counts')
                self.yOrig = cnchal.get_value('axis.y.eoffset-counts')
                self.zOrig = cnchal.get_value('axis.z.eoffset-counts')
                self.oScale = cnchal.get_value('plasmac.offset-scale')
                cnchal.set_p('plasmac.x-offset', f'{0:.0f}')
                cnchal.set_p('plasmac.y-offset', f'{0:.0f}')

    def cutrec_move(self, state, x, y):
        if state:
            maxMove = 10
            if self._linear_setting == 'inch':
                maxMove = 0.4
            laser = cnchal.get_value('qtpyvcp.laser.out') > 0
            distX = cnchal.get_value('qtpyvcp.param-kirfwidth.out') * x
            distY = cnchal.get_value('qtpyvcp.param-kirfwidth.out') * y
            xNew = cnchal.get_value('plasmac.axis-x-position') + cnchal.get_value('axis.x.eoffset') - (self.laser_offset_x.value() * laser) + distX
            yNew = cnchal.get_value('plasmac.axis-y-position') + cnchal.get_value('axis.y.eoffset') - (self.laser_offset_y.value() * laser) + distY
            #if xNew > self.xMax or xNew < self.xMin or yNew > self.yMax or yNew < self.yMin:
            #    return
            xTotal = cnchal.get_value('axis.x.eoffset') - (self.laser_offset_x.value() * laser) + distX
            yTotal = cnchal.get_value('axis.y.eoffset') - (self.laser_offset_y.value() * laser) + distY
            if xTotal > maxMove or xTotal < -maxMove or yTotal > maxMove or yTotal < -maxMove:
                return
            moveX = int(distX / self.oScale)
            moveY = int(distY / self.oScale)
            cnchal.set_p('plasmac.x-offset', f'{str(cnchal.get_value("plasmac.x-offset") + moveX)}')
            cnchal.set_p('plasmac.y-offset', f'{str(cnchal.get_value("plasmac.y-offset") + moveY)}')
            cnchal.set_p('plasmac.cut-recovery', '1')

    def cutrec_cancel_pressed(self, state):
        if (state):
            if cnchal.get_value('plasmac.cut-recovery'):
                cnchal.set_p('plasmac.cut-recovery', '0')

    def editor_buttons(self):
        sender = self.sender()
        obj_name = sender.objectName()
        if obj_name == 'btn_edit':
            return
        
        if obj_name == 'btn_save':
            return
        
        if obj_name == 'btn_edit':
            return
                

    def consumable_change(self):
        sender = self.sender()
        obj_name = sender.objectName()
        if obj_name == 'btn_stop_abort':
                self.btn_consumable_change.setEnabled(False)
                self.btn_consumable_change.setChecked(False)
                return

        if obj_name == 'btn_cycle_start':
                self.btn_consumable_change.setEnabled(False)
                self.btn_consumable_change.setChecked(False)
                return

        if obj_name == 'btn_feed_hold':
                self.btn_consumable_change.setEnabled(True)
                return

    def consumable_toggle(self, state):
        if state:
            # ensure machine can not be restarted while consumable is active
            self.btn_cycle_start.setEnabled(False)
            
            x_current_pos = float(POS.Absolute(0))
            y_current_pos = float(POS.Absolute(1))
            x_offset = self.consumable_offset_x.value()
            y_offset = self.consumable_offset_y.value()
            scale = cnchal.get_value('plasmac.offset-scale')
            cnchal.set_p('plasmac.x-offset', f'{(x_offset - x_current_pos)/scale:.0f}')
            cnchal.set_p('plasmac.y-offset', f'{(y_offset - y_current_pos)/scale:.0f}')
            cnchal.set_p('plasmac.consumable-change','1')
        else:
            cnchal.set_p('plasmac.x-offset', f'{0:.0f}')
            cnchal.set_p('plasmac.y-offset', f'{0:.0f}')
            cnchal.set_p('plasmac.consumable-change','0')
            self.btn_cycle_start.setEnabled(True)
            
    def adjust_probe_height(self):
        below_slat = self.slat_top - self.min_z
        buffer = 3
        new_probe_height = (below_slat + self._material_thickness + buffer) * self.units_per_mm
        self.probe_height.SetValue(new_probe_height)

    def probe_test_error(self, value):
        #self.probe_timer.stop()
        cnchal.set_p('plasmac.probe-test','0')
    
    def probe_timeout(self):
        print(f'probe time out')

    def probe_test(self, state):
        LOG.debug(f'probe test state: {state}')
        if state:
            #self.probe_timer.start(1000)
            # stop user from starting a program
            self.btn_cycle_start.setEnabled(False)
            cnchal.set_p('plasmac.probe-test','1')
        else:
            #self.probe_timer.stop()
            self.btn_cycle_start.setEnabled(True)
            cnchal.set_p('plasmac.probe-test','0')

    def breadcrumbs_tracked(self,state):
        LOG.debug(f'breadcrumb tracked {state}')
        vtk = self.vtkbackplot
        vtk.enableBreadcrumbs(state)
        vtk.clearLivePlot()

    def force_cutchart_reload(self, value):
        LOG.debug(f"Cutchart_Reload = {value}")
        if not int(value):
            # if False then nothing to do so exit
            return
        # get current cut chart pin value
        current = self.filter_cutchart_id
        # rest the reload pin back to False
        cnchal.set_p('qtpyvcp.cutchart-reload', '0')
        self.cutchart_pin_update(current)

    def cutchart_pin_update(self, value):
        LOG.debug(f"Cutchart_ID Pin = {value}")
        self.filter_cutchart_id = value
        try:
            # Get the cutchart record based on the pin value.
            cut = self._plasma_plugin.tool_id(value)[0]
        except:
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
            # Update the actual param fields.
            # Is called through gcode parsing change to cut ID or via
            # human interaction with the UI
            for k in MainWindow.param_fld_map:
                fld_data = getattr(data, k)
                ui_fld = getattr(self, MainWindow.param_fld_map[k])
                if isinstance(ui_fld, QLabel):
                    ui_fld.setText(str(fld_data))
                    if k == 'tool_number':
                        self._tool_number = int(fld_data)
                else:
                    ui_fld.setValue(fld_data)
                    # due to events not seeming to trigger we need to force an update
                    if hasattr(ui_fld, "forceUpdatePinValue"):
                        ui_fld.forceUpdatePinValue()
            LOG.debug(f"Thickness = {data.thickness.thickness}")
            self._material_thickness = data.thickness.thickness
        else:
            self.grp_filter_sub_list.hide()
            # set cut params to 0
            ui_fld = getattr(self, 'param_name')
            ui_fld.setText('NONE')
            ui_fld = getattr(self, 'param_process_id')
            ui_fld.setText('NONE')
            self._tool_number = 0
            self._material_thickness = 0
            for v in MainWindow.param_fld_map.values():
                if v not in ('param_name', 'param_process_id'):
                    ui_fld = getattr(self, v)
                    ui_fld.setValue(0)
        # All fields have been set, update any slave displays
        LOG.debug(f"Tool Number = {self._tool_number}")
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
                        if k == 'tool_number':
                            self._tool_number = int(fld_data)
                            LOG.debug(f"Tool Number = {self._tool_number}")
                    else:
                        ui_fld.setValue(fld_data) 
                LOG.debug(f"Thickness = {d.thickness.thickness}")
                self._material_thickness = d.thickness.thickness
    
    def setMode(self):
        LOG.debug("main window initalise")
    
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
        # correctly set the tool_number
        self.last_tool_num_assigned += 1
        arglist['tool_number'] = self.last_tool_num_assigned
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
            self.latest_real_file=newist[0]
            loadProgram(newist[0])

    def single_cut_limits(self):
        # Assumes an axis sequence of x:0, y:1, z:2
        sender = self.sender()
        # print(f'single_cut_limits:  {sender.objectName()}')
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
        src = os.path.expanduser(self.lne_seed_source.text())

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
        LOG.debug(f"MDI button clicked text: {text}")
        if text != 'null':
            # we have something to check so get the gcode words
            words = mdiText.gcode_words()
            if text in words:
                # clear the mdi line
                self.mdiClear()
                for index, value in enumerate(words[text], start=1):
                    # search and populate the params available for that gcode word
                    LOG.debug(f"MDI Param search: {value}")
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
            LOG.debug('MDI - No Param Match')


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
    # VTK Display and Gcode
    #
    def tranformUI_reset(self):
        LOG.debug("Reset to default values")

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
    
    # Reload the current file.  That means the most recently loaded file
    def reload_file(self):    
        #real_file = self.gcode_recentfile.currentData()
        real_file = self.latest_real_file
        if real_file == None or real_file == "":
            return
        loadProgram(real_file)

    #
    # Frame prog on work piece
    #
    def frame_work(self):
        # hack into VTK to get at some internals to get prog bounds
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
        x_laser_offset = self.laser_offset_x.value()
        y_laser_offset = self.laser_offset_y.value()
        if not self.btn_laser.isChecked():
            x_laser_offset = 0
            y_laser_offset = 0
        
        if (y_current + y_length + y_laser_offset) > min_max_y[1]:
            LOG.error(f'FRAMING ERROR: Y will exceed Y-Max')
            return
        if (x_current + x_length + x_laser_offset) > min_max_x[1]:
            LOG.error(f'FRAMING ERROR: X will exceed X-Max')
            return
        if (y_current + y_length + y_laser_offset) < min_max_y[0]:
            LOG.error(f'FRAMING ERROR: Y will exceed Y-Min')
            return
        if (x_current + x_length + x_laser_offset) < min_max_x[0]:
            LOG.error(f'FRAMING ERROR: X will exceed X-Min')
            return
        
        feed_rate = self.framing_feed_rate.value()
        # move_cmd = (
        #     f"F{feed_rate};"
        #     f"G53 G0 Z{min_max_z[1]};"
        #     f"G53 G0 X{x_current + x_laser_offset} Y{y_current + y_laser_offset};"
        #     f"G53 G1 Y{y_current + y_laser_offset + y_length};"
        #     f"G53 G1 X{x_current + x_laser_offset + x_length};"
        #     f"G53 G1 Y{y_current + y_laser_offset};"
        #     f"G53 G1 X{x_current + x_laser_offset};"
        #     f"G53 G1 X{x_current}Y{y_current}"
        # )
        move_cmd = (
            f"F{feed_rate};"
            f"G53 G0 Z{min_max_z[1]};"
            f"G0 X{x_laser_offset} Y{y_laser_offset};"
            f"G91;"
            f"G1 Y{y_length};"
            f"G1 X{x_length};"
            f"G1 Y-{y_length};"
            f"G1 X-{x_length};"
            f"G90;"
            f"G53 G1 X{x_current}Y{y_current}"
        )
        issue_mdi(move_cmd)
        LOG.debug("Frame complete")

    
    #
    # Adjust virtual offsets to cope with sheet stock
    # not being perfectly square to axis of travel.
    #
    # Original code, concept and smarts from QTPlasmac author.
    #
    
    def sheet_align_toggle(self, checked=False):
        sender = self.sender()
        obj_name = sender.objectName()
        match obj_name:
            case 'btn_laser':
                LOG.debug(f'laser {checked}')
                if checked:
                    self.btn_sheet_align_pt1.setEnabled(checked)
                    set_mode.manual()
                else:
                    self.btn_sheet_align_pt1.setChecked(False)
                    self.btn_sheet_align_pt2.setChecked(False)
                    self.btn_sheet_align_pt1.setEnabled(False)
                    self.btn_sheet_align_pt2.setEnabled(False)
                    self.btn_sheet_doalign.setEnabled(False)
                    self.sheet_align_p1 = None
                    self.sheet_align_p2 = None
                    self.build_status_text()

            case 'btn_sheet_align_pt1':
                LOG.debug('point 1')
                if checked:
                    self.btn_sheet_align_pt2.setEnabled(True)
                    self.sheet_align_set_p1()
                    set_mode.manual()
                else:
                    self.btn_sheet_align_pt2.setChecked(False)
                    self.btn_sheet_align_pt2.setEnabled(False)
                    self.btn_sheet_doalign.setEnabled(False)
                    self.sheet_align_p1 = None
                    self.build_status_text()
            
            case 'btn_sheet_align_pt2':
                LOG.debug('point 2')
                if checked:
                    self.btn_sheet_doalign.setEnabled(True)
                    self.sheet_align_set_p2()
                    set_mode.manual()
                else:
                    self.btn_sheet_doalign.setEnabled(False)
                    self.sheet_align_p2 = None
                    self.build_status_text()

            case 'btn_sheet_doalign':
                # do sheet alignment
                LOG.debug('Do alignment')
                self.sheet_align()
                # reset UI state
                self.btn_sheet_align_pt1.setChecked(False)
                self.btn_sheet_align_pt2.setChecked(False)
                self.btn_laser.setChecked(False)
                self.btn_sheet_align_pt1.setEnabled(False)
                self.btn_sheet_align_pt2.setEnabled(False)
                self.btn_sheet_doalign.setEnabled(False)
    
    def sheet_align(self):
        if self.sheet_align_p1 == None or \
           self.sheet_align_p2 == None:
            LOG.debug("Sheet alignment attempted but not all points set.")
            # reset UI state
            self.btn_sheet_align_pt1.setChecked(False)
            self.btn_sheet_align_pt2.setChecked(False)
            self.btn_laser.setChecked(False)
            self.btn_sheet_align_pt1.setEnabled(False)
            self.btn_sheet_align_pt2.setEnabled(False)
            self.btn_sheet_doalign.setEnabled(False)
            return
        # need p1 and p2 set for edge only alignment.
        # Assumed that p1 will be X0Y0
    
        issue_mdi('G10 L2 P0 R0')
        CMD.wait_complete()
        issue_mdi('G10 L2 P0 X0 Y0')
        CMD.wait_complete()
        set_mode.manual()
        CMD.wait_complete()
        #xDiff = self.sheet_align_p2[0] - self.sheet_align_p1[0]
        #yDiff = self.sheet_align_p2[1] - self.sheet_align_p1[1]
        xDiff = self.sheet_align_p2[0] - self.sheet_align_p1[0]
        yDiff = self.sheet_align_p2[1]- self.sheet_align_p1[1]
        if xDiff and yDiff:
            zAngle = math.degrees(math.atan(yDiff / xDiff))
            if xDiff > 0:
                zAngle += 180
            elif yDiff > 0:
                zAngle += 360
            if abs(xDiff) < abs(yDiff):
                zAngle -= 90
        elif xDiff:
            if xDiff > 0:
                zAngle = 180
            else:
                zAngle = 0
        elif yDiff:
            if yDiff > 0:
                zAngle = 180
            else:
                zAngle = 0
        else:
            zAngle = 0

        laser_x = self.laser_offset_x.value()
        laser_y = self.laser_offset_y.value()
        LOG.debug(f'G10 L2 P0 X{self.sheet_align_p1[0]-laser_x} Y{self.sheet_align_p1[1]-laser_y}')
        LOG.debug(f'G10 L2 P0 R{zAngle}')
        #issue_mdi(f'G10 L2 P0 X{self.sheet_align_p1[0]-laser_x} Y{self.sheet_align_p1[1]-laser_y}')
        issue_mdi(f'G10 L20 P0 X{laser_x} Y{laser_y}')
        CMD.wait_complete()
        issue_mdi(f'G10 L2 P0 R{zAngle}')
        CMD.wait_complete()
        issue_mdi('G0 X0 Y0')
        CMD.wait_complete()
        LOG.debug('Alignment done.')
        self.sheet_align_p1 = None
        self.sheet_align_p2 = None
        self.build_status_text()
    
    def build_status_text(self):
        widget = self.lbl_align_data
        ref1 = "REF1:..."
        ref2 = "REF2:..."
        if self. sheet_align_p1 != None:
            ref1 = f"REF1:\n{self.sheet_align_p1[0]:.4f},\n{self.sheet_align_p1[1]:.4f}"
        
        if self. sheet_align_p2 != None:
            ref2 = f"REF2:\n{self.sheet_align_p2[0]:.4f},\n{self.sheet_align_p2[1]:.4f}"
        widget.setText(f'{ref1}\n{ref2}')
    
    def sheet_align_set_p1(self):
        issue_mdi('G10 L2 P0 R0')
        x_current_pos = float(POS.Absolute(0))
        y_current_pos = float(POS.Absolute(1))
        self.sheet_align_p1 = [x_current_pos, y_current_pos]
        self.build_status_text()

    
    def sheet_align_set_p2(self):
        issue_mdi('G10 L2 P0 R0')
        x_current_pos = float(POS.Absolute(0))
        y_current_pos = float(POS.Absolute(1))
        self.sheet_align_p2 = [x_current_pos, y_current_pos]
        self.build_status_text()
    
