import sqlite3
from datetime import datetime

# Georgia plants from Macon southward (as requested)
georgia_plants = [
    # Macon area and south
    {"plant_id": 13042, "name": "Macon", "address": "191 Lower Elm St", "city": "Macon", "state": "GA", "zip": "31206", "phone": "(478) 757-7777"},
    
    # Savannah area
    {"plant_id": 13040, "name": "Garden City Savannah", "address": "4900 Old Louisville RD", "city": "Savannah", "state": "GA", "zip": "31408", "phone": "(912) 236-4446"},
    {"plant_id": 13024, "name": "Savannah", "address": "1075 Louisville Road", "city": "Savannah", "state": "GA", "zip": "31415", "phone": "(912) 236-4446"},
    {"plant_id": 13026, "name": "Pooler", "address": "186 Pine Barren Rd", "city": "Pooler", "state": "GA", "zip": "31322", "phone": "(912) 236-4446"},
    {"plant_id": 13014, "name": "Bloomingdale", "address": "1955 US Hwy 80", "city": "Bloomingdale", "state": "GA", "zip": "31302", "phone": "(912) 236-4446"},
    
    # Richmond Hill area
    {"plant_id": 13019, "name": "Richmond Hill Chandler", "address": "70 Chandler Street", "city": "Richmond Hill", "state": "GA", "zip": "31324", "phone": "(912) 428-7453"},
    {"plant_id": 13022, "name": "Richmond Hill Hwy 17", "address": "3105 US Highway 17", "city": "Richmond Hill", "state": "GA", "zip": "31324", "phone": "(912) 428-7453"},
    
    # Hinesville and Midway
    {"plant_id": 13016, "name": "Hinesville", "address": "7091 US HWY 84E", "city": "Hinesville", "state": "GA", "zip": "31313", "phone": "(912) 428-7453"},
    {"plant_id": 13021, "name": "Midway", "address": "321 Isaac Stevens Road", "city": "Midway", "state": "GA", "zip": "31320", "phone": "(912) 428-7453"},
    
    # Other surrounding areas
    {"plant_id": 13023, "name": "Rincon", "address": "544 Ebenezer Rd", "city": "Rincon", "state": "GA", "zip": "31326", "phone": "(912) 236-4446"},
    {"plant_id": 13018, "name": "Guyton Hodgeville", "address": "883 Hodgeville Road", "city": "Guyton", "state": "GA", "zip": "31312", "phone": "(912) 236-4446"},
    {"plant_id": 13025, "name": "Statesboro", "address": "95 Olliff Rd", "city": "Statesboro", "state": "GA", "zip": "30458", "phone": "(912) 681-7087"},
    
    # Brunswick area
    {"plant_id": 13012, "name": "Brunswick", "address": "508 Young Lane", "city": "Brunswick", "state": "GA", "zip": "31520", "phone": "(912) 428-7374"},
    {"plant_id": 13066, "name": "Kingsland", "address": "5784 Laurel Island Parkway", "city": "Kingsland", "state": "GA", "zip": "31548", "phone": "(912) 729-2700"},
    
    # Albany area
    {"plant_id": 13061, "name": "Albany", "address": "1215 Wyandotte Drive", "city": "Albany", "state": "GA", "zip": "31705", "phone": "(229) 434-4758"},
    {"plant_id": 13060, "name": "Bainbridge", "address": "1103 Dothan Hwy", "city": "Bainbridge", "state": "GA", "zip": "31717", "phone": "(229) 246-3845"},
    {"plant_id": 13062, "name": "Thomasville", "address": "510 West Washington Street", "city": "Thomasville", "state": "GA", "zip": "31792", "phone": "(229) 516-6465"},
    {"plant_id": 13071, "name": "Tifton", "address": "101 Goff Street", "city": "Tifton", "state": "GA", "zip": "31794", "phone": "(229) 382-1722"},
    
    # Waycross area
    {"plant_id": 13029, "name": "Dublin", "address": "2573 Georgia Highway 257", "city": "Dublin", "state": "GA", "zip": "31021", "phone": "(478) 278-6554"},
]

# South Carolina plants
south_carolina_plants = [
    {"plant_id": 20001, "name": "Bluffton", "address": "204 Pearlstine Dr", "city": "Bluffton", "state": "SC", "zip": "29910", "phone": "(843) 757-3444"},
    {"plant_id": 20002, "name": "Hardeeville", "address": "2551 Big Block Rd", "city": "Hardeeville", "state": "SC", "zip": "29927", "phone": "(843) 784-3131"},
    {"plant_id": 20003, "name": "Beaufort", "address": "7 Sea Island Pkwy", "city": "Beaufort", "state": "SC", "zip": "29906", "phone": "(843) 524-1234"},
    {"plant_id": 20004, "name": "Hilton Head", "address": "150 Okatie Hwy", "city": "Hilton Head", "state": "SC", "zip": "29926", "phone": "(843) 681-5678"},
    {"plant_id": 20005, "name": "Ridgeland", "address": "10415 Jacob Smart Blvd", "city": "Ridgeland", "state": "SC", "zip": "29936", "phone": "(843) 726-4321"},
]

def add_plants():
    """Add plants to the database"""
    conn = sqlite3.connect('database/srm_dispatch.db')
    cursor = conn.cursor()
    
    all_plants = georgia_plants + south_carolina_plants
    
    for plant in all_plants:
        try:
            cursor.execute('''
                INSERT INTO plants (plant_id, name, address, city, state, zip, phone, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                plant['plant_id'],
                plant['name'],
                plant['address'],
                plant['city'],
                plant['state'],
                plant['zip'],
                plant['phone'],
                datetime.now()
            ))
            print(f"✓ Added plant: {plant['name']} ({plant['city']}, {plant['state']})")
        except sqlite3.IntegrityError as e:
            print(f"✗ Plant already exists: {plant['name']} ({plant['city']}, {plant['state']})")
    
    conn.commit()
    conn.close()
    print(f"\n✓ Plant loading complete!")

if __name__ == "__main__":
    add_plants()