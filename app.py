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
app.config['DB_PASSWORD'] = "root"
app.config['APP_DB'] = "blog"
app.config['CHARSET'] = "utf8mb4"

# Connect to the DB
conn =  pymysql.connect(host=app.config['APP_HOST'],
                       user=app.config['DB_USER'],
                       unix_socket='/Applications/MAMP/tmp/mysql/mysql.sock',
                       password=app.config['DB_PASSWORD'],
                       db=app.config['APP_DB'],
                       charset=app.config['CHARSET'],
                       cursorclass=pymysql.cursors.DictCursor)

@app.route('/')
def index():
    return render_template("index.html")

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
    createUserStatement = "INSERT INTO SiteUser(`email`, `password`, `type`) VALUES(%s, md5(%s), %s)"
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
    
if __name__ == "__main__":
    app.run("127.0.0.1", 8000, debug = True)
