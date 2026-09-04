# Quickshape Reference

This reference documents all 14 Quickshape primitives in MonoKrom Plasma, including their
parameters, generated G-code structure, and special features.

## Shape Index

| Index | Shape | Key Parameters | Description |
|-------|-------|----------------|-------------|
| 0 | Circle | Diameter | Circle with lead-in |
| 1 | Rectangle | Width, Height | Rectangle with lead-in |
| 2 | Donut | Outer Diameter, Inner Diameter | Annulus with inner and outer cuts |
| 3 | Convex Rectangle | Width, Height, Corner Radius | Rectangle with one rounded corner |
| 4 | Lifting Lug | Width, Height, Hole Position, Lug Thickness | Lifting lug with hole, optional pair |
| 5 | U-Lug | Width, Height, Leg Width, Leg Length | U-shaped lug |
| 6 | Pipe Flange | Outer Diameter, Bolt Circle Diameter, Hole Count, Hole Diameter | Pipe flange with center hole and bolt holes |
| 7 | Pipe Saddle | Pipe Diameter, Pipe Width, Saddle Depth | Pipe saddle profile |
| 8 | Exhaust Flange | Width, Height, Slot Count, Slot Width | Exhaust flange with slot holes |
| 9 | N-Square Grid | Grid Spacing, Hole Count X, Hole Count Y, Hole Diameter | N-hole rectangle grid with optional center hole |
| 10 | L-Gusset | Width, Height, Leg Width, Thickness | L-shaped gusset |
| 11 | Angle Gusset | Width, Height, Leg Width, Thickness | Angle gusset with optional mirrored pair |
| 12 | Truss Support | Width, Height, Web Height | Truss support shape |
| 13 | Web Stiffener | Width, Height, Web Height | Web stiffener shape |

## Shape Details

### 0: Circle

Generates a circle with the specified diameter, including a lead-in move.

**Parameters:**
| Parameter | Unit | Description |
|-----------|------|-------------|
| Diameter | mm/in | Circle outer diameter |

**Generated G-code:**
```
G0 Z<pierce height>
G1 Z<pierce height> F<probe speed>
G0 Z<pierce height>
G4 P<pierce delay>
G1 Z<cut height> F<cut feed rate>
G4 P<pierce delay>
M3
G1 X<lead-in start> F<cut feed rate>  (lead-in)
G1 X<circle start> F<cut feed rate>
G3/X<circle end> I<J offset> F<cut feed rate>  (circle cut)
G1 X<lead-in end> F<cut feed rate>  (lead-out)
M5
G0 Z<safe height>
```

### 1: Rectangle

Generates a rectangle with the specified width and height, including lead-in.

**Parameters:**
| Parameter | Unit | Description |
|-----------|------|-------------|
| Width | mm/in | Rectangle width |
| Height | mm/in | Rectangle height |

**Generated G-code:**
```
G0 Z<pierce height>
G1 Z<pierce height> F<probe speed>
G0 Z<pierce height>
G4 P<pierce delay>
G1 Z<cut height> F<cut feed rate>
G4 P<pierce delay>
M3
G1 X<lead-in start> F<cut feed rate>  (lead-in)
G1 X<rect start> F<cut feed rate>
G1 X<width> F<cut feed rate>  (side 1)
G1 Y<height> F<cut feed rate>  (side 2)
G1 X-<width> F<cut feed rate>  (side 3)
G1 Y-<height> F<cut feed rate>  (side 4)
G1 X<lead-in end> F<cut feed rate>  (lead-out)
M5
G0 Z<safe height>
```

### 2: Donut

Generates an annulus (ring) with both outer and inner cuts.

**Parameters:**
| Parameter | Unit | Description |
|-----------|------|-------------|
| Outer Diameter | mm/in | Outer circle diameter |
| Inner Diameter | mm/in | Inner circle diameter (0 = no inner cut) |

**Features:**
- If Inner Diameter = 0, only the outer circle is cut.
- If Inner Diameter > 0, both outer and inner circles are cut (outer first, then inner).
- Smart hole detection: if Inner Diameter < hole detection threshold, the inner cut is
  skipped (treated as a through-cut feature).

### 3: Convex Rectangle

Generates a rectangle with one rounded corner.

**Parameters:**
| Parameter | Unit | Description |
|-----------|------|-------------|
| Width | mm/in | Rectangle width |
| Height | mm/in | Rectangle height |
| Corner Radius | mm/in | Radius of the rounded corner |

**Features:**
- The rounded corner is at the top-right of the rectangle.
- Corner radius must be less than half of the minimum dimension.

### 4: Lifting Lug

Generates a lifting lug with a hole for a lifting pin.

**Parameters:**
| Parameter | Unit | Description |
|-----------|------|-------------|
| Width | mm/in | Lug width |
| Height | mm/in | Lug height |
| Hole Position X | mm/in | X position of hole from left edge |
| Hole Position Y | mm/in | Y position of hole from bottom edge |
| Lug Thickness | mm/in | Optional second lug (0 = single lug) |

**Features:**
- If Lug Thickness > 0, generates a second lug mirrored at the specified offset.
- Hole is cut as a through-cut (no lead-in) if diameter < threshold.

### 5: U-Lug

Generates a U-shaped lug profile.

**Parameters:**
| Parameter | Unit | Description |
|-----------|------|-------------|
| Width | mm/in | Overall width |
| Height | mm/in | Overall height |
| Leg Width | mm/in | Width of each U leg |
| Leg Length | mm/in | Length of each U leg (from base) |

**Features:**
- Cut path traces the outer perimeter of the U-shape, then the inner perimeter.
- Smart hole detection applies to the inner cut if it qualifies.

### 6: Pipe Flange

Generates a pipe flange with a center hole and bolt holes around a bolt circle.

**Parameters:**
| Parameter | Unit | Description |
|-----------|------|-------------|
| Outer Diameter | mm/in | Flange outer diameter |
| Bolt Circle Diameter | mm/in | Diameter of bolt hole circle |
| Hole Count | int | Number of bolt holes |
| Hole Diameter | mm/in | Diameter of bolt holes |

**Features:**
- Center hole is cut first (if diameter > 0).
- Bolt holes are distributed evenly around the bolt circle.
- Bolt holes are cut as through-cuts (no lead-in) if diameter < threshold.

### 7: Pipe Saddle

Generates a pipe saddle profile for fitting a flat plate onto a cylindrical pipe.

**Parameters:**
| Parameter | Unit | Description |
|-----------|------|-------------|
| Pipe Diameter | mm/in | Outer diameter of the pipe |
| Pipe Width | mm/in | Width of contact area on pipe |
| Saddle Depth | mm/in | Depth of saddle cut (typically = pipe radius) |

**Features:**
- Generates a curved profile that matches the pipe surface.
- Uses arc moves to approximate the pipe curvature.

### 8: Exhaust Flange

Generates an exhaust flange with slot holes.

**Parameters:**
| Parameter | Unit | Description |
|-----------|------|-------------|
| Width | mm/in | Flange width |
| Height | mm/in | Flange height |
| Slot Count | int | Number of slot holes |
| Slot Width | mm/in | Width of each slot (length in Y direction) |

**Features:**
- Slots are distributed evenly across the flange.
- Each slot is cut as a through-cut (no lead-in) if width < threshold.

### 9: N-Square Grid

Generates a grid of holes in a rectangular pattern.

**Parameters:**
| Parameter | Unit | Description |
|-----------|------|-------------|
| Grid Spacing | mm/in | Center-to-center spacing between holes |
| Hole Count X | int | Number of holes in X direction |
| Hole Count Y | int | Number of holes in Y direction |
| Hole Diameter | mm/in | Diameter of each hole |

**Features:**
- Holes are arranged in a rectangular grid pattern.
- Optional center hole can be added (if center hole diameter > 0).
- All holes are cut as through-cuts (no lead-in) if diameter < threshold.

### 10: L-Gusset

Generates an L-shaped gusset (bracket).

**Parameters:**
| Parameter | Unit | Description |
|-----------|------|-------------|
| Width | mm/in | Overall width |
| Height | mm/in | Overall height |
| Leg Width | mm/in | Width of each leg |
| Thickness | mm/in | Plate thickness (for display only) |

**Features:**
- Cut path traces the outer perimeter of the L-shape.
- Inner corner is sharp (no radius).

### 11: Angle Gusset

Generates an angle gusset with an optional mirrored pair.

**Parameters:**
| Parameter | Unit | Description |
|-----------|------|-------------|
| Width | mm/in | Overall width |
| Height | mm/in | Overall height |
| Leg Width | mm/in | Width of each leg |
| Thickness | mm/in | Plate thickness (for display only) |

**Features:**
- If mirrored pair is enabled, generates a second gusset mirrored across the Y axis.
- Gap between gussets is configurable.

### 12: Truss Support

Generates a truss support shape.

**Parameters:**
| Parameter | Unit | Description |
|-----------|------|-------------|
| Width | mm/in | Overall width |
| Height | mm/in | Overall height |
| Web Height | mm/in | Height of the truss web (inner section) |

**Features:**
- Cut path traces the outer perimeter, then the inner web cutout.
- Web cutout is cut as a through-cut if dimensions < threshold.

### 13: Web Stiffener

Generates a web stiffener shape.

**Parameters:**
| Parameter | Unit | Description |
|-----------|------|-------------|
| Width | mm/in | Overall width |
| Height | mm/in | Overall height |
| Web Height | mm/in | Height of the web stiffener (inner section) |

**Features:**
- Similar to Truss Support but with different internal geometry.
- Cut path traces the outer perimeter, then the inner cutout.

## Common Features

All Quickshapes share these features:

### Kerf Compensation

All cut paths are offset by the current kerf value from the selected material. The kerf
value is stored in the process database and applied automatically.

### Smart Hole Detection

Internal features (holes, cutouts) that are smaller than the hole detection threshold are
cut as through-cuts without lead-ins. This improves cut quality for small features where
lead-ins would be unnecessary.

The threshold is set in the Settings tab under Plasma Cut Settings:
- `hole_detect` — Enable/disable hole detection
- `max_hole_size` — Maximum hole size for through-cut (mm)

### Lead-ins

External cuts (outer perimeters) use the configured lead-in type and length from the
material settings. Lead-in type and length are stored per material in the process database.

### Plasma Start/Stop Sequences

Each shape includes proper plasma start and stop sequences:
1. `G0 Z<pierce height>` — Rapid to pierce height
2. `G1 Z<pierce height> F<probe speed>` — Probe approach
3. Ohmic probe (if enabled)
4. `G4 P<pierce delay>` — Pierce delay
5. `G1 Z<cut height> F<cut feed rate>` — Lower to cut height
6. `M3` — Torch on
7. Cut path with lead-in
8. `M5` — Torch off
9. `G0 Z<safe height>` — Retract

### Material Selection

Quickshape parameters (kerf, lead-in, pierce height, cut height, feed rate) are applied
based on the currently selected material from the process database. Changing the material
in the preview window automatically updates all shape parameters.

## Limitations

- Quickshapes generate 2D profiles only (no 3D contours).
- Pipe Saddle geometry is an approximation (uses arc moves, not true cylindrical development).
- All shapes are cut in a single plane (Z = constant during cutting).
- No support for bevel cuts or multi-plane operations.

## See Also

- [Conversational (Quickshapes)](../user-guide/conversational.md) — User guide for using Quickshapes
- [Parameters](../user-guide/parameters.md) — Managing materials and cut parameters
- [G-Code Syntax](gcode-syntax.md) — G-code reference for Quickshape output
