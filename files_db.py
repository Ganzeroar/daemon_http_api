import sqlite3

def create_db():
    conn = sqlite3.connect('files_and_hash.db')
    cursor = conn.cursor()

    req = 'CREATE TABLE files_and_hash (file_name text, file_hash text, path_to_file text)'
    cursor.execute(req)

def drop_db():
    conn = sqlite3.connect('files_and_hash.db')
    cursor = conn.cursor()
    cursor.executescript('DROP TABLE IF EXISTS files_and_hash')

def get_all_file_hashes():
    conn = sqlite3.connect('files_and_hash.db')
    cursor = conn.cursor()
    string_sql = 'SELECT file_hash FROM files_and_hash'
    cursor.execute(string_sql)
    try:
        hashes = cursor.fetchall()[0]
        return hashes
    except:
        return []

def get_all_file_names():
    conn = sqlite3.connect('files_and_hash.db')
    cursor = conn.cursor()
    string_sql = 'SELECT file_name FROM files_and_hash'
    cursor.execute(string_sql)
    names = cursor.fetchall()[0]
    return names

def insert_file_name_and_hash(file_name, file_hash, path_to_file):
    conn = sqlite3.connect('files_and_hash.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO files_and_hash (file_name, file_hash, path_to_file) VALUES (?, ?, ?)', (file_name, file_hash, path_to_file))
    conn.commit()

def get_name_using_hash(file_hash):
    conn = sqlite3.connect('files_and_hash.db')
    cursor = conn.cursor()
    string_sql = f"SELECT file_name FROM files_and_hash WHERE file_hash = '{file_hash}'"
    cursor.execute(string_sql)
    try:
        file_name = cursor.fetchall()[0][0]
        return file_name
    except:
        return []

def get_hash_using_name(file_name):
    conn = sqlite3.connect('files_and_hash.db')
    cursor = conn.cursor()
    string_sql = f"SELECT file_hash FROM files_and_hash WHERE file_name = '{file_name}'"
    cursor.execute(string_sql)
    file_hash = cursor.fetchall()[0][0]
    return file_hash

def get_path_to_file_using_hash(file_hash):
    conn = sqlite3.connect('files_and_hash.db')
    cursor = conn.cursor()
    string_sql = f"SELECT path_to_file FROM files_and_hash WHERE file_hash = '{file_hash}'"
    cursor.execute(string_sql)
    try:
        path_to_file = cursor.fetchall()[0][0]
        return path_to_file
    except:
        return []

def delete_file_using_hash(file_hash):
    conn = sqlite3.connect('files_and_hash.db')
    cursor = conn.cursor()
    string_sql = f"DELETE FROM files_and_hash WHERE file_hash='{file_hash}'"
    cursor.execute(string_sql)
    conn.commit()

if __name__ == '__main__':
    try:
        drop_db()
        create_db()
    except:
        pass