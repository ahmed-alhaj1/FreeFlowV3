from driver import db
import datetime
import uuid
import os

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(64), index=True, unique = True)
	password = db.Column(db.String(60), index=True, unique=True )

	first_name = db.Column(db.String(64), index=True, unique = True)
	last_name = db.Column(db.String(64), index=True, unique = True)

	email = db.Column(db.String(64), index=True, unique = True)
	files = db.relationship('FileContents', backref ='owner', lazy= 'dynamic')

	def __init__(self, username, password, first_name, last_name, email):
		self.username = username
		#self.Id = Id
		self.password = password
		self.first_name = first_name
		self.last_name = last_name
		self.email = email
	def __repr__(self):
		return '<User {}>'.format(self.username)
#def rep_user_info():
	#user = db.query.filter_by(username='ahmed')


class FileContents(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	data = db.Column(db.LargeBinary(), nullable=True)
	#size = db.Column(db.Integer, nullable=False)
	filename = db.Column(db.String(30), nullable=True)
	user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
	"""
	def __init__(data = None, filename = None , user_id= None):
		self.data = data
		self.filename = filename
	"""	

def prepare_info(  username, password , first_name, last_name,  email):
	Id = make_id()
	date = get_date()
	dirname = 'uploads/'+username[0:3]+ str(date.year ) +Id[0:4]
	make_dir(dirname)
	return User( username, password, first_name, last_name,  email,dirname )
	

def make_id():
	return str(uuid.uuid4().fields[-1])[:5]
def get_date():
	return datetime.datetime.now()
def make_dir(path):
	os.mkdir(path)

def init_db():
	db.create_all()
