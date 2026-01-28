import sqlite3

def remove_driver():
    """Remove Kimberly Hill from drivers table"""
    conn = sqlite3.connect('database/srm_dispatch.db')
    cursor = conn.cursor()
    
    # Remove Kimberly Hill
    cursor.execute("DELETE FROM drivers WHERE name LIKE '%Kimberly Hill%'")
    
    rows_deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    if rows_deleted > 0:
        print(f"✓ Removed Kimberly Hill from drivers database")
    else:
        print("✗ Kimberly Hill not found in drivers database")

if __name__ == "__main__":
    remove_driver()