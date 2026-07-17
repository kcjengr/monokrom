# Sheet Alignment Fix Plan

**File**: `src/monokrom/plasma/sheet_alignment.py`
**Priority**: Critical — affects coordinate system setup for all sheet alignment operations

---

## Critical Issues

### 1. Broken `_calculate_angle` Method (Mathematical Error)

**Problem**: The angle calculation logic is incorrect for all quadrants and edge cases. The `elif y_diff > 0: z_angle += 360` condition applies the wrong quadrant correction, and the `abs(x_diff) < abs(y_diff)` adjustment has no geometric basis.

**Current behavior** (broken):
- Q1 (x>0, y>0): Adds 180° to atan result
- Q2 (x<0, y>0): Adds 360° to atan result
- Q3 (x<0, y<0): No correction
- Horizontal/vertical lines: Returns wrong angles

**Fix**: Replace with standard `atan2` implementation that returns the correct angle for all quadrants:

```python
@staticmethod
def _calculate_angle(x_diff, y_diff):
    """Calculate rotation angle from two point differences using atan2.

    Args:
        x_diff: Difference in X coordinates (p2.x - p1.x).
        y_diff: Difference in Y coordinates (p2.y - p1.y).

    Returns:
        float: Rotation angle in degrees.
    """
    if x_diff == 0 and y_diff == 0:
        return 0
    return math.degrees(math.atan2(y_diff, x_diff))
```

**Verification matrix**:

| x_diff | y_diff | Expected atan2 | Old Result | New Result |
|--------|--------|----------------|------------|------------|
| 1, 1 | | 45° | 225° | 45° |
| -1, 1 | | 135° | 315° | 135° |
| -1, -1 | | -135° | 45° | -135° |
| 1, -1 | | -45° | 206.57° | -45° |
| 5, 0 | | 0° | 180° | 0° |
| -5, 0 | | 180° | 0° | 180° |
| 0, 5 | | 90° | 180° | 90° |
| 0, -5 | | -90° | 0° | -90° |

---

### 2. Missing Same-Point Validation in `align()`

**Problem**: If both reference points are at the same machine position, `x_diff` and `y_diff` will both be zero. The current code sends `G10 L2 P0 R0` which rotates 0°, effectively doing nothing. There's no user feedback that the alignment failed due to coincident points.

**Fix**: Add validation before angle calculation:

```python
def align(self, laser_offset_x_value, laser_offset_y_value):
    if self.sheet_align_p1 is None or self.sheet_align_p2 is None:
        return False

    # Validate points are not coincident
    x_diff = self.sheet_align_p2[0] - self.sheet_align_p1[0]
    y_diff = self.sheet_align_p2[1] - self.sheet_align_p1[1]
    if x_diff == 0 and y_diff == 0:
        return False  # Points must differ to define a valid rotation axis
```

---

## Minor Issues

### 3. Hardcoded Status Text in `get_status_text()`

**Problem**: Lines 50-51 hardcode `"REF1:..."` and `"REF2:..."` strings that never get replaced when points aren't set. This results in confusing display text.

**Fix**: Use actual values or indicate "not set" properly:

```python
def get_status_text(self):
    if self.sheet_align_p1 is None:
        ref1 = "REF1: not set"
    else:
        ref1 = f"REF1:\n{self.sheet_align_p1[0]:.4f},\n{self.sheet_align_p1[1]:.4f}"

    if self.sheet_align_p2 is None:
        ref2 = "REF2: not set"
    else:
        ref2 = f"REF2:\n{self.sheet_align_p2[0]:.4f},\n{self.sheet_align_p2[1]:.4f}"

    return f'{ref1}\n{ref2}'
```

---

### 4. `_handle_laser` Doesn't Track Alignment Mode State

**Problem**: The `_handle_laser` method only toggles UI button states without setting any internal state flag. There's no way to know if alignment mode is active from within the service.

**Fix**: Add an internal `_alignment_active` flag:

```python
def __init__(self, hal):
    self.hal = hal
    self.sheet_align_p1 = None
    self.sheet_align_p2 = None
    self._alignment_active = False

def _handle_laser(self, checked):
    if checked:
        self._alignment_active = True
        return {
            'btn_sheet_align_pt1': {'enabled': True},
        }
    self._alignment_active = False
    return {
        'btn_sheet_align_pt1': {'enabled': False, 'checked': False},
        'btn_sheet_align_pt2': {'enabled': False, 'checked': False},
        'btn_sheet_doalign': {'enabled': False},
    }
```

---

### 5. `align()` Sends Rotation After Laser Offset

**Problem**: The sequence sends `G10 L20 P0 X{...} Y{...}` (laser offset) followed by `G10 L2 P0 R{angle}` (rotation). Depending on CNC controller interpretation, the order may matter — rotation should typically be applied first, then offset.

**Fix**: Reorder the MDI commands:

```python
# Calculate rotation angle from two points
x_diff = self.sheet_align_p2[0] - self.sheet_align_p1[0]
y_diff = self.sheet_align_p2[1] - self.sheet_align_p1[1]
z_angle = self._calculate_angle(x_diff, y_diff)

# Reset coordinate system
self.hal.send_mdi('G10 L2 P0 R0')
self.hal.wait_complete()
self.hal.send_mdi('G10 L2 P0 X0 Y0')
self.hal.wait_complete()
self.hal.wait_complete()

# Apply rotation first, then laser offset
self.hal.send_mdi(f'G10 L2 P0 R{z_angle}')
self.hal.wait_complete()
self.hal.send_mdi(f'G10 L20 P0 X{laser_offset_x_value} Y{laser_offset_y_value}')
self.hal.wait_complete()
self.hal.send_mdi('G0 X0 Y0')
self.hal.wait_complete()
```

---

## Implementation Order

1. **Critical Issue 1** — Replace `_calculate_angle` with correct `atan2` implementation
2. **Critical Issue 2** — Add same-point validation in `align()`
3. **Minor Issue 4** — Reorder MDI commands in `align()` (may be controller-dependent)
4. **Minor Issue 3** — Fix hardcoded status text
5. **Minor Issue 5** — Add alignment mode state tracking

**Estimated effort**: 30-60 minutes (mostly mechanical changes to existing logic)

**Risk**: Low — all changes are contained within `sheet_alignment.py`. The `atan2` fix is a direct replacement with well-tested standard library behavior.
