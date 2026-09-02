# Troubleshooting

This section covers common issues, error messages, and troubleshooting procedures for
MonoKrom Plasma.

## Qt / Runtime Issues

### Black Screen / OpenGL Issues

MonoKrom Plasma requires OpenGL and forces the OpenGL RHI backend. If you see a black screen:

1. **Verify OpenGL is available:**
   ```bash
   glxinfo | grep "OpenGL renderer"
   ```

2. **Check environment variables** — MonoKrom sets these automatically in `__init__.py`:
   ```bash
   export QT_API=pyside6
   export QSG_RHI_BACKEND=opengl
   ```

3. **If using PyQt5 alongside PySide6**, force PySide6:
   ```bash
   QT_API=pyside6 monokrom_plasma --ini <config>
   ```

### Qt Dependency Errors

If you encounter Qt dependency errors:

1. **Run the QtPyVCP installation script:**
    ```bash
    # Package installation:
    /usr/lib/python3/dist-packages/qtpyvcp/designer/install_script

    # Run in place:
    ~/linuxcnc-dev/lib/python/qtpyvcp/designer/install_script
    ```

2. **Verify PySide6 is installed:**
   ```bash
   python3 -c "import PySide6; print(PySide6.__version__)"
   ```

### Write Access to /tmp

MonoKrom requires write access to `/tmp`. Verify permissions:

```bash
ls -ld /tmp
# Expected: drwxrwxrwt  (others must have write)
```

If adjustment is needed:
```bash
sudo chmod o+rw /tmp
```

## HAL / LinuxCNC Issues

### VCP Fails to Connect to LinuxCNC

MonoKrom Plasma requires a running LinuxCNC instance. If the VCP fails to initialize:

1. **Ensure LinuxCNC is running:**
   ```bash
   linuxcnc ~/linuxcnc/configs/sim.monokrom/plasmac/plasmac_sim.ini
   ```

2. **Check HAL socket connectivity** — The VCP connects via HAL sockets. Verify the
   LinuxCNC instance is using the same config.

3. **Check for port conflicts** — Only one instance of the VCP can connect to a given
   LinuxCNC configuration.

### E-Stop Not Responding

If the E-Stop button doesn't work:

1. **Check hardware E-Stop** — Verify the physical E-Stop circuit is complete.
2. **Check `ESTOP_TYPE`** — In the INI file:
   ```ini
   [QTPLASMAC]
   ESTOP_TYPE = 0  # 0 = indicator only, 1 = software controllable
   ```
3. **Check HAL connections** — Verify `estop-out` is connected in the HAL files.

### Contact Bounce

Mechanical relays, switches, or external interference can cause inconsistent behavior on:
- Float switch
- Ohmic probe
- Breakaway switch
- Arc OK (Modes 1 & 2)

**Symptoms:**
- Probing triggers prematurely or not at all
- Arc OK flickers during cutting
- Float switch reports false triggers

**Solution — Add debounce in HAL:**

In `custom.hal`, add debounce components:

```hal
loadrt dbounce names=db_float,db_ohmic,db_breakaway,db_arcok
addf db_float servo-thread
addf db_ohmic servo-thread
addf db_breakaway servo-thread
addf db_arcok servo-thread

# Each increment = one servo thread cycle (1ms at 1MHz period)
setp db_float.delay 5      # 5ms debounce
setp db_ohmic.delay 5
setp db_breakaway.delay 5
setp db_arcok.delay 5

net float-switch => db_float.in
net ohmic-probe => db_ohmic.in
net breakaway => db_breakaway.in
net arc-ok => db_arcok.in
```

**Tuning:**
- Use Halscope to plot the input signal and observe bounce duration.
- Start with `delay = 5` (5ms at 1MHz servo period).
- Increase if bounce persists, decrease for faster response.

**Note:** Each increment of debounce delay adds approximately 0.001 mm (0.00004") to the
probed height result.

## Arc / Plasma Issues

### Arc Never Transfers

1. **Check pierce height** — Too high prevents arc transfer. Reduce pierce height.
2. **Check pierce delay** — Too short may not allow full penetration. Increase pierce delay.
3. **Check consumables** — Worn tip or nozzle prevents proper arc formation. Replace.
4. **Check gas pressure** — Verify gas supply and regulator settings.
5. **Check torch on signal** — Verify `plasmac.torch-on` is connected and active.
6. **Enable torch pulse** — Try adding a short torch pulse (0.1-0.3s) for difficult materials.

### Arc Lost During Cutting

1. **Check THC settings** — VAD threshold may be too sensitive. Adjust VAD threshold.
2. **Check for voids** — Material gaps or edges trigger void retraction. Enable/disable
   void sense as appropriate.
3. **Check arc OK signal** — Intermittent Arc OK causes arc loss detection. Add debounce
   (see Contact Bounce above).
4. **Check contact load** — Gold contacts need minimal current; other materials may need
   a parallel resistor (see QTPlasmac docs).

### Excessive Spatter

1. **Check cut height** — Too low causes consumable contact. Increase cut height.
2. **Check cut feed rate** — Too fast for material thickness. Reduce feed rate.
3. **Check consumables** — Worn or damaged consumables cause poor arc focus. Replace.
4. **Check gas type** — Wrong gas for material causes poor cut quality.

## Probing Issues

### Probe Never Triggers

1. **Ohmic probe enabled?** — Check **Ohmic Probe Enable** on Settings tab.
2. **Ohmic probe connected?** — Verify `plasmac.ohmic-probe` HAL pin is connected.
3. **Ohmic enable active?** — Verify `plasmac.ohmic-enable` output is wired.
4. **Float switch stuck?** — Check mechanical movement of float switch.
5. **Workpiece conductivity** — Paint, rust, or oxide layer may prevent ohmic detection.
   Clean the workpiece surface.

### Inconsistent Probe Results

1. **Run Probe Test** — Follow the calibration procedure in [Probe](probe.md).
2. **Check float travel** — Incorrect float travel causes height offset errors.
3. **Check debounce** — Too little debounce causes false triggers; too much causes delayed
   triggers.
4. **Check low-pass filter** — Arc voltage noise may interfere with ohmic probing. Enable
   low-pass filter if needed:
   ```hal
   setp plasmac.lowpass-frequency 100  # 100 Hz cutoff
   ```

## Process Database Issues

### No Materials Showing in Dropdown

1. **Check database exists** — Verify `plasma_table.db` exists in the config directory.
2. **Check database is populated** — Use sqlite3 to verify:
   ```bash
   sqlite3 plasma_table.db "SELECT COUNT(*) FROM cuts;"
   ```
3. **Seed the database** — If empty, import from `master-seed-source.csv`.

### Filters Not Matching

1. **Check filter field values** — Ensure filter selections match database entries exactly
   (case-sensitive).
2. **Check locked filters** — A locked filter may be preventing desired selections.
3. **Check database encoding** — Ensure no encoding issues in the CSV seed file.

## G-code / File Issues

### Program Won't Load

1. **Check file extension** — Only `.ngc`, `.nc`, and `.tap` files are accepted.
2. **Check file location** — Files must be in the configured NC Files directory.
3. **Check file format** — Verify the file contains valid G-code.
4. **Check filter configuration** — In the INI file:
   ```ini
   [FILTER]
   PROGRAM_EXTENSION = .ngc,.nc,.tap GCode File (*.ngc, *.nc, *.tap)
   ngc = plasma_gcode_preprocessor
   ```

### Backplot Not Displaying

1. **Check VTK configuration** — Verify the SPINDLE model is configured:
   ```ini
   [VTK]
   SPINDLE = jet_tracking_crosshair.stl
   ```
2. **Check file is loaded** — Backplot only shows after a file is loaded.
3. **Check OpenGL** — Black VTK window indicates OpenGL issues (see above).

## Error Messages

### Critical Errors

| Message | Cause | Action |
|---------|-------|--------|
| "Cannot connect to LinuxCNC" | LinuxCNC not running | Start LinuxCNC instance |
| "E-Stop active" | Hardware or software E-Stop | Release E-Stop, reset |
| "Probe failed" | Ohmic or float probe didn't trigger | Check connections, clean workpiece |
| "Arc fail timeout" | No arc transfer within timeout | Check pierce params, consumables |

### Warning Messages

| Message | Cause | Action |
|---------|-------|--------|
| "Arc OK intermittent" | Flickering arc OK signal | Check debounce, connections |
| "Void detected" | Torch over material gap | Reposition and resume |
| "THC threshold exceeded" | Voltage outside THC range | Check THC settings, cut params |
| "Consumable change active" | Offset applied for consumable wear | Replace consumables, deactivate |

## Getting Help

If issues persist:

1. **Check the log file** — Set `LOG_LEVEL = DEBUG` in the INI file and check `sim.log`.
2. **Use Halscope** — Plot relevant HAL signals to diagnose timing issues.
3. **Check the LinuxCNC forum** — The QtPyVCP section at [forum.linuxcnc.org/qtpyvcp](https://forum.linuxcnc.org/qtpyvcp/) has active discussions.
4. **Review the MonoKrom forum thread** — See acknowledgements in README for the original
   forum thread.
