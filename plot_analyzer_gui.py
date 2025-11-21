#!/usr/bin/env python3
"""
GUI Wrapper for Plot Foliage Analyzer
Provides a graphical interface to configure and launch the plot analysis tool.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import sys
import os
import threading

class PlotAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Plot Foliage Analyzer")
        self.root.geometry("700x600")
        
        # Variables
        self.input_path = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.width_var = tk.StringVar()
        self.height_var = tk.StringVar()
        self.normalize_var = tk.StringVar(value="none")
        self.tune_var = tk.BooleanVar(value=True)
        self.resume_var = tk.BooleanVar(value=False)
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Title
        title_label = ttk.Label(main_frame, text="Plot Foliage Analyzer", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=row, column=0, columnspan=3, pady=(0, 10))
        row += 1
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Input path (file or folder)
        ttk.Label(main_frame, text="Input Path:").grid(
            row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_path, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        input_btns = ttk.Frame(main_frame)
        input_btns.grid(row=row, column=2, pady=5)
        ttk.Button(input_btns, text="Folder...",
                  command=self.browse_input_folder).pack(fill=tk.X, pady=2)
        ttk.Button(input_btns, text="File...",
                  command=self.browse_input_file).pack(fill=tk.X, pady=2)
        row += 1
        
        # Output folder
        ttk.Label(main_frame, text="Output Folder:").grid(
            row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_folder, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        ttk.Button(main_frame, text="Browse...", 
                  command=self.browse_output).grid(row=row, column=2, pady=5)
        row += 1
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # Options frame
        options_label = ttk.Label(main_frame, text="Options:", 
                                 font=('Arial', 11, 'bold'))
        options_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(5, 5))
        row += 1
        
        # Width
        ttk.Label(main_frame, text="Width (pixels):").grid(
            row=row, column=0, sticky=tk.W, pady=5)
        width_entry = ttk.Entry(main_frame, textvariable=self.width_var, width=20)
        width_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(main_frame, text="(optional)", foreground='gray').grid(
            row=row, column=2, sticky=tk.W, pady=5)
        row += 1
        
        # Height
        ttk.Label(main_frame, text="Height (pixels):").grid(
            row=row, column=0, sticky=tk.W, pady=5)
        height_entry = ttk.Entry(main_frame, textvariable=self.height_var, width=20)
        height_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(main_frame, text="(optional)", foreground='gray').grid(
            row=row, column=2, sticky=tk.W, pady=5)
        row += 1
        
        # Normalize
        ttk.Label(main_frame, text="Normalize Output:").grid(
            row=row, column=0, sticky=tk.W, pady=5)
        normalize_combo = ttk.Combobox(main_frame, textvariable=self.normalize_var,
                                       values=["none", "landscape", "portrait"],
                                       state='readonly', width=18)
        normalize_combo.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(main_frame, text="Rotate rectified images", foreground='gray').grid(
            row=row, column=2, sticky=tk.W, pady=5)
        row += 1
        
        # Checkboxes
        ttk.Checkbutton(main_frame, text="Enable HSV Tuner (interactive adjustment)",
                       variable=self.tune_var).grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=5)
        row += 1
        
        ttk.Checkbutton(main_frame, text="Resume from last processed image",
                       variable=self.resume_var).grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=5)
        row += 1
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # Info text
        info_frame = ttk.LabelFrame(main_frame, text="Information", padding="5")
        info_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        info_text = tk.Text(info_frame, height=6, width=80, wrap=tk.WORD, 
                           background='#f0f0f0', relief=tk.FLAT)
        info_text.insert('1.0', 
            "This tool analyzes plot images to quantify green vegetation (foliage).\n\n"
            "• Input path can be a single image or a folder of images\n"
            "• Output folder will store rectified images, masks, and results CSV\n"
            "• With HSV Tuner enabled, you'll interactively adjust thresholds\n"
            "• Use Resume to continue interrupted batch processing")
        info_text.config(state=tk.DISABLED)
        info_text.pack(fill=tk.BOTH, expand=True)
        row += 1
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=15)
        
        ttk.Button(button_frame, text="Run Analysis", 
                  command=self.run_analysis, style='Accent.TButton').pack(
            side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Help", 
                  command=self.show_help).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Quit", 
                  command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
    def browse_input_folder(self):
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder:
            self.input_path.set(folder)
            
    def browse_input_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.tif *.tiff *.bmp"),
                ("All files", "*.*"),
            ],
        )
        if file_path:
            self.input_path.set(file_path)
            
    def browse_output(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(folder)
    
    def validate_inputs(self):
        input_path = self.input_path.get().strip()
        if not input_path:
            messagebox.showerror("Error", "Please select an input file or folder")
            return False
            
        if not self.output_folder.get():
            messagebox.showerror("Error", "Please select an output folder")
            return False
            
        if not os.path.exists(input_path):
            messagebox.showerror("Error", "Input path does not exist")
            return False
            
        # Validate width and height if provided
        if self.width_var.get():
            try:
                int(self.width_var.get())
            except ValueError:
                messagebox.showerror("Error", "Width must be a valid integer")
                return False
                
        if self.height_var.get():
            try:
                int(self.height_var.get())
            except ValueError:
                messagebox.showerror("Error", "Height must be a valid integer")
                return False
        
        return True
    
    def build_command(self):
        # Find the script path relative to this GUI script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        plots_script = os.path.join(script_dir, "src", "plots_green.py")
        
        cmd = [sys.executable, plots_script]
        cmd.extend(["--input", self.input_path.get()])
        cmd.extend(["--output", self.output_folder.get()])
        
        if self.width_var.get():
            cmd.extend(["--width", self.width_var.get()])
            
        if self.height_var.get():
            cmd.extend(["--height", self.height_var.get()])
            
        if self.normalize_var.get() != "none":
            cmd.extend(["--normalize", self.normalize_var.get()])
            
        if self.tune_var.get():
            cmd.append("--tune")
            
        if self.resume_var.get():
            cmd.append("--resume")
            
        return cmd
    
    def run_analysis(self):
        if not self.validate_inputs():
            return
            
        cmd = self.build_command()
        
        # Show command to user
        cmd_str = ' '.join(cmd)
        result = messagebox.askyesno(
            "Confirm", 
            f"Ready to run analysis with the following command:\n\n{cmd_str}\n\n"
            "The program will open in a new window. Continue?")
        
        if not result:
            return
        
        # Set QT platform for Linux
        env = os.environ.copy()
        if sys.platform.startswith('linux'):
            env['QT_QPA_PLATFORM'] = 'xcb'
        
        try:
            # Run the command
            subprocess.Popen(cmd, env=env)
            self.root.after(0, self.root.destroy)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start analysis:\n{str(e)}")
    
    def show_help(self):
        help_window = tk.Toplevel(self.root)
        help_window.title("Help - Plot Foliage Analyzer")
        help_window.geometry("600x500")
        
        text = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, padx=10, pady=10)
        text.pack(fill=tk.BOTH, expand=True)
        
        help_text = """
PLOT FOLIAGE ANALYZER - HELP

This tool helps you analyze plot images to quantify green vegetation (carrot foliage).

WORKFLOW:
1. Select your input file or folder containing plot images
2. Select an output folder for results
3. Configure options as needed
4. Click "Run Analysis"

INTERACTIVE STEPS:
For each image, you will:
• Click 4 corners of the plot
• (Optional) Adjust HSV thresholds to refine green detection
• (Optional) Exclude non-plot areas with brush or rectangles

CONTROLS - Corner Selection:
• Left-click: Add corner point (4 needed)
• a/d: Rotate image 90° left/right
• h/v: Flip horizontally/vertically
• u: Undo last point
• r: Reset all points
• s: Skip this image
• p: Go back to the previous image to re-mask
• Enter: Accept (when 4 points selected)
• q/Esc: Quit program

CONTROLS - HSV Tuner (if enabled):
• Sliders: Adjust H/S/V min/max thresholds
• Left drag: Paint exclusion (b toggles paint/erase)
• [/]: Change brush size
• Shift+drag: Draw exclusion rectangle
• c: Cycle view (overlay/mask/image)
• m: Toggle exclusion overlay
• u: Undo last stroke/rectangle
• x: Clear all exclusions
• Enter: Accept and continue
• q/Esc: Exit tuner

OUTPUT:
• Rectified images and masks
• foliage_results.csv with percent green per image
• HSV threshold settings
• Exclusion masks (reusable in future runs)

For more details, see the README.md file.
"""
        text.insert('1.0', help_text)
        text.config(state=tk.DISABLED)
        
        ttk.Button(help_window, text="Close", 
                  command=help_window.destroy).pack(pady=10)


def main():
    root = tk.Tk()
    app = PlotAnalyzerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
