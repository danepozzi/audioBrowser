import ffmpeg
import time
import itertools
import whisper
import json
import os
import re
from datetime import datetime
from pathlib import Path

def transcribe_audio(audio_path):
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"File not found: {audio_path}")

    print(f"Processing audio file: {audio_path}")

    start_time = time.time()

    filename = os.path.basename(audio_path)
    date_match = re.match(r"^(\d{6,8})[-_]", filename)
    date = date_match.group(1) if date_match else "unknown"
    notes = filename.replace(f"{date}-", "").replace("_mixed_stereo.wav", "")

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
        "notes": notes,
        "transcript": []
    }
    parent_dir = str(Path(audio_path).parent)

    # Write the cleaned transcription to a text file and add it to the JSON data
    with open(parent_dir + "/transcription.txt", "w", encoding="utf-8") as txt_file:
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

    json_file_path = parent_dir + f"/{filename}.json"
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(json_data, json_file, indent=4)

    print(f"Transcription completed in {elapsed_time:.2f} seconds (~{elapsed_time/60:.2f} minutes).")
    print(f"Transcription text saved to 'transcription.txt'")
    print(f"Transcription JSON saved to 'transcription.json'")

if __name__ == "__main__":
    audio_path = "/path/to/your/audio/file.wav"  # Only needed if running the script directly
    transcribe_audio(audio_path)