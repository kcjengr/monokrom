# Statistics

The Statistics tab (on the right column, below the SUB-LIST) displays cut session metrics
and arc status indicators.

![Statistics Screenshot](../_static/screenshots/statistics.png)

## Cut Length

Displays the total length of material cut during the current session. This value accumulates
across all cuts in a single VCP session and resets when the VCP is restarted.

**Unit:** Millimeters (metric) or Inches (imperial), based on the INI file configuration.

## Cut Time

Displays the total time the torch was actively cutting during the current session. This
measures the duration from torch-on (M3) to torch-off (M5) across all cuts.

**Unit:** Seconds

## Arc OK Indicator

A visual indicator showing the current arc OK status:

| State | Color | Description |
|-------|-------|-------------|
| **Active** | Green | Cutting arc is established and stable |
| **Inactive** | Red/Gray | No arc detected (torch off, or arc lost) |
| **Flashing** | Yellow | Arc OK signal is intermittent (possible issue) |

## Session Information

The Statistics tab also displays:

| Field | Description |
|-------|-------------|
| **Session Start** | Time when the VCP was started |
| **Current Program** | Name of the currently loaded G-code file |
| **Total Cuts** | Number of completed cuts in the current session |
| **Machine State** | Current machine state (Idle, Running, Paused) |

## Resetting Statistics

Statistics reset automatically when the VCP is restarted. To reset during a session:

1. Stop the current program (ABORT).
2. The statistics will remain at their current values.
3. Start a new program — statistics continue accumulating.
4. Restart the VCP to reset all statistics to zero.
