import os
import files_db

current_path = os.getcwd()
try:
    os.mkdir(current_path + '/store/')
    os.mkdir(current_path + '/for_functional_tests/')
    os.mkdir(current_path + '/for_unit_tests/')
    files_db.create_db()
except:
    pass


os.system('gunicorn -b 127.0.0.1:5000 app:app --daemon')