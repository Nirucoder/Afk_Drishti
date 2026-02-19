# 🛡️ AFK-Ultron Command Panel - Frontend

**Real-Time Drone Surveillance Command & Control Interface**

A production-ready, military-grade tactical dashboard for monitoring drone detection systems in real-time.

---

## ✨ Features

### 🗺️ **Live Tactical Map**
- Interactive Leaflet map with OpenStreetMap tiles
- 5km geofence visualization (red dashed circle)
- Color-coded detection markers (High=Red, Medium=Orange, Low=Green)
- Auto-removal of markers after 5 minutes
- Popup details with detection images, GPS, confidence, and timestamp
- Pulsing animation for high-priority alerts
- Center map and clear markers controls

### ⚠️ **Real-Time Alerts Feed**
- Scrollable feed showing last 20 detections
- Newest alerts appear at top with slide-in animation
- Each alert displays:
  - Detection image (with green boxes and red GPS text)
  - Confidence percentage with color-coded badge
  - Alert message
  - GPS coordinates
  - Timestamp
- Color-coded left border (High=Red, Medium=Orange, Low=Green)

### 📊 **Statistics Dashboard**
- **Total Detections** - All-time or period-based count
- **Peak Hour** - Hour with most detections
- **Average Confidence** - Mean detection confidence
- **High Alerts** - Count of high-priority detections (≥85%)
- Period selector: Today, This Week, This Month, All Time
- Auto-updates every 30 seconds
- Smooth number animations

### 🔔 **Alert System**
- Web Audio API-generated alert sounds (no audio files needed)
- High alerts: 1000 Hz tone
- Medium/Low alerts: 800 Hz tone
- Duration: 200ms
- Toast notifications for new detections

### 📤 **Export Functions**
- **CSV Export** - Export detections to CSV file
- **PDF Export** - Generate PDF report
- Period-based filtering
- Success/error toast notifications

### 🔌 **WebSocket Integration**
- Real-time connection to backend server
- Live detection updates without page refresh
- Connection status indicator (green=connected, red=disconnected)
- Auto-reconnection on disconnect

---

## 🎨 Design

### **Tactical Military Theme**
- Dark mode with deep blue-black background (#0a0e27)
- Glassmorphism effects (semi-transparent cards with backdrop blur)
- Gradient accents (green #00ff88, red #ff4444, orange #ffbb33)
- Smooth animations and transitions
- Modern typography (Inter font family)

### **UI Components**
- Responsive grid layout (map + sidebar)
- Hover effects on buttons and cards
- Pulsing connection status indicator
- Slide-in animations for alerts
- Loading overlay with spinner
- Toast notifications

---

## 📁 File Structure

```
frontend/
├── index.html              # Main HTML structure
├── css/
│   ├── style.css          # Complete styling (tactical theme)
│   └── js/
│       └── api.js         # API client (UltronAPI class)
├── js/
│   ├── app.js             # Main application logic
│   └── map.js             # Leaflet map module (TacticalMap class)
└── README.md              # This file
```

---

## 🚀 Quick Start

### **1. Prerequisites**

Ensure backend server is running:
```powershell
cd c:\Users\user\Desktop\AFK-Ultron-main\CommandPanel
python server.py
```

### **2. Open Dashboard**

**Option A: Served by Backend (Recommended)**
```
http://localhost:5000
```

**Option B: Direct File Access**
```
Open: c:\Users\user\Desktop\AFK-Ultron-main\frontend\index.html
```

**Option C: Local Server**
```powershell
cd c:\Users\user\Desktop\AFK-Ultron-main\frontend
python -m http.server 8080
# Then open: http://localhost:8080
```

### **3. Verify Connection**

- Check connection status indicator (should be green)
- Console should show: "✅ WebSocket connected"
- Map should load with geofence circle

---

## 🔧 Configuration

### **API Endpoints**

Edit `css/js/api.js`:
```javascript
const CONFIG = {
    API_BASE_URL: 'http://localhost:5000',
    SOCKET_URL: 'http://localhost:5000',
    UPDATE_INTERVAL: 30000 // 30 seconds
};
```

### **Map Center**

Edit `js/app.js` (line 96):
```javascript
this.map = new TacticalMap('map', [YOUR_LAT, YOUR_LON], 14);
```

### **Geofence Radius**

Edit `js/map.js` (line 28):
```javascript
radius: 5000, // Change to desired radius in meters
```

### **Alert Retention**

Edit `js/app.js` (line 10):
```javascript
this.maxAlerts = 20; // Change max number of alerts to display
```

### **Marker Auto-Removal**

Edit `js/map.js` (line 13):
```javascript
this.markerTimeout = 300000; // Change timeout in milliseconds
```

---

## 📡 API Integration

### **REST API Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/detections/live` | GET | Get detections from last hour |
| `/api/detections/all` | GET | Get all detections |
| `/api/statistics?period=today` | GET | Get statistics |
| `/api/export/csv?period=week` | GET | Export CSV |
| `/api/export/pdf?period=month` | GET | Export PDF |

### **WebSocket Events**

**Server → Client:**
- `connect` - Connection established
- `disconnect` - Connection lost
- `new_detection` - New detection alert
- `detections_update` - Batch update

### **Detection Data Format**

```javascript
{
  "timestamp": "2026-01-30 00:26:47",
  "latitude": 28.613909,
  "longitude": 77.208998,
  "confidence": 0.9394,
  "message": "TRACKING: 4 HUMANS",
  "drone_id": "ULTRON-01",
  "alert_level": "HIGH",
  "duration": 8.5,
  "image_base64": "/9j/4AAQSkZJ..." // JPEG with detection boxes
}
```

---

## 🎯 Usage Examples

### **Using the API Client**

```javascript
// Initialize API
const api = new UltronAPI();

// Get live detections
const detections = await api.getLiveDetections();

// Get statistics
const stats = await api.getStatistics('today');

// Export CSV
const csvPath = await api.exportCSV('week');

// Initialize WebSocket
const socket = api.initWebSocket();

// Listen for new detections
api.onNewDetection((data) => {
    console.log('New detection:', data);
});
```

### **Using the Map**

```javascript
// Initialize map
const map = new TacticalMap('map', [28.6139, 77.2090], 14);
map.init();

// Add marker
map.addMarker(detection);

// Clear all markers
map.clearAllMarkers();

// Center map
map.centerMap();
```

---

## 🔊 Alert Sounds

Alert sounds are generated using Web Audio API (no audio files required):

- **High Alerts**: 1000 Hz sine wave, 200ms duration
- **Medium/Low Alerts**: 800 Hz sine wave, 200ms duration

To disable sounds, comment out the `playAlertSound()` call in `js/app.js`.

---

## 📊 Statistics Auto-Update

Statistics automatically refresh every 30 seconds. To change:

```javascript
// In js/app.js, line 238
this.statsUpdateInterval = setInterval(() => {
    this.updateStatistics();
}, 30000); // Change to desired interval in milliseconds
```

---

## 🎨 Customization

### **Change Color Scheme**

Edit `css/style.css`:
```css
:root {
    --accent-green: #00ff88;  /* Change to your color */
    --accent-red: #ff4444;    /* Change to your color */
    --accent-orange: #ffbb33; /* Change to your color */
}
```

### **Modify Alert Thresholds**

Edit `js/app.js` (line 183):
```javascript
getAlertLevel(confidence) {
    if (confidence >= 0.85) return 'HIGH';    // Change threshold
    if (confidence >= 0.70) return 'MEDIUM';  // Change threshold
    return 'LOW';
}
```

### **Add Custom Statistics**

1. Add HTML card in `index.html`
2. Add API endpoint in backend
3. Fetch data in `updateStatistics()` method
4. Display using `animateValue()` for smooth transitions

---

## 🐛 Troubleshooting

### **Map Not Loading**
- Check internet connection (needs OpenStreetMap tiles)
- Check browser console for errors
- Verify Leaflet library is loaded

### **No WebSocket Connection**
- Verify backend server is running
- Check `CONFIG.SOCKET_URL` in `api.js`
- Check browser console for connection errors
- Ensure port 5000 is not blocked by firewall

### **No Alerts Appearing**
- Check WebSocket connection status
- Verify backend is sending `new_detection` events
- Check browser console for JavaScript errors
- Ensure `alertsFeed` element exists

### **Images Not Displaying**
- Verify `image_base64` field is present in detection data
- Check image data is valid base64-encoded JPEG
- Inspect network tab for failed requests

### **Statistics Not Updating**
- Check API endpoint `/api/statistics` is accessible
- Verify period selector value
- Check browser console for fetch errors

---

## 📱 Responsive Design

The dashboard is fully responsive:

- **Desktop** (1200px+): Full grid layout
- **Tablet** (768px-1199px): Stacked layout
- **Mobile** (<768px): Single column, optimized controls

---

## 🔒 Security Notes

- No authentication implemented (add if deploying publicly)
- CORS enabled for all origins (restrict in production)
- WebSocket accepts all connections (add auth if needed)
- API keys should be environment variables in production

---

## 🚀 Performance

- Markers auto-remove after 5 minutes to prevent memory leaks
- Maximum 20 alerts retained in feed
- Efficient DOM updates using `insertBefore()`
- Smooth animations using CSS transitions
- Debounced statistics updates (30s interval)

---

## 📚 Dependencies

### **External Libraries (CDN)**

- **Leaflet.js** 1.9.4 - Interactive maps
- **Socket.IO** 4.5.4 - WebSocket client
- **Google Fonts** - Inter font family

### **No Build Tools Required**

This is a vanilla JavaScript application - no npm, webpack, or build process needed!

---

## 🎉 Features Checklist

- ✅ Live Leaflet map with geofence
- ✅ Color-coded detection markers (High/Medium/Low)
- ✅ Auto-removal of markers after 5 minutes
- ✅ Real-time alerts feed with images
- ✅ Slide-in animations for new alerts
- ✅ Statistics dashboard with 4 key metrics
- ✅ Auto-update every 30 seconds
- ✅ WebSocket real-time integration
- ✅ Alert sounds using Web Audio API
- ✅ CSV and PDF export buttons
- ✅ Connection status indicator
- ✅ Toast notifications
- ✅ Loading overlay
- ✅ Responsive design
- ✅ Tactical military dark theme
- ✅ Glassmorphism effects

---

## 📞 Support

For issues or questions:
1. Check browser console (F12) for errors
2. Verify backend server is running
3. Check network tab for failed API calls
4. Review this README for configuration options

---

**Built with ❤️ for AFK-Ultron Drone Surveillance System**

**Status**: Production Ready ✅
