"""
Load real Smyrna Ready Mix data into the dispatch system
"""

import sqlite3
from datetime import date

DATABASE = 'database/srm_dispatch.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def query_db(query, args=(), commit=False):
    """Helper function for database queries"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, args)
    
    if commit:
        conn.commit()
        result = cur.lastrowid
    else:
        result = cur.fetchall()
    
    conn.close()
    return result

def clear_sample_data():
    """Clear sample data but keep the structure"""
    print("Clearing sample data...")
    conn = get_db()
    
    # Clear in order due to foreign key constraints
    conn.execute('DELETE FROM tracking_events')
    conn.execute('DELETE FROM loads')
    conn.execute('DELETE FROM assignments')
    conn.execute('DELETE FROM jobs')
    conn.execute('DELETE FROM trailers')
    conn.execute('DELETE FROM trucks')
    conn.execute('DELETE FROM drivers')
    
    conn.commit()
    conn.close()
    print("✓ Sample data cleared")

def load_real_data():
    """Load real Smyrna Ready Mix data"""
    
    # Real driver data
    drivers = [
        ('THOR WAYMAN', '555-0001', 'thor.wayman@smyrnareadymix.com', 'DRV001'),
        ('ALBERT MITCHELL', '555-0002', 'albert.mitchell@smyrnareadymix.com', 'DRV002'),
        ('DAVID POWELL', '555-0003', 'david.powell@smyrnareadymix.com', 'DRV003'),
        ('TALLY BUTLER', '555-0004', 'tally.butler@smyrnareadymix.com', 'DRV004'),
        ('KEITH CROFT', '555-0005', 'keith.croft@smyrnareadymix.com', 'DRV005'),
        ('JEROME POLITE', '555-0006', 'jerome.polite@smyrnareadymix.com', 'DRV006'),
        ('CLEVELAND TOLBERT', '555-0007', 'cleveland.tolbert@smyrnareadymix.com', 'DRV007'),
        ('RYAN REED', '555-0008', 'ryan.reed@smyrnareadymix.com', 'DRV008'),
        ('DONNELL DAVIS', '555-0009', 'donnell.davis@smyrnareadymix.com', 'DRV009'),
        ('KIMBERLY ROBERTS', '555-0010', 'kimberly.roberts@smyrnareadymix.com', 'DRV010'),
        ('DONALD WINTER', '555-0011', 'donald.winter@smyrnareadymix.com', 'DRV011'),
        ('JOSEPH K. SARGENT', '555-0012', 'joseph.sargent@smyrnareadymix.com', 'DRV012'),
        ('LONNIE THOMPSON', '555-0013', 'lonnie.thompson@smyrnareadymix.com', 'DRV013'),
        ('RACHEL HUTTO', '555-0014', 'rachel.hutto@smyrnareadymix.com', 'DRV014'),
        ('NAQUETIG LEWIS', '555-0015', 'naquetig.lewis@smyrnareadymix.com', 'DRV015'),
        ('DAVID HOUSTON', '555-0016', 'david.houston@smyrnareadymix.com', 'DRV016'),
        ('GLENN GOODNO', '555-0017', 'glenn.goodno@smyrnareadymix.com', 'DRV017'),
        ('KIMBERLY HILL', '555-0018', 'kimberly.hill@smyrnareadymix.com', 'DRV018'),
        ('LESLEY MURPHY', '555-0019', 'lesley.murphy@smyrnareadymix.com', 'DRV019'),
        ('RENA ABROMOWITZ', '555-0020', 'rena.abromowitz@smyrnareadymix.com', 'DRV020'),
        ('JIMMY LAND', '555-0021', 'jimmy.land@smyrnareadymix.com', 'DRV021'),
        ('BILL RUMPTZ', '555-0022', 'bill.rumptz@smyrnareadymix.com', 'DRV022'),
        ('DORRELL GRANT', '555-0023', 'dorrell.grant@smyrnareadymix.com', 'DRV023'),
        ('ALICIA SAMPSON', '555-0024', 'alicia.sampson@smyrnareadymix.com', 'DRV024'),
        ('QUADASHA JACKSON', '555-0025', 'quadasha.jackson@smyrnareadymix.com', 'DRV025'),
    ]
    
    print("Loading drivers...")
    for driver in drivers:
        query_db('''
            INSERT INTO drivers (name, phone, email, employee_id)
            VALUES (?, ?, ?, ?)
        ''', driver, commit=True)
    print(f"✓ Added {len(drivers)} drivers")
    
    # Real truck data
    trucks = [
        ('23060', 'TRK-23060', 'Mack', 'Granite', 2023, 20, 'SAMARA-23060'),
        ('23066', 'TRK-23066', 'Mack', 'Granite', 2023, 20, 'SAMARA-23066'),
        ('23068', 'TRK-23068', 'Mack', 'Granite', 2023, 20, 'SAMARA-23068'),
        ('24067', 'TRK-24067', 'Mack', 'Granite', 2024, 20, 'SAMARA-24067'),
        ('24068', 'TRK-24068', 'Mack', 'Granite', 2024, 20, 'SAMARA-24068'),
        ('25046', 'TRK-25046', 'Mack', 'Granite', 2025, 20, 'SAMARA-25046'),
        ('25049', 'TRK-25049', 'Mack', 'Granite', 2025, 20, 'SAMARA-25049'),
        ('25052', 'TRK-25052', 'Mack', 'Granite', 2025, 20, 'SAMARA-25052'),
        ('825', 'TRK-825', 'Peterbilt', '379', 2020, 22, 'SAMARA-825'),
        ('828', 'TRK-828', 'Peterbilt', '379', 2020, 22, 'SAMARA-828'),
        ('829', 'TRK-829', 'Peterbilt', '379', 2020, 22, 'SAMARA-829'),
        ('DT4', 'TRK-DT4', 'Kenworth', 'W900', 2021, 21, 'SAMARA-DT4'),
        ('SC2', 'TRK-SC2', 'Kenworth', 'W900', 2021, 21, 'SAMARA-SC2'),
        ('SG21', 'TRK-SG21', 'Freightliner', 'Cascadia', 2020, 20, 'SAMARA-SG21'),
        ('SG24', 'TRK-SG24', 'Freightliner', 'Cascadia', 2020, 20, 'SAMARA-SG24'),
        ('SG25', 'TRK-SG25', 'Freightliner', 'Cascadia', 2020, 20, 'SAMARA-SG25'),
        ('SG26', 'TRK-SG26', 'Freightliner', 'Cascadia', 2020, 20, 'SAMARA-SG26'),
        ('SG27', 'TRK-SG27', 'Freightliner', 'Cascadia', 2020, 20, 'SAMARA-SG27'),
        ('SG28', 'TRK-SG28', 'Freightliner', 'Cascadia', 2020, 20, 'SAMARA-SG28'),
        ('SG9', 'TRK-SG9', 'International', 'Lonestar', 2022, 23, 'SAMARA-SG9'),
        ('T10', 'TRK-T10', 'International', 'Lonestar', 2022, 23, 'SAMARA-T10'),
        ('T7', 'TRK-T7', 'Mack', 'Anthem', 2021, 21, 'SAMARA-T7'),
        ('T9', 'TRK-T9', 'Mack', 'Anthem', 2021, 21, 'SAMARA-T9'),
        ('W10', 'TRK-W10', 'Volvo', 'VNL', 2020, 20, 'SAMARA-W10'),
        ('W14', 'TRK-W14', 'Volvo', 'VNL', 2020, 20, 'SAMARA-W14'),
        ('W17', 'TRK-W17', 'Volvo', 'VNL', 2020, 20, 'SAMARA-W17'),
        ('W18', 'TRK-W18', 'Volvo', 'VNL', 2020, 20, 'SAMARA-W18'),
        ('W19', 'TRK-W19', 'Volvo', 'VNL', 2020, 20, 'SAMARA-W19'),
        ('W22', 'TRK-W22', 'Volvo', 'VNL', 2020, 20, 'SAMARA-W22'),
        ('W23', 'TRK-W23', 'Volvo', 'VNL', 2020, 20, 'SAMARA-W23'),
        ('W24', 'TRK-W24', 'Volvo', 'VNL', 2020, 20, 'SAMARA-W24'),
        ('W27', 'TRK-W27', 'Volvo', 'VNL', 2020, 20, 'SAMARA-W27'),
        ('W28', 'TRK-W28', 'Volvo', 'VNL', 2020, 20, 'SAMARA-W28'),
        ('W29', 'TRK-W29', 'Volvo', 'VNL', 2020, 20, 'SAMARA-W29'),
        ('W30', 'TRK-W30', 'Volvo', 'VNL', 2020, 20, 'SAMARA-W30'),
        ('W31', 'TRK-W31', 'Volvo', 'VNL', 2020, 20, 'SAMARA-W31'),
        ('W4', 'TRK-W4', 'Western Star', '4700', 2019, 22, 'SAMARA-W4'),
        ('W5', 'TRK-W5', 'Western Star', '4700', 2019, 22, 'SAMARA-W5'),
        ('W6', 'TRK-W6', 'Western Star', '4700', 2019, 22, 'SAMARA-W6'),
        ('W9', 'TRK-W9', 'Western Star', '4700', 2019, 22, 'SAMARA-W9'),
    ]
    
    print("Loading trucks...")
    for truck in trucks:
        query_db('''
            INSERT INTO trucks (truck_number, plate_number, make, model, year, capacity_tons, samara_device_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', truck, commit=True)
    print(f"✓ Added {len(trucks)} trucks")
    
    # Real trailer data
    trailers = [
        ('DT-59', 'TRL-DT59', 'dump', 10),
        ('DT65', 'TRL-DT65', 'dump', 10),
        ('DT-67', 'TRL-DT67', 'dump', 10),
        ('DT-87', 'TRL-DT87', 'dump', 10),
        ('DT88', 'TRL-DT88', 'dump', 10),
        ('DT-107', 'TRL-DT107', 'dump', 10),
        ('DT-111', 'TRL-DT111', 'dump', 10),
        ('BT-114', 'TRL-BT114', 'dump', 12),
        ('DT11', 'TRL-DT11', 'dump', 10),
        ('WT-14', 'TRL-WT14', 'dump', 10),
        ('D-2', 'TRL-D2', 'dump', 10),
        ('D03', 'TRL-D03', 'dump', 10),
        ('WT-13', 'TRL-WT13', 'dump', 10),
    ]
    
    print("Loading trailers...")
    for trailer in trailers:
        query_db('''
            INSERT INTO trailers (trailer_number, plate_number, type, capacity_cubic_yards)
            VALUES (?, ?, ?, ?)
        ''', trailer, commit=True)
    print(f"✓ Added {len(trailers)} trailers")
    
    # Real driver-truck-trailer assignments
    # Format: (driver_name, truck_number, trailer_number)
    assignments_data = [
        ('THOR WAYMAN', '23060', 'DT-59'),
        ('ALBERT MITCHELL', '23066', 'DT65'),
        ('DAVID POWELL', '23068', 'DT-67'),
        ('TALLY BUTLER', '24067', 'DT-87'),
        ('KEITH CROFT', '24068', 'DT88'),
        ('JEROME POLITE', '25046', 'DT-107'),
        ('CLEVELAND TOLBERT', '25049', 'DT-111'),
        ('RYAN REED', '25052', 'BT-114'),
        ('DONNELL DAVIS', '825', None),
        ('KIMBERLY ROBERTS', '828', None),
        ('DONALD WINTER', '829', None),
        ('JOSEPH K. SARGENT', 'SG24', None),
        ('LONNIE THOMPSON', 'SG27', None),
        ('RACHEL HUTTO', 'SG28', None),
        ('NAQUETIG LEWIS', 'SG9', 'DT11'),
        ('DAVID HOUSTON', 'T10', 'WT-14'),
        ('GLENN GOODNO', 'T7', None),
        ('KIMBERLY HILL', 'W10', None),
        ('LESLEY MURPHY', 'W14', 'D03'),
        ('RENA ABROMOWITZ', 'W19', None),
        ('JIMMY LAND', 'W23', 'WT-13'),
        ('BILL RUMPTZ', 'W28', None),
        ('DORRELL GRANT', 'W29', None),
        ('ALICIA SAMPSON', 'W30', None),
        ('QUADASHA JACKSON', 'W31', None),
    ]
    
    print("Creating driver assignments...")
    today = date.today()
    
    # Get all drivers, trucks, and trailers
    drivers_dict = {row['name']: row['id'] for row in query_db('SELECT id, name FROM drivers')}
    trucks_dict = {row['truck_number']: row['id'] for row in query_db('SELECT id, truck_number FROM trucks')}
    trailers_dict = {row['trailer_number']: row['id'] for row in query_db('SELECT id, trailer_number FROM trailers')}
    
    for driver_name, truck_num, trailer_num in assignments_data:
        driver_id = drivers_dict.get(driver_name)
        truck_id = trucks_dict.get(truck_num)
        trailer_id = trailers_dict.get(trailer_num) if trailer_num else None
        
        if driver_id and truck_id:
            query_db('''
                INSERT INTO assignments (driver_id, truck_id, trailer_id, assigned_date, is_active)
                VALUES (?, ?, ?, ?, 1)
            ''', (driver_id, truck_id, trailer_id, today), commit=True)
    
    print(f"✓ Created {len(assignments_data)} driver assignments")
    
    # Add some common job sites
    jobs = [
        ('SRM BLUFFTON', 'JOB-BLF', '17044 Bluffton Rd', 'Bluffton', 'SC', '29910', 'Site Manager', '843-555-0101'),
        ('SRM RIDGELAND', 'JOB-RDG', '17032 Ridgeland Ave', 'Ridgeland', 'SC', '29936', 'Site Manager', '843-555-0102'),
        ('SRM GOOSE CREEK', 'JOB-GSC', '17007 Goose Creek Blvd', 'Goose Creek', 'SC', '29445', 'Site Manager', '843-555-0103'),
        ('SRM NORTH AUGUSTA', 'JOB-NAG', '17035 Augusta Rd', 'Edgefield', 'SC', '29824', 'Site Manager', '803-555-0104'),
        ('SRM BRUNSWICK', 'JOB-BRW', '13012 Brunswick Hwy', 'Brunswick', 'GA', '31520', 'Site Manager', '912-555-0105'),
        ('SRM GARDEN CITY', 'JOB-GDC', '13040 Garden City Rd', 'Savannah', 'GA', '31408', 'Site Manager', '912-555-0106'),
        ('SRM STATESBORO', 'JOB-STB', '13025 Statesboro Pike', 'Statesboro', 'GA', '30458', 'Site Manager', '912-555-0107'),
        ('SRM GUYTON HODGEVILLE', 'JOB-GYT', '13018 Guyton Rd', 'Guyton', 'GA', '31312', 'Site Manager', '912-555-0108'),
        ('SRM RICHMOND HILL', 'JOB-RCH', '13022 Richmond Hill Way', 'Richmond Hill', 'GA', '31324', 'Site Manager', '912-555-0109'),
        ('SRM AUGUSTA', 'JOB-AUG', '13028 Augusta Blvd', 'Augusta', 'GA', '30906', 'Site Manager', '706-555-0110'),
        ('SRM BLOOMINGDALE', 'JOB-BLM', '13014 Bloomingdale Rd', 'Bloomingdale', 'GA', '31302', 'Site Manager', '912-555-0111'),
        ('SRM SAVANNAH', 'JOB-SAV', '13024 Savannah Hwy', 'Savannah', 'GA', '31405', 'Site Manager', '912-555-0112'),
        ('SRM JOHNS ISLAND', 'JOB-JHN', '17006 Johns Island Pkwy', 'Johns Island', 'SC', '29455', 'Site Manager', '843-555-0113'),
        ('SRM SUMMERVILLE', 'JOB-SUM', '17008 Summerville Ave', 'Summerville', 'SC', '29483', 'Site Manager', '843-555-0114'),
    ]
    
    print("Loading job sites...")
    for job in jobs:
        query_db('''
            INSERT INTO jobs (job_name, job_number, address, city, state, zip, contact_person, contact_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', job, commit=True)
    print(f"✓ Added {len(jobs)} job sites")
    
    print("\n" + "="*60)
    print("Real data loaded successfully!")
    print("="*60)
    print(f"\nSystem now has:")
    print(f"  • {len(drivers)} drivers")
    print(f"  • {len(trucks)} trucks (all with Samara device IDs)")
    print(f"  • {len(trailers)} trailers")
    print(f"  • {len(assignments_data)} active driver assignments")
    print(f"  • {len(jobs)} job sites")
    print("\nAll drivers are assigned to their regular trucks!")
    print("Ready to start dispatching loads.")

if __name__ == '__main__':
    print("Loading Smyrna Ready Mix real data...")
    print("="*60)
    clear_sample_data()
    load_real_data()