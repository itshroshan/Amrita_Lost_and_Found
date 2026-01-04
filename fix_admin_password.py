import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

hashed = generate_password_hash("admin1234")  # your admin password

cursor.execute("""
    UPDATE users
    SET password=?, is_verified=1
    WHERE role='admin'
""", (hashed,))

conn.commit()
conn.close()

print("Admin password fixed")
