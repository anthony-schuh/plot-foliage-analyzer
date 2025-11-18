# Plot Foliage Analyzer

Interactive OpenCV tool for rectifying plot images and quantifying **green vegetation (carrot foliage)** with per-image corner selection, orientation tools, **live HSV threshold tuning**, and **exclusion masking** (brush + rectangle).

---

## Table of Contents
- [What this does](#what-this-does)
- [Features](#features)
- [Installation](#installation)
- [Quick start](#quick-start)
  - [GUI wrapper](#gui-wrapper)
  - [Command line](#command-line)
- [Workflow overview](#workflow-overview)
- [Keyboard & mouse controls](#keyboard--mouse-controls)
  - [Phase 1: Corner selection](#phase-1-corner-selection)
  - [Phase 2: HSV tuner + exclusions](#phase-2-hsv-tuner--exclusions)
- [Command-line options](#command-line-options)
- [Outputs](#outputs)
- [How thresholds & exclusions persist](#how-thresholds--exclusions-persist)
- [Tips & best practices](#tips--best-practices)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [License](#license)

---

## What this does
For each photo of a research plot:
1. **Click 4 plot corners**.
2. **Rectify** the image (perspective-correct top-down view).
3. Optionally **tune green detection** with HSV sliders.
4. **Exclude** non-foliage areas by painting or drawing rectangles.
5. Output the rectified image, mask, overlay, and **% green** to a CSV.

---

## Features
- **EXIF-aware loading** — handles camera rotation metadata.
- **Orientation tools** — rotate/flip before corner selection.
- **Robust window creation** — avoids NULL window errors.
- **Per-image corner selection** — frames vary; pick each time.
- **Perspective rectification** — standardized top-down view.
- **Live HSV tuner** — adjust H/S/V min/max interactively.
- **Exclusion tools** — brush (paint/erase) and **Shift+drag rectangles**.
- **Persistence** — remembers last thresholds; saves per-image exclusion masks.
- **Resume capability** — interrupt and resume batch processing anytime.
- **Progress tracking** — automatically saves progress after each image.
- **Normalization** — optional portrait/landscape for outputs.

---

## Installation
Python 3.8+ recommended.

```bash
pip install opencv-python numpy pillow
```

**Linux GUI note:** On Wayland/GNOME, forcing XCB is often most reliable:

```bash
export QT_QPA_PLATFORM=xcb
```

If you’re SSH’ing, use a local desktop session or enable X forwarding with `ssh -X` (GUI required).

---

## Quick start

### GUI wrapper
**Easiest option:** Use the graphical interface to configure and run the analyzer.

```bash
./run_gui.sh
```

Or directly:
```bash
python3 plot_analyzer_gui.py
```

The GUI lets you browse for folders, set options, and launch the analysis tool. See [GUI_README.md](GUI_README.md) for details.

### Command line

```bash
QT_QPA_PLATFORM=xcb python src/plots_green.py   --input field_imaging/Canopy_wk4/   --output field_imaging/output/   --normalize landscape   --tune
```

- Window opens for each image.
- Rotate/flip if needed → click 4 corners → **Enter**.
- **HSV Tuner** opens: adjust sliders, paint/rect exclusions → **Enter**.
- Press **q** to quit anytime; use `--resume` to continue later.

---

## Workflow overview
1. **Load** image (EXIF orientation applied).
2. **Phase 1: Corner selection**
   - Rotate/flip for a comfortable view.
   - Click exactly 4 corners of the plot.
3. **Rectify** to top-down, cropped image.
4. **Normalize** orientation (optional).
5. **Phase 2: HSV tuner** (if `--tune`)
   - Adjust sliders until green mask looks right.
   - Exclude non-plot/artefacts with brush or rectangles.
   - Press **Enter** to accept.
6. **Save** results (images, masks, overlay, CSV, JSON).

---

## Keyboard & mouse controls

### Phase 1: Corner selection
**Goal:** Orient image, pick 4 plot corners.

**Mouse**
- **Left-click**: add a corner point (max 4).

**Keyboard**
| Key  | Action                              |
|------|-------------------------------------|
| a    | Rotate 90° counter-clockwise        |
| d    | Rotate 90° clockwise                |
| h    | Flip horizontally                   |
| v    | Flip vertically                     |
| u    | Undo last point                      |
| r    | Reset all points                     |
| s    | Skip this image                      |
| Enter| Accept (only when 4 points selected) |
| q/Esc| Quit program                         |

> Tip: Click corners roughly **TL → TR → BR → BL** for consistency.

---

### Phase 2: HSV tuner + exclusions
**Goal:** Fine-tune green mask and remove unwanted areas.

**Sliders**
- `H_min` / `H_max` (0–180)
- `S_min` / `S_max` (0–255)
- `V_min` / `V_max` (0–255)

**Exclusion tools**
| Action                 | Mouse/Key                                         |
|------------------------|---------------------------------------------------|
| Brush exclude/erase    | Left drag (**b** toggles paint↔erase)              |
| Brush size             | `[` / `]`                                          |
| Rectangle exclude      | Shift + Left drag (always adds exclusion)          |

**View & overlay**
| Key   | Action                                      |
|-------|---------------------------------------------|
| c     | Cycle view: overlay ↔ mask ↔ image          |
| m     | Toggle exclusion overlay (red)              |
| u     | Undo last stroke/rectangle                   |
| x     | Clear all exclusions                         |
| Enter | Accept thresholds & exclusions, continue    |
| q/Esc | Accept current settings and exit tuner      |

---

## Command-line options
```text
--input <folder>            Folder with input images
--output <folder>           Folder to save results
--width <int>               Forced rectified width (px)
--height <int>              Forced rectified height (px)
--normalize [none|landscape|portrait]
                            Rotate rectified output to desired orientation
--tune                      Open HSV tuner for each image
```

**Example:**
```bash
QT_QPA_PLATFORM=xcb python src/plots_green.py   --input data/in   --output data/out   --normalize landscape   --tune
```

**Batch (no tuner):**
```bash
python src/plots_green.py --input data/in --output data/out --normalize landscape
```

**Resume after interruption:**
```bash
python src/plots_green.py --input data/in --output data/out --normalize landscape --resume
```

---

## Outputs
In `--output`:

Per image:
- `{basename}_rectified.jpg` — rectified plot
- `{basename}_mask.png` — binary vegetation mask (after exclusions)
- `{basename}_overlay.jpg` — rectified image + green overlay
- `{basename}_corners.json` — clicked points, ops, thresholds
- `{basename}_exclude.png` — exclusion mask (0=keep, 255=exclude)

Run-level:
- `foliage_results.csv` — one row per image:
  ```
  image, percent_green, rect_width, rect_height
  ```
- `hsv_thresholds.json` — last-used HSV ranges

---

## How thresholds & exclusions persist
- **HSV thresholds**: Stored globally in `hsv_thresholds.json` in the output folder; reloaded at next run.
- **Exclusion mask**: Stored per-image as `{basename}_exclude.png`; applied automatically in future runs.

---

## Tips & best practices
- Lighting changes → expect to tweak thresholds.
- Set `--width/--height` or `--normalize` for uniform outputs.
- Click plot corners, avoid paths/alleys.
- Use rectangles for big areas; brush for small edits.
- Undo often — strokes and rectangles are recorded.
- Headless environments not supported (GUI required).

---

## Troubleshooting
**NULL window handler**
- Use `QT_QPA_PLATFORM=xcb` on Linux.
- Install `opencv-python`, not `opencv-python-headless`.

**No window / SSH**
- Use a local session or `ssh -X`.
- Wayland → try `QT_QPA_PLATFORM=xcb`.

**Mask grabs soil/labels**
- Raise `S_min` and `V_min`.
- Use rectangles to exclude signage.
- Narrow `H_min`/`H_max` for green shadows.

---

## FAQ
**Do I select corners every time?**  
Yes — ensures correct rectification.

**Can I reuse exclusions without tuning?**  
Yes — existing `{basename}_exclude.png` files are applied.

**What is “percent green”?**  
`(green_pixels_after_exclusions / total_pixels) * 100`

**Can I standardize output size?**  
Yes — `--width` and/or `--height`.

**Change default HSV ranges?**  
Edit defaults in the script or run `--tune` to update.

---

## License

