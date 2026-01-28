"""
AI Dispatch Knowledge Base & Smart Optimization Engine
Smyrna Ready Mix Dispatch System

This module contains:
- Truck knowledge (types, capacities, home locations, specialties)
- Route knowledge (distances, travel times, road conditions)
- Material knowledge (densities, handling requirements)
- Productivity calculator (cycle times, loads/day, tons/day)
- Operating hours & constraint enforcement
- Smart scoring algorithm with multiple factors
"""

import math
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Tuple, Any


# =============================================================================
# TRUCK TYPE DEFINITIONS
# =============================================================================

class TruckType:
    """Truck type categories with their characteristics"""

    # Truck type constants
    LONG_DUMP = "long_dump"          # End dump semi-trailer with trailer (25 tons)
    SHORT_DUMP = "short_dump"        # Tandem dump truck, no trailer (18 tons)
    BELLY_DUMP = "belly_dump"        # Bottom dump trailer (24-30 tons)
    SUPER_DUMP = "super_dump"        # Maximum payload dump (up to 26 tons)
    TRANSFER = "transfer"            # Transfer dump (26-27 tons)
    END_DUMP = "end_dump"            # Standard end dump with trailer (25 tons)
    LOWBOY = "lowboy"                # Lowboy/equipment hauler (not for aggregate)
    TANDEM = "tandem"                # Tandem dump, no trailer (18 tons)

    # Type characteristics
    CHARACTERISTICS = {
        LONG_DUMP: {
            "name": "Long Dump (Semi End Dump with Trailer)",
            "typical_capacity_tons": 25,
            "min_capacity": 24,
            "max_capacity": 26,
            "best_for": ["long_haul", "highway", "large_jobs"],
            "material_handling": ["all"],  # Most versatile
            "unload_time_minutes": 5,
            "load_time_minutes": 12,
            "fuel_efficiency_mpg": 5.5,
            "avg_speed_loaded_mph": 55,
            "avg_speed_empty_mph": 60,
            "can_handle_wet_materials": True,
            "can_handle_large_rocks": True,
            "notes": "Best for longer hauls. More efficient on highway. Takes longer to cycle but carries more."
        },
        SHORT_DUMP: {
            "name": "Tandem Dump (No Trailer)",
            "typical_capacity_tons": 18,
            "min_capacity": 16,
            "max_capacity": 20,
            "best_for": ["short_haul", "city", "tight_spaces"],
            "material_handling": ["all"],
            "unload_time_minutes": 3,
            "load_time_minutes": 8,
            "fuel_efficiency_mpg": 6.5,
            "avg_speed_loaded_mph": 45,
            "avg_speed_empty_mph": 50,
            "can_handle_wet_materials": True,
            "can_handle_large_rocks": True,
            "notes": "Tandem dump truck without trailer. Better for short runs and tight job sites. Faster cycle but 18 tons max."
        },
        BELLY_DUMP: {
            "name": "Belly Dump (Bottom Dump)",
            "typical_capacity_tons": 26,
            "min_capacity": 24,
            "max_capacity": 30,
            "best_for": ["paving", "windrow", "continuous_ops"],
            "material_handling": ["sand", "gravel", "hot_asphalt", "57s", "89s"],
            "unload_time_minutes": 2,  # Very fast unload
            "load_time_minutes": 10,
            "fuel_efficiency_mpg": 5.0,
            "avg_speed_loaded_mph": 50,
            "avg_speed_empty_mph": 55,
            "can_handle_wet_materials": False,  # Material contacts axles
            "can_handle_large_rocks": False,
            "notes": "Excellent for laying windrows. Fast turnaround. NOT for clay, large rocks, or cold mix."
        },
        SUPER_DUMP: {
            "name": "Super Dump",
            "typical_capacity_tons": 25,
            "min_capacity": 24,
            "max_capacity": 26,
            "best_for": ["maximum_payload", "highway"],
            "material_handling": ["all"],
            "unload_time_minutes": 4,
            "load_time_minutes": 10,
            "fuel_efficiency_mpg": 5.5,
            "avg_speed_loaded_mph": 50,
            "avg_speed_empty_mph": 55,
            "can_handle_wet_materials": True,
            "can_handle_large_rocks": True,
            "notes": "Maximum legal payload. Good all-around choice for medium-long hauls."
        },
        TRANSFER: {
            "name": "Transfer Dump",
            "typical_capacity_tons": 26,
            "min_capacity": 25,
            "max_capacity": 27,
            "best_for": ["aggregate", "construction", "large_volume"],
            "material_handling": ["sand", "gravel", "57s", "67s", "89s"],
            "unload_time_minutes": 5,
            "load_time_minutes": 12,
            "fuel_efficiency_mpg": 5.0,
            "avg_speed_loaded_mph": 50,
            "avg_speed_empty_mph": 55,
            "can_handle_wet_materials": True,
            "can_handle_large_rocks": False,
            "notes": "High capacity for aggregate hauling. Can unload pup trailer separately."
        },
        END_DUMP: {
            "name": "End Dump (With Trailer)",
            "typical_capacity_tons": 25,
            "min_capacity": 24,
            "max_capacity": 26,
            "best_for": ["versatile", "stockpiling", "demolition"],
            "material_handling": ["all"],
            "unload_time_minutes": 4,
            "load_time_minutes": 10,
            "fuel_efficiency_mpg": 5.5,
            "avg_speed_loaded_mph": 50,
            "avg_speed_empty_mph": 55,
            "can_handle_wet_materials": True,
            "can_handle_large_rocks": True,
            "notes": "Standard end dump with trailer. 25 tons per load. Most versatile."
        },
        "lowboy": {
            "name": "Lowboy (Equipment Hauler)",
            "typical_capacity_tons": 0,
            "min_capacity": 0,
            "max_capacity": 0,
            "best_for": ["equipment", "heavy_machinery", "excavators"],
            "material_handling": [],  # Does not haul aggregate
            "unload_time_minutes": 30,
            "load_time_minutes": 30,
            "fuel_efficiency_mpg": 4.5,
            "avg_speed_loaded_mph": 45,
            "avg_speed_empty_mph": 55,
            "can_handle_wet_materials": False,
            "can_handle_large_rocks": False,
            "notes": "Equipment hauler only. Does NOT haul aggregate materials. Used for moving heavy equipment."
        },
        "tandem": {
            "name": "Tandem Dump (No Trailer)",
            "typical_capacity_tons": 18,
            "min_capacity": 16,
            "max_capacity": 20,
            "best_for": ["short_haul", "city", "tight_spaces"],
            "material_handling": ["all"],
            "unload_time_minutes": 3,
            "load_time_minutes": 8,
            "fuel_efficiency_mpg": 6.5,
            "avg_speed_loaded_mph": 45,
            "avg_speed_empty_mph": 50,
            "can_handle_wet_materials": True,
            "can_handle_large_rocks": True,
            "notes": "Tandem dump truck without trailer. 18 tons per load max."
        }
    }

    @classmethod
    def get_characteristics(cls, truck_type: str) -> Dict:
        """Get characteristics for a truck type"""
        return cls.CHARACTERISTICS.get(truck_type, cls.CHARACTERISTICS[cls.END_DUMP])


# =============================================================================
# MATERIAL KNOWLEDGE
# =============================================================================

class MaterialKnowledge:
    """Knowledge about materials and their handling requirements"""

    # Material density (tons per cubic yard)
    DENSITIES = {
        "SAND": 1.35,      # Dry sand
        "57": 1.4,         # 57 stone
        "57s": 1.4,
        "67": 1.5,         # 67 stone
        "67s": 1.5,
        "89": 1.35,        # 89 stone
        "89s": 1.35,
        "4": 1.3,          # #4 stone
        "4s": 1.3,
        "57L": 1.45,       # 57 limestone
        "GRAVEL": 1.5,
        "ASPHALT": 2.2,    # Hot mix asphalt
        "TOPSOIL": 1.1,
        "DIRT": 1.2,
        "CRUSHED_STONE": 1.4,
    }

    # Load time adjustments by material (multiplier)
    LOAD_TIME_FACTORS = {
        "SAND": 0.9,       # Easy to load
        "57": 1.0,
        "57s": 1.0,
        "67": 1.0,
        "67s": 1.0,
        "89": 0.95,
        "89s": 0.95,
        "4": 1.2,          # Larger stones take longer
        "4s": 1.2,
        "57L": 1.0,
        "ASPHALT": 0.8,    # Fast loading
    }

    # Unload time adjustments by material (multiplier)
    UNLOAD_TIME_FACTORS = {
        "SAND": 0.8,       # Flows easily
        "57": 1.0,
        "57s": 1.0,
        "67": 1.0,
        "67s": 1.0,
        "89": 0.9,
        "89s": 0.9,
        "4": 1.3,          # May stick/jam
        "4s": 1.3,
        "57L": 1.0,
        "ASPHALT": 0.7,    # Hot, flows fast
    }

    @classmethod
    def get_density(cls, material_code: str) -> float:
        """Get material density in tons per cubic yard"""
        return cls.DENSITIES.get(material_code.upper(), 1.4)

    @classmethod
    def get_load_time_factor(cls, material_code: str) -> float:
        """Get load time adjustment factor"""
        return cls.LOAD_TIME_FACTORS.get(material_code.upper(), 1.0)

    @classmethod
    def get_unload_time_factor(cls, material_code: str) -> float:
        """Get unload time adjustment factor"""
        return cls.UNLOAD_TIME_FACTORS.get(material_code.upper(), 1.0)


# =============================================================================
# TRUCK KNOWLEDGE BASE
# =============================================================================

class TruckKnowledgeBase:
    """
    Knowledge base for trucks including:
    - Home/parking locations (for deadhead optimization)
    - Truck types and specialties
    - Capacity and efficiency data
    - Historical performance
    """

    def __init__(self):
        # Truck registry: truck_id/name -> knowledge
        self._trucks: Dict[str, Dict] = {}

        # Default operating hours
        self.default_start_time = time(6, 0)   # 6:00 AM
        self.default_end_time = time(18, 0)    # 6:00 PM
        self.default_work_hours = 10.0

    def register_truck(self,
                      truck_id: str,
                      truck_name: str,
                      truck_type: str = TruckType.END_DUMP,
                      capacity_tons: float = 22.0,
                      home_location: str = None,
                      home_city: str = None,
                      home_lat: float = None,
                      home_lon: float = None,
                      specialty_materials: List[str] = None,
                      avoid_materials: List[str] = None,
                      driver_preference: str = None,
                      notes: str = None):
        """Register a truck in the knowledge base"""

        type_chars = TruckType.get_characteristics(truck_type)

        self._trucks[truck_id] = {
            "id": truck_id,
            "name": truck_name,
            "type": truck_type,
            "type_name": type_chars["name"],
            "capacity_tons": capacity_tons or type_chars["typical_capacity_tons"],
            "home_location": home_location,
            "home_city": home_city,
            "home_coords": (home_lat, home_lon) if home_lat and home_lon else None,
            "specialty_materials": specialty_materials or [],
            "avoid_materials": avoid_materials or [],
            "driver_preference": driver_preference,
            "notes": notes,
            # Derived from type
            "load_time_minutes": type_chars["load_time_minutes"],
            "unload_time_minutes": type_chars["unload_time_minutes"],
            "fuel_efficiency_mpg": type_chars["fuel_efficiency_mpg"],
            "avg_speed_loaded_mph": type_chars["avg_speed_loaded_mph"],
            "avg_speed_empty_mph": type_chars["avg_speed_empty_mph"],
            "best_for": type_chars["best_for"],
        }

    def get_truck(self, truck_id: str) -> Optional[Dict]:
        """Get truck knowledge by ID"""
        return self._trucks.get(str(truck_id))

    def get_all_trucks(self) -> Dict[str, Dict]:
        """Get all registered trucks"""
        return self._trucks.copy()

    def update_truck(self, truck_id: str, **kwargs):
        """Update truck properties"""
        if truck_id in self._trucks:
            self._trucks[truck_id].update(kwargs)


# =============================================================================
# ROUTE & DESTINATION KNOWLEDGE
# =============================================================================

class RouteKnowledge:
    """
    Knowledge about routes, destinations, and travel times.
    Pre-computed distances and times for common routes.
    """

    # Georgia coordinates (approximate city centers)
    GA_COORDINATES = {
        # Coastal Georgia
        "brunswick": (31.1499, -81.4915),
        "savannah": (32.0809, -81.0912),
        "hinesville": (31.8468, -81.5956),
        "statesboro": (32.4488, -81.7832),
        "jesup": (31.6074, -81.8856),
        "waycross": (31.2136, -82.3540),

        # Central Georgia
        "macon": (32.8407, -83.6324),
        "dublin": (32.5404, -82.9037),
        "vidalia": (32.2179, -82.4134),
        "swainsboro": (32.5974, -82.3335),

        # South Carolina
        "beaufort": (32.4316, -80.6698),
        "bluffton": (32.2371, -80.8604),
        "hardeeville": (32.2871, -81.0804),
        "ridgeland": (32.4807, -80.9801),

        # Pickup locations (quarries/suppliers)
        "garden_city": (32.0965, -81.1576),  # Vulcan
        "pembroke": (32.1368, -81.6245),      # Martin Marietta
        "lake_park": (30.6869, -83.1823),     # Martin Marietta
        "folkston": (30.8307, -82.0098),      # E.R. Jahna
        "kingsland": (30.7997, -81.6898),     # E.R. Jahna
        "tillman": (32.4538, -81.1217),       # Cemex (SC)
    }

    # Pre-computed distances (miles) between common points
    # Format: (origin, destination) -> miles
    DISTANCE_MATRIX = {
        # Brunswick to suppliers
        ("brunswick", "garden_city"): 78,
        ("brunswick", "pembroke"): 85,
        ("brunswick", "folkston"): 42,
        ("brunswick", "kingsland"): 25,

        # Savannah area to suppliers
        ("savannah", "garden_city"): 8,
        ("savannah", "pembroke"): 35,

        # SC to suppliers
        ("beaufort", "tillman"): 35,
        ("bluffton", "tillman"): 28,
        ("hardeeville", "tillman"): 15,
        ("ridgeland", "tillman"): 22,

        # Macon area
        ("macon", "dublin"): 55,
        ("dublin", "vidalia"): 40,
    }

    # Road condition factors (multiplier for travel time)
    ROAD_CONDITIONS = {
        "highway": 1.0,      # Normal highway
        "urban": 1.3,        # City traffic
        "rural": 1.1,        # Back roads
        "construction": 1.5, # Construction zones
    }

    def __init__(self):
        self._custom_distances: Dict[Tuple[str, str], float] = {}
        self._location_coords: Dict[str, Tuple[float, float]] = dict(self.GA_COORDINATES)

    def add_location(self, name: str, lat: float, lon: float):
        """Add a new location with coordinates"""
        self._location_coords[name.lower()] = (lat, lon)

    def get_distance(self, origin: str, destination: str) -> float:
        """
        Get distance between two points in miles.
        Uses pre-computed matrix first, then calculates from coordinates.
        """
        origin_key = origin.lower().replace(" ", "_")
        dest_key = destination.lower().replace(" ", "_")

        # Check pre-computed matrix
        if (origin_key, dest_key) in self.DISTANCE_MATRIX:
            return self.DISTANCE_MATRIX[(origin_key, dest_key)]
        if (dest_key, origin_key) in self.DISTANCE_MATRIX:
            return self.DISTANCE_MATRIX[(dest_key, origin_key)]

        # Check custom distances
        if (origin_key, dest_key) in self._custom_distances:
            return self._custom_distances[(origin_key, dest_key)]

        # Calculate from coordinates
        if origin_key in self._location_coords and dest_key in self._location_coords:
            return self._haversine_distance(
                self._location_coords[origin_key],
                self._location_coords[dest_key]
            )

        # Default estimate
        return 50.0  # Conservative default

    def _haversine_distance(self, coord1: Tuple[float, float],
                           coord2: Tuple[float, float]) -> float:
        """Calculate distance between coordinates using Haversine formula"""
        R = 3959  # Earth's radius in miles

        lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
        lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))

        # Apply road factor (roads are ~1.3x straight-line distance)
        return R * c * 1.3

    def set_custom_distance(self, origin: str, destination: str, miles: float):
        """Set a custom distance between two points"""
        origin_key = origin.lower().replace(" ", "_")
        dest_key = destination.lower().replace(" ", "_")
        self._custom_distances[(origin_key, dest_key)] = miles
        self._custom_distances[(dest_key, origin_key)] = miles


# =============================================================================
# PRODUCTIVITY CALCULATOR
# =============================================================================

class ProductivityCalculator:
    """
    Calculates realistic productivity metrics:
    - Cycle time (load + travel + unload + return)
    - Loads per day
    - Tons per day
    - Cost per ton
    """

    # Efficiency factors
    EFFICIENCY_FACTOR = 0.85  # 85% efficiency (breaks, delays, etc.)
    WAIT_TIME_FACTOR = 0.1    # 10% of cycle for waiting

    def __init__(self, route_knowledge: RouteKnowledge = None):
        self.routes = route_knowledge or RouteKnowledge()

    def calculate_cycle_time(self,
                            distance_miles: float,
                            truck_type: str = TruckType.END_DUMP,
                            material_code: str = "57",
                            road_type: str = "highway") -> Dict[str, float]:
        """
        Calculate complete cycle time for a route.

        Returns:
            Dict with breakdown of times in hours
        """
        type_chars = TruckType.get_characteristics(truck_type)

        # Speed adjustments
        speed_loaded = type_chars["avg_speed_loaded_mph"]
        speed_empty = type_chars["avg_speed_empty_mph"]

        # Apply road condition factor
        road_factor = RouteKnowledge.ROAD_CONDITIONS.get(road_type, 1.0)
        speed_loaded /= road_factor
        speed_empty /= road_factor

        # Travel times
        travel_loaded_hours = distance_miles / speed_loaded
        travel_empty_hours = distance_miles / speed_empty

        # Load/unload times (in hours)
        base_load_time = type_chars["load_time_minutes"] / 60
        base_unload_time = type_chars["unload_time_minutes"] / 60

        # Apply material factors
        load_factor = MaterialKnowledge.get_load_time_factor(material_code)
        unload_factor = MaterialKnowledge.get_unload_time_factor(material_code)

        load_time_hours = base_load_time * load_factor
        unload_time_hours = base_unload_time * unload_factor

        # Wait time (queuing at plant, etc.)
        subtotal = travel_loaded_hours + travel_empty_hours + load_time_hours + unload_time_hours
        wait_time_hours = subtotal * self.WAIT_TIME_FACTOR

        # Total cycle time
        total_cycle_hours = subtotal + wait_time_hours

        return {
            "travel_loaded_hours": round(travel_loaded_hours, 2),
            "travel_empty_hours": round(travel_empty_hours, 2),
            "load_time_hours": round(load_time_hours, 2),
            "unload_time_hours": round(unload_time_hours, 2),
            "wait_time_hours": round(wait_time_hours, 2),
            "total_cycle_hours": round(total_cycle_hours, 2),
            "total_cycle_minutes": round(total_cycle_hours * 60, 0),
        }

    def calculate_daily_productivity(self,
                                    distance_miles: float,
                                    truck_type: str = TruckType.END_DUMP,
                                    truck_capacity_tons: float = None,
                                    material_code: str = "57",
                                    work_hours: float = 10.0,
                                    road_type: str = "highway") -> Dict[str, Any]:
        """
        Calculate realistic daily productivity for a truck on a route.

        This is the KEY function for smart dispatch - tells you how many
        tons a truck can realistically move in a day on a specific route.

        Args:
            distance_miles: One-way distance to destination
            truck_type: Type of truck
            truck_capacity_tons: Override truck capacity (optional)
            material_code: Material being hauled
            work_hours: Available work hours
            road_type: Road conditions

        Returns:
            Dict with loads_per_day, tons_per_day, and breakdown
        """
        type_chars = TruckType.get_characteristics(truck_type)

        # Get capacity
        capacity = truck_capacity_tons or type_chars["typical_capacity_tons"]

        # Calculate cycle time
        cycle = self.calculate_cycle_time(
            distance_miles, truck_type, material_code, road_type
        )

        # Effective work hours (with efficiency factor)
        effective_hours = work_hours * self.EFFICIENCY_FACTOR

        # Loads per day
        if cycle["total_cycle_hours"] > 0:
            theoretical_loads = effective_hours / cycle["total_cycle_hours"]
            # Round down - can't do partial loads
            loads_per_day = int(theoretical_loads)
        else:
            loads_per_day = 0

        # Tons per day
        tons_per_day = loads_per_day * capacity

        # Determine haul category
        round_trip = distance_miles * 2
        if round_trip <= 30:
            haul_category = "short"
        elif round_trip <= 80:
            haul_category = "medium"
        else:
            haul_category = "long"

        return {
            "distance_miles": distance_miles,
            "round_trip_miles": round(distance_miles * 2, 1),
            "truck_type": truck_type,
            "truck_capacity_tons": capacity,
            "material_code": material_code,
            "work_hours": work_hours,
            "effective_hours": round(effective_hours, 1),
            "cycle_time_hours": cycle["total_cycle_hours"],
            "cycle_time_minutes": cycle["total_cycle_minutes"],
            "loads_per_day": loads_per_day,
            "tons_per_day": round(tons_per_day, 1),
            "haul_category": haul_category,
            "cycle_breakdown": cycle,
            # Additional metrics
            "tons_per_hour": round(tons_per_day / work_hours, 1) if work_hours > 0 else 0,
            "miles_per_load": round(distance_miles * 2, 1),
            "is_efficient": tons_per_day >= capacity * 3,  # At least 3 loads = efficient
        }

    def estimate_route_productivity(self,
                                   origin_city: str,
                                   destination_city: str,
                                   truck_type: str = TruckType.END_DUMP,
                                   truck_capacity_tons: float = None,
                                   material_code: str = "57",
                                   work_hours: float = 10.0) -> Dict[str, Any]:
        """
        Estimate productivity for a route between two cities.
        Uses route knowledge to get distance.
        """
        distance = self.routes.get_distance(origin_city, destination_city)

        result = self.calculate_daily_productivity(
            distance_miles=distance,
            truck_type=truck_type,
            truck_capacity_tons=truck_capacity_tons,
            material_code=material_code,
            work_hours=work_hours
        )

        result["origin"] = origin_city
        result["destination"] = destination_city

        return result


# =============================================================================
# OPERATING HOURS & CONSTRAINTS
# =============================================================================

class OperatingConstraints:
    """
    Manages operating hours and other constraints:
    - Work day limits
    - Hours of Service (HOS) compliance
    - Supplier operating hours
    - Plant receiving hours
    """

    # Supplier operating hours
    SUPPLIER_HOURS = {
        "martin_marietta": {
            "open": time(6, 0),
            "close": time(17, 0),
            "saturday": time(12, 0),  # Closes early Saturday
            "sunday": None,           # Closed
        },
        "vulcan": {
            "open": time(6, 0),
            "close": time(16, 30),
            "saturday": time(12, 0),
            "sunday": None,
        },
        "er_jahna": {
            "open": time(6, 0),
            "close": time(17, 0),
            "saturday": time(12, 0),
            "sunday": None,
        },
        "cemex": {
            "open": time(6, 0),
            "close": time(17, 0),
            "saturday": None,
            "sunday": None,
        },
        "east_coast_terminal": {
            "open": time(6, 0),
            "close": time(16, 0),
            "saturday": None,
            "sunday": None,
        },
    }

    # Maximum driving hours per day (DOT)
    MAX_DRIVING_HOURS = 11.0
    MAX_ON_DUTY_HOURS = 14.0

    def __init__(self):
        self.work_start = time(6, 0)
        self.work_end = time(18, 0)

    def get_available_work_hours(self,
                                 date: datetime = None,
                                 start_time: time = None) -> float:
        """Calculate available work hours for the day"""
        if date is None:
            date = datetime.now()

        start = start_time or self.work_start

        # Check if weekend
        if date.weekday() == 6:  # Sunday
            return 0.0
        elif date.weekday() == 5:  # Saturday
            # Reduced hours
            return 6.0

        # Calculate hours from start to end
        start_dt = datetime.combine(date.date(), start)
        end_dt = datetime.combine(date.date(), self.work_end)

        if start_dt >= end_dt:
            return 0.0

        hours = (end_dt - start_dt).total_seconds() / 3600
        return min(hours, self.MAX_ON_DUTY_HOURS)

    def is_supplier_open(self, supplier_name: str,
                        check_time: datetime = None) -> bool:
        """Check if a supplier is currently open"""
        if check_time is None:
            check_time = datetime.now()

        supplier_key = supplier_name.lower().replace(" ", "_")
        hours = self.SUPPLIER_HOURS.get(supplier_key)

        if not hours:
            return True  # Assume open if unknown

        weekday = check_time.weekday()
        current_time = check_time.time()

        if weekday == 6:  # Sunday
            return hours.get("sunday") is not None
        elif weekday == 5:  # Saturday
            close_time = hours.get("saturday")
            if close_time is None:
                return False
            return hours["open"] <= current_time <= close_time
        else:
            return hours["open"] <= current_time <= hours["close"]

    def can_complete_load(self,
                         cycle_time_hours: float,
                         current_time: datetime = None) -> Tuple[bool, str]:
        """
        Check if a driver can complete another load before end of day.

        Returns:
            (can_complete, reason)
        """
        if current_time is None:
            current_time = datetime.now()

        completion_time = current_time + timedelta(hours=cycle_time_hours)

        if completion_time.time() > self.work_end:
            return False, f"Would finish at {completion_time.strftime('%H:%M')}, past {self.work_end.strftime('%H:%M')}"

        return True, "OK"


# =============================================================================
# SMART SCORING ENGINE
# =============================================================================

class SmartScoringEngine:
    """
    Multi-factor scoring for dispatch optimization.
    Considers:
    - Productivity (tons per day)
    - Cost efficiency
    - Truck suitability
    - Deadhead distance (from home location)
    - Driver workload balance
    - Material constraints
    """

    # Scoring weights (must sum to 1.0)
    WEIGHTS = {
        "productivity": 0.30,      # Tons per day potential
        "cost_efficiency": 0.20,   # Cost per ton
        "truck_suitability": 0.15, # Right truck for the job
        "deadhead": 0.15,          # Distance from truck home
        "workload_balance": 0.10,  # Balance across drivers
        "constraints": 0.10,       # Meets all constraints
    }

    def __init__(self,
                 truck_knowledge: TruckKnowledgeBase,
                 route_knowledge: RouteKnowledge,
                 productivity_calc: ProductivityCalculator,
                 constraints: OperatingConstraints):
        self.trucks = truck_knowledge
        self.routes = route_knowledge
        self.productivity = productivity_calc
        self.constraints = constraints

    def score_assignment(self,
                        truck_id: str,
                        driver_id: str,
                        pickup_location: str,
                        destination: str,
                        material_code: str,
                        quantity_tons: float,
                        current_loads_today: int = 0,
                        all_driver_loads: Dict[str, int] = None) -> Dict[str, Any]:
        """
        Calculate a comprehensive score for assigning a truck to a delivery.

        Returns:
            Dict with total_score, component scores, and reasoning
        """
        truck = self.trucks.get_truck(truck_id)
        if not truck:
            # Use defaults if truck not in knowledge base
            truck = {
                "type": TruckType.END_DUMP,
                "capacity_tons": 22,
                "home_city": None,
            }

        scores = {}
        reasoning = []

        # 1. Productivity Score
        distance = self.routes.get_distance(pickup_location, destination)
        prod = self.productivity.calculate_daily_productivity(
            distance_miles=distance,
            truck_type=truck.get("type", TruckType.END_DUMP),
            truck_capacity_tons=truck.get("capacity_tons"),
            material_code=material_code
        )

        # Score based on tons per day (100+ tons = 1.0, 50 tons = 0.5, etc.)
        tons_target = 100  # Target tons per day
        scores["productivity"] = min(1.0, prod["tons_per_day"] / tons_target)
        reasoning.append(f"Can haul {prod['tons_per_day']} tons/day ({prod['loads_per_day']} loads)")

        # 2. Cost Efficiency Score
        # Calculate cost per ton
        if prod["tons_per_day"] > 0:
            # Estimate daily cost (fuel + driver)
            fuel_cost = (distance * 2 * prod["loads_per_day"]) / 6.0 * 3.50
            driver_cost = prod["work_hours"] * 25.0
            total_daily_cost = fuel_cost + driver_cost
            cost_per_ton = total_daily_cost / prod["tons_per_day"]

            # $5/ton = 1.0, $15/ton = 0.5, $25/ton = 0.0
            scores["cost_efficiency"] = max(0, 1.0 - (cost_per_ton - 5) / 20)
            reasoning.append(f"Cost: ${cost_per_ton:.2f}/ton")
        else:
            scores["cost_efficiency"] = 0
            reasoning.append("Cannot complete any loads")

        # 3. Truck Suitability Score
        type_chars = TruckType.get_characteristics(truck.get("type", TruckType.END_DUMP))
        suitability = 0.7  # Base score

        # Check material handling
        if material_code.upper() in ["SAND", "57", "57S", "89", "89S", "67", "67S"]:
            if truck.get("type") == TruckType.BELLY_DUMP:
                suitability = 1.0  # Belly dumps excellent for aggregates
                reasoning.append("Belly dump ideal for aggregates")

        # Check distance suitability
        if distance > 40 and "long_haul" in type_chars.get("best_for", []):
            suitability = min(1.0, suitability + 0.2)
            reasoning.append("Long dump good for long haul")
        elif distance < 20 and "short_haul" in type_chars.get("best_for", []):
            suitability = min(1.0, suitability + 0.2)
            reasoning.append("Short dump good for short haul")

        # Check capacity vs quantity
        if truck.get("capacity_tons", 22) >= quantity_tons:
            suitability = min(1.0, suitability + 0.1)
        else:
            suitability = max(0, suitability - 0.3)
            reasoning.append("Truck capacity may be insufficient")

        scores["truck_suitability"] = suitability

        # 4. Deadhead Score (distance from truck's home to pickup)
        if truck.get("home_city"):
            deadhead = self.routes.get_distance(truck["home_city"], pickup_location)
            # 0 miles = 1.0, 50 miles = 0.5, 100 miles = 0.0
            scores["deadhead"] = max(0, 1.0 - deadhead / 100)
            if deadhead > 30:
                reasoning.append(f"Deadhead: {deadhead:.0f} miles from home")
        else:
            scores["deadhead"] = 0.7  # Neutral if no home location known

        # 5. Workload Balance Score
        if all_driver_loads:
            avg_loads = sum(all_driver_loads.values()) / max(1, len(all_driver_loads))
            deviation = abs(current_loads_today - avg_loads)
            # 0 deviation = 1.0, 5+ deviation = 0.0
            scores["workload_balance"] = max(0, 1.0 - deviation / 5)
            if deviation > 2:
                reasoning.append(f"Driver has {current_loads_today} loads (avg: {avg_loads:.1f})")
        else:
            scores["workload_balance"] = 0.8

        # 6. Constraints Score
        constraint_score = 1.0

        # Check if supplier is open
        if not self.constraints.is_supplier_open(pickup_location):
            constraint_score *= 0.5
            reasoning.append("Supplier may be closed")

        # Check if can complete load today
        can_complete, reason = self.constraints.can_complete_load(
            prod["cycle_time_hours"]
        )
        if not can_complete:
            constraint_score *= 0.3
            reasoning.append(f"Time constraint: {reason}")

        scores["constraints"] = constraint_score

        # Calculate weighted total score
        total_score = sum(
            scores[key] * self.WEIGHTS[key]
            for key in self.WEIGHTS
        )

        return {
            "total_score": round(total_score * 100, 1),  # 0-100 scale
            "confidence": round(total_score * 100, 1),
            "scores": {k: round(v * 100, 1) for k, v in scores.items()},
            "productivity": prod,
            "reasoning": reasoning,
            "recommendation_quality": self._quality_label(total_score),
        }

    def _quality_label(self, score: float) -> str:
        """Get quality label for a score"""
        if score >= 0.8:
            return "excellent"
        elif score >= 0.6:
            return "good"
        elif score >= 0.4:
            return "fair"
        else:
            return "poor"


# =============================================================================
# MAIN AI DISPATCH ENGINE
# =============================================================================

class AIDispatchEngine:
    """
    Main AI dispatch engine that combines all knowledge bases
    and scoring to make smart dispatch recommendations.
    """

    def __init__(self):
        self.trucks = TruckKnowledgeBase()
        self.routes = RouteKnowledge()
        self.productivity = ProductivityCalculator(self.routes)
        self.constraints = OperatingConstraints()
        self.scorer = SmartScoringEngine(
            self.trucks, self.routes, self.productivity, self.constraints
        )

    def register_truck(self, **kwargs):
        """Register a truck in the knowledge base"""
        self.trucks.register_truck(**kwargs)

    def add_route(self, origin: str, destination: str, miles: float):
        """Add a custom route distance"""
        self.routes.set_custom_distance(origin, destination, miles)

    def add_location(self, name: str, lat: float, lon: float):
        """Add a location with coordinates"""
        self.routes.add_location(name, lat, lon)

    def calculate_productivity(self,
                              origin: str,
                              destination: str,
                              truck_type: str = TruckType.END_DUMP,
                              capacity_tons: float = None,
                              material: str = "57") -> Dict:
        """Calculate productivity for a route"""
        return self.productivity.estimate_route_productivity(
            origin, destination, truck_type, capacity_tons, material
        )

    def score_assignment(self,
                        truck_id: str,
                        driver_id: str,
                        pickup: str,
                        destination: str,
                        material: str,
                        quantity: float = 20.0,
                        current_loads: int = 0,
                        all_loads: Dict[str, int] = None) -> Dict:
        """Score an assignment"""
        return self.scorer.score_assignment(
            truck_id, driver_id, pickup, destination, material,
            quantity, current_loads, all_loads
        )

    def recommend_best_truck(self,
                            available_trucks: List[Dict],
                            pickup: str,
                            destination: str,
                            material: str,
                            quantity: float = 20.0,
                            driver_loads: Dict[str, int] = None) -> List[Dict]:
        """
        Recommend the best truck(s) for a delivery.

        Args:
            available_trucks: List of {"truck_id", "driver_id", "current_loads"}
            pickup: Pickup location
            destination: Delivery destination
            material: Material code
            quantity: Quantity in tons
            driver_loads: Dict of driver_id -> load count for workload balance

        Returns:
            Sorted list of recommendations with scores
        """
        recommendations = []

        for truck_info in available_trucks:
            score = self.score_assignment(
                truck_id=truck_info.get("truck_id"),
                driver_id=truck_info.get("driver_id"),
                pickup=pickup,
                destination=destination,
                material=material,
                quantity=quantity,
                current_loads=truck_info.get("current_loads", 0),
                all_loads=driver_loads
            )

            recommendations.append({
                "truck_id": truck_info.get("truck_id"),
                "driver_id": truck_info.get("driver_id"),
                "driver_name": truck_info.get("driver_name"),
                "truck_number": truck_info.get("truck_number"),
                **score
            })

        # Sort by total score descending
        recommendations.sort(key=lambda x: x["total_score"], reverse=True)

        return recommendations


# =============================================================================
# EXAMPLE USAGE & TESTING
# =============================================================================

def example_usage():
    """Example of how to use the AI Dispatch Engine"""

    # Initialize engine
    engine = AIDispatchEngine()

    # Register trucks with knowledge
    engine.register_truck(
        truck_id="1",
        truck_name="Thor",
        truck_type=TruckType.LONG_DUMP,
        capacity_tons=24,
        home_city="brunswick",
        notes="Long dump, good for highway hauls to Brunswick plant"
    )

    engine.register_truck(
        truck_id="2",
        truck_name="Hammer",
        truck_type=TruckType.SHORT_DUMP,
        capacity_tons=18,
        home_city="savannah",
        notes="Short dump, best for local Savannah area runs"
    )

    # Calculate productivity for Thor doing 57s to Brunswick
    prod = engine.calculate_productivity(
        origin="garden_city",  # Vulcan pickup
        destination="brunswick",
        truck_type=TruckType.LONG_DUMP,
        capacity_tons=24,
        material="57"
    )

    print(f"\n=== Thor: Garden City to Brunswick ===")
    print(f"Distance: {prod['distance_miles']} miles one-way")
    print(f"Cycle time: {prod['cycle_time_minutes']} minutes")
    print(f"Loads per day: {prod['loads_per_day']}")
    print(f"Tons per day: {prod['tons_per_day']}")
    print(f"Haul category: {prod['haul_category']}")
    print(f"Efficient: {prod['is_efficient']}")

    # Score an assignment
    score = engine.score_assignment(
        truck_id="1",
        driver_id="10",
        pickup="garden_city",
        destination="brunswick",
        material="57",
        quantity=24,
        current_loads=2
    )

    print(f"\n=== Assignment Score ===")
    print(f"Total Score: {score['total_score']}/100")
    print(f"Quality: {score['recommendation_quality']}")
    print(f"Reasoning: {', '.join(score['reasoning'])}")

    return engine


if __name__ == "__main__":
    example_usage()
