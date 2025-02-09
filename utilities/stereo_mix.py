import os
import subprocess
import sys

ROOT_DIR = ""

# valid mono file extensions
AUDIO_EXTENSIONS = (".wav", ".mp3", ".flac", ".aac", ".ogg", ".m4a")

def find_audio_files(folder):
    """Find all mono audio files in a given folder."""
    mono_files = [f for f in os.listdir(folder) if f.lower().endswith(AUDIO_EXTENSIONS)]
    mono_files = [os.path.join(folder, f) for f in mono_files]
    
    # Filter only mono files (FFmpeg check)
    mono_files = [f for f in mono_files if is_mono(f)]
    
    return mono_files

def is_mono(file_path):
    """Check if an audio file is mono using FFmpeg."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=channels",
             "-of", "csv=p=0", file_path],
            capture_output=True, text=True
        )
        return result.stdout.strip() == "1"  # Mono if output is "1"
    except Exception as e:
        print(f"Error checking {file_path}: {e}")
        return False

def mixdown_mono_files(mono_files, output_file):
    """Mix multiple mono files into a stereo file using FFmpeg, force overwriting output."""
    
    if os.path.exists(output_file):
        os.remove(output_file)  # Ensure clean overwrite

    input_args = []
    for file in mono_files:
        input_args.extend(["-i", file])

    # mix all mono files into stereo
    filter_complex = f"{''.join([f'[{i}:a]' for i in range(len(mono_files))])}amix=inputs={len(mono_files)}:normalize=0[aout]"

    cmd = [
        "ffmpeg", *input_args,
        "-filter_complex", filter_complex,
        "-map", "[aout]",  # output mapping
        "-ac", "2",
        "-y",  # overwrite output
        output_file
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"Mixed down to: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error processing {mono_files}: {e}")

def process_folders(root_dir):
    """Cycle through all subdirectories and mix mono files if needed."""
    for folder, _, _ in os.walk(root_dir):
        mono_files = find_audio_files(folder)

        if len(mono_files) in [3, 4]:
            output_file = os.path.join(folder, "mixed_stereo.wav")
            
            if not os.path.exists(output_file):  # Avoid overwriting
                print(f"Mixing {len(mono_files)} mono files in {folder}...")
                mixdown_mono_files(mono_files, output_file)
            else:
                print(f"⚠️ Stereo file already exists in {folder}, reprocessing...")
                mixdown_mono_files(mono_files, output_file)

if __name__ == "__main__":
    if not os.path.exists(ROOT_DIR):
        print(f"Error: Root directory '{ROOT_DIR}' not found.")
        sys.exit(1)

    process_folders(ROOT_DIR)
    print("All folders processed!")