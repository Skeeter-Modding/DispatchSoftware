-- Smyrna Ready Mix Dispatch System Database Schema

-- Drivers Table
CREATE TABLE IF NOT EXISTS drivers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    employee_id TEXT UNIQUE,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trucks Table
CREATE TABLE IF NOT EXISTS trucks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    truck_number TEXT NOT NULL UNIQUE,
    plate_number TEXT,
    make TEXT,
    model TEXT,
    year INTEGER,
    capacity_tons REAL,
    samara_device_id TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trailers Table
CREATE TABLE IF NOT EXISTS trailers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trailer_number TEXT NOT NULL UNIQUE,
    plate_number TEXT,
    type TEXT,
    capacity_cubic_yards REAL,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Plants Table (SRM Concrete locations)
CREATE TABLE IF NOT EXISTS plants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plant_id TEXT UNIQUE,
    name TEXT NOT NULL,
    address TEXT,
    city TEXT,
    state TEXT,
    zip TEXT,
    phone TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Assignments Table (Links drivers to trucks and trailers)
CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    driver_id INTEGER NOT NULL,
    truck_id INTEGER NOT NULL,
    trailer_id INTEGER,
    assigned_date DATE DEFAULT CURRENT_DATE,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (driver_id) REFERENCES drivers(id),
    FOREIGN KEY (truck_id) REFERENCES trucks(id),
    FOREIGN KEY (trailer_id) REFERENCES trailers(id)
);

-- Jobs/Projects Table
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_name TEXT NOT NULL,
    job_number TEXT UNIQUE,
    address TEXT,
    city TEXT,
    state TEXT,
    zip TEXT,
    contact_person TEXT,
    contact_phone TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Loads Table
CREATE TABLE IF NOT EXISTS loads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    load_number TEXT NOT NULL,
    driver_id INTEGER NOT NULL,
    truck_id INTEGER NOT NULL,
    trailer_id INTEGER,
    plant_id INTEGER,
    job_id INTEGER NOT NULL,
    load_date DATE DEFAULT CURRENT_DATE,
    product_type TEXT,
    cubic_yards REAL,
    status TEXT DEFAULT 'assigned',
    -- Status options: assigned, en_route, at_job, delivering, complete, cancelled
    scheduled_time TIME,
    start_time TIMESTAMP,
    complete_time TIMESTAMP,
    notes TEXT,
    samara_tracking_enabled BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (driver_id) REFERENCES drivers(id),
    FOREIGN KEY (truck_id) REFERENCES trucks(id),
    FOREIGN KEY (trailer_id) REFERENCES trailers(id),
    FOREIGN KEY (plant_id) REFERENCES plants(id),
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);

-- Tracking Events Table (For Samara integration)
CREATE TABLE IF NOT EXISTS tracking_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    load_id INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    -- Event types: assigned, departed, arrived, delivering, completed
    latitude REAL,
    longitude REAL,
    location_text TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    samara_event_id TEXT,
    FOREIGN KEY (load_id) REFERENCES loads(id)
);

-- Dispatch Templates (For common routes)
CREATE TABLE IF NOT EXISTS dispatch_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_name TEXT NOT NULL,
    job_id INTEGER NOT NULL,
    product_type TEXT,
    cubic_yards REAL,
    typical_duration_minutes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_loads_driver ON loads(driver_id);
CREATE INDEX IF NOT EXISTS idx_loads_date ON loads(load_date);
CREATE INDEX IF NOT EXISTS idx_loads_status ON loads(status);
CREATE INDEX IF NOT EXISTS idx_assignments_driver ON assignments(driver_id);
CREATE INDEX IF NOT EXISTS idx_assignments_date ON assignments(assigned_date);
CREATE INDEX IF NOT EXISTS idx_tracking_load ON tracking_events(load_id);