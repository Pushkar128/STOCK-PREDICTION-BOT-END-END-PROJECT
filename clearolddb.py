import sqlite3

# Connect to your database
conn = sqlite3.connect('trades.db')
cursor = conn.cursor()

# Option A: Delete EVERYTHING and start fresh (Recommended)
cursor.execute("DELETE FROM signals")

# Option B: Delete only specific IDs if you want to keep some
# cursor.execute("DELETE FROM signals WHERE id <= 10")

conn.commit()
conn.close()

print("🧹 Database cleared! Your dashboard will be empty and ready for fresh signals.")