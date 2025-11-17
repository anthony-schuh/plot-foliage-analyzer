# Resume Feature Example

## How It Works

The resume feature allows you to interrupt batch processing at any time and continue later without reprocessing images.

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

[QUIT] Stopping after processing 30 images.
Run with --resume to continue from where you left off.
```

### Resume Processing

Continue from image 31:

```bash
QT_QPA_PLATFORM=xcb python src/plots_green.py \
    --input data/input/ \
    --output data/output/ \
    --normalize landscape \
    --tune \
    --resume
```

Output shows:

```
[RESUME] Skipping already processed: image_001.jpg
[RESUME] Skipping already processed: image_002.jpg
...
[RESUME] Skipping already processed: image_030.jpg

Processing 70 of 100 total images
Resuming from image 31

[OK] image_031.jpg → 51.20% green, size=800x600
...
```

## Behind the Scenes

The tool creates and maintains:

1. **`.progress.json`** - Tracks which images are completed
   ```json
   {
     "processed": [
       "image_001.jpg",
       "image_002.jpg",
       "image_030.jpg"
     ]
   }
   ```

2. **`foliage_results.csv`** - Appends new results (doesn't overwrite)
   ```csv
   image,percent_green,rect_width,rect_height
   image_001.jpg,45.23,800,600
   image_002.jpg,52.10,800,600
   ...
   ```

## Benefits

- **Save Time**: No need to reprocess completed images
- **Flexibility**: Take breaks during long sessions
- **Data Safety**: CSV is flushed after each image
- **Error Recovery**: If the program crashes, resume from last success
- **Manual Control**: Delete `.progress.json` to start fresh

## Pro Tips

1. **Fresh start**: Delete `.progress.json` in output folder to reprocess all
2. **Check progress**: Look at `.progress.json` to see what's been processed
3. **Partial rerun**: Edit `.progress.json` to remove specific images from processed list
4. **Backup results**: CSV is updated after each image, so you never lose work
