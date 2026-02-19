# 🚀 Phase 2: Backend Development - Complete Guide

## ✅ What Was Built

Phase 2 creates the **"brain"** of the Command Panel - a complete backend system that:

1. ✅ **Receives** detection data from `app.py` via JSON file
2. ✅ **Stores** data in SQLite database
3. ✅ **Filters** detections (5-second persistence)
4. ✅ **Calculates** statistics and analytics
5. ✅ **Serves** data via REST API
6. ✅ **Pushes** real-time updates via WebSocket
7. ✅ **Exports** reports (CSV/PDF)

---

## 📦 Components Created

### 1. **database.py** - Data Storage

**What it does:**
- Creates SQLite database with 3 tables
- Stores detections with GPS, confidence, timestamps
- Tracks safe zones
- Calculates alert levels (HIGH/MEDIUM/LOW)
- Generates statistics

**Key Features:**
```python
# Add detection
db.add_detection(data, duration=5.2)

# Get recent detections
detections = db.get_detections_last_hours(1)

# Get statistics
stats = db.get_statistics('today')
# Returns: total, high_alerts, avg_confidence, peak_hour, etc.

# Add safe zone
db.add_safe_zone("Main Entrance", 28.6139, 77.2090, radius=50)
```

**Database Tables:**

| Table | Purpose |
|-------|---------|
| `detections` | Stores all detection events |
| `safe_zones` | Defines safe areas |
| `detection_tracking` | Tracks duration of detections |

---

### 2. **analytics.py** - Reports & Exports

**What it does:**
- Exports data to CSV (Excel-compatible)
- Generates professional PDF reports
- Creates heatmap data for visualization
- Analyzes hourly distribution

**Key Features:**
```python
analytics = Analytics(db)

# Export to CSV
analytics.export_to_csv(period='today')
# Creates: data/detections_export.csv

# Generate PDF report
analytics.export_to_pdf(period='week')
# Creates: data/detection_report.pdf

# Get heatmap data
heatmap = analytics.generate_heatmap_data()
# Returns: [[lat, lon, intensity], ...]
```

**PDF Report Includes:**
- ✅ Detection statistics
- ✅ Alert breakdown (HIGH/MEDIUM/LOW)
- ✅ Peak hour analysis
- ✅ Recent detections table
- ✅ Professional formatting

---

### 3. **server.py** - Flask API Server

**What it does:**
- Provides REST API endpoints
- WebSocket for real-time updates
- Smart detection filtering (5-second persistence)
- File watcher for `live_feed.json`

**REST API Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/api/detections/live` | GET | Last hour detections |
| `/api/detections/all` | GET | All detections |
| `/api/statistics?period=today` | GET | Statistics |
| `/api/safe-zones` | GET/POST | Safe zones |
| `/api/export/csv?period=week` | GET | Export CSV |
| `/api/export/pdf?period=month` | GET | Export PDF |
| `/api/heatmap?period=all` | GET | Heatmap data |

**WebSocket Events:**

| Event | Direction | Description |
|-------|-----------|-------------|
| `connect` | Client → Server | Client connects |
| `new_detection` | Server → Client | New detection alert |
| `request_update` | Client → Server | Request data update |
| `detections_update` | Server → Client | Data update response |

---

## 🔄 Data Flow (Phase 1 + Phase 2 Integration)

```
┌─────────────────────────────────────────────────────────────┐
│                    ULTRON APP (app.py)                      │
│  1. Detects human                                           │
│  2. Calculates GPS                                          │
│  3. Encodes image to base64                                 │
│  4. Writes to live_feed.json                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    (JSON file updated)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              FLASK SERVER (server.py)                       │
│                                                             │
│  File Watcher Thread:                                       │
│  1. Detects JSON file change                                │
│  2. Reads detection data                                    │
│  3. Smart filtering (5-second persistence)                  │
│     ├─ Track location                                       │
│     ├─ Count occurrences                                    │
│     ├─ Calculate duration                                   │
│     └─ Only store if duration >= 5s                         │
│  4. Store in database                                       │
│  5. Emit WebSocket event to clients                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    (Data stored & broadcasted)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  DATABASE (database.py)                     │
│  • SQLite storage                                           │
│  • Calculate alert levels                                   │
│  • Check safe zones                                         │
│  • Generate statistics                                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    (Data available via API)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              WEB FRONTEND (Phase 3)                         │
│  • Live map display                                         │
│  • Real-time alerts                                         │
│  • Statistics dashboard                                     │
│  • Export reports                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Smart Filtering Explained

### The Problem
Without filtering, you get **spam**:
- Person walks past camera
- Camera captures 30 frames/second
- Each frame triggers a detection
- Result: 30 alerts in 1 second! 😱

### The Solution: 5-Second Persistence

```python
# Track each unique location
detection_key = f"{lat:.5f}_{lon:.5f}"

if detection_key in active_detections:
    # Update existing
    duration = current_time - first_seen
    
    if duration >= 5.0:  # Only alert if person stays 5+ seconds
        db.add_detection(data)
        socketio.emit('new_detection', data)
else:
    # New detection - start tracking
    active_detections[detection_key] = {
        'first_seen': current_time,
        'count': 1
    }
```

**Result:**
- ✅ Person walks past (2 seconds) → **No alert** (filtered out)
- ✅ Person stands still (5+ seconds) → **Alert triggered** (real threat)

---

## 🚀 Installation & Setup

### 1. Install Dependencies

```bash
cd CommandPanel
pip install -r requirements.txt
```

**Packages installed:**
- `flask` - Web framework
- `flask-socketio` - WebSocket support
- `flask-cors` - Cross-origin requests
- `reportlab` - PDF generation

### 2. Test Database Module

```bash
python database.py
```

**Expected output:**
```
======================================================================
🗄️  DATABASE MODULE TEST
======================================================================
✅ Database tables created/verified
✅ Safe zone 'Main Entrance' added (ID: 1)
✅ Detection #1 added: TEST DETECTION [HIGH] @ (28.61400, 77.20910)

📊 Statistics:
   Total Detections: 1
   High Alerts: 1
   Average Confidence: 92.00%
   Peak Hour: 23:00 (1 detections)

======================================================================
✅ Database test complete!
```

### 3. Test Analytics Module

```bash
python analytics.py
```

**Expected output:**
```
======================================================================
📊 ANALYTICS MODULE TEST
======================================================================
✅ CSV exported: data/detections_export.csv (3 records)
✅ PDF report generated: data/detection_report.pdf

🗺️  Heatmap data points: 3
⏰ Hourly distribution: 3 total detections

======================================================================
✅ Analytics test complete!
   CSV: data/detections_export.csv
   PDF: data/detection_report.pdf
```

### 4. Start Flask Server

```bash
python server.py
```

**Expected output:**
```
======================================================================
🚀 AFK-ULTRON COMMAND PANEL SERVER
======================================================================
📡 Starting server on http://localhost:5000
🔌 WebSocket enabled for real-time updates
👁️  Monitoring: data/live_feed.json
⏱️  Persistence threshold: 5.0s
======================================================================
✅ File watcher started
 * Running on http://0.0.0.0:5000
```

---

## 🧪 Testing the API

### Test REST Endpoints

```bash
# Get API info
curl http://localhost:5000/

# Get live detections
curl http://localhost:5000/api/detections/live

# Get statistics
curl http://localhost:5000/api/statistics?period=today

# Export CSV
curl http://localhost:5000/api/export/csv?period=week

# Export PDF
curl http://localhost:5000/api/export/pdf?period=month
```

### Test WebSocket (JavaScript)

```javascript
// Connect to WebSocket
const socket = io('http://localhost:5000');

// Listen for new detections
socket.on('new_detection', (data) => {
    console.log('New detection:', data);
    // Update map, show alert, etc.
});

// Request manual update
socket.emit('request_update');
```

---

## 📊 Database Schema

### Table: `detections`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Auto-increment ID |
| `timestamp` | DATETIME | Detection time |
| `latitude` | REAL | GPS latitude |
| `longitude` | REAL | GPS longitude |
| `confidence` | REAL | AI confidence (0-1) |
| `message` | TEXT | Alert message |
| `drone_id` | TEXT | Drone identifier |
| `alert_level` | TEXT | HIGH/MEDIUM/LOW |
| `duration` | REAL | Seconds visible |
| `in_safe_zone` | BOOLEAN | In safe zone? |
| `image_base64` | TEXT | Base64 image |
| `created_at` | DATETIME | Record creation time |

### Table: `safe_zones`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Zone ID |
| `name` | TEXT | Zone name |
| `center_lat` | REAL | Center latitude |
| `center_lon` | REAL | Center longitude |
| `radius` | REAL | Radius (meters) |
| `created_at` | DATETIME | Creation time |

---

## 🎨 Alert Levels

| Level | Confidence | Color | Priority |
|-------|-----------|-------|----------|
| **HIGH** | ≥ 85% | 🔴 Red | Critical |
| **MEDIUM** | 70-84% | 🟡 Yellow | Warning |
| **LOW** | < 70% | 🟢 Green | Info |

---

## 📈 Statistics Available

```python
stats = db.get_statistics('today')
```

**Returns:**
```json
{
    "total_detections": 42,
    "high_alerts": 15,
    "average_confidence": 0.8734,
    "peak_hour": "14:00",
    "peak_hour_count": 8,
    "alert_breakdown": {
        "HIGH": 15,
        "MEDIUM": 20,
        "LOW": 7
    },
    "period": "today"
}
```

---

## 🔧 Configuration

### Adjust Persistence Threshold

In `server.py`:
```python
PERSISTENCE_THRESHOLD = 5.0  # Change to 3.0 for 3 seconds
```

### Change Server Port

```python
socketio.run(app, host='0.0.0.0', port=8080)  # Use port 8080
```

### Database Location

In `database.py`:
```python
db = DetectionDatabase(db_path='custom/path/detections.db')
```

---

## ✅ Integration Checklist

- [x] **Phase 1**: JSON export from `app.py` ✅
- [x] **Phase 2**: Backend server ✅
  - [x] Database module
  - [x] Analytics module
  - [x] Flask server
  - [x] WebSocket support
  - [x] File watcher
  - [x] Smart filtering
- [ ] **Phase 3**: Web frontend (Next!)

---

## 🚀 Next Steps: Phase 3

Phase 3 will create the **web interface**:
- 🗺️ Live map with Leaflet.js
- 🚨 Real-time alert display
- 📊 Statistics dashboard
- 📥 Export buttons (CSV/PDF)
- 🎨 Beautiful UI with animations

---

## 📁 File Structure

```
CommandPanel/
├── data/
│   ├── live_feed.json          # From Phase 1 (app.py writes here)
│   ├── detections.db           # SQLite database
│   ├── detections_export.csv   # CSV exports
│   └── detection_report.pdf    # PDF reports
│
├── database.py                 # ✅ NEW - Database module
├── analytics.py                # ✅ NEW - Analytics & exports
├── server.py                   # ✅ NEW - Flask API server
├── requirements.txt            # ✅ NEW - Python dependencies
│
└── PHASE2_BACKEND_GUIDE.md     # This file
```

---

## 🏆 Summary

**Phase 2 Status:** ✅ **COMPLETE**

**What's Working:**
- ✅ SQLite database with 3 tables
- ✅ Smart detection filtering (5-second persistence)
- ✅ REST API with 8 endpoints
- ✅ WebSocket real-time updates
- ✅ CSV export
- ✅ Professional PDF reports
- ✅ Statistics calculation
- ✅ Safe zone checking
- ✅ Alert level classification
- ✅ File watcher integration with Phase 1

**Ready for:** Phase 3 - Web Frontend Development

---

**Date:** 2026-01-29  
**Version:** 1.0  
**Status:** Production Ready
