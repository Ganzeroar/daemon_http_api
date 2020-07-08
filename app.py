from flask import Flask, jsonify, request, send_from_directory
import werkzeug
from werkzeug.utils import secure_filename
import hashlib
import os
import sys

import files_db

app = Flask(__name__)

current_file_path = os.getcwd() + '/store/'

@app.route('/delete/<hash_id>', methods=['DELETE'])
def delete_file(hash_id): 
    file_hash = secure_filename(hash_id)
    file_name = files_db.get_name_using_hash(file_hash)
    path_to_file = files_db.get_path_to_file_using_hash(file_hash)

    directory_name = file_hash[:2]
    existing_directory = os.listdir(current_file_path)

    path_to_exist_files = current_file_path + directory_name

    if directory_name in existing_directory:
        existing_files = os.listdir(path_to_exist_files)
        if file_name in existing_files:
            files_db.delete_file_using_hash(file_hash)
            os.remove(path_to_exist_files + '/' + file_name)
            return 'file was deleted'
        else:
            return 'file not found'
    else:
        return 'file not found'

@app.route('/download/<hash_id>', methods=['GET'])
def download_file(hash_id):
    file_hash = secure_filename(hash_id)

    directory_name = file_hash[:2]
    existing_directory = os.listdir(current_file_path)

    path_to_exist_files = current_file_path + directory_name
    
    if directory_name in existing_directory:
        existing_files = os.listdir(path_to_exist_files)
        file_name = files_db.get_name_using_hash(file_hash) 
        if file_name in existing_files:
            return send_from_directory(path_to_exist_files, file_name, as_attachment=True)
        else:
            return 'file_not_found'
    else:
        return 'file_not_found'

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        user_file = request.files["file"]
    except werkzeug.exceptions.BadRequestKeyError as e:
        return 'No files to download'
        
    file_name = secure_filename(user_file.filename)
    file_hash = hashlib.md5(file_name.encode('utf-8')).hexdigest()

    file_hash_from_db = files_db.get_all_file_hashes()
    if file_hash in file_hash_from_db:
        return 'this file already exist'

    directory_name = str(file_hash[:2])
    existing_directory = os.listdir(current_file_path)
    path_to_exist_files = current_file_path + directory_name
        
    if directory_name not in existing_directory:
        os.mkdir(path_to_exist_files)
    path_to_file = path_to_exist_files
    files_db.insert_file_name_and_hash(file_name, file_hash, path_to_file)
    user_file.save(os.path.join(path_to_file, file_name))

    return jsonify({'hash':file_hash})
    

if __name__ == '__main__':
    app.run(debug=True)