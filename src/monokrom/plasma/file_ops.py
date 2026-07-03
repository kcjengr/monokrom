"""File operations service for plasma main window."""

import os


class FileOpsService:
    """Handles G-code file loading, saving, and reloading operations."""

    def __init__(self, parent, load_program_fn=None, ngc_loc=None):
        self.parent = parent
        self._load_program_fn = load_program_fn
        self._ngc_loc = ngc_loc

    def _get_load_program(self):
        """Lazy-load the loadProgram function to avoid QtPyVCP import without runtime."""
        if self._load_program_fn is not None:
            return self._load_program_fn
        from qtpyvcp.actions.program_actions import load as loadProgram
        return loadProgram

    def open_latest(self):
        """Opens the latest file by date/time in the default ngc location."""
        if self._ngc_loc is not None:
            search_dir = os.path.expanduser(self._ngc_loc)
        else:
            from . import mainwindow as mw
            search_dir = os.path.expanduser(mw.NGC_LOC)
        newest = None
        with os.scandir(search_dir) as it:
            for entry in it:
                if not entry.name.startswith('.') and entry.is_file():
                    file_stat = entry.stat()
                    if newest is None:
                        newest = (entry.path, file_stat.st_mtime)
                    elif newest[1] < file_stat.st_mtime:
                        newest = (entry.path, file_stat.st_mtime)
        if newest is not None:
            self.parent.latest_real_file = newest[0]
            self.parent.reset_vtk_btns()
            self._get_load_program()(newest[0])

    def save_file(self):
        """Saves the current G-code editor content and reloads it."""
        real_file = self.parent.latest_real_file
        if real_file is None:
            return

        name_parts = real_file.rsplit(".", 1)
        if name_parts[0].endswith("_parsed"):
            ppart = "."
        else:
            ppart = "_parsed."
        new_name = name_parts[0] + ppart + name_parts[1]

        self.parent.gcode_editor.saveFile(new_name)
        self._get_load_program()(new_name)
        self.parent.reset_vtk_btns()

    def reload_file(self):
        """Reloads the most recently loaded G-code file."""
        real_file = self.parent.latest_real_file
        if real_file is None or real_file == "":
            return
        self._get_load_program()(real_file)
        self.parent.reset_vtk_btns()
