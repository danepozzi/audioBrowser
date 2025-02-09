import os
import subprocess
import argparse

def convert_to_wav(input_file, output_file):
    """Convert an audio file to WAV format using FFmpeg."""
    try:
        subprocess.run(["ffmpeg", "-i", input_file, "-acodec", "pcm_s16le", "-ar", "44100", output_file], 
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Converted: {input_file} -> {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting {input_file}: {e}")

def process_folder(folder):
    """Recursively process a folder to find and convert non-WAV audio files."""
    for root, _, files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            if file.lower().endswith(".wav"):
                continue
            
            output_file = os.path.splitext(file_path)[0] + ".wav"
            
            if not os.path.exists(output_file):
                convert_to_wav(file_path, output_file)

def main(root_dir):
    folder = root_dir.strip()
    
    if not os.path.isdir(folder):
        print("Invalid folder path.")
        return
    
    process_folder(folder)
    print("Processing complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a specified folder.")
    parser.add_argument("folder", type=str, help="Path to the folder to process")
    args = parser.parse_args()
    main(args.folder)

