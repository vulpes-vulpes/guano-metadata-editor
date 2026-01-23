#!/usr/bin/env python3
"""
Diagnostic script to inspect WAV file chunks and test metadata preservation.
"""

import struct
import sys
from pathlib import Path

def read_wav_chunks(filepath):
    """Read and display all chunks in a WAV file."""
    chunks = []
    
    with open(filepath, 'rb') as f:
        # Read RIFF header
        riff = f.read(4)
        if riff != b'RIFF':
            print(f"Not a RIFF file: {riff}")
            return chunks
        
        file_size = struct.unpack('<I', f.read(4))[0]
        wave = f.read(4)
        if wave != b'WAVE':
            print(f"Not a WAVE file: {wave}")
            return chunks
        
        print(f"RIFF WAVE file, declared size: {file_size} bytes")
        print("\nChunks found:")
        print("-" * 60)
        
        # Read all chunks
        while True:
            chunk_id = f.read(4)
            if len(chunk_id) < 4:
                break
            
            chunk_size = struct.unpack('<I', f.read(4))[0]
            chunk_data_pos = f.tell()
            
            chunk_info = {
                'id': chunk_id.decode('ascii', errors='replace'),
                'size': chunk_size,
                'position': chunk_data_pos
            }
            chunks.append(chunk_info)
            
            # Display chunk info
            print(f"Chunk: '{chunk_info['id']}'  Size: {chunk_size:,} bytes  Position: {chunk_data_pos}")
            
            # Read first few bytes as preview for metadata chunks
            if chunk_info['id'] in ['guan', 'wamd', 'bext', 'iXML']:
                preview = f.read(min(100, chunk_size))
                f.seek(chunk_data_pos)  # Reset position
                try:
                    preview_text = preview.decode('utf-8', errors='ignore')[:80]
                    print(f"  Preview: {preview_text}")
                except:
                    pass
            
            # Skip to next chunk (chunks are word-aligned)
            f.seek(chunk_data_pos + chunk_size + (chunk_size % 2))
    
    return chunks

def compare_chunks(file1, file2):
    """Compare chunks between two files."""
    chunks1 = read_wav_chunks(file1)
    chunks2 = read_wav_chunks(file2)
    
    ids1 = set(c['id'] for c in chunks1)
    ids2 = set(c['id'] for c in chunks2)
    
    print("\n" + "=" * 60)
    print("COMPARISON:")
    print("=" * 60)
    
    lost = ids1 - ids2
    gained = ids2 - ids1
    
    if lost:
        print(f"\n⚠️  CHUNKS LOST: {', '.join(lost)}")
    if gained:
        print(f"\n✓  CHUNKS GAINED: {', '.join(gained)}")
    if not lost and not gained:
        print("\n✓  All chunks preserved")
    
    return lost, gained

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print(f"  {sys.argv[0]} <wavfile>                    # Inspect a file")
        print(f"  {sys.argv[0]} <original> <modified>        # Compare files")
        sys.exit(1)
    
    file1 = sys.argv[1]
    
    if len(sys.argv) == 2:
        # Single file inspection
        print(f"Inspecting: {file1}")
        print("=" * 60)
        read_wav_chunks(file1)
    else:
        # File comparison
        file2 = sys.argv[2]
        print(f"ORIGINAL: {file1}")
        print("=" * 60)
        read_wav_chunks(file1)
        
        print("\n\n")
        print(f"MODIFIED: {file2}")
        print("=" * 60)
        read_wav_chunks(file2)
        
        compare_chunks(file1, file2)
