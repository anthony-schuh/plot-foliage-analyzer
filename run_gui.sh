#!/bin/bash
# Launcher script for Plot Foliage Analyzer GUI

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set QT platform for Linux systems (helps with GUI display)
export QT_QPA_PLATFORM=xcb

# Launch the GUI
python3 "$SCRIPT_DIR/plot_analyzer_gui.py" "$@"
