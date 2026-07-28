"""Tests for process_filter.py — verify the ProcessFilterService."""

import pytest
from unittest.mock import MagicMock, patch

from monokrom.plasma.process_filter import ProcessFilterService


class MockCutObject:
    """Mock cut data object with ORM-like attributes."""

    def __init__(self, name="Test Cut", cut_id=1, thickness=None, materialid=0,
                 tool_number=0, gas="Oxygen", machine="Test", material="Steel",
                 distance_system="mm", pressure_system="PSI", operation="Cut",
                 quality="Good", consumable="Torch",
                 pierce_height=5, pierce_delay=10, cut_height=20,
                 cut_speed=100, plunge_rate=50, volts=40,
                 kerf_width=2, puddle_height=5, puddle_delay=10,
                 amps=80, pause_at_end=0, pressure=30):
        self.name = name
        self.id = cut_id
        self.thickness = MagicMock()
        self.thickness.thickness = thickness if thickness is not None else 10.0
        self.materialid = materialid
        self.tool_number = tool_number
        self.gas = gas
        self.machine = machine
        self.material = material
        self.distance_system = distance_system
        self.pressure_system = pressure_system
        self.operation = operation
        self.quality = quality
        self.consumable = consumable
        # Param attributes matching param_fld_map
        self.pierce_height = pierce_height
        self.pierce_delay = pierce_delay
        self.cut_height = cut_height
        self.cut_speed = cut_speed
        self.plunge_rate = plunge_rate
        self.volts = volts
        self.kerf_width = kerf_width
        self.puddle_height = puddle_height
        self.puddle_delay = puddle_delay
        self.amps = amps
        self.pause_at_end = pause_at_end
        self.pressure = pressure


class MockHal:
    """Mock HALBridge for testing."""

    def __init__(self):
        self.pins = {}
        self.set_p_calls = []

    def get_value(self, pin_name):
        return self.pins.get(pin_name)

    def set_p(self, pin_name, value):
        self.pins[pin_name] = value
        self.set_p_calls.append((pin_name, value))


class MockWidget:
    """Mock Qt widget with common methods."""

    def __init__(self, text="", value=0, checked=False):
        self._text = text
        self._value = value
        self._checked = checked
        self._items = []
        self._current_index = 0
        self._visible = True

    def text(self):
        return self._text

    def setText(self, text):
        self._text = text

    def value(self):
        return self._value

    def setValue(self, value):
        self._value = value

    def isChecked(self):
        return self._checked

    def setChecked(self, checked):
        self._checked = checked

    def clear(self):
        self._items = []
        self._current_index = 0

    def addItem(self, item_or_text="", data=None):
        if hasattr(item_or_text, 'setData'):
            # item_or_text is a QListWidgetItem or similar
            item = item_or_text
            if data is not None:
                item.setData.return_value = data
        else:
            # Traditional text, data
            item = MagicMock()
            if data is not None:
                item.data.return_value = data
            item.text.return_value = item_or_text
        self._items.append(item)
        return item

    def currentData(self):
        return self._items[self._current_index].data() if self._items else None

    def setCurrentRow(self, row, model=None):
        self._current_index = row

    def row(self, item=None):
        """Return the row index of an item."""
        if item is None:
            return self._current_index
        for i, it in enumerate(self._items):
            if it is item:
                return i
        return -1

    def show(self):
        self._visible = True

    def hide(self):
        self._visible = False

    def isVisible(self):
        return self._visible

    def currentText(self):
        return self._text


class MockSender:
    """Mock for parent.sender() in param_update_from_filters."""

    def __init__(self, text=""):
        self._text = text

    def currentText(self):
        return self._text


class MockPlasmaPlugin:
    """Mock plasma plugin with required methods."""

    def __init__(self, cuts=None, tool_map=None, linear_systems=None,
                 thicknesses_list=None):
        self._cuts = cuts or []
        self._tool_map = tool_map or {}
        self._linear_systems = linear_systems or []
        self._thicknesses_list = thicknesses_list or []
        self.addCut_calls = []
        self.updateCut_calls = []

    def cut(self, arglist):
        return self._cuts

    def tool_id(self, tool_id):
        return self._tool_map.get(tool_id, [])

    def addCut(self, **kwargs):
        self.addCut_calls.append(kwargs)

    def updateCut(self, cut, **kwargs):
        self.updateCut_calls.append((cut, kwargs))

    def linearsystems(self):
        return self._linear_systems

    def thicknesses(self, linear_setting_id):
        return self._thicknesses_list

    # Additional filter data methods that load_ui_filter_data calls
    def gases(self):
        return []

    def machines(self):
        return []

    def materials(self):
        return []

    def operations(self):
        return []

    def qualities(self):
        return []

    def consumables(self):
        return []

    def pressuresystems(self):
        return []


class MockMainWindow:
    """Minimal mock of MainWindow for ProcessFilterService tests."""

    # Class-level field maps (mimic MainWindow class attributes)
    filter_fld_map = {
        'gases': 'filter_gas',
        'machines': 'filter_machine',
        'materials': 'filter_material',
        'thicknesses': 'filter_thickness',
        'linearsystems': 'filter_distance_system',
        'pressuresystems': 'filter_pressure_system',
        'operations': 'filter_operation',
        'qualities': 'filter_quality',
        'consumables': 'filter_consumable',
    }

    param_fld_map = {
        'name': 'param_name',
        'tool_number': 'param_process_id',
        'pierce_height': 'param_pierceheight',
        'pierce_delay': 'param_piercedelay',
        'cut_height': 'param_cutheight',
        'cut_speed': 'param_cutfeedrate',
        'plunge_rate': 'param_plungefeedrate',
        'volts': 'param_cutvolts',
        'kerf_width': 'param_kerfwidth',
        'puddle_height': 'param_puddlejumpheight',
        'puddle_delay': 'param_puddlejumpdelay',
        'amps': 'param_cutamps',
        'pause_at_end': 'param_pauseatend',
        'pressure': 'param_gaspressure',
    }

    def __init__(self):
        # State attributes
        self.last_tool_num_assigned = 0
        self._tool_number = 0
        self._material_thickness = 0
        self.filter_cutchart_id = None
        self._linear_setting_id = 0

        # Plasma plugin
        self._plasma_plugin = MockPlasmaPlugin()

        # HAL bridge
        self.hal = MockHal()

        # Filter widgets
        self.filter_gas = MockWidget()
        self.filter_machine = MockWidget()
        self.filter_material = MockWidget()
        self.filter_thickness = MockWidget()
        self.filter_distance_system = MockWidget()
        self.filter_pressure_system = MockWidget()
        self.filter_operation = MockWidget()
        self.filter_quality = MockWidget()
        self.filter_consumable = MockWidget()

        # Param widgets
        self.param_name = MockWidget()
        self.param_process_id = MockWidget()
        self.param_pierceheight = MockWidget()
        self.param_piercedelay = MockWidget()
        self.param_cutheight = MockWidget()
        self.param_cutfeedrate = MockWidget()
        self.param_plungefeedrate = MockWidget()
        self.param_cutvolts = MockWidget()
        self.param_kerfwidth = MockWidget()
        self.param_puddlejumpheight = MockWidget()
        self.param_puddlejumpdelay = MockWidget()
        self.param_cutamps = MockWidget()
        self.param_pauseatend = MockWidget()
        self.param_gaspressure = MockWidget()

        # Sub-list widgets
        self.grp_filter_sub_list = MockWidget()
        self.filter_sub_list = MockWidget()
        self.filter_sub_list.hide()

        # Labels
        self.lbl_process_name = MockWidget()

        # Sender mock
        self.sender = MagicMock(return_value=MockSender())


class TestProcessFilterServiceInit:
    """Tests for ProcessFilterService initialization."""

    def test_init_stores_parent(self):
        parent = MockMainWindow()
        service = ProcessFilterService(parent)
        assert service.parent is parent

    def test_init_stores_filter_fld_map(self):
        parent = MockMainWindow()
        service = ProcessFilterService(parent)
        assert service.filter_fld_map is parent.filter_fld_map

    def test_init_stores_param_fld_map(self):
        parent = MockMainWindow()
        service = ProcessFilterService(parent)
        assert service.param_fld_map is parent.param_fld_map

    def test_init_with_custom_parent(self):
        parent = MockMainWindow()
        service = ProcessFilterService(parent)
        assert service.parent.last_tool_num_assigned == 0


class TestProcessFilterLoadUiFilterData:
    """Tests for load_ui_filter_data."""

    def test_load_populates_filter_combos(self):
        parent = MockMainWindow()
        parent._plasma_plugin = MockPlasmaPlugin(
            cuts=[],
            thicknesses_list=[MockCutObject(name="10mm", thickness=10.0),
                              MockCutObject(name="20mm", thickness=20.0)]
        )
        service = ProcessFilterService(parent)

        service.load_ui_filter_data()

        # Check that filter_thickness was populated
        assert len(parent.filter_thickness._items) == 2
        assert parent.filter_thickness._items[0].text() == "10mm"
        assert parent.filter_thickness._items[1].text() == "20mm"

    def test_load_does_not_populate_other_filters(self):
        parent = MockMainWindow()
        parent._plasma_plugin = MockPlasmaPlugin(
            cuts=[],
            thicknesses_list=[MockCutObject(name="10mm", thickness=10.0)]
        )
        service = ProcessFilterService(parent)

        service.load_ui_filter_data()

        # Other filters should remain empty
        assert parent.filter_gas._items == []
        assert parent.filter_machine._items == []
        assert parent.filter_material._items == []

    def test_load_with_empty_plugin(self):
        parent = MockMainWindow()
        parent._plasma_plugin = MockPlasmaPlugin()
        service = ProcessFilterService(parent)

        service.load_ui_filter_data()

        # All filters should be cleared but empty
        for key, widget_name in parent.filter_fld_map.items():
            widget = getattr(parent, widget_name)
            assert widget._items == []

    def test_load_clears_existing_items(self):
        parent = MockMainWindow()
        parent._plasma_plugin = MockPlasmaPlugin(
            cuts=[],
            thicknesses_list=[MockCutObject(name="10mm", thickness=10.0)]
        )
        service = ProcessFilterService(parent)

        # Pre-populate filter with existing items
        parent.filter_thickness.addItem("Old Item", "old_id")
        assert len(parent.filter_thickness._items) == 1

        service.load_ui_filter_data()

        # Should be cleared and repopulated
        assert len(parent.filter_thickness._items) == 1
        assert parent.filter_thickness._items[0].text() == "10mm"


class TestProcessFilterGetFilterQuery:
    """Tests for get_filter_query."""

    def test_get_filter_query_returns_cuts(self):
        parent = MockMainWindow()
        parent._plasma_plugin = MockPlasmaPlugin(
            cuts=[MockCutObject(name="Cut 1", cut_id=1),
                  MockCutObject(name="Cut 2", cut_id=2)]
        )
        service = ProcessFilterService(parent)

        # Set filter values
        parent.filter_gas._items = [MagicMock()]
        parent.filter_gas._items[0].data.return_value = "Oxygen"
        parent.filter_machine._items = [MagicMock()]
        parent.filter_machine._items[0].data.return_value = "Test"
        parent.filter_material._items = [MagicMock()]
        parent.filter_material._items[0].data.return_value = "Steel"
        parent.filter_thickness._items = [MagicMock()]
        parent.filter_thickness._items[0].data.return_value = "10mm"

        result = service.get_filter_query()

        assert result is not None
        assert len(result) == 2

    def test_get_filter_query_returns_none_when_empty(self):
        parent = MockMainWindow()
        parent._plasma_plugin = MockPlasmaPlugin(
            cuts=[]
        )
        service = ProcessFilterService(parent)

        # Set filter values
        parent.filter_gas._items = [MagicMock()]
        parent.filter_gas._items[0].data.return_value = "Oxygen"

        result = service.get_filter_query()

        assert result is None

    def test_get_filter_query_passes_all_filter_data(self):
        parent = MockMainWindow()
        parent._plasma_plugin = MockPlasmaPlugin(
            cuts=[MockCutObject(name="Cut 1", cut_id=1)]
        )
        service = ProcessFilterService(parent)

        # Set all filter values
        parent.filter_gas._items = [MagicMock()]
        parent.filter_gas._items[0].data.return_value = "Oxygen"
        parent.filter_machine._items = [MagicMock()]
        parent.filter_machine._items[0].data.return_value = "Test"
        parent.filter_material._items = [MagicMock()]
        parent.filter_material._items[0].data.return_value = "Steel"
        parent.filter_thickness._items = [MagicMock()]
        parent.filter_thickness._items[0].data.return_value = "10mm"
        parent.filter_distance_system._items = [MagicMock()]
        parent.filter_distance_system._items[0].data.return_value = "mm"
        parent.filter_pressure_system._items = [MagicMock()]
        parent.filter_pressure_system._items[0].data.return_value = "PSI"
        parent.filter_operation._items = [MagicMock()]
        parent.filter_operation._items[0].data.return_value = "Cut"
        parent.filter_quality._items = [MagicMock()]
        parent.filter_quality._items[0].data.return_value = "Good"
        parent.filter_consumable._items = [MagicMock()]
        parent.filter_consumable._items[0].data.return_value = "Torch"

        result = service.get_filter_query()

        assert result is not None
        assert len(result) == 1

    def test_get_filter_query_with_empty_filters(self):
        parent = MockMainWindow()
        parent._plasma_plugin = MockPlasmaPlugin(
            cuts=[]
        )
        service = ProcessFilterService(parent)

        # Don't set any filter values (empty items)
        result = service.get_filter_query()

        # Plugin returns None when no cuts match
        assert result is None


class TestProcessFilterGetCurrentCut:
    """Tests for get_current_cut."""

    def test_get_current_cut_returns_cut(self):
        parent = MockMainWindow()
        parent._plasma_plugin = MockPlasmaPlugin(
            tool_map={1: [MockCutObject(name="Cut 1", cut_id=1)]}
        )
        service = ProcessFilterService(parent)

        # Set param_process_id to "1"
        parent.param_process_id._text = "1"

        result = service.get_current_cut()

        assert result is not None
        assert len(result) == 1
        assert result[0].name == "Cut 1"

    def test_get_current_cut_returns_none_when_tool_id_is_none(self):
        parent = MockMainWindow()
        parent._plasma_plugin = MockPlasmaPlugin(
            tool_map={}
        )
        service = ProcessFilterService(parent)

        # Set param_process_id to "NONE"
        parent.param_process_id._text = "NONE"

        result = service.get_current_cut()

        assert result is None

    def test_get_current_cut_returns_none_when_tool_not_found(self):
        parent = MockMainWindow()
        parent._plasma_plugin = MockPlasmaPlugin(
            tool_map={}
        )
        service = ProcessFilterService(parent)

        # Set param_process_id to "5"
        parent.param_process_id._text = "5"

        result = service.get_current_cut()

        assert result is None

    def test_get_current_cut_handles_uppercase(self):
        parent = MockMainWindow()
        parent._plasma_plugin = MockPlasmaPlugin(
            tool_map={1: [MockCutObject(name="Cut 1", cut_id=1)]}
        )
        service = ProcessFilterService(parent)

        # Set param_process_id to "1" (already uppercase)
        parent.param_process_id._text = "1"

        result = service.get_current_cut()

        assert result is not None

    def test_get_current_cut_with_invalid_tool_id_raises_value_error(self):
        parent = MockMainWindow()
        parent._plasma_plugin = MockPlasmaPlugin(
            tool_map={}
        )
        service = ProcessFilterService(parent)

        # Set param_process_id to "abc" (not a valid int)
        parent.param_process_id._text = "abc"

        # Should raise ValueError
        with pytest.raises(ValueError):
            service.get_current_cut()


class TestProcessFilterParamUpdateFromFilters:
    """Tests for param_update_from_filters."""

    def test_param_update_from_filters_happy_path(self):
        parent = MockMainWindow()
        parent._plasma_plugin = MockPlasmaPlugin(
            cuts=[MockCutObject(name="Cut 1", cut_id=1, thickness=10.0, materialid=5, tool_number=1)],
            tool_map={1: [MockCutObject(name="Cut 1", cut_id=1, thickness=10.0, materialid=5, tool_number=1)]}
        )
        service = ProcessFilterService(parent)

        # Set filter values
        parent.filter_gas._items = [MagicMock()]
        parent.filter_gas._items[0].data.return_value = "Oxygen"
        parent.filter_machine._items = [MagicMock()]
        parent.filter_machine._items[0].data.return_value = "Test"
        parent.filter_material._items = [MagicMock()]
        parent.filter_material._items[0].data.return_value = "Steel"
        parent.filter_thickness._items = [MagicMock()]
        parent.filter_thickness._items[0].data.return_value = "10mm"
        parent.filter_distance_system._items = [MagicMock()]
        parent.filter_distance_system._items[0].data.return_value = "mm"
        parent.filter_pressure_system._items = [MagicMock()]
        parent.filter_pressure_system._items[0].data.return_value = "PSI"
        parent.filter_operation._items = [MagicMock()]
        parent.filter_operation._items[0].data.return_value = "Cut"
        parent.filter_quality._items = [MagicMock()]
        parent.filter_quality._items[0].data.return_value = "Good"
        parent.filter_consumable._items = [MagicMock()]
        parent.filter_consumable._items[0].data.return_value = "Torch"

        # Set param widgets
        parent.param_name._text = "Cut 1"
        parent.param_process_id._text = ""
        parent.param_pierceheight._text = "5"
        parent.param_piercedelay._text = "10"
        parent.param_cutheight._text = "20"
        parent.param_cutfeedrate._text = "100"
        parent.param_plungefeedrate._text = "50"
        parent.param_cutvolts._text = "40"
        parent.param_kerfwidth._text = "2"
        parent.param_puddlejumpheight._text = "5"
        parent.param_puddlejumpdelay._text = "10"
        parent.param_cutamps._text = "80"
        parent.param_pauseatend._text = "0"
        parent.param_gaspressure._text = "30"

        service.param_update_from_filters()

        # Verify param widgets were updated
        assert parent.param_name._value == "Cut 1"
        assert parent.param_process_id._value == 1
        assert parent.param_pierceheight._value == 5
        assert parent.param_piercedelay._value == 10
        assert parent.param_cutheight._value == 20
        assert parent.param_cutfeedrate._value == 100
        assert parent.param_plungefeedrate._value == 50
        assert parent.param_cutvolts._value == 40
        assert parent.param_kerfwidth._value == 2
        assert parent.param_puddlejumpheight._value == 5
        assert parent.param_puddlejumpdelay._value == 10
        assert parent.param_cutamps._value == 80
        assert parent.param_pauseatend._value == 0
        assert parent.param_gaspressure._value == 30

    def test_param_update_from_filters_no_results(self):
        parent = MockMainWindow()
        parent._plasma_plugin = MockPlasmaPlugin(
            cuts=[]
        )
        service = ProcessFilterService(parent)

        # Set filter values
        parent.filter_gas._items = [MagicMock()]
        parent.filter_gas._items[0].data.return_value = "Oxygen"

        # Set param widgets
        parent.param_name._text = ""
        parent.param_process_id._text = ""
        parent.param_pierceheight._text = "5"
        parent.param_piercedelay._text = "10"
        parent.param_cutheight._text = "20"
        parent.param_cutfeedrate._text = "100"
        parent.param_plungefeedrate._text = "50"
        parent.param_cutvolts._text = "40"
        parent.param_kerfwidth._text = "2"
        parent.param_puddlejumpheight._text = "5"
        parent.param_puddlejumpdelay._text = "10"
        parent.param_cutamps._text = "80"
        parent.param_pauseatend._text = "0"
        parent.param_gaspressure._text = "30"

        service.param_update_from_filters(0)

        # Verify reset
        assert parent.param_name._text == "NONE"
        assert parent.param_process_id._text == "NONE"
        assert parent._tool_number == 0
        assert parent._material_thickness == 0
        assert parent.lbl_process_name._text == "NONE"

    def test_param_update_from_filters_single_result(self):
        parent = MockMainWindow()
        parent._plasma_plugin = MockPlasmaPlugin(
            cuts=[MockCutObject(name="Cut 1", cut_id=1, thickness=10.0, materialid=5)]
        )
        service = ProcessFilterService(parent)

        # Set filter values
        parent.filter_gas._items = [MagicMock()]
        parent.filter_gas._items[0].data.return_value = "Oxygen"
        parent.filter_machine._items = [MagicMock()]
        parent.filter_machine._items[0].data.return_value = "Test"
        parent.filter_material._items = [MagicMock()]
        parent.filter_material._items[0].data.return_value = "Steel"
        parent.filter_thickness._items = [MagicMock()]
        parent.filter_thickness._items[0].data.return_value = "10mm"
        parent.filter_distance_system._items = [MagicMock()]
        parent.filter_distance_system._items[0].data.return_value = "mm"
        parent.filter_pressure_system._items = [MagicMock()]
        parent.filter_pressure_system._items[0].data.return_value = "PSI"
        parent.filter_operation._items = [MagicMock()]
        parent.filter_operation._items[0].data.return_value = "Cut"
        parent.filter_quality._items = [MagicMock()]
        parent.filter_quality._items[0].data.return_value = "Good"
        parent.filter_consumable._items = [MagicMock()]
        parent.filter_consumable._items[0].data.return_value = "Torch"

        # Set param widgets
        parent.param_name._text = ""
        parent.param_process_id._text = ""
        parent.param_pierceheight._text = "5"
        parent.param_piercedelay._text = "10"
        parent.param_cutheight._text = "20"
        parent.param_cutfeedrate._text = "100"
        parent.param_plungefeedrate._text = "50"
        parent.param_cutvolts._text = "40"
        parent.param_kerfwidth._text = "2"
        parent.param_puddlejumpheight._text = "5"
        parent.param_puddlejumpdelay._text = "10"
        parent.param_cutamps._text = "80"
        parent.param_pauseatend._text = "0"
        parent.param_gaspressure._text = "30"

        service.param_update_from_filters(0)

        # Single result should not show sub-list
        assert parent.grp_filter_sub_list._visible is False

    def test_param_update_from_filters_multi_result(self):
        parent = MockMainWindow()
        parent._plasma_plugin = MockPlasmaPlugin(
            cuts=[
                MockCutObject(name="Cut 1", cut_id=1, thickness=10.0, materialid=5),
                MockCutObject(name="Cut 2", cut_id=2, thickness=20.0, materialid=10),
            ]
        )
        service = ProcessFilterService(parent)

        # Set filter values
        parent.filter_gas._items = [MagicMock()]
        parent.filter_gas._items[0].data.return_value = "Oxygen"
        parent.filter_machine._items = [MagicMock()]
        parent.filter_machine._items[0].data.return_value = "Test"
        parent.filter_material._items = [MagicMock()]
        parent.filter_material._items[0].data.return_value = "Steel"
        parent.filter_thickness._items = [MagicMock()]
        parent.filter_thickness._items[0].data.return_value = "10mm"
        parent.filter_distance_system._items = [MagicMock()]
        parent.filter_distance_system._items[0].data.return_value = "mm"
        parent.filter_pressure_system._items = [MagicMock()]
        parent.filter_pressure_system._items[0].data.return_value = "PSI"
        parent.filter_operation._items = [MagicMock()]
        parent.filter_operation._items[0].data.return_value = "Cut"
        parent.filter_quality._items = [MagicMock()]
        parent.filter_quality._items[0].data.return_value = "Good"
        parent.filter_consumable._items = [MagicMock()]
        parent.filter_consumable._items[0].data.return_value = "Torch"

        # Set param widgets
        parent.param_name._text = ""
        parent.param_process_id._text = ""
        parent.param_pierceheight._text = "5"
        parent.param_piercedelay._text = "10"
        parent.param_cutheight._text = "20"
        parent.param_cutfeedrate._text = "100"
        parent.param_plungefeedrate._text = "50"
        parent.param_cutvolts._text = "40"
        parent.param_kerfwidth._text = "2"
        parent.param_puddlejumpheight._text = "5"
        parent.param_puddlejumpdelay._text = "10"
        parent.param_cutamps._text = "80"
        parent.param_pauseatend._text = "0"
        parent.param_gaspressure._text = "30"

        service.param_update_from_filters(0)

        # Multi result should show sub-list
        assert parent.grp_filter_sub_list._visible is True
        assert len(parent.filter_sub_list._items) == 2

    def test_param_update_from_filters_highlighted_cut(self):
        parent = MockMainWindow()
        parent._plasma_plugin = MockPlasmaPlugin(
            cuts=[
                MockCutObject(name="Cut 1", cut_id=1, thickness=10.0, materialid=5),
                MockCutObject(name="Cut 2", cut_id=2, thickness=20.0, materialid=10),
            ]
        )
        parent.filter_cutchart_id = 2
        service = ProcessFilterService(parent)

        # Set filter values
        parent.filter_gas._items = [MagicMock()]
        parent.filter_gas._items[0].data.return_value = "Oxygen"
        parent.filter_machine._items = [MagicMock()]
        parent.filter_machine._items[0].data.return_value = "Test"
        parent.filter_material._items = [MagicMock()]
        parent.filter_material._items[0].data.return_value = "Steel"
        parent.filter_thickness._items = [MagicMock()]
        parent.filter_thickness._items[0].data.return_value = "10mm"
        parent.filter_distance_system._items = [MagicMock()]
        parent.filter_distance_system._items[0].data.return_value = "mm"
        parent.filter_pressure_system._items = [MagicMock()]
        parent.filter_pressure_system._items[0].data.return_value = "PSI"
        parent.filter_operation._items = [MagicMock()]
        parent.filter_operation._items[0].data.return_value = "Cut"
        parent.filter_quality._items = [MagicMock()]
        parent.filter_quality._items[0].data.return_value = "Good"
        parent.filter_consumable._items = [MagicMock()]
        parent.filter_consumable._items[0].data.return_value = "Torch"

        # Set param widgets
        parent.param_name._text = ""
        parent.param_process_id._text = ""
        parent.param_pierceheight._text = "5"
        parent.param_piercedelay._text = "10"
        parent.param_cutheight._text = "20"
        parent.param_cutfeedrate._text = "100"
        parent.param_plungefeedrate._text = "50"
        parent.param_cutvolts._text = "40"
        parent.param_kerfwidth._text = "2"
        parent.param_puddlejumpheight._text = "5"
        parent.param_puddlejumpdelay._text = "10"
        parent.param_cutamps._text = "80"
        parent.param_pauseatend._text = "0"
        parent.param_gaspressure._text = "30"

        service.param_update_from_filters(0)

        # Cut 2 should be highlighted (selected)
        assert parent.filter_sub_list._current_index == 1


class TestProcessFilterFilterSubListSelect:
    """Tests for filter_sub_list_select."""

    def test_filter_sub_list_select_finds_item(self):
        parent = MockMainWindow()
        parent._plasma_plugin = MockPlasmaPlugin(
            cuts=[
                MockCutObject(name="Cut 1", cut_id=1, thickness=10.0, materialid=5, tool_number=1),
                MockCutObject(name="Cut 2", cut_id=2, thickness=20.0, materialid=10, tool_number=2),
            ]
        )
        service = ProcessFilterService(parent)

        # Set filter values
        parent.filter_gas._items = [MagicMock()]
        parent.filter_gas._items[0].data.return_value = "Oxygen"
        parent.filter_machine._items = [MagicMock()]
        parent.filter_machine._items[0].data.return_value = "Test"
        parent.filter_material._items = [MagicMock()]
        parent.filter_material._items[0].data.return_value = "Steel"
        parent.filter_thickness._items = [MagicMock()]
        parent.filter_thickness._items[0].data.return_value = "10mm"
        parent.filter_distance_system._items = [MagicMock()]
        parent.filter_distance_system._items[0].data.return_value = "mm"
        parent.filter_pressure_system._items = [MagicMock()]
        parent.filter_pressure_system._items[0].data.return_value = "PSI"
        parent.filter_operation._items = [MagicMock()]
        parent.filter_operation._items[0].data.return_value = "Cut"
        parent.filter_quality._items = [MagicMock()]
        parent.filter_quality._items[0].data.return_value = "Good"
        parent.filter_consumable._items = [MagicMock()]
        parent.filter_consumable._items[0].data.return_value = "Torch"

        # Set param widgets
        parent.param_name._text = ""
        parent.param_process_id._text = ""
        parent.param_pierceheight._text = "5"
        parent.param_piercedelay._text = "10"
        parent.param_cutheight._text = "20"
        parent.param_cutfeedrate._text = "100"
        parent.param_plungefeedrate._text = "50"
        parent.param_cutvolts._text = "40"
        parent.param_kerfwidth._text = "2"
        parent.param_puddlejumpheight._text = "5"
        parent.param_puddlejumpdelay._text = "10"
        parent.param_cutamps._text = "80"
        parent.param_pauseatend._text = "0"
        parent.param_gaspressure._text = "30"

        # Create mock item with UserRole data
        item = MagicMock()
        item.data.return_value = 2  # cut_id=2

        service.filter_sub_list_select(item)

        # Verify Cut 2 was applied
        assert parent.param_name._value == "Cut 2"
        assert parent.param_process_id._value == 2
        assert parent._material_thickness == 20.0

    def test_filter_sub_list_select_item_not_found(self):
        parent = MockMainWindow()
        parent._plasma_plugin = MockPlasmaPlugin(
            cuts=[
                MockCutObject(name="Cut 1", cut_id=1, thickness=10.0, materialid=5),
            ]
        )
        service = ProcessFilterService(parent)

        # Set filter values
        parent.filter_gas._items = [MagicMock()]
        parent.filter_gas._items[0].data.return_value = "Oxygen"
        parent.filter_machine._items = [MagicMock()]
        parent.filter_machine._items[0].data.return_value = "Test"
        parent.filter_material._items = [MagicMock()]
        parent.filter_material._items[0].data.return_value = "Steel"
        parent.filter_thickness._items = [MagicMock()]
        parent.filter_thickness._items[0].data.return_value = "10mm"
        parent.filter_distance_system._items = [MagicMock()]
        parent.filter_distance_system._items[0].data.return_value = "mm"
        parent.filter_pressure_system._items = [MagicMock()]
        parent.filter_pressure_system._items[0].data.return_value = "PSI"
        parent.filter_operation._items = [MagicMock()]
        parent.filter_operation._items[0].data.return_value = "Cut"
        parent.filter_quality._items = [MagicMock()]
        parent.filter_quality._items[0].data.return_value = "Good"
        parent.filter_consumable._items = [MagicMock()]
        parent.filter_consumable._items[0].data.return_value = "Torch"

        # Set param widgets
        parent.param_name._text = ""
        parent.param_process_id._text = ""
        parent.param_pierceheight._text = "5"
        parent.param_piercedelay._text = "10"
        parent.param_cutheight._text = "20"
        parent.param_cutfeedrate._text = "100"
        parent.param_plungefeedrate._text = "50"
        parent.param_cutvolts._text = "40"
        parent.param_kerfwidth._text = "2"
        parent.param_puddlejumpheight._text = "5"
        parent.param_puddlejumpdelay._text = "10"
        parent.param_cutamps._text = "80"
        parent.param_pauseatend._text = "0"
        parent.param_gaspressure._text = "30"

        # Create mock item with UserRole data for non-existent cut
        item = MagicMock()
        item.data.return_value = 999  # non-existent cut_id

        service.filter_sub_list_select(item)

        # Should not update params since item not found
        assert parent.param_name._text == ""
        assert parent._tool_number == 0
        assert parent._material_thickness == 0


class TestProcessFilterAddNewCutProcess:
    """Tests for add_new_cut_process."""

    def test_add_new_cut_process_with_name(self):
        parent = MockMainWindow()
        parent._plasma_plugin = MockPlasmaPlugin()
        service = ProcessFilterService(parent)

        # Set filter values
        parent.filter_gas._items = [MagicMock()]
        parent.filter_gas._items[0].data.return_value = "Oxygen"
        parent.filter_machine._items = [MagicMock()]
        parent.filter_machine._items[0].data.return_value = "Test"
        parent.filter_material._items = [MagicMock()]
        parent.filter_material._items[0].data.return_value = "Steel"
        parent.filter_thickness._items = [MagicMock()]
        parent.filter_thickness._items[0].data.return_value = "10mm"
        parent.filter_distance_system._items = [MagicMock()]
        parent.filter_distance_system._items[0].data.return_value = "mm"
        parent.filter_pressure_system._items = [MagicMock()]
        parent.filter_pressure_system._items[0].data.return_value = "PSI"
        parent.filter_operation._items = [MagicMock()]
        parent.filter_operation._items[0].data.return_value = "Cut"
        parent.filter_quality._items = [MagicMock()]
        parent.filter_quality._items[0].data.return_value = "Good"
        parent.filter_consumable._items = [MagicMock()]
        parent.filter_consumable._items[0].data.return_value = "Torch"

        # Set param widgets
        parent.param_name._text = "New Cut"
        parent.param_process_id._text = ""
        parent.param_pierceheight._text = "5"
        parent.param_piercedelay._text = "10"
        parent.param_cutheight._text = "20"
        parent.param_cutfeedrate._text = "100"
        parent.param_plungefeedrate._text = "50"
        parent.param_cutvolts._text = "40"
        parent.param_kerfwidth._text = "2"
        parent.param_puddlejumpheight._text = "5"
        parent.param_puddlejumpdelay._text = "10"
        parent.param_cutamps._text = "80"
        parent.param_pauseatend._text = "0"
        parent.param_gaspressure._text = "30"

        service.add_new_cut_process(name="New Cut")

        # Verify addCut was called
        assert len(parent._plasma_plugin.addCut_calls) == 1
        assert parent._plasma_plugin.addCut_calls[0]['name'] == "New Cut"
        assert parent._plasma_plugin.addCut_calls[0]['tool_number'] == 1
        assert parent.last_tool_num_assigned == 1

    def test_add_new_cut_process_without_name(self):
        parent = MockMainWindow()
        parent._plasma_plugin = MockPlasmaPlugin()
        service = ProcessFilterService(parent)

        # Set filter values
        parent.filter_gas._items = [MagicMock()]
        parent.filter_gas._items[0].data.return_value = "Oxygen"
        parent.filter_machine._items = [MagicMock()]
        parent.filter_machine._items[0].data.return_value = "Test"
        parent.filter_material._items = [MagicMock()]
        parent.filter_material._items[0].data.return_value = "Steel"
        parent.filter_thickness._items = [MagicMock()]
        parent.filter_thickness._items[0].data.return_value = "10mm"
        parent.filter_distance_system._items = [MagicMock()]
        parent.filter_distance_system._items[0].data.return_value = "mm"
        parent.filter_pressure_system._items = [MagicMock()]
        parent.filter_pressure_system._items[0].data.return_value = "PSI"
        parent.filter_operation._items = [MagicMock()]
        parent.filter_operation._items[0].data.return_value = "Cut"
        parent.filter_quality._items = [MagicMock()]
        parent.filter_quality._items[0].data.return_value = "Good"
        parent.filter_consumable._items = [MagicMock()]
        parent.filter_consumable._items[0].data.return_value = "Torch"

        # Set param widgets
        parent.param_name._text = ""
        parent.param_process_id._text = ""
        parent.param_pierceheight._text = "5"
        parent.param_piercedelay._text = "10"
        parent.param_cutheight._text = "20"
        parent.param_cutfeedrate._text = "100"
        parent.param_plungefeedrate._text = "50"
        parent.param_cutvolts._text = "40"
        parent.param_kerfwidth._text = "2"
        parent.param_puddlejumpheight._text = "5"
        parent.param_puddlejumpdelay._text = "10"
        parent.param_cutamps._text = "80"
        parent.param_pauseatend._text = "0"
        parent.param_gaspressure._text = "30"

        service.add_new_cut_process(name=None)

        # Should not call addCut when name is None
        assert len(parent._plasma_plugin.addCut_calls) == 0

    def test_add_new_cut_process_increments_tool_number(self):
        parent = MockMainWindow()
        parent._plasma_plugin = MockPlasmaPlugin()
        service = ProcessFilterService(parent)

        # Set filter values
        parent.filter_gas._items = [MagicMock()]
        parent.filter_gas._items[0].data.return_value = "Oxygen"
        parent.filter_machine._items = [MagicMock()]
        parent.filter_machine._items[0].data.return_value = "Test"
        parent.filter_material._items = [MagicMock()]
        parent.filter_material._items[0].data.return_value = "Steel"
        parent.filter_thickness._items = [MagicMock()]
        parent.filter_thickness._items[0].data.return_value = "10mm"
        parent.filter_distance_system._items = [MagicMock()]
        parent.filter_distance_system._items[0].data.return_value = "mm"
        parent.filter_pressure_system._items = [MagicMock()]
        parent.filter_pressure_system._items[0].data.return_value = "PSI"
        parent.filter_operation._items = [MagicMock()]
        parent.filter_operation._items[0].data.return_value = "Cut"
        parent.filter_quality._items = [MagicMock()]
        parent.filter_quality._items[0].data.return_value = "Good"
        parent.filter_consumable._items = [MagicMock()]
        parent.filter_consumable._items[0].data.return_value = "Torch"

        # Set param widgets
        parent.param_name._text = "Cut 1"
        parent.param_process_id._text = ""
        parent.param_pierceheight._text = "5"
        parent.param_piercedelay._text = "10"
        parent.param_cutheight._text = "20"
        parent.param_cutfeedrate._text = "100"
        parent.param_plungefeedrate._text = "50"
        parent.param_cutvolts._text = "40"
        parent.param_kerfwidth._text = "2"
        parent.param_puddlejumpheight._text = "5"
        parent.param_puddlejumpdelay._text = "10"
        parent.param_cutamps._text = "80"
        parent.param_pauseatend._text = "0"
        parent.param_gaspressure._text = "30"

        service.add_new_cut_process(name="Cut 1")

        # Tool number should be incremented
        assert parent.last_tool_num_assigned == 1
        assert parent._plasma_plugin.addCut_calls[0]['tool_number'] == 1

        # Add another cut
        service.add_new_cut_process(name="Cut 2")

        assert parent.last_tool_num_assigned == 2
        assert parent._plasma_plugin.addCut_calls[1]['tool_number'] == 2


class TestProcessFilterUpdateCut:
    """Tests for update_cut."""

    def test_update_cut_finds_and_updates(self):
        parent = MockMainWindow()
        parent._plasma_plugin = MockPlasmaPlugin(
            tool_map={1: [MockCutObject(name="Cut 1", cut_id=1, thickness=10.0, materialid=5)]}
        )
        service = ProcessFilterService(parent)

        # Set param_process_id to "1"
        parent.param_process_id._text = "1"

        # Set param widgets
        parent.param_name._text = "Updated Cut"
        parent.param_name._value = "Updated Cut"
        parent.param_process_id._text = "1"
        parent.param_pierceheight._text = "10"
        parent.param_piercedelay._text = "15"
        parent.param_cutheight._text = "25"
        parent.param_cutfeedrate._text = "120"
        parent.param_plungefeedrate._text = "60"
        parent.param_cutvolts._text = "45"
        parent.param_kerfwidth._text = "3"
        parent.param_puddlejumpheight._text = "8"
        parent.param_puddlejumpdelay._text = "15"
        parent.param_cutamps._text = "90"
        parent.param_pauseatend._text = "5"
        parent.param_gaspressure._text = "35"

        service.update_cut()

        # Verify updateCut was called
        assert len(parent._plasma_plugin.updateCut_calls) == 1
        cut_obj, kwargs = parent._plasma_plugin.updateCut_calls[0]
        assert cut_obj[0].name == "Cut 1"
        assert kwargs['name'] == "Updated Cut"

    def test_update_cut_returns_early_when_no_current_cut(self):
        parent = MockMainWindow()
        parent._plasma_plugin = MockPlasmaPlugin(
            tool_map={}
        )
        service = ProcessFilterService(parent)

        # Set param_process_id to "NONE"
        parent.param_process_id._text = "NONE"

        service.update_cut()

        # Should not call updateCut
        assert len(parent._plasma_plugin.updateCut_calls) == 0

    def test_update_cut_with_invalid_tool_id_raises_value_error(self):
        parent = MockMainWindow()
        parent._plasma_plugin = MockPlasmaPlugin(
            tool_map={}
        )
        service = ProcessFilterService(parent)

        # Set param_process_id to "abc" (invalid)
        parent.param_process_id._text = "abc"

        # Should raise ValueError from get_current_cut
        with pytest.raises(ValueError):
            service.update_cut()
