<div>
<img src="./_source_docs/microchip-logo2.png" width="200"/>
</div>

The compensator script can also be used standalone from the command line without this GUI.
[Link to standalone command-line User&#39;s Guide](./README.md)

# *Filter Configuration Generator GUI - Documentation*

## *Overview*

The Filter Configuration Generator GUI is a Python-based graphical user interface built with Tkinter that allows users to create, edit, and manage digital filter configuration files for compensator systems. The tool is specifically designed for nPnZ (n-Pole n-Zero) filter design and interfaces with the `nPnZ_compensator.py` script to generate filter coefficients.

## *Requirements*

### *System Requirements*

- Python 3.6 or higher
- Operating System: Windows, Linux, or macOS

### *Python Dependencies*

- `tkinter` (usually included with Python)
- `json` (standard library)
- `subprocess` (standard library)
- `os` (standard library)
- `datetime` (standard library)

### *Additional Files*

- `nPnZ_compensator.py` - The coefficient generation script (must be in the same directory)

## *Installation*

1. Ensure Python 3.6+ is installed on your system
2. Download `filter_config_gui.py` to your working directory
3. Place `nPnZ_compensator.py` in the same directory
4. Run the GUI without parameter (it will load default configuration):

   ```bash
   python filter_config_gui.py
   ```

   or run the GUI with a custom configuration file as parameter to load default configuration from an existing file:
   ```bash
   python filter_config_gui.py ./_config/filter_config_DPSK4_BUCK_Q31.json
   ```

## *User Interface Layout*

The GUI is organized into three main sections:

### 1. General Information (Left Panel)

Contains metadata and identification fields for the filter:

- **Filter Name**: Unique identifier for your filter configuration

  - This name is used to auto-generate other filenames
  - Example: `dpsk4_buck_float_vcomp`
- **H File Name (auto)**: Read-only field, automatically generated from Filter Name

  - Format: PascalCase with underscores + `.h` extension
  - Example: `Dpsk4_Buck_Float_Vcomp.h`
- **Bode Plot Output**: Output filename for the Bode plot

  - Auto-generated from Filter Name but remains editable
  - Format: PascalCase with underscores + `_Bode_Plot.pdf`
  - Example: `Dpsk4_Buck_Float_Vcomp_Bode_Plot.pdf`
- **Filter Type**: Dropdown selection for filter topology

  - Options: 1P1Z, 2P2Z, 3P3Z, 4P4Z, 5P5Z, 6P6Z
  - Default: 3P3Z
- **Author**: Name and identifier of the filter designer

  - Example: `Anthony PELE - M24683`
- **Description**: Multi-line text field for filter documentation

  - Describe the purpose and application of the filter

**Auto-generated fields (not shown in UI):**

- Version: Always set to "1.0.0"
- Company: Always set to "Microchip Technology Inc."
- Date: Automatically set to current date (YYYY-MM-DD format)

### 2. Filter Parameters (Right Panel)

Technical parameters for the filter design and Bode plot generation:

- **Bode Plot Min Freq (10^N)**: Minimum frequency for Bode plot as power of 10

  - Range: -10 to 10
  - Default: 0 (represents 10^0 = 1 Hz)
- **Bode Plot Max Freq (10^N)**: Maximum frequency for Bode plot as power of 10

  - Range: -10 to 10
  - Default: 6 (represents 10^6 = 1 MHz)
- **Bode Plot Nb Points**: Number of frequency points for Bode plot

  - Default: 1000
  - Higher values provide smoother plots but increase computation time
- **Sampling Frequency (Hz)**: Digital system sampling frequency

  - Units: Hertz (Hz)
  - Default: 500000 (500 kHz)
  - Must match your target system's sampling frequency
- **Digital Filter Time Delay (s)**: Estimated computational delay

  - Units: Seconds
  - Default: 700e-9 (700 nanoseconds)
  - Accounts for digital processing latency
- **ADC Trigger Point Delay (s)**: ADC sampling timing offset

  - Units: Seconds
  - Default: 1e-6 (1 microsecond)
  - Accounts for ADC conversion time and trigger timing
- **Coefficient Format**: Number format for filter coefficients

  - Options:
    - **float**: Floating-point representation (32-bit or 64-bit)
    - **Q15**: Fixed-point Q15 format (16-bit signed, 1 sign + 15 fractional bits)
    - **Q31**: Fixed-point Q31 format (32-bit signed, 1 sign + 31 fractional bits)
  - Default: float
- **Plant Data File (optional)**: Path to a tab-delimited text file containing plant (power stage) Bode data (frequency, gain, phase)

  - Use the "Browse..." button to select a file, or type the path manually
  - When a plant file is provided, the Bode plot output will include an overlay of the open-loop response (plant + compensator) alongside the compensator-only plots
  - When left empty, only the compensator Bode plot is generated
  - When loading a JSON configuration that already contains a `"plant_data_file"` key, the field is automatically populated with that path
  - The plant data file is expected to be a tab-separated text file with columns: Frequency (Hz), Gain (dB), Phase (degrees), with a header row that is skipped during parsing
  - Default: empty (no plant data)

### 3. Frequencies Configuration (Bottom Panel)

Defines the pole and zero locations for the filter transfer function:

#### Integrator Pole

- Single pole at low frequency to provide DC gain
- Fixed to one entry (cannot add/remove)
- Frequency in Hz
- Default: 1200 Hz

#### Zeros

- Add multiple zeros to shape the frequency response
- Each zero entry includes:
  - Frequency (Hz)
  - Type: Automatically set to "Zero"
- Use "+ Add Zero" button to add more zeros
- Use "Remove" button to delete individual zeros
- Default: Two zeros at 2551 Hz and 3827 Hz

#### Poles

- Add multiple poles to stabilize the filter
- Each pole entry includes:
  - Frequency (Hz)
  - Type: Automatically set to "Pole"
- Use "+ Add Pole" button to add more poles
- Use "Remove" button to delete individual poles
- Default: Two poles at 80000 Hz and 170000 Hz

## Action Buttons

### 📂 Load JSON

- Opens a file browser to select an existing JSON configuration file
- Default directory: Same folder as the Python script
- Loads all parameters from the selected file into the GUI
- Validates JSON structure before loading

### ⚙️ Generate Coefficients

Performs the following actions:

1. Collects all current parameters from the GUI
2. Generates JSON configuration file with format: `<filter_name>.json`
3. Saves JSON file in the same directory as the Python script
4. Executes: `python nPnZ_compensator.py <filter_name>.json`
5. Displays output in a popup window showing:
   - Configuration file path
   - Command executed
   - Standard output (STDOUT)
   - Standard error (STDERR)
   - Execution status

## *File Format*

### *JSON Configuration Structure*

```json
{
    "name": "filter_name",
    "h_file_name": "Filter_Name.h",
    "bode_plot_output_file_name": "Filter_Name_Bode_Plot.pdf",
    "type": "3P3Z",
    "version": "1.0.0",
    "description": "Description of the filter",
    "author": "Author Name",
    "company": "Microchip Technology Inc.",
    "date": "2025-11-26",
    "plant_data_file": "PLANT.txt",
    "filter_parameters": {
        "BODE_PLOT_MIN_FREQ_10powerN": 0,
        "BODE_PLOT_MAX_FREQ_10powerN": 6,
        "BODE_PLOT_NB_POINTS": 1000,
        "SAMPLING_FREQUENCY_HZ": 500000,
        "ESTIMATED_DIGITAL_FILTER_TIME_DELAY_IN_S": 7e-07,
        "ESTIMATED_ADC_TRIGGER_POINT_DELAY": 1e-06,
        "coefficient_format": "float",
        "frequencies_Hz": {
            "Integrator_pole": [
                {
                    "frequency": 1200,
                    "type": "Integrator"
                }
            ],
            "Zeros": [
                {
                    "frequency": 2551,
                    "type": "Zero"
                },
                {
                    "frequency": 3827,
                    "type": "Zero"
                }
            ],
            "Poles": [
                {
                    "frequency": 80000,
                    "type": "Pole"
                },
                {
                    "frequency": 170000,
                    "type": "Pole"
                }
            ]
        }
    }
}
```

## *Workflow Examples*

### *Example 1: Creating a New Filter Configuration*

1. Launch the GUI: `python filter_config_gui.py`
2. Enter general information:
   - Filter Name: `buck_converter_vmode`
   - Author: `John Doe - M12345`
   - Description: `Voltage mode buck converter compensator`
3. Set filter type: `3P3Z`
4. Configure filter parameters:
   - Sampling Frequency: 250000 Hz (250 kHz)
   - Coefficient Format: `Q15`
5. Set frequencies:
   - Integrator Pole: 800 Hz
   - Zeros: 3000 Hz, 5000 Hz
   - Poles: 50000 Hz, 100000 Hz
6. Click "⚙️ Generate Coefficients"
7. Review output in popup window
8. Files generated:
   - `buck_converter_vmode.json`
   - `Buck_Converter_Vmode.h` (generated by nPnZ_compensator.py)
   - `Buck_Converter_Vmode_Bode_Plot.pdf` (generated by nPnZ_compensator.py)

### *Example 2: Modifying an Existing Configuration*

1. Launch the GUI
2. Click "📂 Load JSON"
3. Select your existing configuration file
4. Modify desired parameters
5. Click "⚙️ Generate Coefficients" to regenerate

### *Example 3: Comparing Different Coefficient Formats*

1. Create base configuration with `float` format
2. Generate coefficients
3. Change Coefficient Format to `Q15`
4. Rename Filter Name to append `_q15`
5. Generate coefficients
6. Compare the output files

## *Tips and Best Practices*

### Filter Design Guidelines

1. **Pole-Zero Placement**:

   - Place zeros below the desired crossover frequency to boost gain
   - Place poles above crossover frequency to attenuate high-frequency noise
   - Integrator pole provides DC gain and steady-state accuracy
2. **Sampling Frequency**:

   - Choose at least 10x higher than the highest pole/zero frequency
   - Higher sampling rates provide better digital approximation
3. **Coefficient Format Selection**:

   - Use `float` for initial design and simulation
   - Use `Q15` for 16-bit microcontrollers (limited dynamic range)
   - Use `Q31` for 32-bit microcontrollers (better precision)
4. **Naming Conventions**:

   - Use descriptive filter names: `<application>_<topology>_<version>`
   - Example: `buck_vmode_rev2`, `boost_cmode_final`

### Troubleshooting

**Issue**: "nPnZ_compensator.py not found" warning

- **Solution**: Ensure `nPnZ_compensator.py` is in the same directory as `filter_config_gui.py`

**Issue**: GUI window too small on high-DPI displays

- **Solution**: Adjust window size in code or use OS scaling settings

**Issue**: Cannot load JSON file

- **Solution**: Verify JSON syntax is valid using a JSON validator

**Issue**: Generated coefficients overflow in Q15 format

- **Solution**:
  - Reduce gain by adjusting pole/zero frequencies
  - Switch to Q31 format for higher dynamic range
  - Scale the input/output signals in your application

## *Advanced Usage*

### *Batch Processing*

Create multiple configurations programmatically:

```python
import json

base_config = {
    # ... base configuration ...
}

for freq in [50000, 100000, 150000]:
    config = base_config.copy()
    config["name"] = f"filter_{freq}Hz"
    config["filter_parameters"]["SAMPLING_FREQUENCY_HZ"] = freq
  
    with open(f"filter_{freq}Hz.json", 'w') as f:
        json.dump(config, f, indent=4)
```

### *Integration with Other Tools*

The JSON output can be used with:

- MATLAB/Octave for analysis
- Python control systems libraries (scipy.signal)
- Custom visualization tools
- Automated testing frameworks

## *Support and Contact*

For issues, questions, or feature requests related to the GUI, please contact your system administrator or the tool maintainer.

For issues with the `nPnZ_compensator.py` script, refer to its separate documentation.

## *Version History*

- **v2.0** (2026-10-14): Bug fixes and improvements
  - **Bug fixes (nPnZ_compensator.py):**
    - Fixed missing parentheses on `Harmonize_DSP_Coefficients_Scaling_Q31()` and `_Q15()` method calls (were no-ops)
    - Fixed Q15 header output incorrectly using Q31 bit-shift scaling values instead of Q15 values
    - Fixed `Fs` variable scope issue in `Update_filter_from_s_polynoms_update()` (now uses `self.Fs`)
    - Fixed bare `except` clause narrowed to `except KeyError` to avoid masking unrelated errors
  - **Improvements (filter_config_gui.py):**
    - Added pole/zero count validation against selected filter type (e.g. 3P3Z expects 3 poles and 2 zeros in s-domain)
    - Added Plant Data File selector field with Browse button for optional plant Bode data overlay

- **v1.0** (2025-11-26): Initial release
  - Basic filter configuration GUI
  - Support for 1P1Z to 6P6Z filters
  - Float, Q15, and Q31 coefficient formats
  - Auto-generation of filenames
  - Direct integration with nPnZ_compensator.py

## *License*

This tool is provided for use within Microchip Technology Inc. projects. Refer to your organization's software licensing policy for usage terms.

<div>
<img src="./_source_docs/microchip-logo2.png" width="200"/>
</div>
