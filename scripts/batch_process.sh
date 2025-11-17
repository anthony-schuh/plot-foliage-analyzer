#!/bin/bash
# Batch processing script for multiple image directories

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Default values
INPUT_BASE=""
OUTPUT_BASE=""
NORMALIZE="landscape"
TUNE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --input-base)
            INPUT_BASE="$2"
            shift 2
            ;;
        --output-base)
            OUTPUT_BASE="$2"
            shift 2
            ;;
        --normalize)
            NORMALIZE="$2"
            shift 2
            ;;
        --tune)
            TUNE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [ -z "$INPUT_BASE" ] || [ -z "$OUTPUT_BASE" ]; then
    echo "Usage: $0 --input-base <dir> --output-base <dir> [--normalize landscape|portrait|none] [--tune]"
    exit 1
fi

# Process each subdirectory
for input_dir in "$INPUT_BASE"/*/ ; do
    if [ -d "$input_dir" ]; then
        dir_name=$(basename "$input_dir")
        output_dir="$OUTPUT_BASE/$dir_name"
        
        echo "Processing: $dir_name"
        
        cmd="QT_QPA_PLATFORM=xcb python $PROJECT_DIR/src/plots_green.py --input \"$input_dir\" --output \"$output_dir\" --normalize $NORMALIZE"
        
        if [ "$TUNE" = true ]; then
            cmd="$cmd --tune"
        fi
        
        eval $cmd
    fi
done

echo "Batch processing complete!"
