"""
Configuration file for Smyrna Ready Mix Dispatch System

Environment Variables (set these for production):
- DATABASE_PATH: Path to SQLite database file (default: database/srm_dispatch.db)
- SECRET_KEY: Flask secret key for session security
- GROQ_API_KEY: API key for Groq AI integration
- SAMSARA_API_TOKEN: API token for Samsara GPS integration
"""

import os

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
# Use DATABASE_PATH environment variable for persistent storage across deployments
# Example: export DATABASE_PATH=/var/data/srm_dispatch.db
DATABASE_PATH = os.environ.get('DATABASE_PATH', 'database/srm_dispatch.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'database', 'schema.sql')

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================
SECRET_KEY = os.environ.get('SECRET_KEY', 'srm-dispatch-secret-key-2024-change-in-production')
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

# =============================================================================
# SAMSARA API CONFIGURATION
# =============================================================================
SAMSARA_API_TOKEN = os.environ.get('SAMSARA_API_TOKEN')
SAMSARA_API_BASE_URL = "https://api.samsara.com"
SAMSARA_ENABLED = os.environ.get('SAMSARA_ENABLED', 'False').lower() in ('true', '1', 'yes')
SAMSARA_SYNC_INTERVAL = int(os.environ.get('SAMSARA_SYNC_INTERVAL', '300'))
SAMSARA_GEOFENCE_RADIUS = int(os.environ.get('SAMSARA_GEOFENCE_RADIUS', '100'))

# Legacy aliases (for backwards compatibility)
SAMARA_API_TOKEN = SAMSARA_API_TOKEN
SAMARA_API_BASE_URL = SAMSARA_API_BASE_URL
SAMARA_ENABLED = SAMSARA_ENABLED
SAMARA_SYNC_INTERVAL = SAMSARA_SYNC_INTERVAL
SAMARA_GEOFENCE_RADIUS = SAMSARA_GEOFENCE_RADIUS

# =============================================================================
# DEMO/SIMULATION MODE
# =============================================================================
# When True, simulates GPS tracking without actual Samsara API
DEMO_MODE = os.environ.get('DEMO_MODE', 'True').lower() in ('true', '1', 'yes')