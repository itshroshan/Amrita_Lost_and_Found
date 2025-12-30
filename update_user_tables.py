import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE users ADD COLUMN is_verified INTEGER DEFAULT 0")
    print("Column is_verified added")
except Exception as e:
    print("Already exists or error:", e)

conn.commit()
conn.close()
