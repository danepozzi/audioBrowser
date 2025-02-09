import os
import argparse
from flask import Flask, jsonify, send_from_directory, render_template, request
import json

app = Flask(__name__)

parser = argparse.ArgumentParser(description="Set the path to the audio folder")
parser.add_argument(
    '--audio-folder', 
    type=str, 
    required=True, 
    help="The path to the folder containing the audio files"
)

args = parser.parse_args()
AUDIO_FOLDER = args.audio_folder

@app.route('/')
def index():
    # Serve the index.html file from the templates folder
    return render_template('index.html')

@app.route('/list_audio_files')
def list_audio_files():
    # List to store the paths of audio files
    audio_files = []
    
    # Walk through the AUDIO_FOLDER and collect all .wav files
    for root, dirs, files in os.walk(AUDIO_FOLDER):
        for file in files:
            if file.endswith(".wav"):
                # Add the relative file path to the list
                audio_files.append(os.path.relpath(os.path.join(root, file), AUDIO_FOLDER))
    
    # Return the list of audio files as a JSON response
    return jsonify({"audio_files": audio_files})

@app.route('/audio/<path:filename>')
def serve_audio(filename):
    # Serve the audio file from the AUDIO_FOLDER
    return send_from_directory(AUDIO_FOLDER, filename)

@app.route('/transcription/<path:audio_filename>')
def serve_transcription(audio_filename):
    # Extract the base name of the audio file to find the json
    transcription_filename = audio_filename.replace(".wav", ".json")

    # Ensure the transcription file exists
    transcription_path = os.path.join(AUDIO_FOLDER, transcription_filename)
    
    if os.path.exists(transcription_path):
        # If the transcription file exists, return the transcription as a JSON response
        with open(transcription_path, 'r') as file:
            transcription_data = json.load(file)  # Load the entire JSON
        return jsonify(transcription_data), 200
    else:
        return jsonify({"error": "Transcription not found"}), 404

@app.route('/update_transcription/<path:audio_filename>', methods=['POST'])
def update_transcription(audio_filename):
    # Find the json
    transcription_filename = audio_filename.replace(".wav", ".json")

    transcription_path = os.path.join(AUDIO_FOLDER, transcription_filename)

    if os.path.exists(transcription_path):
        # Get the updated transcription data from the request
        updated_transcription = request.json.get('transcription')

        # Read the existing data to keep other fields intact
        try:
            with open(transcription_path, 'r') as file:
                existing_data = json.load(file)
            
            # Update the transcription part with the new transcription
            existing_data['transcript'] = updated_transcription

            # Write the updated data back to the file
            with open(transcription_path, 'w') as file:
                json.dump(existing_data, file, indent=4)
            
            return jsonify({"message": "Transcription updated successfully"}), 200
        except Exception as e:
            return jsonify({"error": f"Error saving transcription: {str(e)}"}), 500
    else:
        return jsonify({"error": "Transcription file not found"}), 404

@app.route('/add_annotation/<path:audio_filename>', methods=['POST'])
def add_annotation(audio_filename):
    # Find json
    transcription_filename = audio_filename.replace(".wav", ".json")

    transcription_path = os.path.join(AUDIO_FOLDER, transcription_filename)

    if os.path.exists(transcription_path):
        # Get the annotation data from the request
        new_annotation = request.json.get('annotation')

        # Read the existing data to keep other fields intact
        try:
            with open(transcription_path, 'r') as file:
                existing_data = json.load(file)
            
            # Add the new annotation to the annotations field
            if 'annotations' not in existing_data:
                existing_data['annotations'] = []  # Initialize if the field doesn't exist

            existing_data['annotations'].append(new_annotation)

            # Write the updated data back to the file
            with open(transcription_path, 'w') as file:
                json.dump(existing_data, file, indent=4)
            
            return jsonify({"message": "Annotation added successfully"}), 200
        except Exception as e:
            return jsonify({"error": f"Error saving annotation: {str(e)}"}), 500
    else:
        return jsonify({"error": "Transcription file not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)