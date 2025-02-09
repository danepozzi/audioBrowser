# Simularr Audio Browser

Tools to transcribe, edit and annotate simularr audio files.

## Install
Linux
```
python -m venv venv
source venv/bin/activate
sudo apt install python3.13
pip install -r requirements.txt
```
OSX
```
python -m venv venv
source venv/bin/activate
brew install python@3.13
pip install -r requirements.txt
```

## Preprocess

See [Utilities](utilities/readme.md).

## Transcription

Transcription uses whisper from openAI. To transcribe a single file:
```
python3 transcribe.py /path/to/file.wav
```
To transcibe all .wav files in a given folder:
```
python3 transcribe_folder.py /path/to/folder
```
For each .wav a transcript is generated in .txt and .json format. The json file contains also infromations about date, place and notes about the recording, if the .wav file follows simularr's naming conventions (see [Utilities](utilities/readme.md)).

### Notes
Metal Performance Shaders don't work out of the box for official whisper (missing torch implementations). I tried unofficial implementations, like [lightning whisper](https://github.com/mustafaaljadery/lightning-whisper-mlx) but transcription quality is not as good. I ended up running whisper entirely on CPU: roughly 6 minutes of audio are transcribed in 1 minute, which is probably ok.

## Audio Browser:
An interface to browse sound file, along with generated transciptions. It allows to edit and annotate trancsiptions, using a flask app as backend to manipulate json files and serve audio files.
```
python3 audio_browser.py --audio-folder /path/to/audio/folder
```
Then visit: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Ideas
- Speaker diarization
- Topic modeling
- Search for a specific word
- Combine filters (interval, place, topic etc)