import sqlite3
import os

# Import configuration
import config

def init_database():
    """Initialize the dispatch database with all tables"""
    # Ensure database directory exists
    db_dir = os.path.dirname(config.DATABASE_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        print(f"Created database directory: {db_dir}")

    db_exists = os.path.exists(config.DATABASE_PATH)

    if db_exists:
        print(f"Database already exists at: {config.DATABASE_PATH}")
        print("Checking for schema updates...")
    else:
        print(f"Creating new database at: {config.DATABASE_PATH}")

    conn = sqlite3.connect(config.DATABASE_PATH)
    cursor = conn.cursor()

    # Read and execute schema (CREATE IF NOT EXISTS is safe for existing DBs)
    with open(config.SCHEMA_PATH, 'r') as f:
        schema = f.read()
        cursor.executescript(schema)

    conn.commit()

    # Check if we have any data
    cursor.execute('SELECT COUNT(*) FROM drivers')
    driver_count = cursor.fetchone()[0]

    conn.close()

    if db_exists:
        print(f"Existing database preserved with {driver_count} drivers")
    else:
        print("New database created - run init_sample_data.py to add sample data")

    print("Database initialization complete!")

if __name__ == "__main__":
    init_database()