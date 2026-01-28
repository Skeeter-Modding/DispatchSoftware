# Smyrna Ready Mix Dispatch System

A comprehensive dispatch management system for dump truck operations with automatic GPS tracking integration.

## Features

### 🚚 Core Functionality
- **Driver Management**: Add, edit, and manage drivers with contact information
- **Fleet Management**: Track trucks and trailers with capacity and maintenance info
- **Daily Assignments**: Link drivers to trucks and trailers for daily operations
- **Job Management**: Manage construction sites and delivery locations
- **Load Dispatch**: Create and track individual loads with status updates

### ⚡ Batch Dispatch
- **Multi-load Creation**: Create 4-10 loads per driver in one operation
- **Quick Templates**: Set product type, cubic yards, and delivery times
- **Time Scheduling**: Automatic scheduling with customizable intervals
- **Smart Routing**: Assign multiple jobs or repeat locations

### 📊 Dashboard & Tracking
- **Real-time Overview**: View today's assignments, loads, and statistics
- **Status Tracking**: Monitor load status (Assigned → En Route → At Job → Delivering → Complete)
- **Quick Actions**: Fast access to common operations
- **Auto-refresh**: Dashboard updates every 30 seconds

### 🛰️ Samara Integration (Auto Tracking)
- **GPS Tracking**: Automatic location updates from Samara devices
- **Geofence Detection**: Auto-update load status based on location
- **Real-time Sync**: Status updates synchronized every 5 minutes
- **Device Management**: Link Samara device IDs to trucks
- **Tracking History**: View location and timestamp history

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python app.py
```
The database will be automatically created on first run.

### 3. Load Sample Data (Optional)
```bash
python init_sample_data.py
```
This will populate the system with sample drivers, trucks, jobs, and loads for testing.

### 4. Start the Application
```bash
python app.py
```

### 5. Access the System
Open your browser and navigate to: `http://localhost:5000`

## System Architecture

### Database Structure
- **drivers**: Driver information and contact details
- **trucks**: Truck fleet with Samara device IDs
- **trailers**: Trailer inventory
- **assignments**: Daily driver-truck-trailer assignments
- **jobs**: Construction sites and delivery locations
- **loads**: Individual load records with status tracking
- **tracking_events**: GPS and location history from Samara

### Load Status Workflow
```
Assigned → En Route → At Job → Delivering → Complete
```

### Samara Integration
The system is designed to integrate with Samara GPS tracking devices:
1. Add Samara device ID to truck records
2. Enable tracking on loads (enabled by default)
3. Automatic status updates based on GPS location
4. Geofence detection for job sites
5. Real-time sync every 5 minutes

## Usage Guide

### Daily Workflow

1. **Morning Setup**
   - Create driver assignments (link drivers to trucks/trailers)
   - Verify Samara devices are linked to trucks
   - Check active jobs and locations

2. **Batch Dispatch (4-10 loads per driver)**
   - Go to Dispatch page
   - Click "Batch Create Loads"
   - Select drivers and load parameters
   - Set job, product type, cubic yards
   - Configure start time and intervals
   - Click "Create All Loads"

3. **Monitor Operations**
   - Dashboard shows real-time overview
   - Load Tracking page for detailed status
   - Samara Integration page for GPS updates

4. **Status Updates**
   - Automatic updates from Samara tracking
   - Manual status updates via dropdown
   - Tracking history maintained for each load

### Samara Setup

To enable automatic tracking:

1. Add Samara device IDs to trucks:
   - Go to Trucks → Add/Edit Truck
   - Enter Samara Device ID
   - Save changes

2. Configure geofences (optional):
   - Set geofence radius in Samara Integration
   - Define job site coordinates
   - Auto-update triggers on entry/exit

3. Monitor tracking:
   - Visit Samara Integration page
   - View currently tracked loads
   - Check sync status and history

## Sample Data

The system includes sample data for testing:
- 5 drivers with contact information
- 5 trucks with Samara devices linked
- 5 trailers
- 5 active job sites
- 5 daily assignments
- Multiple loads with various statuses

## Technical Stack

- **Backend**: Flask (Python 3.11)
- **Database**: SQLite
- **Frontend**: Bootstrap 5, jQuery
- **Icons**: Font Awesome 6
- **Tracking**: Samara API integration (structured for implementation)

## File Structure

```
srm_dispatch/
├── app.py                          # Main Flask application
├── init_sample_data.py            # Sample data initialization
├── requirements.txt                # Python dependencies
├── database/
│   ├── schema.sql                 # Database schema
│   └── srm_dispatch.db            # SQLite database (created on run)
├── templates/
│   ├── base.html                  # Base template
│   ├── dashboard.html             # Dashboard page
│   ├── dispatch.html              # Dispatch interface
│   ├── drivers.html               # Driver management
│   ├── trucks.html                # Truck management
│   ├── trailers.html              # Trailer management
│   ├── assignments.html           # Assignment management
│   ├── jobs.html                  # Job management
│   ├── loads.html                 # Load tracking
│   └── samara.html                # Samara integration
└── static/
    ├── css/
    │   └── style.css              # Custom styles
    └── js/
        └── main.js                # JavaScript functions
```

## Features for Smyrna Ready Mix

### Optimized for Daily Operations
- **No More Manual Tracking**: Batch dispatch creates 4-10 loads per driver instantly
- **Quick Assignment**: One-click driver-truck-trailer linking
- **Auto-Status Updates**: Samara tracking eliminates manual status checks
- **Real-time Dashboard**: See everything at a glance

### Scalability
- Supports unlimited drivers, trucks, and jobs
- Handles hundreds of daily loads
- Historical data retained indefinitely
- Fast SQLite database for quick queries

### Future Enhancements
- Mobile app for drivers
- Advanced reporting and analytics
- Invoice generation
- Customer notifications
- Weather integration
- Route optimization

## Support

For questions or issues with the dispatch system, contact your system administrator.

## License

Proprietary - Smyrna Ready Mix Internal Use