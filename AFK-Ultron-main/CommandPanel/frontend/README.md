# 🌐 AFK-Ultron Frontend Dashboard

Modern web dashboard for real-time drone detection monitoring.

## 📁 Structure

```
frontend/
├── index.html          # Main dashboard page
├── css/
│   └── styles.css     # Dark theme with glassmorphism
└── js/
    ├── config.js      # Configuration (API URLs, map settings)
    ├── api.js         # REST API communication
    ├── websocket.js   # WebSocket real-time updates
    ├── map.js         # Leaflet map functionality
    └── app.js         # Main application logic
```

## ✨ Features

- **Live Map** - Interactive map with detection markers and 5km geofence
- **Real-time Updates** - WebSocket push notifications for instant alerts
- **Statistics Dashboard** - Total detections, active alerts, last detection time
- **Alerts Panel** - Scrolling list of recent detections with timestamps
- **Export Functions** - CSV and PDF export buttons
- **Auto-refresh** - Automatic data refresh every 5 seconds
- **Connection Status** - Visual indicator for server connection
- **Responsive Design** - Works on desktop, tablet, and mobile

## 🎨 Design

- **Theme**: Dark mode with glassmorphism effects
- **Colors**: Cyan (#00ccff) and green (#00ff88) accents
- **Animations**: Smooth transitions and micro-interactions
- **Typography**: Segoe UI for clean, modern look

## 🔧 Configuration

### Change Map Center

Edit `js/config.js`:
```javascript
const MAP_CONFIG = {
    defaultCenter: [YOUR_LAT, YOUR_LON],
    defaultZoom: 13,
    geofenceRadius: 5000
};
```

### Change API URL

Edit `js/config.js`:
```javascript
const API_BASE_URL = 'http://YOUR_SERVER:5000';
```

### Change Refresh Rate

Edit `js/config.js`:
```javascript
const ALERT_CONFIG = {
    autoRefreshInterval: 3000  // milliseconds
};
```

## 📡 API Integration

### REST API Calls

```javascript
// Get live detections
const response = await api.getLiveDetections();

// Get statistics
const stats = await api.getStatistics('today');

// Export to CSV
const result = await api.exportCSV('week');
```

### WebSocket Events

```javascript
// Listen for new detections
socket.on('new_detection', (data) => {
    console.log('New detection:', data);
    // Update UI
});
```

## 🗺️ Map Features

- **Markers**: Red dots for each detection
- **Geofence**: Blue circle showing 5km radius
- **Popups**: Click marker to see detection details
- **Auto-center**: Map centers on latest detection

## 📊 Statistics

The dashboard displays:
- **Total Detections**: All-time detection count
- **Active Alerts**: Detections in last 5 minutes
- **Last Detection**: Time of most recent detection

## 🚨 Alerts Panel

- Shows last 20 detections
- Auto-scrolls to latest
- Displays:
  - Timestamp
  - Alert message
  - GPS coordinates
  - Confidence level (in popup)

## 🎯 Export Functions

### CSV Export
```javascript
exportCSV()  // Exports all detections to CSV
```

### PDF Export
```javascript
exportPDF()  // Generates PDF report
```

## 🔌 Dependencies

### External Libraries (CDN)

- **Socket.IO** - WebSocket client
  ```html
  <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
  ```

- **Leaflet** - Interactive maps
  ```html
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  ```

### No Build Process Required

This is a vanilla JavaScript application - no npm, webpack, or build tools needed!

## 🚀 Usage

### Served by Backend (Recommended)

The backend server automatically serves these files:

```
http://localhost:5000/              → index.html
http://localhost:5000/frontend/css/ → styles.css
http://localhost:5000/frontend/js/  → JavaScript files
```

### Standalone (Development)

You can also run independently:

```powershell
# Python HTTP server
python -m http.server 8080

# Then open: http://localhost:8080
```

**Note:** Update `config.js` to point to backend:
```javascript
const API_BASE_URL = 'http://localhost:5000';
```

## 🎨 Customization

### Change Colors

Edit `css/styles.css`:

```css
/* Primary gradient */
background: linear-gradient(135deg, #YOUR_COLOR1, #YOUR_COLOR2);

/* Accent color */
color: #YOUR_ACCENT_COLOR;
```

### Add New Statistics

1. Add HTML in `index.html`:
```html
<div class="stat-card">
    <h3>New Stat</h3>
    <p class="stat-value" id="newStat">0</p>
</div>
```

2. Update in `js/app.js`:
```javascript
document.getElementById('newStat').textContent = value;
```

### Add New Map Features

Edit `js/map.js`:

```javascript
// Add custom layer
const customLayer = L.circle([lat, lon], {
    color: '#ff0000',
    radius: 1000
}).addTo(map);
```

## 🧪 Testing

### Check Console

Open browser console (F12) and look for:
```
✅ API module loaded
✅ WebSocket module loaded
✅ Map module loaded
✅ App module loaded
🗺️ Map initialized
✅ WebSocket connected
```

### Verify API Connection

```javascript
// In browser console
api.getLiveDetections().then(console.log);
```

### Test WebSocket

```javascript
// In browser console
socket.emit('request_update');
```

## 📱 Responsive Design

The dashboard is responsive and works on:
- **Desktop** (1920x1080+)
- **Laptop** (1366x768+)
- **Tablet** (768x1024)
- **Mobile** (375x667)

## 🔒 Security Notes

- No authentication implemented (add if needed)
- CORS enabled for all origins (restrict in production)
- WebSocket accepts all connections (add auth if needed)

## 🐛 Troubleshooting

### Map not loading
- Check internet connection (needs OpenStreetMap tiles)
- Check browser console for errors

### No real-time updates
- Verify WebSocket connection (green dot)
- Check server is running
- Check browser console for errors

### API errors
- Verify backend is running on correct port
- Check `config.js` has correct API_BASE_URL
- Check browser network tab (F12)

## 📚 Learn More

- **Leaflet Docs**: https://leafletjs.com/
- **Socket.IO Docs**: https://socket.io/docs/
- **Fetch API**: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API

## 🎉 You're Ready!

This frontend is fully functional and ready to use. Just start the backend server and open http://localhost:5000!

---

**Built with ❤️ for AFK-Ultron Command Panel**
