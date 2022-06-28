from venv import create
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors # Used to itnerface the database
from datetime import datetime # May need this for your datetime columns/client
import hashlib # But can use this for md5
import re # If you want to use regex
import json # You'll need this library to parse json objects in python
from datetime import date

# Verifies if an email is in a valid format via regex (regular expressions)
def validateEmail(email):
    # Regex is a way to examine a pattern in a string given a format pattern
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    # Checks if string input has the regex pattern
    return re.fullmatch(regex, email)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'MQZtHs3r6y>KdO/' # Needed for session and other stuff
app.config['APP_HOST'] = "localhost" # 127.0.0.1 is localhost IP for all computers

# Set this to your custom DB information
app.config['DB_USER'] = "root"
app.config['DB_PASSWORD'] = 'root' # 'root' if using unix, '' if using windows
app.config['APP_DB'] = "air_ticket_reservation"
app.config['CHARSET'] = "utf8mb4"

# Connect to the DB
conn =  pymysql.connect(host=app.config['APP_HOST'],
                       user=app.config['DB_USER'],
                       unix_socket='/Applications/MAMP/tmp/mysql/mysql.sock', # for use in unix mamp
                       password=app.config['DB_PASSWORD'],
                       db=app.config['APP_DB'],
                       charset=app.config['CHARSET'],
                       cursorclass=pymysql.cursors.DictCursor)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/customer-login')
def customer_login():
    return render_template('customer-login.html')

@app.route('/staff-login')
def staff_login():
    return render_template('staff-login.html')

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')

# public information
@app.route('/public-flight-search')
def public_flight_search():
    return render_template('public-flight-view.html')

@app.route('/public-flight-view')
def public_flight_view():
    cursor = conn.cursor()
    query = """
            SELECT AirlineName, FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, FlightStatus, ArrivalAirport, DepartureAirport
            FROM Flight NATURAL JOIN Changes
            WHERE (DepartureDate > CURRENT_DATE)
            ORDER BY DepartureDate
            """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('public-flight-view.html', flights = data)

# REST = Representational State Transfer
# GET, POST are REST methods
# GET specifies what to do when the client wants a page loaded
# POST is for when you want to mutate data in your database

# customer registration / login
@app.route('/customer-registration', methods=['GET', 'POST'])
def customer_registration():
    return render_template('customer-registration.html')

@app.route('/customer-registration-auth', methods=['GET', 'POST'])
def customer_registration_auth():
        #grabs information from the forms
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    password = request.form['password']
    buildingNumber = request.form['building-number']
    street = request.form['street']
    city = request.form['city']
    state = request.form['state']
    passportNumber = request.form['passport-number']
    passportExp = request.form['passport-expiration']
    passportCountry = request.form['passport-country']
    dateOfBirth = request.form['date-of-birth']
    print(request.form)
    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    noDupEmailQuery = 'SELECT CustomerEmail FROM customer WHERE CustomerEmail = %s'
    cursor.execute(noDupEmailQuery, (email))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('customer-registration.html', error = error)
    else:
        #password = hashlib.md5(password.encode())
        ins = 'INSERT INTO Customer VALUES(%s, %s, md5(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (name, email, password, int(buildingNumber), street, city, state, phone, passportNumber,passportExp, passportCountry, dateOfBirth))
        conn.commit()
        cursor.close()
        return render_template('customer-login.html')

def loggedIn():
    return len(session) > 0

@app.route('/customer-login-auth',  methods=['GET', 'POST'])
def customer_login_auth(): 
    #grabs information from the forms
    username = request.form['customer-username']
    password = request.form['customer-password']

    #cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = 'SELECT CustomerEmail, CustomerPassword FROM Customer WHERE CustomerEmail = %s and CustomerPassword = md5(%s)'
    cursor.execute(query, (username, password))
    #stores the results in a variable
    data = cursor.fetchone()

    # use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    
    sessionRunning = loggedIn()
    if (sessionRunning == True): 
        error = 'Other users signed in. Please sign out of current session.'
        return render_template('customer-login.html', error=error)
    
    if(data):
        # creates a session for the the user
        # session is a built in
        session['username'] = username
        
        # query to return the name of the customer
        cursor = conn.cursor()
        query = 'SELECT CustomerName FROM Customer WHERE CustomerEmail = %s and CustomerPassword = md5(%s)'
        cursor.execute(query, (username, password))
        name = cursor.fetchone()['CustomerName']
        cursor.close()

        return redirect('customer-home')
    else:
        error = 'Invalid login or username'
        return render_template('customer-login.html', error=error)

@app.route('/customer-home')
def customer_home():
    # cursor used to send queries
    if len(session) == 0:
        return render_template('no-session.html')
    
    cursor = conn.cursor()

    username = session['username']

    # query to return the name of the customer
    query = 'SELECT CustomerName FROM Customer WHERE CustomerEmail = %s'
    cursor.execute(query, (username))
    name = cursor.fetchone()['CustomerName']
    cursor.close()

    return render_template('customer-home.html', name = name)

### customer use cases ###
# view my flights
@app.route('/customer-flight-view')
def customer_flight_view():
    username = session['username']
    cursor = conn.cursor()
    # query = 'SELECT AirlineName, FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, FlightStatus FROM Flight NATURAL JOIN updates NATURAL JOIN purchasedfor NATURAL JOIN ticket NATURAL JOIN customer WHERE CustomerEmail = %s AND DepartureDate > CURRENT_DATE OR (DepartureDate = CURRENT_DATE AND DepartureTime > CURRENT_TIME) ORDER BY DepartureDate'
    query = """
            SELECT AirlineName, FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, FlightStatus FROM Flight 
            NATURAL JOIN Ticket NATURAL JOIN Changes
            WHERE (CustomerEmail = %s AND DepartureDate > CURRENT_DATE) OR (DepartureDate = CURRENT_DATE AND DepartureTime > CURRENT_TIME)
            ORDER BY DepartureDate
            """
    cursor.execute(query, (username))
    data = cursor.fetchall()
    for item in data:
        cursor.close()
    return render_template('customer-flight-view.html', flights = data)

@app.route('/customer-past-flight-view')
def customer_past_flight_view():
    username = session['username']
    cursor = conn.cursor()
    query = """
            SELECT AirlineName, FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, FlightStatus
            FROM Flight NATURAL JOIN Changes NATURAL JOIN Ticket
            WHERE CustomerEmail = %s AND DepartureDate < CURRENT_DATE OR (DepartureDate = CURRENT_DATE AND DepartureTime < CURRENT_TIME)
            ORDER BY DepartureDate
            """
    cursor.execute(query, (username))
    data = cursor.fetchall()
    for item in data:
        cursor.close()
    return render_template('customer-past-flight-view.html', flights = data)

# search for flights
@app.route('/customer-flight-search', methods = ['GET', 'POST'])
def customer_flight_search():
    return render_template('customer-flight-search.html')

# find oneway tickets
@app.route('/customer-oneway-results', methods = ['GET', 'POST'])
def customer_oneway_flight_search():
    departure_city = request.form['departure-city']
    departure_airport = request.form['departure-airport']
    destination_city = request.form['destination-city']
    destination_airport = request.form['destination-airport']
    departure_date = request.form['departure-date']
    cursor = conn.cursor()
    # oneWayQuery = 'SELECT f.AirlineName, f.FlightNumber, f.DepartureDate, f.DepartureTime, ArrivalDate, FlightStatus, COUNT(ticketID) as booked, numberOfSeats FROM flight as f LEFT JOIN purchasedfor AS p ON p.FlightNumber = f.FlightNumber AND p.DepartureDate = f.DepartureDate AND p.DepartureTime = f.DepartureTime INNER JOIN Changes AS u ON u.FlightNumber = f.FlightNumber AND u.DepartureDate = f.DepartureDate AND u.DepartureTime = f.DepartureTime INNER JOIN airplane ON f.AirplaneID = airplane.AirplaneID INNER JOIN airport AS a1 ON a1.AirportName = f.DepartureAirport INNER JOIN airport AS a2 ON a2.AirportName = f.ArrivalAirport WHERE f.FlightNumber NOT IN (SELECT FlightNumber from flight as f2 GROUP BY FlightNumber HAVING COUNT(f2.FlightNumber) > 1) AND a1.AirportCity = %s AND f.DepartureAirport = %s AND a2.AirportCity = %s AND f.ArrivalAirport = %s AND f.DepartureDate = %s GROUP BY f.AirlineName, f.FlightNumber, f.DepartureDate, f.DepartureTime, ArrivalDate, FlightStatus, NumberOfSeats HAVING booked < NumberOfSeats'
    oneWayQuery =  """
                    SELECT f.AirlineName, f.FlightNumber, f.DepartureDate, f.DepartureTime, ArrivalDate, ArrivalTime, FlightStatus, numberOfSeats, COUNT(TicketID) as numFlights
                    FROM Flight as f
                    LEFT JOIN Ticket AS t
                    On t.FlightNumber = f.FlightNumber
                    INNER JOIN Changes AS u
                    ON u.FlightNumber = f.FlightNumber AND u.DepartureDate = f.DepartureDate AND u.DepartureTime = f.DepartureTime
                    INNER JOIN Airplane
                    ON f.AirplaneID = airplane.AirplaneID
                    INNER JOIN Airport AS airport1
                    ON airport1.AirportName = f.DepartureAirport
                    INNER JOIN Airport AS airport2
                    ON airport2.AirportName = f.ArrivalAirport
                    WHERE f.FlightNumber NOT IN
                        (SELECT FlightNumber FROM Flight as f2 
                        GROUP BY FlightNumber 
                        HAVING COUNT(f2.FlightNumber) > 1)
                    AND airport1.AirportCity = %s AND f.DepartureAirport = %s AND airport2.AirportCity = %s AND f.ArrivalAirport = %s AND f.DepartureDate = %s
                    GROUP BY f.AirlineName, f.FlightNumber, f.DepartureDate, f.DepartureTime, ArrivalDate, FlightStatus, numberOfSeats
                    HAVING numFlights < NumberOfSeats
                   """
    cursor.execute(oneWayQuery, (departure_city, departure_airport, destination_city, destination_airport, departure_date))
    data = cursor.fetchall()
    cursor.close()
    today = date.today()
    if departure_date < str(today):
        message = 'Date is in the past'
        data = ''
        return render_template('customer-oneway-results.html', flights = data, error = message)
    elif (data):
        return render_template('customer-oneway-results.html', flights = data)
    else:
        message = "No flights available"
        return render_template('customer-oneway-results.html', flights = data, error = message)
    return

# find round-trip tickets
@app.route('/customer-round-results', methods = ['GET', 'POST'])
def customer_round_flight_search():
    departure_city = request.form['departure-city']
    departure_airport = request.form['departure-airport']
    destination_city = request.form['destination-city']
    destination_airport = request.form['destination-airport']
    departure_date = request.form['departure-date']
    return_date = request.form['return-date']
    cursor = conn.cursor()
    oneWayQuery =  """
                SELECT f.AirlineName, f.FlightNumber, f.DepartureDate, f.DepartureTime, ArrivalDate, ArrivalTime, FlightStatus, numberOfSeats, COUNT(TicketID) as numFlights
                FROM Flight as f
                LEFT JOIN Ticket AS t
                On t.FlightNumber = f.FlightNumber
                INNER JOIN Changes AS u
                ON u.FlightNumber = f.FlightNumber AND u.DepartureDate = f.DepartureDate AND u.DepartureTime = f.DepartureTime
                INNER JOIN Airplane
                ON f.AirplaneID = airplane.AirplaneID
                INNER JOIN Airport AS airport1
                ON airport1.AirportName = f.DepartureAirport
                INNER JOIN Airport AS airport2
                ON airport2.AirportName = f.ArrivalAirport
                WHERE f.FlightNumber NOT IN
                    (SELECT FlightNumber FROM Flight as f2 
                    GROUP BY FlightNumber 
                    HAVING COUNT(f2.FlightNumber) > 1)
                AND airport1.AirportCity = %s AND f.DepartureAirport = %s AND airport2.AirportCity = %s AND f.ArrivalAirport = %s AND f.DepartureDate = %s
                GROUP BY f.AirlineName, f.FlightNumber, f.DepartureDate, f.DepartureTime, ArrivalDate, FlightStatus, numberOfSeats
                HAVING numFlights < NumberOfSeats
                """
    cursor.execute(oneWayQuery, (departure_city, departure_airport, destination_city, destination_airport, departure_date))
    departs = cursor.fetchall()

    cursor.execute(oneWayQuery, (destination_city, destination_airport, departure_city, departure_airport, return_date))
    returns = cursor.fetchall()

    cursor.close()
    today = date.today()
    if departure_date < str(today):
        message = 'Date is in the past'
        data = ''
        return render_template('customer-round-results.html', error = message)
    elif (departs and returns):
        return render_template('customer-round-results.html', departs = departs, returns = returns)
    else:
        message = "No flights available"
        return render_template('customer-round-results.html',  error = message)

# purchase tickets
@app.route('/customer-purchase-ticket', methods = ['GET', 'POST'])
def customer_ticket_purchase():
    flight_number = request.form['flight-number']
    dept_date = request.form['departure-date']
    dept_time = request.form['departure-time']
    cursor = conn.cursor()
    checkFlightHasSeats = 'SELECT f.AirlineName, f.FlightNumber, f.DepartureDate, f.DepartureTime, f.BasePrice, f.ArrivalDate, f.ArrivalTime, f.ArrivalAirport, f.DepartureAirport, COUNT(ticketID) as booked, numberOfSeats FROM flight as f LEFT JOIN purchasedfor AS p ON p.FlightNumber = f.FlightNumber AND p.DepartureDate = f.DepartureDate AND p.DepartureTime = f.DepartureTime INNER JOIN Changes AS u ON u.FlightNumber = f.FlightNumber AND u.DepartureDate = f.DepartureDate AND u.DepartureTime = f.DepartureTime INNER JOIN airplane ON f.AirplaneID = airplane.AirplaneID INNER JOIN airport AS a1 ON a1.AirportName = f.DepartureAirport INNER JOIN airport AS a2 ON a2.AirportName = f.ArrivalAirport WHERE f.FlightNumber NOT IN (SELECT FlightNumber from flight as f2 GROUP BY FlightNumber HAVING COUNT(f2.FlightNumber) > 1) AND f.DepartureDate = %s AND f.DepartureTime = %s AND f.FlightNumber = %s GROUP BY f.AirlineName, f.FlightNumber, f.DepartureDate, f.DepartureTime, ArrivalDate, FlightStatus, NumberOfSeats HAVING booked < NumberOfSeats'
    cursor.execute(checkFlightHasSeats, (dept_date, dept_time, flight_number))
    data = cursor.fetchone()
    airline, arrival_date, arrival_airport, dept_air, arr_time = data['AirlineName'], data['ArrivalDate'], data['ArrivalAirport'], data['DepartureAirport'], data['ArrivalTime']
    totalBooked = data['booked']
    totalSeats = data['numberOfSeats']
    basePrice = data['BasePrice']
    cursor.close()
    if totalBooked/totalSeats >= 0.7: 
        basePrice *= 1.2 
    round_trip = "N/A"
    return render_template('customer-purchase-ticket.html', airline = airline, flight_num = flight_number, dept_date = dept_date, dept_time = dept_time, arr_date = arrival_date, arr_time = arr_time, arr_air = arrival_airport, dept_air = dept_air, baseprice = basePrice)

@app.route('/customer-round-purchase', methods = ['GET', 'POST'])
def customer_round_purchase():
    flight_number1 = request.form['flight-number1']
    departure_date = request.form['departure-date']
    departure_time = request.form['departure-time']
    flight_number2 = request.form['flight-number2']
    return_date = request.form['return-date']
    return_time = request.form['return-time']
    
    cursor = conn.cursor()

    checkFlightHasSeats = 'SELECT f.AirlineName, f.FlightNumber, f.DepartureDate, f.DepartureTime, f.BasePrice, f.ArrivalDate, f.ArrivalTime, f.ArrivalAirport, f.DepartureAirport, COUNT(ticketID) as booked, numberOfSeats FROM flight as f LEFT JOIN purchasedfor AS p ON p.FlightNumber = f.FlightNumber AND p.DepartureDate = f.DepartureDate AND p.DepartureTime = f.DepartureTime INNER JOIN Changes AS u ON u.FlightNumber = f.FlightNumber AND u.DepartureDate = f.DepartureDate AND u.DepartureTime = f.DepartureTime INNER JOIN airplane ON f.AirplaneID = airplane.AirplaneID INNER JOIN airport AS a1 ON a1.AirportName = f.DepartureAirport INNER JOIN airport AS a2 ON a2.AirportName = f.ArrivalAirport WHERE f.FlightNumber NOT IN (SELECT FlightNumber from flight as f2 GROUP BY FlightNumber HAVING COUNT(f2.FlightNumber) > 1) AND f.DepartureDate = %s AND f.DepartureTime = %s AND f.FlightNumber = %s GROUP BY f.AirlineName, f.FlightNumber, f.DepartureDate, f.DepartureTime, ArrivalDate, FlightStatus, NumberOfSeats HAVING booked < NumberOfSeats'

    cursor.execute(checkFlightHasSeats, (departure_date, departure_time, flight_number1))
    data1 = cursor.fetchone()
    print(data1)
    cursor.execute(checkFlightHasSeats, (return_date, return_time, flight_number2))
    data2 = cursor.fetchone()

    airline1, arrival_date1, arrival_airport1, dept_air1, arr_time1 = data1['AirlineName'], data1['ArrivalDate'], data1['ArrivalAirport'], data1['DepartureAirport'], data1['ArrivalTime']
    totalBooked1 = data1['booked']
    totalSeats1 = data1['numberOfSeats']
    basePrice1 = data1['BasePrice']
    if totalBooked1/totalSeats1 >= 0.7: 
        basePrice1 *= 1.2 

    airline2, arrival_date2, arrival_airport2, dept_air2, arr_time2 = data2['AirlineName'], data2['ArrivalDate'], data2['ArrivalAirport'], data2['DepartureAirport'], data2['ArrivalTime']
    totalBooked2 = data2['booked']
    totalSeats2 = data2['numberOfSeats']
    basePrice2 = data2['BasePrice']
    if totalBooked2/totalSeats2 >= 0.7: 
        basePrice2 *= 1.2 

    baseprice = basePrice1 + basePrice2
    cursor.close()

    return render_template('customer-purchase-ticket.html', round = "round", airline1 = airline1, flight_num1 = flight_number1, dept_date1 = departure_date, dept_time1 = departure_time, arr_date1 = arrival_date1, arr_time1 = arr_time1, arr_air1 = arrival_airport1, dept_air1 = dept_air1, baseprice1 = basePrice1, airline2 = airline2, flight_num2 = flight_number2, dept_date2 = return_date, dept_time2 = return_time, arr_date2 = arrival_date2, arr_time2 = arr_time2, arr_air2 = arrival_airport2, dept_air2 = dept_air2, baseprice2 = basePrice2, baseprice = baseprice)

# enter card information
@app.route('/customer-card-info', methods = ['GET', 'POST'])
def customer_card_info():
    cursor = conn.cursor()
    username = session['username']
    card_number = request.form['card-number']
    card_type = request.form['card-type']
    card_name = request.form['card-name']
    expiration_month = request.form['card-month']
    expiration_year = request.form['card-year']
    card_expiration = str(expiration_month) + "/" + expiration_year
    cardExistsQuery = '''
                        SELECT *
                        FROM CardInfo
                        WHERE CardNumber = %s
                      '''
    cursor.execute(cardExistsQuery, (card_number))
    data = cursor.fetchone()
    if (data):
        usesQuery = 'INSERT INTO Uses VALUES(%s, %s)'
        cursor.execute(usesQuery, (card_number, username))
        return render_template('customer-purchase-ticket.html', success='Ticket purchased!')
    else:
        cardQuery = 'INSERT INTO CardInfo VALUES(%s, %s, %s, %s)'
        cursor.execute(cardQuery, (card_number, card_type, card_name, card_expiration))
        usesQuery = 'INSERT INTO Uses VALUES(%s, %s)'
        cursor.execute(usesQuery, (card_number, username))
        return render_template('customer-purchase-ticket.html', success='Ticket purchased!')

# give ratings and comment
@app.route('/customer-rate-flight')
def rate_flights():
    return render_template('customer-rate-flight.html')

@app.route('/customer-rate-flight-auth', methods=['GET', 'POST'])
def rate_flight_auth(): 
    customerEmail = session['username']
    custTicketID = request.form['ticket-number']
    custRate = request.form['rating']
    custComment = request.form['comment']
    cursor = conn.cursor(); 
    checkCustFlightExist = 'SELECT f.FlightNumber, f.DepartureDate, f.DepartureTime FROM Ticket LEFT JOIN Flight AS f on Ticket.FlightNumber = f.FlightNumber WHERE CustomerEmail = %s AND TicketID = %s AND (CURRENT_DATE > DepartureDate OR (CURRENT_DATE = DepartureDate AND CURRENT_TIME > DepartureTime))'
    cursor.execute(checkCustFlightExist,(customerEmail, custTicketID))
    data1 = cursor.fetchone()
    checkNoRate = 'SELECT f.FlightNumber, f.DepartureDate, f.DepartureTime, TicketID FROM Suggested NATURAL JOIN Ticket LEFT JOIN Flight AS f ON Ticket.FlightNumber = f.FlightNumber WHERE CustomerEmail = %s AND TicketID = %s'
    cursor.execute(checkNoRate, (customerEmail, custTicketID))
    data2 = cursor.fetchone()
    if(data1 and not(data2)): #customer was on the flight and there was no rating written 
        custFlightNum = data1['FlightNumber']
        custDeptDate = data1['DepartureDate']
        custDeptTime = data1['DepartureTime']
        ins = 'INSERT INTO Suggested VALUES(%s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (customerEmail, custTicketID, custDeptDate, custDeptTime, custComment, custRate))
        message = "Submitted Successfully! Click the back button to go home!"
        return render_template('customer-rate-flight.html', message = message)
    elif (data2):
        error = "Flight already given a rating"
        return render_template('customer-rate-flight.html', error=error)
    else:
        error = "Ticket ID does not exist or Departure Date in the Future"
        return render_template('customer-rate-flight.html', error=error)

# track my spending
@app.route('/customer-track-spending')
def track_spending(): 
    username = session['username']
    cursor = conn.cursor()
    getCustYearlySpending = 'SELECT SUM(SoldPrice) AS spend FROM ticket NATURAL Join Flight WHERE CustomerEmail = %s AND PurchaseDate >= CURRENT_DATE - INTERVAL 1 YEAR'
    cursor.execute(getCustYearlySpending, (username))
    yearSpend = cursor.fetchone()['spend']
    getCustMonthlySpending = 'SELECT MONTHNAME(PurchaseDate) AS month, SUM(soldPrice) as spent FROM ticket NATURAL JOIN Flight WHERE CustomerEmail = %s AND PurchaseDate >= CURRENT_DATE - INTERVAL 6 MONTH GROUP BY MONTHNAME(PurchaseDate)'
    cursor.execute(getCustMonthlySpending, (username))
    custMonthlySpending = cursor.fetchall() 
    labels = []
    months = {1:'January', 2: 'February', 3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}
    from datetime import date
    currMonth = date.today().month
    earliest = currMonth-5
    for i in range(earliest,currMonth+1): 
        if i>0 and i<13: 
            labels.append(months[i])
        elif i < 1: 
            i += 12
            labels.append(months[i])
    values = []
    for elem in labels:
        added = False
        for i in range (len(custMonthlySpending)): 
            if custMonthlySpending[i]['month'] == elem: 
                values.append(custMonthlySpending[i]['spent'])
                added = True
                break
        if added == False: 
            values.append(0)
    maximumValue = max(values) + 10
    return render_template('customer-track-spending.html', labels = labels, values = values, yearSpend = yearSpend, max = maximumValue)    

@app.route('/customer-track-spending-limits', methods = ['GET', 'POST'])
def customerSpendingCustom(): 
	cursor = conn.cursor()
	#print(request.form)
	username = session['username']
	start_date = request.form['start-date1']
	#print(request.form)
	end_date = request.form['end-date1']
	getCustMonthlySpending = 'SELECT MONTHNAME(PurchaseDate) AS month, YEAR(PurchaseDate) AS year, SUM(soldPrice) as spent FROM ticket NATURAL JOIN Flight WHERE CustomerEmail = %s AND PurchaseDate >= %s AND PurchaseDate <= %s GROUP BY month, year'
	cursor.execute(getCustMonthlySpending, (username, start_date, end_date))
	custMonthlySpending = cursor.fetchall() 
	labels = []
	values = []
	for elem in custMonthlySpending: 
		date = str(elem['month']) + " " +str(elem['year'])
		labels.append(date)
		values.append(elem['spent'])
	maximumValue = max(values) + 10
	return render_template('customer-track-spending.html', labels = labels, values = values, max = maximumValue)

##### staff #####

# staff registration / login
@app.route('/staff-registration', methods=['GET', 'POST'])
def staff_registration():
    return render_template('staff-registration.html')

@app.route('/staff-registration-auth', methods=['GET', 'POST'])
def staff_registration_auth():
        #grabs information from the forms
    username = request.form['username']
    first_name = request.form['first-name']
    last_name = request.form['last-name']
    password = request.form['password']
    dateOfBirth = request.form['date-of-birth']
    airlineName = request.form['airline']
    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    noDupEmailQuery = 'SELECT Username FROM AirlineStaff WHERE Username = %s'
    cursor.execute(noDupEmailQuery, (username))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('staff-registration.html', error = error)
    else:
        #password = hashlib.md5(password.encode())
        # check if the staff airline exists
        noAirlineQuery = 'SELECT AirlineName FROM Airline WHERE AirlineName = %s'
        cursor.execute(noAirlineQuery, (airlineName))
        data = cursor.fetchone()

        if not data:
            ins = 'INSERT INTO Airline VALUE(%s)'
            cursor.execute(ins, (airlineName))

        ins = 'INSERT INTO AirlineStaff VALUES(%s, md5(%s), %s, %s, %s, %s)'
        cursor.execute(ins, (username, password, first_name, last_name, dateOfBirth, airlineName))
        conn.commit()
        cursor.close()
        return render_template('staff-login.html')

def loggedIn():
    return len(session) > 0

@app.route('/staff-login-auth',  methods=['GET', 'POST'])
def staff_login_auth():
    #grabs information from the forms
    username = request.form['staff-username']
    password = request.form['staff-password']

    #cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = 'SELECT Username, StaffPassword FROM AirlineStaff WHERE Username = %s and StaffPassword = md5(%s)'
    cursor.execute(query, (username, password))
    #stores the results in a variable
    data = cursor.fetchone()

    # use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None

    sessionRunning = loggedIn()
    if (sessionRunning == True): 
        error = 'Other users signed in. Please sign out of current session.'
        return render_template('staff-login.html', error=error)

    if(data):
        # creates a session for the the user
        # session is a built in
        session['username'] = username

        # query to return the name of the staff
        cursor = conn.cursor()
        query = 'SELECT FirstName FROM AirlineStaff WHERE Username = %s and StaffPassword = md5(%s)'
        cursor.execute(query, (username, password))
        name = cursor.fetchone()['FirstName']
        cursor.close()

        return redirect('staff-home')
    else:
        error = 'Invalid login or username'
        return render_template('staff-login.html', error=error)

@app.route('/staff-home', methods=['GET', 'POST'])
def staff_home():
    # cursor used to send queries
    cursor = conn.cursor()
    if len(session) == 0:
        return render_template('no-session.html')
    
    username = session['username']

    # query to return the name of the staff
    query = 'SELECT Firstname FROM AirlineStaff WHERE Username = %s'
    cursor.execute(query, (username))
    name = cursor.fetchone()['Firstname']
    cursor.close()
    return render_template('staff-home.html', name = name)

### staff use cases ###
@app.route('/staff-flight-view', methods = ['GET', 'POST'])
def staff_flight_view():
    username = session['username']
    cursor = conn.cursor()
    query = 'SELECT AirlineName FROM AirlineStaff WHERE Username = %s'
    cursor.execute(query, (username))
    airline_name = cursor.fetchone()
    current_airline_name = airline_name['AirlineName']
    flightQuery = """
                  SELECT DISTINCT AirlineName, FlightNumber, DepartureDate, DepartureTime, DepartureAirport, ArrivalDate, ArrivalTime, FlightStatus FROM AirlineStaff NATURAL JOIN Flight NATURAL JOIN Changes
                  WHERE AirlineName = %s AND (DepartureDate <= CURRENT_DATE + INTERVAL 30 DAY AND (DepartureDate > CURRENT_DATE))
                  OR (DepartureDate = CURRENT_DATE AND DepartureTime > CURRENT_TIME)
                  """
    cursor.execute(flightQuery, (current_airline_name))
    data = cursor.fetchall()
    cursor.close()
    return render_template('staff-flight-view.html', flights = data)

# create flight
@app.route('/staff-create-flight', methods=['GET', 'POST'])
def staff_create_flight():
    return render_template('staff-create-flight.html')

@app.route('/staff-create-flight-auth', methods=['GET', 'POST'])
def staff_create_flight_auth():
    airline_name = request.form['airline-name']
    departure_date = request.form['departure-date']
    departure_time = request.form['departure-time'] + ':00'
    flight_number = request.form['flight-number']
    departure_airport = request.form['departure-airport']
    arrival_airport = request.form['arrival-airport']
    arrival_date = request.form['arrival-date']
    arrival_time = request.form['arrival-time'] + ':00'
    base_price = request.form['base-price']
    airplane_ID = request.form['airplane-ID']

    cursor = conn.cursor()
    query = 'SELECT * FROM Flight WHERE FlightNumber = %s AND DepartureDate = %s AND DepartureTime = %s'
    cursor.execute(query, (flight_number, departure_date, departure_time))
    data = cursor.fetchone()

    if (data):      #flight already exists
        return render_template('staff-create-flight.html', error='Flight Already Exists.')
    else:
        flightValues = 'INSERT INTO Flight VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(flightValues, (airline_name, departure_date, departure_time, flight_number, departure_airport, arrival_airport, arrival_date, arrival_time, base_price, airplane_ID))
        arrivesValues = 'INSERT INTO Arrives VALUES(%s, %s, %s, %s)'
        cursor.execute(arrivesValues, (arrival_airport, flight_number, departure_date, departure_time))
        departsValues = 'INSERT INTO Departs VALUES(%s, %s, %s, %s)'
        cursor.execute(departsValues, (departure_airport, flight_number, departure_date, departure_time))
        username = session['username']
        changesValues = 'INSERT INTO Changes VALUES(%s, %s, %s, %s, %s)'
        cursor.execute(changesValues, (username, flight_number, departure_date, departure_time, 'on-time'))
        conn.commit()
        cursor.close()
        return render_template('staff-create-flight.html', success='Successfully Added!')

# update flight status
@app.route('/staff-update-flight-status')
def staff_update_flight_status():
    return render_template('staff-update-flight-status.html')

@app.route('/staff-update-flight-status-auth', methods=['GET', 'POST'])
def staff_update_flight_status_auth():
    username = session['username']
    flight_number = request.form['flight-number']
    departure_date = request.form['departure-date']
    departure_time = request.form['departure-time']
    flight_status = request.form['flight-status']
    
    cursor = conn.cursor()
    query = ('SELECT * FROM Changes '
            'WHERE Username = %s AND FlightNumber = %s AND DepartureDate = %s AND DepartureTime = %s')
    cursor.execute(query, (username, flight_number, departure_date, departure_time))
    data = cursor.fetchone()

    if (data):
        updateFlightQuery = ('UPDATE Changes SET Username = %s, FlightStatus = %s'
                            'WHERE FlightNumber = %s AND DepartureDate = %s AND DepartureTime = %s')
        cursor.execute(updateFlightQuery, (username, flight_number, departure_date, departure_time, flight_status))
        conn.commit()
        cursor.close()
        return render_template('staff-update-flight-status.html', success='Successfully Changed!') 

    else: 
        return render_template('staff-update-flight-status.html', error='Flight Does Not Exist.')

# add airplane
@app.route('/staff-add-airplane', methods=['GET', 'POST'])
def staff_add_airplane():
    return render_template('staff-add-airplane.html')

@app.route('/staff-add-airplane-auth', methods=['GET', 'POST'])
def staff_add_airplane_auth():
    airline_name = request.form['airline-name']
    airplane_id = request.form['airplane-ID']
    num_seats = request.form['num-seats']
    airplane_company = request.form['airplane-company']
    airplane_age = request.form['airplane-age']

    cursor = conn.cursor()
    query = 'SELECT * FROM Airplane WHERE AirlineName = %s and AirplaneID = %s'
    cursor.execute(query, (airline_name, airplane_id))
    data = cursor.fetchone()
    cursor.close()

    if (data):
        return render_template('staff-add-airplane.html', error='This Airplane Already Exists.')
    else:
        cursor = conn.cursor()
        addAirplane = 'INSERT INTO Airplane VALUES(%s, %s, %s, %s, %s)'
        cursor.execute(addAirplane, (airline_name, int(airplane_id), int(num_seats), airplane_company, int(airplane_age)))
        getAirplanes = 'SELECT * FROM Airplane WHERE AirlineName = %s'
        cursor.execute(getAirplanes, (airline_name))
        all_airplanes = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('staff-add-airplane.html', success="Successfully Added!")    #need a new template here

# add airport
@app.route('/staff-add-airport', methods=['GET', 'POST'])
def staff_add_airport():
    return render_template('staff-add-airport.html')

@app.route('/staff-add-airport-auth', methods=['GET', 'POST'])
def staff_add_airport_auth():
    airport_code = request.form['airport-code']
    airport_name = request.form['airport-name']
    airport_city = request.form['airport-city']
    airport_country = request.form['airport-country']
    airport_type = request.form['airport-type']

    cursor = conn.cursor()
    query = 'SELECT * FROM Airport WHERE AirportName = %s'
    cursor.execute(query, (airport_name))
    data = cursor.fetchone()
    cursor.close()
    if (data):
        return render_template('staff-add-airport.html', error='This Airport Already Exists.')
    else:
        cursor = conn.cursor()
        addAirport = 'INSERT INTO Airport Values(%s, %s, %s, %s, %s)'
        cursor.execute(addAirport, (airport_code, airport_name, airport_city, airport_country, airport_type))
        conn.commit()
        cursor.close()
        return render_template('staff-add-airport.html', success='Successfully Added!')

# view customer ratings
@app.route('/staff-view-ratings')
def staffViewRatings():
        return render_template('staff-view-ratings.html')

@app.route('/staff-view-ratings-auth', methods = ['GET', 'POST'])
def staff_view_ratings_auth():
    flight_number = request.form['flight-number']
    cursor = conn.cursor()
    query = 'SELECT CustomerComment, Rate FROM Suggested WHERE FlightNumber = %s GROUP BY CustomerComment, Rate'
    cursor.execute(query, (flight_number))
    data = cursor.fetchall()

    query = 'SELECT AVG(Rate) FROM Suggested WHERE FlightNumber = %s'
    cursor.execute(query, (flight_number))
    avg_rate = cursor.fetchone()['AVG(Rate)']

    if (data):
        return render_template('staff-view-ratings.html', avg_rate=avg_rate, data=data, flight_number = flight_number)
    
    return render_template('staff-view-ratings.html', error="This flight does not exist.")
# view frequent customers
@app.route('/staff-frequent-customers')
def staffViewFreqCustomers():
    cursor = conn.cursor()
    username = session['username']
    airlineQuery = 'SELECT AirlineName FROM AirlineStaff WHERE username = %s'
    cursor.execute(airlineQuery, (username))
    airline_name = cursor.fetchone()['AirlineName']
    
    queryYear = """
                SELECT CustomerEmail, COUNT(*) AS numFlights
                FROM Ticket
                WHERE AirlineName = %s AND purchaseDate >= CURRENT_DATE - INTERVAL 1 YEAR
                GROUP BY CustomerEmail
                ORDER BY numFlights DESC 
                LIMIT 1
                """

    cursor.execute(queryYear, (airline_name))
    top_customer = cursor.fetchone()['CustomerEmail']

    query = """
            SELECT AirlineName, FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, FlightStatus
            FROM Flight NATURAL JOIN Changes NATURAL JOIN Ticket
            WHERE CustomerEmail = %s AND DepartureDate < CURRENT_DATE OR (DepartureDate = CURRENT_DATE AND DepartureTime < CURRENT_TIME)
            ORDER BY DepartureDate
            """
    cursor.execute(query, (top_customer))
    data = cursor.fetchall()

    cursor.close()
    return render_template('staff-frequent-customers.html', top_customer = top_customer, flights = data)

# view customer flights
@app.route('/staff-view-customer-flights', methods = ['GET', 'POST'])
def staffViewCustomerFlights():
    customer_email = request.form['customer-email']
    cursor = conn.cursor()
    username = session['username']
    airlineQuery = ('SELECT AirlineName'
                    'FROM AirlineStaff'
                    'WHERE username = %s')
    cursor.execute(airlineQuery, (username))                    
    airline_name = cursor.fetchone()['AirlineName']
    flightsQuery = ('SELECT FlightNumber, DepartureDate, DepartureTime'
                    'FROM Flight NATURAL JOIN Changes NATURAL JOIN PurchasedFor NATURAL JOIN Ticket NATURAL JOIN Customer'
                    'WHERE CustomerEmail = %s AND AirlineName = %s')
    cursor.execute(flightsQuery, (customer_email, airline_name))
    customerFlights = cursor.fetchall()
    cursor.close()
    if customerFlights:
        return render_template('staff-view-Customer-Flights.html', customerFlights = customerFlights, customer_email = customer_email)
    else: #no customer flights found
        return


@app.route('/staff-view-revenue')
def staffViewReports():
    cursor = conn.cursor()
    monthReportQuery = ('SELECT COUNT(TicketID) AS totalTickets, MONTHNAME(PurchaseDate) AS Month'
                        'FROM Ticket' 
                        'WHERE PurchaseDate >= CURRENT_DATE - INTERVAL 1 MONTH GROUP BY Month')
    cursor.execute(monthReportQuery)
    lastMonth = cursor.fetchone()
    labels, values = [lastMonth['month']], [lastMonth['tickets']]

    yearReportQuery = ('SELECT COUNT(TicketID) AS totalTickets, MONTHNAME(PurchaseDate) AS Month'
                        'FROM Ticket' 
                        'WHERE PurchaseDate >= CURRENT_DATE - INTERVAL 1 YEAR GROUP BY Month')
    cursor.execute(yearReportQuery)
    lastYear = cursor.fetchall()
    months = {1:'January', 2: 'February', 3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}

    currentMonth = date.today().month
    earliest = currentMonth - 12
    labels1 = []
    for i in range(earliest,currentMonth):
        if i > 0 and i < 13:
            labels1.append(months[i])
        elif i < 1: 
            i += 12
            labels1.append(months[i])
    values1 = []
    for item in labels1:
        added = False
        for i in range(len(lastYear)):
            if lastYear[i]['month'] == item:
                values1.append(lastYear[i]['tickets'])
                added = True
                break
        if added == False:
            values1.append(0)
    maxValue = max(values1) + 1

    return render_template('staff-view-revenue.html', labels = labels, values = values, labels1 = labels1, values1 = values1, max = 10, max1 = maxValue)

@app.route('/staff-view-revenue')
def staffViewRevenue():
    cursor = conn.cursor()
    monthlyRevenueQuery = ('SELECT SUM(SoldPrice) AS Sale'
                           'FROM Ticket'
                           'WHERE PurchaseDate >= CURRENT_DATE - INTERVAL 1 MONTH')
    cursor.execute(monthlyRevenueQuery)
    monthSales = cursor.fetchall()

    annualRevenueQuery = ('SELECT Sum(SoldPrice) As Sale'
                          'FROM Ticket'
                          'WHERE PurchaseDate >= CURRENT_DATE - INTERVAL 1 YEAR')
    cursor.execute(annualRevenueQuery)
    yearSales = cursor.fetchall()

    return render_template('staff-view-revenue.html', monthSales = monthSales, yearSales = yearSales)


@app.route('/staff-View-Revenue-Travel-Class')
def staffViewRevenueTravelClass():
    cursor = conn.cursor()
    classRevenueQuery = ('SELECT Sum(SoldPrice) AS Sale'
                         'FROM Ticket'
                         'WHERE PurchaseDate <= CURRENT_DATE'
                         'GROUP BY TravelClass')
    cursor.execute(classRevenueQuery)

    return render_template('staff-view-revenue-.html')

@app.route('/staff-top-destinations')
def staffViewTopDestinations():
    username = session['username']
    cursor = conn.cursor()
    query = """
            SELECT AirportCity FROM Airport AS a LEFT JOIN Flight AS f ON f.ArrivalAirport = a.AirportName
            GROUP BY AirportName
            ORDER BY Count(AirportName) DESC LIMIT 3
            """

    cursor.execute(query)
    data = cursor.fetchall()
 
    first = data[0]['AirportCity']
    second = data[1]['AirportCity']
    third = data[2]['AirportCity']
    # >= DATEADD(MONTH, -3, GETDATE())

    return render_template('staff-top-destinations.html', first = first, second=second, third=third)


if __name__ == "__main__":
    app.run("127.0.0.1", 8000, debug = True)
