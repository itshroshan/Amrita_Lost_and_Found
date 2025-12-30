import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
UPDATE users SET is_verified = 1
WHERE email = 'roshansah393@gmail.com'
""")

conn.commit()
conn.close()

print("Admin marked as verified")
