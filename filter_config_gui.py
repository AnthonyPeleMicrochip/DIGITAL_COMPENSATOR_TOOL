#!/usr/bin/env python3
"""
Filter Configuration Generator GUI
Creates and manages filter configuration JSON files for digital compensators
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, font
import json
import subprocess
import sys
import os
from datetime import date
import math


class FilterConfigGUI:
    def __init__(self, root, default_file=None):
        self.root = root
        self.root.title("Filter Configuration Generator")
        self.root.geometry("1200x800")
        
        if default_file is None:
            # Initialize default configuration
            self.config = {
                "name": "Name_your_filter_here",
                "h_file_name": "your_filter_C_code_header_file_name_here.h",
                "bode_plot_output_file_name": "your_filter_BODE_Plot_file_name_here.pdf",
                "h_file_output_folder": "./_output_docs",
                "type": "3P3Z",
                "version": "1.0.0",
                "description": "Your compesator description here.",
                "author": "Who wrote this filter?",
                "company": "Microchip Technology Inc.",
                "date": str(date.today()),
                "filter_parameters": {
                    "BODE_PLOT_MIN_FREQ_10powerN": 0,
                    "BODE_PLOT_MAX_FREQ_10powerN": 6,
                    "BODE_PLOT_NB_POINTS": 1000,
                    "SAMPLING_FREQUENCY_HZ": 500000,
                    "ESTIMATED_DIGITAL_FILTER_TIME_DELAY_IN_S": 700e-9,
                    "ESTIMATED_ADC_TRIGGER_POINT_DELAY": 1e-6,
                    "coefficient_format": "float",
                    "frequencies_Hz": {
                        "Integrator_pole": [
                            {"frequency": 1200, "type": "Integrator"}
                        ],
                        "Zeros": [
                            {"frequency": 2551, "type": "Zero"},
                            {"frequency": 3827, "type": "Zero"}
                        ],
                        "Poles": [
                            {"frequency": 80000, "type": "Pole"},
                            {"frequency": 170000, "type": "Pole"}
                        ]
                    }
                }
            }
        else:
            # Load configuration from provided JSON file
            with open(default_file, 'r') as f:
                self.config = json.load(f)       
        
        self.create_widgets()
        self.load_config_to_ui()
    
    def create_widgets(self):
        # Create main container with scrollbar
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # ===== GENERAL INFORMATION SECTION (LEFT) =====
        gen_frame = ttk.LabelFrame(scrollable_frame, text="General Information", padding="10")
        gen_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(0, 5))
        

        # Filter Name
        row_number=0
        ttk.Label(gen_frame, text="Filter Name:").grid(row=row_number, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar(value=self.config["name"])
        self.name_var.trace_add("write", self.update_auto_filenames)
        ttk.Entry(gen_frame, textvariable=self.name_var, width=40).grid(row=row_number, column=1, pady=5, padx=5)
        
        # H File Name (auto-generated)
        row_number += 1
        ttk.Label(gen_frame, text="C Code .h Header File Name (Generated):").grid(row=row_number, column=0, sticky=tk.W, pady=5)
        self.h_file_var = tk.StringVar(value=self.config["h_file_name"])
        #h_entry = ttk.Entry(gen_frame, textvariable=self.h_file_var, width=40, state="readonly")
        h_entry = ttk.Entry(gen_frame, textvariable=self.h_file_var, width=40)
        h_entry.grid(row=row_number, column=1, pady=5, padx=5)
        
        # Bode Plot Output File Name
        row_number += 1
        ttk.Label(gen_frame, text="Bode Plot pdf file name (Generated):").grid(row=row_number, column=0, sticky=tk.W, pady=5)
        self.bode_var = tk.StringVar(value=self.config["bode_plot_output_file_name"])
        ttk.Entry(gen_frame, textvariable=self.bode_var, width=40).grid(row=row_number, column=1, pady=5, padx=5)

        # Output Folder
        row_number += 1
        ttk.Label(gen_frame, text="Header .h File Output Folder:").grid(row=row_number, column=0, sticky=tk.W, pady=5)
        output_folder_frame = ttk.Frame(gen_frame)
        output_folder_frame.grid(row=row_number, column=1, pady=5, padx=5, sticky=tk.W)
        self.output_folder_var = tk.StringVar(value=self.config.get("h_file_output_folder", "./_output_docs"))
        ttk.Entry(output_folder_frame, textvariable=self.output_folder_var, width=30).grid(row=0, column=0)
        ttk.Button(output_folder_frame, text="Browse...", command=self.browse_output_folder, width=10).grid(row=0, column=1, padx=(5, 0))

        # Filter Type
        row_number += 1
        ttk.Label(gen_frame, text="Filter Type:").grid(row=row_number, column=0, sticky=tk.W, pady=5)
        self.type_var = tk.StringVar(value=self.config["type"])
        type_combo = ttk.Combobox(gen_frame, textvariable=self.type_var, 
                                   values=["1P1Z", "2P2Z", "3P3Z", "4P4Z", "5P5Z", "6P6Z"],
                                   state="readonly", width=37)
        type_combo.grid(row=row_number, column=1, pady=5, padx=5)
        
        # Author
        row_number += 1
        ttk.Label(gen_frame, text="Author:").grid(row=row_number, column=0, sticky=tk.W, pady=5)
        self.author_var = tk.StringVar(value=self.config["author"])
        ttk.Entry(gen_frame, textvariable=self.author_var, width=40).grid(row=row_number, column=1, pady=5, padx=5)
        
        # Description
        row_number += 1
        ttk.Label(gen_frame, text="Description:").grid(row=row_number, column=0, sticky=tk.W, pady=5)
        self.desc_text = tk.Text(gen_frame, width=40, height=3)
        self.desc_text.grid(row=row_number, column=1, pady=5, padx=5)
        self.desc_text.insert("1.0", self.config["description"])
        
        # ===== FILTER PARAMETERS SECTION (RIGHT) =====
        param_frame = ttk.LabelFrame(scrollable_frame, text="Filter Parameters", padding="10")
        param_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(5, 0))
        
        # Bode Plot Min Freq
        row_number = 0
        ttk.Label(param_frame, text="Bode Plot Min Freq (10\u207F):").grid(row=row_number, column=0, sticky=tk.W, pady=5)
        self.min_freq_var = tk.IntVar(value=self.config["filter_parameters"]["BODE_PLOT_MIN_FREQ_10powerN"])
        ttk.Spinbox(param_frame, from_=-10, to=10, textvariable=self.min_freq_var, width=27).grid(row=row_number, column=1, pady=5, padx=5)
        
        row_number += 1
        label_font = font.Font(slant="italic", size=12)
        self.bode_min_label_var = tk.StringVar()
        ttk.Label(
            param_frame,
            font=label_font,
            textvariable=self.bode_min_label_var
            ).grid(row=row_number, column=1, sticky=tk.W, pady=5)
        # Link changes of Bode freq exponents to label updates
        self.min_freq_var.trace_add("write", self.update_bode_labels)
        
        
        # Bode Plot Max Freq
        row_number += 1
        ttk.Label(param_frame, text="Bode Plot Max Freq (10\u207F):").grid(row=row_number, column=0, sticky=tk.W, pady=5)
        self.max_freq_var = tk.IntVar(value=self.config["filter_parameters"]["BODE_PLOT_MAX_FREQ_10powerN"])
        ttk.Spinbox(param_frame, from_=-10, to=10, textvariable=self.max_freq_var, width=27).grid(row=row_number, column=1, pady=5, padx=5)
        
        row_number += 1
        label_font = font.Font(slant="italic", size=12)
        self.bode_max_label_var = tk.StringVar()
        ttk.Label(
            param_frame,
            font=label_font,
            textvariable=self.bode_max_label_var
            ).grid(row=row_number, column=1, sticky=tk.W, pady=5)
        # Link changes of Bode freq exponents to label updates
        self.max_freq_var.trace_add("write", self.update_bode_labels)
        
        
        # Bode Plot Number of Points
        row_number += 1
        ttk.Label(param_frame, text="Bode Plot Nb Points:").grid(row=row_number, column=0, sticky=tk.W, pady=5)
        self.nb_points_var = tk.IntVar(value=self.config["filter_parameters"]["BODE_PLOT_NB_POINTS"])
        ttk.Entry(param_frame, textvariable=self.nb_points_var, width=30).grid(row=row_number, column=1, pady=5, padx=5)
        
        # Sampling Frequency
        row_number += 1
        ttk.Label(param_frame, text="Sampling Frequency (Hz):").grid(row=row_number, column=0, sticky=tk.W, pady=5)
        self.sampling_freq_var = tk.DoubleVar(value=self.config["filter_parameters"]["SAMPLING_FREQUENCY_HZ"])
        ttk.Entry(param_frame, textvariable=self.sampling_freq_var, width=30).grid(row=row_number, column=1, pady=5, padx=5)
        
        # Digital Filter Time Delay
        row_number += 1
        ttk.Label(param_frame, text="Digital Filter Time Delay (s):").grid(row=row_number, column=0, sticky=tk.W, pady=5)
        self.filter_delay_var = tk.DoubleVar(value=self.config["filter_parameters"]["ESTIMATED_DIGITAL_FILTER_TIME_DELAY_IN_S"])
        ttk.Entry(param_frame, textvariable=self.filter_delay_var, width=30).grid(row=row_number, column=1, pady=5, padx=5)
        
        # ADC Trigger Point Delay
        row_number += 1
        ttk.Label(param_frame, text="ADC Trigger Point Delay (s):").grid(row=row_number, column=0, sticky=tk.W, pady=5)
        self.adc_delay_var = tk.DoubleVar(value=self.config["filter_parameters"]["ESTIMATED_ADC_TRIGGER_POINT_DELAY"])
        ttk.Entry(param_frame, textvariable=self.adc_delay_var, width=30).grid(row=row_number, column=1, pady=5, padx=5)
        
        # Coefficient Format
        row_number += 1
        ttk.Label(param_frame, text="Coefficient Format:").grid(row=row_number, column=0, sticky=tk.W, pady=5)
        self.coef_format_var = tk.StringVar(value=self.config["filter_parameters"]["coefficient_format"])
        coef_combo = ttk.Combobox(param_frame, textvariable=self.coef_format_var,
                                   values=["float", "Q15", "Q31"],
                                   state="readonly", width=27)
        coef_combo.grid(row=row_number, column=1, pady=5, padx=5)

        # Plant Data File (optional)
        row_number += 1
        ttk.Label(param_frame, text="Plant Data File (optional):").grid(row=row_number, column=0, sticky=tk.W, pady=5)
        plant_file_frame = ttk.Frame(param_frame)
        plant_file_frame.grid(row=row_number, column=1, pady=5, padx=5, sticky=tk.W)
        self.plant_file_var = tk.StringVar(value=self.config.get("plant_data_file", ""))
        ttk.Entry(plant_file_frame, textvariable=self.plant_file_var, width=20).grid(row=0, column=0)
        ttk.Button(plant_file_frame, text="Browse...", command=self.browse_plant_file).grid(row=0, column=1, padx=(5, 0))
        
        # ===== FREQUENCIES SECTION =====
        freq_frame = ttk.LabelFrame(scrollable_frame, text="Frequencies Configuration", padding="10")
        freq_frame.grid(row=1, column=0, columnspan=1, sticky=(tk.W, tk.E), pady=5)
        
        # Integrator Pole
        ttk.Label(freq_frame, text="Integrator Pole (Hz):", font=("", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.integrator_var = tk.DoubleVar(value=self.config["filter_parameters"]["frequencies_Hz"]["Integrator_pole"][0]["frequency"])
        ttk.Entry(freq_frame, textvariable=self.integrator_var, width=20).grid(row=0, column=1, pady=5, padx=5)
        
        # Zeros
        ttk.Label(freq_frame, text="Zeros:", font=("", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.zeros_frame = ttk.Frame(freq_frame)
        self.zeros_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        self.zero_entries = []
        self.create_frequency_list("Zeros")
        
        ttk.Button(freq_frame, text="+ Add Zero", command=lambda: self.add_frequency("Zeros")).grid(row=3, column=0, columnspan=3, pady=5)
        
        # Poles
        ttk.Label(freq_frame, text="Poles:", font=("", 10, "bold")).grid(row=4, column=0, sticky=tk.W, pady=5)
        self.poles_frame = ttk.Frame(freq_frame)
        self.poles_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        self.pole_entries = []
        self.create_frequency_list("Poles")
        
        ttk.Button(freq_frame, text="+ Add Pole", command=lambda: self.add_frequency("Poles")).grid(row=6, column=0, columnspan=3, pady=5)
        
        # ===== BODE PLOT SECTION =====
        bode_frame = ttk.LabelFrame(scrollable_frame, text="Bode Plot", padding="10")
        bode_frame.grid(row=1, column=1, columnspan=1, sticky=(tk.W, tk.E), pady=5)
        

        
        # ===== ACTION BUTTONS =====
        button_frame = ttk.Frame(scrollable_frame, padding="10")
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="📂 Load JSON", command=self.load_json, width=20).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="💾 Save Configuration", command=self.save_config_as, width=25).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="⚙️ Generate Coefficients", command=self.run_compensator, width=25).grid(row=0, column=2, padx=5)
    
    def browse_plant_file(self):
        """Open file dialog to select a plant data text file."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filename = filedialog.askopenfilename(
            initialdir=script_dir,
            title="Select Plant Data File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.plant_file_var.set(filename)

    def browse_output_folder(self):
        """Open dialog to select the output folder for generated files."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        current = self.output_folder_var.get().strip()
        if current:
            initial = os.path.join(script_dir, current)
        else:
            initial = script_dir
        folder = filedialog.askdirectory(initialdir=initial, title="Select Output Folder")
        if folder:
            rel = os.path.relpath(folder, script_dir).replace("\\", "/")
            self.output_folder_var.set("./" + rel)

    def update_auto_filenames(self, *args):
        """Auto-generate H file name and Bode plot filename from filter name"""
        name = self.name_var.get()
        # Convert to PascalCase with underscores for H file
        pascal_case = '_'.join(word.capitalize() for word in name.split('_'))
        self.h_file_var.set(pascal_case + '.h')
        
        # Generate Bode plot filename from filter name
        bode_filename = pascal_case + '_Bode_Plot.pdf'
        self.bode_var.set(bode_filename)
        
    def update_bode_labels(self, *args):
        """Update the explanatory labels for Bode min/max frequencies."""
        try:
            min_n = int(self.min_freq_var.get())
            max_n = int(self.max_freq_var.get())
        except Exception:
            return

        def _format_freq(hz: float) -> str:
            if hz >= 1e6:
                return f"{hz / 1e6:.3g} MHz"
            if hz >= 1e3:
                return f"{hz / 1e3:.3g} kHz"
            if hz >= 1:
                return f"{hz:.3g} Hz"
            return f"{hz:.3g} Hz"

        min_hz = 10 ** min_n
        max_hz = 10 ** max_n

        if hasattr(self, "bode_min_label_var"):
            self.bode_min_label_var.set(
                f"Bode plot min frequency: {_format_freq(min_hz)}"
            )
        if hasattr(self, "bode_max_label_var"):
            self.bode_max_label_var.set(
                f"Bode plot max frequency: {_format_freq(max_hz)}"
            )
    
    
    def create_frequency_list(self, freq_type):
        """Create entry fields for frequencies (Zeros or Poles)"""
        frequencies = self.config["filter_parameters"]["frequencies_Hz"][freq_type]
        
        if freq_type == "Zeros":
            parent_frame = self.zeros_frame
            entries_list = self.zero_entries
        else:
            parent_frame = self.poles_frame
            entries_list = self.pole_entries
        
        for i, freq_data in enumerate(frequencies):
            frame = ttk.Frame(parent_frame)
            frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=2)
            
            var = tk.DoubleVar(value=freq_data["frequency"])
            ttk.Label(frame, text=f"{freq_type[:-1]} {i+1} (Hz):").grid(row=0, column=0, padx=5)
            ttk.Entry(frame, textvariable=var, width=20).grid(row=0, column=1, padx=5)
            ttk.Button(frame, text="Remove", command=lambda f=frame, v=var: self.remove_frequency(freq_type, f, v)).grid(row=0, column=2, padx=5)
            
            entries_list.append((frame, var))
    
    def add_frequency(self, freq_type):
        """Add a new frequency entry"""
        if freq_type == "Zeros":
            parent_frame = self.zeros_frame
            entries_list = self.zero_entries
        else:
            parent_frame = self.poles_frame
            entries_list = self.pole_entries
        
        i = len(entries_list)
        frame = ttk.Frame(parent_frame)
        frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=2)
        
        var = tk.DoubleVar(value=1000)
        ttk.Label(frame, text=f"{freq_type[:-1]} {i+1} (Hz):").grid(row=0, column=0, padx=5)
        ttk.Entry(frame, textvariable=var, width=20).grid(row=0, column=1, padx=5)
        ttk.Button(frame, text="Remove", command=lambda f=frame, v=var: self.remove_frequency(freq_type, f, v)).grid(row=0, column=2, padx=5)
        
        entries_list.append((frame, var))
    
    def remove_frequency(self, freq_type, frame, var):
        """Remove a frequency entry"""
        if freq_type == "Zeros":
            entries_list = self.zero_entries
        else:
            entries_list = self.pole_entries
        
        # Find and remove the entry
        for i, (f, v) in enumerate(entries_list):
            if f == frame:
                entries_list.pop(i)
                frame.destroy()
                break
        
        # Renumber remaining entries
        self.renumber_frequencies(freq_type)
    
    def renumber_frequencies(self, freq_type):
        """Renumber frequency labels after removal"""
        if freq_type == "Zeros":
            entries_list = self.zero_entries
        else:
            entries_list = self.pole_entries
        
        for i, (frame, var) in enumerate(entries_list):
            label = frame.winfo_children()[0]
            label.config(text=f"{freq_type[:-1]} {i+1} (Hz):")
    
    def collect_config(self):
        """Collect all configuration from UI"""
        # Collect Zeros
        zeros = []
        for frame, var in self.zero_entries:
            zeros.append({"frequency": var.get(), "type": "Zero"})
        
        # Collect Poles
        poles = []
        for frame, var in self.pole_entries:
            poles.append({"frequency": var.get(), "type": "Pole"})
        
        config = {
            "name": self.name_var.get(),
            "h_file_name": self.h_file_var.get(),
            "bode_plot_output_file_name": self.bode_var.get(),
            "h_file_output_folder": self.output_folder_var.get(),
            "type": self.type_var.get(),
            "version": "1.0.0",
            "description": self.desc_text.get("1.0", tk.END).strip(),
            "author": self.author_var.get(),
            "company": "Microchip Technology Inc.",
            "date": str(date.today()),
        }
        plant_file = self.plant_file_var.get().strip()
        if plant_file:
            config["plant_data_file"] = plant_file
        config["filter_parameters"] = {
                "BODE_PLOT_MIN_FREQ_10powerN": self.min_freq_var.get(),
                "BODE_PLOT_MAX_FREQ_10powerN": self.max_freq_var.get(),
                "BODE_PLOT_NB_POINTS": self.nb_points_var.get(),
                "SAMPLING_FREQUENCY_HZ": self.sampling_freq_var.get(),
                "ESTIMATED_DIGITAL_FILTER_TIME_DELAY_IN_S": self.filter_delay_var.get(),
                "ESTIMATED_ADC_TRIGGER_POINT_DELAY": self.adc_delay_var.get(),
                "coefficient_format": self.coef_format_var.get(),
                "frequencies_Hz": {
                    "Integrator_pole": [
                        {"frequency": self.integrator_var.get(), "type": "Integrator"}
                    ],
                    "Zeros": zeros,
                    "Poles": poles
                }
            }

        return config
    
    def save_config_as(self):
        """Save configuration to a JSON file chosen by the user, or default to {filter_name}.json"""
        try:
            config = self.collect_config()
            script_dir = os.path.dirname(os.path.abspath(__file__))

            filename = filedialog.asksaveasfilename(
                initialdir=script_dir,
                title="Save Configuration As",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            )

            if not filename:
                filter_name = self.name_var.get()
                filename = os.path.join(script_dir, f"{filter_name}.json")

            with open(filename, 'w') as f:
                json.dump(config, f, indent=4)
            messagebox.showinfo("Success", f"Configuration saved to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration:\n{str(e)}")
    
    def load_json(self):
        """Load configuration from JSON file"""
        try:
            # Get the directory where the script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            filename = filedialog.askopenfilename(
                initialdir=script_dir,
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'r') as f:
                    self.config = json.load(f)
                self.load_config_to_ui()
                messagebox.showinfo("Success", "Configuration loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration:\n{str(e)}")
    
    def load_config_to_ui(self):
        """Load configuration data into UI fields"""
        # Clear existing frequency entries
        for frame, var in self.zero_entries:
            frame.destroy()
        for frame, var in self.pole_entries:
            frame.destroy()
        self.zero_entries.clear()
        self.pole_entries.clear()
        
        # Load general information
        self.name_var.set(self.config["name"])
        self.h_file_var.set(self.config["h_file_name"])
        self.bode_var.set(self.config["bode_plot_output_file_name"])
        self.output_folder_var.set(self.config.get("h_file_output_folder", "./_output_docs"))
        self.type_var.set(self.config["type"])
        self.author_var.set(self.config["author"])
        self.desc_text.delete("1.0", tk.END)
        self.desc_text.insert("1.0", self.config["description"])
        
        # Load filter parameters
        params = self.config["filter_parameters"]
        self.min_freq_var.set(params["BODE_PLOT_MIN_FREQ_10powerN"])
        self.max_freq_var.set(params["BODE_PLOT_MAX_FREQ_10powerN"])
        self.nb_points_var.set(params["BODE_PLOT_NB_POINTS"])
        self.sampling_freq_var.set(params["SAMPLING_FREQUENCY_HZ"])
        self.filter_delay_var.set(params["ESTIMATED_DIGITAL_FILTER_TIME_DELAY_IN_S"])
        self.adc_delay_var.set(params["ESTIMATED_ADC_TRIGGER_POINT_DELAY"])
        self.coef_format_var.set(params["coefficient_format"])
        self.plant_file_var.set(self.config.get("plant_data_file", ""))

        # Load frequencies
        self.integrator_var.set(params["frequencies_Hz"]["Integrator_pole"][0]["frequency"])
        self.create_frequency_list("Zeros")
        self.create_frequency_list("Poles")
    
    def validate_pole_zero_count(self):
        """Check that the number of poles and zeros matches the selected filter type (e.g. 3P3Z)."""
        filter_type_str = self.type_var.get()
        try:
            parts = filter_type_str.upper().replace("Z", "").split("P")
            expected_poles = int(parts[0])
            expected_zeros = int(parts[1])
        except (ValueError, IndexError):
            return True
        actual_poles = 1 + len(self.pole_entries)
        actual_zeros = len(self.zero_entries)
        expected_s_zeros = expected_zeros - 1
        errors = []
        if actual_poles != expected_poles:
            errors.append(f"Poles: expected {expected_poles} (1 integrator + {expected_poles - 1} poles), got {actual_poles} (1 integrator + {len(self.pole_entries)} poles)")
        if actual_zeros != expected_s_zeros:
            errors.append(f"Zeros: expected {expected_s_zeros} in s-domain ({expected_zeros}Z - 1 from bilinear transform), got {actual_zeros}")
        if errors:
            messagebox.showerror("Pole/Zero Count Mismatch",
                f"Filter type {filter_type_str} requires:\n" + "\n".join(errors))
            return False
        return True

    def run_compensator(self):
        """Run the nPnZ_compensator.py script"""
        try:
            if not self.validate_pole_zero_count():
                return

            # First, save the current config to JSON file using filter name
            config = self.collect_config()
            
            # Get the directory where the script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Use filter name for the filename
            filter_name = self.name_var.get()
            config_filename = f"{filter_name}.json"
            config_filepath = os.path.join(script_dir, config_filename)
            
            with open(config_filepath, 'w') as f:
                json.dump(config, f, indent=4)
            
            # Check if nPnZ_compensator.py exists
            compensator_script = os.path.join(script_dir, "nPnZ_compensator.py")
            if not os.path.exists(compensator_script):
                messagebox.showwarning("Warning", 
                    "nPnZ_compensator.py not found in current directory!\n\n"
                    f"Configuration saved to {config_filepath}\n"
                    "Please ensure nPnZ_compensator.py is in the same directory.")
                return
            
            # Use sys.executable for cross-platform compatibility (macOS/Linux/Windows)
            # On macOS, 'python' may not exist or point to Python 2; sys.executable
            # always points to the exact interpreter running this GUI script.
            python_exe = sys.executable
            result = subprocess.run(
                [python_exe, "nPnZ_compensator.py", config_filename],
                capture_output=True,
                text=True,
                cwd=script_dir
            )
            
            # Show output
            output_window = tk.Toplevel(self.root)
            output_window.title("Coefficient Generation Output")
            output_window.geometry("700x500")
            
            output_text = scrolledtext.ScrolledText(output_window, wrap=tk.WORD)
            output_text.pack(expand=True, fill='both', padx=10, pady=10)
            
            output_text.insert(tk.END, f"Configuration saved to: {config_filepath}\n")
            output_text.insert(tk.END, f"Running: {python_exe} nPnZ_compensator.py {config_filename}\n\n")
            output_text.insert(tk.END, "=== STDOUT ===\n")
            output_text.insert(tk.END, result.stdout)
            output_text.insert(tk.END, "\n=== STDERR ===\n")
            output_text.insert(tk.END, result.stderr)
            
            if result.returncode == 0:
                output_text.insert(tk.END, "\n=== Execution completed successfully ===\n")
                    
            else:
                output_text.insert(tk.END, f"\n=== Execution failed with return code {result.returncode} ===\n")
            
            output_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate coefficients:\n{str(e)}")
            


def main(json_config_file = None):
    root = tk.Tk()
    app = FilterConfigGUI(root, default_file=json_config_file)
    root.mainloop()


if __name__ == "__main__":
    try :
        sys.argv[1]
        main(sys.argv[1])
    except IndexError:
        main()