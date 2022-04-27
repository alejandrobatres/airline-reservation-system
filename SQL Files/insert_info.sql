#Alejandro Batres, Devin Zhu

#3a
INSERT INTO Airline VALUES ("China Eastern");


#3b
INSERT INTO Airport VALUES (1010101010, 'JFK', 'NYC', 'USA', 'international');
INSERT INTO Airport VALUES (1010101011, 'PVG', 'Shanghai', 'China', 'international');


#3c
INSERT INTO Customer VALUES('Devin', 'dz1295@nyu.edu', '123', 370, 'Jay', 'NYC', 'NY', '12345678901', '12345678', '2026-01-01', 'USA', '2000-07-04');
INSERT INTO Customer VALUES('Alejandro', 'ab8041@nyu.edu', '321', 370, 'Jay', 'NYC', 'NY', '98765432101', '87654321', '2026-01-02', 'USA', '2000-01-01');
INSERT INTO Customer VALUES('Steven', 'steven123@nyu.edu', '456', 370, 'Jay', 'NYC', 'NY', '2341563900', '23419643', '2022-12-31', 'USA', '2000-12-31');


#3d
INSERT INTO Airplane VALUES('China Eastern', 1234567890, 150, 'Boeing', 10);
INSERT INTO Airplane VALUES('China Eastern', 2233445566, 200, 'Airbus', 7);
INSERT INTO Airplane VALUES('China Eastern', 1357938210, 175, 'Boeing', 1);

#3e
INSERT INTO AirlineStaff VALUES('Staff1', '123', 'John', 'Brown', '1990-10-09', 'China Eastern');

#3f
INSERT INTO Flight VALUES('China Eastern', '2021-05-10', '10:00', 12345, 'JFK', 'PVG', '2021-05-10', '20:00', 565.00, 999);
INSERT INTO Changes VALUES('Staff1', 12345, '2021-05-10', '10:00', 'On-time'); 

INSERT INTO Flight VALUES('China Eastern', '2022-04-01', '8:00', 54321, 'PVG', 'JFK', '2022-04-01', '23:00', 785.00, 111); 
INSERT INTO Changes VALUES('Staff1', 54321, '2022-04-01', '8:00', 'Delayed');

INSERT INTO Flight VALUES('China Eastern', '2023-03-17', '15:00', 94316, 'JFK', 'PVG', '2022-03-18', '3:00', 650.00, 123);
INSERT INTO Changes VALUES('Staff1', 94316, '2023-03-17', '15:00', 'On-time');

#3g
INSERT INTO Ticket VALUES('1', 'dz1295@nyu.edu', 'first_class', 'China Eastern', 12345, 458.85, '2021-04-01', '19:45');
INSERT INTO Ticket VALUES('2', 'ab8041@nyu.edu', 'business_class', 'China Eastern', 54321, 650.50, '2022-03-15', '17:30');
INSERT INTO Ticket VALUES('3', 'steven123@nyu.edu', 'economy_class', 'China Eastern', 94316, 500.00, '2023-02-10', '8:00');

INSERT INTO PurchasedFor VALUES('1', 12345, '2021-05-10', '10:00');
INSERT INTO PurchasedFor VALUES('2', 54321, '2022-04-01', '8:00');
INSERT INTO PurchasedFor VALUES('3', 94316, '2023-03-17', '15:00');

INSERT INTO CardInfo VALUES ('1234953', 'Debit', 'Devin', '2025-06-07');
INSERT INTO CardInfo VALUES ('10239041', 'Credit', 'Alejandro', '2024-08-10');
INSERT INTO CardInfo VALUES ('5722190', 'Credit', 'Steven', '2024-07-01');

INSERT INTO Uses VALUES('1234953', 'dz1295@nyu.edu');
INSERT INTO Uses VALUES('10239041', 'ab8041@nyu.edu');
INSERT INTO Uses VALUES('5722190', 'steven123@nyu.edu');

INSERT INTO PaymentMethod VALUES('1234953', '1');
INSERT INTO PaymentMethod VALUES('10239041', '2');
INSERT INTO PaymentMethod VALUES('5722190', '3');
