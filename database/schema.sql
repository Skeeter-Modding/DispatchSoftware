-- Smyrna Ready Mix Dispatch System Database Schema

-- Drivers Table (Enhanced for AI Dispatch)
CREATE TABLE IF NOT EXISTS drivers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    employee_id TEXT UNIQUE,
    -- AI Knowledge Fields
    home_location TEXT,                   -- Plant name where driver parks
    home_city TEXT,                       -- City for distance calculations
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pickup Locations Table (Quarries, suppliers, etc.)
CREATE TABLE IF NOT EXISTS pickup_locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    supplier_name TEXT,
    address TEXT,
    city TEXT,
    state TEXT DEFAULT 'GA',
    zip TEXT,
    latitude REAL,
    longitude REAL,
    phone TEXT,
    contact_name TEXT,
    material_types TEXT,                  -- JSON array of available materials
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Material Types Table
CREATE TABLE IF NOT EXISTS material_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,            -- e.g., '57', '89', 'SAND'
    name TEXT NOT NULL,
    category TEXT,                        -- 'stone', 'sand', 'gravel', 'fill'
    density_tons_per_cy REAL DEFAULT 1.4, -- Tons per cubic yard
    typical_load_tons REAL DEFAULT 22,
    notes TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default material types
INSERT OR IGNORE INTO material_types (code, name, category, density_tons_per_cy, typical_load_tons) VALUES
    ('57', '#57 Stone', 'stone', 1.4, 22),
    ('67', '#67 Stone', 'stone', 1.4, 22),
    ('89', '#89 Stone', 'stone', 1.5, 23),
    ('4', '#4 Stone', 'stone', 1.3, 21),
    ('SAND', 'Concrete Sand', 'sand', 1.35, 24),
    ('MSAND', 'Mason Sand', 'sand', 1.35, 24),
    ('GAB', 'Graded Aggregate Base', 'gravel', 1.5, 23),
    ('FILL', 'Fill Dirt', 'fill', 1.2, 20),
    ('RAP', 'Recycled Asphalt', 'gravel', 1.4, 22);

-- Trucks Table (Enhanced for AI Dispatch)
CREATE TABLE IF NOT EXISTS trucks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    truck_number TEXT NOT NULL UNIQUE,
    plate_number TEXT,
    make TEXT,
    model TEXT,
    year INTEGER,
    capacity_tons REAL,
    samara_device_id TEXT,
    -- AI Knowledge Fields
    truck_type TEXT DEFAULT 'end_dump',  -- long_dump, short_dump, belly_dump, super_dump, transfer, end_dump
    truck_name TEXT,                      -- Friendly name (e.g., "Thor", "Hammer")
    home_location TEXT,                   -- Where truck parks overnight
    home_city TEXT,                       -- City for distance calculations
    home_lat REAL,                        -- Home latitude
    home_lon REAL,                        -- Home longitude
    specialty_materials TEXT,             -- JSON array of preferred materials
    avoid_materials TEXT,                 -- JSON array of materials to avoid
    fuel_efficiency_mpg REAL DEFAULT 6.0,
    avg_speed_loaded_mph REAL DEFAULT 50,
    avg_speed_empty_mph REAL DEFAULT 55,
    load_time_minutes REAL DEFAULT 10,
    unload_time_minutes REAL DEFAULT 5,
    notes TEXT,
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

-- ============================================================================
-- ORDERS AND ACTIVE LOADS TABLES
-- ============================================================================

-- Orders Table (Customer orders with tonnage tracking)
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number TEXT UNIQUE,
    job_id INTEGER,
    plant_id INTEGER,                     -- Delivery destination plant
    pickup_location_id INTEGER,           -- Where to pick up material
    material_id INTEGER,
    quantity_tons REAL NOT NULL,          -- Total tons ordered
    -- Fulfillment tracking
    tons_delivered REAL DEFAULT 0,        -- Tons delivered so far
    tons_remaining REAL,                  -- Auto-calculated remaining
    loads_assigned INTEGER DEFAULT 0,     -- Number of loads assigned
    loads_completed INTEGER DEFAULT 0,    -- Number of loads completed
    estimated_trucks_needed INTEGER,      -- AI estimate of trucks needed
    -- Schedule and status
    requested_date DATE,
    requested_time TIME,
    priority TEXT DEFAULT 'normal',       -- 'urgent', 'high', 'normal', 'low'
    status TEXT DEFAULT 'pending',        -- 'pending', 'in_progress', 'delivered', 'cancelled'
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    FOREIGN KEY (plant_id) REFERENCES plants(id),
    FOREIGN KEY (pickup_location_id) REFERENCES pickup_locations(id),
    FOREIGN KEY (material_id) REFERENCES material_types(id)
);

-- Active Loads Table (Currently in progress)
CREATE TABLE IF NOT EXISTS loads_active (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    load_number TEXT NOT NULL,
    order_id INTEGER,                     -- Link to parent order for fulfillment tracking
    driver_id INTEGER NOT NULL,
    truck_id INTEGER NOT NULL,
    trailer_id INTEGER,
    assignment_id INTEGER,
    job_id INTEGER,
    plant_id INTEGER,
    pickup_location_id INTEGER,
    material_id INTEGER,
    quantity_tons REAL DEFAULT 22,
    status TEXT DEFAULT 'assigned',       -- assigned, en_route, at_job, delivering, complete
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    en_route_at TIMESTAMP,
    at_job_at TIMESTAMP,
    delivering_at TIMESTAMP,
    completed_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (driver_id) REFERENCES drivers(id),
    FOREIGN KEY (truck_id) REFERENCES trucks(id),
    FOREIGN KEY (trailer_id) REFERENCES trailers(id),
    FOREIGN KEY (assignment_id) REFERENCES assignments(id),
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    FOREIGN KEY (plant_id) REFERENCES plants(id),
    FOREIGN KEY (pickup_location_id) REFERENCES pickup_locations(id),
    FOREIGN KEY (material_id) REFERENCES material_types(id)
);

-- Load History Table (Completed/archived loads)
CREATE TABLE IF NOT EXISTS loads_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    load_number TEXT NOT NULL,
    order_id INTEGER,
    driver_id INTEGER NOT NULL,
    truck_id INTEGER NOT NULL,
    trailer_id INTEGER,
    assignment_id INTEGER,
    job_id INTEGER,
    plant_id INTEGER,
    pickup_location_id INTEGER,
    material_id INTEGER,
    quantity_tons REAL,
    status TEXT,
    assigned_at TIMESTAMP,
    en_route_at TIMESTAMP,
    at_job_at TIMESTAMP,
    delivering_at TIMESTAMP,
    completed_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Daily Driver Summary (For productivity tracking)
CREATE TABLE IF NOT EXISTS daily_driver_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    driver_id INTEGER NOT NULL,
    summary_date DATE NOT NULL,
    total_loads INTEGER DEFAULT 0,
    total_tons REAL DEFAULT 0,
    total_miles REAL DEFAULT 0,
    hours_worked REAL DEFAULT 0,
    efficiency_score REAL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (driver_id) REFERENCES drivers(id),
    UNIQUE(driver_id, summary_date)
);

-- AI Recommendations Table (Stores AI dispatch suggestions)
CREATE TABLE IF NOT EXISTS ai_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    recommended_driver_id INTEGER,
    recommended_truck_id INTEGER,
    recommended_plant_id INTEGER,
    estimated_distance_miles REAL,
    estimated_time_minutes REAL,
    estimated_fuel_cost REAL,
    estimated_profit REAL,
    confidence_score REAL,
    reasoning TEXT,
    was_accepted BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (recommended_driver_id) REFERENCES drivers(id),
    FOREIGN KEY (recommended_truck_id) REFERENCES trucks(id),
    FOREIGN KEY (recommended_plant_id) REFERENCES plants(id)
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_loads_driver ON loads(driver_id);
CREATE INDEX IF NOT EXISTS idx_loads_date ON loads(load_date);
CREATE INDEX IF NOT EXISTS idx_loads_status ON loads(status);
CREATE INDEX IF NOT EXISTS idx_assignments_driver ON assignments(driver_id);
CREATE INDEX IF NOT EXISTS idx_assignments_date ON assignments(assigned_date);
CREATE INDEX IF NOT EXISTS idx_tracking_load ON tracking_events(load_id);

-- Indexes for new tables
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(requested_date);
CREATE INDEX IF NOT EXISTS idx_loads_active_driver ON loads_active(driver_id);
CREATE INDEX IF NOT EXISTS idx_loads_active_status ON loads_active(status);
CREATE INDEX IF NOT EXISTS idx_loads_active_order ON loads_active(order_id);
CREATE INDEX IF NOT EXISTS idx_loads_history_driver ON loads_history(driver_id);
CREATE INDEX IF NOT EXISTS idx_loads_history_date ON loads_history(assigned_at);
CREATE INDEX IF NOT EXISTS idx_daily_summary_driver ON daily_driver_summary(driver_id);
CREATE INDEX IF NOT EXISTS idx_daily_summary_date ON daily_driver_summary(summary_date);

-- ============================================================================
-- AI DISPATCH KNOWLEDGE TABLES
-- ============================================================================

-- Route Distances (Known routes between locations)
CREATE TABLE IF NOT EXISTS route_distances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    origin_name TEXT NOT NULL,
    origin_type TEXT,                     -- 'pickup', 'plant', 'job', 'city'
    destination_name TEXT NOT NULL,
    destination_type TEXT,
    distance_miles REAL NOT NULL,
    typical_drive_time_minutes REAL,
    road_type TEXT DEFAULT 'highway',     -- 'highway', 'urban', 'rural'
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(origin_name, destination_name)
);

-- Location Coordinates (For distance calculations)
CREATE TABLE IF NOT EXISTS location_coordinates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_name TEXT NOT NULL UNIQUE,
    location_type TEXT,                   -- 'pickup', 'plant', 'job', 'city', 'truck_home'
    city TEXT,
    state TEXT,
    latitude REAL,
    longitude REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Truck Productivity History (Learning from past performance)
CREATE TABLE IF NOT EXISTS truck_productivity_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    truck_id INTEGER NOT NULL,
    driver_id INTEGER,
    date TEXT NOT NULL,
    origin_location TEXT,
    destination_location TEXT,
    material_code TEXT,
    total_loads INTEGER DEFAULT 0,
    total_tons REAL DEFAULT 0,
    total_hours REAL DEFAULT 0,
    total_miles REAL DEFAULT 0,
    tons_per_hour REAL,
    cost_per_ton REAL,
    cycle_time_avg_minutes REAL,
    efficiency_score REAL,                -- 0-100 score
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (truck_id) REFERENCES trucks(id),
    FOREIGN KEY (driver_id) REFERENCES drivers(id)
);

-- AI Dispatch Settings (Configurable parameters)
CREATE TABLE IF NOT EXISTS ai_dispatch_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_name TEXT NOT NULL UNIQUE,
    setting_value TEXT,
    setting_type TEXT DEFAULT 'string',   -- 'string', 'number', 'boolean', 'json'
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default AI settings
INSERT OR IGNORE INTO ai_dispatch_settings (setting_name, setting_value, setting_type, description) VALUES
    ('efficiency_factor', '0.85', 'number', 'Work efficiency factor (0-1)'),
    ('target_tons_per_day', '100', 'number', 'Target tons per day for scoring'),
    ('max_deadhead_miles', '50', 'number', 'Maximum acceptable deadhead distance'),
    ('work_start_time', '06:00', 'string', 'Default work start time'),
    ('work_end_time', '18:00', 'string', 'Default work end time'),
    ('scoring_weight_productivity', '0.30', 'number', 'Weight for productivity score'),
    ('scoring_weight_cost', '0.20', 'number', 'Weight for cost efficiency score'),
    ('scoring_weight_suitability', '0.15', 'number', 'Weight for truck suitability'),
    ('scoring_weight_deadhead', '0.15', 'number', 'Weight for deadhead distance'),
    ('scoring_weight_workload', '0.10', 'number', 'Weight for workload balance'),
    ('scoring_weight_constraints', '0.10', 'number', 'Weight for constraint compliance');

-- Supplier Operating Hours
CREATE TABLE IF NOT EXISTS supplier_hours (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_name TEXT NOT NULL,
    pickup_location_id INTEGER,
    weekday_open TIME DEFAULT '06:00',
    weekday_close TIME DEFAULT '17:00',
    saturday_open TIME,
    saturday_close TIME DEFAULT '12:00',
    sunday_open TIME,
    sunday_close TIME,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pickup_location_id) REFERENCES pickup_locations(id)
);

-- Insert default supplier hours
INSERT OR IGNORE INTO supplier_hours (supplier_name, weekday_open, weekday_close, saturday_close) VALUES
    ('Martin Marietta', '06:00', '17:00', '12:00'),
    ('Vulcan', '06:00', '16:30', '12:00'),
    ('E.R. Jahna', '06:00', '17:00', '12:00'),
    ('Cemex', '06:00', '17:00', NULL),
    ('East Coast Terminal', '06:00', '16:00', NULL);

-- Indexes for AI tables
CREATE INDEX IF NOT EXISTS idx_route_origin ON route_distances(origin_name);
CREATE INDEX IF NOT EXISTS idx_route_dest ON route_distances(destination_name);
CREATE INDEX IF NOT EXISTS idx_productivity_truck ON truck_productivity_history(truck_id);
CREATE INDEX IF NOT EXISTS idx_productivity_date ON truck_productivity_history(date);
CREATE INDEX IF NOT EXISTS idx_location_name ON location_coordinates(location_name);