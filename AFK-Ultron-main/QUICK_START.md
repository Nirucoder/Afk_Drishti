# 🚀 Quick Start Guide - Backend-Frontend Integration

## ✅ What's Been Set Up

Your AFK-Ultron project now has a complete file structure with:

1. **Backend** (CommandPanel/) - Flask server with REST API and WebSocket
2. **Frontend** (CommandPanel/frontend/) - Modern web dashboard
3. **Integration** - Server configured to serve frontend files

## 📁 Current File Structure

```
AFK-Ultron-main/
├── Ultron/
│   └── app.py                    # Drone detection system
│
├── CommandPanel/
│   ├── server.py                 # ✅ Updated to serve frontend
│   ├── database.py               # Database handler
│   ├── analytics.py              # Statistics & exports
│   ├── requirements.txt          # Dependencies
│   ├── data/
│   │   └── live_feed.json       # Real-time feed
│   └── frontend/                 # ✅ NEW - Web dashboard
│       ├── index.html           # Main page
│       ├── css/
│       │   └── styles.css       # Styling
│       └── js/
│           ├── config.js        # Configuration
│           ├── api.js           # API calls
│           ├── websocket.js     # Real-time updates
│           ├── map.js           # Map functionality
│           └── app.js           # Main logic
│
└── INTEGRATION_GUIDE.md          # Full integration docs
```

## 🎯 How to Run

### Step 1: Install Dependencies

```powershell
cd c:\Users\user\Desktop\AFK-Ultron-main\CommandPanel
pip install flask flask-socketio flask-cors python-socketio reportlab matplotlib
```

### Step 2: Start Backend Server

```powershell
python server.py
```

You should see:
```
🚀 AFK-ULTRON COMMAND PANEL SERVER
📡 Starting server on http://localhost:5000
```

### Step 3: Start Drone Detection

Open a **new terminal**:

```powershell
cd c:\Users\user\Desktop\AFK-Ultron-main\Ultron
python app.py
```

### Step 4: Open Dashboard

Open your browser and go to:
**http://localhost:5000**

## 🔄 Data Flow

```
┌─────────────┐         ┌──────────────┐         ┌──────────────┐
│   Ultron    │  JSON   │  CommandPanel│ WebSocket│   Frontend   │
│   app.py    ├────────>│  server.py   ├─────────>│  Dashboard   │
│  (Camera)   │  File   │  (Backend)   │ Real-time│  (Browser)   │
└─────────────┘         └──────────────┘         └──────────────┘
```

1. Camera detects person → `app.py`
2. Detection saved to → `data/live_feed.json`
3. Server watches file → `server.py`
4. After 5 seconds → Stored in database
5. WebSocket emits → Real-time update
6. Frontend receives → Updates map & alerts

## 🧪 Testing

### Test 1: Backend API

```powershell
# In browser or curl
http://localhost:5000/api
```

Should return API information.

### Test 2: Frontend Loading

```powershell
http://localhost:5000
```

Should show the dashboard with map and statistics.

### Test 3: Real-Time Detection

1. Run `app.py` (drone system)
2. Point camera at a person
3. Watch dashboard update in real-time!

## 📊 Dashboard Features

✅ **Live Map** - Shows detection locations with markers
✅ **Statistics** - Total detections, active alerts, last detection time
✅ **Alerts Panel** - Real-time scrolling alerts
✅ **Export** - CSV and PDF export buttons
✅ **Auto-Refresh** - Updates every 5 seconds
✅ **WebSocket** - Real-time push notifications

## 🔧 Customization

### Change Map Center

Edit `frontend/js/config.js`:
```javascript
const MAP_CONFIG = {
    defaultCenter: [YOUR_LAT, YOUR_LON],  // Your location
    defaultZoom: 13,
    geofenceRadius: 5000
};
```

### Change API URL (for different servers)

Edit `frontend/js/config.js`:
```javascript
const API_BASE_URL = 'http://YOUR_SERVER_IP:5000';
```

### Change Refresh Rate

Edit `frontend/js/config.js`:
```javascript
const ALERT_CONFIG = {
    autoRefreshInterval: 3000  // 3 seconds instead of 5
};
```

## 🌐 Access from Other Devices

### On Same Network

1. Find your PC's IP address:
```powershell
ipconfig
```

2. Look for "IPv4 Address" (e.g., 192.168.1.100)

3. On other device, open:
```
http://192.168.1.100:5000
```

### Allow Firewall Access

```powershell
# Run as Administrator
netsh advfirewall firewall add rule name="Flask Server" dir=in action=allow protocol=TCP localport=5000
```

## 🎨 If You Have Your Own Frontend

If you already have frontend files on GitHub:

1. **Clone your repo:**
```powershell
cd c:\Users\user\Desktop\AFK-Ultron-main\CommandPanel
git clone YOUR_GITHUB_URL frontend
```

2. **Update API endpoints** in your JavaScript files to use:
```javascript
const API_BASE_URL = window.location.origin;
```

3. **Include Socket.IO** in your HTML:
```html
<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
```

4. **Connect to WebSocket:**
```javascript
const socket = io(window.location.origin);
socket.on('new_detection', (data) => {
    // Handle real-time detection
});
```

## ❓ Troubleshooting

### Dashboard shows "Frontend not found"

- Check that `frontend/` folder exists in `CommandPanel/`
- Verify `index.html` is in `CommandPanel/frontend/`

### No real-time updates

- Check browser console (F12) for WebSocket errors
- Verify `flask-socketio` is installed
- Restart server

### Map not loading

- Check internet connection (needs OpenStreetMap tiles)
- Check browser console for JavaScript errors

### CORS errors

- Verify `flask-cors` is installed
- Check that CORS is enabled in `server.py`

## 📚 Next Steps

1. ✅ Customize the dashboard design
2. ✅ Add more statistics panels
3. ✅ Implement heatmap visualization
4. ✅ Add user authentication
5. ✅ Deploy to production server

## 🎉 You're All Set!

Your backend and frontend are now fully integrated and ready to use!

**Need help?** Check `INTEGRATION_GUIDE.md` for detailed documentation.
