import sqlite3
from datetime import datetime

# Location-Material mappings based on user requirements
location_material_mappings = [
    # Martin Marietta Materials - All rock types
    {"location_id": "MM-001", "material_code": "SAND", "restriction": "None"},
    {"location_id": "MM-001", "material_code": "57", "restriction": "None"},
    {"location_id": "MM-001", "material_code": "89", "restriction": "None"},
    {"location_id": "MM-001", "material_code": "67", "restriction": "None"},
    {"location_id": "MM-001", "material_code": "4", "restriction": "None"},
    
    {"location_id": "MM-002", "material_code": "SAND", "restriction": "None"},
    {"location_id": "MM-002", "material_code": "57", "restriction": "None"},
    {"location_id": "MM-002", "material_code": "89", "restriction": "None"},
    {"location_id": "MM-002", "material_code": "67", "restriction": "None"},
    {"location_id": "MM-002", "material_code": "4", "restriction": "None"},
    
    {"location_id": "MM-003", "material_code": "SAND", "restriction": "None"},
    {"location_id": "MM-003", "material_code": "57", "restriction": "None"},
    {"location_id": "MM-003", "material_code": "89", "restriction": "None"},
    {"location_id": "MM-003", "material_code": "67", "restriction": "None"},
    {"location_id": "MM-003", "material_code": "4", "restriction": "None"},
    
    {"location_id": "MM-004", "material_code": "SAND", "restriction": "None"},
    {"location_id": "MM-004", "material_code": "57", "restriction": "None"},
    {"location_id": "MM-004", "material_code": "89", "restriction": "None"},
    {"location_id": "MM-004", "material_code": "67", "restriction": "None"},
    {"location_id": "MM-004", "material_code": "4", "restriction": "None"},
    
    {"location_id": "MM-005", "material_code": "SAND", "restriction": "None"},
    {"location_id": "MM-005", "material_code": "57", "restriction": "None"},
    {"location_id": "MM-005", "material_code": "89", "restriction": "None"},
    {"location_id": "MM-005", "material_code": "67", "restriction": "None"},
    {"location_id": "MM-005", "material_code": "4", "restriction": "None"},
    
    {"location_id": "MM-006", "material_code": "SAND", "restriction": "None"},
    {"location_id": "MM-006", "material_code": "57", "restriction": "None"},
    {"location_id": "MM-006", "material_code": "89", "restriction": "None"},
    {"location_id": "MM-006", "material_code": "67", "restriction": "None"},
    {"location_id": "MM-006", "material_code": "4", "restriction": "None"},
    
    # Vulcan Garden City - ONLY 57s, ONLY to Brunswick, GA plant
    {"location_id": "VL-001", "material_code": "57", "restriction": "Deliver to Brunswick, GA plant ONLY"},
    
    # E.R. Jahna Industries - ONLY Sand
    {"location_id": "JAHNA-001", "material_code": "SAND", "restriction": "None"},
    {"location_id": "JAHNA-002", "material_code": "SAND", "restriction": "None"},
    
    # Cemex Tillman (note: user said Cemex Deerfield but we have Tillman - will check)
    # Assuming Tillman is the Deerfield equivalent - ONLY Sand, ONLY for SC plants
    {"location_id": "CEMEX-001", "material_code": "SAND", "restriction": "Deliver to SC plants ONLY"},
    
    # East Coast Terminal - 57 Limestone, ONLY for SC plants
    {"location_id": "ECT-001", "material_code": "57L", "restriction": "Deliver to SC plants ONLY"}
]

def setup_location_materials():
    """Setup location-material mappings"""
    conn = sqlite3.connect('database/srm_dispatch.db')
    cursor = conn.cursor()
    
    # Create location_materials table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS location_materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pickup_location_id TEXT NOT NULL,
            material_code TEXT NOT NULL,
            restriction TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pickup_location_id) REFERENCES pickup_locations(location_id),
            FOREIGN KEY (material_code) REFERENCES material_types(code),
            UNIQUE(pickup_location_id, material_code)
        )
    ''')
    print("✓ Location materials table created")
    
    # Add mappings
    for mapping in location_material_mappings:
        try:
            cursor.execute('''
                INSERT INTO location_materials (pickup_location_id, material_code, restriction, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                mapping['location_id'],
                mapping['material_code'],
                mapping['restriction'],
                'active',
                datetime.now(),
                datetime.now()
            ))
            print(f"✓ Added: {mapping['location_id']} -> {mapping['material_code']} ({mapping['restriction'] or 'No restriction'})")
        except sqlite3.IntegrityError as e:
            print(f"✗ Mapping already exists: {mapping['location_id']} -> {mapping['material_code']}")
    
    conn.commit()
    conn.close()
    print(f"\n✓ Location-material mappings setup complete!")

if __name__ == "__main__":
    setup_location_materials()