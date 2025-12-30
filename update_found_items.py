import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
ALTER TABLE found_items
ADD COLUMN reported_by TEXT
""")

conn.commit()
conn.close()

print("found_items table updated")
