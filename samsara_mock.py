"""
Mock Samsara API Service
========================
This module provides a complete mock implementation of the Samsara Fleet API.
It mirrors the real Samsara API structure exactly, making it easy to switch
to the real API by simply providing an API key.

Designed for integration with JONEL Access Unlimited dispatch systems.

Samsara API Reference: https://developers.samsara.com/
"""

import random
import math
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json


# ============================================================================
# SAMSARA API DATA MODELS (Matching real API response structures)
# ============================================================================

@dataclass
class SamsaraGPSLocation:
    """GPS location data matching Samsara's location format"""
    latitude: float
    longitude: float
    heading: int  # 0-360 degrees
    speed: float  # mph
    time: str  # ISO 8601 format
    reverseGeo: Dict[str, str] = None

    def __post_init__(self):
        if self.reverseGeo is None:
            self.reverseGeo = {
                "formattedLocation": "Simulated Location, GA"
            }


@dataclass
class SamsaraVehicle:
    """Vehicle data matching Samsara's vehicle format"""
    id: str
    name: str
    vin: Optional[str] = None
    serial: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    licensePlate: Optional[str] = None
    externalIds: Optional[Dict[str, str]] = None
    tags: Optional[List[Dict]] = None


@dataclass
class SamsaraVehicleLocation:
    """Vehicle with location data"""
    id: str
    name: str
    location: SamsaraGPSLocation
    engineState: Dict[str, Any]


@dataclass
class SamsaraAsset:
    """Asset data matching Samsara's asset format"""
    id: str
    name: str
    type: str  # "vehicle", "trailer", "equipment", "unpowered", "uncategorized"
    serialNumber: Optional[str] = None
    externalIds: Optional[Dict[str, str]] = None
    tags: Optional[List[Dict]] = None


@dataclass
class SamsaraDriver:
    """Driver data matching Samsara's driver format"""
    id: str
    name: str
    username: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    driverActivationStatus: str = "active"
    externalIds: Optional[Dict[str, str]] = None
    tags: Optional[List[Dict]] = None


# ============================================================================
# GEOFENCE DEFINITIONS (SRM/JONEL Compatible)
# ============================================================================

# Key locations for geofence-based status updates
GEOFENCES = {
    # SRM Plants (23 locations)
    "SRM-SMYRNA": {"lat": 33.8839, "lon": -84.5144, "radius": 200, "type": "plant"},
    "SRM-MARIETTA": {"lat": 33.9526, "lon": -84.5499, "radius": 200, "type": "plant"},
    "SRM-ALPHARETTA": {"lat": 34.0754, "lon": -84.2941, "radius": 200, "type": "plant"},
    "SRM-LAWRENCEVILLE": {"lat": 33.9562, "lon": -83.9880, "radius": 200, "type": "plant"},
    "SRM-DULUTH": {"lat": 34.0029, "lon": -84.1447, "radius": 200, "type": "plant"},
    "SRM-BUFORD": {"lat": 34.1207, "lon": -84.0043, "radius": 200, "type": "plant"},
    "SRM-GAINESVILLE": {"lat": 34.2979, "lon": -83.8241, "radius": 200, "type": "plant"},
    "SRM-CUMMING": {"lat": 34.2073, "lon": -84.1402, "radius": 200, "type": "plant"},
    "SRM-CANTON": {"lat": 34.2368, "lon": -84.4908, "radius": 200, "type": "plant"},
    "SRM-WOODSTOCK": {"lat": 34.1015, "lon": -84.5194, "radius": 200, "type": "plant"},
    "SRM-KENNESAW": {"lat": 34.0234, "lon": -84.6155, "radius": 200, "type": "plant"},
    "SRM-DOUGLASVILLE": {"lat": 33.7515, "lon": -84.7477, "radius": 200, "type": "plant"},
    "SRM-NEWNAN": {"lat": 33.3807, "lon": -84.7997, "radius": 200, "type": "plant"},
    "SRM-PEACHTREE-CITY": {"lat": 33.3968, "lon": -84.5958, "radius": 200, "type": "plant"},
    "SRM-FAYETTEVILLE": {"lat": 33.4487, "lon": -84.4549, "radius": 200, "type": "plant"},
    "SRM-MCDONOUGH": {"lat": 33.4473, "lon": -84.1469, "radius": 200, "type": "plant"},
    "SRM-STOCKBRIDGE": {"lat": 33.5443, "lon": -84.2330, "radius": 200, "type": "plant"},
    "SRM-CONYERS": {"lat": 33.6676, "lon": -84.0177, "radius": 200, "type": "plant"},
    "SRM-COVINGTON": {"lat": 33.5968, "lon": -83.8602, "radius": 200, "type": "plant"},
    "SRM-MONROE": {"lat": 33.7948, "lon": -83.7133, "radius": 200, "type": "plant"},
    "SRM-ATHENS": {"lat": 33.9519, "lon": -83.3576, "radius": 200, "type": "plant"},
    "SRM-WINDER": {"lat": 33.9926, "lon": -83.7202, "radius": 200, "type": "plant"},
    "SRM-JEFFERSON": {"lat": 34.1115, "lon": -83.6021, "radius": 200, "type": "plant"},

    # Major Quarries/Pickup Locations
    "VULCAN-NORCROSS": {"lat": 33.9412, "lon": -84.2135, "radius": 300, "type": "pickup"},
    "VULCAN-LITHONIA": {"lat": 33.7132, "lon": -84.1052, "radius": 300, "type": "pickup"},
    "MARTIN-MARIETTA-KENNESAW": {"lat": 34.0156, "lon": -84.5832, "radius": 300, "type": "pickup"},
    "MARTIN-MARIETTA-CUMMING": {"lat": 34.1823, "lon": -84.1156, "radius": 300, "type": "pickup"},
    "HANSON-AUBURN": {"lat": 34.0134, "lon": -83.8276, "radius": 300, "type": "pickup"},
    "JAHNA-APALACHEE": {"lat": 33.7845, "lon": -83.5123, "radius": 300, "type": "pickup"},
    "EAST-COAST-TERMINAL": {"lat": 33.7556, "lon": -84.3889, "radius": 300, "type": "pickup"},
}


# ============================================================================
# MOCK DATA GENERATORS
# ============================================================================

class MockSamsaraDataGenerator:
    """Generates realistic mock data for Samsara API responses"""

    def __init__(self, db_connection=None):
        self.db = db_connection
        self._vehicle_positions = {}  # Track simulated positions
        self._last_update = {}

    def _get_trucks_from_db(self) -> List[Dict]:
        """Get truck data from database if available"""
        if self.db is None:
            return self._generate_mock_trucks()

        try:
            cursor = self.db.execute("""
                SELECT t.id, t.truck_number, t.plate_number, t.make, t.model,
                       t.year, t.samara_device_id, t.truck_type, t.truck_name,
                       t.home_lat, t.home_lon, t.home_city,
                       d.name as driver_name, d.id as driver_id
                FROM trucks t
                LEFT JOIN assignments a ON t.id = a.truck_id AND a.is_active = 1
                LEFT JOIN drivers d ON a.driver_id = d.id
                WHERE t.status = 'active'
            """)
            return [dict(row) for row in cursor.fetchall()]
        except Exception:
            return self._generate_mock_trucks()

    def _generate_mock_trucks(self) -> List[Dict]:
        """Generate mock truck data if database unavailable"""
        trucks = []
        truck_types = ['end_dump', 'belly_dump', 'super_dump', 'transfer', 'tandem']
        makes = ['Kenworth', 'Peterbilt', 'Mack', 'Freightliner', 'International']

        for i in range(1, 16):
            trucks.append({
                'id': i,
                'truck_number': f'T{i:03d}',
                'plate_number': f'GA-{random.randint(1000, 9999)}',
                'make': random.choice(makes),
                'model': f'Model-{random.choice(["W900", "389", "Anthem", "Cascadia", "LT"])}',
                'year': random.randint(2018, 2024),
                'samara_device_id': f'SAM-{i:06d}',
                'truck_type': random.choice(truck_types),
                'truck_name': f'Truck {i}',
                'home_lat': 33.8 + random.uniform(-0.3, 0.3),
                'home_lon': -84.4 + random.uniform(-0.3, 0.3),
                'home_city': 'Atlanta',
                'driver_name': f'Driver {i}',
                'driver_id': i
            })
        return trucks

    def _simulate_vehicle_movement(self, vehicle_id: str, home_lat: float, home_lon: float) -> SamsaraGPSLocation:
        """Simulate realistic vehicle movement"""
        current_time = time.time()

        # Initialize or get current position
        if vehicle_id not in self._vehicle_positions:
            self._vehicle_positions[vehicle_id] = {
                'lat': home_lat,
                'lon': home_lon,
                'heading': random.randint(0, 360),
                'speed': 0,
                'state': 'idle',  # idle, en_route, at_location
                'target': None
            }
            self._last_update[vehicle_id] = current_time

        pos = self._vehicle_positions[vehicle_id]
        elapsed = current_time - self._last_update.get(vehicle_id, current_time)

        # Simulate movement based on state
        if pos['state'] == 'idle':
            # 30% chance to start moving
            if random.random() < 0.3:
                pos['state'] = 'en_route'
                pos['target'] = random.choice(list(GEOFENCES.keys()))
                pos['speed'] = random.uniform(35, 65)
                pos['heading'] = random.randint(0, 360)
            else:
                pos['speed'] = 0

        elif pos['state'] == 'en_route':
            # Move towards target
            if pos['target'] and pos['target'] in GEOFENCES:
                target = GEOFENCES[pos['target']]

                # Calculate direction to target
                dlat = target['lat'] - pos['lat']
                dlon = target['lon'] - pos['lon']
                distance = math.sqrt(dlat**2 + dlon**2)

                if distance < 0.005:  # Close to target (~500m)
                    pos['state'] = 'at_location'
                    pos['speed'] = 0
                    pos['lat'] = target['lat'] + random.uniform(-0.001, 0.001)
                    pos['lon'] = target['lon'] + random.uniform(-0.001, 0.001)
                else:
                    # Move towards target
                    pos['heading'] = int(math.degrees(math.atan2(dlon, dlat))) % 360
                    speed_factor = min(elapsed, 60) / 3600  # Convert to hours
                    move_dist = pos['speed'] * speed_factor / 69  # ~69 miles per degree
                    pos['lat'] += dlat / distance * move_dist
                    pos['lon'] += dlon / distance * move_dist
                    pos['speed'] = random.uniform(40, 65)

        elif pos['state'] == 'at_location':
            # 20% chance to leave
            if random.random() < 0.2:
                pos['state'] = 'en_route'
                pos['target'] = random.choice(list(GEOFENCES.keys()))
                pos['speed'] = random.uniform(35, 55)
            else:
                pos['speed'] = 0

        self._last_update[vehicle_id] = current_time

        # Check if inside any geofence
        location_name = "In Transit"
        for name, geo in GEOFENCES.items():
            dist = math.sqrt((pos['lat'] - geo['lat'])**2 + (pos['lon'] - geo['lon'])**2) * 69 * 5280  # feet
            if dist < geo['radius']:
                location_name = name.replace('-', ' ').title()
                break

        return SamsaraGPSLocation(
            latitude=round(pos['lat'], 6),
            longitude=round(pos['lon'], 6),
            heading=pos['heading'],
            speed=round(pos['speed'], 1),
            time=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z'),
            reverseGeo={"formattedLocation": location_name}
        )


# ============================================================================
# MOCK SAMSARA API CLIENT
# ============================================================================

class MockSamsaraAPI:
    """
    Mock implementation of Samsara Fleet API

    This class mirrors the real Samsara API exactly. To switch to the real API:
    1. Set SAMSARA_API_KEY environment variable
    2. Change USE_MOCK_API = False

    Compatible with JONEL Access Unlimited integration via Flex API.
    """

    BASE_URL = "https://api.samsara.com"
    MOCK_MODE = True

    def __init__(self, api_key: str = None, db_connection=None):
        self.api_key = api_key or "mock_api_key_demo"
        self.db = db_connection
        self.data_generator = MockSamsaraDataGenerator(db_connection)
        self._rate_limit_remaining = 5
        self._rate_limit_reset = time.time() + 1

    def _check_rate_limit(self):
        """Simulate Samsara rate limiting (5 req/sec)"""
        if time.time() > self._rate_limit_reset:
            self._rate_limit_remaining = 5
            self._rate_limit_reset = time.time() + 1

        if self._rate_limit_remaining <= 0:
            return {
                "error": "Rate limit exceeded",
                "code": 429,
                "message": "Too many requests. Rate limit: 5 requests/sec"
            }

        self._rate_limit_remaining -= 1
        return None

    def _build_pagination(self, data: List, limit: int = 300, after: str = None) -> Dict:
        """Build paginated response matching Samsara format"""
        start_idx = 0
        if after:
            try:
                start_idx = int(after)
            except ValueError:
                start_idx = 0

        end_idx = start_idx + limit
        page_data = data[start_idx:end_idx]

        pagination = {}
        if end_idx < len(data):
            pagination["endCursor"] = str(end_idx)
            pagination["hasNextPage"] = True
        else:
            pagination["hasNextPage"] = False

        return {"data": page_data, "pagination": pagination}

    # ========================================================================
    # ASSETS API (https://api.samsara.com/assets)
    # ========================================================================

    def list_assets(
        self,
        type: str = None,
        after: str = None,
        limit: int = 300,
        include_external_ids: bool = False,
        include_tags: bool = False,
        tag_ids: List[str] = None,
        ids: List[str] = None
    ) -> Dict:
        """
        List all assets.

        Endpoint: GET https://api.samsara.com/assets
        Rate limit: 5 requests/sec

        Args:
            type: Filter by asset type (vehicle, trailer, equipment, unpowered, uncategorized)
            after: Pagination cursor
            limit: Max results per page (default 300)
            include_external_ids: Include external IDs in response
            include_tags: Include tags in response
            tag_ids: Filter by tag IDs
            ids: Filter by specific asset IDs

        Returns:
            Paginated list of assets matching Samsara API format
        """
        rate_error = self._check_rate_limit()
        if rate_error:
            return rate_error

        trucks = self.data_generator._get_trucks_from_db()
        assets = []

        for truck in trucks:
            asset_type = "vehicle"
            if truck.get('truck_type') in ['trailer', 'flatbed_trailer']:
                asset_type = "trailer"

            # Apply type filter
            if type and asset_type != type:
                continue

            # Apply ID filter
            if ids and str(truck['id']) not in ids:
                continue

            asset = {
                "id": truck.get('samara_device_id') or f"SAM-{truck['id']:06d}",
                "name": truck.get('truck_name') or truck.get('truck_number'),
                "type": asset_type,
                "serialNumber": truck.get('plate_number'),
            }

            if include_external_ids:
                asset["externalIds"] = {
                    "dispatch_truck_id": str(truck['id']),
                    "truck_number": truck.get('truck_number')
                }

            if include_tags:
                asset["tags"] = [
                    {"id": "tag-fleet", "name": "SRM Fleet"},
                    {"id": f"tag-{truck.get('truck_type', 'unknown')}", "name": truck.get('truck_type', 'unknown').replace('_', ' ').title()}
                ]

            assets.append(asset)

        return self._build_pagination(assets, limit, after)

    # ========================================================================
    # FLEET API - VEHICLES
    # ========================================================================

    def list_vehicles(
        self,
        after: str = None,
        limit: int = 512,
        include_external_ids: bool = False,
        include_tags: bool = False,
        tag_ids: List[str] = None
    ) -> Dict:
        """
        List all vehicles in the fleet.

        Endpoint: GET https://api.samsara.com/fleet/vehicles
        Rate limit: 5 requests/sec
        """
        rate_error = self._check_rate_limit()
        if rate_error:
            return rate_error

        trucks = self.data_generator._get_trucks_from_db()
        vehicles = []

        for truck in trucks:
            vehicle = {
                "id": truck.get('samara_device_id') or f"SAM-{truck['id']:06d}",
                "name": truck.get('truck_name') or truck.get('truck_number'),
                "vin": f"1XKWD49X{truck['id']:09d}",
                "serial": truck.get('samara_device_id'),
                "make": truck.get('make', 'Unknown'),
                "model": truck.get('model', 'Unknown'),
                "year": truck.get('year', 2020),
                "licensePlate": truck.get('plate_number'),
            }

            if include_external_ids:
                vehicle["externalIds"] = {
                    "dispatch_truck_id": str(truck['id']),
                    "truck_number": truck.get('truck_number')
                }

            if include_tags:
                vehicle["tags"] = [
                    {"id": "tag-fleet", "name": "SRM Fleet", "parentTagId": None}
                ]

            vehicles.append(vehicle)

        return self._build_pagination(vehicles, limit, after)

    def get_vehicle(self, vehicle_id: str) -> Dict:
        """
        Get a specific vehicle by ID.

        Endpoint: GET https://api.samsara.com/fleet/vehicles/{id}
        """
        rate_error = self._check_rate_limit()
        if rate_error:
            return rate_error

        trucks = self.data_generator._get_trucks_from_db()
        for truck in trucks:
            if truck.get('samara_device_id') == vehicle_id or str(truck['id']) == vehicle_id:
                return {
                    "data": {
                        "id": truck.get('samara_device_id') or f"SAM-{truck['id']:06d}",
                        "name": truck.get('truck_name') or truck.get('truck_number'),
                        "vin": f"1XKWD49X{truck['id']:09d}",
                        "make": truck.get('make', 'Unknown'),
                        "model": truck.get('model', 'Unknown'),
                        "year": truck.get('year', 2020),
                        "licensePlate": truck.get('plate_number'),
                    }
                }

        return {"error": "Vehicle not found", "code": 404}

    # ========================================================================
    # FLEET API - VEHICLE LOCATIONS
    # ========================================================================

    def get_vehicle_locations(
        self,
        after: str = None,
        vehicle_ids: List[str] = None,
        tag_ids: List[str] = None
    ) -> Dict:
        """
        Get current GPS locations for all vehicles.

        Endpoint: GET https://api.samsara.com/fleet/vehicles/locations
        Rate limit: 5 requests/sec

        This is the primary endpoint for real-time fleet tracking.
        """
        rate_error = self._check_rate_limit()
        if rate_error:
            return rate_error

        trucks = self.data_generator._get_trucks_from_db()
        locations = []

        for truck in trucks:
            vehicle_id = truck.get('samara_device_id') or f"SAM-{truck['id']:06d}"

            # Apply vehicle ID filter
            if vehicle_ids and vehicle_id not in vehicle_ids:
                continue

            home_lat = truck.get('home_lat') or 33.8839
            home_lon = truck.get('home_lon') or -84.5144

            location = self.data_generator._simulate_vehicle_movement(
                vehicle_id, home_lat, home_lon
            )

            # Determine engine state based on speed
            engine_running = location.speed > 0

            locations.append({
                "id": vehicle_id,
                "name": truck.get('truck_name') or truck.get('truck_number'),
                "location": {
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "heading": location.heading,
                    "speed": location.speed,
                    "time": location.time,
                    "reverseGeo": location.reverseGeo
                },
                "engineState": {
                    "value": "On" if engine_running else "Off",
                    "time": location.time
                }
            })

        return self._build_pagination(locations, 512, after)

    def get_vehicle_location(self, vehicle_id: str) -> Dict:
        """
        Get current GPS location for a specific vehicle.

        Endpoint: GET https://api.samsara.com/fleet/vehicles/{id}/locations
        """
        rate_error = self._check_rate_limit()
        if rate_error:
            return rate_error

        trucks = self.data_generator._get_trucks_from_db()
        for truck in trucks:
            if truck.get('samara_device_id') == vehicle_id or str(truck['id']) == vehicle_id:
                home_lat = truck.get('home_lat') or 33.8839
                home_lon = truck.get('home_lon') or -84.5144

                location = self.data_generator._simulate_vehicle_movement(
                    vehicle_id, home_lat, home_lon
                )

                return {
                    "data": {
                        "id": vehicle_id,
                        "name": truck.get('truck_name') or truck.get('truck_number'),
                        "location": {
                            "latitude": location.latitude,
                            "longitude": location.longitude,
                            "heading": location.heading,
                            "speed": location.speed,
                            "time": location.time,
                            "reverseGeo": location.reverseGeo
                        }
                    }
                }

        return {"error": "Vehicle not found", "code": 404}

    # ========================================================================
    # FLEET API - VEHICLE STATS
    # ========================================================================

    def get_vehicle_stats(
        self,
        types: List[str] = None,
        after: str = None,
        vehicle_ids: List[str] = None
    ) -> Dict:
        """
        Get current vehicle stats (fuel, odometer, engine hours, etc.)

        Endpoint: GET https://api.samsara.com/fleet/vehicles/stats

        Args:
            types: Stats to return (engineStates, fuelPercents, obdOdometerMeters, etc.)
        """
        rate_error = self._check_rate_limit()
        if rate_error:
            return rate_error

        if types is None:
            types = ["engineStates", "fuelPercents", "obdOdometerMeters"]

        trucks = self.data_generator._get_trucks_from_db()
        stats = []

        for truck in trucks:
            vehicle_id = truck.get('samara_device_id') or f"SAM-{truck['id']:06d}"

            if vehicle_ids and vehicle_id not in vehicle_ids:
                continue

            current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
            vehicle_stats = {
                "id": vehicle_id,
                "name": truck.get('truck_name') or truck.get('truck_number'),
            }

            if "engineStates" in types:
                vehicle_stats["engineState"] = {
                    "value": random.choice(["On", "Off", "Idle"]),
                    "time": current_time
                }

            if "fuelPercents" in types:
                vehicle_stats["fuelPercent"] = {
                    "value": random.randint(25, 95),
                    "time": current_time
                }

            if "obdOdometerMeters" in types:
                vehicle_stats["obdOdometerMeters"] = {
                    "value": random.randint(50000, 500000) * 1609,  # miles to meters
                    "time": current_time
                }

            if "engineSeconds" in types:
                vehicle_stats["engineSeconds"] = {
                    "value": random.randint(5000, 50000) * 3600,  # hours to seconds
                    "time": current_time
                }

            stats.append(vehicle_stats)

        return self._build_pagination(stats, 512, after)

    # ========================================================================
    # FLEET API - DRIVERS
    # ========================================================================

    def list_drivers(
        self,
        after: str = None,
        limit: int = 512,
        driver_activation_status: str = None,
        include_external_ids: bool = False
    ) -> Dict:
        """
        List all drivers.

        Endpoint: GET https://api.samsara.com/fleet/drivers
        """
        rate_error = self._check_rate_limit()
        if rate_error:
            return rate_error

        drivers = []

        if self.db:
            try:
                cursor = self.db.execute("""
                    SELECT id, name, phone, email, employee_id, status
                    FROM drivers WHERE status = 'active'
                """)
                db_drivers = [dict(row) for row in cursor.fetchall()]

                for d in db_drivers:
                    driver = {
                        "id": f"driver-{d['id']}",
                        "name": d['name'],
                        "phone": d.get('phone'),
                        "email": d.get('email'),
                        "driverActivationStatus": "active" if d['status'] == 'active' else "deactivated"
                    }

                    if include_external_ids:
                        driver["externalIds"] = {
                            "dispatch_driver_id": str(d['id']),
                            "employee_id": d.get('employee_id')
                        }

                    drivers.append(driver)
            except Exception:
                pass

        # Generate mock drivers if none from DB
        if not drivers:
            for i in range(1, 16):
                drivers.append({
                    "id": f"driver-{i}",
                    "name": f"Driver {i}",
                    "phone": f"555-010{i:01d}",
                    "driverActivationStatus": "active"
                })

        return self._build_pagination(drivers, limit, after)

    # ========================================================================
    # ADDRESSES/GEOFENCES API
    # ========================================================================

    def list_addresses(
        self,
        after: str = None,
        limit: int = 512
    ) -> Dict:
        """
        List all addresses/geofences.

        Endpoint: GET https://api.samsara.com/addresses
        """
        rate_error = self._check_rate_limit()
        if rate_error:
            return rate_error

        addresses = []
        for name, geo in GEOFENCES.items():
            addresses.append({
                "id": f"addr-{name.lower()}",
                "name": name.replace('-', ' ').title(),
                "formattedAddress": f"{name.replace('-', ' ').title()}, GA",
                "geofence": {
                    "circle": {
                        "latitude": geo['lat'],
                        "longitude": geo['lon'],
                        "radiusMeters": geo['radius']
                    }
                },
                "tags": [{"id": f"tag-{geo['type']}", "name": geo['type'].title()}]
            })

        return self._build_pagination(addresses, limit, after)

    # ========================================================================
    # REPORTS API
    # ========================================================================

    def get_vehicle_locations_history(
        self,
        start_time: str,
        end_time: str,
        vehicle_ids: List[str] = None,
        after: str = None
    ) -> Dict:
        """
        Get historical GPS locations for vehicles.

        Endpoint: GET https://api.samsara.com/fleet/vehicles/locations/history

        Args:
            start_time: ISO 8601 start time
            end_time: ISO 8601 end time
            vehicle_ids: Filter by vehicle IDs
        """
        rate_error = self._check_rate_limit()
        if rate_error:
            return rate_error

        # Generate mock historical data
        history = []
        trucks = self.data_generator._get_trucks_from_db()

        for truck in trucks[:5]:  # Limit to 5 vehicles for demo
            vehicle_id = truck.get('samara_device_id') or f"SAM-{truck['id']:06d}"

            if vehicle_ids and vehicle_id not in vehicle_ids:
                continue

            points = []
            base_lat = truck.get('home_lat') or 33.8839
            base_lon = truck.get('home_lon') or -84.5144

            # Generate 24 points (one per hour)
            for i in range(24):
                timestamp = datetime.utcnow() - timedelta(hours=24-i)
                points.append({
                    "latitude": base_lat + random.uniform(-0.1, 0.1),
                    "longitude": base_lon + random.uniform(-0.1, 0.1),
                    "heading": random.randint(0, 360),
                    "speed": random.uniform(0, 65) if 6 <= i <= 18 else 0,
                    "time": timestamp.strftime('%Y-%m-%dT%H:%M:%S.000Z')
                })

            history.append({
                "id": vehicle_id,
                "name": truck.get('truck_name') or truck.get('truck_number'),
                "locations": points
            })

        return self._build_pagination(history, 512, after)

    # ========================================================================
    # WEBHOOKS API (For JONEL Integration)
    # ========================================================================

    def list_webhooks(self) -> Dict:
        """
        List configured webhooks.

        Endpoint: GET https://api.samsara.com/webhooks

        Webhooks can push real-time events to JONEL's Flex API.
        """
        return {
            "data": [
                {
                    "id": "webhook-jonel-dispatch",
                    "name": "JONEL Dispatch Integration",
                    "url": "https://api.jonel.com/flex/samsara/events",
                    "eventTypes": [
                        "GeofenceEntry",
                        "GeofenceExit",
                        "VehicleEngineTurnedOn",
                        "VehicleEngineTurnedOff"
                    ],
                    "enabled": True
                }
            ],
            "pagination": {"hasNextPage": False}
        }

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def health_check(self) -> Dict:
        """Check API connectivity (mock always returns healthy)"""
        return {
            "status": "healthy",
            "mode": "mock" if self.MOCK_MODE else "live",
            "api_version": "2024-01",
            "rate_limit_remaining": self._rate_limit_remaining,
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_api_info(self) -> Dict:
        """Get API configuration info"""
        return {
            "mode": "MOCK DEMO MODE",
            "note": "This is simulated data. Connect real API key for live data.",
            "base_url": self.BASE_URL,
            "endpoints_available": [
                "GET /assets",
                "GET /fleet/vehicles",
                "GET /fleet/vehicles/{id}",
                "GET /fleet/vehicles/locations",
                "GET /fleet/vehicles/{id}/locations",
                "GET /fleet/vehicles/stats",
                "GET /fleet/drivers",
                "GET /addresses",
                "GET /fleet/vehicles/locations/history",
                "GET /webhooks"
            ],
            "jonel_compatible": True,
            "flex_api_ready": True
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_mock_api(db_connection=None) -> MockSamsaraAPI:
    """Factory function to create a mock API instance"""
    return MockSamsaraAPI(db_connection=db_connection)


def format_for_jonel(samsara_response: Dict) -> Dict:
    """
    Transform Samsara API response to JONEL Flex API format.

    This enables seamless integration between Samsara GPS data
    and JONEL's Access Unlimited dispatch system.
    """
    if "error" in samsara_response:
        return samsara_response

    # Map Samsara vehicle locations to JONEL format
    if "data" in samsara_response:
        data = samsara_response["data"]
        if isinstance(data, list) and len(data) > 0 and "location" in data[0]:
            jonel_data = []
            for item in data:
                jonel_data.append({
                    "truckId": item.get("id"),
                    "truckName": item.get("name"),
                    "gpsLatitude": item["location"]["latitude"],
                    "gpsLongitude": item["location"]["longitude"],
                    "gpsHeading": item["location"]["heading"],
                    "gpsSpeed": item["location"]["speed"],
                    "gpsTimestamp": item["location"]["time"],
                    "currentLocation": item["location"]["reverseGeo"]["formattedLocation"],
                    "engineStatus": item.get("engineState", {}).get("value", "Unknown")
                })
            return {"trucks": jonel_data, "count": len(jonel_data)}

    return samsara_response
