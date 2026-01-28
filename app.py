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

        # Update daily summary - parse date from string
        assigned_at = load['assigned_at']
        if assigned_at:
            # Parse the date string (format: YYYY-MM-DD HH:MM:SS or YYYY-MM-DD)
            try:
                date_part = assigned_at.split(' ')[0] if ' ' in assigned_at else assigned_at
                update_daily_summary(load['driver_id'], date_part, conn)
            except:
                update_daily_summary(load['driver_id'], datetime.date.today().isoformat(), conn)
        else:
            update_daily_summary(load['driver_id'], datetime.date.today().isoformat(), conn)

        conn.commit()

    conn.close()

def update_daily_summary(driver_id, date, conn=None):
    """Update daily driver summary with completed loads"""
    should_close = False
    if conn is None:
        conn = get_db()
        should_close = True

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

    if should_close:
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

    # Get pending orders count
    pending_orders = query_db('SELECT COUNT(*) as count FROM orders WHERE status="pending"', one=True)
    pending_orders_count = pending_orders['count'] if pending_orders else 0

    # Format today's date
    today_date = today.strftime('%A, %B %d, %Y')

    return render_template('dashboard.html',
                         stats=stats,
                         recent_loads=recent_loads,
                         active_assignments=active_assignments,
                         today_date=today_date,
                         pending_orders=pending_orders_count)

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
                         trailers=trailers,
                         today=today.isoformat())

@app.route('/assignments/add', methods=['POST'])
def add_assignment():
    """Add new assignment"""
    driver_id = request.form.get('driver_id')
    truck_id = request.form.get('truck_id')
    trailer_id = request.form.get('trailer_id') or None
    assigned_date = request.form.get('assigned_date') or datetime.date.today()

    # Deactivate any existing assignments for this driver today
    query_db('''
        UPDATE assignments SET is_active = 0
        WHERE driver_id = ? AND assigned_date = ?
    ''', (driver_id, assigned_date), commit=True)

    query_db('''
        INSERT INTO assignments (driver_id, truck_id, trailer_id, assigned_date, is_active)
        VALUES (?, ?, ?, ?, 1)
    ''', (driver_id, truck_id, trailer_id, assigned_date), commit=True)

    return redirect(url_for('assignments'))

@app.route('/assignments/<int:assignment_id>/delete', methods=['POST'])
def delete_assignment(assignment_id):
    """Delete an assignment"""
    query_db('DELETE FROM assignments WHERE id = ?', (assignment_id,), commit=True)
    return jsonify({'success': True})

@app.route('/assignments/<int:assignment_id>/deactivate', methods=['POST'])
def deactivate_assignment(assignment_id):
    """Deactivate an assignment"""
    query_db('UPDATE assignments SET is_active = 0 WHERE id = ?', (assignment_id,), commit=True)
    return jsonify({'success': True})

@app.route('/assignments/<int:assignment_id>/activate', methods=['POST'])
def activate_assignment(assignment_id):
    """Activate an assignment"""
    query_db('UPDATE assignments SET is_active = 1 WHERE id = ?', (assignment_id,), commit=True)
    return jsonify({'success': True})

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
        SELECT lm.*, pl.name as location_name, mt.name as material_name
        FROM location_materials lm
        JOIN pickup_locations pl ON lm.pickup_location_id = pl.location_id
        JOIN material_types mt ON lm.material_code = mt.code
        ORDER BY pl.name, mt.name
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
    zip_code = request.form.get('zip')
    contact_name = request.form.get('contact_name')
    contact_phone = request.form.get('contact_phone')
    is_one_time = request.form.get('is_one_time') == 'true'

    query_db('''
        INSERT INTO jobs (job_name, job_number, address, city, state, zip, contact_person, contact_phone, is_one_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (job_name, job_number, address, city, state, zip_code, contact_name, contact_phone, is_one_time), commit=True)

    if request.headers.get('Content-Type') == 'application/json' or request.is_json:
        return jsonify({'success': True})
    return redirect(url_for('jobs'))

@app.route('/loads')
def loads():
    """Loads tracking page"""
    status_filter = request.args.get('status')

    if status_filter:
        loads_list = query_db('''
            SELECT l.*, d.name as driver_name, t.truck_number, j.job_name, j.address
            FROM loads_active l
            JOIN drivers d ON l.driver_id = d.id
            JOIN trucks t ON l.truck_id = t.id
            JOIN jobs j ON l.job_id = j.id
            WHERE l.status = ?
            ORDER BY l.assigned_at DESC
        ''', (status_filter,))
    else:
        loads_list = query_db('''
            SELECT l.*, d.name as driver_name, t.truck_number, j.job_name, j.address
            FROM loads_active l
            JOIN drivers d ON l.driver_id = d.id
            JOIN trucks t ON l.truck_id = t.id
            JOIN jobs j ON l.job_id = j.id
            ORDER BY l.assigned_at DESC
        ''')

    return render_template('loads.html', loads=loads_list, status_filter=status_filter)

# Route that matches what JavaScript calls: /loads/<id>/status
@app.route('/loads/<int:load_id>/status', methods=['POST'])
def update_load_status_by_id(load_id):
    """Update load status via JSON (matches JavaScript calls)"""
    data = request.get_json() if request.is_json else request.form
    status = data.get('status')

    conn = get_db()
    cur = conn.cursor()

    # Determine which timestamp field to update based on status
    timestamp_updates = {
        'en_route': 'en_route_at',
        'at_job': 'at_job_at',
        'delivering': 'delivering_at',
        'complete': 'completed_at'
    }

    timestamp_field = timestamp_updates.get(status)

    if timestamp_field:
        cur.execute(f'''
            UPDATE loads_active
            SET status = ?, {timestamp_field} = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, load_id))
    else:
        cur.execute('''
            UPDATE loads_active
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, load_id))

    conn.commit()
    conn.close()

    # If load is complete, archive it
    if status == 'complete':
        archive_load(load_id)

    return jsonify({'success': True})

# Keep old route for backwards compatibility
@app.route('/loads/update_status', methods=['POST'])
def update_load_status():
    """Update load status (form-based)"""
    load_id = request.form.get('load_id')
    status = request.form.get('status')

    return update_load_status_by_id(int(load_id))

@app.route('/loads/add', methods=['POST'])
def add_single_load():
    """Add a single load"""
    data = request.get_json() if request.is_json else request.form

    driver_id = data.get('driver_id')
    truck_id = data.get('truck_id')
    trailer_id = data.get('trailer_id') or None
    job_id = data.get('job_id')
    plant_id = data.get('plant_id') or None
    pickup_location_id = data.get('pickup_location_id') or None
    material_id = data.get('material_id') or None
    quantity_tons = data.get('quantity_tons', 20.0)
    notes = data.get('notes', '')

    # Generate load number
    today = datetime.datetime.now()
    load_count = query_db(
        'SELECT COUNT(*) as count FROM loads_active WHERE DATE(assigned_at) = ?',
        (today.date(),), one=True
    )['count']
    load_number = f"{today.strftime('%Y%m%d')}-{int(driver_id):03d}-{load_count + 1:02d}"

    # Get assignment_id if exists
    assignment = query_db('''
        SELECT id FROM assignments
        WHERE driver_id = ? AND truck_id = ? AND assigned_date = ? AND is_active = 1
    ''', (driver_id, truck_id, today.date()), one=True)
    assignment_id = assignment['id'] if assignment else None

    query_db('''
        INSERT INTO loads_active (
            load_number, driver_id, truck_id, trailer_id, assignment_id,
            job_id, plant_id, pickup_location_id, material_id, quantity_tons,
            status, assigned_at, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'assigned', CURRENT_TIMESTAMP, ?)
    ''', (load_number, driver_id, truck_id, trailer_id, assignment_id,
          job_id, plant_id, pickup_location_id, material_id, quantity_tons, notes), commit=True)

    if request.is_json:
        return jsonify({'success': True, 'load_number': load_number})
    return redirect(url_for('loads'))

@app.route('/dispatch')
def dispatch():
    """Dispatch page with batch dispatch functionality"""
    today = datetime.date.today()
    today_date = today.strftime('%A, %B %d, %Y')

    # Get active assignments for today
    active_assignments = query_db('''
        SELECT a.*, d.name as driver_name, d.phone, t.truck_number, tr.trailer_number
        FROM assignments a
        JOIN drivers d ON a.driver_id = d.id
        JOIN trucks t ON a.truck_id = t.id
        LEFT JOIN trailers tr ON a.trailer_id = tr.id
        WHERE a.is_active = 1 AND a.assigned_date = ?
        ORDER BY d.name
    ''', (today,))

    # Get loads grouped by driver for today
    loads_by_driver = {}
    for assignment in active_assignments:
        driver_id = assignment['driver_id']
        driver_loads = query_db('''
            SELECT l.*, j.job_name, m.name as material_name
            FROM loads_active l
            JOIN jobs j ON l.job_id = j.id
            LEFT JOIN material_types m ON l.material_id = m.id
            WHERE l.driver_id = ? AND DATE(l.assigned_at) = ?
            ORDER BY l.assigned_at
        ''', (driver_id, today))
        loads_by_driver[driver_id] = driver_loads

    # Get all jobs
    jobs = query_db('SELECT * FROM jobs WHERE status="active" ORDER BY job_name')

    # Get plants
    plants = query_db('SELECT * FROM plants WHERE status="active" ORDER BY name')

    # Get pickup locations
    pickup_locs = query_db('SELECT * FROM pickup_locations WHERE status="active" ORDER BY name')

    # Get material types
    materials = query_db('SELECT * FROM material_types WHERE status="active" ORDER BY name')

    # Get location-material mappings for JavaScript
    location_materials = query_db('''
        SELECT lm.*, pl.name as location_name, mt.name as material_name, mt.id as material_id
        FROM location_materials lm
        JOIN pickup_locations pl ON lm.pickup_location_id = pl.location_id
        JOIN material_types mt ON lm.material_code = mt.code
        ORDER BY pl.name, mt.name
    ''')

    # Get pending orders
    pending_orders = query_db('''
        SELECT o.*, j.job_name, j.address as job_address
        FROM orders o
        LEFT JOIN jobs j ON o.job_id = j.id
        WHERE o.status = 'pending'
        ORDER BY o.created_at DESC
    ''')

    return render_template('dispatch.html',
                         active_assignments=active_assignments,
                         loads_by_assignment=loads_by_driver,
                         jobs=jobs,
                         plants=plants,
                         pickup_locations=pickup_locs,
                         materials=materials,
                         location_materials=location_materials,
                         today_date=today_date,
                         pending_orders=pending_orders)

@app.route('/dispatch/batch', methods=['POST'])
def batch_dispatch():
    """Batch dispatch loads for multiple drivers - handles both JSON and form data"""
    # Handle JSON data from JavaScript
    if request.is_json:
        data = request.get_json()
        assignments_data = data.get('assignments', [])

        conn = get_db()
        cur = conn.cursor()
        total_loads = 0

        for driver_data in assignments_data:
            driver_id = driver_data.get('driver_id')
            truck_id = driver_data.get('truck_id')
            trailer_id = driver_data.get('trailer_id') or None
            loads = driver_data.get('loads', [])

            for i, load_info in enumerate(loads):
                load_number = f"{datetime.datetime.now().strftime('%Y%m%d')}-{int(driver_id):03d}-{i+1:02d}"

                cur.execute('''
                    INSERT INTO loads_active (
                        load_number, driver_id, truck_id, trailer_id,
                        job_id, plant_id, pickup_location_id, material_id, quantity_tons,
                        status, assigned_at, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'assigned', CURRENT_TIMESTAMP, ?)
                ''', (
                    load_number, driver_id, truck_id, trailer_id,
                    load_info.get('job_id'),
                    load_info.get('plant_id'),
                    load_info.get('pickup_location_id'),
                    load_info.get('material_id'),
                    load_info.get('quantity_tons', 20.0),
                    load_info.get('notes', '')
                ))
                total_loads += 1

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': f'Created {total_loads} loads'})

    # Handle form data (original implementation)
    assignment_ids = request.form.getlist('assignment_ids')
    job_id = request.form.get('job_id')
    plant_id = request.form.get('plant_id') or None
    pickup_location_id = request.form.get('pickup_location_id') or None
    material_id = request.form.get('material_id') or None
    quantity_tons = request.form.get('quantity_tons', 20.0)
    loads_per_driver = int(request.form.get('loads_per_driver', 4))

    conn = get_db()
    cur = conn.cursor()

    for assignment_id in assignment_ids:
        cur.execute('''
            SELECT driver_id, truck_id, trailer_id
            FROM assignments
            WHERE id = ?
        ''', (assignment_id,))
        assignment = cur.fetchone()

        if assignment:
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

# ============ ORDERS MANAGEMENT ============

@app.route('/orders')
def orders():
    """Orders management page - orders that haven't been assigned to drivers yet"""
    status_filter = request.args.get('status', 'pending')
    today = datetime.date.today()

    orders_list = query_db('''
        SELECT o.*, j.job_name, j.address as job_address, j.city as job_city,
               m.name as material_name, p.name as plant_name
        FROM orders o
        LEFT JOIN jobs j ON o.job_id = j.id
        LEFT JOIN material_types m ON o.material_id = m.id
        LEFT JOIN plants p ON o.plant_id = p.id
        WHERE o.status = ? OR ? = 'all'
        ORDER BY o.priority DESC, o.created_at ASC
    ''', (status_filter, status_filter))

    # Get data for forms
    jobs = query_db('SELECT * FROM jobs WHERE status="active" ORDER BY job_name')
    materials = query_db('SELECT * FROM material_types WHERE status="active" ORDER BY name')
    plants = query_db('SELECT * FROM plants WHERE status="active" ORDER BY name')
    pickup_locations = query_db('SELECT * FROM pickup_locations WHERE status="active" ORDER BY name')

    # Get active assignments for assigning orders to drivers
    active_assignments = query_db('''
        SELECT a.*, d.name as driver_name, d.phone, t.truck_number, tr.trailer_number
        FROM assignments a
        JOIN drivers d ON a.driver_id = d.id
        JOIN trucks t ON a.truck_id = t.id
        LEFT JOIN trailers tr ON a.trailer_id = tr.id
        WHERE a.is_active = 1 AND a.assigned_date = ?
        ORDER BY d.name
    ''', (today,))

    return render_template('orders.html',
                         orders=orders_list,
                         jobs=jobs,
                         materials=materials,
                         plants=plants,
                         pickup_locations=pickup_locations,
                         active_assignments=active_assignments,
                         status_filter=status_filter)

@app.route('/orders/add', methods=['POST'])
def add_order():
    """Add a new order (without driver assignment)"""
    data = request.get_json() if request.is_json else request.form

    job_id = data.get('job_id')
    material_id = data.get('material_id') or None
    plant_id = data.get('plant_id') or None
    pickup_location_id = data.get('pickup_location_id') or None
    quantity_tons = data.get('quantity_tons', 20.0)
    priority = data.get('priority', 'normal')
    notes = data.get('notes', '')
    customer_name = data.get('customer_name', '')
    customer_phone = data.get('customer_phone', '')

    # Handle one-time customer address
    is_one_time = data.get('is_one_time') == 'true' or data.get('is_one_time') == True
    if is_one_time and not job_id:
        # Create a one-time job entry
        one_time_address = data.get('one_time_address', '')
        one_time_city = data.get('one_time_city', '')
        one_time_state = data.get('one_time_state', 'GA')

        job_id = query_db('''
            INSERT INTO jobs (job_name, address, city, state, contact_person, contact_phone, is_one_time, status)
            VALUES (?, ?, ?, ?, ?, ?, 1, 'active')
        ''', (f"One-Time: {customer_name or one_time_address[:30]}",
              one_time_address, one_time_city, one_time_state,
              customer_name, customer_phone), commit=True)

    # Generate order number
    today = datetime.datetime.now()
    order_count = query_db(
        'SELECT COUNT(*) as count FROM orders WHERE DATE(created_at) = ?',
        (today.date(),), one=True
    )['count']
    order_number = f"ORD-{today.strftime('%Y%m%d')}-{order_count + 1:04d}"

    query_db('''
        INSERT INTO orders (
            order_number, job_id, material_id, plant_id, pickup_location_id,
            quantity_tons, priority, notes, customer_name, customer_phone, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
    ''', (order_number, job_id, material_id, plant_id, pickup_location_id,
          quantity_tons, priority, notes, customer_name, customer_phone), commit=True)

    if request.is_json:
        return jsonify({'success': True, 'order_number': order_number})
    return redirect(url_for('orders'))

@app.route('/orders/<int:order_id>/assign', methods=['POST'])
def assign_order(order_id):
    """Assign an order to a driver"""
    data = request.get_json() if request.is_json else request.form

    driver_id = data.get('driver_id')
    truck_id = data.get('truck_id')
    trailer_id = data.get('trailer_id') or None

    # Get order details
    order = query_db('SELECT * FROM orders WHERE id = ?', (order_id,), one=True)

    if not order:
        return jsonify({'success': False, 'error': 'Order not found'}), 404

    # Create load from order
    today = datetime.datetime.now()
    load_count = query_db(
        'SELECT COUNT(*) as count FROM loads_active WHERE DATE(assigned_at) = ?',
        (today.date(),), one=True
    )['count']
    load_number = f"{today.strftime('%Y%m%d')}-{int(driver_id):03d}-{load_count + 1:02d}"

    query_db('''
        INSERT INTO loads_active (
            load_number, driver_id, truck_id, trailer_id,
            job_id, plant_id, pickup_location_id, material_id, quantity_tons,
            status, assigned_at, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'assigned', CURRENT_TIMESTAMP, ?)
    ''', (load_number, driver_id, truck_id, trailer_id,
          order['job_id'], order['plant_id'], order['pickup_location_id'],
          order['material_id'], order['quantity_tons'], order['notes']), commit=True)

    # Update order status
    query_db('UPDATE orders SET status = "assigned" WHERE id = ?', (order_id,), commit=True)

    return jsonify({'success': True, 'load_number': load_number})

@app.route('/orders/<int:order_id>/delete', methods=['POST'])
def delete_order(order_id):
    """Delete an order"""
    query_db('DELETE FROM orders WHERE id = ?', (order_id,), commit=True)
    return jsonify({'success': True})

# ============ ONE-TIME CUSTOMER ============

@app.route('/api/one-time-job', methods=['POST'])
def create_one_time_job():
    """Create a one-time job/customer address"""
    data = request.get_json()

    job_name = data.get('job_name', f"One-Time Customer")
    address = data.get('address')
    city = data.get('city')
    state = data.get('state', 'GA')
    zip_code = data.get('zip', '')
    contact_name = data.get('contact_name', '')
    contact_phone = data.get('contact_phone', '')

    job_id = query_db('''
        INSERT INTO jobs (job_name, address, city, state, zip, contact_person, contact_phone, is_one_time, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1, 'active')
    ''', (job_name, address, city, state, zip_code, contact_name, contact_phone), commit=True)

    return jsonify({'success': True, 'job_id': job_id})

@app.route('/ai-assistant')
def ai_assistant():
    """AI Assistant page"""
    return render_template('ai_assistant.html')

@app.route('/samara/integration')
def samara_integration():
    """Samsara GPS integration page"""
    return render_template('samara.html')

# ============ DRIVER-TRUCK AUTO-ASSIGNMENT ============

@app.route('/driver-defaults')
def driver_defaults():
    """Manage default driver-truck assignments"""
    defaults = query_db('''
        SELECT dtd.*, d.name as driver_name, t.truck_number, tr.trailer_number
        FROM driver_truck_defaults dtd
        JOIN drivers d ON dtd.driver_id = d.id
        JOIN trucks t ON dtd.truck_id = t.id
        LEFT JOIN trailers tr ON dtd.trailer_id = tr.id
        WHERE dtd.is_active = 1
        ORDER BY d.name
    ''')

    # Get unassigned drivers
    assigned_driver_ids = [d['driver_id'] for d in defaults]
    all_drivers = query_db('SELECT * FROM drivers WHERE status="active" ORDER BY name')
    unassigned_drivers = [d for d in all_drivers if d['id'] not in assigned_driver_ids]

    trucks = query_db('SELECT * FROM trucks WHERE status="active" ORDER BY truck_number')
    trailers = query_db('SELECT * FROM trailers WHERE status="active" ORDER BY trailer_number')

    return render_template('driver_defaults.html',
                         defaults=defaults,
                         unassigned_drivers=unassigned_drivers,
                         drivers=all_drivers,
                         trucks=trucks,
                         trailers=trailers)

@app.route('/driver-defaults/add', methods=['POST'])
def add_driver_default():
    """Add or update driver-truck default"""
    data = request.get_json() if request.is_json else request.form

    driver_id = data.get('driver_id')
    truck_id = data.get('truck_id')
    trailer_id = data.get('trailer_id') or None

    # Upsert - update if exists, insert if not
    existing = query_db('SELECT id FROM driver_truck_defaults WHERE driver_id = ?', (driver_id,), one=True)

    if existing:
        query_db('''
            UPDATE driver_truck_defaults
            SET truck_id = ?, trailer_id = ?, updated_at = CURRENT_TIMESTAMP
            WHERE driver_id = ?
        ''', (truck_id, trailer_id, driver_id), commit=True)
    else:
        query_db('''
            INSERT INTO driver_truck_defaults (driver_id, truck_id, trailer_id)
            VALUES (?, ?, ?)
        ''', (driver_id, truck_id, trailer_id), commit=True)

    if request.is_json:
        return jsonify({'success': True})
    return redirect(url_for('driver_defaults'))

@app.route('/driver-defaults/<int:default_id>/delete', methods=['POST'])
def delete_driver_default(default_id):
    """Delete driver-truck default"""
    query_db('DELETE FROM driver_truck_defaults WHERE id = ?', (default_id,), commit=True)
    return jsonify({'success': True})

@app.route('/assignments/auto-create', methods=['POST'])
def auto_create_assignments():
    """Auto-create today's assignments from driver defaults"""
    today = datetime.date.today()

    # Get all active driver defaults
    defaults = query_db('''
        SELECT dtd.*, d.name as driver_name
        FROM driver_truck_defaults dtd
        JOIN drivers d ON dtd.driver_id = d.id
        WHERE dtd.is_active = 1 AND d.status = 'active'
    ''')

    created = 0
    for default in defaults:
        # Check if assignment already exists for today
        existing = query_db('''
            SELECT id FROM assignments
            WHERE driver_id = ? AND assigned_date = ?
        ''', (default['driver_id'], today), one=True)

        if not existing:
            query_db('''
                INSERT INTO assignments (driver_id, truck_id, trailer_id, assigned_date, is_active)
                VALUES (?, ?, ?, ?, 1)
            ''', (default['driver_id'], default['truck_id'], default['trailer_id'], today), commit=True)
            created += 1

    return jsonify({'success': True, 'created': created, 'message': f'Created {created} assignments'})

# ============ COST FACTORS ============

@app.route('/cost-factors')
def cost_factors():
    """View and manage cost factors for AI optimization"""
    factors = query_db('SELECT * FROM cost_factors ORDER BY factor_name')
    return render_template('cost_factors.html', factors=factors)

@app.route('/cost-factors/update', methods=['POST'])
def update_cost_factor():
    """Update a cost factor"""
    data = request.get_json() if request.is_json else request.form

    factor_name = data.get('factor_name')
    factor_value = float(data.get('factor_value'))

    query_db('''
        UPDATE cost_factors
        SET factor_value = ?, updated_at = CURRENT_TIMESTAMP
        WHERE factor_name = ?
    ''', (factor_value, factor_name), commit=True)

    return jsonify({'success': True})

# ============ AI DISPATCH OPTIMIZATION ============

def get_cost_factors():
    """Get all cost factors as a dictionary"""
    factors = query_db('SELECT factor_name, factor_value FROM cost_factors')
    return {f['factor_name']: f['factor_value'] for f in factors}

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula (returns miles)"""
    import math
    R = 3959  # Earth's radius in miles

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c

def estimate_delivery_costs(distance_miles, quantity_tons, costs):
    """Estimate costs for a delivery"""
    # Fuel cost (round trip)
    fuel_gallons = (distance_miles * 2) / costs.get('fuel_mpg', 6.0)
    fuel_cost = fuel_gallons * costs.get('fuel_cost_per_gallon', 3.50)

    # Time estimate
    drive_time_hours = (distance_miles * 2) / costs.get('average_speed_mph', 35.0)
    load_time_hours = (costs.get('load_time_minutes', 20) + costs.get('unload_time_minutes', 15)) / 60

    total_hours = drive_time_hours + load_time_hours

    # Labor and truck costs
    driver_cost = total_hours * costs.get('driver_hourly_rate', 25.0)
    truck_cost = total_hours * costs.get('truck_hourly_cost', 15.0)

    total_cost = fuel_cost + driver_cost + truck_cost

    return {
        'fuel_cost': round(fuel_cost, 2),
        'driver_cost': round(driver_cost, 2),
        'truck_cost': round(truck_cost, 2),
        'total_cost': round(total_cost, 2),
        'estimated_hours': round(total_hours, 2),
        'distance_miles': round(distance_miles, 1)
    }

@app.route('/api/ai/optimize', methods=['POST'])
def ai_optimize_dispatch():
    """AI optimization endpoint - recommends best driver/plant for orders"""
    data = request.get_json()
    order_ids = data.get('order_ids', [])

    if not order_ids:
        # Get all pending orders
        pending = query_db('SELECT id FROM orders WHERE status = "pending"')
        order_ids = [o['id'] for o in pending]

    costs = get_cost_factors()
    recommendations = []

    # Get today's available drivers (those with assignments)
    today = datetime.date.today()
    available_drivers = query_db('''
        SELECT a.*, d.name as driver_name, t.truck_number, t.capacity_tons
        FROM assignments a
        JOIN drivers d ON a.driver_id = d.id
        JOIN trucks t ON a.truck_id = t.id
        WHERE a.is_active = 1 AND a.assigned_date = ?
    ''', (today,))

    # Get plants with coordinates (we'll use city-based estimates)
    plants = query_db('SELECT * FROM plants WHERE status = "active"')

    for order_id in order_ids:
        order = query_db('SELECT o.*, j.city as job_city, j.state as job_state FROM orders o LEFT JOIN jobs j ON o.job_id = j.id WHERE o.id = ?', (order_id,), one=True)

        if not order:
            continue

        best_recommendation = None
        best_score = -1

        for driver in available_drivers:
            # Count driver's current loads for today
            current_loads = query_db('''
                SELECT COUNT(*) as count FROM loads_active
                WHERE driver_id = ? AND DATE(assigned_at) = ?
            ''', (driver['driver_id'], today), one=True)['count']

            # Prefer drivers with fewer loads (capacity-based)
            load_score = max(0, 10 - current_loads) / 10  # 0-1 score

            for plant in plants:
                # Estimate distance based on cities (simplified)
                # In production, you'd use actual coordinates or a mapping API
                base_distance = 25  # Default estimate in miles

                # Adjust based on same state
                if order['job_state'] and plant['state'] == order['job_state']:
                    base_distance *= 0.7  # Closer if same state

                # Calculate costs
                cost_estimate = estimate_delivery_costs(
                    base_distance,
                    order['quantity_tons'] or 20,
                    costs
                )

                # Calculate score (lower cost = higher score)
                cost_score = max(0, 1 - (cost_estimate['total_cost'] / 500))  # Normalize

                # Combined score
                total_score = (load_score * 0.4) + (cost_score * 0.6)

                if total_score > best_score:
                    best_score = total_score
                    best_recommendation = {
                        'order_id': order_id,
                        'order_number': order['order_number'],
                        'driver_id': driver['driver_id'],
                        'driver_name': driver['driver_name'],
                        'truck_id': driver['truck_id'],
                        'truck_number': driver['truck_number'],
                        'plant_id': plant['id'],
                        'plant_name': plant['name'],
                        'estimated_distance': cost_estimate['distance_miles'],
                        'estimated_cost': cost_estimate['total_cost'],
                        'estimated_hours': cost_estimate['estimated_hours'],
                        'confidence': round(total_score * 100, 1),
                        'reasoning': f"Driver has {current_loads} loads today. Est. {cost_estimate['distance_miles']} miles, ${cost_estimate['total_cost']} cost."
                    }

        if best_recommendation:
            recommendations.append(best_recommendation)

            # Save recommendation to database
            query_db('''
                INSERT INTO ai_recommendations (
                    order_id, recommended_driver_id, recommended_truck_id,
                    recommended_plant_id, estimated_distance_miles,
                    estimated_time_minutes, estimated_fuel_cost, estimated_profit,
                    confidence_score, reasoning
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                order_id,
                best_recommendation['driver_id'],
                best_recommendation['truck_id'],
                best_recommendation['plant_id'],
                best_recommendation['estimated_distance'],
                best_recommendation['estimated_hours'] * 60,
                best_recommendation['estimated_cost'] * 0.3,  # ~30% is fuel
                0,  # Profit calculation would need material pricing
                best_recommendation['confidence'],
                best_recommendation['reasoning']
            ), commit=True)

    return jsonify({
        'success': True,
        'recommendations': recommendations,
        'count': len(recommendations)
    })

@app.route('/api/ai/apply-recommendation', methods=['POST'])
def apply_ai_recommendation():
    """Apply an AI recommendation - assign the order to the recommended driver"""
    data = request.get_json()

    order_id = data.get('order_id')
    driver_id = data.get('driver_id')
    truck_id = data.get('truck_id')
    plant_id = data.get('plant_id')

    # Get order details
    order = query_db('SELECT * FROM orders WHERE id = ?', (order_id,), one=True)

    if not order:
        return jsonify({'success': False, 'error': 'Order not found'}), 404

    # Create load from order
    today = datetime.datetime.now()
    load_count = query_db(
        'SELECT COUNT(*) as count FROM loads_active WHERE DATE(assigned_at) = ?',
        (today.date(),), one=True
    )['count']
    load_number = f"{today.strftime('%Y%m%d')}-{int(driver_id):03d}-{load_count + 1:02d}"

    query_db('''
        INSERT INTO loads_active (
            load_number, driver_id, truck_id,
            job_id, plant_id, pickup_location_id, material_id, quantity_tons,
            status, assigned_at, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'assigned', CURRENT_TIMESTAMP, ?)
    ''', (load_number, driver_id, truck_id,
          order['job_id'], plant_id or order['plant_id'], order['pickup_location_id'],
          order['material_id'], order['quantity_tons'], order['notes']), commit=True)

    # Update order status
    query_db('UPDATE orders SET status = "assigned" WHERE id = ?', (order_id,), commit=True)

    # Update recommendation status
    query_db('''
        UPDATE ai_recommendations SET status = "applied"
        WHERE order_id = ? AND status = "pending"
    ''', (order_id,), commit=True)

    return jsonify({'success': True, 'load_number': load_number})

@app.route('/api/ai/recommendations')
def get_ai_recommendations():
    """Get recent AI recommendations"""
    recommendations = query_db('''
        SELECT ar.*, o.order_number, d.name as driver_name,
               t.truck_number, p.name as plant_name
        FROM ai_recommendations ar
        JOIN orders o ON ar.order_id = o.id
        JOIN drivers d ON ar.recommended_driver_id = d.id
        JOIN trucks t ON ar.recommended_truck_id = t.id
        LEFT JOIN plants p ON ar.recommended_plant_id = p.id
        WHERE ar.status = 'pending'
        ORDER BY ar.confidence_score DESC
    ''')

    return jsonify({
        'success': True,
        'recommendations': [dict(r) for r in recommendations]
    })

# ============ PLANT MATERIALS ============

@app.route('/plant-materials')
def plant_materials():
    """View materials available at each plant"""
    materials_by_plant = query_db('''
        SELECT pm.*, p.name as plant_name, p.city, p.state, m.name as material_name, m.code
        FROM plant_materials pm
        JOIN plants p ON pm.plant_id = p.id
        JOIN material_types m ON pm.material_id = m.id
        WHERE pm.is_available = 1
        ORDER BY p.name, m.name
    ''')

    plants = query_db('SELECT * FROM plants WHERE status="active" ORDER BY name')
    materials = query_db('SELECT * FROM material_types WHERE status="active" ORDER BY name')

    return render_template('plant_materials.html',
                         materials_by_plant=materials_by_plant,
                         plants=plants,
                         materials=materials)

# ============ DATABASE INITIALIZATION ============

def ensure_tables_exist():
    """Ensure all required tables exist"""
    conn = get_db()
    cur = conn.cursor()

    # Check if orders table exists, create if not
    cur.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT UNIQUE,
            job_id INTEGER,
            material_id INTEGER,
            plant_id INTEGER,
            pickup_location_id INTEGER,
            quantity_tons REAL DEFAULT 20.0,
            priority TEXT DEFAULT 'normal',
            notes TEXT,
            customer_name TEXT,
            customer_phone TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs(id),
            FOREIGN KEY (material_id) REFERENCES material_types(id),
            FOREIGN KEY (plant_id) REFERENCES plants(id)
        )
    ''')

    # Add is_one_time column to jobs if it doesn't exist
    try:
        cur.execute('ALTER TABLE jobs ADD COLUMN is_one_time BOOLEAN DEFAULT 0')
    except:
        pass  # Column already exists

    conn.commit()
    conn.close()

# Run table check on startup
ensure_tables_exist()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5500)
