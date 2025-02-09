# Simularr Audio Utilities

Tools to convert, mix and rename audio files, following simularr's naming conventions.

## Preprocess

Whisper works best with stereo wav files. If we have other formats, we first convert to wav:
```
python3 convert_to_wav.py /path/to/folder
```
If we have mono files (multitrack recordings), we mix them down to stereo:
```
python3 stereo_mix.py
```
This ensures all mixed stereos are properly named, following simularr's convention: XXMMDD_place_notes_recorderinfos.wav
```
python3 rename_to_path.py /path/to/folder
```
This capitalizes all words and substitutes all hypens and spaces with underscores. Results in: XXMMDD_Place_Notes_Recorderinfos.wav
```
python3 rename_files_titlecase.py /path/to/folder
```