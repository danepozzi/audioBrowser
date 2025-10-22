# Audio Browser

Tools to transcribe, edit and annotate audio files.

## Transcription
Transcription uses whisper from openAI. To transcribe a single file:
```
python transcribe_audio.py /path/to/file -d /destination/folder
```
```
python transcribe.py /path/to/file.wav
```
To transcibe all .wav files in a given folder:
```
python transcribe_folder.py /path/to/folder
```


## Audio Browser:
```
python audio_browser.py --audio-folder /path/to/audio/folder
```
Then visit: [http://127.0.0.1:5000](http://127.0.0.1:5000)
