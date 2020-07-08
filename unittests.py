import unittest
from unittest.mock import patch
import requests
import os
import shutil

import app
import files_db

IP_ADDRESS = 'http://127.0.0.1:5000'

class UploadTest(unittest.TestCase):
    '''тест загрузки файлов на сервер'''

    def setUp(self):
        try:
            files_db.create_db()
        except:
            files_db.drop_db()
            files_db.create_db

    def tearDown(self):
        try:
            files_db.drop_db()

            current_path = str(os.getcwd()) + '/store/'
            existing_directory = os.listdir(current_path)
            if existing_directory:
                for x in existing_directory:
                    shutil.rmtree(current_path+x)
        except Exception as e:
            print(e)
        
    def test_request_without_file_return_error_message(self):
        response = requests.post(IP_ADDRESS + "/upload") 
        self.assertEqual(response.text, 'No files to download')

    def test_request_with_file_return_200(self):
        with open('txt_files_for_test/first_test_file.txt', 'rb') as df:
            file_to_download = {'file' : ('first_test_file.txt', df.read())}
        response = requests.post(IP_ADDRESS + "/upload", files=file_to_download) 
        self.assertEqual(response.status_code, 200)

    def test_after_downloading_file_create_database_entry(self):
        with open('txt_files_for_test/first_test_file.txt', 'rb') as df:
            file_to_download = {'file' : ('first_test_file.txt', df.read())}
        response = requests.post(IP_ADDRESS + "/upload", files=file_to_download) 
        file_hash = response.json()['hash']

        data = files_db.get_all_file_names()
        path_to_file = files_db.get_path_to_file_using_hash(file_hash)
        existing_files = os.listdir(path_to_file)

        self.assertIn('first_test_file.txt', data)
        self.assertIn('first_test_file.txt', existing_files)

    def test_after_correct_request_create_directory(self):
        with open('txt_files_for_test/first_test_file.txt', 'rb') as df:
            file_to_download = {'file' : ('first_test_file.txt', df.read())}
        response = requests.post(IP_ADDRESS + "/upload", files=file_to_download) 
        file_hash = response.json()['hash']
        
        directory_names = os.listdir('store/')
        self.assertEqual(file_hash[:2], directory_names[0])

    def test_directory_with_correct_name_exist_dont_create_new(self):
        with open('txt_files_for_test/first_test_file.txt', 'rb') as df:
            file_to_download = {'file' : ('first_test_file.txt', df.read())}
        response = requests.post(IP_ADDRESS + "/upload", files=file_to_download) 
        directory_names = os.listdir('store/')
        self.assertEqual(len(directory_names), 1)
        
    def test_request_with_file_return_hash_of_created_file(self):
        with open('txt_files_for_test/first_test_file.txt', 'rb') as df:
            file_to_download = {'file' : ('first_test_file.txt', df.read())}
        response = requests.post(IP_ADDRESS + "/upload", files=file_to_download) 

        file_hash = response.json()['hash']
        file_name = files_db.get_name_using_hash(file_hash)

        directory_names = os.listdir('store/')
        created_directory = directory_names[0]
        created_file = os.listdir('store/'+created_directory)
        self.assertIn(file_name, created_file)
    
    def test_if_hash_already_in_db_return_error_message(self):
        with open('txt_files_for_test/first_test_file.txt', 'rb') as df:
            file_to_download = {'file' : ('first_test_file.txt', df.read())}
        response = requests.post(IP_ADDRESS + "/upload", files=file_to_download) 

        with open('txt_files_for_test/first_test_file.txt', 'rb') as df:
            file_to_download = {'file' : ('first_test_file.txt', df.read())}
        response = requests.post(IP_ADDRESS + "/upload", files=file_to_download) 

        self.assertEqual(response.text, 'this file already exist')

class DownloadTest(unittest.TestCase):
    '''тест скачивания файлов с сервера'''

    def setUp(self):
        try:
            files_db.create_db()
        except:
            pass
        with open('txt_files_for_test/first_test_file.txt', 'rb') as df:
            file_to_download = {'file' : ('first_test_file.txt', df.read())}
        response = requests.post(IP_ADDRESS + "/upload", files=file_to_download)
        
    def tearDown(self):
        try:
            files_db.drop_db()

            current_path = str(os.getcwd()) + '/store/'
            existing_directory = os.listdir(current_path)
            if existing_directory:
                for x in existing_directory:
                    shutil.rmtree(current_path+x)
        except Exception as e:
            print(e)

    def test_request_without_hash_return_404(self):
        response = requests.get(IP_ADDRESS + "/download/")
        self.assertEqual(response.status_code, 404)

    def test_request_with_bad_hash_return_error_message(self):
        response = requests.get(IP_ADDRESS + "/download/1a2b3c")
        self.assertEqual(response.text, 'file_not_found')

    def test_correct_request_with_hash_return_file(self):
        test_file_hash = files_db.get_all_file_hashes()
            
        response = requests.get(IP_ADDRESS + f"/download/{test_file_hash}")
        file_name = response.headers.get('content-disposition')[21:]
        self.assertEqual(file_name, 'first_test_file.txt')

    def test_correct_request_with_hash_return_and_download_file(self):
        test_file_hash = files_db.get_all_file_hashes()

        response = requests.get(IP_ADDRESS + f"/download/{test_file_hash}")
        file_name = response.headers.get('content-disposition')[21:]

        directory_name = file_name[:2]
        current_path = os.getcwd()

        with open(current_path+'/for_unit_tests/'+file_name, 'wb') as f:
            f.write(response.content)

        existing_files = os.listdir(current_path+'/for_unit_tests/')

        self.assertEqual(len(existing_files), 1)
        self.assertIn(file_name, existing_files)

    def test_in_downloaded_file_correct_data(self):
        test_file_hash = files_db.get_all_file_hashes()

        response = requests.get(IP_ADDRESS + f"/download/{test_file_hash}")
        file_name = response.headers.get('content-disposition')[21:]
        
        directory_name = file_name[:2]
        current_path = os.getcwd()

        with open(current_path+'/for_unit_tests/'+file_name, 'wb') as f:
            f.write(response.content)

        with open(current_path+'/for_unit_tests/'+file_name) as f:
            text = f.read()

        self.assertEqual(text, 'some test some file\n')

class DeleteTest(unittest.TestCase):
    '''тест удаления файлов на сервере'''

    def setUp(self):
        try:
            files_db.create_db()
        except:
            pass
        with open('txt_files_for_test/first_test_file.txt', 'rb') as df:
            file_to_download = {'file' : ('first_test_file.txt', df.read())}
        response = requests.post(IP_ADDRESS + "/upload", files=file_to_download)
    def tearDown(self):
        try:
            files_db.drop_db()

            current_path = str(os.getcwd()) + '/store/'
            existing_directory = os.listdir(current_path)
            if existing_directory:
                for x in existing_directory:
                    shutil.rmtree(current_path+x)
        except Exception as e:
            print(e)

    def test_request_without_hash_return_404(self):
        response = requests.delete(IP_ADDRESS + "/delete/")
        self.assertEqual(response.status_code, 404)
    
    def test_request_with_bad_hash_return_error_message(self):
        response = requests.delete(IP_ADDRESS + "/delete/1a2b3c")
        self.assertEqual(response.text, 'file not found')

    def test_correct_request_with_hash_return_message(self):
        test_file_hash = files_db.get_all_file_hashes()[0]
        response = requests.delete(IP_ADDRESS + f"/delete/{test_file_hash}")
        self.assertEqual(response.text, 'file was deleted')

    def test_correct_request_with_hash_delete_file(self):
        test_file_hash = files_db.get_all_file_hashes()
        existing_files_before = os.listdir('store/'+test_file_hash[0][:2])

        response = requests.delete(IP_ADDRESS + f"/delete/{test_file_hash}")
        
        existing_files_after = os.listdir('store/'+test_file_hash[0][:2])
        self.assertEqual(len(existing_files_before) -1, len(existing_files_after))

    def test_correct_request_with_hash_delete_data_in_database(self):
        test_file_hash_before = files_db.get_all_file_hashes()

        response = requests.delete(IP_ADDRESS + f"/delete/{test_file_hash_before}")
        
        test_file_hash_after = files_db.get_all_file_hashes()
        self.assertEqual(len(test_file_hash_before) -1, len(test_file_hash_after))

if __name__ == '__main__':
    unittest.main()