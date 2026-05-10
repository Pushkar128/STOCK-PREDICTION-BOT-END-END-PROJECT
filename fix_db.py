import sqlite3
from datetime import datetime

# Connect to your existing database
conn = sqlite3.connect('trades.db')
cursor = conn.cursor()

# Get today's date in the format your filter expects (YYYY-MM-DD)
today_date = datetime.now().strftime("%Y-%m-%d")

# Fetch all signals
cursor.execute("SELECT id, time FROM signals")
rows = cursor.fetchall()

for row in rows:
    id_val, time_val = row
    # If the stored time doesn't have a date (length is short like "15:30")
    if len(time_val) <= 5:
        new_time = f"{today_date} {time_val}"
        cursor.execute("UPDATE signals SET time = ? WHERE id = ?", (new_time, id_val))
        print(f"Fixed ID {id_val}: {time_val} -> {new_time}")

conn.commit()
conn.close()
print("✅ Database repair complete!")