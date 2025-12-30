import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Delete old admin
cursor.execute("DELETE FROM users WHERE role='admin'")

# Insert new admin
cursor.execute("""
INSERT INTO users (name, email, password, role)
VALUES (?, ?, ?, ?)
""", ("Admin", "roshansah393@gmail.com", "admin123", "admin"))

conn.commit()
conn.close()

print("Admin credentials updated successfully")
