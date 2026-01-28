"""
Smyrna Ready Mix Dispatch System
Main Flask application with database integration
Updated for tons measurement and historical load tracking
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import datetime
from functools import wraps
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'srm-dispatch-secret-key-2024'
DATABASE = 'database/srm_dispatch.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with schema"""
    conn = get_db()
    with open('database/schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

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

def archive_load(load_id):
    """Move completed load from loads_active to loads_history"""
    conn = get_db()
    cur = conn.cursor()
    
    # Get load data
    cur.execute("SELECT * FROM loads_active WHERE id = ?", (load_id,))
    load = cur.fetchone()
    
    if load:
        # Insert into loads_history
        cur.execute('''
            INSERT INTO loads_history (
                load_number, driver_id, truck_id, trailer_id, assignment_id,
                job_id, plant_id, pickup_location_id, material_id, quantity_tons,
                status, assigned_at, en_route_at, at_job_at, delivering_at,
                completed_at, notes, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            load['load_number'], load['driver_id'], load['truck_id'], load['trailer_id'],
            load['assignment_id'], load['job_id'], load['plant_id'], load['pickup_location_id'],
            load['material_id'], load['quantity_tons'], load['status'], load['assigned_at'],
            load['en_route_at'], load['at_job_at'], load['delivering_at'], load['completed_at'],
            load['notes'], load['created_at'], load['updated_at']
        ))
        
        # Delete from loads_active
        cur.execute("DELETE FROM loads_active WHERE id = ?", (load_id,))
        
        # Update daily summary
        update_daily_summary(load['driver_id'], load['assigned_at'].date() if load['assigned_at'] else datetime.date.today())
        
        conn.commit()
    
    conn.close()

def update_daily_summary(driver_id, date):
    """Update daily driver summary with completed loads"""
    conn = get_db()
    cur = conn.cursor()
    
    # Get completed loads for this driver on this date
    cur.execute('''
        SELECT COUNT(*) as count, COALESCE(SUM(quantity_tons), 0) as total_tons
        FROM loads_history
        WHERE driver_id = ? AND DATE(created_at) = ?
    ''', (driver_id, date))
    
    result = cur.fetchone()
    
    # Insert or update daily summary
    cur.execute('''
        INSERT OR REPLACE INTO daily_driver_summary (driver_id, date, total_loads, total_tons, completed_loads)
        VALUES (?, ?, ?, ?, ?)
    ''', (driver_id, date, result['count'], result['total_tons'], result['count']))
    
    conn.commit()
    conn.close()

# Routes
@app.route('/')
def dashboard():
    """Main dashboard with overview"""
    today = datetime.date.today()
    
    stats = {
        'active_drivers': query_db('SELECT COUNT(*) as count FROM drivers WHERE status="active"', one=True)['count'],
        'active_trucks': query_db('SELECT COUNT(*) as count FROM trucks WHERE status="active"', one=True)['count'],
        'today_loads': query_db('SELECT COUNT(*) as count FROM loads_active WHERE DATE(assigned_at)=?', (today,), one=True)['count'],
        'completed_loads': query_db('SELECT COUNT(*) as count FROM loads_active WHERE DATE(assigned_at)=? AND status="complete"', (today,), one=True)['count'],
        'pending_loads': query_db('SELECT COUNT(*) as count FROM loads_active WHERE DATE(assigned_at)=? AND status IN ("assigned", "en_route", "at_job")', (today,), one=True)['count']
    }
    
    # Get recent active loads
    recent_loads = query_db('''
        SELECT l.*, d.name as driver_name, t.truck_number, j.job_name
        FROM loads_active l
        JOIN drivers d ON l.driver_id = d.id
        JOIN trucks t ON l.truck_id = t.id
        JOIN jobs j ON l.job_id = j.id
        WHERE DATE(l.assigned_at) = ?
        ORDER BY l.assigned_at DESC
        LIMIT 10
    ''', (today,))
    
    # Get active assignments
    active_assignments = query_db('''
        SELECT a.*, d.name as driver_name, t.truck_number, tr.trailer_number
        FROM assignments a
        JOIN drivers d ON a.driver_id = d.id
        JOIN trucks t ON a.truck_id = t.id
        LEFT JOIN trailers tr ON a.trailer_id = tr.id
        WHERE a.is_active = 1 AND a.assigned_date = ?
        ORDER BY d.name
    ''', (today,))
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         recent_loads=recent_loads,
                         active_assignments=active_assignments)

@app.route('/drivers')
def drivers():
    """Driver management page"""
    drivers = query_db('SELECT * FROM drivers ORDER BY name')
    return render_template('drivers.html', drivers=drivers)

@app.route('/drivers/add', methods=['POST'])
def add_driver():
    """Add new driver"""
    name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email')
    employee_id = request.form.get('employee_id')
    
    query_db('''
        INSERT INTO drivers (name, phone, email, employee_id)
        VALUES (?, ?, ?, ?)
    ''', (name, phone, email, employee_id), commit=True)
    
    return redirect(url_for('drivers'))

@app.route('/trucks')
def trucks():
    """Truck management page"""
    trucks = query_db('SELECT * FROM trucks ORDER BY truck_number')
    return render_template('trucks.html', trucks=trucks)

@app.route('/trucks/add', methods=['POST'])
def add_truck():
    """Add new truck"""
    truck_number = request.form.get('truck_number')
    plate_number = request.form.get('plate_number')
    make = request.form.get('make')
    model = request.form.get('model')
    year = request.form.get('year')
    capacity_tons = request.form.get('capacity_tons')
    samara_device_id = request.form.get('samara_device_id')
    
    query_db('''
        INSERT INTO trucks (truck_number, plate_number, make, model, year, capacity_tons, samara_device_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (truck_number, plate_number, make, model, year, capacity_tons, samara_device_id), commit=True)
    
    return redirect(url_for('trucks'))

@app.route('/trailers')
def trailers():
    """Trailer management page"""
    trailers = query_db('SELECT * FROM trailers ORDER BY trailer_number')
    return render_template('trailers.html', trailers=trailers)

@app.route('/trailers/add', methods=['POST'])
def add_trailer():
    """Add new trailer"""
    trailer_number = request.form.get('trailer_number')
    plate_number = request.form.get('plate_number')
    trailer_type = request.form.get('type')
    capacity_tons = request.form.get('capacity_tons')
    
    query_db('''
        INSERT INTO trailers (trailer_number, plate_number, type, capacity_tons)
        VALUES (?, ?, ?, ?)
    ''', (trailer_number, plate_number, trailer_type, capacity_tons), commit=True)
    
    return redirect(url_for('trailers'))

@app.route('/assignments')
def assignments():
    """Assignments management page"""
    today = datetime.date.today()
    assignments = query_db('''
        SELECT a.*, d.name as driver_name, t.truck_number, tr.trailer_number
        FROM assignments a
        JOIN drivers d ON a.driver_id = d.id
        JOIN trucks t ON a.truck_id = t.id
        LEFT JOIN trailers tr ON a.trailer_id = tr.id
        WHERE a.assigned_date >= ?
        ORDER BY a.assigned_date DESC, d.name
    ''', (today,))
    
    # Get available drivers, trucks, and trailers for the form
    drivers = query_db('SELECT * FROM drivers WHERE status="active" ORDER BY name')
    trucks = query_db('SELECT * FROM trucks WHERE status="active" ORDER BY truck_number')
    trailers = query_db('SELECT * FROM trailers WHERE status="active" ORDER BY trailer_number')
    
    return render_template('assignments.html', 
                         assignments=assignments,
                         drivers=drivers,
                         trucks=trucks,
                         trailers=trailers)

@app.route('/assignments/add', methods=['POST'])
def add_assignment():
    """Add new assignment"""
    driver_id = request.form.get('driver_id')
    truck_id = request.form.get('truck_id')
    trailer_id = request.form.get('trailer_id')
    assigned_date = request.form.get('assigned_date') or datetime.date.today()
    
    query_db('''
        INSERT INTO assignments (driver_id, truck_id, trailer_id, assigned_date)
        VALUES (?, ?, ?, ?)
    ''', (driver_id, truck_id, trailer_id, assigned_date), commit=True)
    
    return redirect(url_for('assignments'))

@app.route('/jobs')
def jobs():
    """Jobs management page"""
    jobs = query_db('SELECT * FROM jobs ORDER BY job_name')
    return render_template('jobs.html', jobs=jobs)

@app.route('/plants')
def plants():
    """Plants management page"""
    plants_list = query_db('SELECT * FROM plants ORDER BY state, city, name')
    return render_template('plants.html', plants=plants_list)

@app.route('/pickup-locations')
def pickup_locations():
    """Pickup locations management page"""
    pickup_list = query_db('SELECT * FROM pickup_locations ORDER BY city, name')
    return render_template('pickup_locations.html', pickup_locations=pickup_list)

@app.route('/materials')
def materials():
    """Materials management page"""
    materials_list = query_db('SELECT * FROM material_types ORDER BY category, name')
    
    # Get location-material mappings with location names
    location_materials = query_db('''
        SELECT lm.*, pl.name as location_name
        FROM location_materials lm
        JOIN pickup_locations pl ON lm.pickup_location_id = pl.location_id
        ORDER BY pl.name, lm.material_code
    ''')
    
    return render_template('materials.html', materials=materials_list, location_materials=location_materials)

@app.route('/jobs/add', methods=['POST'])
def add_job():
    """Add new job"""
    job_name = request.form.get('job_name')
    job_number = request.form.get('job_number')
    address = request.form.get('address')
    city = request.form.get('city')
    state = request.form.get('state')
    zip = request.form.get('zip')
    contact_name = request.form.get('contact_name')
    contact_phone = request.form.get('contact_phone')
    
    query_db('''
        INSERT INTO jobs (job_name, job_number, address, city, state, zip, contact_person, contact_phone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (job_name, job_number, address, city, state, zip, contact_name, contact_phone), commit=True)
    
    return redirect(url_for('jobs'))

@app.route('/loads')
def loads():
    """Loads tracking page"""
    status_filter = request.args.get('status')
    
    if status_filter:
        loads = query_db('''
            SELECT l.*, d.name as driver_name, t.truck_number, j.job_name
            FROM loads_active l
            JOIN drivers d ON l.driver_id = d.id
            JOIN trucks t ON l.truck_id = t.id
            JOIN jobs j ON l.job_id = j.id
            WHERE l.status = ?
            ORDER BY l.assigned_at DESC
        ''', (status_filter,))
    else:
        loads = query_db('''
            SELECT l.*, d.name as driver_name, t.truck_number, j.job_name
            FROM loads_active l
            JOIN drivers d ON l.driver_id = d.id
            JOIN trucks t ON l.truck_id = t.id
            JOIN jobs j ON l.job_id = j.id
            ORDER BY l.assigned_at DESC
        ''')
    
    return render_template('loads.html', loads=loads, status_filter=status_filter)

@app.route('/loads/update_status', methods=['POST'])
def update_load_status():
    """Update load status and archive if complete"""
    load_id = request.form.get('load_id')
    status = request.form.get('status')
    
    conn = get_db()
    cur = conn.cursor()
    
    # Update timestamp based on status
    timestamp_field = {
        'en_route': 'en_route_at',
        'at_job': 'at_job_at',
        'delivering': 'delivering_at',
        'complete': 'completed_at'
    }.get(status, 'updated_at')
    
    cur.execute(f'''
        UPDATE loads_active 
        SET status = ?, {timestamp_field} = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (status, load_id))
    
    # If load is complete, archive it
    if status == 'complete':
        archive_load(load_id)
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/dispatch')
def dispatch():
    """Dispatch page with batch dispatch functionality"""
    today = datetime.date.today()
    
    # Get active assignments for today
    assignments = query_db('''
        SELECT a.*, d.name as driver_name, t.truck_number, tr.trailer_number
        FROM assignments a
        JOIN drivers d ON a.driver_id = d.id
        JOIN trucks t ON a.truck_id = t.id
        LEFT JOIN trailers tr ON a.trailer_id = tr.id
        WHERE a.is_active = 1 AND a.assigned_date = ?
        ORDER BY d.name
    ''', (today,))
    
    # Get all jobs
    jobs = query_db('SELECT * FROM jobs WHERE status="active" ORDER BY job_name')
    
    # Get plants
    plants = query_db('SELECT * FROM plants WHERE status="active" ORDER BY name')
    
    # Get pickup locations
    pickup_locations = query_db('SELECT * FROM pickup_locations WHERE status="active" ORDER BY name')
    
    # Get material types
    materials = query_db('SELECT * FROM material_types WHERE status="active" ORDER BY name')
    
    return render_template('dispatch.html', 
                         assignments=assignments,
                         jobs=jobs,
                         plants=plants,
                         pickup_locations=pickup_locations,
                         materials=materials)

@app.route('/dispatch/batch', methods=['POST'])
def batch_dispatch():
    """Batch dispatch loads for multiple drivers"""
    assignment_ids = request.form.getlist('assignment_ids')
    job_id = request.form.get('job_id')
    plant_id = request.form.get('plant_id')
    pickup_location_id = request.form.get('pickup_location_id')
    material_id = request.form.get('material_id')
    quantity_tons = request.form.get('quantity_tons', 20.0)  # Default 20 tons
    loads_per_driver = int(request.form.get('loads_per_driver', 4))
    
    conn = get_db()
    cur = conn.cursor()
    
    for assignment_id in assignment_ids:
        # Get assignment details
        cur.execute('''
            SELECT driver_id, truck_id, trailer_id
            FROM assignments
            WHERE id = ?
        ''', (assignment_id,))
        assignment = cur.fetchone()
        
        if assignment:
            # Create multiple loads for this driver
            for i in range(loads_per_driver):
                load_number = f"{datetime.datetime.now().strftime('%Y%m%d')}-{assignment['driver_id']:03d}-{i+1:02d}"
                
                cur.execute('''
                    INSERT INTO loads_active (
                        load_number, driver_id, truck_id, trailer_id, assignment_id,
                        job_id, plant_id, pickup_location_id, material_id, quantity_tons,
                        status, assigned_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'assigned', CURRENT_TIMESTAMP)
                ''', (load_number, assignment['driver_id'], assignment['truck_id'],
                      assignment['trailer_id'], assignment_id, job_id, plant_id,
                      pickup_location_id, material_id, quantity_tons))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': f'Created {len(assignment_ids) * loads_per_driver} loads'})

@app.route('/history')
def history():
    """Historical load tracking page"""
    driver_id = request.args.get('driver_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Build query
    query = '''
        SELECT lh.*, d.name as driver_name, t.truck_number, j.job_name,
               p.name as plant_name, pl.name as pickup_location, m.name as material_name
        FROM loads_history lh
        JOIN drivers d ON lh.driver_id = d.id
        JOIN trucks t ON lh.truck_id = t.id
        JOIN jobs j ON lh.job_id = j.id
        LEFT JOIN plants p ON lh.plant_id = p.id
        LEFT JOIN pickup_locations pl ON lh.pickup_location_id = pl.id
        LEFT JOIN material_types m ON lh.material_id = m.id
        WHERE 1=1
    '''
    params = []
    
    if driver_id:
        query += ' AND lh.driver_id = ?'
        params.append(driver_id)
    
    if start_date:
        query += ' AND DATE(lh.created_at) >= ?'
        params.append(start_date)
    
    if end_date:
        query += ' AND DATE(lh.created_at) <= ?'
        params.append(end_date)
    
    query += ' ORDER BY lh.created_at DESC'
    
    loads = query_db(query, params)
    
    # Get drivers for filter
    drivers = query_db('SELECT * FROM drivers WHERE status="active" ORDER BY name')
    
    return render_template('history.html', loads=loads, drivers=drivers,
                         driver_id=driver_id, start_date=start_date, end_date=end_date)

@app.route('/history/driver/<int:driver_id>')
def driver_history(driver_id):
    """View specific driver's history"""
    driver = query_db('SELECT * FROM drivers WHERE id = ?', (driver_id,), one=True)
    
    # Get driver's daily summaries
    summaries = query_db('''
        SELECT dds.*, d.name as driver_name
        FROM daily_driver_summary dds
        JOIN drivers d ON dds.driver_id = d.id
        WHERE dds.driver_id = ?
        ORDER BY dds.date DESC
        LIMIT 30
    ''', (driver_id,))
    
    # Get recent loads for this driver
    recent_loads = query_db('''
        SELECT lh.*, j.job_name, p.name as plant_name, m.name as material_name
        FROM loads_history lh
        LEFT JOIN jobs j ON lh.job_id = j.id
        LEFT JOIN plants p ON lh.plant_id = p.id
        LEFT JOIN material_types m ON lh.material_id = m.id
        WHERE lh.driver_id = ?
        ORDER BY lh.created_at DESC
        LIMIT 50
    ''', (driver_id,))
    
    return render_template('driver_history.html', driver=driver, 
                         summaries=summaries, recent_loads=recent_loads)

@app.route('/api/driver/<int:driver_id>/summary/<date>')
def driver_daily_summary(driver_id, date):
    """API endpoint to get driver's daily summary"""
    summary = query_db('''
        SELECT dds.*, d.name as driver_name
        FROM daily_driver_summary dds
        JOIN drivers d ON dds.driver_id = d.id
        WHERE dds.driver_id = ? AND dds.date = ?
    ''', (driver_id, date), one=True)
    
    if summary:
        # Get detailed loads for this day
        loads = query_db('''
            SELECT lh.*, j.job_name, p.name as plant_name, m.name as material_name
            FROM loads_history lh
            LEFT JOIN jobs j ON lh.job_id = j.id
            LEFT JOIN plants p ON lh.plant_id = p.id
            LEFT JOIN material_types m ON lh.material_id = m.id
            WHERE lh.driver_id = ? AND DATE(lh.created_at) = ?
            ORDER BY lh.created_at ASC
        ''', (driver_id, date))
        
        return jsonify({
            'summary': dict(summary),
            'loads': [dict(load) for load in loads]
        })
    else:
        return jsonify({'error': 'No data found for this date'}), 404

@app.route('/ai-assistant')
def ai_assistant():
    """AI Assistant page"""
    return render_template('ai_assistant.html')

@app.route('/samara/integration')
def samara_integration():
    """Samsara GPS integration page"""
    return render_template('samara.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5500)