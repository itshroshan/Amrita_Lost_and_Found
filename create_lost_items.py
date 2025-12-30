import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS lost_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_email TEXT,
    item_name TEXT,
    description TEXT,
    location TEXT
)
""")

conn.commit()
conn.close()

print("Lost items table created")
