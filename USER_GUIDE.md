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
- Standardize variable fields to common values across your dataset
- Add new metadata fields (standard GUANO or custom)
- Queue multiple changes and apply them all in a single pass
- Monitor progress with integrated progress tracking

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
- Action buttons (Edit Common Fields, Edit Variable Fields, Add Field)
- Pending Changes queue panel
- Activity log at the bottom

### Your First Session

1. **Select a directory**: Click "Browse..." and navigate to a folder containing WAV files with GUANO metadata
2. **Load files**: Click "Load Files" to scan the directory (progress bar shows loading status)
3. **Review metadata**: Check the "Common Fields" and "Variable Fields" tabs
4. **Queue changes**: Use "Edit Common Fields", "Edit Variable Fields", or "Add Field" to queue your changes
5. **Review pending changes**: Check the "Pending Changes" panel at the bottom
6. **Apply all changes**: Click "▶ Apply All Changes" to update all files in one pass

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

- **Edit Common Fields**: Opens a dialog to modify fields shared across all files
  - Change field values in text boxes
  - Check "Delete" checkbox to remove fields from all files
  - Changes are queued, not immediately applied
- **Edit Variable Fields**: Opens a dialog to standardize fields that vary across files
  - Enter new values to standardize across all files
  - Check "Delete field" checkbox to remove variable fields from all files
  - Converts them to common fields or deletes them
- **Add Field**: Opens a dialog to add new metadata fields (standard GUANO or custom) to all files

### Pending Changes Panel

Shows all queued changes before applying them:
- **[C]** - Common field edit (or delete)
- **[V→C]** - Variable field standardization (variable → common, or delete)
- **[NEW]** - New field addition
- Fields marked for deletion show with `<delete>` as the value
- **Remove Selected**: Remove a specific queued change
- **Clear All**: Clear all pending changes
- **▶ Apply All Changes**: Apply all pending changes in a single pass (button is disabled when queue is empty)

### Activity Log

Shows a running log of all operations:
- Files loaded (including count of filtered ._ files)
- Changes queued
- Updates applied
- Progress status
- Errors or warnings

## Common Workflows

### Workflow 1: Reviewing Metadata

**Goal**: Check what metadata exists in your recordings

1. Load files from directory (with progress tracking)
2. Review "Common Fields" tab to see shared metadata
3. Review "Variable Fields" tab to see what varies (expand to see file-by-file values)
4. Note any missing or incorrect fields

### Workflow 2: Adding Site Information

**Goal**: Add location details to all recordings from a session

1. Load files
2. Click "Edit Common Fields"
3. Add or modify fields like:
   - `Site Name`: "Forest Preserve Site A"
   - `Loc Position`: "42.123456 -71.234567"
   - `Loc Elevation`: "245"
4. Click "Add to Queue" - changes appear in Pending Changes panel
5. Review queued changes at the bottom of the window
6. Click "▶ Apply All Changes" to update all files
7. Confirm the operation in the dialog

### Workflow 3: Correcting Species Identification

**Goal**: Update species identification across multiple files

1. Load files from session
2. Click "Edit Common Fields"
3. Update `Species Manual ID` field
4. Optionally add a `Note` explaining the correction
5. Click "Add to Queue"
6. Review in Pending Changes panel
7. Click "▶ Apply All Changes"

### Workflow 4: Batch Metadata Updates (NEW - Most Efficient!)

**Goal**: Update multiple types of changes in a single pass through files

1. Load files
2. Click "Edit Common Fields" and queue changes to existing fields
3. Click "Edit Variable Fields" to standardize varying fields
4. Click "Add Field" to add new metadata fields
5. Review ALL queued changes in the Pending Changes panel:
   - Common field edits show as [C]
   - Variable standardizations show as [V→C]
   - New fields show as [NEW]
6. Click "▶ Apply All Changes" once to apply everything
7. All changes are applied in a **single pass** - much faster than processing files multiple times!

### Workflow 5: Removing Incorrect Metadata

**Goal**: Delete a field that was incorrectly set

1. Load files
2. Click "Edit Common Fields" (or "Edit Variable Fields" for variable fields)
3. Find the field you want to remove
4. **Check the "Delete" checkbox** next to that field (the entry will be disabled)
5. Click "Add to Queue"
6. Review in Pending Changes panel - deleted fields show with `<delete>` as the value
7. Click "▶ Apply All Changes"
8. The field will be deleted from all files

**Note**: You can also delete a field by clearing its value completely (leaving it blank), but using the Delete checkbox makes your intent explicit.

### Workflow 6: Standardizing Variable Fields

**Goal**: Convert fields that vary across files to a single common value

1. Load files
2. Review "Variable Fields" tab to see which fields differ
3. Click "Edit Variable Fields"
4. For each field you want to standardize:
   - **To set a common value**: Enter the new value in the field
   - **To delete the field**: Check the "Delete field" checkbox
5. Click "Add to Queue"
6. The changes show as [V→C] in Pending Changes
7. Click "▶ Apply All Changes" to standardize or delete across all files

**Example use cases**:
- Standardize inconsistent site names to a single value
- Remove fields that were incorrectly set with different values
- Update equipment information that varied due to a bug

## Safety Features

### 1. Pending Changes Queue

All changes are queued before being applied:
- Review all pending changes before applying
- See exactly what will change with clear labels ([C], [V→C], [NEW])
- Remove or modify queued changes before applying
- Apply button is disabled until you queue changes
- All changes applied in a single, atomic operation

### 2. Multi-Step Confirmation

Before any files are modified:
- Protected fields (like GUANO|Version) require extra confirmation
- Final "Apply All Changes" dialog shows:
  - Complete list of all pending changes
  - Number of files affected
  - Warning about file modification
  - Strong recommendation to maintain your own backups

### 3. Variable Fields Protection

Variable fields are handled safely:
- Can only be standardized through "Edit Variable Fields" dialog
- Clear warning that this will overwrite different values
- Prevents accidental data loss from bulk editing

### 4. Validation and Error Handling

The application checks:
- Directory exists and is readable
- Files are valid WAV files
- GUANO metadata is present
- Write permissions before modifications
- File integrity after updates

### 5. Progress Tracking

Integrated progress reporting:
- Progress bar during file loading
- Progress bar during updates
- File count tracking
- Real-time operation status
- Estimated time for large datasets

### 6. Activity Logging

All operations are logged:
- Files loaded (including filtered ._ files on macOS)
- Errors encountered
- Changes queued and applied
- Operation completion status

The log persists during your session for reference.

### 7. Automatic File Filtering

macOS metadata files are automatically excluded:
- Files starting with `._` are filtered during loading
- These are AppleDouble metadata files created by macOS
- Prevents "Invalid WAV" errors
- Filtered file count is reported in the log

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

### Problem: Changes don't appear in pending queue

**Cause**: Need to click "Add to Queue" button in the dialog

**Solution**: After editing fields, click "Add to Queue" (not "Cancel"). The dialog will close and changes will appear in the Pending Changes panel.

### Problem: Apply All Changes button is grayed out

**Cause**: No changes are queued

**Solution**: Queue at least one change using Edit Common Fields, Edit Variable Fields, or Add Field. The button will become active when changes are pending.

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

1. **Maintain your own backups**
   - Always work on a copy of your data, not your only copy
   - Use version control or backup systems appropriate for your workflow
   - Consider working on a test subset first for large datasets
   - Storage is cheap, data is precious

2. **Review the data**
   - Check Common Fields to see what's shared across files
   - Expand Variable Fields to understand variation
   - Verify file count matches expectations

3. **Use the pending changes queue effectively**
   - Queue all related changes together
   - Review the complete list before applying
   - Apply everything in one pass - much faster than multiple operations

### During Editing

1. **Use clear, consistent naming**
   - Site names: Use consistent format (e.g., "ForestPreserve_SiteA")
   - Species: Use standard abbreviations or full names
   - Notes: Be descriptive but concise

2. **Review pending changes carefully**
   - Check the Pending Changes panel before applying
   - Verify field names and values are correct
   - Use "Remove Selected" to fix mistakes before applying
   - The [C], [V→C], and [NEW] labels help identify change types

3. **Monitor progress**
   - Watch the progress bar during operations
   - Check the Activity Log for completion status
   - Note any errors or warnings reported

### After Editing

1. **Verify changes**
   - The display automatically refreshes after applying changes
   - Load files again to verify updates were written correctly
   - Open a few files in your analysis software to confirm

2. **Document changes**
   - Review the Activity Log for a record of what was done
   - Keep a separate log of major metadata updates
   - Note date, changes made, and reason for future reference

3. **Test with analysis tools**
   - Verify updated metadata appears in Kaleidoscope, SonoBat, etc.
   - Ensure changes are compatible with your workflow

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

For advanced users who need to automate metadata operations, you can use the core module directly:

```python
from guano_metadata_manager import GuanoMetadataManager

manager = GuanoMetadataManager()

# Load files with progress callback
def progress(current, total):
    print(f"Loading: {current}/{total}")

count, errors = manager.load_directory("/path/to/files", progress_callback=progress)

# Get common fields
common = manager.get_common_fields()

# Update fields across all files
updates = {'Site Name': 'New Site Name', 'Species Manual ID': 'MYLU'}
updated, errors = manager.update_common_fields(updates, progress_callback=progress)
print(f"Updated {updated} files")
```

**Note**: The programmatic API applies changes immediately. The pending changes queue is a GUI-only feature for user convenience.

See `example_usage.py` for more examples.

### Batch Processing

For processing multiple directories efficiently:

1. **Process each directory separately** using the GUI
2. **Use the pending changes queue** to batch all edits together
3. **Apply consistent metadata** across sessions by queuing the same field updates
4. **Monitor the Activity Log** to track progress and any issues
5. **For very large datasets** (10,000+ files):
   - The app uses parallel processing and memory optimization
   - Progress bars show real-time status
   - Typically processes 100-1000 files per second depending on system

**Pro tip**: Queue common field edits, variable field standardizations, and new field additions all at once for maximum efficiency!

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
