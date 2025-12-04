# Resume Feature Example

## How It Works

The resume feature now works automatically: rerun the same command and the tool inspects the output folder to skip images that already produced rectified/mask/overlay/corner files.

## Example Workflow

### Initial Processing

Process a batch of 100 images:

```bash
QT_QPA_PLATFORM=xcb python src/plots_green.py \
    --input data/input/ \
    --output data/output/ \
    --normalize landscape \
    --tune
```

After processing 30 images, you press `q` to quit:

```
[OK] image_001.jpg → 45.23% green, size=800x600
[OK] image_002.jpg → 52.10% green, size=800x600
...
[OK] image_030.jpg → 48.75% green, size=800x600

[QUIT] Stopping early. Existing outputs remain intact.
Re-run the command to continue; images with saved outputs will be skipped automatically.
```

### Automatic Continue

Later, rerun exactly the same command (no extra flags needed):

```bash
QT_QPA_PLATFORM=xcb python src/plots_green.py \
    --input data/input/ \
    --output data/output/ \
    --normalize landscape \
    --tune
```

The tool scans the output folder before starting and prints:

```
Found 100 input image(s) in 'data/input/'.
Detected 30 already processed image(s) in 'data/output/'.
Processing 70 remaining image(s).

[OK] image_031.jpg → 51.20% green, size=800x600
...
```

## Behind the Scenes

The tool now relies entirely on the files it already creates:

1. **Output artifacts** — `_rectified.jpg`, `_mask.png`, `_overlay.jpg`, and `_corners.json` define whether an image is considered processed. If any of these exist for a base filename, that image is skipped on the next run.
2. **`foliage_results.csv`** — Rewritten after each success to keep the summary table up to date (and acts as an additional safeguard/backlog of what was processed).

## Benefits

- **Save Time**: No need to reprocess completed images
- **Flexibility**: Take breaks during long sessions
- **Data Safety**: CSV is flushed after each image
- **Error Recovery**: If the program crashes, resume from last success
- **Manual Control**: Delete specific output artifacts to reprocess a photo from scratch

## Pro Tips

1. **Fresh start**: Delete the entire output folder (or the specific `_rectified/_mask/_overlay/_corners` files) to force every image to re-run.
2. **Check progress**: Count how many `_rectified.jpg` files exist to see how far the batch has gone.
3. **Partial rerun**: Remove the outputs for just the images you want to redo; the next run will include them again.
4. **Backup results**: CSV and exclusion masks update after each image, so copy them elsewhere if you need historical snapshots.
