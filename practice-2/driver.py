import os
from flask import Flask, render_template, flash, redirect, url_for, abort, g, session, request
from config import Config
from flask_script import Manager
from flask import session
# from flask_dropzone import Dropzone
#from flask_bcrypt import check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy as sql
from flask_migrate import Migrate, MigrateCommand
import base64
#from models import prepare_info

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'xc9*\x8f\xd1Z\x0e_;Z\x19XqK\x8fW\x01\xf1\xf1\xe2\x12V\xac'
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
	create_db()
	from models import User
	return render_template('home.html')

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


@app.route('/profile',methods=['GET','POST'])
def load_profile():
	from models import User, FileContents
	#print("/profile debug #1")
	if request.method == 'POST':
		userName = request.form['username']
		owner = User.query.filter_by(username=userName).first()
		if owner != None:
			#print("/profile debug #2 Owner!=None")
			files = FileContents.query.filter_by(user_id = owner.username).all()
			if owner.get_password() == request.form['password']:
				session['userName'] = userName
				#print("/profile debug #3")
				return render_template('upload.html', user = userName,files = files)

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
	if 'userName' not in session:
		return render_template('login.html')
	else:
		user = session["userName"]
		files = FileContents.query.filter_by(user_id = owner.id).all()
		print(type(files))
		return render_template('upload.html', user = user, files=files)

@app.route('/upload_file', methods=['POST','GET'])
def upload_file():
	from werkzeug import secure_filename
	import os
	from models import FileContents, User
	# print("/uploead file debug #1")
	user = session["userName"]
	owner = User.query.filter_by(username=user).first()
	files = FileContents.query.filter_by(user_id = owner.username).all()
	if request.method == 'POST':
		input_file = request.files['file']
		input_file.save(secure_filename(input_file.filename))

		owner = User.query.filter_by(username=user).first()
		# filecontent=input_file.read()
		with open(input_file.filename, "rb") as pdf_file:
			encoded_string = base64.b64encode(pdf_file.read())
		# print("/uploead file debug #2")
		new_file = FileContents(data=encoded_string, filename=input_file.filename, user_id =owner.username)
		os.remove(input_file.filename)
		user = session["userName"]
		db.session.add(new_file)
		db.session.commit()

		return render_template('upload.html',user = owner.username, files = files)
	return render_template('upload.html',user = owner.username, files = files)

@app.route('/file/<int:id>')
def get_user_file(id):
	import os.path
	from models import FileContents, User
	file = FileContents.query.filter_by(id = id).first()
	directory = "static"
	completeName = os.path.join(directory,file.get_name())
	if file != None:
		with open(completeName, "wb") as fh:
			fh.write(base64.decodebytes(file.data))
		pdf_file = open(completeName,"r")
		return render_template('file_view.html',user = session["userName"], file = file)

@app.errorhandler(404)
def page_not_found(e):
 return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
 return render_template('500.html'), 500

if __name__ == "__main__":
	#app.run(debug=True, host= '0.0.0.0', port =4000)
	# manager.run()
	app.run(debug=True)
