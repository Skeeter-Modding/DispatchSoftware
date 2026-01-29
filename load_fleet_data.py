"""
Load Real SRM Fleet Data
========================
This script loads the actual SRM Coastal fleet data including:
- Tractors (trucks) with proper numbering
- Trailers (dump trailers)
- Drivers with assignments
- Default truck-driver assignments
"""

import sqlite3
import os

DATABASE = os.environ.get('DATABASE_PATH', 'database/srm_dispatch.db')

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Real SRM Coastal Fleet Data
FLEET_DATA = [
    # Format: (truck_number, trailer, driver_name, home_plant)
    ("23060", "DT-59 Dump", "THOR WAYMAN", "SRM BLUFFTON"),
    ("23066", "DT65 Dump", "ALBERT MITCHELL", "SRM RIDGELAND"),
    ("23068", "DT-67 Dump", "DAVID POWELL", "SRM GOOSE CREEK"),
    ("24067", "DT-87 Dump", "TALLY BUTLER", "SRM BLUFFTON"),
    ("24068", "DT88 Dump", "KEITH CROFT", "NORTH AUGUSTA"),
    ("25046", "DT-107 Dump", "JEROME POLITE", "SRM BRUNSWICK"),
    ("25049", "DT-111 Dump", "CLEVELAND TOLBERT", None),
    ("25052", "BT-114", "RYAN REED", None),
    ("825", None, "DONNELL DAVIS", "JAHNA Fleming"),
    ("828", None, "KIMBERLY ROBERTS", "SRM RIDGELAND"),
    ("829", None, "DONALD WINTER", "SRM RIDGELAND"),
    ("DT4", None, None, "SRM GARDEN CITY"),
    ("SC2", None, None, None),
    ("SG21", None, None, "JAHNA Fleming"),
    ("SG24", None, "JOSEPH K. SARGENT", "SRM STATESBORO"),
    ("SG25", None, None, "SRM STATESBORO"),
    ("SG26", None, None, "SRM GUYTON HODGEVILLE"),
    ("SG27", None, "LONNIE THOMPSON", "SRM RICHMOND HILL"),
    ("SG28", None, "RACHEL HUTTO", "SRM RICHMOND HILL"),
    ("SG9", "DT11 Dump", "NAQUETIG LEWIS", "JAHNA Fleming"),
    ("T10", "WT-14 Dump", "DAVID HOUSTON", "SRM BRUNSWICK"),
    ("T7", None, "GLENN GOODNO", "SRM AUGUSTA"),
    ("T9", "D-2 Dump", None, "SRM BRUNSWICK"),
    ("W10", None, "KIMBERLY HILL", "JAHNA Fleming"),
    ("W14", "D03 Dump", "LESLEY MURPHY", "SRM GARDEN CITY"),
    ("W17", None, None, "SRM PORTABLE ELLABELL"),
    ("W18", None, None, "SRM BLOOMINGDALE"),
    ("W19", None, "RENA ABROMOWITZ", "SRM GARDEN CITY"),
    ("W22", None, None, "SRM SAVANNAH"),
    ("W23", "WT-13 Dump", "JIMMY LAND", "SRM JOHNS ISLAND"),
    ("W24", None, None, "SRM SUMMERVILLE"),
    ("W27", None, None, "JAHNA Fleming"),
    ("W28", None, "BILL RUMPTZ", "JAHNA Fleming"),
    ("W29", None, "DORRELL GRANT", "SRM GUYTON HODGEVILLE"),
    ("W30", None, "ALICIA SAMPSON", "SRM RICHMOND HILL"),
    ("W31", None, "QUADASHA JACKSON", None),
]

# Plant locations with coordinates (Savannah/Coastal GA/SC area)
PLANT_LOCATIONS = {
    "SRM BLUFFTON": {"city": "Bluffton", "state": "SC", "lat": 32.2371, "lon": -80.8604},
    "SRM RIDGELAND": {"city": "Ridgeland", "state": "SC", "lat": 32.4807, "lon": -80.9804},
    "SRM GOOSE CREEK": {"city": "Goose Creek", "state": "SC", "lat": 32.9810, "lon": -80.0326},
    "NORTH AUGUSTA": {"city": "North Augusta", "state": "SC", "lat": 33.5018, "lon": -81.9651},
    "SRM BRUNSWICK": {"city": "Brunswick", "state": "GA", "lat": 31.1499, "lon": -81.4915},
    "JAHNA Fleming": {"city": "Fleming", "state": "GA", "lat": 31.8632, "lon": -81.4240},
    "SRM GARDEN CITY": {"city": "Savannah", "state": "GA", "lat": 32.0969, "lon": -81.1803},
    "SRM STATESBORO": {"city": "Statesboro", "state": "GA", "lat": 32.4488, "lon": -81.7832},
    "SRM GUYTON HODGEVILLE": {"city": "Guyton", "state": "GA", "lat": 32.3368, "lon": -81.3976},
    "SRM RICHMOND HILL": {"city": "Richmond Hill", "state": "GA", "lat": 31.9382, "lon": -81.3054},
    "SRM AUGUSTA": {"city": "Augusta", "state": "GA", "lat": 33.4735, "lon": -81.9748},
    "SRM PORTABLE ELLABELL": {"city": "Ellabell", "state": "GA", "lat": 32.1460, "lon": -81.4726},
    "SRM BLOOMINGDALE": {"city": "Bloomingdale", "state": "GA", "lat": 32.1324, "lon": -81.2982},
    "SRM SAVANNAH": {"city": "Savannah", "state": "GA", "lat": 32.0809, "lon": -81.0912},
    "SRM JOHNS ISLAND": {"city": "Johns Island", "state": "SC", "lat": 32.7041, "lon": -80.0579},
    "SRM SUMMERVILLE": {"city": "Summerville", "state": "SC", "lat": 33.0185, "lon": -80.1756},
    "SRM BEAUFORT": {"city": "Beaufort", "state": "SC", "lat": 32.4316, "lon": -80.6698},
    "SRM HARDEEVILLE": {"city": "Hardeeville", "state": "SC", "lat": 32.2871, "lon": -81.0804},
    "SRM HINESVILLE": {"city": "Hinesville", "state": "GA", "lat": 31.8468, "lon": -81.5959},
    "SRM POOLER": {"city": "Pooler", "state": "GA", "lat": 32.1157, "lon": -81.2470},
    "SRM RINCON": {"city": "Rincon", "state": "GA", "lat": 32.2960, "lon": -81.2354},
    "SRM MIDWAY": {"city": "Midway", "state": "GA", "lat": 31.8057, "lon": -81.4301},
    "SRM KINGSLAND": {"city": "Kingsland", "state": "GA", "lat": 30.7999, "lon": -81.6898},
}


def clear_existing_data(db):
    """Clear existing fleet data"""
    cursor = db.cursor()
    cursor.execute("DELETE FROM assignments")
    cursor.execute("DELETE FROM driver_truck_defaults")
    cursor.execute("DELETE FROM drivers")
    cursor.execute("DELETE FROM trucks")
    cursor.execute("DELETE FROM trailers")
    db.commit()
    print("Cleared existing fleet data")


def load_drivers(db):
    """Load drivers from fleet data"""
    cursor = db.cursor()
    drivers = {}

    for truck_num, trailer, driver_name, home_plant in FLEET_DATA:
        if driver_name and driver_name not in drivers:
            # Get home location info
            home_city = None
            if home_plant and home_plant in PLANT_LOCATIONS:
                home_city = PLANT_LOCATIONS[home_plant]["city"]

            cursor.execute('''
                INSERT INTO drivers (name, phone, home_location, home_city, status)
                VALUES (?, ?, ?, ?, 'active')
            ''', (driver_name.title(), f"555-{len(drivers)+1000}", home_plant, home_city))

            drivers[driver_name] = cursor.lastrowid
            print(f"  Added driver: {driver_name.title()}")

    db.commit()
    print(f"Loaded {len(drivers)} drivers")
    return drivers


def load_trailers(db):
    """Load trailers from fleet data"""
    cursor = db.cursor()
    trailers = {}

    for truck_num, trailer, driver_name, home_plant in FLEET_DATA:
        if trailer and trailer not in trailers:
            # Determine trailer type
            trailer_type = "Dump Trailer"
            if "BT" in trailer:
                trailer_type = "Belly Dump"
            elif "WT" in trailer:
                trailer_type = "Walking Floor"

            cursor.execute('''
                INSERT INTO trailers (trailer_number, type, capacity_cubic_yards, status)
                VALUES (?, ?, 25, 'active')
            ''', (trailer, trailer_type))

            trailers[trailer] = cursor.lastrowid
            print(f"  Added trailer: {trailer}")

    db.commit()
    print(f"Loaded {len(trailers)} trailers")
    return trailers


def load_trucks(db):
    """Load trucks from fleet data"""
    cursor = db.cursor()
    trucks = {}

    for truck_num, trailer, driver_name, home_plant in FLEET_DATA:
        if truck_num not in trucks:
            # Determine truck type based on prefix
            if truck_num.startswith("W"):
                truck_type = "end_dump"
                make = "Western Star"
            elif truck_num.startswith("T"):
                truck_type = "transfer"
                make = "Peterbilt"
            elif truck_num.startswith("SG"):
                truck_type = "super_dump"
                make = "Kenworth"
            elif truck_num.startswith("SC"):
                truck_type = "side_dump"
                make = "Mack"
            elif truck_num.startswith("DT"):
                truck_type = "end_dump"
                make = "Freightliner"
            else:
                # Numeric trucks (23060, 24067, etc.)
                truck_type = "tandem"
                make = "Volvo"

            # Get home location info
            home_lat, home_lon = 32.08, -81.09  # Default to Savannah
            home_city = "Savannah"
            if home_plant and home_plant in PLANT_LOCATIONS:
                loc = PLANT_LOCATIONS[home_plant]
                home_lat = loc["lat"]
                home_lon = loc["lon"]
                home_city = loc["city"]

            # Generate Samsara device ID
            samsara_id = f"SAM-{truck_num.replace('-', '').upper()}"

            cursor.execute('''
                INSERT INTO trucks (
                    truck_number, make, model, year, capacity_tons,
                    truck_type, truck_name, home_location, home_city,
                    home_lat, home_lon, samara_device_id, status
                ) VALUES (?, ?, ?, ?, 25, ?, ?, ?, ?, ?, ?, ?, 'active')
            ''', (
                truck_num, make, "Dump Truck", 2023,
                truck_type, f"Truck {truck_num}", home_plant, home_city,
                home_lat, home_lon, samsara_id
            ))

            trucks[truck_num] = cursor.lastrowid
            print(f"  Added truck: {truck_num} ({make} {truck_type})")

    db.commit()
    print(f"Loaded {len(trucks)} trucks")
    return trucks


def create_assignments(db, drivers, trucks, trailers):
    """Create driver-truck-trailer assignments"""
    cursor = db.cursor()
    assignment_count = 0

    for truck_num, trailer, driver_name, home_plant in FLEET_DATA:
        if driver_name and truck_num in trucks:
            driver_id = drivers.get(driver_name)
            truck_id = trucks.get(truck_num)
            trailer_id = trailers.get(trailer) if trailer else None

            if driver_id and truck_id:
                # Create active assignment
                cursor.execute('''
                    INSERT INTO assignments (driver_id, truck_id, trailer_id, is_active)
                    VALUES (?, ?, ?, 1)
                ''', (driver_id, truck_id, trailer_id))

                # Create default assignment
                cursor.execute('''
                    INSERT OR REPLACE INTO driver_truck_defaults (driver_id, truck_id, trailer_id)
                    VALUES (?, ?, ?)
                ''', (driver_id, truck_id, trailer_id))

                assignment_count += 1
                print(f"  Assigned: {driver_name.title()} -> {truck_num}" + (f" + {trailer}" if trailer else ""))

    db.commit()
    print(f"Created {assignment_count} assignments")


def update_plants(db):
    """Update plants table with coastal GA/SC locations"""
    cursor = db.cursor()

    for plant_name, info in PLANT_LOCATIONS.items():
        # Check if plant exists
        cursor.execute("SELECT id FROM plants WHERE name LIKE ?", (f"%{info['city']}%",))
        existing = cursor.fetchone()

        if not existing:
            plant_id = f"SRM-{info['city'].upper().replace(' ', '')[:8]}"
            cursor.execute('''
                INSERT INTO plants (plant_id, name, city, state, status)
                VALUES (?, ?, ?, ?, 'active')
            ''', (plant_id, plant_name, info['city'], info['state']))
            print(f"  Added plant: {plant_name}")

    db.commit()
    print("Updated plants")


def main():
    print("=" * 60)
    print("Loading SRM Coastal Fleet Data")
    print("=" * 60)

    db = get_db()

    # Clear existing data
    clear_existing_data(db)

    # Load all data
    print("\nLoading drivers...")
    drivers = load_drivers(db)

    print("\nLoading trailers...")
    trailers = load_trailers(db)

    print("\nLoading trucks...")
    trucks = load_trucks(db)

    print("\nCreating assignments...")
    create_assignments(db, drivers, trucks, trailers)

    print("\nUpdating plants...")
    update_plants(db)

    print("\n" + "=" * 60)
    print("Fleet data loaded successfully!")
    print(f"  Drivers: {len(drivers)}")
    print(f"  Trucks: {len(trucks)}")
    print(f"  Trailers: {len(trailers)}")
    print("=" * 60)

    db.close()


if __name__ == "__main__":
    main()
