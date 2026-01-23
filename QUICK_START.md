# GUANO Metadata Editor - Quick Start

## ✅ Installation Complete!

Your GUANO Metadata Editor is ready to use. Here's what was created:

### Core Application Files
- ✅ `guano_gui.py` - Main GUI application
- ✅ `guano_metadata_manager.py` - Core metadata logic
- ✅ `requirements.txt` - Dependencies (guano package)

### Documentation
- ✅ `README.md` - Quick reference
- ✅ `USER_GUIDE.md` - Comprehensive documentation
- ✅ `PROJECT_STRUCTURE.md` - Technical details

### Utilities
- ✅ `setup.sh` - Automated setup script
- ✅ `verify_setup.py` - Installation verification
- ✅ `example_usage.py` - Code examples

### Dependencies Installed
- ✅ guano (version 1.0.16) - Successfully installed

---

## 🚀 Launch the Application

```bash
cd "/Users/toby.thorne/Code/GUANO Utility"
python3 guano_gui.py
```

### ⚠️ IMPORTANT: If Python Crashes on Launch

This is a known tkinter compatibility issue on macOS with Apple's default Python. You'll see:
```
macOS 26 (2602) or later required, have instead 16 (1602) !
zsh: abort
```

**Quick Fix:** Install Python from [python.org](https://www.python.org/downloads/) and use it instead:
```bash
# After installing Python from python.org:
/Library/Frameworks/Python.framework/Versions/3.11/bin/python3 guano_gui.py
```

**See [TKINTER_FIX.md](TKINTER_FIX.md) for complete solutions and alternatives.**

---

## 📖 First-Time Usage

### 1. Select Your Data
- Click **Browse** to select a folder with WAV files
- Click **Load Files** to read the metadata

### 2. Review Metadata
- **Common Fields** tab: Shows fields identical across all files
- **Variable Fields** tab: Shows fields that differ per file

### 3. Create a Backup (Important!)
- Click **Create Backup** before making any changes
- Backups are timestamped and saved in the same directory

### 4. Edit Common Fields
- Click **Edit Common Fields**
- Modify values or leave blank to delete a field
- Confirm changes to apply to all files

---

## ⚠️ Important Safety Features

### The application includes multiple safety layers:

1. **Read-Only Variable Fields**
   - Fields that differ between files cannot be edited
   - Prevents accidental data inconsistency

2. **Timestamped Backups**
   - Creates `GUANO_backup_YYYYMMDD_HHMMSS` folders
   - Complete copies before any modifications

3. **Multi-Step Confirmation**
   - Shows preview of changes before applying
   - Requires explicit confirmation

4. **Activity Log**
   - Records all operations
   - Shows errors and warnings

---

## 📋 Common Tasks

### Task 1: Check What Metadata Exists
```
1. Load files from directory
2. View "Common Fields" tab for shared metadata
3. View "Variable Fields" tab for file-specific data
```

### Task 2: Add Site Information to All Files
```
1. Load files
2. Create backup (recommended!)
3. Edit Common Fields
4. Add/modify: Site Name, Loc Position, etc.
5. Apply changes
```

### Task 3: Update Species Identification
```
1. Load files from recording session
2. Create backup
3. Edit Common Fields
4. Update "Species Manual ID"
5. Optionally add a "Note" field
6. Apply changes
```

### Task 4: Remove Incorrect Field
```
1. Load files
2. Create backup
3. Edit Common Fields
4. Clear the value (make it blank)
5. Apply - field will be deleted from all files
```

---

## 🔧 Troubleshooting

### Application Won't Start
```bash
# Check Python version (need 3.7+)
python3 --version

# Verify guano package
python3 -c "import guano; print('OK')"

# Reinstall if needed
pip3 install --upgrade guano
```

### "No GUANO metadata found"
- Your WAV files may not contain GUANO metadata
- Check if files are from GUANO-compatible equipment
- Some formats may need conversion first

### Permission Errors
- Ensure files aren't open in another program
- Check file/directory permissions
- Try copying files to a location with full access

---

## 📚 More Information

- **Comprehensive Guide**: See [USER_GUIDE.md](USER_GUIDE.md)
- **Technical Details**: See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- **Code Examples**: See [example_usage.py](example_usage.py)

### GUANO Format Resources
- **Official Site**: http://guano-md.org/
- **Specification**: https://github.com/riggsd/guano-spec
- **Python Library**: https://guano-py.readthedocs.io/

---

## 💡 Tips

1. **Always create backups** before editing valuable data
2. **Organize files by recording session** for meaningful common fields
3. **Use consistent naming** for sites, species, etc.
4. **Check the Activity Log** if something goes wrong
5. **Process small batches first** to test your workflow

---

## 🎯 Quick Reference

### File Types
- **Reads**: WAV files with GUANO metadata
- **Creates**: Timestamped backup folders
- **Modifies**: Metadata within WAV files (audio unchanged)

### What Can Be Edited
- ✅ Fields identical across all files (Common Fields)
- ❌ Fields that differ per file (Variable Fields - reference only)

### Common GUANO Fields
- `Site Name` - Recording location
- `Species Manual ID` - Species identification  
- `Loc Position` - GPS coordinates
- `Note` - General notes
- `Make`, `Model` - Equipment info

---

## ✨ You're All Set!

Launch the application and start managing your bat acoustic metadata:

```bash
python3 guano_gui.py
```

**Need help?** Check [USER_GUIDE.md](USER_GUIDE.md) for detailed instructions and troubleshooting.

**Happy researching! 🦇**
