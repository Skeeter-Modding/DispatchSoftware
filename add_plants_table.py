import sqlite3

def add_plants_table():
    """Add plants table to existing database"""
    conn = sqlite3.connect('database/dispatch.db')
    cursor = conn.cursor()
    
    # Add plants table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plant_id TEXT UNIQUE,
            name TEXT NOT NULL,
            address TEXT,
            city TEXT,
            state TEXT,
            zip TEXT,
            phone TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add plant_id column to loads table if it doesn't exist
    try:
        cursor.execute('ALTER TABLE loads ADD COLUMN plant_id INTEGER')
        print("✓ Added plant_id column to loads table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("✓ plant_id column already exists in loads table")
        else:
            raise
    
    conn.commit()
    conn.close()
    print("✓ Database schema updated successfully!")

if __name__ == "__main__":
    add_plants_table()