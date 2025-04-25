-- Author table
CREATE TABLE IF NOT EXISTS `author` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `first_name` VARCHAR(50),
  `last_name` VARCHAR(50),
  `patronymic` VARCHAR(50),
  `birth_year` VARCHAR(10),
  `country` VARCHAR(45)
);

-- Genre table
CREATE TABLE IF NOT EXISTS `genre` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `genre_type` VARCHAR(45),
  `name` VARCHAR(45)
);

-- Book table
CREATE TABLE IF NOT EXISTS `book` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` VARCHAR(250),
  `year` VARCHAR(10),
  `quantity` INTEGER,
  `price` REAL,
  `author_id` INTEGER NOT NULL,
  `genre_id` INTEGER NOT NULL,
  `publishing_house` VARCHAR(100),
  FOREIGN KEY (`author_id`) REFERENCES `author` (`id`),
  FOREIGN KEY (`genre_id`) REFERENCES `genre` (`id`)
);

-- Debiting act table
CREATE TABLE IF NOT EXISTS `debiting_act` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `date` TIMESTAMP,
  `quantity` INTEGER,
  `commentary` VARCHAR(250),
  `book_id` INTEGER NOT NULL,
  FOREIGN KEY (`book_id`) REFERENCES `book` (`id`)
);

-- Employee table
CREATE TABLE IF NOT EXISTS `employee` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `first_name` VARCHAR(50),
  `last_name` VARCHAR(50),
  `patronymic` VARCHAR(50),
  `position` VARCHAR(50)
);

-- Order request table
CREATE TABLE IF NOT EXISTS `order_request` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `date` TIMESTAMP,
  `quantity` INTEGER,
  `book_id` INTEGER NOT NULL,
  `employee_id` INTEGER NOT NULL,
  FOREIGN KEY (`book_id`) REFERENCES `book` (`id`),
  FOREIGN KEY (`employee_id`) REFERENCES `employee` (`id`)
);

-- Supplier table
CREATE TABLE IF NOT EXISTS `supplier` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` VARCHAR(250),
  `contact` VARCHAR(250),
  `contact_person` VARCHAR(250)
);

-- Lading bill table
CREATE TABLE IF NOT EXISTS `lading_bill` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `date` TIMESTAMP,
  `book_id` INTEGER NOT NULL,
  `order_request_id` INTEGER NOT NULL,
  `supplier_id` INTEGER NOT NULL,
  FOREIGN KEY (`book_id`) REFERENCES `book` (`id`),
  FOREIGN KEY (`order_request_id`) REFERENCES `order_request` (`id`),
  FOREIGN KEY (`supplier_id`) REFERENCES `supplier` (`id`)
);

-- Reader table
CREATE TABLE IF NOT EXISTS `reader` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `first_name` VARCHAR(50),
  `last_name` VARCHAR(50),
  `patronymic` VARCHAR(50),
  `date_birth` TIMESTAMP,
  `contact` VARCHAR(250)
);

-- Given book table
CREATE TABLE IF NOT EXISTS `given_book` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `quantity` VARCHAR(50),
  `given_date` TIMESTAMP,
  `return_date` TIMESTAMP,
  `return_date_fact` TIMESTAMP,
  `reader_id` INTEGER NOT NULL,
  `employee_id` INTEGER NOT NULL,
  `book_id` INTEGER NOT NULL,
  FOREIGN KEY (`reader_id`) REFERENCES `reader` (`id`),
  FOREIGN KEY (`employee_id`) REFERENCES `employee` (`id`),
  FOREIGN KEY (`book_id`) REFERENCES `book` (`id`)
);

