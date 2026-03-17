# GUANO Metadata Editor

An app to streamline editing GUANO metadata in bat acoustic monitoring files. GUANO is an open standard for storing contextual information relating to bat acoustic monitoring within the WAV files themselves.
Most bat monitoring equipment and software will generate GUANO, e.g. acoustic monitors saving the model number, serial number, timestamp, location, etc. into WAV files as they are created.
Additional context, such as site names, project names, or ownership, typically needs to be added manually during initial data processing. Having all of these data embedded in the files themselves means the context of the recording cannot be lost.

However, sometimes there may be mistakes in the metadata. For example, a typo while adding a value, or an inconsistent approach across a project.

This utility aims to help. It lets you quickly read the GUANO from a set of files, add new fields, and safely edit existing ones. If you make as many typos as I do, you'll find it helpful.

## Acknowledgements

- The [GUANO metadata format](http://guano-md.org/) was developed by [David Riggs](https://github.com/riggsd) and is a superb contribution to the field of bat acoustics.
- This package uses the [guano-py](https://github.com/riggsd/guano-py) library, also developed by [David Riggs](https://github.com/riggsd), for reading and writing metadata.
- This project was developed with extensive assistance from GitHub Copilot (https://github.com/features/copilot) for code generation and autocompletion.

## Features

- **Read existing GUANO metadata** from directories of WAV files with GUANO metadata
- **Add new GUANO metadata fields** - choose from standard GUANO fields or create custom namespaced fields
- **Smart summarization** - differentiates between:
  - Fields identical across all files (e.g., site name, equipment)
  - Fields that differ per file (e.g., timestamp, filename)
- **Safe editing** of common GUANO metadata fields across multiple files
- **Automatic backups** before any modifications
- **WAV chunk preservation** - maintains all other metadata chunks (LIST, INFO, etc.)
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
5. **Add New Fields** (NEW in 1.1.0):
   - Click "Add Field" to add a new metadata field to all loaded files
   - Choose from **Standard GUANO Fields** (23 spec-defined fields) or define a **Custom Field**
   - Helpful descriptions from the GUANO specification guide field selection
   - Automatic warnings if the field already exists
6. **Edit Common Fields**: 
   - Click "Edit Common Fields" to modify fields shared across all files
   - Make your changes in the dialog
   - Review the confirmation showing which files will be affected
7. **Create Backup**: Always recommended - creates timestamped copies before editing
8. **Apply Changes**: Confirm to write the updated metadata (all WAV chunks are preserved)

See [QUICK_START.md](QUICK_START.md) for a visual guide or [USER_GUIDE.md](USER_GUIDE.md) for comprehensive documentation.

## Technical Details

- **Language**: Python 3.7+
- **GUI Framework**: tkinter
- **Dependencies**: guano>=1.0.12
- **Distribution**: PyInstaller standalone executables
- **Architecture**: Modular design with separate GUI, metadata manager, and WAV chunk preserver

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

### Python crashes on launch (macOS)
- This is usually a tkinter compatibility issue with the system Python or a Homebrew Python without Tk support
- **Quick fix**: Install Python from python.org or install the matching Homebrew `python-tk` package
- **Alternative**: Use the command-line interface via `example_usage.py`

### For Source Installation Issues
See [USER_GUIDE.md](USER_GUIDE.md) for developer troubleshooting.

## Contributing

Contributions are welcome! This is a utility tool for bat acoustic research.

1. Fork the repository
2. Create a feature branch
3. Test thoroughly with your bat acoustic data
4. Submit a pull request

See [CHANGELOG.md](CHANGELOG.md) for version history.