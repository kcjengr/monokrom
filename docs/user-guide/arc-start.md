# Arc Start

Arc start controls how the torch ignites and transitions from pierce to cutting. This page
covers pierce height, pierce delay, cut height, and related settings.

## Arc Start Sequence

The standard arc start sequence in MonoKrom Plasma follows these steps:

```
1. Rapid to pierce height (G0 Z<pierce height>)
2. Approach to pierce height at probe speed (G1 Z<pierce height> F<probe speed>)
3. Ohmic probe / height sense (if enabled)
4. Rapid to pierce height (G0 Z<pierce height>)
5. Pierce delay (G4 P<pierce delay>)
6. Lower to cut height (G1 Z<cut height> F<cut feed rate>)
7. Pierce delay at cut height (G4 P<pierce delay>)
8. Torch on (M3)
9. Optional: Puddle jump
10. Begin cutting
```

## Pierce Height

The distance between the torch tip and the workpiece during the pierce operation.

**Setting:**

- Too high → Arc may not transfer, or pierce takes longer
- Too low → Spatter, consumable wear, risk of crash

**Note:** Pierce height depends on machine type, amperage, gas, and material. The values below
are examples for a Hypertherm 45 cutting mild steel. Actual values are stored in the process
database (see [Parameters](parameters.md)).

### Example: Hypertherm 45 — Mild Steel

| Thickness  | Pierce Height |
| ---------- | ------------- |
| ≤ 1 mm     | 1.5 mm        |
| 1.3–6.4 mm | 3.8 mm        |

### Example: Hypertherm 45 — Stainless Steel

| Thickness | Pierce Height |
| --------- | ------------- |
| ≤ 1 mm    | 1.5 mm        |
| 1.6–4 mm  | 2.0–3.8 mm    |
| > 4 mm    | 3.8 mm        |

### Example: Hypertherm 45 — Aluminum

| Thickness | Pierce Height |
| --------- | ------------- |
| All       | 3.8 mm        |

## Pierce Delay

The time (in seconds) the torch stays energized at pierce height before lowering to cut
height. This allows the material to fully melt through at the pierce point.

**Setting:**

- Too short → Incomplete pierce, arc lost when lowering to cut height
- Too long → Excessive kerf at pierce point, reduced consumable life

**Note:** Pierce height depends on machine type, amperage, gas, and material. The values below
are examples for a Hypertherm 45 cutting mild steel. Actual values are stored in the process
database (see [Parameters](parameters.md)).

### Example: Hypertherm 45 — Mild Steel

| Thickness | Pierce Delay (s) |
| --------- | ---------------- |
| All       | 0.5              |

### Example: Hypertherm 45 — Stainless Steel

| Thickness  | Pierce Delay (s) |
| ---------- | ---------------- |
| ≤ 1 mm     | 0.5              |
| 1.6–2.0 mm | 0.5              |
| 2.5–3.2 mm | 0.7              |
| 4.8 mm     | 1.0              |

### Example: Hypertherm 45 — Aluminum

| Thickness | Pierce Delay (s) |
| --------- | ---------------- |
| All       | 0.5              |

## Cut Height

The distance between the torch tip and the workpiece during the cutting operation. Cut height
is typically lower than pierce height for better cutting quality.

**Setting:**

- Too high → Wide kerf, poor cut quality, excessive dross
- Too low → Consumable contact, spatter, risk of crash

**Note:** Cut height depends on machine type, amperage, gas, and material. The values below
are examples for a Hypertherm 45 cutting mild steel. Actual values are stored in the process
database (see [Parameters](parameters.md)).

### Example: Hypertherm 45 — Mild Steel

| Thickness | Cut Height |
| --------- | ---------- |
| All       | 1.5 mm     |

### Example: Hypertherm 45 — Stainless Steel

| Thickness  | Cut Height |
| ---------- | ---------- |
| ≤ 1 mm     | 1.5 mm     |
| 1.6–3.2 mm | 1.5 mm     |
| 4.0–6.4 mm | 1.5 mm     |

### Example: Hypertherm 45 — Aluminum

| Thickness | Cut Height |
| --------- | ---------- |
| All       | 1.5 mm     |

## Cut Feed Rate

The speed at which the torch moves during cutting, in mm/min (or in/min). This value is
selected from the process database based on the current material filter settings.

**Setting factors:**

- Material thickness (thicker = slower)
- Material type (stainless cuts slower than mild steel)
- Gas type (oxygen enables faster cutting on mild steel)
- Plasma power source (higher amperage = faster cutting)

## Puddle Jump

A puddle jump retracts the torch to a higher height after pierce, holds briefly, then
lowers to cut height. This creates a "puddle" of molten metal that improves arc transfer
on certain materials.

### Puddle Jump Height

Height to which the torch retracts after pierce.

**Typical:** 2-4 mm above cut height

### Puddle Jump Delay

Delay (in seconds) at puddle jump height before lowering to cut height.

**Typical:** 0.2-0.5 seconds

### When to Use Puddle Jump

- Stainless steel (improves arc stability)
- Aluminum (helps break through oxide layer)
- Materials with poor arc transfer characteristics

### When NOT to Use Puddle Jump

- Mild steel with oxygen (not needed, may worsen cut quality)
- Thin materials (< 1 mm, may burn through)

## Arc Fail Timeout

Maximum time (in seconds) the system waits for arc transfer after the torch is energized.
If no Arc OK signal is detected within this time, the cut is aborted.

**Default:** 3.0 seconds

**Setting:**

- Too short → False arc failure on difficult materials
- Too long → Extended wait time before operator intervention

## Arc Max Starts

Maximum number of arc start attempts before the system gives up and reports an error.

**Default:** 3 attempts

**Setting:**

- Too low → Frustration on materials requiring multiple attempts
- Too high → Extended time on failed pierce attempts

## Arc Retry Delay

Delay (in seconds) between arc start retry attempts. Allows the plasma to cool between
attempts and gives the operator time to inspect the consumables.

**Default:** 5.0 seconds

## Arc OK Voltage Thresholds

For Mode 0 (soft arc OK), the system calculates arc presence from arc voltage. The following
thresholds define valid arc conditions:

| Threshold       | Default | Description                                        |
| --------------- | ------- | -------------------------------------------------- |
| **Arc OK High** | 250.0 V | Minimum voltage for valid arc OK                   |
| **Arc OK Low**  | 60.0 V  | Maximum voltage below which arc is considered lost |

**Hysteresis:** The difference between High and Low (20 V in this case) prevents rapid
on/off switching when voltage is near the threshold.

## Torch Pulse

Duration (in seconds) of the initial torch pulse at the start of each cut. The pulse helps
establish arc transfer on difficult materials by pre-heating the pierce point.

**Default:** 1.0 seconds

**When to use:**

- Stainless steel
- Aluminum
- Materials with oxide layers
- Cold plasma starts in cold weather

## Arc Start Troubleshooting

| Problem                            | Possible Cause                  | Solution                                                         |
| ---------------------------------- | ------------------------------- | ---------------------------------------------------------------- |
| Arc never transfers                | Pierce height too high          | Reduce pierce height                                             |
| Arc transfers but immediately lost | Pierce delay too short          | Increase pierce delay                                            |
| Excessive spatter at pierce        | Pierce height too low           | Increase pierce height                                           |
| Wide kerf at pierce point          | Pierce delay too long           | Reduce pierce delay                                              |
| Consumable contact during cut      | Cut height too low              | Increase cut height                                              |
| Arc fail timeout                   | Arc OK not connected (Mode 1/2) | Check HAL connections                                            |
| Multiple arc start attempts        | Poor arc transfer               | Enable torch pulse, check consumables                            |
| Inconsistent arc OK                | Contact bounce on Arc OK input  | Increase debounce (see [Troubleshooting](../troubleshooting.md)) |
