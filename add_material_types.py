import sqlite3
from datetime import datetime

# Material types we haul
material_types = [
    {"code": "SAND", "name": "Sand", "description": "Fine aggregate material", "category": "Aggregates"},
    {"code": "57", "name": "57s", "description": "Coarse aggregate - 1 inch nominal size", "category": "Rock"},
    {"code": "89", "name": "89s", "description": "Fine aggregate - 3/8 inch nominal size", "category": "Rock"},
    {"code": "67", "name": "67s", "description": "Coarse aggregate - 3/4 inch nominal size", "category": "Rock"},
    {"code": "4", "name": "4s", "description": "Large aggregate - 4 inch nominal size", "category": "Rock"},
    {"code": "57L", "name": "57 Limestone", "description": "57 limestone - 1 inch nominal size", "category": "Rock"}
]

def add_material_types():
    """Add material types to the database"""
    conn = sqlite3.connect('database/srm_dispatch.db')
    cursor = conn.cursor()
    
    # Create material types table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS material_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ Material types table created")
    
    # Add material types
    for material in material_types:
        try:
            cursor.execute('''
                INSERT INTO material_types (code, name, description, category, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                material['code'],
                material['name'],
                material['description'],
                material['category'],
                'active',
                datetime.now(),
                datetime.now()
            ))
            print(f"✓ Added material: {material['name']} ({material['code']})")
        except sqlite3.IntegrityError as e:
            print(f"✗ Material already exists: {material['name']}")
    
    conn.commit()
    conn.close()
    print(f"\n✓ Material types loading complete!")

if __name__ == "__main__":
    add_material_types()