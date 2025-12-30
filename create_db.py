import sqlite3

# Connect to database (creates file if not exists)
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    role TEXT
)
""")

# Insert admin account (only once)
cursor.execute("""
INSERT INTO users (name, email, password, role)
VALUES ('Admin', 'admin@amrita.edu', 'admin123', 'admin')
""")

conn.commit()
conn.close()

print("Database created successfully")
