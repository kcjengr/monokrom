# THC (Thermal Height Control)

Thermal Height Control (THC) maintains the correct torch-to-workpiece distance during cutting
by monitoring arc voltage and adjusting the Z axis. This page explains how THC works, how to
tune it, and how to diagnose common problems.

For parameter definitions and default values, see [Settings → THC / ARC / PROBE & MARKING](settings.md).

---

## How THC Works

During cutting, the arc voltage changes as the torch height changes:

- **Torch too high** → Arc voltage increases (longer arc)
- **Torch too low** → Arc voltage decreases (shorter arc)

THC uses this relationship as a feedback loop:

```
Voltage Error = Measured Voltage - Target Voltage
Z Correction = f(P, I, D, Voltage Error)
```

The target voltage comes from the current cut process. The measured voltage comes from the
plasma power source via the arc voltage input. The PID controller combines three responses:

1. **Proportional** — reacts to the current error
2. **Integral** — reacts to accumulated past errors
3. **Derivative** — reacts to the rate of error change

---

## Enabling THC

THC is enabled via the **THC Enabled** checkbox in the **THC, Torch & Ohmic** panel on the
right side of the Settings page. When disabled, the Z axis remains at the configured cut
height regardless of arc voltage.

**When to disable THC:**

- Piercing (THC should be off during pierce)
- Cutting non-conductive materials
- Testing new cut parameters
- When arc voltage is unreliable or noisy

---

## PID Tuning

PID tuning is the most important skill for getting good THC performance. This section walks
through each gain and explains how to recognize correct and incorrect tuning.

### Understanding the Gains

| Gain | What it does | Analogy |
| --- | --- | --- |
| **P (Proportional)** | Reacts to the current voltage error. Larger error → larger Z movement. | Turning the steering wheel proportionally to how far off course you are. |
| **I (Integral)** | Accumulates small errors over time. Eliminates persistent drift. | Noticing you are consistently 10 cm to the left of center and gradually correcting. |
| **D (Derivative)** | Reacts to how fast the error is changing. Dampens sudden movements. | Feeling the car start to sway and easing off the steering before it gets bad. |

### Tuning P (Proportional)

P is the most important gain. Without P, the THC will not respond to voltage errors at all.

**How to tune:**

1. Set I and D to zero.
2. Start with P at zero.
3. Run a test cut and slowly increase P in steps of 0.5–1.0.
4. Watch the Z axis. When P is too low, the Z lags behind voltage changes — the torch cuts
   too deep on voltage drops and too high on voltage rises.
5. Continue increasing P until the Z axis tracks voltage changes closely.
6. Push P a bit further until you see slight oscillation (the Z wobbles up and down during
   the cut).
7. Reduce P by 20–30% from that oscillation point. This is your starting P value.

**What correct P looks like:**

- Z follows voltage changes smoothly
- No visible oscillation during steady cutting
- Corners and transitions are clean

**What too-little P looks like:**

- Cuts run too deep when voltage drops (e.g., at material joints)
- Cuts run too shallow when voltage rises
- The Z axis moves too slowly to keep up

**What too-much P looks like:**

- Z oscillates during cutting (visible up-and-down movement)
- Cut surface shows wavy pattern
- Excessive Z motor activity and noise

### Tuning I (Integral)

I is usually set to zero on plasma machines. It is only needed when you observe persistent
height drift during long cuts.

**How to tune:**

1. Start with P tuned and I at zero.
2. Run a long cut (10+ minutes) and watch the Z position relative to the cut surface.
3. If the torch gradually drifts closer to or farther from the material, increase I in small
   steps of 0.01.
4. Stop when the drift is eliminated.
5. If the Z starts to oscillate slowly, reduce I.

**What correct I looks like:**

- No height drift during extended cuts
- No slow oscillation

**What too-much I looks like:**

- Slow, rolling oscillation (period of several seconds)
- Z position drifts in one direction, reverses, drifts back — repeating cycle

**When I is not needed:**

- Short cuts (under 5 minutes)
- Machines with good voltage signal quality
- Machines with good mechanical Z axis response

### Tuning D (Derivative)

D is the least commonly used gain. It dampens rapid voltage changes that P alone cannot handle.

**How to tune:**

1. Start with P and I tuned and D at zero.
2. If P causes oscillation that cannot be reduced by backing off P, try increasing D in
   small steps of 0.005.
3. D should reduce oscillation without making the Z response sluggish.
4. Stop when oscillation is eliminated or reduced to an acceptable level.

**What correct D looks like:**

- Oscillation reduced without slowing response
- Sharp transitions (corners, material changes) are clean

**What too-much D looks like:**

- Z responds to electrical noise
- Small voltage spikes cause small Z movements
- Generally not recommended for plasma cutting unless the voltage signal is very noisy

### Tuning Summary

```
Start: P=0, I=0, D=0
  ↓
Increase P until Z tracks voltage, then add 20-30% → P tuned
  ↓
Run long cut. If drift observed, increase I in small steps → I tuned
  ↓
If P causes oscillation, try increasing D in small steps → D tuned (optional)
```

---

## THC Delay

THC Delay is the time between arc transfer confirmation and when THC begins making corrections.
This prevents the THC from reacting to pierce instability.

**Default:** 0.5 seconds

**Tuning:**

- **Too short** — The Z axis reacts to pierce voltage fluctuations, causing oscillation at cut start.
- **Too long** — The THC responds slowly to real height changes after the pierce stabilizes.

The delay is set in the **THC** panel on the Settings page.

---

## THC Threshold

THC Threshold defines the voltage variation window around the target voltage. Voltage
fluctuations within this window are ignored; the Z axis only moves when the voltage drifts
beyond it.

**Default:** 1.0 V

**Tuning:**

- **Too high** — The THC ignores real voltage changes and becomes sluggish.
- **Too low** — The THC reacts to electrical noise and causes unnecessary Z movement.

The threshold is set in the **THC** panel on the Settings page.

---

## VAD (Velocity Anti-Dive)

VAD prevents the torch from diving into the material when the arc voltage drops suddenly.
This can happen at the start of a cut, when crossing a weld seam, or when the arc briefly
interrupts.

### VAD Threshold

The percentage of the current cut feed rate the machine can slow to before locking the THC
to prevent torch dive. Higher values require a greater voltage change to trigger the dive
prevention.

**Default:** 60 %

**Tuning:** Set slightly above the expected idle/no-arc voltage, well below the cutting voltage.

### VAD Override

Controls the size of the change in cut voltage per second necessary to lock the THC and
prevent torch dive. Higher values require a greater voltage change rate to trigger.

**Default:** 100 %

---

## Void Sensing

Void sensing detects when the torch moves over a gap in the material — the edge of a cut
piece, a hole, or an uncut area. When a void is detected, the torch retracts to the safe
height to prevent damage.

### Enabling Void Sensing

Enable the **Void Anti Dive** checkbox in the **THC, Torch & Ohmic** panel on the right
side of the Settings page.

### How It Works

1. During cutting, the system monitors arc voltage.
2. If voltage drops below the THC threshold for a sustained period, a void is detected.
3. The torch retracts to safe height at the VAD override rate.
4. The operator must manually resume cutting.

### Troubleshooting False Voids

| Symptom | Cause | Solution |
| --- | --- | --- |
| Torch retracts on every corner | VAD threshold too low | Increase VAD threshold |
| Torch retracts on thin sections | VAD threshold too sensitive for material | Adjust VAD threshold per material |
| Torch doesn't retract on actual voids | Void anti-dive not enabled | Check **Void Anti Dive** in THC, Torch & Ohmic panel |

---

## Mesh Mode

Mesh mode is designed for cutting expanded metal (mesh). The mesh pattern causes rapid
voltage fluctuations that would confuse standard THC. In mesh mode, THC filters out these
rapid fluctuations and maintains a stable cutting height.

### Enabling Mesh Mode

Enable the **Mesh Sense** checkbox in the **THC, Torch & Ohmic** panel on the right side
of the Settings page.

### How It Works

Mesh mode applies additional low-pass filtering to the arc voltage signal, ignoring
fluctuations that occur faster than the mesh pattern frequency.

---

## Corner Lock

Corner lock holds the torch at pierce height briefly at each corner of a cut path. This
ensures clean corner cuts by allowing the material to fully melt through at the change of
direction.

Corner lock is controlled via the HAL pin `plasmac.corner-lock`. It is not a UI checkbox.

---

## Safe Height

Safe Height is a hard lower limit on Z during cutting. The THC will never command the torch
below this height, even if voltage readings suggest it should. This is a critical safety
feature that prevents crashes if THC malfunctions.

**Default:** 25

**Setting:** Set safe height slightly above the slat top (for slat-table machines) or a few
mm above the workpiece surface.

The safe height is set in the **THC** panel on the Settings page.

---

## Height Per Volt

Height Per Volt is the distance the Z axis must move to change arc voltage by one volt. It
is used for manual height manipulation and initial THC calibration.

**Default:** 0.100

**Setting procedure:**

1. Cut a test piece at a known height.
2. Measure the actual arc voltage with a multimeter.
3. Adjust Height Per Volt until the calculated height matches the actual height.

This setting is in the **ARC** panel on the Settings page.

---

## Arc Voltage Calibration

The **ARC** panel on the Settings page contains two settings that calibrate the arc voltage
reading:

**Voltage Scale** — A multiplier applied to the raw arc voltage input. If the displayed
voltage reads 10% high, reduce the scale by 10%.

**Voltage Offset** — A constant added to the raw voltage reading. Used to zero the reading
when there is no arc. If the displayed voltage reads 5 V when the torch is off, adjust the
offset.

These values are typically set once during initial setup and rarely changed.

---

## Arc OK Voltage Limits

In Mode 0 (soft arc OK), the system determines arc presence from voltage alone. Two settings
define the valid arc voltage window:

**OK High Volts** — Minimum voltage considered a valid arc. Below this, the system considers
the arc lost.

**OK Low Volts** — Maximum voltage below which the arc is considered lost. Above this, the
system considers the arc present.

Note: If the plasma power source provides a dedicated Arc OK signal, Mode 1 or 2 should be
used instead, and these settings are not applicable.

---

## THC State Indicators

The Settings page displays THC status via checkboxes in the **THC, Torch & Ohmic** panel:

| Indicator | What it means |
| --- | --- |
| **THC Enabled** | THC is actively controlling Z height |
| **THC Auto Volts** | Target voltage is being adjusted automatically |
| **THC (Velocity) Anti-Dive** | Anti-dive is active, preventing torch dive |
| **Void Anti Dive** | Void detection is monitoring for material gaps |
| **Ohmic Sense** | Ohmic probing is enabled for height detection |

---

## THC Troubleshooting

| Problem | Likely Cause | How to Fix |
| --- | --- | --- |
| Z oscillates during cut | P too high, or I too high | Reduce P by 20%, or reduce I to zero |
| Z drifts during long cuts | I too low, or P too low | Increase I in 0.01 steps, or increase P |
| Z lags behind voltage changes | P too low | Increase P |
| THC not responding | THC disabled | Enable **THC Enabled** checkbox |
| Z reacts to electrical noise | No low-pass filter, or D too high | Enable low-pass in HAL (see [Troubleshooting](../troubleshooting.md)), or reduce D |
| Torch crashes on void | VAD not enabled | Enable **Void Anti Dive** checkbox |
| Poor corner cuts | Corner lock disabled | Enable `plasmac.corner-lock` HAL pin |
| Slow THC response | Delay too long, or P too low | Reduce Delay, or increase P |
| THC reacts at cut start | Delay too short | Increase THC Delay |

---

## Tuning Decision Flow

Use this flowchart when troubleshooting THC performance:

```
Problem: Z oscillates
  ↓
Is it fast oscillation (period < 1s)?
  YES → Reduce P
  NO → Is it slow oscillation (period > 2s)?
    YES → Reduce I (or set to zero)
    NO → Check for mechanical issues (backlash, loose couplings)

Problem: Z drifts during cut
  ↓
Does it drift in one direction?
  YES → Increase I
  NO → Increase P

Problem: Torch cuts too deep at joints
  ↓
Increase P slightly

Problem: Torch crashes on void
  ↓
Enable Void Anti Dive. If still crashing, increase VAD Override.

Problem: THC reacts to electrical noise
  ↓
Reduce Threshold. If noise persists, enable low-pass filter in HAL.
```
