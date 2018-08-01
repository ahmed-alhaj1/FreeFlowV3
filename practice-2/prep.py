from models import User
import datetime
import uuid
import os

def prepare_info(  username, password , first_name, last_name,  email):
        Id = make_id()
        date = get_date()
        dirname = 'uploads/'+username[0:3]+ str(date.year ) +Id[0:4]
        make_dir(dirname)
        return User(username, password, first_name, last_name,  email,dirname )
        

def make_id():
        return str(uuid.uuid4().fields[-1])[:5]
def get_date():
        return datetime.datetime.now()
def make_dir(path):
        os.mkdir(path)

