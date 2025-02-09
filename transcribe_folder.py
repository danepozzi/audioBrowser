import os
import argparse
from transcribe import transcribe_audio

def find_files_to_transcribe(root_dir):
    """Find all .wav files."""
    files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.startswith('.'):
                print(f"Skipping: {filename}")
                continue
            if filename.endswith(".wav"):
                file_path = os.path.join(dirpath, filename)
                files.append(file_path)
    return files

def main(root_dir):
    audio_files = find_files_to_transcribe(root_dir)
    
    total_files = len(audio_files)
    if total_files == 0:
        print("No .wav files found.")
        return
    
    print(f"Found {total_files} .wav files. Starting transcription...")
    
    # Transcribe each file and track progress
    for i, audio_file in enumerate(audio_files, start=1):
        json_file = audio_file.replace('.wav', '.json')
        if os.path.exists(json_file):
            print(f"Skipping {audio_file}, transcription already exists.")
            continue
        
        print(f"Transcribing audio file {i}/{total_files}...")
        transcribe_audio(audio_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe all .wav files in a given directory.")
    parser.add_argument("root_directory", type=str, help="Root directory to scan for audio files.")
    args = parser.parse_args()
    
    main(args.root_directory)