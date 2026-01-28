import sqlite3

conn = sqlite3.connect('database/srm_dispatch.db')
c = conn.cursor()

# Check drivers
c.execute("SELECT COUNT(*) FROM drivers WHERE status = 'active'")
driver_count = c.fetchone()[0]
print(f"👨‍✈️ Active Drivers: {driver_count}")

# Check if Kimberly Hill exists
c.execute("SELECT * FROM drivers WHERE name LIKE '%Kimberly%'")
kimberly = c.fetchone()
if kimberly:
    print("⚠️  Kimberly Hill still in database")
else:
    print("✓ Kimberly Hill removed successfully")

# Check pickup locations
c.execute("SELECT COUNT(*) FROM pickup_locations")
pickup_count = c.fetchone()[0]
print(f"\n📦 Total Pickup Locations: {pickup_count}")

# Show pickup locations by company
print("\n📦 Pickup Locations by Company:")
c.execute("SELECT company, COUNT(*) FROM pickup_locations GROUP BY company ORDER BY company")
for row in c.fetchall():
    print(f"  {row[0]}: {row[1]}")

# Show all pickup locations
print("\n📦 All Pickup Locations:")
c.execute("SELECT location_id, name, company, city, state FROM pickup_locations ORDER BY company, name")
for row in c.fetchall():
    print(f"  {row[0]:15} | {row[1]:30} | {row[2]:25} | {row[3]}, {row[4]}")

conn.close()