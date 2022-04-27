# Alejandro Batres, Devin Zhu

CREATE TABLE IF NOT EXISTS Airline(
    AirlineName varchar(50),
    PRIMARY KEY (AirlineName)
    ); 

CREATE TABLE IF NOT EXISTS Airplane(
    AirlineName varchar(50) NOT NULL, 
    AirplaneID int(10) NOT NULL, 
    NumberOfSeats int(5) NOT NULL,
    AirplaneCompany varchar(30) NOT NULL,
    AirplaneAge int(3) NOT NULL,
    PRIMARY KEY (AirlineName, AirplaneID),
    FOREIGN KEY (AirlineName) REFERENCES Airline(AirlineName)
    );

CREATE TABLE IF NOT EXISTS Flight(
    AirlineName varchar(50) NOT NULL, 
    DepartureDate date NOT NULL, 
    DepartureTime time NOT NULL, 
    FlightNumber int(5) NOT NULL,
    DepartureAirport varchar(50) NOT NULL,
    ArrivalAirport varchar(50) NOT NULL, 
    ArrivalDate date NOT NULL,
    ArrivalTime time NOT NULL, 
    BasePrice float(6,2) NOT NULL, 
    AirplaneID int(10) NOT NULL, 
    PRIMARY KEY (FlightNumber, DepartureDate, DepartureTime),
    FOREIGN KEY (AirlineName) REFERENCES Airline(AirlineName)
    );

CREATE TABLE IF NOT EXISTS Airport(
    AirportCode int(10) NOT NULL,
    AirportName varchar(50), 
    AirportCity varchar(50) NOT NULL,
    AirportCountry varchar(50) NOT NULL,
    AirportType varchar(50) NOT NULL,
    PRIMARY KEY (AirportName)
    );

CREATE TABLE IF NOT EXISTS Arrives(
    AirportName varchar(50), 
    FlightNumber int(5), 
    DepartureDate date, 
    DepartureTime time,
    FOREIGN KEY (AirportName) REFERENCES Airport(AirportName),
    FOREIGN KEY (FlightNumber, DepartureDate, DepartureTime) REFERENCES Flight(FlightNumber, DepartureDate, DepartureTime)
    );

CREATE TABLE IF NOT EXISTS Departs(
    AirportName varchar(50), 
    FlightNumber int(5), 
    DepartureDate date, 
    DepartureTime time, 
    PRIMARY KEY (AirportName, FlightNumber, DepartureDate, DepartureTime), 
    FOREIGN KEY (AirportName) REFERENCES Airport(AirportName), 
    FOREIGN KEY (FlightNumber, DepartureDate, DepartureTime) REFERENCES Flight(FlightNumber, DepartureDate, DepartureTime)
    ); 

CREATE TABLE IF NOT EXISTS AirlineStaff(
    Username varchar(50), 
    StaffPassword varchar(50) NOT NULL,
    Firstname varchar(50) NOT NULL, 
    Lastname varchar(50) NOT NULL, 
    DateOfBirth date NOT NULL, 
    AirlineName varchar(50) NOT NULL,
    PRIMARY KEY (Username), 
    FOREIGN KEY (AirlineName) REFERENCES Airline(AirlineName)
    );

CREATE TABLE IF NOT EXISTS PhoneNumber(
    Username varchar(50), 
    AirlineStaffPhoneNumber varchar(11) NOT NULL, 
    PRIMARY KEY (Username, AirlineStaffPhoneNumber), 
    FOREIGN KEY (Username) REFERENCES AirlineStaff(Username)
    );

CREATE TABLE IF NOT EXISTS Changes(
    Username varchar(50), 
    FlightNumber int(5), 
    DepartureDate date, 
    DepartureTime time, 
    FlightStatus varchar(20) NOT NULL, 
    PRIMARY KEY (Username, FlightNumber, DepartureDate, DepartureTime), 
    FOREIGN KEY (Username) REFERENCES AirlineStaff(Username),
    FOREIGN KEY (FlightNumber, DepartureDate, DepartureTime) REFERENCES Flight(FlightNumber, DepartureDate, DepartureTime)
    );

CREATE TABLE IF NOT EXISTS Customer(
    CustomerName varchar(50) NOT NULL, 
    CustomerEmail varchar(50),
    CustomerPassword varchar(50) NOT NULL, 
    BuildingNumber int(3) NOT NULL, 
    Street varchar(50) NOT NULL, 
    City varchar(50) NOT NULL, 
    State varchar(50) NOT NULL, 
    CustomerPhoneNumber varchar(11) NOT NULL,
    PassportNumber varchar(8) NOT NULL, 
    PassportExpiration date NOT NULL, 
    PassportCountry varchar(50) NOT NULL, 
    DateOfBirth date NOT NULL, 
    PRIMARY KEY (CustomerEmail)
    );

CREATE TABLE IF NOT EXISTS Suggested(
    CustomerEmail varchar(50),
    FlightNumber int(5), 
    DepartureDate date, 
    DepartureTime time, 
    CustomerComment text DEFAULT NULL,
    Rate float(2,1) NOT NULL, 
    PRIMARY KEY (CustomerEmail, FlightNumber, DepartureDate, DepartureTime), 
    FOREIGN KEY (CustomerEmail) REFERENCES Customer(CustomerEmail),
    FOREIGN KEY (FlightNumber, DepartureDate, DepartureTime) REFERENCES Flight(FlightNumber, DepartureDate, DepartureTime)
    );

CREATE TABLE IF NOT EXISTS Updates(
    Username varchar(50), 
    FlightNumber int(5), 
    DepartureDate date, 
    DepartureTime time, 
    FlightStatus varchar(20) NOT NULL, 
    PRIMARY KEY (Username, FlightNumber, DepartureDate, DepartureTime), 
    FOREIGN KEY (Username) REFERENCES AirlineStaff(Username),
    FOREIGN KEY (FlightNumber, DepartureDate, DepartureTime) REFERENCES Flight(FlightNumber, DepartureDate, DepartureTime)
    );

CREATE TABLE IF NOT EXISTS Ticket(
    TicketID varchar(50), 
    CustomerEmail varchar(50) NOT NULL, 
    TravelClass varchar(50) NOT NULL,
    AirlineName varchar(50) NOT NULL, 
    FlightNumber int(5) NOT NULL, 
    SoldPrice float(6, 2) NOT NULL, 
    PurchaseDate date NOT NULL, 
    PurchasedTime time NOT NULL, 
    PRIMARY KEY (TicketID), 
    FOREIGN KEY (CustomerEmail) REFERENCES Customer(CustomerEmail),
    FOREIGN KEY (AirlineName) REFERENCES Airline(AirlineName),
    FOREIGN KEY (FlightNumber) REFERENCES Flight(FlightNumber)
    ); 

CREATE TABLE IF NOT EXISTS PurchasedFor(
    TicketID varchar(50), 
    FlightNumber int(5), 
    DepartureDate date, 
    DepartureTime time, 
    PRIMARY KEY (TicketID, FlightNumber, DepartureDate, DepartureTime), 
    FOREIGN KEY (TicketID) REFERENCES Ticket(TicketID),
    FOREIGN KEY (FlightNumber, DepartureDate,DepartureTime) REFERENCES Flight(FlightNumber, DepartureDate, DepartureTime)
    );

CREATE TABLE IF NOT EXISTS CardInfo(
    CardNumber varchar(20), 
    CardType varchar(6) NOT NULL, 
    CardName varchar(50) NOT NULL, 
    ExpirationDate date NOT NULL, 
    PRIMARY KEY (CardNumber)
    );

CREATE TABLE IF NOT EXISTS Uses(
    CardNumber varchar(20),
    CustomerEmail varchar(50), 
    PRIMARY KEY (CardNumber, CustomerEmail), 
    FOREIGN KEY (CardNumber) REFERENCES CardInfo(CardNumber),
    FOREIGN KEY (CustomerEmail) REFERENCES Customer(CustomerEmail)
    );

CREATE TABLE IF NOT EXISTS PaymentMethod(
    CardNumber varchar(20), 
    TicketID varchar(50),
    PRIMARY KEY (CardNumber, TicketID),
    FOREIGN KEY (CardNumber) REFERENCES cardinfo(CardNumber),
    FOREIGN KEY (TicketID) REFERENCES Ticket(TicketID)
    );

