from flask import Flask, render_template, url_for, session, request
from passlib.hash import sha256_crypt
import pymysql
import yaml

app = Flask(__name__)

"""
db = yaml.load(open('db.yaml'))
myApp = pymysql.connect(host=db['mysql_host'], user=db['mysql_user'], password=db['mysql_password'], db=db['mysql_db'], charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
"""

@app.route('/')
def index():
	if 'username' in session:
		username = session['username']
		# check if user filled out profile + has matches
		cur = myApp.cursor()
		cur.execute("SELECT userID FROM user WHERE username=%s", [username])
		userID = cur.fetchone()['userID']
		cur.execute("SELECT hackathonID FROM usertohackathon WHERE userID=%s", [userID])
		if cur.fetchone() is not None:
			return render_template('index.html', username=username, profile=profile)
		return render_template('index.html', username=username)
	return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
	error = []
	isIssue = False
	if request.method == 'POST':
		# fetch form data
		userDetails = request.form
		username = userDetails['username']
		email = userDetails['email']
		password = userDetails['password']
		confirm_password = userDetails['confirm_password']

		cur = myApp.cursor()
		cur.execute("SELECT * FROM user WHERE username = %s", [username])
		
		#error handling
		if cur.fetchone() is not None:
			error.append('Please choose a different username.')
			isIssue = True

		cur.execute("SELECT * FROM user WHERE email = %s", [email])
		
		if cur.fetchone() is not None:
			error.append('Email already registered.')
			isIssue = True

		if password != confirm_password:
			error.append('Passwords do not match.')
			isIssue = True

		if isIssue: # if any errors
			return render_template('register.html', error = error)

		# if no errors, add to database
		cur.execute("INSERT INTO user(email, username, password) VALUES(%s, %s, %s)", [email, username, sha256_crypt.encrypt(password)])
		myApp.commit()
		cur.close() 
		flash('Congrats! You are now a registered user.')
		return redirect(url_for('login'))
	return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if 'username' in session:
		return redirect(url_for('index'))
	if request.method == 'POST':
		username_form  = request.form['username']
		password_form  = request.form['password']
		cur = myApp.cursor()
		cur.execute("SELECT COUNT(1) FROM user WHERE username = %s;", [username_form]) # CHECKS IF USERNAME EXISTS
		if cur.fetchone() is not None:
			cur.execute("SELECT password FROM user WHERE username = %s;", [username_form]) # FETCH THE PASSWORD
			for row in cur.fetchall():
				if sha256_crypt.verify(password_form, row['password']):
					session['username'] = request.form['username']
					cur.close()
					return redirect(url_for('index'))
				else:
					error = "Wrong password"
		else:
			error = "Username not found"
		cur.close()
	return render_template('login.html', error=error)

#@app.route('/results')
#def matches():
	# stuff
    
if __name__ == '__main__':
	app.run(debug=True)
