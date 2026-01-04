import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Get all users
cursor.execute("SELECT id, password FROM users")
users = cursor.fetchall()

for user_id, password in users:
    # Skip already hashed passwords
    if password.startswith("pbkdf2:"):
        continue

    hashed = generate_password_hash(password)

    cursor.execute(
        "UPDATE users SET password=? WHERE id=?",
        (hashed, user_id)
    )

conn.commit()
conn.close()

print("✅ All existing user passwords have been hashed")
