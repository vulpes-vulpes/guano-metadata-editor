"""
GUANO Metadata Manager

Core module for reading and writing GUANO metadata in WAV files.
Provides functionality to analyze metadata consistency across multiple files.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict
import logging

try:
    import guano
except ImportError:
    raise ImportError(
        "The 'guano' package is required. Install it with: pip install guano"
    )

from wav_chunk_preserver import safe_guano_write


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# GUANO specification constants
# Reference: https://github.com/riggsd/guano-spec/blob/master/guano_specification.md
# ---------------------------------------------------------------------------

# All fields defined in the GUANO specification, with type, required flag,
# and a short description drawn directly from the spec.
GUANO_STANDARD_FIELDS: Dict[str, Dict] = {
    "GUANO|Version": {
        "type": "string",
        "required": True,
        "description": "GUANO metadata version in use. Must be '1.0'. "
                       "Must appear as the very first field in the metadata block.",
    },
    "Filter HP": {
        "type": "float",
        "required": False,
        "description": "High-pass filter frequency in kHz.",
    },
    "Filter LP": {
        "type": "float",
        "required": False,
        "description": "Low-pass filter frequency in kHz.",
    },
    "Firmware Version": {
        "type": "string",
        "required": False,
        "description": "Device firmware version in the manufacturer's own format.",
    },
    "Hardware Version": {
        "type": "string",
        "required": False,
        "description": "Device hardware revision or hardware options.",
    },
    "Humidity": {
        "type": "float",
        "required": False,
        "description": "Relative humidity as a percentage (0.0–100.0).",
    },
    "Length": {
        "type": "float",
        "required": False,
        "description": "Recording length in seconds. "
                       "For time-expanded files this is the actual (not .WAV) duration.",
    },
    "Loc Accuracy": {
        "type": "float",
        "required": False,
        "description": "Location accuracy in metres (Estimated Position Error, 1-sigma).",
    },
    "Loc Elevation": {
        "type": "float",
        "required": False,
        "description": "Elevation above mean sea level in metres.",
    },
    "Loc Position": {
        "type": "lat/lon",
        "required": False,
        "description": "WGS84 latitude/longitude pair, space-separated e.g. '51.5074 -0.1278'.",
    },
    "Make": {
        "type": "string",
        "required": False,
        "description": "Manufacturer of the recording hardware.",
    },
    "Model": {
        "type": "string",
        "required": False,
        "description": "Model name or number of the recording hardware.",
    },
    "Note": {
        "type": "multiline string",
        "required": False,
        "description": "Freeform text note associated with the recording. "
                       "Use \\n to encode a literal newline.",
    },
    "Original Filename": {
        "type": "string",
        "required": False,
        "description": "Original filename as used by the recording hardware. "
                       "Editing software should preserve this value when renaming files.",
    },
    "Samplerate": {
        "type": "integer",
        "required": False,
        "description": "Recording samplerate in Hz. "
                       "For time-expanded files this is TE × the .WAV samplerate.",
    },
    "Serial": {
        "type": "string",
        "required": False,
        "description": "Serial number or unique identifier of the recording hardware.",
    },
    "Species Auto ID": {
        "type": "list",
        "required": False,
        "description": "Auto-classified species/guild, comma-separated. "
                       "Most dominant species should appear first.",
    },
    "Species Manual ID": {
        "type": "list",
        "required": False,
        "description": "Manually identified species/guild, comma-separated. "
                       "Most dominant species should appear first.",
    },
    "Tags": {
        "type": "list",
        "required": False,
        "description": "Comma-separated arbitrary tags or labels.",
    },
    "TE": {
        "type": "integer",
        "required": False,
        "description": "Time-expansion factor. Omit or use 1 for direct (non-expanded) recordings.",
    },
    "Temperature Ext": {
        "type": "float",
        "required": False,
        "description": "External (ambient) temperature in degrees Celsius.",
    },
    "Temperature Int": {
        "type": "float",
        "required": False,
        "description": "Internal device temperature in degrees Celsius.",
    },
    "Timestamp": {
        "type": "datetime",
        "required": True,
        "description": "Recording start time in ISO 8601 format, "
                       "e.g. '2015-12-31T23:59:59+04:00'. "
                       "Include UTC offset wherever possible.",
    },
}

# Registered GUANO namespaces.  Manufacturer/software authors should use their
# own reserved namespace for any custom fields.  End users should use 'User'.
GUANO_RESERVED_NAMESPACES: Dict[str, str] = {
    "GUANO":  "GUANO meta-metadata (do not use for custom fields)",
    "User":   "User-defined personal fields",
    "Anabat": "Titley Scientific",
    "BAT":    "Binary Acoustic Technologies",
    "BATREC": "Bat Recorder by Bill Kraus",
    "MSFT":   "Myotisoft",
    "NABat":  "North American Bat Monitoring Program",
    "OAD":    "Open Acoustic Devices",
    "PET":    "Pettersson",
    "SB":     "SonoBat",
    "WA":     "Wildlife Acoustics",
}

# Fields that should not be silently overwritten; the user should be
# explicitly warned before any change is made.
GUANO_PROTECTED_FIELDS: set = {"GUANO|Version"}


class GuanoMetadataManager:
    """
    Manager class for reading and editing GUANO metadata in WAV files.
    """
    
    def __init__(self):
        self.files: List[Path] = []
        self.metadata: Dict[str, guano.GuanoFile] = {}
        self.common_fields: Dict[str, Any] = {}
        self.variable_fields: Dict[str, List[Tuple[str, Any]]] = {}
        
    def load_directory(self, directory: str) -> Tuple[int, List[str]]:
        """
        Load all WAV files from a directory.
        
        Args:
            directory: Path to directory containing WAV files
            
        Returns:
            Tuple of (number of files loaded, list of error messages)
        """
        self.files = []
        self.metadata = {}
        errors = []
        
        directory_path = Path(directory)
        
        if not directory_path.exists():
            errors.append(f"Directory does not exist: {directory}")
            return 0, errors
            
        if not directory_path.is_dir():
            errors.append(f"Path is not a directory: {directory}")
            return 0, errors
        
        # Find all WAV files (case-insensitive)
        wav_files = list(directory_path.glob('**/*.wav')) + \
                    list(directory_path.glob('**/*.WAV'))
        
        if not wav_files:
            errors.append(f"No WAV files found in directory: {directory}")
            return 0, errors
        
        logger.info(f"Found {len(wav_files)} WAV files in {directory}")
        
        # Resolve the directory once for symlink containment checks below.
        resolved_dir = directory_path.resolve()

        # Load metadata from each file
        for wav_file in wav_files:
            # Guard against symlinks that point outside the selected directory.
            # Without this, a crafted symlink could cause reads (or later writes)
            # to affect files the user never intended to touch.
            try:
                if not wav_file.resolve().is_relative_to(resolved_dir):
                    logger.warning(
                        f"Skipping {wav_file.name}: resolves outside selected "
                        f"directory (possible symlink attack)"
                    )
                    errors.append(f"Skipped (outside directory): {wav_file.name}")
                    continue
            except OSError:
                errors.append(f"Could not resolve path: {wav_file.name}")
                continue
            try:
                g = guano.GuanoFile(str(wav_file))
                
                # Check if file has GUANO metadata
                if not g:
                    logger.warning(f"No GUANO metadata found in: {wav_file.name}")
                    errors.append(f"No GUANO metadata: {wav_file.name}")
                    continue
                
                self.files.append(wav_file)
                self.metadata[str(wav_file)] = g
                logger.info(f"Loaded metadata from: {wav_file.name}")
                
            except Exception as e:
                logger.error(f"Error loading {wav_file.name}: {str(e)}")
                errors.append(f"Error loading {wav_file.name}: {str(e)}")
        
        if self.files:
            self._analyze_fields()
        
        return len(self.files), errors
    
    def _analyze_fields(self):
        """
        Analyze metadata fields to determine which are common (identical across
        all files) and which are variable (differ between files).
        """
        if not self.metadata:
            return
        
        # Collect all fields and their values across all files
        field_values: Dict[str, List[Any]] = defaultdict(list)
        
        for filepath, g in self.metadata.items():
            filename = Path(filepath).name
            
            # GuanoFile stores metadata in _md with nested namespaces
            if hasattr(g, '_md') and g._md:
                for key, value in g._md.items():
                    if isinstance(value, dict):
                        # Namespaced fields (e.g., GUANO|Version, Filter|HPF)
                        for subkey, subvalue in value.items():
                            # Handle empty namespace
                            if key:
                                full_key = f"{key}|{subkey}"
                            else:
                                full_key = subkey
                            field_values[full_key].append((filename, subvalue))
                    else:
                        # Non-namespaced field - use key as-is
                        field_values[key].append((filename, value))
        
        # Categorize fields as common or variable
        self.common_fields = {}
        self.variable_fields = {}
        
        for field, values in field_values.items():
            # Check if all values are identical
            unique_values = set(str(v[1]) for v in values if v[1] is not None)
            
            if len(unique_values) == 1 and len(values) == len(self.files):
                # All files have the same value for this field
                self.common_fields[field] = values[0][1]
            else:
                # Values differ across files or not all files have this field
                self.variable_fields[field] = values
        
        logger.info(f"Found {len(self.common_fields)} common fields and "
                   f"{len(self.variable_fields)} variable fields")
    
    def get_common_fields(self) -> Dict[str, Any]:
        """Get metadata fields that are identical across all files."""
        return self.common_fields.copy()
    
    def get_variable_fields(self) -> Dict[str, List[Tuple[str, Any]]]:
        """Get metadata fields that differ between files."""
        return self.variable_fields.copy()
    
    def get_file_count(self) -> int:
        """Get the number of loaded files."""
        return len(self.files)
    
    def create_backup(self, backup_dir: Optional[str] = None) -> Tuple[bool, str]:
        """
        Create backup copies of all loaded files.
        
        Args:
            backup_dir: Optional custom backup directory path.
                       If None, creates timestamped folder in same location.
        
        Returns:
            Tuple of (success, backup_path or error_message)
        """
        if not self.files:
            return False, "No files loaded"
        
        try:
            # Create backup directory
            if backup_dir is None:
                parent_dir = self.files[0].parent
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = parent_dir / f"GUANO_backup_{timestamp}"
            else:
                backup_path = Path(backup_dir)
            
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Copy all files
            for file_path in self.files:
                dest = backup_path / file_path.name
                shutil.copy2(file_path, dest)
                logger.info(f"Backed up: {file_path.name}")
            
            logger.info(f"Backup created at: {backup_path}")
            return True, str(backup_path)
            
        except Exception as e:
            error_msg = f"Backup failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def _coerce_field_value(self, field: str, value: str) -> Any:
        """
        Convert string values to the proper type expected by GuanoFile.
        
        Args:
            field: Field name (e.g., 'Loc Position', 'Samplerate')
            value: String value from user input
            
        Returns:
            Properly typed value for the field
        """
        # Handle fields that require special coercion
        if field == 'Loc Position':
            # Expects tuple of floats: (latitude, longitude)
            parts = value.split()
            if len(parts) != 2:
                raise ValueError(f"Loc Position must be two space-separated numbers (lat lon), got: {value}")
            return tuple(float(v) for v in parts)
        elif field in ('Filter HP', 'Length', 'Loc Accuracy', 'Loc Elevation'):
            return float(value)
        elif field in ('Samplerate',):
            return int(value)
        elif field == 'TE':
            return int(value) if value else 1
        elif field == 'Note':
            # Preserve newline handling
            return value.replace('\\n', '\n')
        else:
            # Return as string for other fields
            return value
    
    def update_common_fields(self, field_updates: Dict[str, Any]) -> Tuple[int, List[str]]:
        """
        Update common metadata fields across all loaded files.
        
        Args:
            field_updates: Dictionary of field names and new values
        
        Returns:
            Tuple of (number of files updated, list of error messages)
        """
        if not self.files:
            return 0, ["No files loaded"]
        
        if not field_updates:
            return 0, ["No field updates provided"]
        
        updated_count = 0
        errors = []
        
        logger.info(f"Updating {len(field_updates)} fields in {len(self.files)} files")
        
        for filepath in self.files:
            try:
                # Re-open the file to ensure we have fresh data
                g = guano.GuanoFile(str(filepath))
                
                # Update fields using proper GuanoFile API
                for field, value in field_updates.items():
                    try:
                        if value is None or value == "":
                            # Delete field if value is empty
                            if field in g:
                                del g[field]
                                logger.debug(f"Deleted field '{field}' from {Path(filepath).name}")
                        else:
                            # Coerce value to proper type before setting
                            coerced_value = self._coerce_field_value(field, value)
                            g[field] = coerced_value
                            logger.debug(f"Set '{field}' = '{coerced_value}' in {Path(filepath).name}")
                    except Exception as e:
                        logger.warning(f"Could not update field '{field}' in {Path(filepath).name}: {e}")
                
                # Write using safe method that preserves all chunks (including LIST)
                safe_guano_write(str(filepath), g)
                
                # Update our cached metadata
                self.metadata[str(filepath)] = g
                updated_count += 1
                logger.info(f"Updated: {Path(filepath).name}")
                
            except Exception as e:
                error_msg = f"Error updating {Path(filepath).name}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
                
            except Exception as e:
                error_msg = f"Error updating {Path(filepath).name}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        # Refresh analysis after updates
        if updated_count > 0:
            # Reload metadata
            for filepath in self.files:
                try:
                    self.metadata[str(filepath)] = guano.GuanoFile(str(filepath))
                except Exception as e:
                    logger.warning(f"Error reloading {filepath}: {e}")
            
            self._analyze_fields()
        
        return updated_count, errors
    
    def get_field_info(self, field_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific metadata field.
        
        Args:
            field_name: Name of the field to inspect
            
        Returns:
            Dictionary with field information
        """
        info = {
            'name': field_name,
            'is_common': field_name in self.common_fields,
            'is_variable': field_name in self.variable_fields,
            'value': None,
            'values': []
        }
        
        if info['is_common']:
            info['value'] = self.common_fields[field_name]
        
        if info['is_variable']:
            info['values'] = self.variable_fields[field_name]
        
        return info
    
    def get_all_field_names(self) -> List[str]:
        """Get a sorted list of all field names across all files."""
        all_fields = set(self.common_fields.keys()) | set(self.variable_fields.keys())
        return sorted(all_fields)
    
    def validate_directory(self, directory: str) -> Tuple[bool, str]:
        """
        Validate that a directory exists and is accessible.
        
        Args:
            directory: Path to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        path = Path(directory)
        
        if not path.exists():
            return False, "Directory does not exist"
        
        if not path.is_dir():
            return False, "Path is not a directory"
        
        if not os.access(path, os.R_OK):
            return False, "Directory is not readable"
        
        return True, "Directory is valid"


def format_value(value: Any) -> str:
    """
    Format a metadata value for display.
    
    Args:
        value: The value to format
        
    Returns:
        Formatted string representation
    """
    if value is None:
        return "<empty>"
    elif isinstance(value, (list, tuple)):
        return ", ".join(str(v) for v in value)
    else:
        return str(value)
