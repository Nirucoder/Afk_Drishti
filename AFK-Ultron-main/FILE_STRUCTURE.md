# 📁 Complete File Structure Reference

## Directory Tree

```
c:\Users\user\Desktop\AFK-Ultron-main\
│
├── 📄 INTEGRATION_GUIDE.md          # Detailed integration documentation
├── 📄 QUICK_START.md                # Quick start guide (read this first!)
├── 📄 FILE_STRUCTURE.md             # This file
│
├── 📁 Ultron/                        # PHASE 1: Drone Detection System
│   ├── app.py                       # Main detection application
│   ├── background.jpg               # UI background image
│   └── yolov8n.pt                   # YOLO model (auto-downloaded)
│
├── 📁 CommandPanel/                  # PHASE 2 & 3: Backend + Frontend
│   │
│   ├── 📄 server.py                 # ✅ Flask backend server (UPDATED)
│   ├── 📄 database.py               # SQLite database operations
│   ├── 📄 analytics.py              # Statistics and export functions
│   ├── 📄 requirements.txt          # Python dependencies
│   │
│   ├── 📁 data/                     # Data storage directory
│   │   ├── live_feed.json          # Real-time detection feed (updated by Ultron)
│   │   ├── detections.db           # SQLite database (auto-created)
│   │   └── detections_export.csv   # CSV exports
│   │
│   └── 📁 frontend/                 # ✅ NEW: Web Dashboard (PHASE 3)
│       │
│       ├── 📄 index.html           # Main dashboard page
│       │
│       ├── 📁 css/
│       │   └── styles.css          # Dashboard styling
│       │
│       ├── 📁 js/
│       │   ├── config.js           # Configuration (API URLs, map settings)
│       │   ├── api.js              # REST API communication
│       │   ├── websocket.js        # WebSocket real-time updates
│       │   ├── map.js              # Leaflet map functionality
│       │   └── app.js              # Main application logic
│       │
│       └── 📁 assets/              # (Optional) Images, icons, etc.
│
└── 📁 .git/                         # Git repository data

```

## File Descriptions

### Root Level

| File | Purpose |
|------|---------|
| `INTEGRATION_GUIDE.md` | Complete guide on connecting backend and frontend |
| `QUICK_START.md` | Step-by-step instructions to run the system |
| `FILE_STRUCTURE.md` | This file - directory structure reference |

### Ultron/ (Drone Detection System)

| File | Purpose | Modified? |
|------|---------|-----------|
| `app.py` | Main detection app with camera, YOLO, GPS | ✅ Yes - Exports JSON |
| `background.jpg` | UI background image | No |

**What it does:**
- Captures video from camera
- Detects humans using YOLO
- Calculates GPS coordinates
- Exports detections to `../CommandPanel/data/live_feed.json`

### CommandPanel/ (Backend Server)

| File | Purpose | Modified? |
|------|---------|-----------|
| `server.py` | Flask REST API + WebSocket server | ✅ Yes - Serves frontend |
| `database.py` | SQLite database operations | No |
| `analytics.py` | Statistics, CSV/PDF export | No |
| `requirements.txt` | Python package dependencies | No |

**What it does:**
- Watches `data/live_feed.json` for changes
- Stores detections in database after 5-second persistence
- Provides REST API endpoints
- Sends real-time WebSocket updates
- **NEW:** Serves frontend dashboard

### CommandPanel/data/ (Data Storage)

| File | Purpose | Auto-created? |
|------|---------|---------------|
| `live_feed.json` | Real-time detection feed | Yes (by Ultron) |
| `detections.db` | SQLite database | Yes (by server) |
| `detections_export.csv` | CSV exports | Yes (on export) |

### CommandPanel/frontend/ (Web Dashboard) ✅ NEW

| File | Purpose |
|------|---------|
| `index.html` | Main dashboard HTML structure |
| `css/styles.css` | Modern dark theme with glassmorphism |
| `js/config.js` | Configuration (API URLs, map center, etc.) |
| `js/api.js` | REST API communication module |
| `js/websocket.js` | WebSocket connection for real-time updates |
| `js/map.js` | Leaflet map with markers and geofence |
| `js/app.js` | Main application logic and UI updates |

**What it does:**
- Displays live map with detection markers
- Shows statistics (total, active, last detection)
- Real-time alerts panel
- Export to CSV/PDF buttons
- Auto-refreshes every 5 seconds
- Receives WebSocket push notifications

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         DATA FLOW                               │
└─────────────────────────────────────────────────────────────────┘

1. DETECTION (Ultron/app.py)
   ↓
   Camera captures frame
   ↓
   YOLO detects person
   ↓
   Calculate GPS coordinates
   ↓
   Write to: CommandPanel/data/live_feed.json
   {
     "timestamp": "2026-01-30 02:00:00",
     "latitude": 28.6139,
     "longitude": 77.2090,
     "confidence": 0.85,
     "message": "HUMAN DETECTED",
     "drone_id": "ULTRON-01",
     "image_base64": "..."
   }

2. BACKEND PROCESSING (CommandPanel/server.py)
   ↓
   File watcher detects change
   ↓
   Read live_feed.json
   ↓
   Smart filtering (5-second persistence)
   ↓
   Store in database (detections.db)
   ↓
   Emit WebSocket event: 'new_detection'

3. FRONTEND UPDATE (CommandPanel/frontend/)
   ↓
   WebSocket receives 'new_detection'
   ↓
   Update statistics panel
   ↓
   Add marker to map
   ↓
   Add alert to alerts panel
   ↓
   User sees real-time update!
```

## API Endpoints

### REST API (HTTP)

```
GET  /                           → Serve dashboard (index.html)
GET  /api                        → API information
GET  /frontend/<path>            → Serve static files (CSS, JS)

GET  /api/detections/live        → Get detections (last hour)
GET  /api/detections/all         → Get all detections
GET  /api/statistics?period=all  → Get statistics
GET  /api/export/csv?period=all  → Export to CSV
GET  /api/export/pdf?period=all  → Export to PDF
```

### WebSocket Events

```
Client → Server:
  - connect              → Establish connection
  - request_update       → Request manual update

Server → Client:
  - connection_response  → Connection confirmed
  - new_detection        → New detection alert (real-time)
  - detections_update    → Batch update
```

## Port Usage

| Service | Port | URL |
|---------|------|-----|
| Backend Server | 5000 | http://localhost:5000 |
| Frontend Dashboard | 5000 | http://localhost:5000 (served by backend) |
| WebSocket | 5000 | ws://localhost:5000 |

## Dependencies

### Python (Backend)

```
flask==2.3.0
flask-socketio==5.3.0
flask-cors==4.0.0
python-socketio==5.9.0
reportlab==4.0.0
matplotlib==3.7.0
```

### JavaScript (Frontend)

```
Socket.IO Client (CDN)
Leaflet Maps (CDN)
Vanilla JavaScript (no frameworks)
```

## Configuration Files

### Backend Config (in server.py)

```python
JSON_FILE_PATH = 'data/live_feed.json'
PERSISTENCE_THRESHOLD = 5.0  # seconds
```

### Frontend Config (js/config.js)

```javascript
API_BASE_URL = window.location.origin
MAP_CONFIG = {
    defaultCenter: [28.6139, 77.2090],
    defaultZoom: 13,
    geofenceRadius: 5000
}
```

## How to Modify

### Change Map Location

Edit `CommandPanel/frontend/js/config.js`:
```javascript
defaultCenter: [YOUR_LAT, YOUR_LON]
```

### Change Persistence Time

Edit `CommandPanel/server.py`:
```python
PERSISTENCE_THRESHOLD = 10.0  # 10 seconds instead of 5
```

### Change Refresh Rate

Edit `CommandPanel/frontend/js/config.js`:
```javascript
autoRefreshInterval: 3000  # 3 seconds instead of 5
```

### Add Custom Styling

Edit `CommandPanel/frontend/css/styles.css`

### Add New API Endpoint

1. Add route in `server.py`
2. Add method in `frontend/js/api.js`
3. Call from `frontend/js/app.js`

## Backup Important Files

Before making changes, backup:
- `Ultron/app.py`
- `CommandPanel/server.py`
- `CommandPanel/database.py`
- `CommandPanel/data/detections.db`

## Next Steps

1. ✅ Read `QUICK_START.md` to run the system
2. ✅ Customize map center in `config.js`
3. ✅ Test with real camera detections
4. ✅ Export data to CSV/PDF
5. ✅ Deploy to production server (optional)

---

**Your system is now fully integrated and ready to use!** 🚀
