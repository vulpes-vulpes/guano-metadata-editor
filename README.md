# GUANO Metadata Editor

A user-friendly GUI application for reading and editing GUANO metadata in WAV files containing bat vocalizations. Available as standalone executables for macOS, Windows, and Linux - no Python installation required!

## Features

- **Read metadata** from directories of WAV files with GUANO metadata
- **Smart summarization** - differentiates between:
  - Fields identical across all files (e.g., site name, equipment)
  - Fields that differ per file (e.g., timestamp, filename)
- **Safe editing** of common metadata fields across multiple files
- **Automatic backups** before any modifications
- **WAV chunk preservation** - maintains all metadata chunks (LIST, INFO, etc.)
- **Clear warnings** and multi-step confirmations before changes
- **User-friendly GUI** - no command-line experience needed
- **Cross-platform** - works on macOS, Windows, and Linux

## Quick Start

### Download Pre-Built Application (Recommended)

**No Python installation required!**

1. Go to the [Releases page](https://github.com/vulpes-vulpes/guano-metadata-editor/releases)
2. Download the latest version for your platform:
   - **macOS**: `GUANO-Metadata-Editor-macOS.dmg`
   - **Windows**: `GUANO-Metadata-Editor-Windows.zip`
   - **Linux**: `GUANO-Metadata-Editor-Linux.tar.gz`
3. Install and run:
   - **macOS**: Open DMG, drag to Applications, right-click and select "Open" (first launch only)
   - **Windows**: Extract ZIP, run the .exe (click "More info" → "Run anyway" if prompted)
   - **Linux**: Extract tar.gz, make executable with `chmod +x`, then run

See [USER_GUIDE.md](USER_GUIDE.md) for detailed instructions.

### For Developers (Running from Source)

If you want to contribute or modify the code:

**Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/guano-metadata-editor.git
   cd guano-metadata-editor
   ```
## How to Use
1. **Launch the Application**: Double-click the app (or run `python guano_gui.py` if using source)
2. **Select Directory**: Click "Browse" to select a folder containing WAV files with GUANO metadata
3. **Load Files**: Click "Load Files" to scan and read metadata from all WAV files
4. **View Summary**: 
   - **Common tab**: Fields identical across all files (e.g., site name, equipment)
   - **Variable tab**: Fields that differ per file (e.g., timestamp, filename) with file-by-file details
5. **Edit Common Fields**: 
   - Click "Edit Common Fields" to modify fields shared across all files
   - Make your changes in the dialog
   - Review the confirmation showing which files will be affected
6. **Create Backup**: Always recommended - creates timestamped copies before editing
7. **Apply Changes**: Confirm to write the updated metadata (all WAV chunks are preserved)

See [QUICK_START.md](QUICK_START.md) for a visual guide or [USER_GUIDE.md](USER_GUIDE.md) for comprehensive documentation.data from all WAV files
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
WAV chunk preservation** - all chunks (LIST, INFO, etc.) maintained during edits
- **Multi-step confirmation** before any file modifications
- **Clear error messages** if issues occur
- **Read-only display** of variable fields to prevent accidental mismatches
- **Detailed logging** of all operations in the activity log

## Technical Details

- **Language**: Python 3.7+
- **GUI Framework**: tkinter
- **Dependencies**: guano>=1.0.12
- **Distribution**: PyInstaller standalone executables
- **Architecture**: Modular design with separate GUI, metadata manager, and WAV chunk preserver

### File Structure

- `guano_gui.py` - Main GUI application
- `guano_metadata_manager.py` - Core metadata reading/writing logic
- `About GUANO

This application works with the [GUANO metadata format](http://guano-md.org/), an open standard for bat acoustic recordings. It uses the [guano-py](https://github.com/riggsd/guano-py) library for reading and writing metadata.

## License

This software is provided as-is for working with GUANO metadata in bat acoustic research. The GUANO format and guano-py library are separate open-source projects with their own licenses.

## Troubleshooting

### Application won't open (macOS)
- Right-click the app and select "Open" (security requirement for unsigned apps)
- Click "Open" in the dialog that appears

### Windows Defender warning
- Click "More info" → "Run anyway" (normal for unsigned open-source software)

### No metadata found
- Ensure your WAV files contain GUANO metadata
- Check that files are not corrupted
- Verify files have read permissions

### Cannot write metadata
- Check write permissions on the directory
- Ensure files are not open in another program
- Create a backup before attempting edits

### For Source Installation Issues
See [USER_GUIDE.md](USER_GUIDE.md) for developer troubleshooting.

## Contributing

Contributions are welcome! This is a utility tool for bat acoustic research.

1. Fork the repository
2. Create a feature branch
3. Test thoroughly with your bat acoustic data
4. Submit a pull request

See [CHANGELOG.md](CHANGELOG.md) for version history.
### Python crashes on launch (macOS)
- This is a tkinter compatibility issue with Apple's Python
- **Quick fix**: Install Python from python.org (includes compatible Tk)
- **See**: [TKINTER_FIX.md](TKINTER_FIX.md) for detailed solutions
- **Alternative**: Use command-line interface via `example_usage.py`

## Contributing

This is a utility tool for bat acoustic research. Suggestions and improvements are welcome!
