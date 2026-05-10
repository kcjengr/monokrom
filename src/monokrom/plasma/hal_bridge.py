"""Thin HAL/LinuxCNC communication bridge for dependency injection."""


class HALBridge:
    """Wraps all LinuxCNC/HAL/MDI communication in a single injectable class.

    Production code passes real dependencies. Test code passes mocks.

    When no deps are injected, defaults are loaded lazily on first use so that
    importing this module never requires a running Qt/LinuxCNC instance.
    """

    def __init__(self, cnchal=None, issue_mdi_fn=None, cmd=None):
        # Use explicit None checks — {} and 0 would be falsy but are valid mocks
        self._cnchal = cnchal if cnchal is not None else _DefaultCnchal()
        self._issue_mdi = issue_mdi_fn if issue_mdi_fn is not None else _DefaultMdi()
        self._cmd = cmd if cmd is not None else _DefaultCmd()

    # -- HAL pin reads/writes ------------------------------------------------

    def get_value(self, pin_name: str):
        """Return the current value of a HAL pin."""
        return self._cnchal.get_value(pin_name)

    def set_p(self, pin_name: str, value):
        """Set a HAL pin to *value* (string or numeric)."""
        self._cnchal.set_p(pin_name, value)

    # -- MDI commands --------------------------------------------------------

    def send_mdi(self, gcode: str):
        """Queue an MDI command for LinuxCNC."""
        self._issue_mdi(gcode)

    def wait_complete(self):
        """Block until the last LinuxCNC command finishes."""
        self._cmd.wait_complete()

    # -- Convenience helpers -------------------------------------------------

    def set_offset(self, axis: str, value: float | int):
        """Set an axis virtual offset (eoffset)."""
        self.set_p(f'axis.{axis}.eoffset', str(value))

    def get_eoffset(self, axis: str):
        """Get the current eoffset for an axis."""
        return self.get_value(f'axis.{axis}.eoffset')

    def set_offsets(self, x: float | int = 0, y: float | int = 0):
        """Reset X/Y virtual offsets (common pattern in recovery/consumable)."""
        self.set_p('plasmac.x-offset', f'{x:.0f}')
        self.set_p('plasmac.y-offset', f'{y:.0f}')


# -- Lazy default factories --------------------------------------------------

class _DefaultCnchal:
    """Lazily imports linuxcnc hal module on first use."""
    def __init__(self):
        self._module = None

    def _ensure(self):
        if self._module is None:
            import hal
            self._module = hal
        return self._module

    def get_value(self, pin_name: str):
        return self._ensure().get_value(pin_name)

    def set_p(self, pin_name: str, value):
        self._ensure().set_p(pin_name, value)


class _DefaultMdi:
    """Lazily imports qtpyvcp issue_mdi on first use."""
    def __init__(self):
        self._fn = None

    def _ensure(self):
        if self._fn is None:
            from qtpyvcp.actions.machine_actions import issue_mdi
            self._fn = issue_mdi
        return self._fn

    def __call__(self, gcode: str):
        self._ensure()(gcode)


class _DefaultCmd:
    """Lazily creates linuxcnc.command() on first use."""
    def __init__(self):
        self._cmd = None

    def _ensure(self):
        if self._cmd is None:
            import linuxcnc
            self._cmd = linuxcnc.command()
        return self._cmd

    def wait_complete(self):
        self._ensure().wait_complete()
