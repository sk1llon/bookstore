CREATE DATABASE IF NOT EXISTS bookstore CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bookstore;

DROP TABLE IF EXISTS OrderItems;
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS Books;
DROP TABLE IF EXISTS Publishers;
DROP TABLE IF EXISTS Authors;
DROP TABLE IF EXISTS Genres;
DROP TABLE IF EXISTS Users;

CREATE TABLE Users (
    UserID INT PRIMARY KEY AUTO_INCREMENT,
    Login VARCHAR(50) NOT NULL UNIQUE,
    Password VARCHAR(255) NOT NULL,
    Role ENUM('client', 'manager', 'admin') NOT NULL,
    FIO VARCHAR(150) NOT NULL
);

CREATE TABLE Genres (
    GenreID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL
);

CREATE TABLE Authors (
    AuthorID INT PRIMARY KEY AUTO_INCREMENT,
    FullName VARCHAR(150) NOT NULL
);

CREATE TABLE Publishers (
    PublisherID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL
);

CREATE TABLE Books (
    BookID INT PRIMARY KEY AUTO_INCREMENT,
    Title VARCHAR(255) NOT NULL,
    GenreID INT NOT NULL,
    Description TEXT,
    AuthorID INT NOT NULL,
    PublisherID INT NOT NULL,
    Price DECIMAL(10, 2) NOT NULL,
    Year INT,
    StockQuantity INT NOT NULL DEFAULT 0,
    Discount INT DEFAULT 0,
    CoverPath VARCHAR(255),
    FOREIGN KEY (GenreID) REFERENCES Genres(GenreID),
    FOREIGN KEY (AuthorID) REFERENCES Authors(AuthorID),
    FOREIGN KEY (PublisherID) REFERENCES Publishers(PublisherID)
);

CREATE TABLE Orders (
    OrderID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT NOT NULL,
    Status VARCHAR(50) NOT NULL,
    DeliveryAddress VARCHAR(255),
    OrderDate DATE NOT NULL,
    IssueDate DATE,
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

CREATE TABLE OrderItems (
    ItemID INT PRIMARY KEY AUTO_INCREMENT,
    OrderID INT NOT NULL,
    BookID INT NOT NULL,
    Quantity INT NOT NULL DEFAULT 1,
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID) ON DELETE CASCADE,
    FOREIGN KEY (BookID) REFERENCES Books(BookID)
);

INSERT INTO Users (UserID, Login, Password, Role, FIO) VALUES
(1, 'reader1', '123456', 'client', 'Иванов Иван Иванович'),
(2, 'booklover', 'qwerty', 'client', 'Петрова Анна Сергеевна'),
(3, 'manager', 'manager', 'manager', 'Сидоров Пётр Алексеевич'),
(4, 'admin', 'admin', 'admin', 'Васильева Ольга Дмитриевна');

INSERT INTO Genres (GenreID, Name) VALUES
(1, 'Фантастика'),
(2, 'Детектив'),
(3, 'Классика'),
(4, 'Научно-популярная'),
(5, 'Фэнтези');

INSERT INTO Authors (AuthorID, FullName) VALUES
(1, 'Дж. Р. Р. Толкин'),
(2, 'Агата Кристи'),
(3, 'Ф. М. Достоевский'),
(4, 'Ю Несбё'),
(5, 'Стивен Кинг');

INSERT INTO Publishers (PublisherID, Name) VALUES
(1, 'Эксмо'),
(2, 'АСТ'),
(3, 'Азбука'),
(4, 'Corpus'),
(5, 'Фантом Пресс');

INSERT INTO Books (BookID, Title, GenreID, Description, AuthorID, PublisherID, Price, Year, StockQuantity, Discount, CoverPath) VALUES
(1, 'Властелин колец: Братство кольца', 1, 'Первая книга трилогии', 1, 1, 890.00, 2023, 45, 5, 'covers/lotr1.jpg'),
(2, 'Убийство в «Восточном экспрессе»', 2, 'Классический детектив', 2, 2, 650.00, 2024, 0, 20, 'covers/orient.jpg'),
(3, 'Преступление и наказание', 3, 'Философский роман', 3, 3, 780.00, 2022, 18, 0, 'covers/crime.jpg'),
(4, 'Снеговик', 2, 'Норвежский триллер', 4, 4, 720.00, 2025, 9, 12, 'covers/snowman.jpg'),
(5, 'Оно', 5, 'Ужасы', 5, 5, 950.00, 2023, 32, 15, 'covers/it.jpg'),
(6, 'Хоббит', 1, 'Предыстория Властелина колец', 1, 1, 590.00, 2024, 67, 8, 'covers/hobbit.jpg');

INSERT INTO Orders (OrderID, UserID, Status, DeliveryAddress, OrderDate, IssueDate) VALUES
(1, 1, 'Новый', 'Москва, ул. Тверская, д. 12', '2026-02-28', NULL),
(2, 2, 'Выдан', 'СПб, Невский пр., д. 56', '2026-02-15', '2026-02-20'),
(3, 1, 'В обработке', 'Москва, Ленинградский пр., д. 41', '2026-03-02', NULL);

INSERT INTO OrderItems (ItemID, OrderID, BookID, Quantity) VALUES
(1, 1, 1, 1),
(2, 1, 5, 1),
(3, 2, 3, 2),
(4, 3, 4, 1),
(5, 3, 6, 1);
