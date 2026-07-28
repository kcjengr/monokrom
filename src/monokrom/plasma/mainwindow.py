import os
from tempfile import NamedTemporaryFile

from qtpyvcp import hal as qthal
import linuxcnc

### Supports the @Slot decorator to solve property type issues.
from PySide6.QtCore import Qt, QItemSelectionModel, Slot, QTimer
from PySide6.QtWidgets import QLabel, QListWidgetItem, QAbstractButton, QTableView, QListWidget
import qtpyvcp
from qtpyvcp.widgets.form_widgets.main_window import VCPMainWindow
from qtpyvcp.plugins import getPlugin
from qtpyvcp.utilities.info import Info
from qtpyvcp.actions.program_actions import load as loadProgram
from qtpyvcp.actions.machine_actions import mode as set_mode
from qtpyvcp.actions.machine_actions import jog

import monokrom_rc
import common_rc

### mdi GCODE text created by JT from linuxcnc
from monokrom.plasma.hal_bridge import HALBridge
from monokrom.plasma.consumable_change import ConsumableChangeService
from monokrom.plasma.cut_recovery import CutRecoveryService
from monokrom.plasma.sheet_alignment import SheetAlignmentService
from monokrom.plasma.mdi_panel import MdiPanelService
from monokrom.plasma.shape_generator import ShapeGeneratorService
from monokrom.plasma.file_ops import FileOpsService
from monokrom.plasma.process_filter import ProcessFilterService

# Part of debug tracing enablement under Eclipse/Pydev - leave.
# import pydevd;pydevd.settrace()

__updated__ = "2026-07-28"


# Setup logging
from qtpyvcp.utilities import logger

LOG = logger.getLogger("qtpyvcp." + __name__)
INFO = Info()
STATUS = getPlugin("status")
STAT = STATUS.stat
POS = getPlugin("position")

# GCODEPROPS = getPlugin('gcode_properties')

ini_file = os.environ.get("LINUXCNC_INI_FILE", "")
INI = linuxcnc.ini(ini_file) if ini_file else INFO.ini
NGC_LOC = INI.find("DISPLAY", "PROGRAM_PREFIX")
if NGC_LOC is None:
    NGC_LOC = "~/linuxcnc/nc_files"

USER_BUTTONS = 10


class MainWindow(VCPMainWindow):
    """Main window class for the VCP."""

    # field map of <plugin data getter>:<ui obj name>
    locked_fld_map = {
        "machines": "filter_machine",
        "linearsystems": "filter_distance_system",
        "pressuresystems": "filter_pressure_system",
    }

    # field map of <plugin data getter>:<ui obj name>
    filter_fld_map = {
        "gases": "filter_gas",
        "machines": "filter_machine",
        "materials": "filter_material",
        "thicknesses": "filter_thickness",
        "linearsystems": "filter_distance_system",
        "pressuresystems": "filter_pressure_system",
        "operations": "filter_operation",
        "qualities": "filter_quality",
        "consumables": "filter_consumable",
    }

    # field map of <plugin data getter>:<cutchart orm relationship field>
    relationship_fld_map = {
        "gases": "gas",
        "machines": "machine",
        "materials": "material",
        "thicknesses": "thickness",
        "linearsystems": "linearsystem",
        "pressuresystems": "pressuresystem",
        "operations": "operation",
        "qualities": "quality",
        "consumables": "consumable",
    }

    param_fld_map = {
        "name": "param_name",
        "tool_number": "param_process_id",
        #'id':'param_process_id',
        "pierce_height": "param_pierceheight",
        "pierce_delay": "param_piercedelay",
        "cut_height": "param_cutheight",
        "cut_speed": "param_cutfeedrate",
        "plunge_rate": "param_plungefeedrate",
        "volts": "param_cutvolts",
        "kerf_width": "param_kirfwidth",
        "puddle_height": "param_puddlejumpheight",
        "puddle_delay": "param_puddlejumpdelay",
        "amps": "param_cutamps",
        "pause_at_end": "param_pauseatend",
        "pressure": "param_gaspressure",
    }

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self._init_services()
        self._setup_ui_defaults()
        self._connect_signals()
        self._create_hal_pins()

    def _init_services(self):
        # -- Service instantiation ------------------------------------------------
        self.hal = HALBridge()
        self.consumable_service = ConsumableChangeService(self.hal)
        self.sheet_align_service = SheetAlignmentService(self.hal)
        self.cut_recovery_service = CutRecoveryService(self.hal)
        self.shape_gen_service = ShapeGeneratorService(self)
        self.file_ops = FileOpsService(self)
        self._plasma_plugin = getPlugin("plasmaprocesses")
        self.process_filter_service = ProcessFilterService(self)

        # -- State initialization -------------------------------------------------
        self.filter_cutchart_id = None
        self.detail_index_num = 0
        self.latest_real_file = ""
        self._tool_number = 0
        self._material_thickness = 0

        # -- INI / info reads -----------------------------------------------------
        self.min_x = float(INI.find("AXIS_X", "MIN_LIMIT"))
        self.min_y = float(INI.find("AXIS_Y", "MIN_LIMIT"))
        self.max_x = float(INI.find("AXIS_X", "MAX_LIMIT"))
        self.max_y = float(INI.find("AXIS_Y", "MAX_LIMIT"))
        self.min_z = INFO.getAxisMinMax("Z")[0]
        self.slat_top = float(INI.find("PLASMAC", "SLAT_TOP"))

        z_max_vel = float(INI.find("AXIS_Z", "MAX_VELOCITY")) * 60 / 2
        self.thc_feed_rate.setText(str(z_max_vel))
        self.hal.set_p("plasmac.thc-feed-rate", str(z_max_vel))

        if INFO.getIsMachineMetric():
            self._linear_setting = "mm"
            LOG.debug("Machine is Metric")
        else:
            self._linear_setting = "inch"
            LOG.debug("Machine is Imperial")

        self.units_per_mm = self.hal.get_value("halui.machine.units-per-mm")
        self._pressure_setting = INFO.ini.find("PLASMAC", "PRESSURE")
        self._machine = INFO.ini.find("PLASMAC", "MACHINE")

        # need to hold linear setting ID so can filter thicknesses based on measurement system
        for s in self._plasma_plugin.linearsystems():
            if s.name == self._linear_setting:
                self._linear_setting_id = s.id
                LOG.debug(f"Linear system ID held = {self._linear_setting_id}")

    def _setup_ui_defaults(self):
        # -- Dialog widget handles ------------------------------------------------
        LOG.debug("monokrom-Mainwindow:  dialogs loaded")
        self.open_file_dialog_widget = qtpyvcp.DIALOGS["open_file"].findChild(
            QTableView
        )
        self.recent_files_dialog_widget = qtpyvcp.DIALOGS["recent_files"].findChild(
            QListWidget
        )

        # -- Probe timer ----------------------------------------------------------
        self.probe_timer = QTimer()
        self.probe_timer.timeout.connect(self.probe_timeout)

        # -- Tab visibility / VTK defaults ----------------------------------------
        self.tabs_ctl_run_right.setTabVisible(2, False)
        self.tab_holes_and_slots.setTabVisible(1, False)

        for plot in (self.vtkbackplot, self.vtk_qs):
            plot.update_active_wcs(0)
            plot.setViewZ()
            plot.enable_panning(True)
            plot.setProgramViewWhenLoadingProgram(True, "z")

        # -- Widget states / visibility -------------------------------------------
        self.widget_recovery.setEnabled(False)
        self.btn_consumable_change.setEnabled(False)
        self.mdiFrame.hide()
        self.transformFrame.hide()
        self.grp_filter_sub_list.hide()

        # -- Consumable offset bounds ---------------------------------------------
        margin = 10 * self.units_per_mm
        self.consumable_offset_x.setMinimum(self.min_x + margin)
        self.consumable_offset_y.setMinimum(self.min_y + margin)
        self.consumable_offset_x.setMaximum(self.max_x - margin)
        self.consumable_offset_y.setMaximum(self.max_y - margin)

        # -- Jog defaults ---------------------------------------------------------
        jog.set_increment(1 * self.units_per_mm)
        jog.set_jog_continuous(True)
        self.smart_hole_indicator.setState(self.chkb_hole_detect_enable.isChecked())

        # -- User buttons ---------------------------------------------------------
        for user_i in range(1, USER_BUTTONS + 1):
            user_btn = getattr(self, f"user{user_i}")
            if user_btn is None:
                continue
            user_name = INFO.ini.find("DISPLAY", f"USER{user_i}_NAME")
            if user_name:
                user_action = INFO.ini.find("DISPLAY", f"USER{user_i}_ACTION")
                user_btn.setText(user_name)
                user_btn.filename = user_action

        # -- Locked filters -------------------------------------------------------
        self.filter_machine.setCurrentText(self._machine)
        self.filter_distance_system.setCurrentText(self._linear_setting)
        self.filter_pressure_system.setCurrentText(self._pressure_setting)

    def _connect_signals(self):
        # -- Filter / process signals ---------------------------------------------
        self.btn_save_run_process.clicked.connect(self.update_cut)
        self.btn_run_reload.clicked.connect(self.param_update_from_filters)
        self.filter_sub_list.itemClicked.connect(self.filter_sub_list_select)
        self.btn_seed_db.clicked.connect(self.seed_database)

        for val in MainWindow.filter_fld_map.values():
            filter_widget = getattr(self, val)
            filter_widget.currentIndexChanged.connect(self.param_update_from_filters)

        # -- General UI signals ---------------------------------------------------
        self.btn_zero_xy.clicked.connect(self.zero_wcs_xy)
        self.btn_probe_test.toggled.connect(self.probe_test)
        self.vtk_no_lines.toggled.connect(self.breadcrumbs_tracked)
        self.grp_shape_btns.buttonClicked.connect(self.clicked_shape_btn)
        self.btn_qs_refresh.clicked.connect(self.clicked_qs_refresh)
        self.single_cut_x.focusReceived.connect(self.single_cut_limits)
        self.single_cut_y.focusReceived.connect(self.single_cut_limits)

        # -- Dialog signals -------------------------------------------------------
        self.open_file_dialog_widget.fileLoadFromDialog.connect(self.set_openfile)
        self.recent_files_dialog_widget.fileLoadFromDialog.connect(self.set_openfile)

        # -- File I/O ------------------------------------------------------------
        self.btn_load_newest.clicked.connect(self.openLatest)
        
        # reload
        self.btn_reload.clicked.connect(self.reload_file)
        self.btn_reload_2.clicked.connect(self.reload_file)
        self.btn_transform_apply.clicked.connect(self.reload_file)

        # -- Slider resets --------------------------------------------------------
        self.btn_reset_rapid.clicked.connect(lambda: self.rapid_slider.setValue(100))
        self.btn_reset_feed.clicked.connect(lambda: self.feed_slider.setValue(100))
        self.btn_reset_jog.clicked.connect(lambda: self.jog_slider.setValue(100))

        # -- Cut recovery ---------------------------------------------------------
        self.btn_cut_recover_rev.pressed.connect(
            lambda: self.on_cut_recovery_direction(-1)
        )
        self.btn_cut_recover_fwd.pressed.connect(
            lambda: self.on_cut_recovery_direction(1)
        )
        self.btn_cut_recover_rev.released.connect(
            lambda: self.on_cut_recovery_direction(0)
        )
        self.btn_cut_recover_fwd.released.connect(
            lambda: self.on_cut_recovery_direction(0)
        )
        self.btn_cut_recover_cancel.pressed.connect(self.on_cut_recovery_cancel)
        self.btn_recovery_n.pressed.connect(lambda: self.on_cut_recovery_move(0, 1))
        self.btn_recovery_ne.pressed.connect(lambda: self.on_cut_recovery_move(1, 1))
        self.btn_recovery_e.pressed.connect(lambda: self.on_cut_recovery_move(1, 0))
        self.btn_recovery_se.pressed.connect(lambda: self.on_cut_recovery_move(1, -1))
        self.btn_recovery_s.pressed.connect(lambda: self.on_cut_recovery_move(0, -1))
        self.btn_recovery_sw.pressed.connect(lambda: self.on_cut_recovery_move(-1, -1))
        self.btn_recovery_w.pressed.connect(lambda: self.on_cut_recovery_move(-1, 0))
        self.btn_recovery_nw.pressed.connect(lambda: self.on_cut_recovery_move(-1, 1))

        # -- Cut recovery buttons (expects button names like 'btn_feed_hold') ----
        for btn_name in ("btn_feed_hold", "btn_cycle_start", "btn_stop_abort"):
            getattr(self, btn_name).clicked.connect(
                lambda x, b=btn_name: self.on_cut_recovery_button(b)
            )

        # -- Consumable change buttons (expects action names like 'feed_hold') ----
        for btn_name, action in [
            ("btn_feed_hold", "feed_hold"),
            ("btn_cycle_start", "cycle_start"),
            ("btn_stop_abort", "stop_abort"),
        ]:
            getattr(self, btn_name).clicked.connect(
                lambda x, a=action: self.on_consumable_button(a)
            )

        self.btn_consumable_change.toggled.connect(self.on_consumable_toggle)

        # -- VTK ------------------------------------------------------------------
        self.vtk_center.clicked.connect(lambda: self.vtkbackplot.setViewProgram("Z"))

        # -- MDI ------------------------------------------------------------------
        self.mdi_service = MdiPanelService(self)
        self.btnMdiParams.clicked.connect(self.btnParams_clicked)
        self.btnMdiBksp.clicked.connect(self.mdiBackSpace_clicked)
        self.btnMdiSpace.clicked.connect(self.mdiSpace_clicked)

        self.btn_save.clicked.connect(self.save_file)
        self.btn_frame_job.clicked.connect(self.frame_work)

        # -- Sheet Alignment ------------------------------------------------------
        self.btn_laser.toggled.connect(self.on_sheet_align_laser)
        self.btn_sheet_align_pt1.toggled.connect(self.on_sheet_align_pt1)
        self.btn_sheet_align_pt2.toggled.connect(self.on_sheet_align_pt2)
        self.btn_sheet_doalign.clicked.connect(self.on_sheet_align_doalign)

    def _create_hal_pins(self):
        comp = qthal.getComponent()

        # -- Cutchart / filter pins -----------------------------------------------
        self.hal_cutchart_id = comp.addPin("cutchart-id", "u32", "in")
        comp.addListener("cutchart-id", self.cutchart_pin_update)
        self.hal_cutchart_reload = comp.addPin("cutchart-reload", "bit", "in")
        comp.addListener("cutchart-reload", self.force_cutchart_reload)

        # -- Probe test error pin -------------------------------------------------
        self.hal_probe_test_error = comp.addPin("probe-test-error", "bit", "in")
        comp.addListener("probe-test-error", self.probe_test_error)

        # -- Material ID for gcode preprocessor -----------------------------------
        self.hal_material_id = comp.addPin("material-id", "u32", "io")

        # -- Default cut chart load -----------------------------------------------
        default_cut_chart = INFO.ini.find("PLASMAC", "DEFAULT_CUTCHART")
        if default_cut_chart is not None:
            self.cutchart_pin_update(default_cut_chart)

        # -- Find largest tool ID -------------------------------------------------
        tools = self._plasma_plugin.tool_list_for_lcnc()
        self.last_tool_num_assigned = -1
        for tool in tools:
            LOG.debug(f"tool = id: {tool.id}, num: {tool.tool_number}")
            if (
                tool.tool_number > self.last_tool_num_assigned
                and tool.tool_number != 99999
            ):
                self.last_tool_num_assigned = tool.tool_number

        # -- External trigger pins ------------------------------------------------
        triggers = [
            (self.btn_feed_hold, "btn-feed-hold"),
            (self.btn_stop_abort, "btn-stop-abort"),
            (self.btn_laser, "btn-laser"),
            (self.btn_sheet_align_pt1, "btn-sheet-align-pt1"),
            (self.btn_sheet_align_pt2, "btn-sheet-align-pt2"),
            (self.btn_sheet_doalign, "btn-sheet-doalign"),
        ]
        for btn, pin_name in triggers:
            pin = comp.addPin(f"{pin_name}.external-trigger", "bit", "in")
            setattr(self, f"{btn.objectName()}_trigger_pin", pin)
            pin.valueChanged.connect(lambda x, b=btn: b.click() if x else None)

        # -- Load filter data after all widgets are ready -------------------------
        self.load_plasma_ui_filter_data()

    def on_exitAppBtn_clicked(self):
        from qtpy.QtWidgets import QApplication

        QApplication.instance().quit()

    def reset_vtk_btns(self):
        self.vtk_prog_extent.setChecked(False)
        self.vtk_mach_extent.setChecked(False)
        self.vtkbackplot.showProgramBounds(False)
        self.vtkbackplot.showMachineBounds(False)

    def set_openfile(self, file_str):
        self.latest_real_file = file_str
        self.reset_vtk_btns()
        LOG.debug(f"set_openfile:  file_str = {file_str}")

    def clicked_shape_btn(self, btn):
        btn_name = btn.objectName()
        LOG.debug(f"shape button pushed: {btn_name} with index {int(btn_name[4:])}")
        self.detail_index_num = int(btn_name[4:])
        self.details_pages.setCurrentIndex(self.detail_index_num)

    def clicked_qs_refresh(self):
        LOG.debug("clicked_qs_refresh")
        lines, error_msg = self.shape_gen_service.generate(self.detail_index_num)
        if error_msg:
            LOG.error(f"Shape generation error: {error_msg}")
            return
        with NamedTemporaryFile(mode="w+", suffix=".ngc", delete=False) as temp_file:
            temp_name = temp_file.name
            temp_file.writelines(lines)
        # make sure hole processing it off as lead ins seem to cause it issues:
        # self.chkb_hole_detect_enable.setCheckState(False)
        self.set_openfile(temp_name)
        loadProgram(temp_name, add_to_recents=False)
        self.vtkbackplot.setViewProgram("Z")
        self.vtk_qs.setViewProgram("Z")
        self.reset_vtk_btns()

    def zero_wcs_xy(self):
        # _current_pos = float(POS.Absolute(0))
        # _current_pos = float(POS.Absolute(1))
        if self.btn_laser.isChecked():
            laser_x = self.laser_offset_x.value()
            laser_y = self.laser_offset_y.value()
        else:
            laser_x = 0
            laser_y = 0
        self.hal.send_mdi(f"G10L20P0X{laser_x}Y{laser_y};G0X0Y0")
        self.btn_laser.setChecked(False)

    def on_cut_recovery_direction(self, direction):
        speed = self.cut_recovery_speed.value() * 0.01 * direction
        self.cut_recovery_service.set_direction(direction, speed)

    def on_cut_recovery_button(self, button_name):
        self.cut_recovery_service.handle_button(
            button_name,
            self.widget_recovery,
            self.jog_stack,
            self.cut_recovery_speed.value(),
        )

    def on_cut_recovery_move(self, x_dir, y_dir):
        self.cut_recovery_service.move(
            x_dir,
            y_dir,
            self.laser_offset_x.value(),
            self.laser_offset_y.value(),
            self._linear_setting,
            self.btn_cut_recover_fwd,
            self.btn_cut_recover_rev,
        )

    def on_cut_recovery_cancel(self):
        self.cut_recovery_service.cancel_pressed()

    def on_consumable_button(self, action):
        changes = self.consumable_service.handle_button(
            action,
            self.btn_consumable_change.isEnabled(),
            self.btn_consumable_change.isChecked(),
            self.btn_cycle_start.isEnabled(),
        )
        if not changes:
            return
        for widget_name, state in changes.items():
            widget = getattr(self, widget_name)
            if "enabled" in state:
                widget.setEnabled(state["enabled"])
            if "checked" in state:
                widget.setChecked(state["checked"])

    def on_consumable_toggle(self, checked):
        if checked:
            changes = self.consumable_service.toggle_on(
                self.consumable_offset_x.value(), self.consumable_offset_y.value(), POS
            )
        else:
            changes = self.consumable_service.toggle_off()

        for widget_name, state in changes.items():
            widget = getattr(self, widget_name)
            if "enabled" in state:
                widget.setEnabled(state["enabled"])
            if "checked" in state:
                widget.setChecked(state["checked"])

    def adjust_probe_height(self):
        below_slat = self.slat_top - self.min_z
        buffer = 3
        new_probe_height = (
            below_slat + self._material_thickness + buffer
        ) * self.units_per_mm
        self.probe_height.SetValue(new_probe_height)

    def probe_test_error(self, value):
        # self.probe_timer.stop()
        self.hal.set_p("plasmac.probe-test", "0")

    def probe_timeout(self):
        LOG.debug("probe time out")

    def probe_test(self, state):
        LOG.debug(f"probe test state: {state}")
        if state:
            # self.probe_timer.start(1000)
            # stop user from starting a program
            self.btn_cycle_start.setEnabled(False)
            self.hal.set_p("plasmac.probe-test", "1")
        else:
            # self.probe_timer.stop()
            self.btn_cycle_start.setEnabled(True)
            self.hal.set_p("plasmac.probe-test", "0")

    def breadcrumbs_tracked(self, state):
        LOG.debug(f"breadcrumb tracked {state}")
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
        self.hal.set_p("qtpyvcp.cutchart-reload", "0")
        self.cutchart_pin_update(current)

    def cutchart_pin_update(self, value):
        LOG.debug(f"Cutchart_ID Pin = {value}")
        self.filter_cutchart_id = value
        try:
            # Get the cutchart record based on the pin value.
            cut = self._plasma_plugin.tool_id(value)[0]
        except Exception as e:
            LOG.warning(f"No Tool / Cutchart found. Error: {e}")
        else:
            # Cycle through all the filters and set them to the correct value
            for k in MainWindow.relationship_fld_map:
                # get handle to UI field
                ui_fld = getattr(self, MainWindow.filter_fld_map[k])
                new_index = ui_fld.findData(
                    getattr(cut, MainWindow.relationship_fld_map[k]).id
                )
                ui_fld.setCurrentIndex(new_index)
            # check to see if there is a sub select required, if so select it

            # All fields have been set, update any slave displays
            ui_fld = getattr(self, "param_name")
            self.lbl_process_name.setText(ui_fld.text())

    def load_plasma_ui_filter_data(self):
        self.process_filter_service.load_ui_filter_data()

    def get_filter_query(self):
        return self.process_filter_service.get_filter_query()

    def get_current_cut(self):
        return self.process_filter_service.get_current_cut()

    def param_update_from_filters(self, index=0):
        self.process_filter_service.param_update_from_filters(index)

    def filter_sub_list_select(self, item):
        self.process_filter_service.filter_sub_list_select(item)

    def setMode(self):
        LOG.debug("main window initalise")

    def add_new_cut_process(self, name=None):
        self.process_filter_service.add_new_cut_process(name)

    def update_cut(self):
        self.process_filter_service.update_cut()

    def openLatest(self):
        """Opens the latest file by date/time in the default ngc location"""
        self.file_ops.open_latest()

    def single_cut_limits(self):
        # Assumes an axis sequence of x:0, y:1, z:2
        sender = self.sender()
        # print(f'single_cut_limits:  {sender.objectName()}')
        min = 0
        max = 0
        if sender.objectName() == "single_cut_x":
            x_pos = POS.Absolute.getValue()[0]
            min = self.min_x - x_pos
            max = self.max_x - x_pos
            # print(f'Absolute X position = {x_pos},  Min={min}, Max={max}, X-Max={self.max_x}')
        elif sender.objectName() == "single_cut_y":
            y_pos = POS.Absolute.getValue()[1]
            # print(f'Absolute Y position = {y_pos},  Min={min}, Max={max}, X-Max={self.max_y}')
            min = self.min_y - y_pos
            max = self.max_y - y_pos
        # set the min/max ranges on the control
        sender.setMaximum(max)
        sender.setMinimum(min)

    def seed_database(self):
        # get db source file and initiate seed
        src = os.path.expanduser(self.lne_seed_source.text())

        if not os.path.isfile(src):
            LOG.debug("DB seed file not found")
            self.lbl_seed_status.setText("DB seed file not found.")
            return

        self.lbl_seed_status.setText("DB seeding started.")
        # file exists. Assume is correct format else things will fail
        self._plasma_plugin.seed_data_base(src)
        self.lbl_seed_status.setText("DB seeding Done.")

    #
    # MDI Panel
    #
    @Slot(QAbstractButton)
    def on_btngrpMdi_buttonClicked(self, button):
        self.mdi_service.append_char(str(button.text()))

    def btnParams_clicked(self):
        text = self.mdiEntry.text()
        LOG.debug(f"MDI button clicked text: {text}")
        self.mdi_service.lookup_params(text)

    def mdiBackSpace_clicked(self):
        self.mdi_service.backspace()

    def mdiSpace_clicked(self):
        self.mdi_service.add_space()

    #
    # VTK Display and Gcode
    #
    def tranformUI_reset(self):
        LOG.debug("Reset to default values")

    #
    # GCode Editor
    #
    def save_file(self):
        self.file_ops.save_file()

    def reload_file(self):
        self.file_ops.reload_file()

    #
    # Frame prog on work piece
    #
    def frame_work(self):
        # hack into VTK to get at some internals to get prog bounds
        vtk = self.vtkbackplot
        program_bounds = vtk.program_bounds_actors[vtk.active_wcs_index].GetBounds()
        LOG.debug(f"prog bounds = {program_bounds}")
        # sample bounds response: (5.659999976158142, 242.86000610351562, 6.462499976158142, 85.72250366210938, 0.0, 0.0)
        # in min/max pairs for X, Y and Z
        x_length = program_bounds[1] - program_bounds[0]
        y_length = program_bounds[3] - program_bounds[2]
        # ignore Z as we don't use it for bounding
        # get max z-height, x-current, y-current
        x_current = POS.abs(0)
        y_current = POS.abs(1)
        # boundaries for move
        min_max_x = INFO.getAxisMinMax("X")[0]
        min_max_y = INFO.getAxisMinMax("Y")[0]
        min_max_z = INFO.getAxisMinMax("Z")[0]
        x_laser_offset = self.laser_offset_x.value()
        y_laser_offset = self.laser_offset_y.value()
        if not self.btn_laser.isChecked():
            x_laser_offset = 0
            y_laser_offset = 0

        if (y_current + y_length + y_laser_offset) > min_max_y[1]:
            LOG.error("FRAMING ERROR: Y will exceed Y-Max")
            return
        if (x_current + x_length + x_laser_offset) > min_max_x[1]:
            LOG.error("FRAMING ERROR: X will exceed X-Max")
            return
        if (y_current + y_length + y_laser_offset) < min_max_y[0]:
            LOG.error("FRAMING ERROR: Y will exceed Y-Min")
            return
        if (x_current + x_length + x_laser_offset) < min_max_x[0]:
            LOG.error("FRAMING ERROR: X will exceed X-Min")
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
        self.hal.send_mdi(move_cmd)
        LOG.debug("Frame complete")

    #
    # Adjust virtual offsets to cope with sheet stock
    # not being perfectly square to axis of travel.
    #
    # Original code, concept and smarts from QTPlasmac author.
    #

    def on_sheet_align_laser(self, checked):
        changes = self.sheet_align_service.handle_toggle("btn_laser", checked)
        if "btn_sheet_align_pt1" in changes:
            self.btn_sheet_align_pt1.setEnabled(
                changes["btn_sheet_align_pt1"].get("enabled", False)
            )
            if "checked" in changes["btn_sheet_align_pt1"]:
                self.btn_sheet_align_pt1.setChecked(
                    changes["btn_sheet_align_pt1"]["checked"]
                )
        if "btn_sheet_align_pt2" in changes:
            self.btn_sheet_align_pt2.setEnabled(
                changes["btn_sheet_align_pt2"].get("enabled", False)
            )
            if "checked" in changes["btn_sheet_align_pt2"]:
                self.btn_sheet_align_pt2.setChecked(
                    changes["btn_sheet_align_pt2"]["checked"]
                )
        if "btn_sheet_doalign" in changes:
            self.btn_sheet_doalign.setEnabled(
                changes["btn_sheet_doalign"].get("enabled", False)
            )
        set_mode.manual()
        self.lbl_align_data.setText(self.sheet_align_service.get_status_text())

    def on_sheet_align_pt1(self, checked):
        changes = self.sheet_align_service.handle_toggle("btn_sheet_align_pt1", checked)
        if "btn_sheet_align_pt2" in changes:
            self.btn_sheet_align_pt2.setEnabled(
                changes["btn_sheet_align_pt2"].get("enabled", False)
            )
            if "checked" in changes["btn_sheet_align_pt2"]:
                self.btn_sheet_align_pt2.setChecked(
                    changes["btn_sheet_align_pt2"]["checked"]
                )
        if "btn_sheet_doalign" in changes:
            self.btn_sheet_doalign.setEnabled(
                changes["btn_sheet_doalign"].get("enabled", False)
            )
        if checked:
            self.sheet_align_service.set_point_1(POS)
        set_mode.manual()
        self.lbl_align_data.setText(self.sheet_align_service.get_status_text())

    def on_sheet_align_pt2(self, checked):
        changes = self.sheet_align_service.handle_toggle("btn_sheet_align_pt2", checked)
        if "btn_sheet_doalign" in changes:
            self.btn_sheet_doalign.setEnabled(
                changes["btn_sheet_doalign"].get("enabled", False)
            )
        if checked:
            self.sheet_align_service.set_point_2(POS)
        set_mode.manual()
        self.lbl_align_data.setText(self.sheet_align_service.get_status_text())

    def on_sheet_align_doalign(self):
        changes = self.sheet_align_service.handle_toggle("btn_sheet_doalign", False)

        success = self.sheet_align_service.align(
            self.laser_offset_x.value(), self.laser_offset_y.value()
        )

        if not success:
            LOG.debug("Sheet alignment attempted but not all points set.")

        # Apply UI reset state
        for widget_name, state in changes.items():
            widget = getattr(self, widget_name)
            if "enabled" in state:
                widget.setEnabled(state["enabled"])
            if "checked" in state:
                widget.setChecked(state["checked"])

        self.lbl_align_data.setText(self.sheet_align_service.get_status_text())
