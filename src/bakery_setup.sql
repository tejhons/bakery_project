CREATE DATABASE IF NOT EXISTS bakery;
USE bakery;

-- ---------------------------------------------------------------------------
-- Products
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Category (
    Category_ID   INT PRIMARY KEY,
    Item_ID       INT                      -- kept from your spreadsheet (no FK: Item already points at Category)
);

CREATE TABLE IF NOT EXISTS Item (
    Item_ID       INT PRIMARY KEY,
    Category_ID   INT NOT NULL,
    Item_name     VARCHAR(100) NOT NULL,
    Item_recipe   VARCHAR(100),
    FOREIGN KEY (Category_ID) REFERENCES Category(Category_ID)
);

CREATE TABLE IF NOT EXISTS Menu (
    Item_ID       INT PRIMARY KEY,
    Category_ID   INT NOT NULL,
    Item_name     VARCHAR(100) NOT NULL,
    Price         DECIMAL(6,2) NOT NULL,
    Exp_Date      DATE,
    Category_Name VARCHAR(50),
    FOREIGN KEY (Item_ID) REFERENCES Item(Item_ID)
);

CREATE TABLE IF NOT EXISTS Inventory (
    Item_ID         INT PRIMARY KEY,
    Category_ID     INT NOT NULL,
    Ingredients_ID  INT,
    Date_Time       DATETIME NULL,
    Price           DECIMAL(6,2),
    Quantity        INT NOT NULL DEFAULT 0,
    FOREIGN KEY (Item_ID) REFERENCES Item(Item_ID)
);

CREATE TABLE IF NOT EXISTS Price_Projection (
    Item_ID   INT PRIMARY KEY,
    Cost      DECIMAL(6,2),
    Price     DECIMAL(6,2),
    Profit    DECIMAL(6,2),
    FOREIGN KEY (Item_ID) REFERENCES Item(Item_ID)
);

-- ---------------------------------------------------------------------------
-- People
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Employee (
    Emp_ID     INT PRIMARY KEY,
    Job_title  VARCHAR(50),
    Hire_date  DATE
);

CREATE TABLE IF NOT EXISTS Login (
    Employee_ID  INT PRIMARY KEY,
    Pwd          VARCHAR(100) NOT NULL,
    FOREIGN KEY (Employee_ID) REFERENCES Employee(Emp_ID)
);

CREATE TABLE IF NOT EXISTS Rewards (
    Customer_ID         INT PRIMARY KEY,
    Tier_ID             INT,
    Tier_type           VARCHAR(20),
    Customer_pn         VARCHAR(15),
    Customer_firstname  VARCHAR(50),
    Customer_lastname   VARCHAR(50),
    Customer_email      VARCHAR(100) NULL
);

-- ---------------------------------------------------------------------------
-- Sales
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Invoice (
    Payment_ID      INT PRIMARY KEY,
    Payment_Method  VARCHAR(20),
    Payment_Status  VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS `Transaction` (
    Transaction_ID     INT PRIMARY KEY,
    Order_ID           INT NOT NULL,
    Reciept_ID         INT,                -- (sic) spelling matches your spreadsheet and app.py
    Employee_ID        INT NOT NULL,
    Customer_ID        INT NOT NULL,
    Payment_ID         INT NOT NULL,
    Payment_Method     VARCHAR(20),
    Payment_Status     VARCHAR(20),
    Transaction_Total  DECIMAL(8,2),
    T_Time             VARCHAR(10),        -- text like '7:15am', same as the spreadsheet
    FOREIGN KEY (Employee_ID) REFERENCES Employee(Emp_ID),
    FOREIGN KEY (Customer_ID) REFERENCES Rewards(Customer_ID),
    FOREIGN KEY (Payment_ID)  REFERENCES Invoice(Payment_ID)
);

CREATE TABLE IF NOT EXISTS Transaction_Order (
    Transaction_ID  INT NOT NULL,
    Item_ID         INT NOT NULL,
    Order_ID        INT NOT NULL,
    Price           DECIMAL(6,2) NOT NULL,
    Quantity        INT NOT NULL,
    PRIMARY KEY (Transaction_ID, Item_ID),
    FOREIGN KEY (Transaction_ID) REFERENCES `Transaction`(Transaction_ID),
    FOREIGN KEY (Item_ID)        REFERENCES Item(Item_ID)
);


-- ---------------------------------------------------------------------------
-- Data (loaded parents-first so foreign keys are satisfied)
-- ---------------------------------------------------------------------------
SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE `Price_Projection`;
TRUNCATE TABLE `Transaction_Order`;
TRUNCATE TABLE `Transaction`;
TRUNCATE TABLE `Invoice`;
TRUNCATE TABLE `Rewards`;
TRUNCATE TABLE `Inventory`;
TRUNCATE TABLE `Menu`;
TRUNCATE TABLE `Login`;
TRUNCATE TABLE `Employee`;
TRUNCATE TABLE `Item`;
TRUNCATE TABLE `Category`;
SET FOREIGN_KEY_CHECKS = 1;

-- Category
INSERT INTO `Category` (`Category_ID`, `Item_ID`) VALUES
    (2001, 1001),
    (2002, 1002),
    (2003, 1003),
    (2004, 1004),
    (2005, 1005),
    (2006, 1006),
    (2007, 1007),
    (2008, 1008);

-- Item
INSERT INTO `Item` (`Category_ID`, `Item_ID`, `Item_name`, `Item_recipe`) VALUES
    (2001, 1001, 'Strawberry filled Puff', 'Pastries'),
    (2002, 1002, 'Macadamia Nut Cookie', 'Cookies'),
    (2003, 1003, 'Matcha Latte', 'Drinks'),
    (2004, 1004, 'Chicken Salad Sandwhich', 'Lunch'),
    (2005, 1005, 'Brioche Bread', 'Breads'),
    (2006, 1006, 'Boston Cream Pie Slice', 'Doughnuts'),
    (2007, 1007, 'Pumpkin Pie Slice', 'Pies'),
    (2008, 1008, 'Red velvet Cake Slice', 'Cakes');

-- Employee
-- Note: Hire_date for 440001 was 11/31/2026 in the spreadsheet (not a real date); stored as 2026-11-30.
INSERT INTO `Employee` (`Emp_ID`, `Job_title`, `Hire_date`) VALUES
    (440001, 'cashier', '2026-11-30'),
    (440002, 'manager', '2026-08-23'),
    (440003, 'banker', '2026-09-13'),
    (440004, 'janitor', '2026-10-23'),
    (440005, 'cashier', '2026-12-16');

-- Login
INSERT INTO `Login` (`Employee_ID`, `Pwd`) VALUES
    (440001, 'GeneandGrams1!'),
    (440002, '212GoGoDo212'),
    (440003, 'Giving807!'),
    (440004, 'DnDGames$s'),
    (440005, 'OvalShapesDonut');

-- Menu
INSERT INTO `Menu` (`Category_ID`, `Item_ID`, `Item_name`, `Price`, `Exp_Date`, `Category_Name`) VALUES
    (2001, 1001, 'Strawberry filled Puff', 3.25, '2026-12-07', 'Pastries'),
    (2002, 1002, 'Macadamia Nut Cookie', 2.25, '2026-12-08', 'Cookies'),
    (2003, 1003, 'Matcha Latte', 8.95, '2026-12-01', 'Drinks'),
    (2004, 1004, 'Chicken Salad Sandwhich', 6.35, '2026-12-10', 'Lunch'),
    (2005, 1005, 'Brioche Bread Loaf', 10.00, '2026-12-11', 'Breads'),
    (2006, 1006, 'Boston Cream Donut', 2.25, '2026-12-12', 'Doughnuts'),
    (2007, 1007, 'Pumpkin Pie Slice', 3.25, '2026-12-13', 'Pies'),
    (2008, 1008, 'Red velvet Cake Slice', 5.00, '2026-12-14', 'Cakes');

-- Inventory
INSERT INTO `Inventory` (`Category_ID`, `Item_ID`, `Ingredients_ID`, `Date_Time`, `Price`, `Quantity`) VALUES
    (2001, 1001, 5001, NULL, 3.25, 60),
    (2002, 1002, 5002, NULL, 2.25, 40),
    (2003, 1003, 5003, NULL, 8.95, 0),
    (2004, 1004, 5004, NULL, 6.35, 6),
    (2005, 1005, 5006, NULL, 10.00, 4),
    (2006, 1006, 5007, NULL, 2.25, 15),
    (2007, 1007, 5009, NULL, 3.25, 20),
    (2008, 1008, 5010, NULL, 5.00, 11);

-- Rewards
INSERT INTO `Rewards` (`Customer_ID`, `Tier_ID`, `Tier_type`, `Customer_pn`, `Customer_firstname`, `Customer_lastname`, `Customer_email`) VALUES
    (1, 401, 'Silver', '2408054545', 'Jane', 'Johnson', NULL),
    (2, 400, 'Bronze', '4105085454', 'Dave', 'Stewwart', 'Dave01@frostburg.edu'),
    (3, 402, 'Gold', '4437173341', 'Dave', 'Thomas', NULL),
    (4, 401, 'Silver', '6671714133', 'John', 'Brown', NULL),
    (5, 402, 'Gold', '7172129232', 'Amy', 'Davis', 'Amy@legacy.com');

-- Invoice
INSERT INTO `Invoice` (`Payment_ID`, `Payment_Method`, `Payment_Status`) VALUES
    (9001, 'Cash', 'Valid'),
    (9002, 'Card', 'Valid'),
    (9003, 'Card', 'Valid'),
    (9004, 'Card', 'Invalid'),
    (9005, 'Cash', 'Pending');

-- Transaction
INSERT INTO `Transaction` (`Transaction_ID`, `Order_ID`, `Reciept_ID`, `Employee_ID`, `Customer_ID`, `Payment_ID`, `Payment_Method`, `Payment_Status`, `Transaction_Total`, `T_Time`) VALUES
    (331, 601, 70001, 440005, 1, 9001, 'Cash', 'Valid', 18.71, '7:15am'),
    (332, 602, 70002, 440005, 2, 9002, 'Card', 'Valid', 6.35, '7:43am'),
    (333, 603, 70003, 440001, 3, 9003, 'Card', 'Valid', 13.00, '12:20pm'),
    (334, 604, 70004, 440001, 4, 9004, 'Card', 'Invalid', 20.00, '2:20pm'),
    (335, 605, 70005, 440005, 5, 9005, 'Cash', 'Pending', 4.50, '8:21am');

-- Transaction_Order
INSERT INTO `Transaction_Order` (`Order_ID`, `Transaction_ID`, `Item_ID`, `Price`, `Quantity`) VALUES
    (601, 331, 1003, 8.96, 1),
    (601, 331, 1001, 3.25, 3),
    (602, 332, 1004, 6.35, 1),
    (603, 333, 1007, 3.25, 4),
    (604, 334, 1008, 5.00, 2),
    (604, 334, 1005, 10.00, 1),
    (605, 335, 1006, 2.25, 2);

-- Price_Projection
INSERT INTO `Price_Projection` (`Item_ID`, `Cost`, `Price`, `Profit`) VALUES
    (1001, 2.50, 3.25, 0.75),
    (1002, 1.50, 2.25, 0.75),
    (1003, 6.99, 8.95, 1.96),
    (1004, 5.00, 6.35, 1.35),
    (1005, 8.25, 10.00, 1.75),
    (1006, 1.25, 2.25, 1.00),
    (1007, 2.15, 3.25, 1.10),
    (1008, 3.50, 5.00, 1.50);

-- ---------------------------------------------------------------------------
-- App user (the app logs in as this, NOT as root)
-- >>> CHANGE the password below before running <<<
-- ---------------------------------------------------------------------------
CREATE USER IF NOT EXISTS 'bakery_app'@'localhost' IDENTIFIED BY 'ChangeMe123!';
GRANT SELECT, INSERT, UPDATE, DELETE ON bakery.* TO 'bakery_app'@'localhost';
FLUSH PRIVILEGES;
