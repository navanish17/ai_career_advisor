import sqlite3
import os

# Find database file
db_files = [f for f in os.listdir('.') if f.endswith('.db')]
if db_files:
    DB_PATH = db_files[0]
    print(f"Found database: {DB_PATH}")
else:
    DB_PATH = "app.db"
    print("Using default: app.db")

# Connect
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check if column exists
cursor.execute("PRAGMA table_info(career_insights)")
columns = [row[1] for row in cursor.fetchall()]

print(f"Current columns: {columns}")

if 'top_salary' not in columns:
    print("Adding top_salary column...")
    cursor.execute("ALTER TABLE career_insights ADD COLUMN top_salary TEXT")
    conn.commit()
    print("✅ Column added successfully!")
else:
    print("✅ Column already exists!")

conn.close()
