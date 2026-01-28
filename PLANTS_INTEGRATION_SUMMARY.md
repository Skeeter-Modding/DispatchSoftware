# SRM Dispatch System - Plant Locations Integration Summary

## Overview
Successfully integrated SRM Concrete plant locations into the Smyrna Ready Mix dispatch system for Georgia (GA) and South Carolina (SC) operations.

## Plants Added

### Georgia Plants (19 locations)
From Macon southward as requested:

**Central/South Georgia:**
1. **Macon** - 191 Lower Elm St, Macon, GA 31206
2. **Dublin** - 2573 Georgia Highway 257, Dublin, GA 31021

**Savannah Area:**
3. **Garden City Savannah** - 4900 Old Louisville RD, Savannah, GA 31408
4. **Savannah** - 1075 Louisville Road, Savannah, GA 31415
5. **Pooler** - 186 Pine Barren Rd, Pooler, GA 31322
6. **Bloomingdale** - 1955 US Hwy 80, Bloomingdale, GA 31302

**Richmond Hill Area:**
7. **Richmond Hill Chandler** - 70 Chandler Street, Richmond Hill, GA 31324
8. **Richmond Hill Hwy 17** - 3105 US Highway 17, Richmond Hill, GA 31324

**Coastal Georgia:**
9. **Hinesville** - 7091 US HWY 84E, Hinesville, GA 31313
10. **Midway** - 321 Isaac Stevens Road, Midway, GA 31320
11. **Rincon** - 544 Ebenezer Rd, Rincon, GA 31326
12. **Guyton Hodgeville** - 883 Hodgeville Road, Guyton, GA 31312
13. **Statesboro** - 95 Olliff Rd, Statesboro, GA 30458
14. **Brunswick** - 508 Young Lane, Brunswick, GA 31520
15. **Kingsland** - 5784 Laurel Island Parkway, Kingsland, GA 31548

**Southwest Georgia:**
16. **Albany** - 1215 Wyandotte Drive, Albany, GA 31705
17. **Bainbridge** - 1103 Dothan Hwy, Bainbridge, GA 31717
18. **Thomasville** - 510 West Washington Street, Thomasville, GA 31792
19. **Tifton** - 101 Goff Street, Tifton, GA 31794

### South Carolina Plants (4 locations)
1. **Beaufort** (17043) - 30 Schwartz Rd Lot 9, Beaufort, SC 29906
2. **Bluffton** (17044) - 45 Sheridan Park Circle, Bluffton, SC 29910
3. **Hardeeville Stiney** (17017) - 1499 Stiney Rd., Hardeeville, SC 29927
4. **Ridgeland** (17032) - 204 Pearlstine Dr, Ridgeland, SC 29936

## System Updates

### Database Changes
1. **Added `plants` table** to store plant location information
   - Fields: id, plant_id, name, address, city, state, zip, phone, status, timestamps
   - Unique constraint on plant_id to prevent duplicates

2. **Updated `loads` table**
   - Added `plant_id` foreign key column
   - Links each load to its originating plant

### Application Updates
1. **New Plant Management Page** (`/plants`)
   - View all plant locations
   - Filter by state (GA/SC)
   - Search by name, city, or zip
   - Activate/deactivate plants
   - Statistics dashboard showing total plants by state

2. **Updated Dispatch Interface**
   - Added plant selection dropdown in batch dispatch modal
   - Plants are now selectable when creating loads
   - Load records include originating plant information

3. **Navigation Updates**
   - Added "Plants" link to Management dropdown menu

### API Endpoints
1. **`GET /plants`** - Plant management page
2. **`POST /api/plants/<id>/status`** - Update plant status (active/inactive)
3. **`GET /api/data?type=plants`** - Get active plants for dropdowns

## Data Source
Plant information sourced from SRM Concrete official website: https://www.smyrnareadymix.com/locations

## Current System Status
✅ **23 plants total** (19 GA, 4 SC)  
✅ All plants south of Macon, GA as requested  
✅ Plant management page fully functional  
✅ Plant selection integrated into dispatch workflow  
✅ Database schema updated and populated  
✅ Application running on port 5500  

## Files Modified
- `database/schema.sql` - Added plants table definition
- `app.py` - Added plants routes and API endpoints
- `templates/plants.html` - New plant management page
- `templates/base.html` - Added plants navigation link
- `templates/dispatch.html` - Added plant selection to dispatch modal
- `load_plants.py` - Script to populate plants data

## Next Steps
The system is now ready to dispatch loads with plant assignments. When creating loads via the batch dispatch feature, dispatchers can select which plant each load originates from, enabling better tracking of inventory and delivery sources.

## Update Notes (2026-01-28)
- Corrected South Carolina plant addresses based on official SRM data
- Removed incorrect Hilton Head location (not in actual SC operations)
- Updated all SC plant IDs to match official SRM numbering system
- Total plant count adjusted to 23 (19 GA, 4 SC)