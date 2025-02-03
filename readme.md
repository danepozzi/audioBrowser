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

We need to mix down everything to stereo wav.
```
python3 stereo_mix.py
```
Cycles throguh folders, if it finds groups of mono files it mixes them down to stereo wav. These files will end with "mixed_stereo.wav"
```
python3 rename_to_path.py
```
Ensures all mixed stereos are properly named.

## Transcription

Transcription uses whisper from openAI. 
```
python3 transcribe_folder.py
```
Will look for all files ending with "mixed_stereo.wav" in the specified folder and run transcription. It generates a txt and a json.

### Notes
Metal Performance Shaders don't work out of the box for official whisper (missing torch implementations). I tried unofficial implementations, like [lightning whisper](https://github.com/mustafaaljadery/lightning-whisper-mlx) but transcription quality is not as good. I ended up running whisper entirely on CPU: roughly 6 minutes of audio are transcribed in 1 minute, which is probably ok.

## Audio Browser:
An interface to browse sound file, along with generated transciptions. It allows to edit and annotate trancsiptions, using a flask app as backend to manipulate json files and serve audio files.
```
python3 flaskapp.py
```
Then visit: [http://127.0.0.1:5000](http://127.0.0.1:5000)