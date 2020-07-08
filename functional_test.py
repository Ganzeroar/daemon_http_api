import unittest
import requests
import os
import shutil
import time

import files_db

class FunctionalTest(unittest.TestCase):
    '''Хранилище файлов с доступом по http'''

    def setUp(self):
        try:
            files_db.create_db()
        except:
            files_db.drop_db()
            files_db.create_db
        with open('second_test_file.txt', 'rb') as df:
            file_to_download = {'file' : ('second_test_file.txt', df.read())}
        response = requests.post("http://127.0.0.1:5000/upload", files=file_to_download)

    def tearDown(self):
        try:
            files_db.drop_db()

            current_path = str(os.getcwd()) + '/store/'
            existing_directory = os.listdir(current_path)
            if existing_directory:
                for x in existing_directory:
                    shutil.rmtree(current_path+x)

            current_path = str(os.getcwd()) + '/for_unit_tests/'
            existing_directory = os.listdir(current_path)
            if existing_directory:
                for x in existing_directory:
                    os.remove(current_path+x)
        except Exception as e:
            print(e)

    def test_upload_file(self):
        ''' Upload:
            - получив файл от клиента, демон возвращает в отдельном поле http
            response хэш загруженного файла
            - демон сохраняет файл на диск в следующую структуру каталогов:
            store/ab/abcdef12345...
            где "abcdef12345..." - имя файла, совпадающее с его хэшем.
            /ab/ - подкаталог, состоящий из первых двух символов хэша файла.
        '''
        with open('first_test_file.txt', 'rb') as df:
            file_to_download = {'file' : ('first_test_file.txt', df.read())}
        response = requests.post("http://127.0.0.1:5000/upload", files=file_to_download) 
        file_hash = response.json()['hash']
        file_name = files_db.get_name_using_hash(file_hash)

        file_hash_in_db = files_db.get_hash_using_name(file_name)

        new_directory_name = file_hash[:2]
        created_file = os.listdir('store/'+new_directory_name)
        created_direcory = os.listdir('store/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(file_hash, file_hash_in_db)
        self.assertEqual(file_name, 'first_test_file.txt')
        self.assertIn(new_directory_name, created_direcory)
        self.assertIn('first_test_file.txt', created_file)

    def test_download_file(self):
        ''' Download:
            Запрос на скачивание: клиент передаёт параметр - хэш файла. 
            Демон ищет файл в локальном хранилище и отдаёт его, если находит.
        '''
        test_file_hash = files_db.get_all_file_hashes()

        response = requests.get(f"http://127.0.0.1:5000/download/{test_file_hash}")
        file_name = response.headers.get('content-disposition')[21:]
        
        directory_name = file_name[:2]
        current_path = os.getcwd()

        with open(current_path+'/for_unit_tests/'+file_name, 'wb') as f:
            f.write(response.content)

        with open(current_path+'/for_unit_tests/'+file_name) as f:
            text = f.read()

        existing_files = os.listdir(current_path+'/for_unit_tests/')

        self.assertEqual(response.status_code, 200)
        self.assertIn(file_name, existing_files)
        self.assertEqual(len(existing_files), 1)
        self.assertEqual(text, 'some test some file 2\n')

        response = requests.get("http://127.0.0.1:5000/download/1a2b3c")
        self.assertEqual(response.text, 'file_not_found')

    def test_delete_file(self):
        ''' Delete:
            Запрос на удаление: клиент передаёт параметр - хэш файла. Демон ищет
            файл в локальном хранилище и удаляет его, если находит.
        '''
        test_file_hash = files_db.get_all_file_hashes()
        existing_files_before = os.listdir('store/'+test_file_hash[0][:2])
        test_file_hash_before = files_db.get_all_file_hashes()

        response = requests.delete(f"http://127.0.0.1:5000/delete/{test_file_hash}")
        
        existing_files_after = os.listdir('store/'+test_file_hash[0][:2])
        test_file_hash_after = files_db.get_all_file_hashes()
        self.assertEqual(len(test_file_hash_before) -1, len(test_file_hash_after))
        self.assertEqual(len(existing_files_before) -1, len(existing_files_after))

        response = requests.delete("http://127.0.0.1:5000/delete/1a2b3c")
        self.assertEqual(response.text, 'file not found')

if __name__ == '__main__':
    unittest.main()
