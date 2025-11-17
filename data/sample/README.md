# Sample Data

Place sample images here for testing and demonstration purposes.

## Recommended Sample Images

- Field plot images with visible vegetation
- Various lighting conditions
- Different plot orientations
- Images with and without markers/labels

## Testing the Tool

Run on sample data:

```bash
QT_QPA_PLATFORM=xcb python src/plots_green.py \
    --input data/sample/ \
    --output data/output/sample_results/ \
    --normalize landscape \
    --tune
```
