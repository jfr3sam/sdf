import concurrent.futures
import gzip
import json
import logging
import os
import shutil
import time

import cv2
import numpy as np
import requests
from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
CHUNK_SIZE = 1024 * 1024  # 1MB chunks
HISTORY_FILE = 'processing_history.json'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_to_history(data):
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
    else:
        history = []
    
    history.append(data)
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['video']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/process', methods=['POST'])
def process_file():
    try:
        data = request.json
        filename = data['filename']
        option = data['option']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        start_time = time.time()
        
        if option == 'send':
            result = send_to_receiver(file_path, option)
        elif option == 'compress':
            compression_level = int(data.get('compressionLevel', 6))
            compressed_path = compress_file(file_path, compression_level)
            result = send_to_receiver(compressed_path, option)
        elif option == 'split':
            chunks = split_file(file_path)
            result = send_to_receiver(chunks, option)
        elif option == 'parallel_split':
            result = send_to_receiver(file_path, option)
        else:
            result = {'error': 'Invalid option'}
        
        end_time = time.time()
        result['time'] = end_time - start_time
        result['filename'] = filename
        result['option'] = option
        
        save_to_history(result)
        
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error in process_file: {str(e)}")
        return jsonify({'error': str(e)}), 500

def send_chunk(chunk, chunk_num, option):
    try:
        files = {'chunk': (f'chunk_{chunk_num}', chunk)}
        response = requests.post('http://localhost:5001/receive_chunk', 
                                files=files, 
                                data={'option': option, 'chunk_num': chunk_num})
        return response.status_code == 200
    except requests.RequestException:
        return False

def send_to_receiver(data, option):
    try:
        if option in ['send', 'compress']:
            with open(data, 'rb') as file:
                files = {'video': (os.path.basename(data), file)}
                response = requests.post('http://localhost:5001/receive', files=files, data={'option': option})
        elif option == 'split':
            files = [('chunks', (f'chunk_{i}', chunk)) for i, chunk in enumerate(data)]
            response = requests.post('http://localhost:5001/receive', files=files, data={'option': option})
        elif option == 'parallel_split':
            chunks = split_file(data)
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(send_chunk, chunk, i, option) 
                            for i, chunk in enumerate(chunks)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            if all(results):
                return {'message': 'All chunks sent successfully using parallel transmission'}
            else:
                return {'error': 'Some chunks failed to send during parallel transmission'}
        elif option in ['frame_difference', 'adaptive_encoding']:
            response = requests.post('http://localhost:5001/receive', json={'frames': data.tolist(), 'option': option})
        else:
            return {'error': 'Invalid option'}

        if response.status_code == 200:
            return {'message': f'File sent to receiver successfully using {option} method'}
        else:
            return {'error': f'Failed to send file to receiver. Status code: {response.status_code}'}
    except requests.RequestException as e:
        logging.error(f"Error in send_to_receiver: {str(e)}")
        return {'error': f'Failed to connect to receiver: {str(e)}'}

def compress_file(file_path, level):
    compressed_path = f"{file_path}.gz"
    with open(file_path, 'rb') as f_in:
        with gzip.open(compressed_path, 'wb', compresslevel=level) as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    return compressed_path

def split_file(file_path, chunk_size=CHUNK_SIZE):
    chunks = []
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            chunks.append(chunk)
    return chunks

@app.route('/history', methods=['GET'])
def get_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
        return jsonify(history)
    else:
        return jsonify([])

@app.route('/clear_history', methods=['POST'])
def clear_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
        return jsonify({'message': 'History cleared successfully'}), 200
    else:
        return jsonify({'message': 'No history to clear'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)