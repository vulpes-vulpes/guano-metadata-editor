"""
WAV Chunk Preservation Module

This module provides functions to modify WAV files while preserving all chunks,
including LIST chunks that guano-py doesn't preserve.
"""

import struct
import io
from pathlib import Path
from typing import Dict, List, Tuple
import logging

# Maximum sane size for a single WAV chunk (256 MB).
# Protects against memory exhaustion when reading corrupted or crafted files.
_MAX_CHUNK_BYTES = 256 * 1024 * 1024

logger = logging.getLogger(__name__)


class WAVChunk:
    """Represents a single chunk in a WAV file."""
    
    def __init__(self, chunk_id: bytes, data: bytes):
        self.chunk_id = chunk_id
        self.data = data
    
    def __len__(self):
        return len(self.data)
    
    def write(self, f):
        """Write this chunk to a file."""
        f.write(self.chunk_id)
        f.write(struct.pack('<I', len(self.data)))
        f.write(self.data)
        # Word-align
        if len(self.data) % 2:
            f.write(b'\x00')


def read_wav_chunks(filepath: str) -> List[WAVChunk]:
    """
    Read all chunks from a WAV file.
    
    Args:
        filepath: Path to WAV file
        
    Returns:
        List of WAVChunk objects
    """
    chunks = []
    
    with open(filepath, 'rb') as f:
        # Read RIFF header
        riff = f.read(4)
        if riff != b'RIFF':
            raise ValueError(f"Not a RIFF file")
        
        file_size = struct.unpack('<I', f.read(4))[0]
        wave = f.read(4)
        if wave != b'WAVE':
            raise ValueError(f"Not a WAVE file")
        
        # Read all chunks
        while True:
            chunk_id = f.read(4)
            if len(chunk_id) < 4:
                break
            
            chunk_size = struct.unpack('<I', f.read(4))[0]

            if chunk_size > _MAX_CHUNK_BYTES:
                logger.warning(
                    f"Chunk {chunk_id!r} size {chunk_size} exceeds limit "
                    f"({_MAX_CHUNK_BYTES} bytes); stopping read."
                )
                break

            chunk_data = f.read(chunk_size)

            if len(chunk_data) < chunk_size:
                logger.warning(f"Incomplete chunk {chunk_id}, expected {chunk_size} bytes, got {len(chunk_data)}")
                break
            
            chunks.append(WAVChunk(chunk_id, chunk_data))
            
            # Skip padding byte if odd size
            if chunk_size % 2:
                f.read(1)
    
    return chunks


def write_wav_with_chunks(filepath: str, chunks: List[WAVChunk]):
    """
    Write a WAV file with the given chunks.
    
    Args:
        filepath: Path to output WAV file
        chunks: List of WAVChunk objects to write
    """
    # Calculate total size
    total_size = 4  # 'WAVE'
    for chunk in chunks:
        total_size += 8 + len(chunk.data)  # chunk_id + size + data
        if len(chunk.data) % 2:
            total_size += 1  # padding
    
    with open(filepath, 'wb') as f:
        # Write RIFF header
        f.write(b'RIFF')
        f.write(struct.pack('<I', total_size))
        f.write(b'WAVE')
        
        # Write all chunks
        for chunk in chunks:
            chunk.write(f)


def update_guano_chunk(chunks: List[WAVChunk], guano_data: bytes) -> List[WAVChunk]:
    """
    Update or add the GUANO chunk in a list of chunks.
    
    Args:
        chunks: List of existing chunks
        guano_data: New GUANO metadata bytes
        
    Returns:
        Updated list of chunks
    """
    new_chunks = []
    guano_updated = False
    
    for chunk in chunks:
        if chunk.chunk_id == b'guan':
            # Replace existing GUANO chunk
            new_chunks.append(WAVChunk(b'guan', guano_data))
            guano_updated = True
        else:
            new_chunks.append(chunk)
    
    # Add GUANO chunk if it didn't exist
    if not guano_updated:
        # Insert after 'fmt ' chunk if possible
        insert_pos = 1  # After fmt
        for i, chunk in enumerate(new_chunks):
            if chunk.chunk_id == b'fmt ':
                insert_pos = i + 1
                break
        new_chunks.insert(insert_pos, WAVChunk(b'guan', guano_data))
    
    return new_chunks


def safe_guano_write(filepath: str, guano_file):
    """
    Write GUANO metadata while preserving all other WAV chunks.
    
    Args:
        filepath: Path to WAV file to update
        guano_file: GuanoFile object with updated metadata
    """
    import tempfile
    import shutil
    
    # Read all existing chunks
    original_chunks = read_wav_chunks(filepath)
    
    # Get updated GUANO data by writing to a temp file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # Write using guano-py to get updated GUANO chunk
        shutil.copy2(filepath, tmp_path)
        guano_file.filename = tmp_path
        guano_file.write(make_backup=False)
        
        # Read the updated GUANO chunk
        temp_chunks = read_wav_chunks(tmp_path)
        guano_chunk_data = None
        
        for chunk in temp_chunks:
            if chunk.chunk_id == b'guan':
                guano_chunk_data = chunk.data
                break
        
        if guano_chunk_data is None:
            raise ValueError("Could not extract GUANO chunk from temporary file")
        
        # Update GUANO chunk in original chunks
        updated_chunks = update_guano_chunk(original_chunks, guano_chunk_data)
        
        # Write to a new temp file first, then atomically replace the original.
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False, dir=Path(filepath).parent) as tmp2:
            tmp_path2 = tmp2.name

        try:
            write_wav_with_chunks(tmp_path2, updated_chunks)
            shutil.move(tmp_path2, filepath)
        except Exception:
            # Clean up the second temp file on failure so it doesn't linger
            # in the user's recording directory.
            try:
                Path(tmp_path2).unlink()
            except OSError:
                pass
            raise

        logger.info(f"Successfully updated {filepath} while preserving all chunks")

    finally:
        # Clean up the first temp file (used only to extract the GUANO chunk).
        try:
            Path(tmp_path).unlink()
        except OSError:
            pass
