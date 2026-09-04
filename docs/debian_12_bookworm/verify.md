# Verify Installation

Once the VCP has loaded, verify basic operation with the following steps:

1. **Home the machine** — Click the **HOME** button for each axis (X, Y, Z) on the Main Tab.

2. **Zero the axes** — Click the `0` button next to each DRO (digital readout) to set zero
   offsets. For Z, jog down to the minimum limit first, then touch off.

3. **Jog the axes** — Use the jog controls on the Main Tab to move the axes. Verify all
   axes respond correctly.

4. **Load a program** — Click the file browser icon or press `Ctrl+O` to load a G-code file
   from `~/linuxcnc/nc_files/`. The VTK backplot should display the toolpath.

5. **Select a material** — Click the material dropdown in the preview window to select a
   material from the process database.

6. **Probe test** — On the Probe tab, click **PROBE TEST**. The Z axis should probe down,
   find the material surface, and move up to the pierce height.

If all steps complete successfully, your MonoKrom Plasma installation is working correctly.
