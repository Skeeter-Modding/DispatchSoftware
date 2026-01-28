import sqlite3

conn = sqlite3.connect('database/srm_dispatch.db')
c = conn.cursor()

c.execute("SELECT id, name, phone, status FROM drivers WHERE name LIKE '%Hill%'")
results = c.fetchall()

if results:
    print("Found Hill:")
    for row in results:
        print(f"  ID: {row[0]}, Name: {row[1]}, Phone: {row[2]}, Status: {row[3]}")
else:
    print("Hill not found")

conn.close()