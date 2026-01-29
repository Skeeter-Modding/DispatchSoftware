"""
AI Dispatch Knowledge Base & Smart Optimization Engine
Smyrna Ready Mix Dispatch System

PROFESSIONAL-GRADE AGGREGATE HAULING INTELLIGENCE
=================================================

This module contains industry-accurate knowledge for dump truck dispatch:
- DOT weight regulations and bridge formula compliance
- Truck type specifications (tandem, tri-axle, quad, super dump, etc.)
- Material densities and handling characteristics
- Cycle time calculations (load, haul, dump, return, wait)
- Productivity metrics (loads/day, tons/day, cost/ton)
- Smart scoring for optimal truck-to-job matching

Industry Terminology:
- BOL: Bill of Lading - legal shipping document
- Scale Ticket: Weight ticket from certified scale
- Deadhead: Driving empty (no load) to pickup location
- Cycle Time: Complete round trip (load → haul → dump → return)
- Windrow: Line of material laid by belly dump for paving
- Stockpile: Material piled at job site or yard
"""

import math
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Tuple, Any


# =============================================================================
# DOT WEIGHT REGULATIONS & BRIDGE FORMULA
# =============================================================================

class DOTRegulations:
    """
    Federal and state DOT weight regulations.
    Based on Federal Bridge Gross Weight Formula.

    Federal Weight Limits:
    - Single axle: 20,000 lbs max
    - Tandem axle: 34,000 lbs max (two consecutive axles ≤96" apart)
    - Gross Vehicle Weight (Interstate): 80,000 lbs max

    Bridge Formula: W = 500 * ((LN)/(N-1) + 12N + 36)
    Where: W = max weight, L = axle spacing (ft), N = number of axles
    """

    # Federal axle weight limits (pounds)
    SINGLE_AXLE_MAX_LBS = 20000
    TANDEM_AXLE_MAX_LBS = 34000
    TRIDEM_AXLE_MAX_LBS = 42000

    # Gross vehicle weight limits
    INTERSTATE_GVW_MAX_LBS = 80000

    # Typical tare weights (empty truck weight in lbs)
    TARE_WEIGHTS = {
        "tandem": 20000,      # Tandem axle dump truck
        "tri_axle": 24000,    # Tri-axle dump truck
        "quad_axle": 28000,   # Quad-axle dump truck
        "semi_end_dump": 32000,  # Tractor + end dump trailer
        "semi_belly_dump": 34000,  # Tractor + belly dump trailer
        "transfer": 36000,    # Transfer truck + pup
    }

    @classmethod
    def calculate_max_payload_lbs(cls, truck_type: str, num_axles: int = 5) -> int:
        """Calculate maximum legal payload based on truck type and axles"""
        tare = cls.TARE_WEIGHTS.get(truck_type, 28000)
        max_gvw = cls.INTERSTATE_GVW_MAX_LBS
        return max_gvw - tare

    @classmethod
    def lbs_to_tons(cls, lbs: int) -> float:
        """Convert pounds to tons"""
        return lbs / 2000

    @classmethod
    def tons_to_lbs(cls, tons: float) -> int:
        """Convert tons to pounds"""
        return int(tons * 2000)


# =============================================================================
# TRUCK TYPE DEFINITIONS - INDUSTRY ACCURATE
# =============================================================================

class TruckType:
    """
    Industry-standard dump truck classifications.

    Axle Configurations:
    - Single axle: Rare, small jobs only (6-10 tons)
    - Tandem axle (10-wheeler): Most common, 12-18 tons
    - Tri-axle: 18-25 tons, versatile
    - Quad-axle: 22-28 tons, heavy hauls
    - Quint-axle: Up to 30 tons (requires permits in some states)

    Trailer Types:
    - End Dump: Hydraulic lift, dumps from rear. Most versatile.
    - Belly Dump (Bottom Dump): Clam-shell gates, windrow spreading.
      NOT for clay, large rocks, or sticky materials.
    - Side Dump: Tips sideways, very stable, good for rip-rap/boulders.
    - Transfer: Truck + pup trailer, highest capacity (38-40 tons).
    - Live Bottom: Conveyor floor, controlled unloading.
    """

    # Truck type constants - matches database truck_type field
    TANDEM = "tandem"                    # Tandem axle dump, no trailer (18 tons)
    TRI_AXLE = "tri_axle"                # Tri-axle dump truck (22 tons)
    QUAD_AXLE = "quad_axle"              # Quad-axle dump truck (25 tons)
    SUPER_DUMP = "super_dump"            # Super dump with strong-arm (26 tons)
    END_DUMP = "end_dump"                # Semi end dump trailer (25 tons)
    LONG_DUMP = "long_dump"              # Same as end_dump, legacy name
    BELLY_DUMP = "belly_dump"            # Bottom dump trailer (26 tons)
    SIDE_DUMP = "side_dump"              # Side dump trailer (24 tons)
    TRANSFER = "transfer"                # Transfer truck + pup (38 tons)
    LIVE_BOTTOM = "live_bottom"          # Conveyor bottom trailer (25 tons)
    LOWBOY = "lowboy"                    # Equipment hauler (NOT for aggregate)
    SHORT_DUMP = "short_dump"            # Legacy alias for tandem

    # Comprehensive truck characteristics - INDUSTRY ACCURATE
    CHARACTERISTICS = {
        TANDEM: {
            "name": "Tandem Axle Dump (10-Wheeler)",
            "description": "Standard tandem axle dump truck without trailer. Most maneuverable.",
            "axle_config": "tandem",
            "num_axles": 3,
            "typical_capacity_tons": 18,
            "min_capacity_tons": 14,
            "max_capacity_tons": 20,
            "cubic_yard_capacity": 10,  # Approximate
            "best_for": ["short_haul", "city_work", "tight_job_sites", "residential"],
            "material_handling": ["all"],  # Can handle any material
            "restrictions": [],
            "unload_time_minutes": 3,
            "load_time_minutes": 8,
            "fuel_efficiency_mpg": 6.0,
            "avg_speed_loaded_mph": 45,
            "avg_speed_empty_mph": 55,
            "hourly_operating_cost": 85,  # Fuel + maintenance + insurance
            "tare_weight_lbs": 20000,
            "notes": "Most common dump truck. Quick cycle times. Best for runs under 20 miles."
        },

        TRI_AXLE: {
            "name": "Tri-Axle Dump Truck",
            "description": "Three-axle dump truck. Good balance of capacity and maneuverability.",
            "axle_config": "tri-axle",
            "num_axles": 4,
            "typical_capacity_tons": 22,
            "min_capacity_tons": 18,
            "max_capacity_tons": 25,
            "cubic_yard_capacity": 14,
            "best_for": ["medium_haul", "commercial_sites", "road_construction"],
            "material_handling": ["all"],
            "restrictions": [],
            "unload_time_minutes": 4,
            "load_time_minutes": 10,
            "fuel_efficiency_mpg": 5.5,
            "avg_speed_loaded_mph": 50,
            "avg_speed_empty_mph": 55,
            "hourly_operating_cost": 95,
            "tare_weight_lbs": 24000,
            "notes": "Versatile workhorse. Good for most aggregate hauling jobs."
        },

        QUAD_AXLE: {
            "name": "Quad-Axle Dump Truck",
            "description": "Four-axle dump truck. Higher capacity, may need permits on some roads.",
            "axle_config": "quad-axle",
            "num_axles": 5,
            "typical_capacity_tons": 25,
            "min_capacity_tons": 22,
            "max_capacity_tons": 28,
            "cubic_yard_capacity": 16,
            "best_for": ["highway_haul", "large_volume_jobs", "DOT_work"],
            "material_handling": ["all"],
            "restrictions": ["weight_restricted_roads"],
            "unload_time_minutes": 5,
            "load_time_minutes": 12,
            "fuel_efficiency_mpg": 5.0,
            "avg_speed_loaded_mph": 50,
            "avg_speed_empty_mph": 55,
            "hourly_operating_cost": 105,
            "tare_weight_lbs": 28000,
            "notes": "High capacity. Check bridge postings and road restrictions."
        },

        SUPER_DUMP: {
            "name": "Super Dump (Strong-Arm)",
            "description": "Dump truck with trailing axle (strong-arm) for maximum legal payload.",
            "axle_config": "super-dump",
            "num_axles": 5,  # 3 + 2 trailing
            "typical_capacity_tons": 26,
            "min_capacity_tons": 24,
            "max_capacity_tons": 28,
            "cubic_yard_capacity": 18,
            "best_for": ["maximum_payload", "highway", "long_haul_aggregate"],
            "material_handling": ["all"],
            "restrictions": ["trailing_axle_requirements"],
            "unload_time_minutes": 5,
            "load_time_minutes": 12,
            "fuel_efficiency_mpg": 5.0,
            "avg_speed_loaded_mph": 50,
            "avg_speed_empty_mph": 55,
            "hourly_operating_cost": 110,
            "tare_weight_lbs": 26000,
            "notes": "Maximum legal payload without trailer. Strong-arm must be down when loaded."
        },

        END_DUMP: {
            "name": "Semi End Dump Trailer",
            "description": "Tractor pulling end dump trailer. Hydraulic hoist dumps from rear.",
            "axle_config": "semi-trailer",
            "num_axles": 5,
            "typical_capacity_tons": 25,
            "min_capacity_tons": 23,
            "max_capacity_tons": 28,
            "cubic_yard_capacity": 22,  # Frameless aluminum can be up to 40 cy
            "best_for": ["long_haul", "highway", "stockpiling", "demolition"],
            "material_handling": ["all"],
            "restrictions": ["tip_stability_on_slopes"],
            "unload_time_minutes": 5,
            "load_time_minutes": 12,
            "fuel_efficiency_mpg": 5.5,
            "avg_speed_loaded_mph": 55,
            "avg_speed_empty_mph": 62,
            "hourly_operating_cost": 120,
            "tare_weight_lbs": 32000,
            "notes": "Most versatile trailer. Watch for tip-over risk on uneven ground. Aluminum trailers maximize payload."
        },

        BELLY_DUMP: {
            "name": "Belly Dump (Bottom Dump) Trailer",
            "description": "Clam-shell gates on bottom. Spreads material in windrow while moving.",
            "axle_config": "semi-trailer",
            "num_axles": 5,
            "typical_capacity_tons": 26,
            "min_capacity_tons": 24,
            "max_capacity_tons": 30,
            "cubic_yard_capacity": 24,
            "best_for": ["paving", "road_base", "windrow_spreading", "continuous_paving"],
            "material_handling": ["sand", "gravel", "hot_mix_asphalt", "57", "67", "89", "GAB", "crush_run"],
            "restrictions": ["no_clay", "no_large_rocks", "no_cold_mix", "no_sticky_materials"],
            "unload_time_minutes": 2,  # Very fast - dumps while moving
            "load_time_minutes": 10,
            "fuel_efficiency_mpg": 5.0,
            "avg_speed_loaded_mph": 50,
            "avg_speed_empty_mph": 58,
            "hourly_operating_cost": 125,
            "tare_weight_lbs": 34000,
            "notes": "PAVING SPECIALIST. Continuous windrow keeps paver moving = better mat quality. NO clay, large rocks, or frost heave material - will hang up under axles!"
        },

        SIDE_DUMP: {
            "name": "Side Dump Trailer",
            "description": "Hydraulic tipping to the side. Most stable dump configuration.",
            "axle_config": "semi-trailer",
            "num_axles": 5,
            "typical_capacity_tons": 24,
            "min_capacity_tons": 22,
            "max_capacity_tons": 26,
            "cubic_yard_capacity": 23,
            "best_for": ["rip_rap", "boulders", "demolition", "uneven_terrain", "windy_conditions"],
            "material_handling": ["all", "large_rocks", "rip_rap", "demolition_debris"],
            "restrictions": [],
            "unload_time_minutes": 3,
            "load_time_minutes": 10,
            "fuel_efficiency_mpg": 5.0,
            "avg_speed_loaded_mph": 50,
            "avg_speed_empty_mph": 58,
            "hourly_operating_cost": 120,
            "tare_weight_lbs": 33000,
            "notes": "MOST STABLE dump configuration. Will not tip over like end dumps. Excellent for large rip-rap and boulders."
        },

        TRANSFER: {
            "name": "Transfer Dump (Truck + Pup)",
            "description": "Dump truck pulling a transfer (pup) trailer. Highest legal capacity.",
            "axle_config": "transfer",
            "num_axles": 7,
            "typical_capacity_tons": 38,
            "min_capacity_tons": 35,
            "max_capacity_tons": 42,
            "cubic_yard_capacity": 30,
            "best_for": ["maximum_volume", "long_haul", "large_jobs", "highway_construction"],
            "material_handling": ["aggregates", "sand", "gravel", "57", "67", "89"],
            "restrictions": ["length_restrictions", "some_job_site_access"],
            "unload_time_minutes": 8,  # Two dumps
            "load_time_minutes": 15,   # Two loads
            "fuel_efficiency_mpg": 4.5,
            "avg_speed_loaded_mph": 50,
            "avg_speed_empty_mph": 55,
            "hourly_operating_cost": 140,
            "tare_weight_lbs": 36000,
            "notes": "HIGHEST CAPACITY. Lead truck dumps first, then pup trailer. Best for long hauls where cycle time matters less than tonnage."
        },

        LIVE_BOTTOM: {
            "name": "Live Bottom (Walking Floor) Trailer",
            "description": "Conveyor belt or walking floor for controlled unloading.",
            "axle_config": "semi-trailer",
            "num_axles": 5,
            "typical_capacity_tons": 25,
            "min_capacity_tons": 23,
            "max_capacity_tons": 27,
            "cubic_yard_capacity": 22,
            "best_for": ["controlled_unload", "spreader_feeding", "asphalt_plants", "recycling"],
            "material_handling": ["all", "mulch", "woodchips", "recyclables"],
            "restrictions": ["slower_unload"],
            "unload_time_minutes": 10,  # Slower but controlled
            "load_time_minutes": 12,
            "fuel_efficiency_mpg": 5.0,
            "avg_speed_loaded_mph": 55,
            "avg_speed_empty_mph": 60,
            "hourly_operating_cost": 130,
            "tare_weight_lbs": 35000,
            "notes": "Controlled metered unloading. No tipping required - stable on any ground. Good for feeding equipment."
        },

        LOWBOY: {
            "name": "Lowboy / RGN (Equipment Hauler)",
            "description": "Low-deck trailer for hauling heavy equipment. NOT for aggregate.",
            "axle_config": "lowboy",
            "num_axles": 5,
            "typical_capacity_tons": 0,  # Does not haul aggregate
            "min_capacity_tons": 0,
            "max_capacity_tons": 0,
            "cubic_yard_capacity": 0,
            "equipment_capacity_lbs": 100000,  # Up to 50 tons of equipment
            "best_for": ["equipment_transport", "excavators", "dozers", "loaders"],
            "material_handling": [],  # Does NOT haul aggregate
            "restrictions": ["equipment_only", "no_aggregate"],
            "unload_time_minutes": 30,
            "load_time_minutes": 30,
            "fuel_efficiency_mpg": 4.5,
            "avg_speed_loaded_mph": 45,
            "avg_speed_empty_mph": 60,
            "hourly_operating_cost": 150,
            "tare_weight_lbs": 40000,
            "notes": "EQUIPMENT ONLY. Used for moving excavators, dozers, loaders, etc. Does NOT haul aggregate materials."
        },

        # Legacy aliases
        LONG_DUMP: {
            "name": "Long Dump (Semi End Dump)",
            "description": "Legacy name for semi end dump trailer.",
            "axle_config": "semi-trailer",
            "num_axles": 5,
            "typical_capacity_tons": 25,
            "min_capacity_tons": 23,
            "max_capacity_tons": 28,
            "cubic_yard_capacity": 22,
            "best_for": ["long_haul", "highway", "stockpiling"],
            "material_handling": ["all"],
            "restrictions": [],
            "unload_time_minutes": 5,
            "load_time_minutes": 12,
            "fuel_efficiency_mpg": 5.5,
            "avg_speed_loaded_mph": 55,
            "avg_speed_empty_mph": 62,
            "hourly_operating_cost": 120,
            "tare_weight_lbs": 32000,
            "notes": "Same as end_dump. Semi with end dump trailer."
        },

        SHORT_DUMP: {
            "name": "Short Dump (Tandem)",
            "description": "Legacy name for tandem axle dump.",
            "axle_config": "tandem",
            "num_axles": 3,
            "typical_capacity_tons": 18,
            "min_capacity_tons": 14,
            "max_capacity_tons": 20,
            "cubic_yard_capacity": 10,
            "best_for": ["short_haul", "city_work", "tight_spaces"],
            "material_handling": ["all"],
            "restrictions": [],
            "unload_time_minutes": 3,
            "load_time_minutes": 8,
            "fuel_efficiency_mpg": 6.0,
            "avg_speed_loaded_mph": 45,
            "avg_speed_empty_mph": 55,
            "hourly_operating_cost": 85,
            "tare_weight_lbs": 20000,
            "notes": "Same as tandem. Tandem axle dump truck."
        },
    }

    @classmethod
    def get_characteristics(cls, truck_type: str) -> Dict:
        """Get characteristics for a truck type"""
        truck_type_lower = (truck_type or "").lower().replace("-", "_").replace(" ", "_")
        return cls.CHARACTERISTICS.get(truck_type_lower, cls.CHARACTERISTICS[cls.END_DUMP])

    @classmethod
    def get_capacity_for_assignment(cls, truck_type: str, has_trailer: bool) -> float:
        """
        Determine capacity based on truck type and trailer status.
        Key business rule: With trailer = 25 tons, Tandem (no trailer) = 18 tons
        """
        if not has_trailer:
            # No trailer = tandem dump truck = 18 tons
            return 18.0

        # Has trailer - get from truck type characteristics
        chars = cls.get_characteristics(truck_type)
        return chars.get("typical_capacity_tons", 25.0)

    @classmethod
    def is_suitable_for_material(cls, truck_type: str, material_code: str) -> Tuple[bool, str]:
        """Check if truck type can handle a specific material"""
        chars = cls.get_characteristics(truck_type)

        # Lowboy can't haul any aggregate
        if truck_type == cls.LOWBOY:
            return False, "Lowboy is for equipment only, not aggregate"

        # Check belly dump restrictions
        if truck_type == cls.BELLY_DUMP:
            material_upper = material_code.upper()
            if material_upper in ["CLAY", "LARGE_ROCK", "BOULDER", "RIP_RAP", "COLD_MIX"]:
                return False, "Belly dump cannot handle clay, large rocks, or cold mix - material hangs up under axles"

        return True, "OK"

    @classmethod
    def get_all_types(cls) -> List[str]:
        """Get list of all truck types"""
        return [cls.TANDEM, cls.TRI_AXLE, cls.QUAD_AXLE, cls.SUPER_DUMP,
                cls.END_DUMP, cls.BELLY_DUMP, cls.SIDE_DUMP, cls.TRANSFER,
                cls.LIVE_BOTTOM, cls.LOWBOY]


# =============================================================================
# MATERIAL KNOWLEDGE - INDUSTRY ACCURATE DENSITIES
# =============================================================================

class MaterialKnowledge:
    """
    Aggregate material specifications and handling characteristics.

    Stone Gradations (ASTM/AASHTO):
    - #4: 1.5" - 0.75" (large stone, drainage)
    - #57: 1" - #4 (most common, driveways, concrete)
    - #67: 0.75" - #4 (concrete aggregate)
    - #89: 3/8" - #8 (small stone, asphalt, pipe bedding)
    - #10: Screenings (fines)

    Densities vary by moisture content and compaction.
    Listed values are "loose" (uncompacted) densities.
    """

    # Material density (tons per cubic yard) - INDUSTRY STANDARD VALUES
    DENSITIES = {
        # Stone products
        "57": 1.40,          # #57 stone - most common
        "57S": 1.40,
        "#57": 1.40,
        "67": 1.45,          # #67 stone
        "67S": 1.45,
        "#67": 1.45,
        "89": 1.35,          # #89 stone (pea gravel size)
        "89S": 1.35,
        "#89": 1.35,
        "4": 1.50,           # #4 stone (large)
        "4S": 1.50,
        "#4": 1.50,
        "10": 1.60,          # #10 screenings
        "SCREENINGS": 1.60,
        "3": 1.55,           # #3 stone
        "#3": 1.55,
        "1": 1.50,           # #1 stone
        "#1": 1.50,
        "RIP_RAP": 1.65,     # Large rip-rap stone
        "RIPRAP": 1.65,

        # Base materials
        "GAB": 1.55,         # Graded Aggregate Base
        "CRUSH_RUN": 1.55,   # Crusher run
        "CRUSHER_RUN": 1.55,
        "ABC": 1.55,         # Aggregate Base Course
        "ROAD_BASE": 1.50,

        # Sand products
        "SAND": 1.35,        # Concrete sand (dry)
        "CONCRETE_SAND": 1.35,
        "MASON_SAND": 1.30,  # Fine mason sand
        "FILL_SAND": 1.40,   # Fill sand
        "WASHED_SAND": 1.35,

        # Gravel
        "GRAVEL": 1.45,
        "PEA_GRAVEL": 1.40,
        "RIVER_ROCK": 1.55,

        # Specialty
        "ASPHALT": 2.20,     # Hot mix asphalt (HMA)
        "HMA": 2.20,
        "HOT_MIX": 2.20,
        "COLD_MIX": 2.10,
        "RAP": 2.00,         # Recycled Asphalt Pavement
        "MILLINGS": 1.80,

        # Fill materials
        "TOPSOIL": 1.10,
        "DIRT": 1.20,
        "FILL_DIRT": 1.25,
        "CLAY": 1.70,        # Heavy, sticky

        # Limestone products
        "57L": 1.45,         # #57 limestone
        "LIMESTONE": 1.45,
        "LIME_SCREENINGS": 1.55,

        # Recycled
        "CONCRETE_RUBBLE": 1.30,
        "RECYCLED_CONCRETE": 1.35,
    }

    # Load time adjustments by material (multiplier to base load time)
    LOAD_TIME_FACTORS = {
        "SAND": 0.90,        # Flows easily
        "57": 1.00,          # Standard
        "67": 1.00,
        "89": 0.95,          # Small stone loads fast
        "4": 1.15,           # Larger stones take longer
        "GAB": 1.05,         # Base material
        "ASPHALT": 0.85,     # Hot, flows fast
        "HMA": 0.85,
        "HOT_MIX": 0.85,
        "RIP_RAP": 1.30,     # Large pieces, careful loading
        "CLAY": 1.25,        # Sticky, harder to handle
        "TOPSOIL": 1.10,     # Can be lumpy
    }

    # Unload time adjustments by material (multiplier to base unload time)
    UNLOAD_TIME_FACTORS = {
        "SAND": 0.80,        # Flows out easily
        "57": 1.00,
        "67": 1.00,
        "89": 0.90,          # Small stone flows well
        "4": 1.20,           # May require bed vibration
        "ASPHALT": 0.75,     # Hot, flows very fast
        "HMA": 0.75,
        "HOT_MIX": 0.75,
        "RIP_RAP": 1.40,     # Large pieces, slow dump
        "CLAY": 1.50,        # Sticks to bed, may need to scrape
        "MILLINGS": 1.10,    # Can be sticky
    }

    # Material handling notes
    HANDLING_NOTES = {
        "ASPHALT": "TEMPERATURE CRITICAL: Keep covered, deliver within 2 hours of loading. Min 275°F at laydown.",
        "HMA": "TEMPERATURE CRITICAL: Keep covered, deliver within 2 hours of loading. Min 275°F at laydown.",
        "CLAY": "Sticks to bed - may need to scrape. Do not use belly dump.",
        "RIP_RAP": "Heavy pieces - use side dump for stability. Check truck capacity.",
        "SAND": "Can shift during transport - level load before highway.",
        "GAB": "Moisture content affects weight. May weigh more when wet.",
    }

    @classmethod
    def get_density(cls, material_code: str) -> float:
        """Get material density in tons per cubic yard"""
        code_upper = (material_code or "57").upper().replace("-", "_").replace(" ", "_")
        return cls.DENSITIES.get(code_upper, 1.40)  # Default to 57 stone density

    @classmethod
    def get_load_time_factor(cls, material_code: str) -> float:
        """Get load time adjustment factor"""
        code_upper = (material_code or "").upper().replace("-", "_")
        return cls.LOAD_TIME_FACTORS.get(code_upper, 1.0)

    @classmethod
    def get_unload_time_factor(cls, material_code: str) -> float:
        """Get unload time adjustment factor"""
        code_upper = (material_code or "").upper().replace("-", "_")
        return cls.UNLOAD_TIME_FACTORS.get(code_upper, 1.0)

    @classmethod
    def get_handling_notes(cls, material_code: str) -> str:
        """Get special handling notes for material"""
        code_upper = (material_code or "").upper().replace("-", "_")
        return cls.HANDLING_NOTES.get(code_upper, "")

    @classmethod
    def cubic_yards_to_tons(cls, cubic_yards: float, material_code: str) -> float:
        """Convert cubic yards to tons for a material"""
        density = cls.get_density(material_code)
        return cubic_yards * density

    @classmethod
    def tons_to_cubic_yards(cls, tons: float, material_code: str) -> float:
        """Convert tons to cubic yards for a material"""
        density = cls.get_density(material_code)
        return tons / density if density > 0 else 0


# =============================================================================
# TRUCK KNOWLEDGE BASE
# =============================================================================

class TruckKnowledgeBase:
    """
    Knowledge base for fleet trucks.
    Tracks truck specifications, home locations, and performance history.
    """

    def __init__(self):
        self._trucks: Dict[str, Dict] = {}
        self.default_start_time = time(6, 0)   # 6:00 AM
        self.default_end_time = time(18, 0)    # 6:00 PM
        self.default_work_hours = 10.0

    def register_truck(self,
                      truck_id: str,
                      truck_name: str,
                      truck_type: str = TruckType.END_DUMP,
                      capacity_tons: float = 25.0,
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

        self._trucks[str(truck_id)] = {
            "id": str(truck_id),
            "name": truck_name,
            "type": truck_type,
            "type_name": type_chars.get("name", "Unknown"),
            "capacity_tons": capacity_tons or type_chars.get("typical_capacity_tons", 25),
            "home_location": home_location,
            "home_city": home_city,
            "home_coords": (home_lat, home_lon) if home_lat and home_lon else None,
            "specialty_materials": specialty_materials or [],
            "avoid_materials": avoid_materials or [],
            "driver_preference": driver_preference,
            "notes": notes,
            # Derived from type
            "load_time_minutes": type_chars.get("load_time_minutes", 10),
            "unload_time_minutes": type_chars.get("unload_time_minutes", 5),
            "fuel_efficiency_mpg": type_chars.get("fuel_efficiency_mpg", 5.5),
            "avg_speed_loaded_mph": type_chars.get("avg_speed_loaded_mph", 50),
            "avg_speed_empty_mph": type_chars.get("avg_speed_empty_mph", 55),
            "hourly_operating_cost": type_chars.get("hourly_operating_cost", 100),
            "best_for": type_chars.get("best_for", []),
        }

    def get_truck(self, truck_id: str) -> Optional[Dict]:
        """Get truck knowledge by ID"""
        return self._trucks.get(str(truck_id))

    def get_all_trucks(self) -> Dict[str, Dict]:
        """Get all registered trucks"""
        return self._trucks.copy()

    def update_truck(self, truck_id: str, **kwargs):
        """Update truck properties"""
        if str(truck_id) in self._trucks:
            self._trucks[str(truck_id)].update(kwargs)


# =============================================================================
# ROUTE & DESTINATION KNOWLEDGE
# =============================================================================

class RouteKnowledge:
    """
    Route knowledge including distances, travel times, and conditions.
    Pre-computed distances for common routes in Southeast Georgia/South Carolina.
    """

    # Georgia/SC coordinates (approximate city centers)
    COORDINATES = {
        # Coastal Georgia
        "brunswick": (31.1499, -81.4915),
        "savannah": (32.0809, -81.0912),
        "hinesville": (31.8468, -81.5956),
        "statesboro": (32.4488, -81.7832),
        "jesup": (31.6074, -81.8856),
        "waycross": (31.2136, -82.3540),
        "kingsland": (30.7997, -81.6898),
        "st_marys": (30.7307, -81.5465),
        "darien": (31.3707, -81.4337),
        "richmond_hill": (31.9385, -81.3051),
        "pooler": (32.1157, -81.2470),
        "garden_city": (32.0965, -81.1576),
        "port_wentworth": (32.1496, -81.1634),

        # South Carolina Lowcountry
        "beaufort": (32.4316, -80.6698),
        "bluffton": (32.2371, -80.8604),
        "hilton_head": (32.2163, -80.7526),
        "hardeeville": (32.2871, -81.0804),
        "ridgeland": (32.4807, -80.9801),

        # Inland Georgia
        "macon": (32.8407, -83.6324),
        "dublin": (32.5404, -82.9037),
        "vidalia": (32.2179, -82.4134),
        "swainsboro": (32.5974, -82.3335),
        "baxley": (31.7788, -82.3487),
        "alma": (31.5393, -82.4621),

        # Quarry/Supplier locations
        "pembroke": (32.1368, -81.6245),      # Martin Marietta
        "lake_park": (30.6869, -83.1823),     # Martin Marietta
        "folkston": (30.8307, -82.0098),      # E.R. Jahna
        "tillman_sc": (32.4538, -81.1217),    # Cemex SC
        "bloomingdale": (32.1335, -81.3001),  # Local supplier
    }

    # Pre-computed distances (miles) - one-way
    DISTANCE_MATRIX = {
        # Brunswick area to suppliers
        ("brunswick", "garden_city"): 78,
        ("brunswick", "pembroke"): 85,
        ("brunswick", "folkston"): 42,
        ("brunswick", "kingsland"): 25,
        ("brunswick", "bloomingdale"): 65,

        # Savannah area to suppliers
        ("savannah", "garden_city"): 8,
        ("savannah", "pembroke"): 35,
        ("savannah", "bloomingdale"): 12,
        ("savannah", "tillman_sc"): 25,

        # SC Lowcountry
        ("beaufort", "tillman_sc"): 35,
        ("bluffton", "tillman_sc"): 28,
        ("hardeeville", "tillman_sc"): 15,
        ("ridgeland", "tillman_sc"): 22,
        ("hilton_head", "tillman_sc"): 40,

        # Hinesville/Fort Stewart area
        ("hinesville", "savannah"): 40,
        ("hinesville", "pembroke"): 25,
        ("hinesville", "garden_city"): 35,

        # Inland routes
        ("macon", "dublin"): 55,
        ("dublin", "vidalia"): 40,
        ("vidalia", "savannah"): 85,
    }

    # Road condition factors
    ROAD_CONDITIONS = {
        "interstate": 1.0,   # I-95, I-16
        "highway": 1.05,     # US highways
        "state_route": 1.10, # State routes
        "urban": 1.25,       # City traffic
        "rural": 1.15,       # Back roads
        "construction": 1.40, # Active construction zone
        "dirt_road": 1.50,   # Unpaved job site access
    }

    def __init__(self):
        self._custom_distances: Dict[Tuple[str, str], float] = {}
        self._custom_drive_times: Dict[Tuple[str, str], float] = {}
        self._location_coords: Dict[str, Tuple[float, float]] = dict(self.COORDINATES)

    def add_location(self, name: str, lat: float, lon: float):
        """Add a new location with coordinates"""
        self._location_coords[name.lower().replace(" ", "_")] = (lat, lon)

    def get_distance(self, origin: str, destination: str) -> float:
        """Get distance between two points in miles"""
        origin_key = origin.lower().replace(" ", "_")
        dest_key = destination.lower().replace(" ", "_")

        # Check pre-computed matrix (both directions)
        if (origin_key, dest_key) in self.DISTANCE_MATRIX:
            return self.DISTANCE_MATRIX[(origin_key, dest_key)]
        if (dest_key, origin_key) in self.DISTANCE_MATRIX:
            return self.DISTANCE_MATRIX[(dest_key, origin_key)]

        # Check custom distances
        if (origin_key, dest_key) in self._custom_distances:
            return self._custom_distances[(origin_key, dest_key)]
        if (dest_key, origin_key) in self._custom_distances:
            return self._custom_distances[(dest_key, origin_key)]

        # Calculate from coordinates
        if origin_key in self._location_coords and dest_key in self._location_coords:
            return self._haversine_distance(
                self._location_coords[origin_key],
                self._location_coords[dest_key]
            )

        # Default estimate
        return 50.0

    def _haversine_distance(self, coord1: Tuple[float, float],
                           coord2: Tuple[float, float]) -> float:
        """Calculate distance using Haversine formula"""
        R = 3959  # Earth's radius in miles

        lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
        lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))

        # Roads are typically 1.3x straight-line distance
        return round(R * c * 1.3, 1)

    def set_custom_distance(self, origin: str, destination: str, miles: float):
        """Set a custom distance between two points"""
        origin_key = origin.lower().replace(" ", "_")
        dest_key = destination.lower().replace(" ", "_")
        self._custom_distances[(origin_key, dest_key)] = miles
        self._custom_distances[(dest_key, origin_key)] = miles


# =============================================================================
# PRODUCTIVITY CALCULATOR - CYCLE TIME & DAILY OUTPUT
# =============================================================================

class ProductivityCalculator:
    """
    Calculates realistic productivity metrics for dump truck operations.

    Cycle Time Components:
    1. Load time - Time at quarry/supplier getting loaded
    2. Haul time (loaded) - Drive time to destination with material
    3. Dump/unload time - Time to dump material at job site
    4. Return time (empty) - Drive time back to pickup location
    5. Wait/queue time - Waiting at scale house, plant, or job site

    Daily Productivity:
    - Effective work hours ÷ cycle time = loads per day
    - Loads per day × tons per load = tons per day

    OVERTIME PAY (FACTORING):
    - Regular time: First 8 hours at base hourly rate
    - Overtime: Hours beyond 8 paid at 1.5x (time and a half)
    - This affects daily cost calculations and job profitability
    - Long hauls (>8 hours) incur overtime costs for factoring
    """

    # Efficiency factor accounts for breaks, delays, fuel stops
    EFFICIENCY_FACTOR = 0.85  # 85% of theoretical max

    # Wait time as percentage of cycle
    WAIT_TIME_PERCENT = 0.10  # 10% of cycle for queuing

    # Overtime configuration (for factoring/cost calculations)
    OVERTIME_THRESHOLD_HOURS = 8.0  # Hours before overtime kicks in
    OVERTIME_MULTIPLIER = 1.5  # Time and a half after 8 hours

    def __init__(self, route_knowledge: RouteKnowledge = None):
        self.routes = route_knowledge or RouteKnowledge()

    def calculate_cycle_time(self,
                            distance_miles: float,
                            truck_type: str = TruckType.END_DUMP,
                            material_code: str = "57",
                            road_type: str = "highway") -> Dict[str, float]:
        """
        Calculate complete cycle time for a route.

        Returns breakdown in hours and minutes.
        """
        type_chars = TruckType.get_characteristics(truck_type)

        # Get speeds
        speed_loaded = type_chars.get("avg_speed_loaded_mph", 50)
        speed_empty = type_chars.get("avg_speed_empty_mph", 55)

        # Apply road condition factor
        road_factor = RouteKnowledge.ROAD_CONDITIONS.get(road_type, 1.0)
        speed_loaded /= road_factor
        speed_empty /= road_factor

        # Travel times (hours)
        travel_loaded_hours = distance_miles / speed_loaded if speed_loaded > 0 else 0
        travel_empty_hours = distance_miles / speed_empty if speed_empty > 0 else 0

        # Load/unload times (convert minutes to hours)
        base_load_time = type_chars.get("load_time_minutes", 10) / 60
        base_unload_time = type_chars.get("unload_time_minutes", 5) / 60

        # Apply material factors
        load_factor = MaterialKnowledge.get_load_time_factor(material_code)
        unload_factor = MaterialKnowledge.get_unload_time_factor(material_code)

        load_time_hours = base_load_time * load_factor
        unload_time_hours = base_unload_time * unload_factor

        # Calculate subtotal
        subtotal = travel_loaded_hours + travel_empty_hours + load_time_hours + unload_time_hours

        # Add wait/queue time
        wait_time_hours = subtotal * self.WAIT_TIME_PERCENT

        # Total cycle time
        total_cycle_hours = subtotal + wait_time_hours

        return {
            "travel_loaded_hours": round(travel_loaded_hours, 3),
            "travel_empty_hours": round(travel_empty_hours, 3),
            "load_time_hours": round(load_time_hours, 3),
            "unload_time_hours": round(unload_time_hours, 3),
            "wait_time_hours": round(wait_time_hours, 3),
            "total_cycle_hours": round(total_cycle_hours, 3),
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

        This is the KEY function for smart dispatch optimization.
        """
        type_chars = TruckType.get_characteristics(truck_type)

        # Get capacity
        capacity = truck_capacity_tons or type_chars.get("typical_capacity_tons", 25)

        # Calculate cycle time
        cycle = self.calculate_cycle_time(distance_miles, truck_type, material_code, road_type)

        # Effective work hours
        effective_hours = work_hours * self.EFFICIENCY_FACTOR

        # Loads per day (integer - can't do partial loads)
        if cycle["total_cycle_hours"] > 0:
            theoretical_loads = effective_hours / cycle["total_cycle_hours"]
            loads_per_day = int(theoretical_loads)
        else:
            loads_per_day = 0

        # Tons per day
        tons_per_day = loads_per_day * capacity

        # Categorize haul distance
        round_trip = distance_miles * 2
        if round_trip <= 30:
            haul_category = "short"
        elif round_trip <= 80:
            haul_category = "medium"
        else:
            haul_category = "long"

        # Calculate cost metrics with overtime factoring
        hourly_cost = type_chars.get("hourly_operating_cost", 100)

        # Calculate overtime costs (time and a half after 8 hours)
        if work_hours <= self.OVERTIME_THRESHOLD_HOURS:
            regular_hours = work_hours
            overtime_hours = 0
            daily_cost = work_hours * hourly_cost
        else:
            regular_hours = self.OVERTIME_THRESHOLD_HOURS
            overtime_hours = work_hours - self.OVERTIME_THRESHOLD_HOURS
            # Regular hours at base rate + overtime at 1.5x rate
            daily_cost = (regular_hours * hourly_cost) + (overtime_hours * hourly_cost * self.OVERTIME_MULTIPLIER)

        cost_per_ton = daily_cost / tons_per_day if tons_per_day > 0 else 0

        return {
            "distance_miles": distance_miles,
            "round_trip_miles": round(distance_miles * 2, 1),
            "truck_type": truck_type,
            "truck_capacity_tons": capacity,
            "material_code": material_code,
            "work_hours": work_hours,
            "regular_hours": round(regular_hours, 2),
            "overtime_hours": round(overtime_hours, 2),
            "effective_hours": round(effective_hours, 2),
            "cycle_time_hours": cycle["total_cycle_hours"],
            "cycle_time_minutes": cycle["total_cycle_minutes"],
            "loads_per_day": loads_per_day,
            "tons_per_day": round(tons_per_day, 1),
            "haul_category": haul_category,
            "cycle_breakdown": cycle,
            "cost_per_ton": round(cost_per_ton, 2),
            "daily_cost": round(daily_cost, 2),
            "overtime_cost": round(overtime_hours * hourly_cost * (self.OVERTIME_MULTIPLIER - 1), 2) if overtime_hours > 0 else 0,
            "tons_per_hour": round(tons_per_day / work_hours, 1) if work_hours > 0 else 0,
            "is_efficient": loads_per_day >= 3,  # At least 3 loads = efficient route
            "has_overtime": overtime_hours > 0,
        }

    def estimate_route_productivity(self,
                                   origin_city: str,
                                   destination_city: str,
                                   truck_type: str = TruckType.END_DUMP,
                                   truck_capacity_tons: float = None,
                                   material_code: str = "57",
                                   work_hours: float = 10.0) -> Dict[str, Any]:
        """Estimate productivity for a route between two cities"""
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
    Operating hours and DOT compliance constraints.

    DOT Hours of Service (HOS):
    - 11 hours max driving time
    - 14 hours max on-duty time
    - 10 hours off-duty required between shifts
    """

    # Supplier operating hours
    SUPPLIER_HOURS = {
        "martin_marietta": {"open": time(6, 0), "close": time(17, 0), "saturday": time(12, 0)},
        "vulcan": {"open": time(6, 0), "close": time(16, 30), "saturday": time(12, 0)},
        "cemex": {"open": time(6, 0), "close": time(17, 0), "saturday": None},
        "hanson": {"open": time(6, 0), "close": time(17, 0), "saturday": time(12, 0)},
        "er_jahna": {"open": time(6, 0), "close": time(17, 0), "saturday": time(12, 0)},
    }

    # DOT limits
    MAX_DRIVING_HOURS = 11.0
    MAX_ON_DUTY_HOURS = 14.0
    REQUIRED_OFF_DUTY_HOURS = 10.0

    def __init__(self):
        self.work_start = time(6, 0)
        self.work_end = time(18, 0)

    def get_available_work_hours(self, date: datetime = None, start_time: time = None) -> float:
        """Calculate available work hours for the day"""
        if date is None:
            date = datetime.now()

        start = start_time or self.work_start

        # Weekend adjustments
        if date.weekday() == 6:  # Sunday
            return 0.0
        elif date.weekday() == 5:  # Saturday
            return 6.0

        # Calculate hours
        start_dt = datetime.combine(date.date(), start)
        end_dt = datetime.combine(date.date(), self.work_end)

        if start_dt >= end_dt:
            return 0.0

        hours = (end_dt - start_dt).total_seconds() / 3600
        return min(hours, self.MAX_ON_DUTY_HOURS)

    def is_supplier_open(self, supplier_name: str, check_time: datetime = None) -> bool:
        """Check if supplier is open"""
        if check_time is None:
            check_time = datetime.now()

        supplier_key = supplier_name.lower().replace(" ", "_")
        hours = self.SUPPLIER_HOURS.get(supplier_key)

        if not hours:
            return True  # Assume open if unknown

        weekday = check_time.weekday()
        current_time = check_time.time()

        if weekday == 6:  # Sunday - all closed
            return False
        elif weekday == 5:  # Saturday
            close_time = hours.get("saturday")
            if close_time is None:
                return False
            return hours["open"] <= current_time <= close_time
        else:
            return hours["open"] <= current_time <= hours["close"]

    def can_complete_load(self, cycle_time_hours: float, current_time: datetime = None) -> Tuple[bool, str]:
        """Check if driver can complete another load before end of day"""
        if current_time is None:
            current_time = datetime.now()

        completion_time = current_time + timedelta(hours=cycle_time_hours)

        if completion_time.time() > self.work_end:
            return False, f"Would finish at {completion_time.strftime('%H:%M')}"

        return True, "OK"


# =============================================================================
# SMART SCORING ENGINE
# =============================================================================

class SmartScoringEngine:
    """
    Multi-factor scoring for optimal truck-to-job assignment.

    Scoring Factors:
    1. Productivity (30%): Tons per day potential
    2. Cost Efficiency (20%): Cost per ton delivered
    3. Truck Suitability (15%): Right truck type for material/job
    4. Deadhead Distance (15%): Distance from truck home to pickup
    5. Workload Balance (10%): Fair distribution across drivers
    6. Constraint Compliance (10%): Meets time/regulation constraints
    """

    WEIGHTS = {
        "productivity": 0.30,
        "cost_efficiency": 0.20,
        "truck_suitability": 0.15,
        "deadhead": 0.15,
        "workload_balance": 0.10,
        "constraints": 0.10,
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
        """Calculate comprehensive score for a truck assignment"""

        truck = self.trucks.get_truck(truck_id)
        if not truck:
            truck = {
                "type": TruckType.END_DUMP,
                "capacity_tons": 25,
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

        # Score: 100+ tons/day = 1.0
        tons_target = 100
        scores["productivity"] = min(1.0, prod["tons_per_day"] / tons_target)
        reasoning.append(f"{prod['tons_per_day']} tons/day ({prod['loads_per_day']} loads)")

        # 2. Cost Efficiency Score
        if prod["tons_per_day"] > 0:
            cost_per_ton = prod["cost_per_ton"]
            # $5/ton = 1.0, $20/ton = 0.0
            scores["cost_efficiency"] = max(0, 1.0 - (cost_per_ton - 5) / 15)
            reasoning.append(f"${cost_per_ton:.2f}/ton")
        else:
            scores["cost_efficiency"] = 0
            reasoning.append("Cannot complete loads")

        # 3. Truck Suitability Score
        suitability = 0.7
        type_chars = TruckType.get_characteristics(truck.get("type", TruckType.END_DUMP))

        # Check material compatibility
        is_suitable, reason = TruckType.is_suitable_for_material(
            truck.get("type", TruckType.END_DUMP), material_code
        )
        if not is_suitable:
            suitability = 0.1
            reasoning.append(reason)

        # Check distance suitability
        if distance > 40 and "long_haul" in type_chars.get("best_for", []):
            suitability = min(1.0, suitability + 0.2)
        elif distance < 20 and "short_haul" in type_chars.get("best_for", []):
            suitability = min(1.0, suitability + 0.2)

        scores["truck_suitability"] = suitability

        # 4. Deadhead Score
        if truck.get("home_city"):
            deadhead = self.routes.get_distance(truck["home_city"], pickup_location)
            scores["deadhead"] = max(0, 1.0 - deadhead / 100)
            if deadhead > 30:
                reasoning.append(f"{deadhead:.0f}mi deadhead")
        else:
            scores["deadhead"] = 0.7

        # 5. Workload Balance Score
        if all_driver_loads:
            avg_loads = sum(all_driver_loads.values()) / max(1, len(all_driver_loads))
            deviation = abs(current_loads_today - avg_loads)
            scores["workload_balance"] = max(0, 1.0 - deviation / 5)
        else:
            scores["workload_balance"] = 0.8

        # 6. Constraints Score
        constraint_score = 1.0
        can_complete, msg = self.constraints.can_complete_load(prod["cycle_time_hours"])
        if not can_complete:
            constraint_score *= 0.3
            reasoning.append(f"Time: {msg}")

        scores["constraints"] = constraint_score

        # Calculate weighted total
        total_score = sum(scores[key] * self.WEIGHTS[key] for key in self.WEIGHTS)

        return {
            "total_score": round(total_score * 100, 1),
            "confidence": round(total_score * 100, 1),
            "scores": {k: round(v * 100, 1) for k, v in scores.items()},
            "productivity": prod,
            "reasoning": reasoning,
            "recommendation_quality": self._quality_label(total_score),
        }

    def _quality_label(self, score: float) -> str:
        if score >= 0.8:
            return "excellent"
        elif score >= 0.6:
            return "good"
        elif score >= 0.4:
            return "fair"
        return "poor"


# =============================================================================
# MAIN AI DISPATCH ENGINE
# =============================================================================

class AIDispatchEngine:
    """
    Main AI dispatch engine combining all knowledge bases
    for smart dispatch recommendations.
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
        """Register a truck"""
        self.trucks.register_truck(**kwargs)

    def add_route(self, origin: str, destination: str, miles: float):
        """Add a custom route distance"""
        self.routes.set_custom_distance(origin, destination, miles)

    def add_location(self, name: str, lat: float, lon: float):
        """Add a location"""
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
                        quantity: float = 25.0,
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
                            quantity: float = 25.0,
                            driver_loads: Dict[str, int] = None) -> List[Dict]:
        """Recommend best trucks for a delivery"""
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

        recommendations.sort(key=lambda x: x["total_score"], reverse=True)
        return recommendations


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    # Initialize engine
    engine = AIDispatchEngine()

    # Calculate productivity: Brunswick to Garden City with 25-ton end dump
    prod = engine.calculate_productivity(
        origin="garden_city",
        destination="brunswick",
        truck_type=TruckType.END_DUMP,
        capacity_tons=25,
        material="57"
    )

    print("=== Productivity Calculation ===")
    print(f"Route: Garden City → Brunswick ({prod['distance_miles']} miles)")
    print(f"Truck: End Dump, 25 tons")
    print(f"Cycle time: {prod['cycle_time_minutes']} minutes")
    print(f"Loads/day: {prod['loads_per_day']}")
    print(f"Tons/day: {prod['tons_per_day']}")
    print(f"Cost/ton: ${prod['cost_per_ton']}")
