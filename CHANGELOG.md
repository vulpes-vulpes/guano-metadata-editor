# Changelog

All notable changes to the GUANO Metadata Editor will be documented in this file.

## [1.2.0] - 2026-04-01

### Major Features

#### Pending Changes Queue System
- **Batch editing workflow**: Queue multiple changes and apply them all in a single pass through files
- **Three change types supported**:
  - `[C]` Common field edits
  - `[V→C]` Variable field standardization
  - `[NEW]` New field additions
- **Visual queue panel**: See all pending changes before applying
  - Remove individual changes
  - Clear all queued changes
  - Changes labeled by type with clear formatting
- **Single-pass processing**: Apply all queued changes in one operation instead of multiple passes
- **Smart button states**: "Apply All Changes" button disabled when queue is empty, enabled with visual indicator when changes are pending

#### Explicit Field Deletion
- **Delete checkboxes** added to Edit Common Fields and Edit Variable Fields dialogs
- **Visual feedback**: Entry fields disable when delete is checked
- **Consistent behavior**: Clear indication of deletion intent across all dialogs
- **Dual method support**: Delete via checkbox (recommended) or by clearing field value
- **Queue display**: Deleted fields show with `<delete>` indicator

### Performance & Memory Improvements
- **Parallel file loading**: ThreadPoolExecutor with adaptive worker count (2-16 based on file count)
- **Parallel updates**: Batched processing for efficient large dataset handling
- **Memory optimization**: 95% reduction in memory usage for large datasets
  - Removed GuanoFile object caching
  - Temporary metadata dictionaries instead of full objects
  - Conservative worker limits (4-6 threads for datasets >1000 files)
  - Batch size: 100 files per update batch
- **Performance**: Tested with 16,000+ files, reduced RAM from 22GB to <2GB

### User Experience Enhancements
- **Integrated progress bars**: Real-time progress tracking during file loading and updates
- **Thread-safe updates**: Smooth progress bar updates using `after_idle()` with proper lambda capture
- **macOS ._ file filtering**: Automatic filtering of AppleDouble metadata files during loading
- **Filtered file reporting**: Log shows count of filtered ._ files
- **Enhanced status indicators**: 
  - Pending changes count with emoji indicator (⚡)
  - Orange bold text when changes are ready
  - Play icon (▶) on Apply All Changes button
- **Larger window**: Increased from 700px to 850px height for better visibility

### Removed Features
- **Backup feature removed**: Simplified workflow, users maintain their own backups
- **Refresh View button removed**: Redundant with automatic refresh after changes
- **Rationale**: Reduces complexity, avoids disk space issues with large datasets, puts backup responsibility with users who understand their infrastructure

### UI Improvements
- **Edit Common Fields dialog**: Delete checkboxes with disabled entry feedback
- **Edit Variable Fields dialog**: 
  - Delete checkboxes for variable field removal
  - Updated instructions for clarity
  - Support for deleting variable fields (previously only standardization)
- **Pending Changes panel**: 
  - Clear type labels: [C], [V→C], [NEW]
  - Delete indicator: `<delete>` for removed fields
  - Remove Selected, Clear All buttons
- **Button reorganization**: Streamlined to Edit Common, Edit Variable, Add Field

### Bug Fixes
- **Loc Position field handling**: Fixed type coercion bug where tuple values became None
- **Progress bar recursion**: Fixed infinite event loop from lambda variable capture
- **Memory leaks**: Eliminated metadata caching preventing garbage collection

### Documentation
- **README.md**: Updated with v1.2.0 pending changes queue workflow
- **USER_GUIDE.md**: Complete rewrite of workflows and features for new queue system
  - New Workflow 4: Batch Metadata Updates
  - New Workflow 6: Standardizing Variable Fields  
  - Updated safety features section
  - Added delete checkbox documentation
  - Removed backup feature references
- **Example workflows**: Updated to show queue-based batch editing

### Technical Changes
- **Thread-safe callbacks**: Progress callbacks use `after_idle()` for safe GUI updates
- **Lambda value capture**: Fixed with default arguments pattern `lambda c=current, t=total`
- **File filtering**: `Path.glob()` with list comprehension for ._ file exclusion
- **Grid layout**: Adjusted weights to keep pending changes panel always visible
- **Confirmation dialogs**: Updated to reference user backup responsibility

### Breaking Changes
- Removed `create_backup()` method from `GuanoMetadataManager`
- Removed `shutil` import (no longer needed)
- Dialog buttons changed from "Apply Changes" to "Add to Queue"
- Removed backup-related GUI elements

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
