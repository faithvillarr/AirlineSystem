#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors, json

#Initialize the app from Flask
app = Flask(__name__)

flight_number = ''

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
    if 'usertype' not in session:
        session['usertype'] = 'null'
    print("Usertype: ",session['usertype'])
    query = 'SELECT * FROM `flights` WHERE deptDate >= CURRENT_DATE ORDER BY deptDate ASC'
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

#! My app routes!!
@app.route('/searchflight', methods=['GET','POST'])
def searchFlights():
	print("flag",request.form)
	deptapt = request.form['deptapt']
	deptdate = request.form['deptdate']
	arrapt = request.form['arrapt']
	arrdate = request.form['arrdate']

	cursor = conn.cursor()
	query = 'SELECT * FROM flights WHERE deptDate = %s and deptAirportCode = %s and arrDate = %s and arrAirportCode = %s'
	cursor.execute(query, (deptdate, deptapt, arrdate, arrapt))
	data3 = cursor.fetchall()
	cursor.close()
	error = None
	return render_template('index.html', flights = data3)

@app.route('/flightdetails', methods = ['GET', 'POST'])
def flightDetails(): # <input type="hidden" name="flight_num" value="{{ flight['flightNum'] }}">
	flight_number = request.args.get('flight_num')
	print(request.args.get('flight_num'))
	#username = session['username']
	#usertype = session['usertype']

	cursor = conn.cursor()
	query = 'SELECT * FROM flights WHERE flightNum = %s'
	cursor.execute(query, (flight_number,))
	myflight = cursor.fetchone()
	print("My Flight: ",myflight)
	cursor.close();
	return render_template('flightdetails.html', flight = myflight) #, username = username), usertype = usertype)

@app.route('/home')
def home():
	username = session['username']
	if(session['usertype'] == 'customer'):
		cursor = conn.cursor();

		#past flights
		pastquery = 'SELECT flights.flightNum, flights.deptAirportCode, flights.deptDate, flights.deptTime, flights.arrAirportCode, flights.arrDate, flights.arrTime, flights.fstatus, flights.baseTicketPrice FROM flights INNER JOIN ticket ON ticket.flightNum = flights.flightNum WHERE ticket.emailAdd = %s AND flights.deptDate < CURRENT_DATE;'
		cursor.execute(pastquery, (username))
		pastflights = cursor.fetchall() 
		print("Past Flights:\n")
		# for i in pastflights:
		#     print(i)

		#future flights
		futurequery = 'SELECT flights.flightNum, flights.deptAirportCode, flights.deptDate, flights.deptTime, flights.arrAirportCode, flights.arrDate, flights.arrTime, flights.fstatus, flights.baseTicketPrice FROM flights INNER JOIN ticket ON ticket.flightNum = flights.flightNum WHERE ticket.emailAdd = %s AND flights.deptDate >= CURRENT_DATE;'
		cursor.execute(futurequery, (username))
		upcflights = cursor.fetchall() 

		spendingquery = 'SELECT sum(pricePaid) from purchased where emailAdd = %s'
		cursor.execute(spendingquery, (username))
		totalspent = cursor.fetchone();
		cursor.close()
		return render_template('home.html', pastflights = pastflights, upcflights = upcflights, totalspent = totalspent)
		# for i in upcflights:
		#     print(i)

	if(session['usertype'] == 'staff'):
		#Get total revenue
		cursor = conn.cursor()
		query = 'SELECT w.airlineName FROM worksFor w WHERE w.userName = %s'
		cursor.execute(query, session['username'])
		airline = cursor.fetchone()['airlineName'];
		print(airline)
		query = 'SELECT SUM(p.pricePaid) AS total_revenue FROM purchased p JOIN ticket t ON p.ticketID = t.ticketID JOIN flights f ON t.flightNum = f.flightNum WHERE f.airline = %s'
		#total_revenue = cursor.execute(query, airline)
		#print(total_revenue)

			
	return render_template('home.html')#, posts=data1)

@app.route('/logout')
def logout():
	session.pop('username')
	session.pop('usertype')
	session['usertype'] = 'null'
	return redirect('/')

@app.route('/userinfo')
def userinfo():
	cursor = conn.cursor();
	query = 'SELECT * FROM  customer WHERE emailAdd = %s'
	cursor.execute(query, (session['username']))
	udata = cursor.fetchone();
	query = 'SELECT phoneNum FROM custPhoneInst WHERE emailAdd = %s'
	cursor.execute(query, (session['username']))
	pdata = cursor.fetchall();
	for i in pdata:
		print(i)
	return render_template('userinfo.html', data = udata, phoneNum = pdata)

@app.route('/addCustPhoneNum', methods=['GET','POST'])
def addCustPhoneNum():
	cursor = conn.cursor();
	newNum = request.form['phoneNum']
	if len(newNum) > 11 or len(newNum) < 9:
		message = 'Improperly formatted phone number.'
		return redirect(url_for('userinfo'))
	query = 'INSERT INTO custphoneinst (emailAdd, phoneNum) VALUES (%s, %s)'
	cursor.execute(query, (session['username'], newNum))
	cursor.close()
	return redirect(url_for('userinfo'))

@app.route('/write-review', methods = ['GET','POST'])
def writeReview():
	cursor = conn.cursor();
	flight_num = request.form['flight_num']
	query = 'SELECT * FROM flights WHERE flightNum = %s'
	cursor.execute(query, (flight_num))
	flight = cursor.fetchone();
	print("flight: ", flight)
	#check if a review already exists. 	
		#if yes -> edit review
		#else -> write new review
	return render_template('writereview.html', flight = flight)

@app.route('/writing', methods = ['POST'])
def writingReview():
	cursor = conn.cursor()
	if(session['usertype'] == 'customer'):
		flight_num = request.form.get('flight_num')
		dept_date = request.form['depdt']
		dept_time = request.form['deptm']
		email_add = session['username']
		rating = request.form['rating']
		comments = request.form['comments']
		query = 'INSERT INTO took (flightNum, deptDate, deptTime, emailAdd, rating, comments) VALUES (%s, %s, %s, %s, %s, %s)'
		cursor.execute(query, (flight_num, dept_date, dept_time, email_add, rating, comments))
		conn.commit()
	cursor.close()
	return redirect(url_for('home'))

@app.route('/purchaseflight', methods=['GET', 'POST'])
def purchasePage():
    cursor = conn.cursor()
    flight_num = request.args.get('myname')
    print("Flight #: ", flight_num)
    query = 'SELECT * FROM flights WHERE flightNum = %s'
    cursor.execute(query, (flight_num,))
    flight = cursor.fetchone()
    print(flight)
    cursor.close()
    return render_template('purchaseflight.html', flight=flight)

@app.route('/purchasingAuth', methods = ['GET'])
def purchasing():
	cursor = conn.cursor()
	
	#!TODO:  implement the purchasing stuff in database
	
	cursor.close()
	return redirect(url_for('home'))


# ADDING FLIGHTS
@app.route('/addFlight', methods = ['GET'])
def addFlight():
	cursor = conn.cursor()
	query = 'SELECT planeID FROM `airplane` WHERE name = ( SELECT airlineName FROM worksfor where userName = %s)' 
	cursor.execute(query, (session['username']))
	planes = cursor.fetchall()
	return render_template('addFlight.html', planes = planes)
@app.route('/addFlightAuth', methods = ['POST'])
def addFlightA():
	#!TODO: insert a check for maintenence and pre-existence
	print("Flga")
	flightNum = request.form['flightNum']
	deptAirportCode = request.form['deptAirportCode']
	deptDate = request.form['deptDate']
	deptTime = request.form['deptTime']
	arrAirportCode = request.form['arrAirportCode']
	arrDate = request.form['arrDate']
	arrTime = request.form['arrTime']
	baseTicketPrice = request.form['baseTicketPrice']
	fstatus = request.form['fstatus']
	planeID = request.form['selectedPlane']
	cursor = conn.cursor()

	airlineq = 'SELECT airlineName FROM worksfor WHERE username = %s'
	#print('Executing worksfor...')
	cursor.execute(airlineq, (session['username']))	
	airline = cursor.fetchone()['airlineName']
	#print(airline)
	#print('success\n')

	#!TODO: Check (1) if flight already exists and (2)if plane is already being used at that time or (3)or if plane is in maintenance.
	#(1) flight exists
	exist_test = 'SELECT * FROM `flights` WHERE flightNum = %s'
	cursor.execute(exist_test, (flightNum))
	check_val = cursor.fetchall()
	if(check_val):
		message = "This flight already exists."
		return render_template('addMaintenance.html', message = message)
	#(2) if plane is being used

	#(3) maintenence check
	main_test = '''
			SELECT flightNum
			FROM maintenancePeriod
			NATURAL JOIN uses
			NATURAL JOIN flights 
			WHERE (startDate < %s OR (startDate = %s AND startTime < %s))
			AND (endDate > %s OR (endDate = %s AND endTime > %s))
			UNION
			SELECT flightNum
			FROM maintenancePeriod
			NATURAL JOIN uses
			NATURAL JOIN flights 
			WHERE (startDate < %s OR (startDate = %s AND startTime < %s))
			AND (endDate > %s OR (endDate = %s AND endTime > %s));
			'''
	cursor.execute(main_test, (deptDate, deptDate, deptTime, deptDate, deptDate, deptTime, arrDate, arrDate, arrTime, arrDate, arrDate, arrTime)) 
	checkmain = cursor.fetchall()
	if(checkmain):
		message = "This plane will be in maintenence during the proposed flight time."
		return render_template('addMaintenance.html', message = message)

	flightq = 'INSERT INTO flights Values (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
	print(flightNum, deptDate, deptTime,arrDate, arrTime, baseTicketPrice, arrAirportCode, deptAirportCode, fstatus)
	#print('Executing flight insert ...')
	cursor.execute(flightq, (flightNum, deptDate, deptTime,arrDate, arrTime, baseTicketPrice, arrAirportCode, deptAirportCode, fstatus))
	#print('success!\n')
	conn.commit()
	#NAME 	flightNum 	deptDate 	deptTime 	planeID 
	print(airline, flightNum, deptDate, deptTime, planeID)
	print('Executing plane in use insert ...')
	usesq = 'INSERT INTO uses VALUES (%s, %s, %s, %s, %s)'
	cursor.execute(usesq, (airline, flightNum, deptDate, deptTime, planeID))
	conn.commit()

	message = "Flight sucessfully added"
	return render_template('addFlight.html', message = message)


#ADDING PLANES
@app.route('/addAirplane', methods = ['GET'])
def addAirplane():
	return render_template('addAirplane.html')
@app.route('/addAirplaneAuth', methods =["POST"])
def addAirplaneA():
	planeID = request.form['planeID']
	numSeats = request.form['numSeats']
	manuCompany = request.form['manuCompany']
	modelNum = request.form['modelNum']
	manuDate =  request.form['manuDate']

	cursor = conn.cursor()

	checkq = 'SELECT * FROM `airplane` WHERE planeID = %s'
	cursor.execute(checkq, (planeID))
	temp = cursor.fetchone();

	#check the plane doesn't exist. exit if so. 
	if(temp):
		message = "This plane already exists."
		return render_template('addAirplane.html', message = message)

	airlineq = 'SELECT airlineName FROM worksfor WHERE username = %s'
	cursor.execute(airlineq, (session['username']))	
	airlinename = cursor.fetchone()['airlineName']

	query = 'SELECT * FROM airplane WHERE planeID = %s'
	cursor.execute(query, planeID)
	if(cursor.fetchone() != 'None'):
		message = "Flight already exists"
		return render_template('addAirplane.html', message = message)
	
	ins_airplane = 'INSERT INTO airplane VALUES(%s, %s, %s, %s, %s, %s, %s)'
	cursor.execute(ins_airplane, (planeID, airlinename, numSeats, manuCompany, modelNum, manuDate, 'null' ))
	conn.commit()
	print("flag")
	message = "Flight sucessfully added"
	return render_template('addAirplane.html', message = message)


#ADDING MAINTENENCE
@app.route('/addMaintenance', methods = ['GET','POST'])
def addMaintenance():
	cursor = conn.cursor()

	#get airline
	airlineq = 'SELECT airlineName FROM worksfor WHERE username = %s'
	cursor.execute(airlineq, (session['username']))	
	airlinename = cursor.fetchone()['airlineName']

	query = 'SELECT * FROM airplane WHERE NAME = %s'
	cursor.execute(query, (airlinename))
	planes= cursor.fetchall()
	cursor.close()
	return render_template('addMaintenance.html', planes = planes, airline = airlinename)

@app.route('/addMaintenanceAuth', methods = ['POST'])
def addMaintenanceA():
	cursor = conn.cursor()
	#!TODO: implement way to find planeID
	planeID = request.form['planeID']
	print("planeID: ", planeID)

	#!TODO: implement way to find airline
	airline = request.form['airline']
	print('airline: ', airline)
	startDate = request.form['startDate']
	startTime = request.form['startTime']
	endDate = request.form['endDate']
	endTime =  request.form['endTime']

	#!TODO: Checked if plane is scheduled for that day
	query = '''
		SELECT flightNum
		FROM maintenancePeriod
		NATURAL JOIN uses
		NATURAL JOIN flights 
		WHERE (%s < deptDate OR (%s = deptDate AND %s < deptTime))
		AND (%s > deptDate OR (%s = deptDate AND %s > deptTime))
		UNION
		SELECT flightNum
		FROM maintenancePeriod
		NATURAL JOIN uses
		NATURAL JOIN flights 
		WHERE (%s < arrDate OR (%s = arrDate AND %s < arrTime))
		AND (%s > arrDate OR (%s = arrDate AND %s > arrTime));
		'''
	cursor.execute(query, (startDate, startDate, startTime, endDate, endDate, endTime, startDate, startDate, startTime, endDate, endDate, endTime))
	check = cursor.fetchall()
	if(check):
		message = "Maintenance conflicts with existing flight."
		return render_template('addMaintenance.html', message = message)


	insert_maintenance = 'INSERT INTO maintenanceperiod VALUES (%s, %s, %s, %s, %s, %s)'
	cursor.execute(insert_maintenance, (planeID, airline, startDate, startTime, endDate, endTime))
	conn.commit();
	message = "Maintenance sucessfully scheduled"
	return render_template('addMaintenance.html', message = message)

#ADDING AIRPORTS
@app.route('/addAirport', methods = ['GET'])
def addAirport():
	return render_template('addAirport.html')
@app.route('/addAirportAuth', methods = ['POST'])
def addAirportA():
	airportCode = request.form['airportCode']
	name = request.form['name']
	city = request.form['city']
	country = request.form['country']
	termNum = request.form['termNum']
	arprtType =  request.form['arprtType']

	cursor = conn.cursor()
	query = 'SELECT * FROM airport WHERE airportCode = %s'
	cursor.execute(query, airportCode)
	if(cursor.fetchone() != 'None'):
		message = "Flight already exists"
		return render_template('addAirport.html', message = message)
		
	ins_airplane = 'INSERT INTO airport VALUES(%s, %s, %s, %s, %s, %s)'
	print(airportCode, name, city, country, termNum, arprtType)
	cursor.execute(ins_airplane, (airportCode, name, city, country, termNum, arprtType))
	conn.commit()
	message = "Flight sucessfully added"
	return render_template('addAirport.html', message = message)

#ADDING STATUS'
@app.route('/addStatus', methods = ['GET'])
def addStatus():
	return render_template('addStatus.html')
@app.route('/addStatusAuth')
def addStatusA():
	message = "Flight sucessfully added"
	return render_template('addStatus.html', message = message)


		
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
