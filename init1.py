#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='airlinesys',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/') # root irl
def hello():
    cursor = conn.cursor()
    # executes query
    query = 'SELECT * FROM `flights` WHERE deptDate >= CURRENT_DATE'
    cursor.execute(query)

    # stores the results in a variable
    data2 = cursor.fetchall()

    for each in data2:
        print(each['flightNum'])
    
    cursor.close()
    error = None

    return render_template('index.html', flights = data2)

#Define route for login
@app.route('/login') #login irl
def login():

	return render_template('login.html')

#Define route for stafflogin
@app.route('/stafflogin') #login irl
def stafflogin():
	return render_template('stafflogin.html')

#Define route for register
@app.route('/custregister')
def custregister():
	return render_template('custregister.html')

@app.route('/staffregister')
def staffregister():
	return render_template('staffregister.html')

#Authenticates customer login
@app.route('/loginAuthCust', methods=['GET', 'POST'])
def loginAuthCust():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()

	#executes query
	query = 'SELECT * FROM customer WHERE emailAdd = %s and cpassword = %s'
	cursor.execute(query, (username, password))	

	#stores the results in a variable
	data = cursor.fetchone() # returns a dictionary of the next row of query's result
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		session['usertype'] = 'customer'
		return redirect(url_for('home'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('login.html', error=error)

#Authenticates staff login
@app.route('/loginAuthStaff', methods=['GET', 'POST'])
def loginAuthStaff():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM airlinestaff WHERE username = %s and aspassword = %s'
	cursor.execute(query, (username, password))	
	#stores the results in a variable
	data = cursor.fetchone() # returns a dictionary of the next row of query's result
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		session['usertype'] = 'staff'
		return redirect(url_for('home'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('stafflogin.html', error=error)
		

#Authenticates the register
@app.route('/registerAuthCust', methods=['GET', 'POST'])
def registerAuthCust(): #!!!!!!!!	START WORKING HERE !!!!!!!!!!!!!!! need to copy and aug for staff login
	#grabs information from the forms
	username = request.form['email']
	password = request.form['password']
	fname = request.form['fname']
	lname = request.form['lname']
	phoneNum = request.form['phoneNum']
	stNum =  request.form['stNum']
	stName =  request.form['stName']
	city = request.form['city']
	state = request.form['state']
	zip_code =  request.form['zip']
	dob =  request.form['dob']
	passportNum = request.form['passportNum']
	ppExpDate =  request.form['passportExpDate']


	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM customer WHERE emailAdd = %s'
	cursor.execute(query, username)
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('custregister.html', error = error)
	else:
		# Insert user information into the customer table
		ins_customer = 'INSERT INTO customer VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
		cursor.execute(ins_customer, (username, fname, lname, password, stNum, stName, None, city, state, zip_code, passportNum, dob, 'United States', ppExpDate))

		# Insert phone number into the custphoneinst table
		ins_phone = 'INSERT INTO custphoneinst VALUES (%s, %s)'
		cursor.execute(ins_phone, (username, phoneNum))
		conn.commit()
		cursor.close()
		session['username'] = username
		session['usertype'] = 'customer'
		return render_template('home.html')
	
#Authenticates the register
@app.route('/registerAStaff', methods=['GET','POST'])
def registerAStaff(): 
    username = request.form['username']
    password = request.form['password']
    fname = request.form['fname']
    lname = request.form['lname']
    dob = request.form['dob']
    company = request.form['company']
    email = request.form['email']
    phoneNum = request.form['phoneNum']

    cursor = conn.cursor()
    query = 'SELECT * FROM airlineStaff WHERE username = %s'
    cursor.execute(query, username)
    data = cursor.fetchone()
    error = None

    if data:
        error = "This user already exists"
        return render_template('staffregister.html', error=error)
    else:
		#add someway to test if airline exists
        ins_staff = 'INSERT INTO airlinestaff VALUES (%s, %s, %s, %s, %s)'
        cursor.execute(ins_staff, (username, password, fname, lname, dob))

        ins_works_for = 'INSERT INTO worksFor VALUES (%s, %s)'
        cursor.execute(ins_works_for, (username, company))

        ins_email = 'INSERT INTO staffemailinst VALUES (%s, %s)'
        cursor.execute(ins_email, (username, email))

        ins_phone = 'INSERT INTO staffphoneinst VALUES (%s, %s)'
        cursor.execute(ins_phone, (username, phoneNum))

        conn.commit()
        cursor.close()
        
        session['username'] = username
        session['usertype'] = 'staff'
        return render_template('home.html')  # You may want to redirect to a different page for staff members




@app.route('/home')
def home():
    username = session['username']
    #cursor = conn.cursor();
    #query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
    #cursor.execute(query, (username))
    #data1 = cursor.fetchall() 
    #for each in data1:
    #    print(each['blog_post'])
    #cursor.close()
    return render_template('home.html', username=username)#, posts=data1)

@app.route('/logout')
def logout():
	session.pop('username')
	session.pop('usertype')
	return redirect('/')
		
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
