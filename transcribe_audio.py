import ffmpeg
import time
import itertools
import whisper
import json
import os
from datetime import datetime
from pathlib import Path
import argparse
import sys

AUDIO_EXTENSIONS = (".wav", ".mp3", ".flac", ".aac", ".ogg", ".m4a", ".aiff")

def convert_to_wav(input_file, output_file):
    try:
        (
            ffmpeg
            .input(input_file)
            .output(output_file, acodec='pcm_s16le', ar=16000) #whisper resamples anyway to 16k
            .overwrite_output()
            .run(quiet=True)
        )
        print(f"Converted: {input_file} -> {output_file}")
    except ffmpeg.Error as e:
        print(f"Error converting {input_file}: {e}")

def transcribe_audio(audio_path, destination_folder=None):
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"File not found: {audio_path}")

    _, ext = os.path.splitext(audio_path)
    if ext.lower() not in AUDIO_EXTENSIONS:
        raise ValueError(
            f"Not an audio file: {', '.join(AUDIO_EXTENSIONS)}"
        )

    if ext.lower() != ".wav":
        print(f"Converting {ext} to .wav")
        filename_without_ext = os.path.splitext(audio_path)[0]
        wav_path = f"{filename_without_ext}.wav"
        convert_to_wav(audio_path, wav_path)
        audio_path = wav_path 
        print(f"Conversion complete: {wav_path}")

    print(f"Processing audio file: {audio_path}")

    start_time = time.time()

    filename = os.path.basename(audio_path)
    filename_without_extension = os.path.splitext(filename)[0]

    probe = ffmpeg.probe(audio_path, v='error', select_streams='a', show_entries='stream=duration')
    audio_duration_seconds = float(probe['streams'][0]['duration'])
    audio_duration_minutes = audio_duration_seconds / 60

    processing_speed = 5.642  # rough estimation on my laptop
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
        "file": audio_path,
        "duration": audio_duration_minutes,
        "transcript": []
    }

    if destination_folder:
        output_dir = destination_folder
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = str(Path(audio_path).parent)

    with open(os.path.join(output_dir, f"{filename_without_extension}.txt"), "w", encoding="utf-8") as txt_file:
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

    json_file_path = os.path.join(output_dir, f"{filename_without_extension}.json")
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(json_data, json_file, indent=4)

    print(f"Transcription completed in {elapsed_time:.2f} seconds (~{elapsed_time/60:.2f} minutes).")
    print(f"Transcription text saved to {os.path.join(output_dir, filename_without_extension + '.txt')}")
    print(f"Transcription JSON saved to {os.path.join(output_dir, filename_without_extension + '.json')}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Transcribe audio file.",
        usage="%(prog)s [audio_path] [-d destination_folder]",
    )
    parser.add_argument(
        'audio_path', type=str, nargs='?', help="Path to the audio file. Example: '/path/to/file.wav'"
    )
    parser.add_argument(
        '-d', '--destination', type=str, help="Destination folder for output files. If not specified, uses the same directory as the audio file."
    )

    args = parser.parse_args()

    if not args.audio_path:
        print("No audio path provided. Please provide the path to an audio file.")
        sys.exit(1)
    
    transcribe_audio(args.audio_path, args.destination)