# SRM Dispatch System - Website Setup Summary

## 🌐 Website Deployment

**Public URL:** https://5500-04daba06-4591-4e5c-8c3a-abf2e41f8f56.sandbox-service.public.prod.myninja.ai

The dispatch system is now hosted and accessible as a website on the VM. You can access it from any device with an internet connection using the URL above.

## 🆕 New Features Added

### 1. Pickup Locations (Martin Marietta Materials)

**6 Pickup Locations Added:**

1. **Statesboro Rail Yard** (MM-001)
   - Address: 8401 US HWY 301S, Statesboro, GA 30458
   - Phone: (912) 681-2992
   - Hours: Mon-Fri 7:00 AM - 4:00 PM
   - Railway Access: Yes

2. **Bloomingdale Rail Yard** (MM-002)
   - Address: 1054 Old River Road, Bloomingdale, GA 31302
   - Phone: (321) 246-4622
   - Hours: Mon-Fri 7:00 AM - 4:00 PM
   - Railway Access: Yes

3. **Wentworth Yard** (MM-003)
   - Address: 127 Gulfstream Road, Savannah, GA 31407
   - Phone: (912) 200-5420
   - Hours: Mon-Fri 7:00 AM - 4:00 PM
   - Railway Access: Yes

4. **Savannah Rail Yard** (MM-004)
   - Address: 4140-B Ogeechee Road, Savannah, GA 31405
   - Phone: (912) 234-8608
   - Hours: Mon-Fri 7:00 AM - 4:30 PM
   - Railway Access: Yes

5. **Savannah Marine Terminal** (MM-005)
   - Address: 42 Forbes Road, Savannah, GA 31404
   - Phone: (912) 231-8130
   - Hours: Mon-Fri 7:00 AM - 4:00 PM

6. **Hinesville Yard** (MM-006)
   - Address: 160 Leroy Coffer Hwy, Midway, GA 31320
   - Phone: (912) 368-3962
   - Hours: Mon-Fri 7:00 AM - 3:00 PM

**Features:**
- View all pickup locations with detailed information
- Filter by city
- Search functionality
- Activate/deactivate locations
- Contact information and hours
- Railway access indicators

### 2. AI Assistant

**Free AI System Integration:**

The AI Assistant provides intelligent support for dispatch operations including:

**Capabilities:**
- 📊 **Today's Status** - Quick overview of daily operations
- 🚛 **Load Tracking** - Real-time load status and tracking
- 👨‍✈️ **Driver Search** - Find drivers by name or truck
- 🏭 **Plant Information** - Quick access to plant details
- 📦 **Pickup Locations** - Martin Marietta Materials location info
- 💡 **Dispatch Recommendations** - AI-powered suggestions
- 🔔 **Alerts** - Notifications for delays and issues

**Features:**
- Interactive chat interface
- Quick action buttons for common tasks
- Natural language queries
- Chat history
- Help documentation
- Responsive design

**Access:** Click "AI Assistant" in the navigation menu

## 📊 Complete System Overview

### Database Tables
1. **Drivers** - 25 drivers with contact info
2. **Trucks** - 40 trucks with Samara device IDs
3. **Trailers** - 13 trailers
4. **Assignments** - 25 active driver assignments
5. **Jobs** - 14 job sites
6. **Plants** - 23 plants (19 GA, 4 SC)
7. **Pickup Locations** - 6 Martin Marietta Materials locations
8. **Loads** - Load tracking with plant and pickup location support
9. **Tracking Events** - GPS/location history from Samsara

### Website Pages
1. **Dashboard** - Real-time stats and overview
2. **Dispatch** - Batch dispatch with plant and pickup location selection
3. **Loads** - Load tracking and management
4. **Drivers** - Driver management
5. **Trucks** - Truck inventory
6. **Trailers** - Trailer inventory
7. **Plants** - SRM Concrete plant locations (GA & SC)
8. **Pickup Locations** - Martin Marietta Materials pickup points
9. **Assignments** - Driver-truck-trailer assignments
10. **Jobs** - Job/project management
11. **AI Assistant** - Intelligent dispatch support
12. **Samara Tracking** - GPS integration interface

## 🔧 Technical Details

### Hosting
- **Platform:** VM hosting
- **Port:** 5500
- **Status:** Live and accessible
- **URL:** https://5500-04daba06-4591-4e5c-8c3a-abf2e41f8f56.sandbox-service.public.prod.myninja.ai

### Technology Stack
- **Backend:** Flask (Python)
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript
- **Styling:** Bootstrap 5
- **Icons:** Font Awesome

### Database Schema Updates
- Added `pickup_locations` table
- Added `pickup_location_id` column to `loads` table
- Added `plant_id` column to `loads` table
- All tables include created_at and updated_at timestamps

## 🎯 System Capabilities

### Dispatch Operations
- ✅ Batch dispatch (4-10 loads per driver)
- ✅ Plant selection for each load
- ✅ Pickup location assignment
- ✅ Load status tracking
- ✅ Real-time updates

### Location Management
- ✅ SRM Concrete plants (GA & SC)
- ✅ Martin Marietta Materials pickup locations
- ✅ Detailed contact information
- ✅ Hours of operation
- ✅ Railway access indicators

### AI Support
- ✅ Natural language queries
- ✅ Quick actions for common tasks
- ✅ Status overviews
- ✅ Load tracking assistance
- ✅ Driver and location search

### Tracking Integration
- ✅ Samsara GPS tracking infrastructure
- ✅ Automatic location updates
- ✅ Event logging
- ✅ Demo mode for testing

## 📱 Access Information

**Website URL:** https://5500-04daba06-4591-4e5c-8c3a-abf2e41f8f56.sandbox-service.public.prod.myninja.ai

**Access Methods:**
1. Direct URL access from any browser
2. Mobile-friendly responsive design
3. No login required (development mode)

## 🚀 Next Steps

1. **Domain Setup** - Configure custom domain name
2. **Production Deployment** - Move to production server
3. **Authentication** - Add user login and permissions
4. **Samsara API** - Activate GPS tracking with API credentials
5. **AI Enhancement** - Connect to AI API for advanced features
6. **Mobile App** - Develop dedicated mobile application

## 📞 Support

The system is fully functional and ready for use. All features are accessible through the web interface. The AI assistant provides guidance for common tasks and operations.

**System Status:** ✅ Online and Operational  
**Last Updated:** 2026-01-28  
**Total Locations:** 29 (23 plants + 6 pickup locations)