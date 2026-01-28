import sqlite3
from datetime import datetime

# New pickup locations
new_pickup_locations = [
    {
        "location_id": "VL-001",
        "name": "Garden City",
        "company": "Vulcan",
        "address": "53 Sonny Perdue Dr",
        "city": "Garden City",
        "state": "GA",
        "zip": "31408",
        "phone": "912-964-9493",
        "hours": "Mon - Fri | 7:00 AM - 4:00 PM",
        "sales_rep": "Sales : 706-533-0519",
        "district_office": "",
        "division_office": "",
        "products": "Aggregates",
        "railway_access": ""
    },
    {
        "location_id": "JAHNA-001",
        "name": "Savannah Sand Mine",
        "company": "E.R. Jahna Industries",
        "address": "828 Rogers Pasture Rd",
        "city": "Fleming",
        "state": "GA",
        "zip": "31309",
        "phone": "",
        "hours": "Mon - Fri | 7:00 AM - 4:00 PM",
        "sales_rep": "",
        "district_office": "",
        "division_office": "",
        "products": "Aggregates",
        "railway_access": ""
    },
    {
        "location_id": "JAHNA-002",
        "name": "Deerfield Sand Mine",
        "company": "E.R. Jahna Industries",
        "address": "Deerfield Sand Mine",
        "city": "Fleming",
        "state": "GA",
        "zip": "31309",
        "phone": "",
        "hours": "Mon - Fri | 7:00 AM - 4:00 PM",
        "sales_rep": "",
        "district_office": "",
        "division_office": "",
        "products": "Aggregates",
        "railway_access": ""
    },
    {
        "location_id": "CEMEX-001",
        "name": "Tillman",
        "company": "Cemex",
        "address": "Highway 321",
        "city": "Tillman",
        "state": "SC",
        "zip": "29943",
        "phone": "1-855-292-8453",
        "hours": "Mon-Fri 7:00 AM - 4:00 PM | Sat-Sun Closed",
        "sales_rep": "Cemex Go Support : 800-767-0608",
        "district_office": "",
        "division_office": "",
        "products": "Aggregates",
        "railway_access": ""
    }
]

def add_new_pickup_locations():
    """Add new pickup locations to the database"""
    conn = sqlite3.connect('database/srm_dispatch.db')
    cursor = conn.cursor()
    
    # Add new pickup locations
    for location in new_pickup_locations:
        try:
            cursor.execute('''
                INSERT INTO pickup_locations (
                    location_id, name, company, address, city, state, zip, phone, 
                    hours, sales_rep, district_office, division_office, products, 
                    railway_access, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                location['location_id'],
                location['name'],
                location['company'],
                location['address'],
                location['city'],
                location['state'],
                location['zip'],
                location['phone'],
                location['hours'],
                location['sales_rep'],
                location['district_office'],
                location['division_office'],
                location['products'],
                location['railway_access'],
                'active',
                datetime.now(),
                datetime.now()
            ))
            print(f"✓ Added pickup location: {location['name']} ({location['company']})")
        except sqlite3.IntegrityError as e:
            print(f"✗ Pickup location already exists: {location['name']}")
    
    conn.commit()
    
    # Get total count
    cursor.execute("SELECT COUNT(*) FROM pickup_locations")
    total = cursor.fetchone()[0]
    
    # Count by company
    cursor.execute("SELECT company, COUNT(*) FROM pickup_locations GROUP BY company")
    print(f"\n📊 Pickup Locations by Company:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} locations")
    
    conn.close()
    print(f"\n✓ New pickup locations added! Total: {total}")

if __name__ == "__main__":
    add_new_pickup_locations()