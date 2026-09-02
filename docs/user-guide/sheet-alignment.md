# Sheet Alignment

Sheet Alignment performs two-point coordinate system rotation, allowing you to cut accurately
even when the workpiece is not perfectly aligned with the machine axes.

## Why Sheet Alignment?

When loading a sheet of material onto the cutting table, it is rarely perfectly aligned with
the machine axes. Sheet alignment measures the actual orientation of the workpiece and
rotates the coordinate system to match, ensuring cuts follow the material edges correctly.

## How It Works

The sheet alignment service uses a two-point method:

1. **Point 1** — The operator marks a known reference point on the workpiece (e.g., a corner
   or pre-drilled hole).
2. **Point 2** — The operator marks a second reference point along an edge or feature.
3. **Calculate** — MonoKrom computes the rotation angle between the two points using `atan2`.
4. **Apply** — A `G10 L2 P0 R<angle>` command rotates the coordinate system.

## Laser Pointer

Most MonoKrom installations include a laser pointer for marking reference points. The laser
is controlled from the WORK tab:

| Button | Function |
|--------|----------|
| **Laser Toggle** | Enable/disable the laser pointer |
| **Sheet Align** | Enter sheet alignment mode |

### Laser Offset

If the laser pointer is not perfectly centered on the torch tip, an X/Y offset must be
configured. The offset is automatically applied during sheet alignment and recovery operations.

**Setting the laser offset:**

1. Home the machine and set WCS zero at a known reference point.
2. Toggle the laser on and note where the laser dot appears.
3. Move the torch so the torch tip is exactly over the reference point.
4. The laser dot position relative to the torch tip is the laser offset.
5. Enter the offset values in the Settings tab under **Offsets → Laser X/Y**.

## Sheet Alignment Workflow

### Prerequisites

1. Machine is homed.
2. WCS zero is set at a known location on the workpiece (or at a convenient reference point).
3. Laser pointer is enabled and offset is configured (if applicable).

### Alignment Steps

1. **Enter alignment mode** — Click the **Sheet Align** button on the WORK tab.

2. **Set Point 1:**
   - Move the torch (using jog or program) so the laser dot is centered on the first
     reference point.
   - Click **Point 1** button to record the machine position.
   - The machine position is stored internally.

3. **Set Point 2:**
   - Move the torch so the laser dot is centered on the second reference point.
   - Click **Point 2** button to record the machine position.
   - The machine position is stored internally.

4. **Align:**
   - Click **Do Align** button.
   - MonoKrom calculates the rotation angle:
     ```
     angle = atan2(y2 - y1, x2 - x1) - atan2(y2_expected - y1_expected, x2_expected - x1_expected)
     ```
   - A `G10 L2 P0 R<angle>` command is sent to rotate the coordinate system.
   - The WORK tab indicates alignment is complete.

5. **Verify:**
   - Check that the WCS axes are now aligned with the workpiece edges.
   - Load and run your cutting program.

### Alignment State Machine

The sheet alignment service uses a state machine:

| State | Description | Active Buttons |
|-------|-------------|----------------|
| **IDLE** | No alignment in progress | Laser Toggle |
| **WAIT_POINT_1** | Waiting for operator to position Point 1 | Point 1 |
| **WAIT_POINT_2** | Waiting for operator to position Point 2 | Point 2 |
| **ALIGNING** | Calculating and applying rotation | Do Align |
| **ALIGNED** | Rotation applied, coordinate system updated | Laser Toggle |

## Laser Offset Compensation

When sheet alignment is active and a laser offset is configured, all operations that use
machine positions automatically compensate for the offset:

- **WCS zero** — Zero position accounts for laser offset when set via laser.
- **Sheet alignment** — Point positions are offset-corrected before angle calculation.
- **Cut recovery** — Recovery jog positions account for laser offset.
- **Consumable change** — Consumable change position accounts for laser offset.

## Cancelling Alignment

To cancel sheet alignment without applying rotation:

1. Click the **Sheet Align** button again to exit alignment mode.
2. The coordinate system returns to its previous state.
3. No `G10` command is sent.

## Manual Coordinate Rotation

If you know the rotation angle directly (e.g., from measurement), you can apply it via MDI:

```
G10 L2 P0 R<angle>
```

Where `<angle>` is in degrees (positive = counter-clockwise).

## Troubleshooting

| Problem | Possible Cause | Solution |
|---------|---------------|----------|
| Cuts are rotated after alignment | Point 1 or Point 2 not accurately placed | Re-align with more precise point placement |
| Laser dot doesn't match torch position | Laser offset not configured | Measure and enter laser offset in Settings |
| Alignment doesn't affect cuts | G10 not applied to correct work coordinate | Verify WCS number in G10 command |
| Alignment fails silently | Laser not enabled | Enable laser toggle before alignment |
