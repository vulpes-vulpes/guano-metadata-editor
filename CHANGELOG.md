# Changelog

All notable changes to the GUANO Metadata Editor will be documented in this file.

## [1.1.0] - 2026-03-16

### Added
- **Add New Fields Feature**
  - New "Add Field" button in the main GUI to add metadata fields to all loaded files
  - Two-mode field selection dialog:
    - **Standard GUANO Fields**: Browse and select from all 23 spec-defined fields with full descriptions and type information
    - **Custom Fields**: Define custom namespaced fields (e.g., `User|Survey Site`, `ACME|GainSetting`)
  - Live preview of field names (e.g., `User|FieldName`) as you type
  - Embedded descriptions from the GUANO specification for each standard field
  - Automatic detection of existing fields with user-facing warnings
  - Support for both standard and custom field additions

### Security & Robustness Improvements
- **Field Name Validation**: Reject field names with `:` or newline characters that would corrupt GUANO format
- **Memory Protection**: Cap WAV chunk sizes at 256 MB to prevent memory exhaustion from crafted files
- **Protected Field Safeguards**: 
  - Added warning before modifying `GUANO|Version` in the edit dialog
  - Require explicit confirmation before any protected field changes
- **Symlink Traversal Protection**: Directory scan now rejects symlinks pointing outside the selected directory
- **Temp File Cleanup**: Fixed resource leak where temp files could be orphaned if write operations fail
- **Exception Handling**: Replaced bare `except:` with specific `except OSError` for more reliable error handling

### Infrastructure
- Added GUANO specification constants to `guano_metadata_manager.py`:
  - `GUANO_STANDARD_FIELDS`: All 23 spec-defined fields with types and descriptions
  - `GUANO_RESERVED_NAMESPACES`: All 11 registered vendor/manufacturer namespaces
  - `GUANO_PROTECTED_FIELDS`: Meta-fields requiring extra confirmation before modification
- Updated `example_usage.py` with new field addition examples

### Documentation
- Enhanced inline documentation explaining field validation and namespace requirements
- Added guidance on using the `User` namespace for personal custom fields to maximize data sharing compatibility

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
