import sqlite3
import os

# Import configuration
import config

# Try to import libsql for Turso support
if config.USE_TURSO:
    try:
        import libsql_experimental as libsql
    except ImportError:
        print("WARNING: libsql not installed, using local SQLite")
        config.USE_TURSO = False

def get_connection():
    """Get database connection - Turso or local SQLite"""
    if config.USE_TURSO:
        conn = libsql.connect(
            "dispatchsoftware",
            sync_url=config.TURSO_DATABASE_URL,
            auth_token=config.TURSO_AUTH_TOKEN
        )
        conn.sync()
        return conn
    else:
        return sqlite3.connect(config.DATABASE_PATH)

def init_database():
    """Initialize the dispatch database with all tables"""

    if config.USE_TURSO:
        print(f"Initializing Turso database: {config.TURSO_DATABASE_URL}")
    else:
        # Ensure database directory exists for local SQLite
        db_dir = os.path.dirname(config.DATABASE_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            print(f"Created database directory: {db_dir}")

        db_exists = os.path.exists(config.DATABASE_PATH)
        if db_exists:
            print(f"Database already exists at: {config.DATABASE_PATH}")
        else:
            print(f"Creating new database at: {config.DATABASE_PATH}")

    conn = get_connection()
    cursor = conn.cursor()

    # Read schema
    with open(config.SCHEMA_PATH, 'r') as f:
        schema = f.read()

    # Execute schema - split into statements for Turso compatibility
    if config.USE_TURSO:
        statements = [s.strip() for s in schema.split(';') if s.strip()]
        for statement in statements:
            try:
                cursor.execute(statement)
            except Exception as e:
                if 'already exists' not in str(e).lower():
                    print(f"Schema warning: {e}")
        conn.commit()
        conn.sync()
    else:
        cursor.executescript(schema)
        conn.commit()

    # Check if we have any data
    cursor.execute('SELECT COUNT(*) FROM drivers')
    driver_count = cursor.fetchone()[0]

    conn.close()

    if config.USE_TURSO:
        print(f"Turso database initialized with {driver_count} drivers")
    else:
        print(f"Local database initialized with {driver_count} drivers")

    print("Database initialization complete!")

if __name__ == "__main__":
    init_database()