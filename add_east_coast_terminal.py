import sqlite3
from datetime import datetime

# East Coast Terminal Co. pickup location
east_coast_terminal = {
    "location_id": "ECT-001",
    "name": "East Coast Terminal Co.",
    "company": "East Coast Terminal Co.",
    "address": "136 Marine Terminal Drive",
    "city": "Savannah",
    "state": "GA",
    "zip": "31404",
    "phone": "(912) 236-1531",
    "hours": "Mon - Fri | 7:00 AM - 4:00 PM",
    "sales_rep": "",
    "district_office": "",
    "division_office": "",
    "products": "Aggregates",
    "railway_access": ""
}

def add_east_coast_terminal():
    """Add East Coast Terminal Co. pickup location"""
    conn = sqlite3.connect('database/srm_dispatch.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO pickup_locations (
                location_id, name, company, address, city, state, zip, phone, 
                hours, sales_rep, district_office, division_office, products, 
                railway_access, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            east_coast_terminal['location_id'],
            east_coast_terminal['name'],
            east_coast_terminal['company'],
            east_coast_terminal['address'],
            east_coast_terminal['city'],
            east_coast_terminal['state'],
            east_coast_terminal['zip'],
            east_coast_terminal['phone'],
            east_coast_terminal['hours'],
            east_coast_terminal['sales_rep'],
            east_coast_terminal['district_office'],
            east_coast_terminal['division_office'],
            east_coast_terminal['products'],
            east_coast_terminal['railway_access'],
            'active',
            datetime.now(),
            datetime.now()
        ))
        print(f"✓ Added pickup location: {east_coast_terminal['name']}")
    except sqlite3.IntegrityError as e:
        print(f"✗ Pickup location already exists: {east_coast_terminal['name']}")
    
    conn.commit()
    
    # Get total count
    cursor.execute("SELECT COUNT(*) FROM pickup_locations")
    total = cursor.fetchone()[0]
    
    # Count by company
    cursor.execute("SELECT company, COUNT(*) FROM pickup_locations GROUP BY company ORDER BY COUNT(*) DESC")
    print(f"\n📊 Pickup Locations by Company:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} locations")
    
    conn.close()
    print(f"\n✓ Pickup location added! Total: {total}")

if __name__ == "__main__":
    add_east_coast_terminal()