import argparse
import os

def rename_files(root_directory):
    for dirpath, _, filenames in os.walk(root_directory):
        for filename in filenames:
            # Skip hidden AppleDouble files (._)
            if filename.startswith("._"):
                continue

            # Check if it's a .wav file
            if filename.lower().endswith(".wav"):
                # Get the relative path of the current directory from the root
                relative_path = os.path.relpath(dirpath, root_directory)

                # Replace path separators with underscores
                parent_folders = relative_path.replace(os.path.sep, "_")
                
                # Construct the new filename
                new_filename = f"{parent_folders}_{filename}"
                
                # Get full file paths
                old_file_path = os.path.join(dirpath, filename)
                new_file_path = os.path.join(dirpath, new_filename)

                # Rename only if new filename doesn't exist
                if not os.path.exists(new_file_path):
                    os.rename(old_file_path, new_file_path)
                    print(f"Renamed: {old_file_path} -> {new_file_path}")
                else:
                    print(f"Skipping (file already exists): {new_file_path}")

def main(root_dir):
    if not os.path.isdir(root_dir):
        print("Invalid folder path.")
        return
    rename_files(root_dir)
    print("Processing complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rename .wav files in a specified folder.")
    parser.add_argument("folder", type=str, help="Path to the folder to process")
    args = parser.parse_args()
    main(args.folder)
