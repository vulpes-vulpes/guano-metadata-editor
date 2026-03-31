"""
GUANO Metadata Manager

Core module for reading and writing GUANO metadata in WAV files.
Provides functionality to analyze metadata consistency across multiple files.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional, Callable
from collections import defaultdict
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing

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
    
    Memory-optimized: Only caches field analysis, not full GuanoFile objects.
    """
    
    def __init__(self):
        self.files: List[Path] = []
        # Don't cache GuanoFile objects - they use too much memory
        # self.metadata will only be populated during analysis, then cleared
        self._metadata_cache: Dict[str, guano.GuanoFile] = {}
        self.common_fields: Dict[str, Any] = {}
        self.variable_fields: Dict[str, List[Tuple[str, Any]]] = {}
        
        # Memory management settings
        self.max_memory_cached_files = 1000  # Only cache metadata for analysis if < 1000 files
    
    def _load_single_file_metadata(self, wav_file: Path, resolved_dir: Path) -> Tuple[bool, Optional[Path], Optional[Dict], Optional[str]]:
        """
        Load only the metadata fields from a single WAV file (not the full GuanoFile object).
        Helper method for parallel processing - memory optimized.
        
        Args:
            wav_file: Path to the WAV file
            resolved_dir: Resolved directory path for symlink checking
            
        Returns:
            Tuple of (success, filepath, metadata_dict, error_message)
        """
        # Guard against symlinks that point outside the selected directory
        try:
            if not wav_file.resolve().is_relative_to(resolved_dir):
                logger.warning(
                    f"Skipping {wav_file.name}: resolves outside selected "
                    f"directory (possible symlink attack)"
                )
                return False, None, None, f"Skipped (outside directory): {wav_file.name}"
        except OSError:
            return False, None, None, f"Could not resolve path: {wav_file.name}"
        
        try:
            g = guano.GuanoFile(str(wav_file))
            
            # Check if file has GUANO metadata
            if not g:
                logger.warning(f"No GUANO metadata found in: {wav_file.name}")
                return False, None, None, f"No GUANO metadata: {wav_file.name}"
            
            # Extract just the metadata dictionary, not the whole GuanoFile object
            # This saves significant memory
            metadata_dict = {}
            if hasattr(g, '_md') and g._md:
                # Make a lightweight copy of the metadata structure
                for key, value in g._md.items():
                    if isinstance(value, dict):
                        metadata_dict[key] = dict(value)
                    else:
                        metadata_dict[key] = value
            
            logger.debug(f"Loaded metadata from: {wav_file.name}")
            return True, wav_file, metadata_dict, None
            
        except Exception as e:
            logger.error(f"Error loading {wav_file.name}: {str(e)}")
            return False, None, None, f"Error loading {wav_file.name}: {str(e)}"
        
    def load_directory(self, directory: str, parallel: bool = True, max_workers: Optional[int] = None, 
                      progress_callback: Optional[Callable[[int, int], None]] = None) -> Tuple[int, List[str]]:
        """
        Load all WAV files from a directory.
        
        Args:
            directory: Path to directory containing WAV files
            parallel: Whether to use parallel processing (default: True)
            max_workers: Maximum number of worker threads (default: CPU count * 2)
            progress_callback: Optional callback(current, total) for progress updates
            
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
        all_wav_files = list(directory_path.glob('**/*.wav')) + \
                        list(directory_path.glob('**/*.WAV'))
        
        # Filter out macOS metadata files (._*) and other hidden files
        wav_files = [f for f in all_wav_files if not f.name.startswith('._') and not f.name.startswith('.')]
        
        # Check for and log filtered files
        filtered_count = len(all_wav_files) - len(wav_files)
        if filtered_count > 0:
            logger.info(f"Filtered out {filtered_count} macOS metadata/hidden files")
        
        if not wav_files:
            errors.append(f"No WAV files found in directory: {directory}")
            return 0, errors
        
        logger.info(f"Found {len(wav_files)} WAV files in {directory}")
        
        # Resolve the directory once for symlink containment checks
        resolved_dir = directory_path.resolve()
        
        # Memory-conscious worker count: limit to 4-6 workers for large file counts
        if max_workers is None:
            if len(wav_files) > 5000:
                max_workers = 4  # Very conservative for huge datasets
            elif len(wav_files) > 1000:
                max_workers = 6  # Conservative for large datasets
            else:
                max_workers = min(len(wav_files), multiprocessing.cpu_count() * 2)
        
        # Temporary storage for metadata during analysis
        temp_metadata = {}
        processed_count = 0

        if parallel and len(wav_files) > 1:
            logger.info(f"Loading files with {max_workers} worker threads")
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all file load tasks
                future_to_file = {
                    executor.submit(self._load_single_file_metadata, wav_file, resolved_dir): wav_file
                    for wav_file in wav_files
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_file):
                    try:
                        success, filepath, metadata_dict, error_msg = future.result()
                        if success:
                            self.files.append(filepath)
                            temp_metadata[str(filepath)] = metadata_dict
                        elif error_msg:
                            errors.append(error_msg)
                        
                        # Report progress
                        processed_count += 1
                        if progress_callback:
                            progress_callback(processed_count, len(wav_files))
                            
                    except Exception as e:
                        wav_file = future_to_file[future]
                        error_msg = f"Unexpected error loading {wav_file.name}: {str(e)}"
                        logger.error(error_msg)
                        errors.append(error_msg)
                        processed_count += 1
                        if progress_callback:
                            progress_callback(processed_count, len(wav_files))
        else:
            # Sequential processing for single file or when parallel is disabled
            for idx, wav_file in enumerate(wav_files, 1):
                success, filepath, metadata_dict, error_msg = self._load_single_file_metadata(wav_file, resolved_dir)
                if success:
                    self.files.append(filepath)
                    temp_metadata[str(filepath)] = metadata_dict
                elif error_msg:
                    errors.append(error_msg)
                
                # Report progress
                if progress_callback:
                    progress_callback(idx, len(wav_files))
        
        if self.files:
            logger.info(f"Analyzing fields from {len(self.files)} loaded files...")
            self._analyze_fields(temp_metadata)
            # Clear temporary metadata after analysis to free memory
            temp_metadata.clear()
            logger.info(f"Field analysis complete, metadata cache cleared to save memory")
        
        return len(self.files), errors
    
    def _analyze_fields(self, metadata_dicts: Dict[str, Dict]):
        """
        Analyze metadata fields to determine which are common (identical across
        all files) and which are variable (differ between files).
        
        Args:
            metadata_dicts: Dictionary mapping filepath to metadata dictionary
        """
        if not metadata_dicts:
            return
        
        # Collect all fields and their values across all files
        field_values: Dict[str, List[Any]] = defaultdict(list)
        
        for filepath, md in metadata_dicts.items():
            filename = Path(filepath).name
            
            # Process metadata dictionary
            for key, value in md.items():
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
    
    def _update_single_file(self, filepath: Path, field_updates: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Update a single file with the given field updates.
        Helper method for parallel processing - memory optimized (doesn't return GuanoFile).
        
        Args:
            filepath: Path to the file to update
            field_updates: Dictionary of field names and new values
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Load, update, write, and discard - don't keep in memory
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
            logger.info(f"Updated: {Path(filepath).name}")
            
            # Don't return the GuanoFile object - let it be garbage collected
            return True, None
            
        except Exception as e:
            error_msg = f"Error updating {Path(filepath).name}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def update_common_fields(self, field_updates: Dict[str, Any], parallel: bool = True, max_workers: Optional[int] = None,
                            progress_callback: Optional[Callable[[int, int], None]] = None) -> Tuple[int, List[str]]:
        """
        Update common metadata fields across all loaded files.
        
        Args:
            field_updates: Dictionary of field names and new values
            parallel: Whether to use parallel processing (default: True)
            max_workers: Maximum number of worker threads (default: CPU count)
            progress_callback: Optional callback(current, total) for progress updates
        
        Returns:
            Tuple of (number of files updated, list of error messages)
        """
        if not self.files:
            return 0, ["No files loaded"]
        
        if not field_updates:
            return 0, ["No field updates provided"]
        
        updated_count = 0
        errors = []
        
        logger.info(f"Updating {len(field_updates)} fields in {len(self.files)} files (parallel={parallel})")
        
        # Memory-conscious worker count for updates
        if max_workers is None:
            if len(self.files) > 5000:
                max_workers = 4  # Very conservative for huge datasets
            elif len(self.files) > 1000:
                max_workers = 6  # Conservative for large datasets
            else:
                max_workers = min(len(self.files), multiprocessing.cpu_count() * 2)
        
        if parallel and len(self.files) > 1:
            logger.info(f"Using {max_workers} worker threads")
            
            # Process in batches to limit memory usage from pending futures
            batch_size = max(100, len(self.files) // 10)  # Process ~10% at a time, min 100
            total_processed = 0
            
            for i in range(0, len(self.files), batch_size):
                batch = self.files[i:i + batch_size]
                logger.info(f"Processing batch {i//batch_size + 1}/{(len(self.files) + batch_size - 1)//batch_size} ({len(batch)} files)")
                
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    # Submit batch of file update tasks
                    future_to_filepath = {
                        executor.submit(self._update_single_file, filepath, field_updates): filepath
                        for filepath in batch
                    }
                    
                    # Collect results as they complete
                    for future in as_completed(future_to_filepath):
                        filepath = future_to_filepath[future]
                        try:
                            success, error_msg = future.result()
                            if success:
                                updated_count += 1
                            else:
                                errors.append(error_msg)
                            
                            # Report progress
                            total_processed += 1
                            if progress_callback:
                                progress_callback(total_processed, len(self.files))
                                
                        except Exception as e:
                            error_msg = f"Unexpected error updating {Path(filepath).name}: {str(e)}"
                            logger.error(error_msg)
                            errors.append(error_msg)
                            total_processed += 1
                            if progress_callback:
                                progress_callback(total_processed, len(self.files))
        else:
            # Sequential processing (for single file or when parallel is disabled)
            for idx, filepath in enumerate(self.files, 1):
                success, error_msg = self._update_single_file(filepath, field_updates)
                if success:
                    updated_count += 1
                else:
                    errors.append(error_msg)
                
                # Report progress
                if progress_callback:
                    progress_callback(idx, len(self.files))
        
        # Refresh analysis after updates by re-scanning (memory efficient)
        if updated_count > 0:
            logger.info(f"Successfully updated {updated_count} files, refreshing analysis...")
            self._refresh_analysis()
        
        return updated_count, errors
    
    def _refresh_analysis(self):
        """
        Re-analyze fields after updates without keeping full GuanoFile objects in memory.
        Memory-optimized version that loads metadata temporarily.
        """
        temp_metadata = {}
        
        logger.info(f"Re-scanning {len(self.files)} files for updated field analysis...")
        
        # Load metadata from each file (lightweight)
        for filepath in self.files:
            try:
                g = guano.GuanoFile(str(filepath))
                
                # Extract just the metadata dictionary
                metadata_dict = {}
                if hasattr(g, '_md') and g._md:
                    for key, value in g._md.items():
                        if isinstance(value, dict):
                            metadata_dict[key] = dict(value)
                        else:
                            metadata_dict[key] = value
                
                temp_metadata[str(filepath)] = metadata_dict
                
            except Exception as e:
                logger.warning(f"Error reloading {filepath}: {e}")
        
        # Analyze fields
        self._analyze_fields(temp_metadata)
        
        # Clear temporary storage
        temp_metadata.clear()
        logger.info("Field analysis refreshed")
    
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
    
    def clean_macos_metadata_files(self, directory: str) -> Tuple[int, List[str]]:
        """
        Remove macOS metadata files (._* files) from a directory.
        These are AppleDouble format files that can interfere with file processing.
        
        Args:
            directory: Path to directory to clean
            
        Returns:
            Tuple of (number of files deleted, list of error messages)
        """
        deleted_count = 0
        errors = []
        
        directory_path = Path(directory)
        
        if not directory_path.exists() or not directory_path.is_dir():
            return 0, ["Invalid directory"]
        
        logger.info(f"Scanning for macOS metadata files in {directory}")
        
        # Find all ._ files
        metadata_files = list(directory_path.glob('**/._*'))
        
        if not metadata_files:
            logger.info("No macOS metadata files found")
            return 0, []
        
        logger.info(f"Found {len(metadata_files)} macOS metadata files")
        
        for file_path in metadata_files:
            try:
                file_path.unlink()  # Delete the file
                deleted_count += 1
                logger.debug(f"Deleted: {file_path.name}")
            except Exception as e:
                error_msg = f"Failed to delete {file_path.name}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        logger.info(f"Deleted {deleted_count} macOS metadata files")
        return deleted_count, errors


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
