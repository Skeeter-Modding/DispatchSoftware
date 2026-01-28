import sqlite3
from datetime import datetime

# Martin Marietta Materials pickup locations
pickup_locations = [
    {
        "location_id": "MM-001",
        "name": "Statesboro Rail Yard",
        "company": "Martin Marietta Materials",
        "address": "8401 US HWY 301S",
        "city": "Statesboro",
        "state": "GA",
        "zip": "30458",
        "phone": "(912) 681-2992",
        "hours": "Mon - Fri | 7:00 AM - 4:00 PM",
        "sales_rep": "Turner Morris : (321) 246-4622",
        "district_office": "Florida District : (407) 723-4851",
        "division_office": "East : (919) 664-1700",
        "products": "Aggregates",
        "railway_access": "Yes"
    },
    {
        "location_id": "MM-002",
        "name": "Bloomingdale Rail Yard",
        "company": "Martin Marietta Materials",
        "address": "1054 Old River Road",
        "city": "Bloomingdale",
        "state": "GA",
        "zip": "31302",
        "phone": "(321) 246-4622",
        "hours": "Mon - Fri | 7:00 AM - 4:00 PM",
        "sales_rep": "Turner Morris : (321) 246-4622",
        "district_office": "Florida District : (407) 723-4851",
        "division_office": "East : (919) 664-1700",
        "products": "Aggregates",
        "railway_access": "Yes"
    },
    {
        "location_id": "MM-003",
        "name": "Wentworth Yard",
        "company": "Martin Marietta Materials",
        "address": "127 Gulfstream Road",
        "city": "Savannah",
        "state": "GA",
        "zip": "31407",
        "phone": "(912) 200-5420",
        "hours": "Mon - Fri | 7:00 AM - 4:00 PM",
        "sales_rep": "Turner Morris : (321) 246-4622",
        "district_office": "Florida District : (407) 723-4851",
        "division_office": "East : (919) 664-1700",
        "products": "Aggregates",
        "railway_access": "Yes"
    },
    {
        "location_id": "MM-004",
        "name": "Savannah Rail Yard",
        "company": "Martin Marietta Materials",
        "address": "4140-B Ogeechee Road",
        "city": "Savannah",
        "state": "GA",
        "zip": "31405",
        "phone": "(912) 234-8608",
        "hours": "Mon - Fri | 7:00 AM - 4:30 PM",
        "sales_rep": "Turner Morris : (321) 246-4622",
        "district_office": "Florida District : (407) 723-4851",
        "division_office": "East : (919) 664-1700",
        "products": "Aggregates",
        "railway_access": "Yes"
    },
    {
        "location_id": "MM-005",
        "name": "Savannah Marine Terminal",
        "company": "Martin Marietta Materials",
        "address": "42 Forbes Road",
        "city": "Savannah",
        "state": "GA",
        "zip": "31404",
        "phone": "(912) 231-8130",
        "hours": "Mon - Fri | 7:00 AM - 4:00 PM",
        "sales_rep": "Turner Morris : (321) 246-4622",
        "district_office": "Florida District : (407) 723-4851",
        "division_office": "East : (919) 664-1700",
        "products": "Aggregates",
        "railway_access": ""
    },
    {
        "location_id": "MM-006",
        "name": "Hinesville Yard",
        "company": "Martin Marietta Materials",
        "address": "160 Leroy Coffer Hwy",
        "city": "Midway",
        "state": "GA",
        "zip": "31320",
        "phone": "(912) 368-3962",
        "hours": "Mon - Fri | 7:00 AM - 3:00 PM",
        "sales_rep": "Turner Morris : (321) 246-4622",
        "district_office": "Florida District : (407) 723-4851",
        "division_office": "East : (919) 664-1700",
        "products": "Aggregates",
        "railway_access": ""
    }
]

def add_pickup_locations():
    """Add pickup locations to the database"""
    conn = sqlite3.connect('database/srm_dispatch.db')
    cursor = conn.cursor()
    
    # Create pickup locations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pickup_locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_id TEXT UNIQUE,
            name TEXT NOT NULL,
            company TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            zip TEXT,
            phone TEXT,
            hours TEXT,
            sales_rep TEXT,
            district_office TEXT,
            division_office TEXT,
            products TEXT,
            railway_access TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ Pickup locations table created")
    
    # Add pickup locations
    for location in pickup_locations:
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
            print(f"✓ Added pickup location: {location['name']} ({location['city']}, {location['state']})")
        except sqlite3.IntegrityError as e:
            print(f"✗ Pickup location already exists: {location['name']}")
    
    conn.commit()
    conn.close()
    print(f"\n✓ Pickup locations loading complete!")

if __name__ == "__main__":
    add_pickup_locations()