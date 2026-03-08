import sqlite3

conn = sqlite3.connect("lostfound.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE lost_items(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
description TEXT,
location TEXT,
date TEXT
)
""")

cur.execute("""
CREATE TABLE found_items(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
description TEXT,
location TEXT,
date TEXT
)
""")

conn.commit()
conn.close()

print("Database Created")
