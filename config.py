"""
Configuration file for Smyrna Ready Mix Dispatch System
"""

# Samsara API Configuration
SAMARA_API_TOKEN = None  # Add your Samsara API token here when you get it
SAMARA_API_BASE_URL = "https://api.samsara.com"

# Samara Integration Settings
SAMARA_ENABLED = False  # Set to True when you have API access
SAMARA_SYNC_INTERVAL = 300  # Sync interval in seconds (default: 5 minutes)
SAMARA_GEOFENCE_RADIUS = 100  # Default geofence radius in meters

# System Settings
DEBUG = True
SECRET_KEY = 'srm-dispatch-secret-key-2024-change-in-production'

# Database
DATABASE_PATH = 'database/srm_dispatch.db'

# Demo/Simulation Mode
# When True, simulates GPS tracking without actual Samara API
DEMO_MODE = True