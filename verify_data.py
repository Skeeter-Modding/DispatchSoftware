import sqlite3

conn = sqlite3.connect('database/srm_dispatch.db')
c = conn.cursor()

# Check loads
c.execute('SELECT COUNT(*) FROM loads')
print(f'Loads in database: {c.fetchone()[0]}')

# Check plants
c.execute('SELECT COUNT(*) FROM plants')
print(f'Plants in database: {c.fetchone()[0]}')

# Show sample plants
print('\nSample plants:')
c.execute('SELECT name, city, state FROM plants LIMIT 5')
for row in c.fetchall():
    print(f'  - {row[0]} ({row[1]}, {row[2]})')

conn.close()