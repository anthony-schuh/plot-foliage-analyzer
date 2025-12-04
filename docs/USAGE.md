# Usage Guide

## Basic Workflow

### 1. Single Directory Processing

Process images from one directory:

```bash
QT_QPA_PLATFORM=xcb python src/plots_green.py \
    --input data/input/ \
    --output data/output/ \
    --normalize landscape \
    --tune
```

**Quit & continue later:**

If you quit mid-batch (press `q` or `Esc`), just rerun the same command; images with existing outputs are skipped automatically.

### 2. Batch Processing

Process multiple directories at once:

```bash
chmod +x scripts/batch_process.sh
./scripts/batch_process.sh \
    --input-base data/input/ \
    --output-base data/output/ \
    --normalize landscape
```

### 3. Combining Results

Merge all CSV results into one file:

```bash
python scripts/combine_results.py \
    --input data/output/ \
    --output combined_results.csv
```

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--input` | Input folder with images | Required |
| `--output` | Output folder for results | Required |
| `--width` | Force rectified width (pixels) | Auto |
| `--height` | Force rectified height (pixels) | Auto |
| `--normalize` | Rotate output orientation | `none` |
| `--tune` | Open HSV tuner for each image | Off |
| `--resume` | Deprecated; auto skip is always on | Off |

## Interactive Controls

### Corner Selection Phase

- **Left-click**: Add corner point
- **a/d**: Rotate 90° counter-clockwise/clockwise
- **h/v**: Flip horizontally/vertically
- **u**: Undo last point
- **r**: Reset all points
- **s**: Skip image
- **Enter**: Accept (when 4 points selected)
- **q/Esc**: Quit

### HSV Tuner Phase

- **Left-drag**: Brush paint/erase
- **Shift+Left-drag**: Rectangle exclusion
- **b**: Toggle brush mode (paint/erase)
- **[/]**: Decrease/increase brush size
- **c**: Cycle view (overlay/mask/image)
- **m**: Toggle exclusion overlay
- **u**: Undo last action
- **x**: Clear all exclusions
- **Enter**: Accept and continue
- **q/Esc**: Accept and exit

## Output Files

For each processed image:

- `{name}_rectified.jpg` - Perspective-corrected image
- `{name}_mask.png` - Binary vegetation mask
- `{name}_overlay.jpg` - Image with green overlay
- `{name}_corners.json` - Processing metadata
- `{name}_exclude.png` - Exclusion mask

Summary files:

- `foliage_results.csv` - Vegetation percentages
- `hsv_thresholds.json` - Last used HSV values

## Tips

1. **Consistent corner selection**: Click in same order (TL→TR→BR→BL)
2. **Lighting variations**: Adjust HSV thresholds with `--tune`
3. **Remove artifacts**: Use Shift+drag rectangles for large areas
4. **Fine adjustments**: Use brush for precise exclusions
5. **Standardize outputs**: Use `--normalize` for consistent orientation
6. **Resume processing**: Quit anytime and rerun; existing outputs are auto-skipped
7. **Results tracking**: CSV/exclusion files update immediately after each image
