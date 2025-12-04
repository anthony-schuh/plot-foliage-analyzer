# Plot Foliage Analyzer - GUI Wrapper

This GUI wrapper provides an easy-to-use graphical interface for the Plot Foliage Analyzer tool.

## Quick Start

### Launch the GUI

**Option 1: Using the launcher script (recommended)**
```bash
./run_gui.sh
```

**Option 2: Direct Python execution**
```bash
python3 plot_analyzer_gui.py
```

On Linux systems, if you encounter GUI display issues, set the QT platform:
```bash
export QT_QPA_PLATFORM=xcb
python3 plot_analyzer_gui.py
```

## Features

The GUI provides a user-friendly interface to:

- **Select folders**: Browse and select input/output directories
- **Configure options**: Set width, height, normalization, and processing modes
- **Enable/disable features**: Toggle the HSV tuner; auto-resume is always enabled
- **View help**: Built-in help documentation with keyboard controls
- **Run analysis**: Launch the analysis tool with your configured settings

## GUI Fields

### Required Fields
- **Input Folder**: Directory containing your plot images
- **Output Folder**: Directory where results will be saved

### Optional Settings
- **Width/Height**: Force specific dimensions for rectified images (in pixels)
- **Normalize Output**: Rotate rectified images to landscape, portrait, or none
- **Enable HSV Tuner**: Open interactive HSV adjustment window for each image
- **Resume (deprecated)**: Auto-skip is always on; checkbox kept for backwards compatibility

## How It Works

1. Fill in the input and output folders
2. Configure your desired options
3. Click "Run Analysis"
4. The GUI will construct and execute the command
5. The plot analyzer opens in a separate window for interactive processing

## Dependencies

The GUI requires:
- Python 3.8+
- tkinter (usually included with Python)
- All dependencies from requirements.txt (opencv-python, numpy, pillow)

## Troubleshooting

**GUI doesn't appear**
- Make sure you're running in a graphical environment (not headless SSH)
- Try using `ssh -X` if connecting remotely
- On Linux, set `export QT_QPA_PLATFORM=xcb`

**Import errors**
- Install dependencies: `pip install -r requirements.txt`
- Ensure tkinter is installed (on Ubuntu/Debian: `sudo apt-get install python3-tk`)

## Command Line Alternative

You can still use the command line directly:
```bash
python src/plots_green.py --input data/in --output data/out --tune
```

See the main README.md for complete command-line documentation.
