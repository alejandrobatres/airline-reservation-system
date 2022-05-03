from venv import create
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors # Used to itnerface the database
from datetime import datetime # May need this for your datetime columns/client
import hashlib # But can use this for md5
import re # If you want to use regex
import json # You'll need this library to parse json objects in python

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
app.config['DB_PASSWORD'] = '' #"root"
app.config['APP_DB'] = "blog"
app.config['CHARSET'] = "utf8mb4"

# Connect to the DB
conn =  pymysql.connect(host=app.config['APP_HOST'],
                       user=app.config['DB_USER'],
                       #unix_socket='/Applications/MAMP/tmp/mysql/mysql.sock',
                       password=app.config['DB_PASSWORD'],
                       db=app.config['APP_DB'],
                       charset=app.config['CHARSET'],
                       cursorclass=pymysql.cursors.DictCursor)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')

# REST = Representational State Transfer
# GET, POST are REST methods
# GET specifies what to do when the client wants a page loaded
# POST is for when you want to mutate data in your database
 
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    success = None
    allusers = None
    
    # Prepared SQL Statement - Just basic SQL
    # "%s" is NOT specifically a string. It's a placeholder for the values you pass in to PyMySQL
    createUserStatement = ("INSERT INTO SiteUser(`email`, `password`, `type`) "
                            "VALUES(%s, md5(%s), %s)")
    fetchUserStatement = "SELECT * FROM SiteUser WHERE type = %s"

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        typeUser = 1

        if not validateEmail(email):
            error = "Invalid email!"

        try:
            # Need cursor for database connections!
            cursor = conn.cursor()

            # Pass in tuple of values

            # getting all users
            cursor.execute(fetchUserStatement, (1))
            allusers = cursor.fetchall()

            # creating user
            cursor.execute(createUserStatement, (email, password, typeUser))
            conn.commit() # Whenever you update or insert using PyMySQL, you must commit to the database            

            # Always close when you're done with the cursor
        except Exception as e:
            error = "An error occurred: {}".format(e)
        cursor.close() # This will error if there's an error with conn.cursor() BTW
        
        if not error:
            success = "User added successfully"
        # We can pass variables to our HTML templates!
    elif request.method == 'GET':
        try:
            # Need cursor for database connections!
            cursor = conn.cursor()

            # Pass in tuple of values
            cursor.execute(fetchUserStatement, (1))
            allusers = cursor.fetchall()

            # Always close when you're done with the cursor
        except Exception as e:
            error = "An error occurred: {}".format(e)
        cursor.close() # This will error if there's an error with conn.cursor() BTW
    return render_template("register.html", error=error, success=success, allusers=allusers)

@app.route('/Airline-Staff-Register')
def airline_staff_register():
    return render_template('Airline-Staff-Register.html')

@app.route('/Airline-Staff-Login')
def airline_staff_login():
    return render_template('Airline-Staff-Login.html')

@app.route('/Customer-Register')
def customer_register():
    return render_template('Customer-Register.html')

@app.route('/Customer-Login')
def customer_login():
    return render_template('Customer-Login.html')


#Public Info
@app.route('/Public-Search-Flights')
def publicSearchFlights():
    return render_template('Public-Search-Flights.html')

@app.route('/Public-View-Flights')
def publicViewFlights():
    cursor = conn.cursor()
    query = ('SELECT AirlineName, FlightNumber, DepartureDate, DepartureTime, ArrivalDate, FlightStatus'
             'FROM Flight NATURAL JOIN Updates'
             'ORDER BY DepartureDate')
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('Public-View-Flights.html', flights = data)


#Customer Use Cases
@app.route('/Customer-View-Flights')
def customerViewFlights():
    username = session['username']
    cursor = conn.cursor()
    query = ('SELECT AirlineName, FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, FlightStatus'
            'FROM Flight NATURAL JOIN Changes NATURAL JOIN PurchasedFor NATURAL JOIN Ticket NATURAL JOIN CUSTOMER'
            'WHERE CustomerEmail = %s AND DepartureDate > CURRENT_DATE OR (DepartureDate = CURRENT_DATE AND DepartureTime > CURRENT_TIME)' 
            'ORDER BY DepartureDate')
    cursor.execute(query, (username))
    data = cursor.fetchall()
    for item in data:
        print(item['AirlineName'])
        cursor.close()
    return render_template('Customer-View-Flights.html')

@app.route('/Customer-View-Past-Flights')
def customerViewPastFlights():
    username = session['username']
    cursor = conn.cursor()
    query = ('SELECT AirlineName, FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, FlightStatus'
            'FROM Flight NATURAL JOIN Changes NATURAL JOIN PurchasedFor NATURAL JOIN Ticket NATURAL JOIN CUSTOMER'
            'WHERE CustomerEmail = %s AND DepartureDate < CURRENT_DATE OR (DepartureDate = CURRENT_DATE AND DepartureTime < CURRENT_TIME)' 
            'ORDER BY DepartureDate')
    cursor.execute(query, (username))
    data = cursor.fetchall()
    for item in data:
        print(item['AirlineName'])
        cursor.close()
    return render_template('Customer-View-Past-Flights.html')

@app.route('/Customer-Search-Flights')
def customerSearchFlights():
    return render_template('Customer-Search-Flights.html')

@app.route('/Customer-Search-One-Way-Flights', methods = ['GET', 'POST'])
def customerSearchOneWay():
    departure_city = request.form.get['departure-city']
    departure_airport = request.form.get['departure-airport']
    destination_city = request.form.get['destination-city']
    destination_airport = request.form.get['destination-airport']
    departure_date = request.form.get['departure-date']
    cursor = conn.cursor()
    oneWayQuery = ('SELECT ')
    #'SELECT f.AirlineName, f.FlightNumber, f.DepartureDate, f.DepartureTime, ArrivalDate, FlightStatus, COUNT(ticketID) as booked, numberOfSeats FROM flight as f LEFT JOIN purchasedfor AS p ON p.FlightNumber = f.FlightNumber AND p.DepartureDate = f.DepartureDate AND p.DepartureTime = f.DepartureTime INNER JOIN updates AS u ON u.FlightNumber = f.FlightNumber AND u.DepartureDate = f.DepartureDate AND u.DepartureTime = f.DepartureTime INNER JOIN airplane ON f.AirplaneID = airplane.AirplaneID INNER JOIN airport AS a1 ON a1.AirportName = f.DepartureAirport INNER JOIN airport AS a2 ON a2.AirportName = f.ArrivalAirport WHERE f.FlightNumber NOT IN (SELECT FlightNumber from flight as f2 GROUP BY FlightNumber HAVING COUNT(f2.FlightNumber) > 1) AND a1.AirportCity = %s AND f.DepartureAirport = %s AND a2.AirportCity = %s AND f.ArrivalAirport = %s AND f.DepartureDate = %s GROUP BY f.AirlineName, f.FlightNumber, f.DepartureDate, f.DepartureTime, ArrivalDate, FlightStatus HAVING booked < NumberOfSeats'
	
    return


@app.route('/Customer-Search-Two-Way-Flights', methods = ['GET', 'POST'])
def customerSearchTwoWay():
    departure_city = request.form.get['departure-city']
    departure_airport = request.form.get['departure-airport']
    destination_city = request.form.get['destination-city']
    destination_airport = request.form.get['destination-airport']
    departure_date = request.form.get['departure-date']
    return_date = request.form.get['return-date']
    cursor = conn.cursor()
    twoWayQuery = ('SELECT')
    cursor.execute(twoWayQuery, (departure_city,departure_airport,destination_city,destination_airport,departure_date,return_date))
    return


@app.route('/Customer-Purchase-Flight', methods = ['GET', 'POST'])
def customerPurchaseFlight():
    flight_number = request.form.get['flight-number']
    departure_date = request.form.get['departure-date']
    departure_time = request.form.get['departure-time']
    cursor = conn.cursor()
    #query = 'SELECT f.AirlineName, f.FlightNumber, f.DepartureDate, f.DepartureTime, f.BasePrice, f.ArrivalDate, f.ArrivalTime, f.ArrivalAirport, f.DepartureAirport, COUNT(ticketID)'
    return


def customerCancelTrip():
    customer_email = session['username']
    return


@app.route('/Customer-Rate-Comment', methods = ['GET', 'POST'])
def customerRateComment():
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
        return render_template('Customer-Rate-Comment.html')
    elif (data1):
        return
    
    return


@app.route('/Customer-Track-Spending')
def customerTrackSpending():
    username = session['username']
    cursor = conn.cursor()
    yearlySpendingQuery = ('SELECT SUM(SoldPrice) As Spent'
                            'FROM TICKET NATURAL JOIN PurchasedFor'
                            'WHERE CustomerEmail = %s AND PurchaseDate >= CURRENT_DATE - INTERVAL 1 YEAR')
    cursor.execute(yearlySpendingQuery, (username))
    #yearlySpend = cursor.fetchone()['spend']

    monthlySpendingQuery = ('SELECT MONTHNAME(PurchaseDate) AS Month, SUM(SoldPrice) AS Spent'
            'FROM Ticket NATURAL JOIN PurchasedFor'
            'WHERE CustomerEmail = %s AND PurchaseDate >= CURRENT_DATE - INTERVAL 6 MONTH'
            'GROUP BY MONTHNAME(PurchaseDate)')
    cursor.execute(monthlySpendingQuery, (username))
    #montlySpend = cursor.fetchall()

    return render_template('Customer-Track-Spending.html')



#Airline Staff Use Cases
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


@app.route('Airline-Staff-View-Frequent-Customers')
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

@app.route('Airline-Staff-View-Customer-Flights', methods = ['GET', 'POST'])
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


@app.route('Airline-Staff-View-Reports')
def staffViewReports():
    cursor = conn.cursor()
    monthReportQuery = ('SELECT COUNT(TicketID) AS totalTickets, MONTHNAME(PurchaseDate) AS Month'
                        'FROM Ticket' 
                        'WHERE PurchaseDate >= CURRENT_DATE - INTERVAL 1 MONTH GROUP BY Month')
    cursor.execute(monthReportQuery)
    lastMonth = cursor.fetchone()

    yearReportQuery = ('SELECT COUNT(TicketID) AS totalTickets, MONTHNAME(PurchaseDate) AS Month'
                        'FROM Ticket' 
                        'WHERE PurchaseDate >= CURRENT_DATE - INTERVAL 1 YEAR GROUP BY Month')
    cursor.execute(yearReportQuery)
    lastYear = cursor.fetchall()
    return render_template('Airline-Staff-View-Reports.html')

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
