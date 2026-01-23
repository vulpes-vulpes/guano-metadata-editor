#!/usr/bin/env python3
"""
LIST Chunk Parser

Reads and displays the contents of LIST chunks in WAV files.
LIST chunks typically contain INFO metadata.
"""

import struct
import sys
from pathlib import Path


def parse_list_chunk(data):
    """
    Parse a LIST chunk's data.
    
    LIST chunks have format:
    - 4 bytes: list type (e.g., 'INFO')
    - followed by subchunks
    """
    if len(data) < 4:
        return {}
    
    list_type = data[0:4].decode('ascii', errors='replace')
    print(f"\nLIST Type: '{list_type}'")
    print("-" * 60)
    
    fields = {}
    pos = 4
    
    while pos < len(data) - 8:
        # Read subchunk ID and size
        chunk_id = data[pos:pos+4]
        if len(chunk_id) < 4:
            break
        
        chunk_id_str = chunk_id.decode('ascii', errors='replace')
        chunk_size = struct.unpack('<I', data[pos+4:pos+8])[0]
        pos += 8
        
        if pos + chunk_size > len(data):
            print(f"Warning: subchunk {chunk_id_str} extends beyond LIST data")
            break
        
        chunk_data = data[pos:pos+chunk_size]
        pos += chunk_size
        
        # Word-align
        if chunk_size % 2:
            pos += 1
        
        # Try to decode as text
        try:
            value = chunk_data.rstrip(b'\x00').decode('utf-8', errors='replace')
        except:
            value = f"<binary data, {len(chunk_data)} bytes>"
        
        fields[chunk_id_str] = value
        print(f"{chunk_id_str}: {value}")
    
    return fields


def read_list_chunks_from_file(filepath):
    """Read and parse all LIST chunks from a WAV file."""
    print(f"Reading LIST chunks from: {filepath}")
    print("=" * 60)
    
    list_count = 0
    
    with open(filepath, 'rb') as f:
        # Read RIFF header
        riff = f.read(4)
        if riff != b'RIFF':
            print("Not a RIFF file")
            return
        
        file_size = struct.unpack('<I', f.read(4))[0]
        wave = f.read(4)
        if wave != b'WAVE':
            print("Not a WAVE file")
            return
        
        # Read all chunks
        while True:
            chunk_id = f.read(4)
            if len(chunk_id) < 4:
                break
            
            chunk_size = struct.unpack('<I', f.read(4))[0]
            chunk_data = f.read(chunk_size)
            
            if chunk_id == b'LIST':
                list_count += 1
                print(f"\n{'='*60}")
                print(f"LIST Chunk #{list_count} (Size: {chunk_size} bytes)")
                print(f"{'='*60}")
                parse_list_chunk(chunk_data)
            
            # Skip padding byte if odd size
            if chunk_size % 2:
                f.read(1)
    
    if list_count == 0:
        print("\nNo LIST chunks found in this file.")
    else:
        print(f"\n{'='*60}")
        print(f"Total LIST chunks found: {list_count}")


# Common LIST/INFO field meanings
INFO_FIELD_DESCRIPTIONS = {
    'INAM': 'Title/Name',
    'IART': 'Artist',
    'ICMT': 'Comment',
    'ICOP': 'Copyright',
    'ICRD': 'Creation Date',
    'IGNR': 'Genre',
    'IPRD': 'Product/Album',
    'ISBJ': 'Subject',
    'ISFT': 'Software',
    'ISRC': 'Source',
    'ITCH': 'Technician/Engineer',
    'IKEY': 'Keywords',
    'IMED': 'Medium',
    'ISRF': 'Source Form',
}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print(f"  {sys.argv[0]} <wavfile>")
        print("\nThis script reads and displays LIST chunk metadata from WAV files.")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    if not Path(filepath).exists():
        print(f"File not found: {filepath}")
        sys.exit(1)
    
    read_list_chunks_from_file(filepath)
    
    print("\n\nCommon INFO Field Meanings:")
    print("-" * 60)
    for code, description in sorted(INFO_FIELD_DESCRIPTIONS.items()):
        print(f"{code}: {description}")
