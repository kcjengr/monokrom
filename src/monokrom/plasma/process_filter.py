"""Process filter data management service for plasma main window."""
# Import these at module level (used by param_update_from_filters and filter_sub_list_select)
from qtpy.QtCore import QItemSelectionModel, Qt
from qtpy.QtWidgets import QLabel, QListWidgetItem

import logging
LOG = logging.getLogger('qtpyvcp.plasma.process_filter')


class ProcessFilterService:
    """Manages cut process filtering, parameter updates, and database operations.

    Handles loading filter data into UI combos, querying cuts based on filters,
    updating param fields from selected cuts, and adding/updating cut processes.
    """

    def __init__(self, parent):
        self.parent = parent
        # Store references to field maps via the parent class (avoids circular import)
        self.filter_fld_map = type(parent).filter_fld_map
        self.param_fld_map = type(parent).param_fld_map

    # -- Public API -----------------------------------------------------------

    def load_ui_filter_data(self):
        """Build up the starting position data for process filters in the UI."""
        parent = self.parent
        for k in self.filter_fld_map:
            if k == 'thicknesses':
                setattr(parent, '_' + k,
                        getattr(parent._plasma_plugin, k)(parent._linear_setting_id))
            else:
                setattr(parent, '_' + k,
                        getattr(parent._plasma_plugin, k)())
            ui_fld = getattr(parent, self.filter_fld_map[k])
            ui_fld.clear()
            for data in getattr(parent, '_' + k):
                ui_fld.addItem(data.name, data.id)

    def get_filter_query(self):
        """Build arglist from UI filters and query the plasma plugin."""
        parent = self.parent
        arglist = []
        for v in self.filter_fld_map.values():
            uifld = getattr(parent, v)
            arglist.append(uifld.currentData())
        cutlist = parent._plasma_plugin.cut(arglist)
        if len(cutlist) > 0:
            return cutlist
        return None

    def get_current_cut(self):
        """Get current cut by tool_id from the plasma plugin."""
        parent = self.parent
        tool_id = parent.param_process_id.text().upper()
        if tool_id == 'NONE':
            return None
        tool_id = int(tool_id)
        cutlist = parent._plasma_plugin.tool_id(tool_id)
        if len(cutlist) > 0:
            return cutlist
        return None

    def param_update_from_filters(self, index=0):
        """Update param fields from filter query results."""
        from qtpy.QtCore import Qt
        from qtpy.QtWidgets import QListWidgetItem

        parent = self.parent
        sender = parent.sender()
        if hasattr(sender, 'currentText'):
            LOG.debug(f"Update params '{index}' '{sender.currentText()}'")
        else:
            LOG.debug('Update params.')

        data = self.get_filter_query()
        if data is not None:
            select_row = 0
            if len(data) > 1:
                parent.grp_filter_sub_list.show()
                parent.filter_sub_list.clear()
                for nm in data:
                    item = QListWidgetItem(nm.name)
                    item.setData(Qt.UserRole, nm.id)
                    parent.filter_sub_list.addItem(item)
                    if nm.id == parent.filter_cutchart_id:
                        select_row = parent.filter_sub_list.row(item)
                    parent.filter_sub_list.setCurrentRow(
                        select_row, QItemSelectionModel.ClearAndSelect)
            else:
                parent.grp_filter_sub_list.hide()

            data = data[select_row]
            for k in self.param_fld_map:
                fld_data = getattr(data, k)
                ui_fld = getattr(parent, self.param_fld_map[k])
                if isinstance(ui_fld, QLabel):
                    ui_fld.setText(str(fld_data))
                    if k == 'tool_number':
                        parent._tool_number = int(fld_data)
                else:
                    ui_fld.setValue(fld_data)
                    if hasattr(ui_fld, "forceUpdatePinValue"):
                        ui_fld.forceUpdatePinValue()
            LOG.debug(f"param_update_from_filters: Thickness = {data.thickness.thickness}")
            LOG.debug(f"param_update_from_filters: MaterialID = {data.materialid}")
            parent.hal.set_p("qtpyvcp.material-id", f"{data.materialid}")

            parent._material_thickness = data.thickness.thickness
        else:
            parent.grp_filter_sub_list.hide()
            ui_fld = getattr(parent, 'param_name')
            ui_fld.setText('NONE')
            ui_fld = getattr(parent, 'param_process_id')
            ui_fld.setText('NONE')
            parent._tool_number = 0
            parent._material_thickness = 0
            for v in self.param_fld_map.values():
                if v not in ('param_name', 'param_process_id'):
                    ui_fld = getattr(parent, v)
                    ui_fld.setValue(0)
        LOG.debug(f"param_update_from_filters: Tool Number = {parent._tool_number}")
        ui_fld = getattr(parent, 'param_name')
        parent.lbl_process_name.setText(ui_fld.text())

    def filter_sub_list_select(self, item):
        """Handle sub-list selection to update param fields."""
        from qtpy.QtCore import Qt

        parent = self.parent
        data = self.get_filter_query()
        item_id = item.data(Qt.UserRole)
        for d in data:
            if d.id == item_id:
                for k in self.param_fld_map:
                    fld_data = getattr(d, k)
                    ui_fld = getattr(parent, self.param_fld_map[k])
                    if isinstance(ui_fld, QLabel):
                        ui_fld.setText(str(fld_data))
                        if k == 'tool_number':
                            parent._tool_number = int(fld_data)
                    else:
                        ui_fld.setValue(fld_data)
                LOG.debug(f"filter_sub_list_select: Thickness = {d.thickness.thickness}")
                parent._material_thickness = d.thickness.thickness

    def add_new_cut_process(self, name=None):
        """Add a new cut process to the database and refresh UI."""
        parent = self.parent
        if name is None:
            LOG.debug('No name set for cut process Add. Do nothing.')
            return

        arglist = {}
        for k in self.filter_fld_map:
            uifld = getattr(parent, self.filter_fld_map[k])
            arglist[k] = uifld.currentData()
        for k in self.param_fld_map:
            uifld = getattr(parent, self.param_fld_map[k])
            if hasattr(uifld, 'value'):
                arglist[k] = uifld.value()
            else:
                arglist[k] = uifld.text()
        arglist['name'] = name
        parent.last_tool_num_assigned += 1
        arglist['tool_number'] = parent.last_tool_num_assigned
        parent._plasma_plugin.addCut(**arglist)
        self.param_update_from_filters()

    def update_cut(self):
        """Update an existing cut process based on param_process_id."""
        parent = self.parent
        q = self.get_current_cut()

        if q is None:
            LOG.warning("No current cut content found. No action taken.")
            return

        arglst = {}
        for k in self.param_fld_map:
            ui_fld = getattr(parent, self.param_fld_map[k])
            if isinstance(ui_fld, QLabel):
                arglst[k] = ui_fld.text()
            else:
                arglst[k] = ui_fld.value()

        parent._plasma_plugin.updateCut(q, **arglst)
