import sqlite3
from datetime import datetime

# Corrected South Carolina plants
sc_plants = [
    {
        "plant_id": "17043",
        "name": "Beaufort",
        "address": "30 Schwartz Rd Lot 9",
        "city": "Beaufort",
        "state": "SC",
        "zip": "29906",
        "phone": "(912) 525-3350"
    },
    {
        "plant_id": "17044",
        "name": "Bluffton",
        "address": "45 Sheridan Park Circle",
        "city": "Bluffton",
        "state": "SC",
        "zip": "29910",
        "phone": "(912) 525-3350"
    },
    {
        "plant_id": "17017",
        "name": "Hardeeville Stiney",
        "address": "1499 Stiney Rd.",
        "city": "Hardeeville",
        "state": "SC",
        "zip": "29927",
        "phone": "(912) 525-3350"
    },
    {
        "plant_id": "17032",
        "name": "Ridgeland",
        "address": "204 Pearlstine Dr",
        "city": "Ridgeland",
        "state": "SC",
        "zip": "29936",
        "phone": "(912) 525-3350"
    }
]

def update_plants():
    """Update South Carolina plants with correct information"""
    conn = sqlite3.connect('database/srm_dispatch.db')
    cursor = conn.cursor()
    
    # Delete incorrect South Carolina plants
    cursor.execute("DELETE FROM plants WHERE state = 'SC'")
    print("✓ Removed incorrect South Carolina plants")
    
    # Add correct plants
    for plant in sc_plants:
        try:
            cursor.execute('''
                INSERT INTO plants (plant_id, name, address, city, state, zip, phone, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                plant['plant_id'],
                plant['name'],
                plant['address'],
                plant['city'],
                plant['state'],
                plant['zip'],
                plant['phone'],
                'active',
                datetime.now(),
                datetime.now()
            ))
            print(f"✓ Added plant: {plant['name']} ({plant['city']}, {plant['state']})")
        except sqlite3.IntegrityError as e:
            print(f"✗ Error adding plant: {plant['name']} - {e}")
    
    conn.commit()
    
    # Verify the update
    cursor.execute("SELECT COUNT(*) FROM plants WHERE state = 'SC'")
    sc_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM plants WHERE state = 'GA'")
    ga_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n✓ Plant update complete!")
    print(f"  South Carolina plants: {sc_count}")
    print(f"  Georgia plants: {ga_count}")
    print(f"  Total plants: {sc_count + ga_count}")

if __name__ == "__main__":
    update_plants()