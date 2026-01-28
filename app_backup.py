"""
Smyrna Ready Mix Dispatch System
Main Flask application with database integration
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

# Routes
@app.route('/')
def dashboard():
    """Main dashboard with overview"""
    # Get today's stats
    today = datetime.date.today()
    
    stats = {
        'active_drivers': query_db('SELECT COUNT(*) as count FROM drivers WHERE status="active"', one=True)['count'],
        'active_trucks': query_db('SELECT COUNT(*) as count FROM trucks WHERE status="active"', one=True)['count'],
        'today_loads': query_db('SELECT COUNT(*) as count FROM loads WHERE load_date=?', (today,), one=True)['count'],
        'completed_loads': query_db('SELECT COUNT(*) as count FROM loads WHERE load_date=? AND status="complete"', (today,), one=True)['count'],
        'pending_loads': query_db('SELECT COUNT(*) as count FROM loads WHERE load_date=? AND status IN ("assigned", "en_route", "at_job")', (today,), one=True)['count']
    }
    
    # Get recent loads
    recent_loads = query_db('''
        SELECT l.*, d.name as driver_name, t.truck_number, j.job_name
        FROM loads l
        JOIN drivers d ON l.driver_id = d.id
        JOIN trucks t ON l.truck_id = t.id
        JOIN jobs j ON l.job_id = j.id
        WHERE l.load_date = ?
        ORDER BY l.created_at DESC
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

@app.route('/drivers/<int:driver_id>/edit', methods=['POST'])
def edit_driver(driver_id):
    """Edit driver"""
    name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email')
    employee_id = request.form.get('employee_id')
    status = request.form.get('status')
    
    query_db('''
        UPDATE drivers 
        SET name=?, phone=?, email=?, employee_id=?, status=?, updated_at=?
        WHERE id=?
    ''', (name, phone, email, employee_id, status, datetime.datetime.now(), driver_id), commit=True)
    
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
    capacity = request.form.get('capacity')
    samara_device_id = request.form.get('samara_device_id')
    
    query_db('''
        INSERT INTO trucks (truck_number, plate_number, make, model, year, capacity_tons, samara_device_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (truck_number, plate_number, make, model, year, capacity, samara_device_id), commit=True)
    
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
    capacity = request.form.get('capacity')
    
    query_db('''
        INSERT INTO trailers (trailer_number, plate_number, type, capacity_cubic_yards)
        VALUES (?, ?, ?, ?)
    ''', (trailer_number, plate_number, trailer_type, capacity), commit=True)
    
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
    """Add new driver-truck assignment"""
    driver_id = request.form.get('driver_id')
    truck_id = request.form.get('truck_id')
    trailer_id = request.form.get('trailer_id')
    
    # Deactivate previous assignments for this driver
    query_db('UPDATE assignments SET is_active=0 WHERE driver_id=? AND is_active=1', (driver_id,), commit=True)
    
    # Create new assignment
    query_db('''
        INSERT INTO assignments (driver_id, truck_id, trailer_id, assigned_date, is_active)
        VALUES (?, ?, ?, ?, 1)
    ''', (driver_id, truck_id, trailer_id, datetime.date.today()), commit=True)
    
    return redirect(url_for('assignments'))

@app.route('/dispatch')
def dispatch():
    """Main dispatch interface"""
    today = datetime.date.today()
    
    # Get all active assignments for today
    active_assignments = query_db('''
        SELECT a.*, d.name as driver_name, d.phone, t.truck_number, tr.trailer_number
        FROM assignments a
        JOIN drivers d ON a.driver_id = d.id
        JOIN trucks t ON a.truck_id = t.id
        LEFT JOIN trailers tr ON a.trailer_id = tr.id
        WHERE a.is_active = 1 AND a.assigned_date = ?
        ORDER BY d.name
    ''', (today,))
    
    # Get all jobs
    jobs = query_db('SELECT * FROM jobs WHERE status="active" ORDER BY job_name')
    
    # Get all plants
    plants = query_db('SELECT * FROM plants WHERE status="active" ORDER BY state, city, name')
    
    # Get all pickup locations
    pickup_locations = query_db('SELECT * FROM pickup_locations WHERE status="active" ORDER BY company, city, name')
    
    # Get all materials
    materials = query_db('SELECT * FROM material_types WHERE status="active" ORDER BY category, name')
    
    # Get location-material mappings
    location_materials = query_db('''
        SELECT lm.*, mt.name as material_name, mt.description
        FROM location_materials lm
        JOIN material_types mt ON lm.material_code = mt.code
        WHERE lm.status = "active"
        ORDER BY lm.pickup_location_id, mt.name
    ''')
    
    # Get today's loads by assignment
    loads_by_assignment = {}
    for assignment in active_assignments:
        loads = query_db('''
            SELECT l.*, j.job_name, j.address
            FROM loads l
            JOIN jobs j ON l.job_id = j.id
            WHERE l.driver_id = ? AND l.load_date = ?
            ORDER BY l.scheduled_time
        ''', (assignment['driver_id'], today))
        loads_by_assignment[assignment['driver_id']] = loads
    
    return render_template('dispatch.html',
                         active_assignments=active_assignments,
                         jobs=jobs,
                         plants=plants,
                         pickup_locations=pickup_locations,
                         materials=materials,
                         location_materials=location_materials,
                         loads_by_assignment=loads_by_assignment)

@app.route('/dispatch/batch', methods=['POST'])
def batch_dispatch():
    """Batch dispatch loads for multiple drivers"""
    # This will handle the 4-10 loads per driver workflow
    data = request.json
    
    for assignment in data.get('assignments', []):
        driver_id = assignment.get('driver_id')
        truck_id = assignment.get('truck_id')
        trailer_id = assignment.get('trailer_id')
        loads = assignment.get('loads', [])
        
        for load in loads:
            load_number = f"L-{datetime.date.today().strftime('%Y%m%d')}-{load.get('sequence', 0)}"
            
            query_db('''
                INSERT INTO loads (load_number, driver_id, truck_id, trailer_id, plant_id, job_id, 
                                  load_date, product_type, cubic_yards, status, scheduled_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (load_number, driver_id, truck_id, trailer_id, load.get('plant_id'),
                  load.get('job_id'), datetime.date.today(), load.get('product_type'), 
                  load.get('cubic_yards'), 'assigned', load.get('scheduled_time')), commit=True)
    
    return jsonify({'success': True, 'message': 'Batch dispatch completed'})

@app.route('/jobs')
def jobs():
    """Jobs/Projects management"""
    jobs = query_db('SELECT * FROM jobs ORDER BY job_name')
    return render_template('jobs.html', jobs=jobs)

@app.route('/jobs/add', methods=['POST'])
def add_job():
    """Add new job"""
    job_name = request.form.get('job_name')
    job_number = request.form.get('job_number')
    address = request.form.get('address')
    city = request.form.get('city')
    state = request.form.get('state')
    zip_code = request.form.get('zip')
    contact_person = request.form.get('contact_person')
    contact_phone = request.form.get('contact_phone')
    
    query_db('''
        INSERT INTO jobs (job_name, job_number, address, city, state, zip, contact_person, contact_phone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (job_name, job_number, address, city, state, zip_code, contact_person, contact_phone), commit=True)
    
    return redirect(url_for('jobs'))

@app.route('/loads')
def loads():
    """Load tracking interface"""
    today = datetime.date.today()
    loads = query_db('''
        SELECT l.*, d.name as driver_name, t.truck_number, j.job_name, j.address
        FROM loads l
        JOIN drivers d ON l.driver_id = d.id
        JOIN trucks t ON l.truck_id = t.id
        JOIN jobs j ON l.job_id = j.id
        WHERE l.load_date >= ?
        ORDER BY l.load_date DESC, l.scheduled_time
    ''', (today,))
    
    return render_template('loads.html', loads=loads)

@app.route('/loads/<int:load_id>/status', methods=['POST'])
def update_load_status(load_id):
    """Update load status"""
    status = request.json.get('status')
    latitude = request.json.get('latitude')
    longitude = request.json.get('longitude')
    location_text = request.json.get('location_text')
    
    # Update load status
    update_query = 'UPDATE loads SET status=?, updated_at=? WHERE id=?'
    update_params = [status, datetime.datetime.now(), load_id]
    
    if status == 'en_route' and not query_db('SELECT start_time FROM loads WHERE id=?', (load_id,), one=True)['start_time']:
        update_query = 'UPDATE loads SET status=?, start_time=?, updated_at=? WHERE id=?'
        update_params = [status, datetime.datetime.now(), datetime.datetime.now(), load_id]
    elif status == 'complete':
        update_query = 'UPDATE loads SET status=?, complete_time=?, updated_at=? WHERE id=?'
        update_params = [status, datetime.datetime.now(), datetime.datetime.now(), load_id]
    
    query_db(update_query, update_params, commit=True)
    
    # Add tracking event
    query_db('''
        INSERT INTO tracking_events (load_id, event_type, latitude, longitude, location_text)
        VALUES (?, ?, ?, ?, ?)
    ''', (load_id, status, latitude, longitude, location_text), commit=True)
    
    return jsonify({'success': True})

@app.route('/samara/integration')
def samara_integration():
    """Samara integration interface"""
    # This will be expanded to handle actual Samara API integration
    loads_with_tracking = query_db('''
        SELECT l.*, d.name as driver_name, t.truck_number, t.samara_device_id, j.job_name
        FROM loads l
        JOIN drivers d ON l.driver_id = d.id
        JOIN trucks t ON l.truck_id = t.id
        JOIN jobs j ON l.job_id = j.id
        WHERE l.samara_tracking_enabled = 1 AND l.load_date >= ?
        ORDER BY l.load_date DESC, l.scheduled_time
    ''', (datetime.date.today(),))
    
    return render_template('samara.html', loads=loads_with_tracking)

@app.route('/plants')
def plants():
    """Plants management page"""
    plants_list = query_db('SELECT * FROM plants ORDER BY state, city, name')
    return render_template('plants.html', plants=plants_list)

@app.route('/api/plants/<int:plant_id>/status', methods=['POST'])
def update_plant_status(plant_id):
    """Update plant status"""
    data = request.json
    new_status = data.get('status')
    
    query_db('UPDATE plants SET status = ?, updated_at = ? WHERE id = ?',
             (new_status, datetime.datetime.now(), plant_id))
    
    return jsonify({'success': True, 'message': f'Plant status updated to {new_status}'})

@app.route('/pickup-locations')
def pickup_locations():
    """Pickup locations management page"""
    pickup_list = query_db('SELECT * FROM pickup_locations ORDER BY city, name')
    return render_template('pickup_locations.html', pickup_locations=pickup_list)

@app.route('/api/pickup-locations/<int:location_id>/status', methods=['POST'])
def update_pickup_location_status(location_id):
    """Update pickup location status"""
    data = request.json
    new_status = data.get('status')
    
    query_db('UPDATE pickup_locations SET status = ?, updated_at = ? WHERE id = ?',
             (new_status, datetime.datetime.now(), location_id))
    
    return jsonify({'success': True, 'message': f'Pickup location status updated to {new_status}'})

@app.route('/ai-assistant')
def ai_assistant():
    """AI assistant interface"""
    return render_template('ai_assistant.html')

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

@app.route('/api/data')
def api_data():
    """API endpoint for data retrieval"""
    data_type = request.args.get('type')
    
    if data_type == 'drivers':
        data = query_db('SELECT * FROM drivers WHERE status="active"')
    elif data_type == 'trucks':
        data = query_db('SELECT * FROM trucks WHERE status="active"')
    elif data_type == 'plants':
        data = query_db('SELECT * FROM plants WHERE status="active" ORDER BY state, city, name')
    elif data_type == 'jobs':
        data = query_db('SELECT * FROM jobs WHERE status="active"')
    elif data_type == 'today_loads':
        data = query_db('''
            SELECT l.*, d.name as driver_name, t.truck_number, j.job_name
            FROM loads l
            JOIN drivers d ON l.driver_id = d.id
            JOIN trucks t ON l.truck_id = t.id
            JOIN jobs j ON l.job_id = j.id
            WHERE l.load_date = ?
            ORDER BY l.scheduled_time
        ''', (datetime.date.today(),))
    else:
        data = []
    
    return jsonify([dict(row) for row in data])

if __name__ == '__main__':
    # Initialize database
    if not os.path.exists(DATABASE):
        init_db()
        print("Database initialized successfully")
    
    app.run(debug=True, host='0.0.0.0', port=5000)