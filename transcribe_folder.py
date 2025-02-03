import os
from transcribe import transcribe_audio  # Importing the function from transcribe.py

def find_files_to_transcribe(root_dir):
    """Find all files ending with 'mixed_stereo.wav'."""
    files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith("mixed_stereo.wav"):
                file_path = os.path.join(dirpath, filename)
                files.append(file_path)
    return files

def main():
    root_directory = '/Volumes/simularr-2/simularr/all_meetings/interval1'  # Change this to the root folder you want to start from

    # Find all the audio files to transcribe
    audio_files = find_files_to_transcribe(root_directory)

    # Track how many files were found
    total_files = len(audio_files)
    if total_files == 0:
        print("No 'mixed_stereo.wav' files found.")
        return

    print(f"Found {total_files} 'mixed_stereo.wav' files. Starting transcription...")

    # Transcribe each file and track progress
    for i, audio_file in enumerate(audio_files, start=1):
        json_file = audio_file.replace('.wav', '.json')  # Adjust based on your file naming
        if os.path.exists(json_file):
            print(f"Skipping {audio_file}, transcription already exists.")
            continue  # Skip transcription if JSON exists

        print(f"Transcribing audio file {i}/{total_files}...")
        transcribe_audio(audio_file)

if __name__ == "__main__":
    main()