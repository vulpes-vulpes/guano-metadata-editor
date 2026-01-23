# Changelog

All notable changes to the GUANO Metadata Editor will be documented in this file.

## [1.0.0] - 2026-01-23

### Initial Release

#### Added
- **Core Functionality**
  - Read GUANO metadata from WAV files in a directory
  - Automatic differentiation between common and variable fields
  - Edit common metadata fields across multiple files
  - Create timestamped backups before modifications
  - **WAV chunk preservation** - Safely preserves all WAV chunks (LIST, etc.) during metadata updates
  - Comprehensive error handling and validation

- **Distribution**
  - **Standalone executables** for macOS, Windows, and Linux (no Python installation required)
  - **PyInstaller configuration** for building native applications
  - **GitHub Actions workflow** for automated multi-platform builds
  - **DMG installer** for macOS, ZIP for Windows, tar.gz for Linux

- **GUI Features**
  - Clean, user-friendly interface using tkinter
  - Directory browser with file loading
  - Two-tab display for Common and Variable fields
  - Edit dialog with field-by-field modification
  - Activity log showing all operations
  - Multi-step confirmation before changes
  - Refresh functionality

- **Safety Features**
  - Automatic backup creation with timestamps
  - **Preservation of all WAV chunks** (LIST, INFO, etc.) during edits
  - Read-only variable fields to prevent inconsistency
  - Multiple confirmation steps before file modification
  - Clear warnings about data changes
  - Validation of directories and files
  - Comprehensive error messages

- **Documentation**
  - README.md with quick start guide
  - USER_GUIDE.md with comprehensive instructions for both users and developers
  - QUICK_START.md for immediate use
  - INSTALLATION.md for developer setup
  - example_usage.py with code examples

- **Developer Tools**
  - Virtual environment setup with Homebrew Python support
  - Well-documented source code
  - Type hints throughout
  - Modular architecture
  - Custom WAV chunk preservation module

#### Technical Details
- **Language**: Python 3.7+ (source), standalone executables available
- **GUI Framework**: tkinter
- **Dependencies**: guano>=1.0.12
- **Platform**: macOS, Linux, Windows
- **Architecture**: MVC-style with separation of concerns
- **Distribution**: PyInstaller-based standalone applications

#### Metadata Features
- Handles all standard GUANO fields with namespace support (e.g., GUANO|Version)
- Supports custom/vendor-specific fields
- Preserves all WAV chunks (audio data and non-GUANO metadata)
- Compatible with guano-py library ecosystem

#### Bug Fixes
- Fixed LIST chunk preservation during metadata writes
- Fixed namespace handling for GUANO fields (handles empty and populated namespaces)
- Fixed compatibility with macOS system Python (virtual environment support)

#### Known Limitations
- Loads all files into memory (suitable for 1000s of files)
- GUI only (command-line option via example_usage.py)
- Cannot bulk-edit variable fields (by design for safety)
- Requires files to already have GUANO metadata

#### Future Considerations
- Progress indicators for large batches
- Undo/redo functionality
- Metadata templates
- Batch processing of multiple directories
- Export metadata to CSV/JSON
- Metadata validation rules
- Integration with analysis pipelines

---

## Version History

### Version Numbering
- Major.Minor.Patch format
- Major: Breaking changes or major features
- Minor: New features, backward compatible
- Patch: Bug fixes, documentation updates

### Planned Features
See GitHub issues or contact maintainer for roadmap.

---

## Contributing

Contributions are welcome! Please:
1. Test thoroughly with your bat acoustic data
2. Follow existing code style
3. Update documentation as needed
4. Consider backward compatibility

---

## Acknowledgments

### GUANO Format
- Created by David A. Riggs (Myotisoft LLC)
- Specification: https://github.com/riggsd/guano-spec
- Python library: https://github.com/riggsd/guano-py

### Bat Acoustic Community
- Thanks to researchers who test and provide feedback
- Thanks to equipment manufacturers supporting GUANO

### Open Source Tools
- Python and the Python community
- tkinter GUI framework
- All contributors to the GUANO ecosystem
