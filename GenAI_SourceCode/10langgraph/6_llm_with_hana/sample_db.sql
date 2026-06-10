-- Create HANA Column Table for Invoices
CREATE COLUMN TABLE INVOICES (
    InvoiceId NVARCHAR(36) NOT NULL,
    CustomerId NVARCHAR(20) NOT NULL,
    InvoiceDate DATE NOT NULL,
    Country NVARCHAR(50) NOT NULL,
    City NVARCHAR(50) NOT NULL,
    State NVARCHAR(50),
    Address NVARCHAR(200) NOT NULL,
    TotalAmount DECIMAL(15,2) NOT NULL,
    Currency NVARCHAR(3) NOT NULL,
    Region NVARCHAR(50) NOT NULL,
    IsPartialDelivery BOOLEAN NOT NULL,
    RefOrderNo NVARCHAR(20) NOT NULL,
    PRIMARY KEY (InvoiceId)
);


INSERT INTO INVOICES VALUES

('A1B2C3D4-E5F6-7890-ABCD-123456789002', 'CUST002', '2024-01-18', 'Germany', 'Berlin', 'Berlin', 'Unter den Linden 45', 8920.75, 'EUR', 'Europe', TRUE, 'ORD-2024-002');
INSERT INTO INVOICES VALUES
('A1B2C3D4-E5F6-7890-ABCD-123456789003', 'CUST003', '2024-01-22', 'Japan', 'Tokyo', 'Tokyo', '1-1-1 Shibuya, Shibuya-ku', 22340.00, 'JPY', 'Asia Pacific', FALSE, 'ORD-2024-003');
INSERT INTO INVOICES VALUES
('A1B2C3D4-E5F6-7890-ABCD-123456789004', 'CUST004', '2024-01-25', 'UK', 'London', 'England', '10 Downing Street', 12500.25, 'GBP', 'Europe', TRUE, 'ORD-2024-004');
INSERT INTO INVOICES VALUES
('A1B2C3D4-E5F6-7890-ABCD-123456789005', 'CUST005', '2024-02-03', 'Canada', 'Toronto', 'Ontario', '100 Queen Street West', 9875.60, 'CAD', 'North America', FALSE, 'ORD-2024-005');
INSERT INTO INVOICES VALUES
('A1B2C3D4-E5F6-7890-ABCD-123456789006', 'CUST006', '2024-02-08', 'Australia', 'Sydney', 'NSW', '200 George Street', 18230.80, 'AUD', 'Asia Pacific', TRUE, 'ORD-2024-006');
INSERT INTO INVOICES VALUES
('A1B2C3D4-E5F6-7890-ABCD-123456789007', 'CUST007', '2024-02-12', 'France', 'Paris', 'Ile-de-France', '25 Avenue des Champs-Élysées', 14560.90, 'EUR', 'Europe', FALSE, 'ORD-2024-007');
INSERT INTO INVOICES VALUES
('A1B2C3D4-E5F6-7890-ABCD-123456789008', 'CUST008', '2024-02-16', 'Brazil', 'São Paulo', 'SP', 'Rua Augusta 1000', 7890.45, 'BRL', 'South America', TRUE, 'ORD-2024-008');
INSERT INTO INVOICES VALUES
('A1B2C3D4-E5F6-7890-ABCD-123456789009', 'CUST009', '2024-02-20', 'India', 'Mumbai', 'Maharashtra', 'Nariman Point, Fort', 25670.30, 'INR', 'Asia Pacific', FALSE, 'ORD-2024-009');
INSERT INTO INVOICES VALUES
('A1B2C3D4-E5F6-7890-ABCD-123456789010', 'CUST010', '2024-02-24', 'China', 'Shanghai', 'Shanghai', '88 Century Avenue, Pudong', 16780.20, 'CNY', 'Asia Pacific', TRUE, 'ORD-2024-010');
INSERT INTO INVOICES VALUES
('A1B2C3D4-E5F6-7890-ABCD-123456789011', 'CUST011', '2024-03-01', 'USA', 'Los Angeles', 'CA', '1234 Hollywood Blvd', 11250.75, 'USD', 'North America', FALSE, 'ORD-2024-011');
INSERT INTO INVOICES VALUES
('A1B2C3D4-E5F6-7890-ABCD-123456789012', 'CUST012', '2024-03-05', 'Italy', 'Milan', 'Lombardy', 'Via Montenapoleone 10', 9876.40, 'EUR', 'Europe', TRUE, 'ORD-2024-012');
INSERT INTO INVOICES VALUES
('A1B2C3D4-E5F6-7890-ABCD-123456789013', 'CUST013', '2024-03-09', 'South Korea', 'Seoul', 'Seoul', '123 Gangnam-daero', 19450.65, 'KRW', 'Asia Pacific', FALSE, 'ORD-2024-013');
INSERT INTO INVOICES VALUES
('A1B2C3D4-E5F6-7890-ABCD-123456789014', 'CUST014', '2024-03-13', 'Mexico', 'Mexico City', 'CDMX', 'Paseo de la Reforma 500', 13240.90, 'MXN', 'North America', TRUE, 'ORD-2024-014');
INSERT INTO INVOICES VALUES
('A1B2C3D4-E5F6-7890-ABCD-123456789015', 'CUST015', '2024-03-17', 'Netherlands', 'Amsterdam', 'North Holland', 'Prinsengracht 263', 8760.15, 'EUR', 'Europe', FALSE, 'ORD-2024-015');
INSERT INTO INVOICES VALUES
('A1B2C3D4-E5F6-7890-ABCD-123456789016', 'CUST016', '2024-03-21', 'Singapore', 'Singapore', 'Singapore', '1 Marina Bay Sands', 21890.85, 'SGD', 'Asia Pacific', TRUE, 'ORD-2024-016');
INSERT INTO INVOICES VALUES
('A1B2C3D4-E5F6-7890-ABCD-123456789017', 'CUST017', '2024-03-25', 'Switzerland', 'Zurich', 'Zurich', 'Bahnhofstrasse 50', 17320.50, 'CHF', 'Europe', FALSE, 'ORD-2024-017');
INSERT INTO INVOICES VALUES
('A1B2C3D4-E5F6-7890-ABCD-123456789018', 'CUST018', '2024-03-29', 'UAE', 'Dubai', 'Dubai', 'Sheikh Zayed Road 100', 24560.70, 'AED', 'Middle East', TRUE, 'ORD-2024-018');

-- Insert 80 sample records with variety
INSERT INTO INVOICES VALUES
('A1B2C3D4-E5F6-7890-ABCD-123456789001', 'CUST001', '2024-01-15', 'USA', 'New York', 'NY', '123 Broadway St, Suite 100', 15750.50, 'USD', 'North America', FALSE, 'ORD-2024-001'),
('A1B2C3D4-E5F6-7890-ABCD-123456789002', 'CUST002', '2024-01-18', 'Germany', 'Berlin', 'Berlin', 'Unter den Linden 45', 8920.75, 'EUR', 'Europe', TRUE, 'ORD-2024-002'),
('A1B2C3D4-E5F6-7890-ABCD-123456789003', 'CUST003', '2024-01-22', 'Japan', 'Tokyo', 'Tokyo', '1-1-1 Shibuya, Shibuya-ku', 22340.00, 'JPY', 'Asia Pacific', FALSE, 'ORD-2024-003'),
('A1B2C3D4-E5F6-7890-ABCD-123456789004', 'CUST004', '2024-01-25', 'UK', 'London', 'England', '10 Downing Street', 12500.25, 'GBP', 'Europe', TRUE, 'ORD-2024-004'),
('A1B2C3D4-E5F6-7890-ABCD-123456789005', 'CUST005', '2024-02-03', 'Canada', 'Toronto', 'Ontario', '100 Queen Street West', 9875.60, 'CAD', 'North America', FALSE, 'ORD-2024-005'),
('A1B2C3D4-E5F6-7890-ABCD-123456789006', 'CUST006', '2024-02-08', 'Australia', 'Sydney', 'NSW', '200 George Street', 18230.80, 'AUD', 'Asia Pacific', TRUE, 'ORD-2024-006'),
('A1B2C3D4-E5F6-7890-ABCD-123456789007', 'CUST007', '2024-02-12', 'France', 'Paris', 'Ile-de-France', '25 Avenue des Champs-Élysées', 14560.90, 'EUR', 'Europe', FALSE, 'ORD-2024-007'),
('A1B2C3D4-E5F6-7890-ABCD-123456789008', 'CUST008', '2024-02-16', 'Brazil', 'São Paulo', 'SP', 'Rua Augusta 1000', 7890.45, 'BRL', 'South America', TRUE, 'ORD-2024-008'),
('A1B2C3D4-E5F6-7890-ABCD-123456789009', 'CUST009', '2024-02-20', 'India', 'Mumbai', 'Maharashtra', 'Nariman Point, Fort', 25670.30, 'INR', 'Asia Pacific', FALSE, 'ORD-2024-009'),
('A1B2C3D4-E5F6-7890-ABCD-123456789010', 'CUST010', '2024-02-24', 'China', 'Shanghai', 'Shanghai', '88 Century Avenue, Pudong', 16780.20, 'CNY', 'Asia Pacific', TRUE, 'ORD-2024-010'),
('A1B2C3D4-E5F6-7890-ABCD-123456789011', 'CUST011', '2024-03-01', 'USA', 'Los Angeles', 'CA', '1234 Hollywood Blvd', 11250.75, 'USD', 'North America', FALSE, 'ORD-2024-011'),
('A1B2C3D4-E5F6-7890-ABCD-123456789012', 'CUST012', '2024-03-05', 'Italy', 'Milan', 'Lombardy', 'Via Montenapoleone 10', 9876.40, 'EUR', 'Europe', TRUE, 'ORD-2024-012'),
('A1B2C3D4-E5F6-7890-ABCD-123456789013', 'CUST013', '2024-03-09', 'South Korea', 'Seoul', 'Seoul', '123 Gangnam-daero', 19450.65, 'KRW', 'Asia Pacific', FALSE, 'ORD-2024-013'),
('A1B2C3D4-E5F6-7890-ABCD-123456789014', 'CUST014', '2024-03-13', 'Mexico', 'Mexico City', 'CDMX', 'Paseo de la Reforma 500', 13240.90, 'MXN', 'North America', TRUE, 'ORD-2024-014'),
('A1B2C3D4-E5F6-7890-ABCD-123456789015', 'CUST015', '2024-03-17', 'Netherlands', 'Amsterdam', 'North Holland', 'Prinsengracht 263', 8760.15, 'EUR', 'Europe', FALSE, 'ORD-2024-015'),
('A1B2C3D4-E5F6-7890-ABCD-123456789016', 'CUST016', '2024-03-21', 'Singapore', 'Singapore', 'Singapore', '1 Marina Bay Sands', 21890.85, 'SGD', 'Asia Pacific', TRUE, 'ORD-2024-016'),
('A1B2C3D4-E5F6-7890-ABCD-123456789017', 'CUST017', '2024-03-25', 'Switzerland', 'Zurich', 'Zurich', 'Bahnhofstrasse 50', 17320.50, 'CHF', 'Europe', FALSE, 'ORD-2024-017'),
('A1B2C3D4-E5F6-7890-ABCD-123456789018', 'CUST018', '2024-03-29', 'UAE', 'Dubai', 'Dubai', 'Sheikh Zayed Road 100', 24560.70, 'AED', 'Middle East', TRUE, 'ORD-2024-018'),
('A1B2C3D4-E5F6-7890-ABCD-123456789019', 'CUST019', '2024-04-02', 'Spain', 'Madrid', 'Madrid', 'Gran Vía 28', 10430.25, 'EUR', 'Europe', FALSE, 'ORD-2024-019'),
('A1B2C3D4-E5F6-7890-ABCD-123456789020', 'CUST020', '2024-04-06', 'Russia', 'Moscow', 'Moscow', 'Red Square 1', 15680.90, 'RUB', 'Europe', TRUE, 'ORD-2024-020'),
('A1B2C3D4-E5F6-7890-ABCD-123456789021', 'CUST021', '2024-04-10', 'USA', 'Chicago', 'IL', '233 S Wacker Dr', 12890.45, 'USD', 'North America', FALSE, 'ORD-2024-021'),
('A1B2C3D4-E5F6-7890-ABCD-123456789022', 'CUST022', '2024-04-14', 'Sweden', 'Stockholm', 'Stockholm', 'Drottninggatan 71A', 9340.80, 'SEK', 'Europe', TRUE, 'ORD-2024-022'),
('A1B2C3D4-E5F6-7890-ABCD-123456789023', 'CUST023', '2024-04-18', 'Norway', 'Oslo', 'Oslo', 'Karl Johans gate 14', 16750.35, 'NOK', 'Europe', FALSE, 'ORD-2024-023'),
('A1B2C3D4-E5F6-7890-ABCD-123456789024', 'CUST024', '2024-04-22', 'Argentina', 'Buenos Aires', 'Buenos Aires', 'Avenida Corrientes 1234', 8920.60, 'ARS', 'South America', TRUE, 'ORD-2024-024'),
('A1B2C3D4-E5F6-7890-ABCD-123456789025', 'CUST025', '2024-04-26', 'South Africa', 'Cape Town', 'Western Cape', '123 Long Street', 11540.75, 'ZAR', 'Africa', FALSE, 'ORD-2024-025'),
('A1B2C3D4-E5F6-7890-ABCD-123456789026', 'CUST026', '2024-04-30', 'Thailand', 'Bangkok', 'Bangkok', '999 Rama IV Road', 18670.20, 'THB', 'Asia Pacific', TRUE, 'ORD-2024-026'),
('A1B2C3D4-E5F6-7890-ABCD-123456789027', 'CUST027', '2024-05-04', 'Turkey', 'Istanbul', 'Istanbul', 'Istiklal Caddesi 145', 14230.85, 'TRY', 'Middle East', FALSE, 'ORD-2024-027'),
('A1B2C3D4-E5F6-7890-ABCD-123456789028', 'CUST028', '2024-05-08', 'Poland', 'Warsaw', 'Mazovia', 'Nowy Świat 64', 7845.50, 'PLN', 'Europe', TRUE, 'ORD-2024-028'),
('A1B2C3D4-E5F6-7890-ABCD-123456789029', 'CUST029', '2024-05-12', 'Chile', 'Santiago', 'Santiago', 'Avenida Providencia 1208', 13560.95, 'CLP', 'South America', FALSE, 'ORD-2024-029'),
('A1B2C3D4-E5F6-7890-ABCD-123456789030', 'CUST030', '2024-05-16', 'New Zealand', 'Auckland', 'Auckland', '1 Queen Street', 20340.40, 'NZD', 'Asia Pacific', TRUE, 'ORD-2024-030'),
('A1B2C3D4-E5F6-7890-ABCD-123456789031', 'CUST031', '2024-05-20', 'Belgium', 'Brussels', 'Brussels', 'Avenue Louise 149', 9780.65, 'EUR', 'Europe', FALSE, 'ORD-2024-031'),
('A1B2C3D4-E5F6-7890-ABCD-123456789032', 'CUST032', '2024-05-24', 'Austria', 'Vienna', 'Vienna', 'Kärtner Straße 51', 16890.30, 'EUR', 'Europe', TRUE, 'ORD-2024-032'),
('A1B2C3D4-E5F6-7890-ABCD-123456789033', 'CUST033', '2024-05-28', 'Denmark', 'Copenhagen', 'Capital', 'Strøget 20', 12450.75, 'DKK', 'Europe', FALSE, 'ORD-2024-033'),
('A1B2C3D4-E5F6-7890-ABCD-123456789034', 'CUST034', '2024-06-01', 'Finland', 'Helsinki', 'Uusimaa', 'Mannerheimintie 103', 8765.20, 'EUR', 'Europe', TRUE, 'ORD-2024-034'),
('A1B2C3D4-E5F6-7890-ABCD-123456789035', 'CUST035', '2024-06-05', 'Israel', 'Tel Aviv', 'Tel Aviv', 'Rothschild Boulevard 1', 19890.85, 'ILS', 'Middle East', FALSE, 'ORD-2024-035'),
('A1B2C3D4-E5F6-7890-ABCD-123456789036', 'CUST036', '2024-06-09', 'Portugal', 'Lisbon', 'Lisbon', 'Rua Augusta 100', 11230.50, 'EUR', 'Europe', TRUE, 'ORD-2024-036'),
('A1B2C3D4-E5F6-7890-ABCD-123456789037', 'CUST037', '2024-06-13', 'Greece', 'Athens', 'Attica', 'Ermou 120', 7650.90, 'EUR', 'Europe', FALSE, 'ORD-2024-037'),
('A1B2C3D4-E5F6-7890-ABCD-123456789038', 'CUST038', '2024-06-17', 'Czech Republic', 'Prague', 'Prague', 'Wenceslas Square 25', 15670.45, 'CZK', 'Europe', TRUE, 'ORD-2024-038'),
('A1B2C3D4-E5F6-7890-ABCD-123456789039', 'CUST039', '2024-06-21', 'Hungary', 'Budapest', 'Budapest', 'Váci utca 13', 9340.60, 'HUF', 'Europe', FALSE, 'ORD-2024-039'),
('A1B2C3D4-E5F6-7890-ABCD-123456789040', 'CUST040', '2024-06-25', 'Ireland', 'Dublin', 'Dublin', 'Grafton Street 78', 13840.75, 'EUR', 'Europe', TRUE, 'ORD-2024-040'),
('A1B2C3D4-E5F6-7890-ABCD-123456789041', 'CUST041', '2024-06-29', 'USA', 'Miami', 'FL', '200 Biscayne Blvd', 18450.20, 'USD', 'North America', FALSE, 'ORD-2024-041'),
('A1B2C3D4-E5F6-7890-ABCD-123456789042', 'CUST042', '2024-07-03', 'Malaysia', 'Kuala Lumpur', 'Kuala Lumpur', 'Jalan Bukit Bintang 55', 22340.85, 'MYR', 'Asia Pacific', TRUE, 'ORD-2024-042'),
('A1B2C3D4-E5F6-7890-ABCD-123456789043', 'CUST043', '2024-07-07', 'Philippines', 'Manila', 'Metro Manila', 'Ayala Avenue 6750', 16780.50, 'PHP', 'Asia Pacific', FALSE, 'ORD-2024-043'),
('A1B2C3D4-E5F6-7890-ABCD-123456789044', 'CUST044', '2024-07-11', 'Indonesia', 'Jakarta', 'Jakarta', 'Jl. Sudirman Kav 52-53', 14290.90, 'IDR', 'Asia Pacific', TRUE, 'ORD-2024-044'),
('A1B2C3D4-E5F6-7890-ABCD-123456789045', 'CUST045', '2024-07-15', 'Vietnam', 'Ho Chi Minh City', 'Ho Chi Minh', 'Dong Khoi Street 115', 8950.45, 'VND', 'Asia Pacific', FALSE, 'ORD-2024-045'),
('A1B2C3D4-E5F6-7890-ABCD-123456789046', 'CUST046', '2024-07-19', 'Egypt', 'Cairo', 'Cairo', 'Tahrir Square 10', 12670.60, 'EGP', 'Africa', TRUE, 'ORD-2024-046'),
('A1B2C3D4-E5F6-7890-ABCD-123456789047', 'CUST047', '2024-07-23', 'Saudi Arabia', 'Riyadh', 'Riyadh', 'King Fahd Road 7777', 21890.75, 'SAR', 'Middle East', FALSE, 'ORD-2024-047'),
('A1B2C3D4-E5F6-7890-ABCD-123456789048', 'CUST048', '2024-07-27', 'Kuwait', 'Kuwait City', 'Al Asimah', 'Arabian Gulf Street 25', 19540.20, 'KWD', 'Middle East', TRUE, 'ORD-2024-048'),
('A1B2C3D4-E5F6-7890-ABCD-123456789049', 'CUST049', '2024-07-31', 'Qatar', 'Doha', 'Doha', 'Corniche Road 100', 25670.85, 'QAR', 'Middle East', FALSE, 'ORD-2024-049'),
('A1B2C3D4-E5F6-7890-ABCD-123456789050', 'CUST050', '2024-08-04', 'USA', 'Seattle', 'WA', '400 Broad Street', 17320.50, 'USD', 'North America', TRUE, 'ORD-2024-050'),
('A1B2C3D4-E5F6-7890-ABCD-123456789051', 'CUST051', '2024-08-08', 'Colombia', 'Bogotá', 'Cundinamarca', 'Carrera 7 # 72-41', 10890.90, 'COP', 'South America', FALSE, 'ORD-2024-051'),
('A1B2C3D4-E5F6-7890-ABCD-123456789052', 'CUST052', '2024-08-12', 'Peru', 'Lima', 'Lima', 'Av. Javier Prado Este 4200', 13450.45, 'PEN', 'South America', TRUE, 'ORD-2024-052'),
('A1B2C3D4-E5F6-7890-ABCD-123456789053', 'CUST053', '2024-08-16', 'Venezuela', 'Caracas', 'Capital District', 'Avenida Francisco de Miranda', 7890.60, 'VES', 'South America', FALSE, 'ORD-2024-053'),
('A1B2C3D4-E5F6-7890-ABCD-123456789054', 'CUST054', '2024-08-20', 'Ecuador', 'Quito', 'Pichincha', 'Av. Amazonas 4545', 9670.75, 'USD', 'South America', TRUE, 'ORD-2024-054'),
('A1B2C3D4-E5F6-7890-ABCD-123456789055', 'CUST055', '2024-08-24', 'Uruguay', 'Montevideo', 'Montevideo', '18 de Julio 1360', 11230.20, 'UYU', 'South America', FALSE, 'ORD-2024-055'),
('A1B2C3D4-E5F6-7890-ABCD-123456789056', 'CUST056', '2024-08-28', 'Nigeria', 'Lagos', 'Lagos', 'Victoria Island 101241', 15680.85, 'NGN', 'Africa', TRUE, 'ORD-2024-056'),
('A1B2C3D4-E5F6-7890-ABCD-123456789057', 'CUST057', '2024-09-01', 'Kenya', 'Nairobi', 'Nairobi', 'Uhuru Highway 20', 8950.50, 'KES', 'Africa', FALSE, 'ORD-2024-057'),
('A1B2C3D4-E5F6-7890-ABCD-123456789058', 'CUST058', '2024-09-05', 'Ghana', 'Accra', 'Greater Accra', 'Independence Avenue 37', 12340.90, 'GHS', 'Africa', TRUE, 'ORD-2024-058'),
('A1B2C3D4-E5F6-7890-ABCD-123456789059', 'CUST059', '2024-09-09', 'Morocco', 'Casablanca', 'Casablanca-Settat', 'Boulevard Mohammed V 200', 14560.45, 'MAD', 'Africa', FALSE, 'ORD-2024-059'),
('A1B2C3D4-E5F6-7890-ABCD-123456789060', 'CUST060', '2024-09-13', 'Tunisia', 'Tunis', 'Tunis', 'Avenue Habib Bourguiba 150', 6780.60, 'TND', 'Africa', TRUE, 'ORD-2024-060'),
('A1B2C3D4-E5F6-7890-ABCD-123456789061', 'CUST061', '2024-09-17', 'USA', 'Boston', 'MA', '1 Boston Place', 19870.75, 'USD', 'North America', FALSE, 'ORD-2024-061'),
('A1B2C3D4-E5F6-7890-ABCD-123456789062', 'CUST062', '2024-09-21', 'Bangladesh', 'Dhaka', 'Dhaka', 'Motijheel Commercial Area', 23450.20, 'BDT', 'Asia Pacific', TRUE, 'ORD-2024-062'),
('A1B2C3D4-E5F6-7890-ABCD-123456789063', 'CUST063', '2024-09-25', 'Pakistan', 'Karachi', 'Sindh', 'Shahrah-e-Faisal 75350', 16890.85, 'PKR', 'Asia Pacific', FALSE, 'ORD-2024-063'),
('A1B2C3D4-E5F6-7890-ABCD-123456789064', 'CUST064', '2024-09-29', 'Sri Lanka', 'Colombo', 'Western Province', 'Galle Road 106', 11230.50, 'LKR', 'Asia Pacific', TRUE, 'ORD-2024-064'),
('A1B2C3D4-E5F6-7890-ABCD-123456789065', 'CUST065', '2024-10-03', 'Nepal', 'Kathmandu', 'Bagmati', 'Durbar Marg 44600', 8950.90, 'NPR', 'Asia Pacific', FALSE, 'ORD-2024-065'),
('A1B2C3D4-E5F6-7890-ABCD-123456789066', 'CUST066', '2024-10-07', 'Cambodia', 'Phnom Penh', 'Phnom Penh', 'Riverside Boulevard 12206', 14670.45, 'KHR', 'Asia Pacific', TRUE, 'ORD-2024-066'),
('A1B2C3D4-E5F6-7890-ABCD-123456789067', 'CUST067', '2024-10-11', 'Laos', 'Vientiane', 'Vientiane', 'Lane Xang Avenue 01000', 7890.60, 'LAK', 'Asia Pacific', FALSE, 'ORD-2024-067'),
('A1B2C3D4-E5F6-7890-ABCD-123456789068', 'CUST068', '2024-10-15', 'Myanmar', 'Yangon', 'Yangon', 'Strand Road 11181', 12340.75, 'MMK', 'Asia Pacific', TRUE, 'ORD-2024-068'),
('A1B2C3D4-E5F6-7890-ABCD-123456789069', 'CUST069', '2024-10-19', 'USA', 'San Francisco', 'CA', '101 California Street', 22890.20, 'USD', 'North America', FALSE, 'ORD-2024-069'),
('A1B2C3D4-E5F6-7890-ABCD-123456789070', 'CUST070', '2024-10-23', 'Luxembourg', 'Luxembourg City', 'Luxembourg', 'Place Guillaume II 2', 18670.85, 'EUR', 'Europe', TRUE, 'ORD-2024-070'),
('A1B2C3D4-E5F6-7890-ABCD-123456789071', 'CUST071', '2024-10-27', 'Slovenia', 'Ljubljana', 'Ljubljana', 'Trubarjeva cesta 50', 9450.50, 'EUR', 'Europe', FALSE, 'ORD-2024-071'),
('A1B2C3D4-E5F6-7890-ABCD-123456789072', 'CUST072', '2024-10-31', 'Croatia', 'Zagreb', 'Zagreb', 'Ilica 14', 13780.90, 'EUR', 'Europe', TRUE, 'ORD-2024-072'),
('A1B2C3D4-E5F6-7890-ABCD-123456789073', 'CUST073', '2024-11-04', 'Slovakia', 'Bratislava', 'Bratislava', 'Hlavné námestie 1', 8340.45, 'EUR', 'Europe', FALSE, 'ORD-2024-073'),
('A1B2C3D4-E5F6-7890-ABCD-123456789074', 'CUST074', '2024-11-08', 'Estonia', 'Tallinn', 'Harju', 'Viru väljak 4', 16890.60, 'EUR', 'Europe', TRUE, 'ORD-2024-074'),
('A1B2C3D4-E5F6-7890-ABCD-123456789075', 'CUST075', '2024-11-12', 'Latvia', 'Riga', 'Riga', 'Brīvības iela 36', 11230.75, 'EUR', 'Europe', FALSE, 'ORD-2024-075'),
('A1B2C3D4-E5F6-7890-ABCD-123456789076', 'CUST076', '2024-11-16', 'Lithuania', 'Vilnius', 'Vilnius', 'Gedimino prospektas 9', 14560.20, 'EUR', 'Europe', TRUE, 'ORD-2024-076'),
('A1B2C3D4-E5F6-7890-ABCD-123456789077', 'CUST077', '2024-11-20', 'Malta', 'Valletta', 'Malta', 'Republic Street 123', 7890.85, 'EUR', 'Europe', FALSE, 'ORD-2024-077'),
('A1B2C3D4-E5F6-7890-ABCD-123456789078', 'CUST078', '2024-11-24', 'Cyprus', 'Nicosia', 'Nicosia', 'Makarios Avenue 230', 19670.50, 'EUR', 'Europe', TRUE, 'ORD-2024-078'),
('A1B2C3D4-E5F6-7890-ABCD-123456789079', 'CUST079', '2024-11-28', 'USA', 'Denver', 'CO', '1700 Broadway', 15340.90, 'USD', 'North America', FALSE, 'ORD-2024-079'),
('A1B2C3D4-E5F6-7890-ABCD-123456789080', 'CUST080', '2024-12-02', 'Iceland', 'Reykjavik', 'Capital Region', 'Laugavegur 26', 12890.45, 'ISK', 'Europe', TRUE, 'ORD-2024-080');