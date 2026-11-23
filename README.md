# 🍰 Bakery Management System

A Streamlit web app for managing a bakery, backed by a MySQL database. Built as a database class project.

**Features**
- Employee login (checked against the `Login` table)
- Place new orders (updates transactions and inventory in one database transaction)
- Sales dashboard (revenue by item, payment method, and category)
- Browse the menu, inventory (with low-stock warnings), transactions, and rewards customers
- Update stock and add rewards customers

## Important: the database is NOT stored in this repo

GitHub only stores the code and a SQL script. The actual MySQL database lives on
the computer running MySQL. After cloning, you create your own copy of the
database on your machine by running `src/bakery_setup.sql` (step 3 below).
The app connects to the MySQL server on **your** computer (`localhost`).

## Requirements

- [Python 3.9+](https://www.python.org/downloads/)
- [MySQL Server 8.x](https://dev.mysql.com/downloads/mysql/) (running locally)
- [MySQL Workbench](https://dev.mysql.com/downloads/workbench/) (optional, but the easiest way to run the SQL script)
- [Git](https://git-scm.com/downloads)

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/tejhons/bakery_project.git
cd <repo-folder>/src
```

### 2. Install Python packages
```bash
pip install -r requirements.txt
```

### 3. Create the database
**Option A: MySQL Workbench**
1. Connect to your local MySQL server (usually "Local instance MySQL80") with your root password.
2. Choose **File → Open SQL Script** and select `src/bakery_setup.sql`.
3. *(Recommended)* Near the bottom of the script, change `ChangeMe123!` to a password of your choice. This is the password for the `bakery_app` database user the app logs in with.
4. Click the lightning-bolt button to run the whole script.
5. Click the refresh icon next to **SCHEMAS**. You should see a `bakery` database with 11 tables.

**Option B: command line**
```bash
mysql -u root -p < bakery_setup.sql
```

The script creates the `bakery` database, all tables, the sample data, and a limited-access `bakery_app` user.

> Re-running the script resets all data back to the original sample data.

### 4. Set the database password

Use the password from `bakery_setup.sql` (`ChangeMe123!` unless you changed it).
Set it in the same terminal you'll run the app from:

| Terminal | Command |
|---|---|
| Windows Command Prompt | `set DB_PASSWORD=ChangeMe123!` |
| Windows PowerShell | `$env:DB_PASSWORD="ChangeMe123!"` |
| Mac / Linux | `export DB_PASSWORD="ChangeMe123!"` |

This only lasts for that terminal window, so repeat it whenever you open a new one.

### 5. Run the app
```bash
streamlit run app.py
```
If `streamlit` isn't recognized, use `python -m streamlit run app.py`.

Your browser opens the app. Log in with a sample employee:

| Employee ID | Password |
|---|---|
| 440001 | `GeneandGrams1!` |
| 440002 | `212GoGoDo212` |

(All sample logins are in the `Login` table.)

## Configuration

The app reads these environment variables. Defaults are shown.

| Variable | Default | Meaning |
|---|---|---|
| `DB_HOST` | `localhost` | MySQL server address |
| `DB_USER` | `bakery_app` | MySQL user |
| `DB_PASSWORD` | *(none)* | MySQL password |
| `DB_NAME` | `bakery` | Database name |

## Project structure

```
src/
├── app.py              # Streamlit app (UI + all database queries)
├── bakery_setup.sql    # Creates tables, loads sample data, creates app user
└── requirements.txt    # Python dependencies
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `Access denied for user 'bakery_app'` | `DB_PASSWORD` isn't set in this terminal, or doesn't match the password in `bakery_setup.sql` |
| `Can't connect to MySQL server` | MySQL isn't running. On Windows, start the **MySQL80** service |
| `Unknown database 'bakery'` | `bakery_setup.sql` didn't finish. Run it again |
| `streamlit` not recognized | Use `python -m streamlit run app.py` |
| Login says invalid | Use an ID and password from the `Login` table (see above) |

## Notes

- This is a class project: passwords in the `Login` table are stored as plain text for simplicity. A real app should store salted hashes.
- Sample data is fictional.
