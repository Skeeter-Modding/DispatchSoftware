import sqlite3

def init_database():
    """Initialize the dispatch database with all tables"""
    conn = sqlite3.connect('database/dispatch.db')
    cursor = conn.cursor()
    
    # Read and execute schema
    with open('database/schema.sql', 'r') as f:
        schema = f.read()
        cursor.executescript(schema)
    
    conn.commit()
    conn.close()
    print("✓ Database initialized successfully!")

if __name__ == "__main__":
    init_database()