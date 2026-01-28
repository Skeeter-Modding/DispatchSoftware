"""
Initialize Smyrna Ready Mix Dispatch System with sample data
"""

import sqlite3
import os
from datetime import datetime, date, timedelta

DATABASE = 'database/srm_dispatch.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def query_db(query, args=(), one=False, commit=False):
    """Helper function for database queries"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, args)
    
    if commit:
        conn.commit()
        result = cur.lastrowid
    else:
        result = cur.fetchone() if one else cur.fetchall()
    
    conn.close()
    return result

def init_sample_data():
    """Initialize database with sample data"""
    print("Initializing sample data...")
    
    # Sample Drivers
    drivers = [
        ('John Smith', '555-0101', 'john.smith@email.com', 'EMP001'),
        ('Michael Johnson', '555-0102', 'mjohnson@email.com', 'EMP002'),
        ('David Williams', '555-0103', 'dwilliams@email.com', 'EMP003'),
        ('Robert Brown', '555-0104', 'rbrown@email.com', 'EMP004'),
        ('James Davis', '555-0105', 'jdavis@email.com', 'EMP005'),
    ]
    
    for driver in drivers:
        query_db('''
            INSERT OR IGNORE INTO drivers (name, phone, email, employee_id)
            VALUES (?, ?, ?, ?)
        ''', driver, commit=True)
    
    print(f"✓ Added {len(drivers)} sample drivers")
    
    # Sample Trucks
    trucks = [
        ('TRK-001', 'ABC-1234', 'Mack', 'Granite', 2020, 20, 'SAMARA-001'),
        ('TRK-002', 'ABC-1235', 'Peterbilt', '379', 2019, 22, 'SAMARA-002'),
        ('TRK-003', 'ABC-1236', 'Kenworth', 'W900', 2021, 21, 'SAMARA-003'),
        ('TRK-004', 'ABC-1237', 'Freightliner', 'Cascadia', 2020, 20, 'SAMARA-004'),
        ('TRK-005', 'ABC-1238', 'International', 'Lonestar', 2022, 23, 'SAMARA-005'),
    ]
    
    for truck in trucks:
        query_db('''
            INSERT OR IGNORE INTO trucks (truck_number, plate_number, make, model, year, capacity_tons, samara_device_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', truck, commit=True)
    
    print(f"✓ Added {len(trucks)} sample trucks")
    
    # Sample Trailers
    trailers = [
        ('TRL-001', 'TRL-1234', 'dump', 10),
        ('TRL-002', 'TRL-1235', 'dump', 12),
        ('TRL-003', 'TRL-1236', 'dump', 10),
        ('TRL-004', 'TRL-1237', 'dump', 12),
        ('TRL-005', 'TRL-1238', 'dump', 10),
    ]
    
    for trailer in trailers:
        query_db('''
            INSERT OR IGNORE INTO trailers (trailer_number, plate_number, type, capacity_cubic_yards)
            VALUES (?, ?, ?, ?)
        ''', trailer, commit=True)
    
    print(f"✓ Added {len(trailers)} sample trailers")
    
    # Sample Jobs
    jobs = [
        ('Downtown Office Complex', 'JOB-001', '123 Main St', 'Atlanta', 'GA', '30303', 'John Doe', '555-0201'),
        ('Highway Bridge Project', 'JOB-002', '456 Highway 85', 'Smyrna', 'GA', '30080', 'Jane Smith', '555-0202'),
        ('Shopping Mall Construction', 'JOB-003', '789 Commerce Blvd', 'Marietta', 'GA', '30060', 'Bob Wilson', '555-0203'),
        ('Residential Development', 'JOB-004', '321 Oak Lane', 'Canton', 'GA', '30114', 'Sarah Johnson', '555-0204'),
        ('School Expansion', 'JOB-005', '654 School Rd', 'Kennesaw', 'GA', '30152', 'Mike Brown', '555-0205'),
    ]
    
    for job in jobs:
        query_db('''
            INSERT OR IGNORE INTO jobs (job_name, job_number, address, city, state, zip, contact_person, contact_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', job, commit=True)
    
    print(f"✓ Added {len(jobs)} sample jobs")
    
    # Create today's assignments
    today = date.today()
    
    # Get IDs for creating assignments
    drivers_list = query_db('SELECT id FROM drivers ORDER BY id')
    trucks_list = query_db('SELECT id FROM trucks ORDER BY id')
    trailers_list = query_db('SELECT id FROM trailers ORDER BY id')
    jobs_list = query_db('SELECT id FROM jobs ORDER BY id')
    
    # Create assignments (driver + truck + trailer)
    for i in range(min(len(drivers_list), 5)):
        query_db('''
            INSERT OR IGNORE INTO assignments (driver_id, truck_id, trailer_id, assigned_date, is_active)
            VALUES (?, ?, ?, ?, 1)
        ''', (drivers_list[i]['id'], trucks_list[i]['id'], trailers_list[i]['id'], today), commit=True)
    
    print(f"✓ Created 5 active driver assignments for today")
    
    # Create some sample loads for today
    assignments = query_db('SELECT * FROM assignments WHERE assigned_date = ? AND is_active = 1', (today,))
    
    load_counter = 1
    for assignment in assignments:
        # Create 4-8 loads per driver
        num_loads = 4 + (load_counter % 5)
        
        for load_num in range(1, num_loads + 1):
            load_number = f"L-{today.strftime('%Y%m%d')}-{load_counter:03d}"
            
            # Alternate between jobs
            job_id = jobs_list[load_num % len(jobs_list)]['id']
            
            # Set scheduled time starting from 7:00 AM with 45 min intervals
            hour = 7 + ((load_num - 1) // 4)
            minute = ((load_num - 1) % 4) * 45
            scheduled_time = f"{hour:02d}:{minute:02d}"
            
            # Vary status based on time of day
            status = 'assigned'
            if load_num <= 2:
                status = 'complete'
            elif load_num == 3:
                status = 'delivering'
            elif load_num == 4:
                status = 'en_route'
            
            # Set times based on status
            start_time = None
            complete_time = None
            if status in ['delivering', 'complete']:
                start_time = datetime.now() - timedelta(hours=1)
            if status == 'complete':
                complete_time = datetime.now() - timedelta(minutes=30)
            
            query_db('''
                INSERT OR IGNORE INTO loads 
                (load_number, driver_id, truck_id, trailer_id, job_id, load_date, 
                 product_type, cubic_yards, status, scheduled_time, start_time, complete_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (load_number, assignment['driver_id'], assignment['truck_id'], assignment['trailer_id'],
                  job_id, today, 'Ready Mix', 8 + (load_num % 3), status, 
                  scheduled_time, start_time, complete_time), commit=True)
            
            load_counter += 1
    
    print(f"✓ Created {load_counter - 1} sample loads for today")
    
    # Add some tracking events
    loads = query_db('SELECT id, status FROM loads WHERE load_date = ? AND status != "assigned"', (today,))
    
    for load in loads:
        if load['status'] == 'complete':
            query_db('''
                INSERT INTO tracking_events (load_id, event_type, location_text, timestamp)
                VALUES (?, 'assigned', 'Dispatch Yard', ?)
            ''', (load['id'], datetime.now() - timedelta(hours=3)), commit=True)
            query_db('''
                INSERT INTO tracking_events (load_id, event_type, location_text, timestamp)
                VALUES (?, 'en_route', 'En route to job site', ?)
            ''', (load['id'], datetime.now() - timedelta(hours=2)), commit=True)
            query_db('''
                INSERT INTO tracking_events (load_id, event_type, location_text, timestamp)
                VALUES (?, 'complete', 'Job site - delivered', ?)
            ''', (load['id'], datetime.now() - timedelta(minutes=30)), commit=True)
        elif load['status'] == 'delivering':
            query_db('''
                INSERT INTO tracking_events (load_id, event_type, location_text, timestamp)
                VALUES (?, 'assigned', 'Dispatch Yard', ?)
            ''', (load['id'], datetime.now() - timedelta(hours=2)), commit=True)
            query_db('''
                INSERT INTO tracking_events (load_id, event_type, location_text, timestamp)
                VALUES (?, 'en_route', 'En route to job site', ?)
            ''', (load['id'], datetime.now() - timedelta(hours=1)), commit=True)
        elif load['status'] == 'en_route':
            query_db('''
                INSERT INTO tracking_events (load_id, event_type, location_text, timestamp)
                VALUES (?, 'assigned', 'Dispatch Yard', ?)
            ''', (load['id'], datetime.now() - timedelta(minutes=30)), commit=True)
    
    print(f"✓ Added sample tracking events")
    
    print("\n" + "="*50)
    print("Sample data initialization complete!")
    print("="*50)
    print("\nSystem ready with:")
    print(f"  • {len(drivers)} drivers")
    print(f"  • {len(trucks)} trucks (with Samara devices)")
    print(f"  • {len(trailers)} trailers")
    print(f"  • {len(jobs)} active jobs")
    print(f"  • 5 driver assignments for today")
    print(f"  • {load_counter - 1} loads scheduled")
    print("\nYou can now start the application with: python app.py")
    print("Then visit: http://localhost:5000")

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        print("Database not found. Please run the main app first to create the database.")
    else:
        init_sample_data()