### Final project for CS-UY 3083.
By Alejandro Batres & Devin Zhu

## Description
Need to book a flight that doesn't really exist?  
Use our airline reservation system!

This system includes a *customer portal*, with...
- Sign up
- Flight view
- Ticket purchase
- Rate flight

And a *employee portal*, with...
- Sign up
- Airplane registration
- Airline registration
- Flight creation
- Flight view
- Cusomter ratings


## Run Locally

Configure MySQL by creating the database called `air_ticket_reservation` and running `SQL\ Files/create_tables.sql`   
You can then fill the databse with sample data by running `SQL\ Files/insert_info.sql`

In Terminal:
```bash
export FLASK_APP=app
flask run
```

The application will run in the browser in [http://localhost:8000/](http://localhost:8000/).
