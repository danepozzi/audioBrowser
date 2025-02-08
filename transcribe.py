import ffmpeg
import time
import itertools
import whisper
import json
import os
import re
from datetime import datetime
from pathlib import Path
import argparse
import sys

def transcribe_audio(audio_path):
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"File not found: {audio_path}")

    print(f"Processing audio file: {audio_path}")

    start_time = time.time()

    filename = os.path.basename(audio_path)
    filename_without_extension = os.path.splitext(filename)[0]
    date_match = re.match(r"^(\d{6,8})[-_]", filename)
    date = date_match.group(1) if date_match else "unknown"

    place_match = filename.split('_')[1]
    place = place_match if place_match else "unknown"   

    notes = filename.split('_', 2)[-1]
    notes = notes.replace(".wav", "")
    notes = re.sub(r'_Ste_\d{3}$', '', notes)  # Remove record infos
    notes = re.sub(r'_Neue_Aufnahme_\d+$', '', notes)
    
    print("Date:", date)
    print("Place:", place)
    print("Notes:", notes)

    # Get audio duration using ffmpeg
    probe = ffmpeg.probe(audio_path, v='error', select_streams='a', show_entries='stream=duration')
    audio_duration_seconds = float(probe['streams'][0]['duration'])
    audio_duration_minutes = audio_duration_seconds / 60

    processing_speed = 5.642  # Minutes of audio processed per minute of processing
    estimated_processing_time = audio_duration_minutes / processing_speed 

    print(f"Audio duration: {audio_duration_minutes:.2f} minutes")
    print(f"Estimated processing time: {estimated_processing_time:.2f} minutes")

    expected_end_time = start_time + (estimated_processing_time * 60)
    end_time_human_readable = datetime.fromtimestamp(expected_end_time).strftime('%Y-%m-%d %H:%M:%S')

    print(f"Running whisper. Expected completion time: {end_time_human_readable}")

    model = whisper.load_model("medium")

    print(f"Transcribing... This may take a while.")

    result = model.transcribe(
        audio_path, 
        word_timestamps=False,  # True enables word-level timestamps
        temperature=0.2,  # set to 0 for deterministic results (5-10% faster)
        beam_size=5,       # set to 1 to disable beam search (30-50% faster)
        fp16=False          # set to True to use mixed-precision (GPU only)
    )

    end_time = time.time()
    elapsed_time = end_time - start_time

    def remove_consecutive_duplicates(transcription):
        return [key for key, _ in itertools.groupby(transcription)]

    cleaned_transcription = remove_consecutive_duplicates(result['segments'])

    json_data = {
        "path": audio_path,
        "duration": audio_duration_minutes,
        "date": date,
        "place": place,
        "notes": notes,
        "transcript": []
    }
    parent_dir = str(Path(audio_path).parent)

    # Write the cleaned transcription to a text file and add it to the JSON data
    with open(parent_dir + f"/{filename_without_extension}.txt", "w", encoding="utf-8") as txt_file:
        for segment in cleaned_transcription:
            start_time = segment["start"]
            end_time = segment["end"]
            text = segment["text"]

            # Convert to HH:MM:SS format for the text file
            start_hms = f"{int(start_time // 3600):02}:{int((start_time % 3600) // 60):02}:{int(start_time % 60):02}"
            end_hms = f"{int(end_time // 3600):02}:{int((end_time % 3600) // 60):02}:{int(end_time % 60):02}"

            txt_file.write(f"[{start_hms} - {end_hms}] {text}\n")
            
            json_data["transcript"].append({
                "start": start_time,
                "end": end_time,
                "text": text
            })

    json_file_path = parent_dir + f"/{filename_without_extension}.json"
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(json_data, json_file, indent=4)

    print(f"Transcription completed in {elapsed_time:.2f} seconds (~{elapsed_time/60:.2f} minutes).")
    print(f"Transcription text saved to {filename_without_extension}.txt")
    print(f"Transcription JSON saved to {filename_without_extension}.json'")

def check_audio_path(audio_path):
    if not os.path.exists(audio_path):
        print(f"Error: The file '{audio_path}' does not exist.")
        return False

    if not audio_path.endswith(".wav"):
        print("Error: The file must have a '.wav' extension.")
        return False

    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Transcribe audio file and extract metadata from the filename.",
        usage="%(prog)s [audio_path]",
    )
    parser.add_argument(
        'audio_path', type=str, nargs='?', help="Path to the audio file. Example: '/path/to/file.wav'"
    )

    args = parser.parse_args()

    if not args.audio_path:
        print("Warning: No audio path provided. Please provide the path to a .wav file.")
        sys.exit(1)
    
    if check_audio_path(args.audio_path):
        transcribe_audio(args.audio_path)