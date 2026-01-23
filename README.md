# GUANO Metadata Utility

A robust Python application with GUI for reading and editing GUANO metadata in WAV files containing bat vocalizations.

## Features

- **Read metadata** from directories of WAV files with GUANO metadata
- **Smart summarization** - differentiates between:
  - Fields identical across all files (e.g., site name, equipment)
  - Fields that differ per file (e.g., timestamp, filename)
- **Safe editing** of common metadata fields
- **Backup creation** before any modifications
- **Clear warnings** and confirmations before changes
- **User-friendly GUI** for easy operation

## Installation

### Requirements
- Python 3.7 or higher
- tkinter (usually included with Python)

### Setup

1. Clone or download this repository
2. Install the required Python package:

```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

```bash
python guano_gui.py
```
**⚠️ macOS Compatibility Note:** If Python crashes on launch with a Tk error, see [TKINTER_FIX.md](TKINTER_FIX.md) for solutions. The quickest fix is installing Python from python.org instead of using Apple's default Python.
### How to Use

1. **Select Directory**: Click "Browse" to select a folder containing WAV files with GUANO metadata
2. **Load Files**: Click "Load Files" to scan and read metadata from all WAV files
3. **View Summary**: 
   - Common fields (identical across all files) appear in the top section
   - Variable fields (differ per file) appear in the bottom section with file-by-file details
4. **Edit Common Fields**: 
   - Click "Edit Common Fields" to modify fields shared across all files
   - Make your changes in the dialog
   - Review the confirmation showing which files will be affected
5. **Create Backup**: Always recommended - creates timestamped copies of all files before editing
6. **Apply Changes**: Confirm to write the updated metadata

## Safety Features

- **Automatic validation** of selected directory and files
- **Backup creation** with timestamped folder names
- **Multi-step confirmation** before any file modifications
- **Clear error messages** if issues occur
- **Read-only display** of variable fields to prevent accidental mismatches
- **Detailed logging** of all operations

## GUANO Format

This utility works with the [GUANO metadata format](http://guano-md.org/), an open standard for bat acoustic recordings. It uses the [guano-py](https://github.com/riggsd/guano-py) library for reading and writing metadata.

## File Structure

- `guano_gui.py` - Main GUI application
- `guano_metadata_manager.py` - Core metadata reading/writing logic
- `requirements.txt` - Python dependencies

## License

This software is provided as-is for working with GUANO metadata. The GUANO format and guano-py library are separate open-source projects with their own licenses.

## Troubleshooting

### No metadata found
- Ensure your WAV files contain GUANO metadata
- Check that files are not corrupted
- Verify files have read permissions

### Cannot write metadata
- Check write permissions on the directory
- Ensure files are not open in another program
- Create a backup before attempting edits

### Import errors
- Verify guano package is installed: `pip list | grep guano`
- Try reinstalling: `pip install --upgrade guano`

### Python crashes on launch (macOS)
- This is a tkinter compatibility issue with Apple's Python
- **Quick fix**: Install Python from python.org (includes compatible Tk)
- **See**: [TKINTER_FIX.md](TKINTER_FIX.md) for detailed solutions
- **Alternative**: Use command-line interface via `example_usage.py`

## Contributing

This is a utility tool for bat acoustic research. Suggestions and improvements are welcome!
