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
    return redirect('/customer-login')

# public information
@app.route('/public-flight-search')
def public_flight_search():
    return render_template('public-flight-view.html')

@app.route('/public-flight-view')
def public_flight_view():
    cursor = conn.cursor()
    query = """
            SELECT AirlineName, FlightNumber, DepartureDate, DepartureTime, ArrivalDate, FlightStatus
            FROM Flight NATURAL JOIN Updates
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
        return render_template('index.html')

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

        return render_template('customer-home.html', name = name)
    else:
        error = 'Invalid login or username'
        return render_template('customer-login.html', error=error)

@app.route('/customer-home')
def customer_home():
    # cursor used to send queries
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
            SELECT AirlineName, FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, FlightStatus
            FROM Flight NATURAL JOIN Changes NATURAL JOIN PurchasedFor NATURAL JOIN Ticket NATURAL JOIN CUSTOMER
            WHERE CustomerEmail = %s AND DepartureDate > CURRENT_DATE OR (DepartureDate = CURRENT_DATE AND DepartureTime > CURRENT_TIME)
            ORDER BY DepartureDate
            """
    cursor.execute(query, (username))
    data = cursor.fetchall()
    for item in data:
        print(item['AirlineName'])
        cursor.close()
    return render_template('customer-flight-view.html', flights = data)

@app.route('/customer-past-flight-view')
def customer_past_flight_view():
    username = session['username']
    cursor = conn.cursor()
    query = """
            SELECT AirlineName, FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, FlightStatus
            FROM Flight NATURAL JOIN Changes NATURAL JOIN PurchasedFor NATURAL JOIN Ticket NATURAL JOIN CUSTOMER
            WHERE CustomerEmail = %s AND DepartureDate < CURRENT_DATE OR (DepartureDate = CURRENT_DATE AND DepartureTime < CURRENT_TIME)
            ORDER BY DepartureDate
            """
    cursor.execute(query, (username))
    data = cursor.fetchall()
    for item in data:
        print(item['AirlineName'])
        cursor.close()
    return render_template('customer-past-flight-view.html', flights = data)

# search for flights
@app.route('/customer-flight-search', methods = ['GET', 'POST'])
def customer_flight_search():
    return render_template('customer-flight-search.html')

@app.route('/customer-oneway-results', methods = ['GET', 'POST'])
def customer_oneway_flight_search():
    departure_city = request.form['departure-city']
    departure_airport = request.form['departure-airport']
    destination_city = request.form['destination-city']
    destination_airport = request.form['destination-airport']
    departure_date = request.form['departure-date']
    cursor = conn.cursor()
    oneWayQuery =  """
                    SELECT f.AirlineName, f.FlightNumber, f.DepartureDate, f.DepartureTime, ArrivalDate, FlightStatus, numberOfSeats, COUNT(ticketID) as numFlights
                    FROM Flight as f
                    LEFT JOIN PurchasedFor AS pf
                    On pf.FlightNumber = f.FlightNumber AND pf.DepartureDate = f.DepartureDate AND pf.DepartureTime = f.DepartureTime
                    INNER JOIN Updates AS u
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

@app.route('/customer-round-results', methods = ['GET', 'POST'])
def customer_round_flight_search():
    departure_city = request.form['departure-city']
    departure_airport = request.form['departure-airport']
    destination_city = request.form['destination-city']
    destination_airport = request.form['destination-airport']
    departure_date = request.form['departure-date']
    return_date = request.form['return-date']
    cursor = conn.cursor()
    twoWayQuery = """
                    SELECT f.AirlineName, f.FlightNumber, f.DepartureDate, f3.DepartureDate AS returnDate, f.DepartureTime, f3.DepartureTime AS returnTime, f.ArrivalDate, FlightStatus, numberOfSeats, COUNT(ticketID) AS numFlights
                    FROM Flight AS f
                    LEFT JOIN PurchasedFor AS pf
                    ON pf.FlightNumber = f.FlightNumber AND pf.DepartureDate = f.DepartureDATE AND pf.DepartureTime = f.DepartureTime
                    INNER JOIN Updates AS u
                    ON u.FlightNumber = f.FlightNumber AND u.DepartureDate = f.DepartureDate AND u.DepartureTime = f.DepartureTime
                    INNER JOIN Airport AS airport1
                    ON airport1.AirportName = f.DepartureAirport
                    INNER JOIN Airport AS airport2
                    ON airport2.AirportName = f.ArrivalAirport
                    INNER JOIN Flight AS f3
                    ON f.FlightNumber = f3.FlightNumber AND f.ArrivalAirport = f3.DepartureAirport
                    WHERE f.FlightNumber IN
                        (SELECT FlightNumber
                        FROM Flight AS f2
                        GROUP BY FlightNumber
                        HAVING COUNT(f2.FlightNumber) > 1)
                    AND f3.DepartureDate > f.DepartureDate AND airport1.AirportCity = %s AND f.DepartureAirport = %s AND airport2.AirportCity = %s AND f.ArrivalAirport = %s AND f.DepartureDate = %s AND f3.DepartureDate = %s
                    GROUP BY f.AirlineName, f.FlightNumber, f.DepartureDate, f.DepartureTime, f.ArrivalDate, FlightStatus, returnDate, returnTime, numberOfSeats
                    HAVING numFlights < NumberOfSeats
                  """
    cursor.execute(twoWayQuery, (departure_city,departure_airport,destination_city,destination_airport,departure_date,return_date))
    data = cursor.fetchall()
    cursor.close()
    today = date.today()
    if departure_date < str(today):
        message = 'Date is in the past'
        data = ''
        return render_template('customer-round-results.html', flights = data, error = message)
    elif (data):
        return render_template('customer-round-results.html', flights = data)
    else:
        message = "No flights available"
        return render_template('customer-round-results.html', flights = data, error = message)
    return

# purchase tickets
@app.route('/customer-oneway-purchase', methods = ['GET', 'POST'])
def customer_ticket_purchase():
    flight_number = request.form['flight-number']
    departure_date = request.form['departure-date']
    departure_time = request.form['departure-time']
    cursor = conn.cursor()
    emptySeatsQuery =   """
                        SELECT f.AirlineName, f.FlightNumber, f.DepartureDate, f.DepartureTime, f.BasePrice, f.ArrivalDate, f.ArrivalTime, f.ArrivalAirport, f.DepartureAirport, COUNT(ticketID) AS bookedSeats, f.numberOfSeats
                        FROM Flight AS f
                        LEFT JOIN PurchasedFor AS pf
                        ON pf.FlightNumber = f.FlightNumber AND pf.DepartureDate = f.DepartureDate AND pf.DepartureTime = f.DepartureTime
                        INNER JOIN Updates AS u
                        ON u.FlightNumber = f.FlightNumber AND u.DepartureDate = f.DepartureDate AND u.DepartureTime = f.DepartureTime
                        INNER JOIN Airplane
                        ON f.AirplaneID = Airplane.AirplaneID
                        INNER JOIN Airport AS airport1
                        ON airport1.AirportName = f.DepartureAirport
                        INNER JOIN Airport AS airport2
                        ON airport2.AirportName = f.ArrivalAirport
                        WHERE f.FlightNumber NOT IN
                                SELECT FlightNumber from Flight AS f2
                                GROUP BY FlightNumber
                                HAVING COUNT(f2.FlightNumber) > 1
                            AND f.DepartureDate = %s AND f.DepartureTime = %s AND f.FlightNumber = %s
                            GROUP BY f.AirlineName, f.FlightNumber, f.DepartureDate, f.DepartureTime, f.ArrivalDate, f.FlightStatus
                            HAVING bookedSeats < f.numberOfSeats
                        """
    cursor.execute(emptySeatsQuery, (departure_date, departure_time, flight_number))
    data = cursor.fetchone()
    airline, arrival_date, arrival_airport, departure_airport, arrival_time = data['AirlineName'], data['ArrivalDate'], data['ArrivalAirport'], data['DepartureAirport'], data['ArrivalTime']
    totalBooked = data['booked']
    totalSeats = data['numberOfSeats']
    basePrice = data['BasePrice']
    if totalBooked > totalSeats >= 0.75:
        basePrice *= 1.25
    round_trip = 'N/A'
    return render_template('customer-ticket-purchase.html', airline = airline, flight_num = flight_number, dept_date = departure_date, dept_time = departure_time, arr_date = arrival_date, arr_time = arrival_time, arr_air = arrival_airport, dept_air = departure_airport, basePrice = basePrice, f1Price = basePrice, round_trip = round_trip)

@app.route('/customer-round-purchase', methods = ['GET', 'POST'])
def customer_round_purchase():
    flight_number = request.form.get['flight-number']
    departure_date = request.form.get['departure-date']
    departure_time = request.form.get['departure-time']
    return_date = request.form.get['return-date']
    return_time = request.form.get['return-time']
    cursor = conn.cursor()
    emptySeatsQuery = ('SELECT f.FlightNumber, f.DepartureDate, f.DepartureTime, COUNT(ticketID) AS bookedSeats, numberOfSeats' 
                       'FROM flight AS f' 
                       'NATURAL JOIN airplane LEFT JOIN Purchasedfor AS pf'
                       'ON f.DepartureDate = pf.DepartureDate AND f.DepartureTime = pf.DepartureTime AND f.FlightNumber = pf.FlightNumber' 
                       'WHERE f.flightNumber = %s AND f.departureDate = %s AND f.departureTime = %s' 
                       'GROUP BY f.FlightNumber, f.DepartureDate, f.DepartureTime, numberOfSeats')
    cursor.execute(emptySeatsQuery, (flight_number, departure_date, departure_time))
    flight1Seats = cursor.fetchone()
    flight1SeatsBooked, flight1TotalSeats = flight1Seats['booked'], flight1Seats['numberOfSeats']
    if flight1SeatsBooked/flight1TotalSeats == 1 or flight1Seats['DepartureDate'] < date.today():
        error = "Flight fully booked or already left"
        return render_template('Customer-Purchase-Flight.html', error = error)
    cursor.execute(emptySeatsQuery, (flight_number, return_date, return_time))
    flight2Seats = cursor.fetchone()
    flight2SeatsBooked, flight2TotalSeats = flight2Seats['booked'], flight2Seats['numberOfSeats']
    flightPriceQuery = ('SELECT * FROM Flight'
                        'WHERE FlightNumber = %s AND DepartureDate = %s AND DepartureTime = %s')
    cursor.execute(flightPriceQuery, (flight_number, departure_date, departure_time))
    flight1Price = cursor.fetchone()
    airline, arrival_date, arrival_time, arrival_airport = flight1Price['AirlineName'], flight1Price['ArrivalDate'], flight1Price['ArrivalTime'], flight1Price['ArrivalAirport']
    basePrice1 = flight1Price['BasePrice']
    cursor.execute(flightPriceQuery, (flight_number, return_date, return_time))
    flight2Price = cursor.fetchone()
    departure_airport = flight2Price['DepartureAirport']
    basePrice2 = flight2Price['BasePrice']
    if flight1SeatsBooked/flight1TotalSeats >= 0.75:
        basePrice1 *= 1.25
    if flight2SeatsBooked / flight2TotalSeats >= 0.75:
        basePrice2 *= 1.25
    totalPrice = basePrice1 + basePrice2
    round_trip = "Returning Flight: \nReturn Date: " + str(return_date) + "\nReturn Time: " + str(return_time)
    return render_template('customer-ticket-purchase.html', airline = airline, flight_num = flight_number, dept_date = departure_date, dept_time = departure_time, arr_date = arrival_date, arr_time = arrival_time, arr_air = arrival_airport, dept_air = departure_airport, baseprice = totalPrice, f1price = basePrice1, f2price = basePrice2, round_trip = round_trip)

@app.route('Customer-Card-Info', methods = ['GET', 'POST'])
def customerCardInfo():
    cursor = conn.cursor()
    username = session['username']
    card_number = request.form.get['card-number']
    card_type = request.form.get['card-type']
    card_name = request.form.get['card-name']
    expiration_month = request.form.get['card-month']
    expiration_year = request.form.get['card-year']
    card_expiration = str(expiration_month) + "/" + expiration_year
    cardExistsQuery = '''
                        SELECT *
                        FROM CardInfo
                        WHERE CardNumber = %s
                      '''
    cursor.execute(cardExistsQuery, (card_number))
    data = cursor.fetchone()
    if (data):
        print('Card already exists.')
    else:
        cardQuery = 'INSERT INTO CardInfo VALUES(%s, %s, %s, %s)'
        cursor.execute(cardQuery, (card_number, card_type, card_name, card_expiration))
        usesQuery = 'INSERT INTO Uses VALUES(%s, %s)'
        cursor.execute(usesQuery, (card_number, username))
        return render_template('Customer-Card-Info.html')



@app.route('/Customer-Cancel-Trip', methods = ['GET', 'POST'])
def customerCancelTrip():
    customer_email = session['username']
    customer_ticketID = request.form.get['ticket-ID']
    flightExistsQuery = '''
                        SELECT FlightNumber, DepartureDate
                        FROM Ticket NATURAL JOIN PurchasedFor NATURAL JOIN Customer
                        WHERE CustomerEmail = %s AND TicketID = %s AND (CURRENT_DATE < DepartureDate - INTERVAL 1 DAY)
                        '''
    cursor = conn.cursor()
    cursor.execute(flightExistsQuery, (customer_email, customer_ticketID))
    data = cursor.fetchone()
    if (data):
        customer_flight_number = request.form.get['flight-number']
        customer_departure_date = request.form.get['departure-date']
        customer_departure_time = request.form.get['departure-time']
        cancelTripQuery = '''
                            DELETE FROM PurchasedFor
                            WHERE TicketID = %s AND FlightNumber = %s AND DepartureDate = %s AND DepartureTime = %s
                          '''
        cursor.execute(cancelTripQuery, (customer_ticketID, customer_flight_number, customer_departure_date, customer_departure_time))
        conn.commit()
        cursor.close()
        return render_template('Customer-Cancel-Trip.html')
    else:
        return

# give ratings and comment
@app.route('/customer-rate-comment', methods = ['GET', 'POST'])
def customer_rate_comment():
    CustomerEmail = session['username']
    customer_ticket_ID = request.form.get['ticket-ID']
    customer_rate = request.form.get['rate']
    customer_comment = request.form.get['comment']
    cursor = conn.cursor()
    flightExistsQuery = ('SELECT FlightNumber, DepartureDate, DepartureTime'
                        'FROM Ticket NATURAL JOIN PurchasedFor NATURAL JOIN Customer'
                        'WHERE CustomerEmail = %s AND TicketID = %s AND (CURRENT_DATE > DepartureDate OR (CURRENT_DATE = DepartureDate AND CURRENT_TIME > DepartureTime))')
    cursor.execute(flightExistsQuery, (CustomerEmail, customer_ticket_ID))
    data = cursor.fetchone()
    noRatingCommentQuery = ('SELECT FlightNumber, DepartureDate, DepartureTime, TicketID'
                            'FROM Suggested NATURAL JOIN Ticket'
                            'WHERE CuustomerEmail = %s AND TicketID = %s')
    cursor.execute(noRatingCommentQuery, (CustomerEmail, customer_ticket_ID))
    data1 = cursor.fetchone()

    if (data and not (data1)):
        customer_flight_number = data['FlightNumber']
        customer_departure_date = data['DepartureDate']
        customer_departure_time = data['DepartureTime']
        query = 'INSERT INTO Suggested VALUES(%s, %s, %s, %s, %s, %s)'
        cursor.execute(query, (CustomerEmail, customer_flight_number, customer_departure_date, customer_departure_time, customer_comment, customer_rate))
        conn.commit()
        cursor.close()
        return render_template('customer-rate-comment.html')
    elif (data1):
        return
    
    return

@app.route('/rate-flights')
def rate_flights():
    return render_template('rate-fights.html')

@app.route('/rate-flights-auth', methods=['GET', 'POST'])
def rate_flight_auth(): 
    customerEmail = session['username']
    custTicketID = request.form['ticket-number']
    custRate = request.form['rate']
    custComment = request.form['comment']
    cursor = conn.cursor(); 
    print(request.form)
    checkCustFlightExist = 'SELECT FlightNumber, DepartureDate, DepartureTime FROM ticket NATURAL JOIN purchasedfor NATURAL JOIN customer WHERE CustomerEmail = %s AND TicketID = %s AND (CURRENT_DATE > DepartureDate OR (CURRENT_DATE = DepartureDate AND CURRENT_TIME > DepartureTime))'
    cursor.execute(checkCustFlightExist,(customerEmail, custTicketID))
    data1 = cursor.fetchone()
    print(data1)
    checkNoRate = 'SELECT FlightNumber, DepartureDate, DepartureTime, TicketID FROM suggested NATURAL JOIN ticket WHERE CustomerEmail = %s AND TicketID = %s'
    cursor.execute(checkNoRate, (customerEmail, custTicketID))
    data2 = cursor.fetchone()
    print(data2)
    print(data2)
    if(data1 and not(data2)): #customer was on the flight and there was no rating written 
        custFlightNum = data1['FlightNumber']
        custDeptDate = data1['DepartureDate']
        custDeptTime = data1['DepartureTime']
        ins = 'INSERT INTO suggested VALUES(%s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (customerEmail, custFlightNum, custDeptDate, custDeptTime, custComment, custRate))
        conn.commit()
        cursor.close()
        message = "Submitted Successfully! Click the back button to go home!"
        return render_template('rate-flights.html', message = message)
    elif (data2): 
        error = "Flight already given a rating"
        return render_template('rate-flights.html', error=error)
    else: 
        error = "Ticket ID does not exist or Departure Date in the Future"
        return render_template('rate-flights.html', error=error)

# track my spending
@app.route('/track-spending')
def track_spending(): 
    username = session['username']
    cursor = conn.cursor()
    getCustYearlySpending = 'SELECT SUM(SoldPrice) AS spend FROM ticket NATURAL JOIN purchasedfor WHERE CustomerEmail = %s AND PurchaseDate >= CURRENT_DATE - INTERVAL 1 YEAR'
    cursor.execute(getCustYearlySpending, (username))
    yearSpend = cursor.fetchone()['spend']
    getCustMonthlySpending = 'SELECT MONTHNAME(PurchaseDate) AS month, SUM(soldPrice) as spent FROM ticket NATURAL JOIN purchasedfor WHERE CustomerEmail = %s AND PurchaseDate >= CURRENT_DATE - INTERVAL 6 MONTH GROUP BY MONTHNAME(PurchaseDate)'
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
    return render_template('track-spending.html', labels = labels, values = values, yearSpend = yearSpend, max = maximumValue)    

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

        return render_template('staff-home.html', name = name)
    else:
        error = 'Invalid login or username'
        return render_template('staff-login.html', error=error)

@app.route('/staff-home')
def staff_home():
    # cursor used to send queries
    cursor = conn.cursor()

    username = session['username']

    # query to return the name of the staff
    query = 'SELECT Firstname FROM AirlineStaff WHERE Username = %s'
    cursor.execute(query, (username))
    name = cursor.fetchone()['Firstname']
    cursor.close()

    return render_template('staff-home.html', name = name)

### staff use cases ###
@app.route('/Airline-Staff-View-Flights', methods = ['GET', 'POST'])
def staffViewFlights():
    username = session['username']
    cursor = conn.cursor()
    query = ('SELECT AirlineName FROM AirlineStaff'
            'WHERE Username = %s')
    cursor.execute(query, (username))
    airline_name = cursor.fetchone()
    current_airline_name = airline_name['AirlineName']
    flightQuery = ('SELECT DISTINCT FlightNumber, DepartureDate, DepartureTime, DepartureAirport, ArrivalDate, ArrivalTime FROM AirlineStaff NATURAL JOIN Flight'
                  'WHERE AirlineName = %s AND (DepartureDate <= CURRENT_DATE + INTERVAL 30 DAY AND (DepartureDate > CURRENT_DATE))'
                  'OR (DepartureDate = CURRENT_DATE AND DepartureTime > CURRENT_TIME')
    cursor.execute(flightQuery, (current_airline_name))
    data = cursor.fetchall()
    cursor.close()
    return render_template('Airline-Staff-View-Flights.html', flights = data)


@app.route('/Airline-Staff-Create-Flights', methods=['GET', 'POST'])
def staffCreateFlights():
    airline_name = request.form.get['airline-name']
    departure_date = request.form.get['departure-date']
    departure_time = request.form.get['departure-time']
    flight_number = request.form.get['flight-number']
    departure_airport = request.form.get['departure-airport']
    arrival_airport = request.form.get['arrival-airport']
    arrival_date = request.form.get['arrival-airport']
    arrival_time = request.form.get['arrival-time']
    base_price = request.form.get['base-price']
    airplane_ID = request.form.get['airplane-ID']

    cursor = conn.cursor()
    query = ('SELECT * FROM Flight'
            'WHERE FlightNumber = %s AND DepartureDate = %s AND DepartureTime = %s')
    cursor.execute(query, (flight_number, departure_date, departure_time))
    data = cursor.fetchone()

    if (data):      #flight already exists
        return
    
    else: 
        flightValues = 'INSERT INTO Flight VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(flightValues, (airline_name, departure_date, departure_time, flight_number, departure_airport, arrival_airport, arrival_date, arrival_time, base_price, airplane_ID))
        arrivesValues = 'INSERT INTO Arrives VALUES(%s, %s, %s, %s)'
        cursor.execute(arrivesValues, (arrival_airport, flight_number, departure_date, departure_time))
        departsValues = 'INSERT INTO Departs VALUES(%s, %s, %s, %s)'
        cursor.execute(departsValues, (departure_airport, flight_number, departure_date, departure_time))
        username = session['username']
        changesValues = 'INSERT INTO Changes VALUES(%s, %s, %s, %s, %s)'
        cursor.execute(changesValues, (username, flight_number, departure_date, departure_time, 'On Time'))
        conn.commit()
        cursor.close()
        return render_template()            #need a new template here

@app.route('/Airline-Staff-Update-Flight-Status', methods=['GET', 'POST'])
def staffUpdateFlightStatus():
    username = session['username']
    flight_number = request.form.get['flight-number']
    departure_date = request.form.get['departure-date']
    departure_time = request.form.get['departure-time']
    flight_status = request.form.get['flight-status']
    
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
        return render_template()        #need new template here   

    else: 
        #flight does not exist
        return


@app.route('/Airline-Staff-Add-Airplane', methods=['GET', 'POST'])
def staffAddAirplane():
    airline_name = request.form.get['airline-name']
    airplane_id = request.form.get['airplane-ID']
    num_seats = request.form.get['num-seats']
    airplane_company = request.form.get['airplane_company']
    airplane_age = request.form.get['airplane_age']

    cursor = conn.cursor()
    query = ('SELECT * FROM Airplane'
            'WHERE AirlineName = %s AND AirplaneID = %s')
    cursor.execute(query, (airline_name, airplane_id))
    data = cursor.fetchone()

    if (data):
        return
    else:
        addAirplane = 'INSERT INTO Airplane VALUES(%s, %s, %s, %s, %s)'
        cursor.execute(addAirplane, (airline_name, airplane_id, num_seats, airplane_company, airplane_age))
        getAirplanes = ('SELECT * FROM Airplane'
                        'WHERE airlineName = %s')
        cursor.execute(getAirplanes, (airline_name))
        all_airplanes = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template()        #need a new template here

@app.route('/Airline-Staff-Add-Airport', methods=['GET', 'POST'])
def staffAddAirport():
    airport_code = request.form.get['airport_code']
    airport_name = request.form.get['airport_code']
    airport_city = request.form.get['airport_city']
    airport_country = request.form.get['airport_country']
    airport_type = request.form.get['airport_type']

    cursor = conn.cursor()
    query = ('SELECT * FROM Airport'
            'WHERE AirportName = %s')
    cursor.execute(query, (airport_name))
    data = cursor.fetchone()
    if (data):
        return
    else:
        addAirport = 'INSERT INTO Airport Values(%s, %s, %s, %s, %s)'
        cursor.execute(addAirport, (airport_code, airport_name, airport_city, airport_country, airport_type))
        conn.commit()
        cursor.close()
        return


@app.route('/Airline-Staff-View-Ratings', methods = ['GET', 'POST'])
def staffViewRatings():
    flight_number = request.form.get['flight-number']
    departure_date = request.form.get['departure-date']
    departure_time = request.form.get['departure-time']
    cursor = conn.cursor()
    query = ('SELECT CustomerComment, Rate FROM Suggested'
            'WHERE FlightNumber = %s AND DepartureDate = %s AND DepartureTime = %s')
    cursor.execute(query, (flight_number, departure_date, departure_time))
    data = cursor.fetchall()

    if (data):
        return render_template('Airline-Staff-View-Ratings.html', flights= data, flight_number = flight_number, date = departure_date, time = departure_time)
    
    else: 
        return


@app.route('/Airline-Staff-View-Frequent-Customers')
def staffViewFreqCustomers():
    cursor = conn.cursor()
    username = session['username']
    airlineQuery = ('SELECT AirlineName'
                    'FROM AirlineStaff'
                    'WHERE username = %s')
    cursor.execute(airlineQuery, (username))
    airline_name = cursor.fetchone()['AirlineName']
    
    queryYear = ('SELECT CustomerEmail, COUNT(*) AS numFlights'
                'FROM Ticket'
                'WHERE AirlineName = %s AND purchaseDate >= CURRENT_DATE - INTERVAL 1 YEAR'
                'GROUP BY CustomerEmail'
                'ORDER BY numFlights DESC' 
                'LIMIT 1')
    cursor.execute(queryYear, (airline_name))
    mostFrequentCustomer = cursor.fetchone()
    cursor.close()
    return render_template('Airline-Staff-View-Frequency-Customers.html', mostFrequentCustomer = mostFrequentCustomer)

@app.route('/Airline-Staff-View-Customer-Flights', methods = ['GET', 'POST'])
def staffViewCustomerFlights():
    customer_email = request.form.get['customer-email']
    cursor = conn.cursor()
    username = session['username']
    airlineQuery = ('SELECT AirlineName'
                    'FROM AirlineStaff'
                    'WHERE username = %s')
    cursor.execute(airlineQuery, (username))                    
    airline_name = cursor.fetchone()['AirlineName']
    flightsQuery = ('SELECT FlightNumber, DepartureDate, DepartureTime'
                    'FROM Flight NATURAL JOIN Updates NATURAL JOIN PurchasedFor NATURAL JOIN Ticket NATURAL JOIN Customer'
                    'WHERE CustomerEmail = %s AND AirlineName = %s')
    cursor.execute(flightsQuery, (customer_email, airline_name))
    customerFlights = cursor.fetchall()
    cursor.close()
    if customerFlights:
        return render_template('Airline-Staff-View-Customer-Flights.html', customerFlights = customerFlights, customer_email = customer_email)
    else: #no customer flights found
        return


@app.route('/Airline-Staff-View-Reports')
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

    return render_template('Airline-Staff-View-Reports.html', labels = labels, values = values, labels1 = labels1, values1 = values1, max = 10, max1 = maxValue)

@app.route('/Airline-Staff-View-Revenue')
def staffViewRevenue():
    cursor = conn.cursor()
    monthlyRevenueQuery = ('SELECT SUM(SoldPrice) AS Sale'
                           'FROM Ticket'
                           'WHERE PurchaseDate >= CURRENT_DATE - INTERVAL 1 MONTH')
    cursor.execute(monthlyRevenueQuery)
    #monthSales = cursor.fetchall()

    annualRevenueQuery = ('SELECT Sum(SoldPrice) As Sale'
                          'FROM Ticket'
                          'WHERE PurchaseDate >= CURRENT_DATE - INTERVAL 1 YEAR')
    cursor.execute(annualRevenueQuery)
    #yearSales = cursor.fetchall()

    return render_template('Airline-Staff-Compare-Revenue.html')


@app.route('/Airline-Staff-View-Revenue-Travel-Class')
def staffViewRevenueTravelClass():
    cursor = conn.cursor()
    classRevenueQuery = ('SELECT Sum(SoldPrice) AS Sale'
                         'FROM Ticket'
                         'WHERE PurchaseDate <= CURRENT_DATE'
                         'GROUP BY TravelClass')
    cursor.execute(classRevenueQuery)

    return render_template('Airline-Staff-View-Revenue-Travel-Class.html')

@app.route('/Airline-Staff-View-Top-Destinations')
def staffViewTopDestinations():
    username = session['username']
    cursor = conn.cursor()
    airlineQuery = ('SELECT AirlineName FROM AirlineStaff'
                    'WHERE username = %s')
    cursor.execute(airlineQuery, (username))
    airline_name = cursor.fetchone()
    ratingsQuery = ('SELECT AirlineName, FlightNumber, DepartureDate, DepartureTime, AVG(Rate) as averageRating'
                    'FROM Suggested NATURAL JOIN Flight'
                    'WHERE AirlineName = %s'
                    'GROUP BY AirlineName, FlightNumber, DepartureDate, DepartureTime')
    cursor.execute(ratingsQuery, (airline_name['AirlineName']))
    #averageRatings = cursor.fetchall()
    conn.commit()
    topDestinationsMonthQuery = ('SELECT AirportCity'
                            'FROM TICKET NATURAL JOIN PurchasedFor NATURAL JOIN Flight INNER JOIN Airport'
                            'ON arrivalAirport = airport.AirportName'
                            'WHERE AirlineName = %s AND arrivalDate >= CURRENT_DATE - INTERVAL 3 MONTH'
                            'GROUP BY AirportName'
                            'ORDER BY Count(AirportName) DESC'
                            'LIMIT 3')
    cursor.execute(topDestinationsMonthQuery, (airline_name['AirlineName']))
    topDestMonth = cursor.fetchall()
    conn.commit()

    topDestinationsYearQuery = ('SELECT AirportCity'
                            'FROM TICKET NATURAL JOIN PurchasedFor NATURAL JOIN Flight INNER JOIN Airport'
                            'ON arrivalAirport = airport.AirportName'
                            'WHERE AirlineName = %s AND arrivalDate >= CURRENT_DATE - INTERVAL 1 YEAR'
                            'GROUP BY AirportName'
                            'ORDER BY Count(AirportName) DESC'
                            'LIMIT 3')
    cursor.execute(topDestinationsYearQuery, (airline_name['AirlineName']))
    topDestYear = cursor.fetchall()
    conn.commit()
    cursor.close()

    return render_template('Airline-Staff-View-Top-Destination.html')






if __name__ == "__main__":
    app.run("127.0.0.1", 8000, debug = True)
