import os
from flask import Flask, render_template, flash, redirect, url_for, abort, g, session, request
from config import Config
from flask_script import Manager
# from flask_dropzone import Dropzone
#from flask_bcrypt import check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy as sql
from flask_migrate import Migrate, MigrateCommand
#from models import prepare_info

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config.from_object(Config)
app.config['SECURITY_KEY'] = 'secret'
app.config['DEBUG'] = True
app.config['ALLOWED_EXTENSIONS'] = set(["pdf", "docx", "doc"])
app.config.update(
	 UPLOADED_PATH=os.path.join(basedir, 'uploads'),

)

user = ''

db = sql(app)
Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

def create_db():
	db.drop_all()
	db.create_all()

@app.route('/')
def home():
	from models import User
	if user == '':
		return render_template('home.html')
	else:
		return "Welcome to FreeFlow " + user

@app.route('/options', methods=['GET','POST'])
def options():
	if request.method == 'GET':
		if request.args['submit'] == 'register':
			return render_template('register.html')
		elif request.args['submit'] == 'login':
			return render_template('login.html')
		else:
			return None
	else:
		return render_template('home.html')

@app.route('/login')
def login():
	return render_template('login.html')


@app.route('/logged',methods=['GET','POST'])
def load_login():
	from models import User
	if request.method == 'POST':
		print("here0")
		username = request.form['username']
		owner = User.query.filter_by(username=username).first()
		if owner != None:
			print("here1")
			if owner.get_password() == request.form['password']:
				user = username
				return render_template('upload.html', user = user)

			else:
				return render_template('login.html', message = 'Wrong Password')
		else:
			return render_template('login.html', message = 'Something happened try again')

@app.route('/register')
def register():
	return render_template('register.html')


@app.route('/create_user', methods=['POST','GET'])
def create_user():
	from models import prepare_info , User
	if request.method == 'POST':
		User = User( request.form['username'], request.form['password'],request.form['FirstN'], request.form['LastN'],request.form['Email'] )
		db.create_all()
		db.session.add(User)
		db.session.commit()
		return render_template('upload.html', user = request.form['username'])


@app.route('/uploads')
def pre_upload():
	if user == '':
		return render_template('login.html')
	else:
		return render_template('upload.html', user = user)

@app.route('/upload_file', methods=['POST','GET'])
def upload_file():
	from models import FileContents, User

		# owner = User.query.filter_by(username=user).first()
		#print(owner.id , owner.username)
	if request.method == 'POST':

		input_file = request.files['file']
			#print(owner.id , owner.username)
		owner = User.query.filter_by(user).first()
		new_file = FileContents(data=input_file.read(), filename=input_file.filename, user_id =owner.username)
		#db.create_all()
		db.session.add(new_file)
		db.session.commit()
		return (input_file.filename, "this file has been upload successfully")




if __name__ == "__main__":
	#app.run(debug=True, host= '0.0.0.0', port =4000)
	manager.run()
