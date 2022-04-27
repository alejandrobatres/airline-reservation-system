#Alejandro Batres, Devin Zhu

#4a
SELECT FlightNumber, AirlineName, AirplaneID, DepartureDate, DepartureTime 
FROM Flight 
WHERE CURRENT_DATE < DepartureDate OR (CURRENT_DATE = DepartureDate AND CURRENT_TIME < DepartureTime);

#4b
SELECT FlightNumber, AirlineName, AirplaneID, DepartureDate, DepartureTime
FROM Changes 
NATURAL JOIN Flight 
WHERE FlightStatus = 'Delayed';


#4c
SELECT distinct CustomerName
FROM Customer as c 
INNER JOIN Ticket as t 
ON c.CustomerEmail = t.CustomerEmail 
INNER JOIN PurchasedFor as p 
ON t.TicketID = p.TicketID
WHERE t.FlightNumber = p.FlightNumber; 

#4d
SELECT AirplaneID
FROM Airplane
WHERE AirlineName = 'China Eastern';
