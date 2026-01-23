# GUANO Metadata Editor - User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Understanding the Interface](#understanding-the-interface)
5. [Common Workflows](#common-workflows)
6. [Safety Features](#safety-features)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## Introduction

The GUANO Metadata Editor is a specialized tool for bat acoustic researchers working with WAV recordings that contain GUANO (Grand Unified Acoustic Notation Ontology) metadata. This application allows you to:

- Quickly scan and summarize metadata across multiple files
- Identify which metadata fields are consistent across recordings
- Edit metadata fields that are shared across all files
- Create backups before making any changes

## Installation

### For Most Users (Recommended)

**Download the pre-built application** - no Python installation required!

1. **Download** the latest release for your platform:
   - **macOS**: Download `GUANO-Metadata-Editor-macOS.dmg`
   - **Windows**: Download `GUANO-Metadata-Editor-Windows.zip`
   - **Linux**: Download `GUANO-Metadata-Editor-Linux.tar.gz`

2. **Install**:
   - **macOS**: Open the DMG and drag the app to Applications
   - **Windows**: Extract the ZIP and run the .exe
   - **Linux**: Extract the tar.gz and run the executable

3. **First Launch**:
   - **macOS**: Right-click the app and select "Open" (security requirement for first launch)
   - **Windows**: Windows Defender may show a warning - click "More info" → "Run anyway"
   - **Linux**: May need to make executable: `chmod +x "GUANO Metadata Editor"`

That's it! No Python, no dependencies, no terminal commands needed.

### For Developers (Running from Source)

If you want to contribute or modify the code:

1. **Requirements**:
   - Python 3.7 or higher
   - Git

2. **Setup**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/guano-metadata-editor.git
   cd guano-metadata-editor
   python3 -m venv guano_venv
   source guano_venv/bin/activate  # Windows: guano_venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run**:
   ```bash
   python guano_gui.py
   ```

See INSTALLATION.md for more developer details.

## Getting Started

### Launching the Application

**If using the standalone application:**
- **macOS**: Double-click the app in Applications
- **Windows**: Double-click the .exe
- **Linux**: Run the executable from the terminal or file manager

The main window will appear with several sections:
- Directory selection at the top
- Tabbed metadata display in the middle
- Action buttons
- Activity log at the bottom

### Your First Session

1. **Select a directory**: Click "Browse..." and navigate to a folder containing WAV files with GUANO metadata
2. **Load files**: Click "Load Files" to scan the directory
3. **Review metadata**: Check the "Common Fields" and "Variable Fields" tabs
4. **Create backup** (recommended): Click "Create Backup" before making any changes
5. **Edit if needed**: Click "Edit Common Fields" to modify shared metadata

## Understanding the Interface

### Directory Selection Section

- **Directory field**: Shows the current directory path
- **Browse button**: Opens a folder picker
- **Load Files button**: Scans for WAV files and reads metadata
- **File count**: Displays how many files were successfully loaded

### Metadata Display Tabs

#### Common Fields Tab

Shows metadata fields that have **identical values** across all loaded files. These are the fields you can edit together.

Examples of common fields:
- `Site Name` - Recording location
- `Species Manual ID` - Species identification
- `Loc Position` - GPS coordinates
- `Note` - General notes about the recording session
- `Make`, `Model` - Recording equipment information

#### Variable Fields Tab

Shows metadata fields that **differ between files**. These are displayed for reference but cannot be bulk edited (since changing them would make files inconsistent).

Examples of variable fields:
- `Timestamp` - Recording date/time (unique per file)
- `Length` - Duration of recording
- `Filename` - Original filename
- `Temperature Ext` - Environmental conditions at recording time

The variable fields are shown in a tree structure:
- Click the arrow next to a field name to expand and see values for each file
- This helps you understand variation across your dataset

### Action Buttons

- **Create Backup**: Creates timestamped copies of all loaded files
- **Edit Common Fields**: Opens a dialog to modify shared metadata
- **Refresh View**: Reloads the display (useful after external changes)

### Activity Log

Shows a running log of all operations:
- Files loaded
- Backups created
- Updates applied
- Errors or warnings

## Common Workflows

### Workflow 1: Reviewing Metadata

**Goal**: Check what metadata exists in your recordings

1. Load files from directory
2. Review "Common Fields" tab to see shared metadata
3. Review "Variable Fields" tab to see what varies
4. Note any missing or incorrect fields

### Workflow 2: Adding Site Information

**Goal**: Add location details to all recordings from a session

1. Load files
2. Create backup (recommended!)
3. Click "Edit Common Fields"
4. Add or modify fields like:
   - `Site Name`: "Forest Preserve Site A"
   - `Loc Position`: "42.123456 -71.234567"
   - `Loc Elevation`: "245"
5. Review changes in confirmation dialog
6. Click "Apply Changes"

### Workflow 3: Correcting Species Identification

**Goal**: Update species identification across multiple files

1. Load files from session
2. Create backup
3. Click "Edit Common Fields"
4. Update `Species Manual ID` field
5. Optionally add a `Note` explaining the correction
6. Apply changes

### Workflow 4: Batch Metadata Updates

**Goal**: Update multiple fields at once for consistency

1. Load files
2. Create backup
3. Edit Common Fields and update:
   - Recording equipment details
   - Site information
   - Processing notes
   - Species identification
4. Apply all changes together

### Workflow 5: Removing Incorrect Metadata

**Goal**: Delete a field that was incorrectly set

1. Load files
2. Create backup
3. Click "Edit Common Fields"
4. **Clear the value** of the field you want to remove (make it blank)
5. Apply changes
6. The field will be deleted from all files

## Safety Features

### 1. Multi-Step Confirmation

Before any files are modified, you'll see:
- A list of changes to be made
- Number of files affected
- A warning icon
- Recommendation to create backup

You must confirm twice:
- Once in the edit dialog
- Once in the final confirmation

### 2. Backup Creation

The "Create Backup" button:
- Creates a new folder named `GUANO_backup_YYYYMMDD_HHMMSS`
- Copies all loaded files to this folder
- Preserves original file timestamps and attributes
- Can be done multiple times (each with unique timestamp)

**Important**: Backups are created in the same parent directory as your files.

### 3. Read-Only Variable Fields

Fields that differ between files are:
- Displayed for reference only
- Cannot be bulk edited
- Prevents accidental inconsistency

### 4. Validation and Error Handling

The application checks:
- Directory exists and is readable
- Files are valid WAV files
- GUANO metadata is present
- Write permissions before modifications
- File integrity after updates

### 5. Activity Logging

All operations are logged:
- Files loaded
- Errors encountered
- Changes applied
- Backup locations

The log persists during your session for reference.

## Troubleshooting

### Problem: "No GUANO metadata found"

**Possible causes**:
- Files don't contain GUANO metadata (only regular WAV files)
- Files are from incompatible recording equipment
- Metadata may be in a different format (Anabat, SonoBat, etc.)

**Solutions**:
- Verify files were created by GUANO-compatible equipment
- Check if files need conversion from another format
- Use guano-py utility scripts to convert from other formats

### Problem: "Permission denied" errors

**Cause**: Application cannot write to files or directory

**Solutions**:
- Check file permissions (right-click → Get Info on macOS)
- Ensure files aren't open in another program
- Try running from a directory where you have write access
- On macOS, check Security & Privacy settings for Terminal/Python

### Problem: macOS won't open the app (security warning)

**Cause**: macOS Gatekeeper blocks unsigned applications

**Solution**:
1. Right-click (or Control-click) the app
2. Select "Open" from the menu
3. Click "Open" in the dialog that appears
4. The app will now open and won't show the warning again

### Problem: Windows Defender flags the application

**Cause**: Unsigned executables may trigger warnings

**Solution**:
1. Click "More info" in the warning dialog
2. Click "Run anyway"
3. This is normal for unsigned open-source software

### Problem: Changes don't appear after editing

**Cause**: View needs refreshing

**Solution**: Click "Refresh View" button after making changes

### Problem: Application won't launch  (for source installations)

**Running from source only** - Standalone app includes all dependencies.

**Cause**: guano-py package not installed

**Solution**:
```bash
# Activate virtual environment first
source guano_venv/bin/activate  # Windows: guano_venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
**Solutions**:
```bash
# Check Python version
python3 --version  # Should be 3.7+

# Reinstall dependencies
pip install -r requirements.txt

# Test tkinter
python3 -m tkinter
```

**Cause**: guano-py package not installed

**Solution**:
```bash
pip install guano
# or
pip3 install guano
```

## Best Practices

### Before Editing

1. **Always create a backup first**
   - Storage is cheap, data is precious
   - Backups are timestamped and easy to identify

2. **Review the data**
   - Check Common Fields to ensure you're editing what you intend
   - Verify file count matches expectations

3. **Make incremental changes**
   - Edit a few fields at a time
   - Test on a small subset before processing large batches

### During Editing

1. **Use clear, consistent naming**
   - Site names: Use consistent format
   - Species: Use standard abbreviations or full names
   - Notes: Be descriptive but concise

2. **Check your work**
   - Review the confirmation dialog carefully
   - Verify which fields are being changed

3. **Keep notes**
   - The Activity Log shows what was done
   - Consider taking screenshots of important changes

### After Editing

1. **Verify changes**
   - Use "Refresh View" to see updated metadata
   - Open a few files in your analysis software to confirm

2. **Keep backups**
   - Don't delete backup folders immediately
   - Store backups separately if editing valuable datasets

3. **Document changes**
   - Keep a separate log of major metadata updates
   - Note date, changes made, and reason

### Data Management

1. **Organize by recording session**
   - Keep files from the same night/site together
   - This makes common fields more meaningful

2. **Use consistent terminology**
   - Agree on field names and values with collaborators
   - Document your metadata schema

3. **Regular metadata audits**
   - Periodically check for missing or incorrect metadata
   - Ensure consistency across your dataset

## Advanced Tips

### Programmatic Access

For advanced users, you can use the core module directly:

```python
from guano_metadata_manager import GuanoMetadataManager

manager = GuanoMetadataManager()
count, errors = manager.load_directory("/path/to/files")

# Get common fields
common = manager.get_common_fields()

# Update fields
updates = {'Site Name': 'New Site Name'}
manager.update_common_fields(updates)
```

See `example_usage.py` for more examples.

### Batch Processing

For processing multiple directories:

1. Process each directory separately
2. Create backups for each
3. Apply consistent metadata across sessions
4. Use the Activity Log to track progress

### Integration with Analysis Pipelines

The GUANO format is supported by many analysis tools:
- **R**: guano-r package
- **Python**: guano-py package (used by this tool)
- **Kaleidoscope**: Directly reads GUANO metadata
- **SonoBat**: Can export to GUANO

Your metadata edits will be visible in these tools.

## Support and Resources

### GUANO Format Resources

- **Specification**: https://github.com/riggsd/guano-spec
- **Python Library**: https://guano-py.readthedocs.io/
- **Homepage**: http://guano-md.org/

### Getting Help

1. **Check the Activity Log**: Often shows why something failed
2. **Review this guide**: Most common issues are addressed
3. **Test with example files**: Verify the tool works with known-good files
4. **GUANO discussion list**: https://groups.google.com/d/forum/guano-md

## Appendix: Common GUANO Fields

Here are some commonly used GUANO metadata fields:

### Core Fields
- `GUANO|Version` - GUANO format version
- `Timestamp` - ISO 8601 timestamp of recording
- `Length` - Recording duration in seconds
- `Samplerate` - Audio sample rate
- `Species Manual ID` - User-identified species

### Equipment
- `Make` - Manufacturer
- `Model` - Device model
- `Firmware Version` - Device firmware

### Location
- `Loc Position` - GPS coordinates (lat lon)
- `Loc Elevation` - Elevation in meters
- `Site Name` - Location description

### Environmental
- `Temperature Ext` - External temperature (°C)
- `Humidity` - Relative humidity (%)

### Notes
- `Note` - General notes
- `Species Auto ID` - Automated identification result

Not all fields will be present in all files - it depends on your recording equipment and how it was configured.
