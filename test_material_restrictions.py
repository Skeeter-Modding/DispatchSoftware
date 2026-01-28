import sqlite3

conn = sqlite3.connect('database/srm_dispatch.db')
c = conn.cursor()

print("=" * 80)
print("TESTING MATERIAL RESTRICTIONS")
print("=" * 80)

# Test 1: Vulcan Garden City - Should only have 57s with restriction
print("\n1. Vulcan Garden City (VL-001):")
c.execute('''
    SELECT mt.name, lm.restriction
    FROM location_materials lm
    JOIN material_types mt ON lm.material_code = mt.code
    WHERE lm.pickup_location_id = "VL-001"
''')
for row in c.fetchall():
    print(f"   Material: {row[0]}")
    print(f"   Restriction: {row[1]}")

# Test 2: E.R. Jahna - Should only have Sand
print("\n2. E.R. Jahna Industries (JAHNA-001, JAHNA-002):")
c.execute('''
    SELECT lm.pickup_location_id, mt.name, lm.restriction
    FROM location_materials lm
    JOIN material_types mt ON lm.material_code = mt.code
    WHERE lm.pickup_location_id LIKE "JAHNA-%"
    ORDER BY lm.pickup_location_id
''')
for row in c.fetchall():
    print(f"   {row[0]}: {row[1]} - {row[2]}")

# Test 3: Cemex - Should only have Sand with SC restriction
print("\n3. Cemex Tillman (CEMEX-001):")
c.execute('''
    SELECT mt.name, lm.restriction
    FROM location_materials lm
    JOIN material_types mt ON lm.material_code = mt.code
    WHERE lm.pickup_location_id = "CEMEX-001"
''')
for row in c.fetchall():
    print(f"   Material: {row[0]}")
    print(f"   Restriction: {row[1]}")

# Test 4: East Coast Terminal - Should only have 57 Limestone with SC restriction
print("\n4. East Coast Terminal (ECT-001):")
c.execute('''
    SELECT mt.name, lm.restriction
    FROM location_materials lm
    JOIN material_types mt ON lm.material_code = mt.code
    WHERE lm.pickup_location_id = "ECT-001"
''')
for row in c.fetchall():
    print(f"   Material: {row[0]}")
    print(f"   Restriction: {row[1]}")

# Test 5: Martin Marietta - Should have all materials
print("\n5. Martin Marietta Materials (MM-001):")
c.execute('''
    SELECT mt.name, lm.restriction
    FROM location_materials lm
    JOIN material_types mt ON lm.material_code = mt.code
    WHERE lm.pickup_location_id = "MM-001"
    ORDER BY mt.name
''')
for row in c.fetchall():
    print(f"   {row[0]} - Restriction: {row[1]}")

# Test 6: Verify all materials
print("\n6. All Material Types:")
c.execute('SELECT code, name, category FROM material_types ORDER BY category, name')
for row in c.fetchall():
    print(f"   {row[0]:6} | {row[1]:20} | {row[2]}")

# Test 7: Count mappings
print("\n7. Location-Material Mapping Summary:")
c.execute('''
    SELECT 
        (SELECT COUNT(*) FROM pickup_locations) as total_locations,
        (SELECT COUNT(*) FROM material_types) as total_materials,
        (SELECT COUNT(*) FROM location_materials) as total_mappings
''')
counts = c.fetchone()
print(f"   Total Locations: {counts[0]}")
print(f"   Total Materials: {counts[1]}")
print(f"   Total Mappings: {counts[2]}")

print("\n" + "=" * 80)
print("✅ ALL TESTS COMPLETED")
print("=" * 80)

conn.close()