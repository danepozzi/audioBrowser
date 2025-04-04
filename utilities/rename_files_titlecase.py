import os
import re
import time
import argparse

def format_filename(filename):
    """Reformats the filename by replacing '-' and spaces with an underscore, then capitalizing words properly."""
    name, ext = os.path.splitext(filename)  # Separate filename from extension
    name = re.sub(r'[-\s]+', '_', name)  # Replace hyphens and spaces with underscores
    name = "_".join([word.capitalize() for word in name.split("_")])  # Capitalize words correctly
    return f"{name}{ext}"  # Reattach extension

def rename_files_in_folder(folder):
    """Recursively renames files in the given folder."""
    for dirpath, _, filenames in os.walk(folder):
        for filename in filenames:
            # Skip AppleDouble files (hidden files starting with '._')
            if filename.startswith('._'):
                continue

            new_filename = format_filename(filename)

            if filename != new_filename:
                old_path = os.path.join(dirpath, filename)
                new_path = os.path.join(dirpath, new_filename)

                # Ensure the file exists before renaming
                if os.path.exists(old_path):
                    # Force rename even if the only change is case (macOS APFS fix)
                    temp_path = os.path.join(dirpath, f"temp_{int(time.time() * 1000)}{os.path.splitext(filename)[1]}")
                    os.rename(old_path, temp_path)
                    os.rename(temp_path, new_path)

                    print(f"Renamed: {old_path} -> {new_path}")
                else:
                    print(f"File not found: {old_path}")

def main(root_dir):
    folder = root_dir.strip()
    
    if not os.path.isdir(folder):
        print("Invalid folder path.")
        return
    
    rename_files_in_folder(folder)
    print("Processing complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rename files in a specified folder.")
    parser.add_argument("folder", type=str, help="Path to the folder to process")
    args = parser.parse_args()
    main(args.folder)
