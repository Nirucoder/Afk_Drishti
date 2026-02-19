# 🔗 Backend-Frontend Integration Guide
## AFK-Ultron Command Panel

This guide explains how to properly structure and connect your backend (already in `CommandPanel/`) with your frontend (from GitHub).

---

## 📁 Recommended File Structure

```
AFK-Ultron-main/
│
├── Ultron/                          # Drone detection system (Phase 1)
│   ├── app.py                       # Main detection app
│   └── background.jpg
│
├── CommandPanel/                    # Backend (Phase 2) - ALREADY COMPLETE
│   ├── server.py                    # Flask API server
│   ├── database.py                  # SQLite database handler
│   ├── analytics.py                 # Statistics & exports
│   ├── requirements.txt             # Python dependencies
│   ├── data/                        # Data storage
│   │   ├── live_feed.json          # Real-time detection feed
│   │   ├── detections.db           # SQLite database
│   │   └── detections_export.csv   # CSV exports
│   └── frontend/                    # Frontend files (TO BE ADDED)
│       ├── index.html              # Main dashboard
│       ├── css/
│       │   └── styles.css          # Styling
│       ├── js/
│       │   ├── app.js              # Main app logic
│       │   ├── map.js              # Map functionality
│       │   ├── api.js              # API communication
│       │   └── websocket.js        # Real-time updates
│       └── assets/
│           └── images/             # Icons, logos, etc.
│
└── INTEGRATION_GUIDE.md            # This file
```

---

## 🚀 Step-by-Step Integration Process

### **Step 1: Clone Your Frontend from GitHub**

```powershell
# Navigate to CommandPanel directory
cd c:\Users\user\Desktop\AFK-Ultron-main\CommandPanel

# Clone your frontend repository into a 'frontend' folder
# Replace YOUR_GITHUB_USERNAME and YOUR_REPO_NAME with actual values
git clone https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git frontend

# OR if you already downloaded it, just move it here:
# Move-Item -Path "path\to\your\frontend\files" -Destination ".\frontend"
```

### **Step 2: Update Backend to Serve Frontend**

Your `server.py` needs to serve the frontend files. Add this to your Flask server:

```python
# In server.py, add this route to serve the frontend

@app.route('/dashboard')
def dashboard():
    """Serve the main dashboard HTML"""
    return send_from_directory('frontend', 'index.html')

@app.route('/frontend/<path:filename>')
def serve_frontend(filename):
    """Serve static frontend files (CSS, JS, images)"""
    return send_from_directory('frontend', filename)

# Alternative: Serve frontend as default
@app.route('/')
def index():
    """Serve dashboard as homepage"""
    return send_from_directory('frontend', 'index.html')
```

### **Step 3: Configure Frontend API Endpoint**

In your frontend JavaScript files, set the backend API URL:

**Option A: Same Server (Recommended for Production)**
```javascript
// In frontend/js/api.js or config.js
const API_BASE_URL = window.location.origin; // Uses same domain
const WS_URL = `ws://${window.location.host}`; // WebSocket URL
```

**Option B: Separate Servers (For Development)**
```javascript
// In frontend/js/api.js or config.js
const API_BASE_URL = 'http://localhost:5000';
const WS_URL = 'ws://localhost:5000';
```

### **Step 4: Update CORS Settings (If Needed)**

If frontend and backend are on different ports during development:

```python
# In server.py (already present, but verify)
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {"origins": "*"},  # Allow all origins for API
    r"/socket.io/*": {"origins": "*"}  # Allow WebSocket connections
})
```

### **Step 5: Install Dependencies**

```powershell
# Backend dependencies
cd c:\Users\user\Desktop\AFK-Ultron-main\CommandPanel
pip install -r requirements.txt

# If requirements.txt is missing any, install manually:
pip install flask flask-socketio flask-cors reportlab matplotlib
```

---

## 🔌 API Endpoints Your Frontend Should Use

### **REST API Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/detections/live` | GET | Get detections from last hour |
| `/api/detections/all` | GET | Get all detections |
| `/api/statistics?period=today` | GET | Get statistics (today/week/month/all) |
| `/api/safe-zones` | GET | Get all safe zones |
| `/api/safe-zones` | POST | Add new safe zone |
| `/api/export/csv?period=all` | GET | Export to CSV |
| `/api/export/pdf?period=all` | GET | Export to PDF |
| `/api/heatmap?period=week` | GET | Get heatmap data |

### **WebSocket Events**

**Client → Server:**
- `connect` - Establish connection
- `request_update` - Request manual update

**Server → Client:**
- `connection_response` - Connection confirmation
- `new_detection` - New detection alert (real-time)
- `detections_update` - Batch detection update

---

## 📝 Frontend JavaScript Example

### **Example: Fetching Live Detections**

```javascript
// frontend/js/api.js
const API_BASE_URL = 'http://localhost:5000';

async function fetchLiveDetections() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/detections/live`);
        const data = await response.json();
        
        if (data.success) {
            console.log(`Received ${data.count} detections`);
            updateMap(data.detections);
        }
    } catch (error) {
        console.error('Error fetching detections:', error);
    }
}

// Call every 5 seconds
setInterval(fetchLiveDetections, 5000);
```

### **Example: WebSocket Connection**

```javascript
// frontend/js/websocket.js
const socket = io('http://localhost:5000');

socket.on('connect', () => {
    console.log('✅ Connected to Command Panel');
});

socket.on('new_detection', (data) => {
    console.log('🚨 New detection:', data);
    addDetectionToMap(data.detection);
    showAlert(data.detection.message);
});

socket.on('disconnect', () => {
    console.log('❌ Disconnected from server');
});
```

---

## 🧪 Testing the Integration

### **1. Start the Backend Server**

```powershell
cd c:\Users\user\Desktop\AFK-Ultron-main\CommandPanel
python server.py
```

You should see:
```
🚀 AFK-ULTRON COMMAND PANEL SERVER
📡 Starting server on http://localhost:5000
🔌 WebSocket enabled for real-time updates
```

### **2. Start the Drone Detection System**

```powershell
cd c:\Users\user\Desktop\AFK-Ultron-main\Ultron
python app.py
```

### **3. Access the Dashboard**

Open your browser and navigate to:
- **http://localhost:5000** (if serving frontend from backend)
- **Or open `frontend/index.html` directly** (if using file protocol)

### **4. Verify Data Flow**

1. ✅ Drone detects a person
2. ✅ `app.py` writes to `CommandPanel/data/live_feed.json`
3. ✅ `server.py` file watcher detects change
4. ✅ Detection stored in database after 5-second persistence
5. ✅ WebSocket emits `new_detection` event
6. ✅ Frontend receives update and displays on map

---

## 🛠️ Alternative Setup: Separate Frontend Server

If you prefer to run frontend separately (e.g., using a development server):

### **Using Python HTTP Server**

```powershell
cd c:\Users\user\Desktop\AFK-Ultron-main\CommandPanel\frontend
python -m http.server 8080
```

Then access: **http://localhost:8080**

### **Using Node.js (if you have npm)**

```powershell
cd c:\Users\user\Desktop\AFK-Ultron-main\CommandPanel\frontend
npx http-server -p 8080
```

---

## 🔧 Troubleshooting

### **Issue: CORS Errors**

**Solution:** Ensure CORS is enabled in `server.py`:
```python
CORS(app, resources={r"/*": {"origins": "*"}})
```

### **Issue: WebSocket Connection Failed**

**Solution:** Check that `flask-socketio` is installed:
```powershell
pip install flask-socketio python-socketio
```

### **Issue: Frontend Can't Fetch Data**

**Solution:** Verify backend is running and check browser console for errors:
```javascript
console.log('API URL:', API_BASE_URL);
```

### **Issue: No Real-Time Updates**

**Solution:** Check that file watcher is running (look for "👁️ Watching file" in server logs)

---

## 📦 Complete Requirements

### **Backend (Python)**
```txt
flask==2.3.0
flask-socketio==5.3.0
flask-cors==4.0.0
python-socketio==5.9.0
reportlab==4.0.0
matplotlib==3.7.0
```

### **Frontend (JavaScript)**
```html
<!-- Include in your HTML -->
<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
```

---

## 🎯 Next Steps

1. ✅ Clone/move your frontend into `CommandPanel/frontend/`
2. ✅ Update `server.py` to serve frontend files
3. ✅ Configure API endpoints in frontend JavaScript
4. ✅ Test the complete data flow
5. ✅ Deploy (optional): Use Gunicorn + Nginx for production

---

## 📞 Need Help?

If you encounter issues:
1. Check server logs for errors
2. Check browser console (F12) for JavaScript errors
3. Verify file paths are correct
4. Ensure all dependencies are installed

**Your backend is already complete and working! Just need to add the frontend files and connect them.** 🚀
