-- Sample Data for Testing

-- Insert Users
INSERT INTO Users (name, email) VALUES
('Alice Johnson', 'alice@example.com'),
('Bob Smith', 'bob@example.com'),
('Charlie Brown', 'charlie@example.com');

-- Insert Hotels
INSERT INTO Hotels (name, city) VALUES
('Grand Hotel', 'New York'),
('Ocean View Resort', 'Miami'),
('Mountain Lodge', 'Denver'),
('City Center Inn', 'New York');

-- Insert Bookings
INSERT INTO Bookings (user_id, hotel_id, date) VALUES
(1, 1, '2025-12-15'),
(1, 2, '2025-12-20'),
(2, 1, '2025-12-16'),
(3, 3, '2025-12-18');
