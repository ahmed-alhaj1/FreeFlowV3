import os
from flask import Flask, render_template, flash, redirect, url_for, abort, g, session, request
from config import Config
from flask_script import Manager
from flask_dropzone import Dropzone
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
         DROPZONE_MAX_FILES=300,

)

dropzone = Dropzone(app)

db = sql(app)
Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

def create_db():
	db.drop_all()
	db.create_all()

@app.route('/')
def login():
	from models import User
	if not session.get('logged_in'):
		return render_template('login.html')
	else:
		return "Welcome to FreeFlow"


@app.route('/login')
def load_login():
	print('here0')
	from models import User
	if request.method == 'GET':
		username = request.args['username']
		owner = User.query.filter_by(username=username).first()
		if owner != None:
			if owner.get_password() == request.args['password']:
				return render_template('logged.html', name = username)
			else:
				flash('wrong password')
			return render_template('logged.html', name = username)
		else:
			flash('wrong password')

# 		if request.args['password'] == 'password' and request.args['username'] =='ahmed':
# 			username = request.args['username']
# 			print('here1')
# ##			session['logged_in']
# 		else:
# 			flash('wrong password')
# 	return render_template('logged.html', name = username)

@app.route('/register')
def register():
	return render_template('register.html')


@app.route('/create_user', methods=['POST','GET'])
def create_user():
	from models import prepare_info , User
	create_db()
	if request.method == 'POST':
		user = User( request.form['username'], request.form['password'],request.form['FirstN'], request.form['LastN'],request.form['Email'] )
		db.create_all()
		db.session.add(user)
		db.session.commit()
		return 'Hello ' + request.form['FirstN'] + request.form['LastN']


@app.route('/uploads')
def pre_upload():
	return render_template('upload.html')

@app.route('/upload_file', methods=['POST','GET'])
def upload_file():
	from models import FileContents, User

	owner = User.query.filter_by(username='sofianx12').first()
	print(owner.id , owner.username)

	if request.method == 'POST':


		input_file = request.files['file']
		print(owner.id , owner.username)

		new_file = FileContents(data=input_file.read(), filename=input_file.filename, user_id =owner.username)
		#db.create_all()
		db.session.add(new_file)
		db.session.commit()
		return (input_file.filename, "this file has been upload successfully")




if __name__ == "__main__":
	#app.run(debug=True, host= '0.0.0.0', port =4000)
	manager.run()
