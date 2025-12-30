import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Add reported_by column if not exists
try:
    cursor.execute("ALTER TABLE found_items ADD COLUMN reported_by TEXT")
    print("Column 'reported_by' added successfully")
except sqlite3.OperationalError as e:
    print("Column already exists or error:", e)

conn.commit()
conn.close()
