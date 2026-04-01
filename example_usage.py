"""
Quick Start Example for GUANO Metadata Manager

This script demonstrates basic usage of the metadata manager without the GUI.
"""

from guano_metadata_manager import (
    GuanoMetadataManager,
    GUANO_STANDARD_FIELDS,
    GUANO_RESERVED_NAMESPACES,
)

def main():
    # Create manager instance
    manager = GuanoMetadataManager()
    
    # Example 1: Load files from a directory
    print("Example 1: Loading files from a directory")
    print("-" * 50)
    
    directory = "/path/to/your/wav/files"  # Change this!
    
    # Optional: Use progress callback to track loading
    def progress_callback(current, total):
        print(f"\rLoading: {current}/{total} files", end='', flush=True)
    
    count, errors = manager.load_directory(directory, progress_callback=progress_callback)
    print()  # New line after progress
    
    print(f"Loaded {count} files")
    if errors:
        print(f"Warnings/errors: {len(errors)}")
        for error in errors[:3]:
            print(f"  - {error}")
    
    if count == 0:
        print("No files loaded. Please check the directory path.")
        return
    
    # Example 2: View common fields
    print("\nExample 2: Common fields (same across all files)")
    print("-" * 50)
    
    common = manager.get_common_fields()
    for field, value in sorted(common.items()):
        print(f"{field}: {value}")
    
    # Example 3: View variable fields
    print("\nExample 3: Variable fields (differ between files)")
    print("-" * 50)
    
    variable = manager.get_variable_fields()
    for field, values in sorted(variable.items()):
        print(f"\n{field}:")
        for filename, value in values[:3]:  # Show first 3
            print(f"  {filename}: {value}")
        if len(values) > 3:
            print(f"  ... and {len(values) - 3} more")
    
    # Example 4: Update common fields
    print("\nExample 4: Updating common fields")
    print("-" * 50)
    print("⚠️  IMPORTANT: Always maintain your own backups before modifying files!")
    print()
    
    # Example updates (uncomment and modify as needed)
    updates = {
        # 'Species Manual ID': 'Myotis lucifugus',  # Update species
        # 'Site Name': 'Research Site A',  # Update site name
        # 'Note': 'Processed batch 2026-04-01',  # Add a note
    }
    
    if updates:
        def update_progress(current, total):
            print(f"\rUpdating: {current}/{total} files", end='', flush=True)
        
        updated_count, errors = manager.update_common_fields(updates, progress_callback=update_progress)
        print()  # New line after progress
        print(f"Updated {updated_count} files")
        if errors:
            print(f"Errors: {len(errors)}")
            for error in errors:
                print(f"  - {error}")
    else:
        print("No updates configured (uncomment and modify the updates dict)")

    # Example 5: Add new fields
    print("\nExample 6: Adding new fields")
    print("-" * 50)

    # Show all5: Add new fields
    print("\nExample 5ANO fields (from the spec):")
    for name, info in sorted(GUANO_STANDARD_FIELDS.items()):
        req = " [required]" if info["required"] else " [optional]"
        print(f"  {name:<22}  type: {info['type']:<18}{req}")
        print(f"    {info['description']}")

    print("\nRegistered GUANO namespaces:")
    for ns, desc in sorted(GUANO_RESERVED_NAMESPACES.items()):
        print(f"  {ns:<10}  {desc}")

    # To add a new standard field, just pass it to update_common_fields.
    # It will be written to every loaded file.
    #
    # Standard field example:
    #   updated_count, errors = manager.update_common_fields({
    #       'Humidity': '65.5',
    #   })
    #
    # Custom (namespaced) field example — use 'User' for personal fields:
    #   updated_count, errors = manager.update_common_fields({
    #       'User|Survey Site': 'Mammoth Cave National Park',
    #   })
    #
    # update_common_fields handles both new and existing fields.
    # Passing None or an empty string as the value will DELETE the field.
    print("\nTo add a field, call update_common_fields with the new field name and value.")
    print("See the commented-out examples above for reference.")

    print("\n" + "=" * 50)
    print("Done! Use guano_gui.py for interactive editing.")


if __name__ == "__main__":
    main()
