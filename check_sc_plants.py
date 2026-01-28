import sqlite3

conn = sqlite3.connect('database/srm_dispatch.db')
c = conn.cursor()

print("South Carolina Plants:")
print("=" * 80)
c.execute('SELECT plant_id, name, address, city, state, zip, phone FROM plants WHERE state = "SC" ORDER BY name')
for row in c.fetchall():
    print(f"\nPlant ID: {row[0]}")
    print(f"Name: {row[1]}")
    print(f"Address: {row[2]}")
    print(f"City: {row[3]}, {row[4]} {row[5]}")
    print(f"Phone: {row[6]}")

conn.close()