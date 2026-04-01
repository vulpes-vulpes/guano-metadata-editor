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

- **Read GUANO metadata from WAV files:** Quickly read GUANO from all files in a directory (including subdirectories)
- **Differentiate "common" and "variable" fields:** Categorize GUANO fields as having a common value across all loaded files, or variable values across files
- **Edit common fields:** Edit or delete fields shared across all files
- **Edit/standardize variable fields:** Replace varying field values with a single common value across all files
- **Add new fields:** Add both standard GUANO fields and custom fields in a safe way compatible with the GUANO specification
- **Pending changes queue:** Queue multiple edits and apply them all in a single pass!
- **Monitor progress:** Integrated progress bar and file count tracking for all operations
- **Efficient for large datasets:** Parallel processing for speed and optimized memory usage for datasets with 10,000+ files
- **Cross-platform:** Works on macOS, Windows, and Linux

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

### Basic Workflow
1. **Launch the Application**: Double-click the app (or run `python guano_gui.py` if using source)
2. **Select Directory**: Click "Browse" to select a folder containing WAV files with GUANO metadata
3. **Load Files**: Click "Load Files" to scan and read metadata from all WAV files
   - Progress bar shows loading status
4. **View Metadata Summary**: 
   - **Common Fields tab**: Fields identical across all files (e.g., site name, equipment model)
   - **Variable Fields tab**: Fields that differ per file (e.g., timestamp, temperature) with expandable file-by-file details

### Editing Workflow (NEW in 1.2.0)
The editor uses a **pending changes queue** system that allows you to batch multiple edits and apply them all at once:

5. **Queue Your Changes**:
   - **Edit Common Fields**: Modify fields shared across all files → adds to queue
   - **Edit Variable Fields**: Standardize varying fields to a single value → adds to queue
   - **Add Field**: Add new metadata fields (standard GUANO or custom) → adds to queue
   
6. **Review Pending Changes**: 
   - All queued changes appear in the "Pending Changes" panel at the bottom
   - Changes are labeled: `[C]` (common), `[V→C]` (variable→common), `[NEW]` (new field)
   - Remove or clear changes if needed

7. **Apply All Changes**: 
   - Click the **▶ Apply All Changes** button (becomes active when changes are queued)
   - Review the confirmation dialog
   - All changes are applied in a **single pass** through all files
   - Progress bar shows update status


### Important Notes
- ⚠️ **Always maintain your own backups** before batch editing operations
- The tool modifies metadata within WAV files but preserves all audio and other data chunks
- Changes cannot be undone after applying - review pending changes carefully
- For safety, consider working on a copy of your data first

See [USER_GUIDE.md](USER_GUIDE.md) for comprehensive documentation with screenshots.

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