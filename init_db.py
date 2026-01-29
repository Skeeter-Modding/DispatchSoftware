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

    print(f"Initializing database at: {config.DATABASE_PATH}")
    conn = sqlite3.connect(config.DATABASE_PATH)
    cursor = conn.cursor()

    # Read and execute schema
    with open(config.SCHEMA_PATH, 'r') as f:
        schema = f.read()
        cursor.executescript(schema)

    conn.commit()
    conn.close()
    print("✓ Database initialized successfully!")

if __name__ == "__main__":
    init_database()