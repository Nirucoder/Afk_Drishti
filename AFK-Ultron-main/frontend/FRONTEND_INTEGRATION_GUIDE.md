# 🌐 Frontend Integration Guide

## 📊 What Data Gets Exported to Frontend

Your backend provides **rich, real-time detection data** through multiple channels. Here's everything available:

---

## 🎯 Available Data

### 1. **Detection Data (JSON)**

Every detection includes:

```json
{
  "timestamp": "2026-01-30 00:26:47",
  "latitude": 28.613909,
  "longitude": 77.208998,
  "confidence": 0.9394,
  "message": "TRACKING: 4 HUMANS",
  "drone_id": "ULTRON-01",
  "image_base64": "/9j/4AAQSkZJRgABAQAA..."
}
```

#### Field Details:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `timestamp` | String | Detection time (YYYY-MM-DD HH:MM:SS) | `"2026-01-30 00:26:47"` |
| `latitude` | Float | GPS latitude (decimal degrees) | `28.613909` |
| `longitude` | Float | GPS longitude (decimal degrees) | `77.208998` |
| `confidence` | Float | AI confidence (0.0 to 1.0) | `0.9394` (93.94%) |
| `message` | String | Detection status | `"TRACKING: 4 HUMANS"` |
| `drone_id` | String | Drone identifier | `"ULTRON-01"` |
| `image_base64` | String | Base64-encoded JPEG image | `"/9j/4AAQSkZJ..."` |

---

### 2. **Image Data (Base64)**

**What's in the image:**
- ✅ **Detection boxes** - Green corner brackets around each person
- ✅ **GPS overlays** - Red text showing "THREAT LOC: lat, lon"
- ✅ **Annotated frame** - Exactly what the operator sees
- ✅ **JPEG format** - Compressed, ~6-12 KB per image
- ✅ **320x180 resolution** - Optimized for web display

**How to use in frontend:**
```html
<!-- Direct display -->
<img src="data:image/jpeg;base64,/9j/4AAQSkZJ..." alt="Detection">

<!-- Or in JavaScript -->
const img = document.createElement('img');
img.src = `data:image/jpeg;base64,${data.image_base64}`;
```

---

### 3. **Database Records**

Additional fields stored in database:

```json
{
  "id": 42,
  "timestamp": "2026-01-30 00:26:47",
  "latitude": 28.613909,
  "longitude": 77.208998,
  "confidence": 0.9394,
  "message": "TRACKING: 4 HUMANS",
  "drone_id": "ULTRON-01",
  "alert_level": "HIGH",
  "duration": 8.5,
  "in_safe_zone": false,
  "image_base64": "...",
  "created_at": "2026-01-30 00:26:55"
}
```

#### Additional Database Fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Unique detection ID |
| `alert_level` | String | HIGH/MEDIUM/LOW (based on confidence) |
| `duration` | Float | How long person was visible (seconds) |
| `in_safe_zone` | Boolean | True if in designated safe zone |
| `created_at` | DateTime | When record was created |

---

## 🔌 Connection Methods

### Method 1: **REST API** (HTTP Requests)

**Base URL:** `http://localhost:5000`

#### Available Endpoints:

```javascript
// 1. Get live detections (last hour)
fetch('http://localhost:5000/api/detections/live')
  .then(res => res.json())
  .then(data => {
    console.log(data.detections); // Array of detections
  });

// 2. Get all detections
fetch('http://localhost:5000/api/detections/all')
  .then(res => res.json())
  .then(data => {
    console.log(data.detections);
  });

// 3. Get statistics
fetch('http://localhost:5000/api/statistics?period=today')
  .then(res => res.json())
  .then(data => {
    console.log(data.statistics);
    // {
    //   total_detections: 42,
    //   high_alerts: 15,
    //   average_confidence: 0.8734,
    //   peak_hour: "14:00",
    //   peak_hour_count: 8,
    //   alert_breakdown: { HIGH: 15, MEDIUM: 20, LOW: 7 }
    // }
  });

// 4. Get safe zones
fetch('http://localhost:5000/api/safe-zones')
  .then(res => res.json())
  .then(data => {
    console.log(data.zones);
  });

// 5. Get heatmap data
fetch('http://localhost:5000/api/heatmap?period=week')
  .then(res => res.json())
  .then(data => {
    console.log(data.data); // [[lat, lon, intensity], ...]
  });

// 6. Export CSV
fetch('http://localhost:5000/api/export/csv?period=today')
  .then(res => res.json())
  .then(data => {
    console.log(data.filepath); // Path to CSV file
  });

// 7. Export PDF
fetch('http://localhost:5000/api/export/pdf?period=week')
  .then(res => res.json())
  .then(data => {
    console.log(data.filepath); // Path to PDF file
  });
```

---

### Method 2: **WebSocket** (Real-Time Updates)

**For live, instant updates as detections happen:**

```javascript
// Connect to WebSocket
const socket = io('http://localhost:5000');

// Listen for connection
socket.on('connect', () => {
  console.log('✅ Connected to AFK-Ultron Command Panel');
});

// Listen for new detections (REAL-TIME)
socket.on('new_detection', (data) => {
  console.log('🚨 New detection:', data);
  
  // data contains:
  // {
  //   detection: { timestamp, latitude, longitude, ... },
  //   duration: 5.2,
  //   detection_id: 42
  // }
  
  // Update map
  addMarkerToMap(data.detection.latitude, data.detection.longitude);
  
  // Display image
  showDetectionImage(data.detection.image_base64);
  
  // Show alert
  showAlert(data.detection.message);
});

// Request manual update
socket.emit('request_update');

// Listen for update response
socket.on('detections_update', (data) => {
  console.log('Detections:', data.detections);
});

// Handle disconnection
socket.on('disconnect', () => {
  console.log('❌ Disconnected from server');
});
```

---

## 🚀 Complete Frontend Integration Example

### **index.html**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AFK-Ultron Command Panel</title>
    <link rel="stylesheet" href="css/style.css">
    
    <!-- Leaflet for maps -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    
    <!-- Socket.IO for real-time updates -->
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
</head>
<body>
    <div class="container">
        <!-- Live Map -->
        <div id="map"></div>
        
        <!-- Detection Feed -->
        <div id="detection-feed"></div>
        
        <!-- Statistics Dashboard -->
        <div id="stats-dashboard"></div>
    </div>
    
    <script src="js/api.js"></script>
    <script src="js/map.js"></script>
    <script src="js/ui.js"></script>
</body>
</html>
```

---

### **js/api.js**

```javascript
// API Configuration
const API_BASE_URL = 'http://localhost:5000';
const SOCKET_URL = 'http://localhost:5000';

// Initialize Socket.IO
const socket = io(SOCKET_URL);

// API Functions
const API = {
    // Get live detections
    async getLiveDetections() {
        const response = await fetch(`${API_BASE_URL}/api/detections/live`);
        const data = await response.json();
        return data.detections;
    },
    
    // Get statistics
    async getStatistics(period = 'today') {
        const response = await fetch(`${API_BASE_URL}/api/statistics?period=${period}`);
        const data = await response.json();
        return data.statistics;
    },
    
    // Get heatmap data
    async getHeatmapData(period = 'all') {
        const response = await fetch(`${API_BASE_URL}/api/heatmap?period=${period}`);
        const data = await response.json();
        return data.data;
    },
    
    // Export CSV
    async exportCSV(period = 'all') {
        const response = await fetch(`${API_BASE_URL}/api/export/csv?period=${period}`);
        const data = await response.json();
        return data.filepath;
    },
    
    // Export PDF
    async exportPDF(period = 'all') {
        const response = await fetch(`${API_BASE_URL}/api/export/pdf?period=${period}`);
        const data = await response.json();
        return data.filepath;
    }
};

// WebSocket Event Handlers
socket.on('connect', () => {
    console.log('✅ Connected to Command Panel');
    updateConnectionStatus(true);
});

socket.on('disconnect', () => {
    console.log('❌ Disconnected from Command Panel');
    updateConnectionStatus(false);
});

socket.on('new_detection', (data) => {
    console.log('🚨 New detection:', data);
    handleNewDetection(data);
});

// Export API
window.API = API;
window.socket = socket;
```

---

### **js/map.js**

```javascript
// Initialize map
const map = L.map('map').setView([28.6139, 77.2090], 13);

// Add tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Store markers
const markers = {};

// Add detection marker
function addDetectionMarker(detection) {
    const { latitude, longitude, message, confidence, image_base64 } = detection;
    
    // Create marker
    const marker = L.marker([latitude, longitude], {
        icon: L.divIcon({
            className: 'detection-marker',
            html: `<div class="marker-icon ${getAlertClass(confidence)}">
                      <span>${Math.round(confidence * 100)}%</span>
                   </div>`
        })
    });
    
    // Create popup with image
    const popupContent = `
        <div class="detection-popup">
            <h3>${message}</h3>
            <img src="data:image/jpeg;base64,${image_base64}" alt="Detection" />
            <p><strong>GPS:</strong> ${latitude.toFixed(6)}, ${longitude.toFixed(6)}</p>
            <p><strong>Confidence:</strong> ${(confidence * 100).toFixed(2)}%</p>
            <p><strong>Time:</strong> ${detection.timestamp}</p>
        </div>
    `;
    
    marker.bindPopup(popupContent);
    marker.addTo(map);
    
    // Store marker
    const key = `${latitude}_${longitude}`;
    markers[key] = marker;
    
    return marker;
}

// Get alert class based on confidence
function getAlertClass(confidence) {
    if (confidence >= 0.85) return 'alert-high';
    if (confidence >= 0.70) return 'alert-medium';
    return 'alert-low';
}

// Export functions
window.addDetectionMarker = addDetectionMarker;
```

---

### **js/ui.js**

```javascript
// Handle new detection
function handleNewDetection(data) {
    const { detection, duration, detection_id } = data;
    
    // Add to map
    addDetectionMarker(detection);
    
    // Add to feed
    addToDetectionFeed(detection);
    
    // Show notification
    showNotification(detection.message, detection.confidence);
    
    // Update statistics
    updateStatistics();
}

// Add to detection feed
function addToDetectionFeed(detection) {
    const feed = document.getElementById('detection-feed');
    
    const item = document.createElement('div');
    item.className = `detection-item ${getAlertClass(detection.confidence)}`;
    item.innerHTML = `
        <div class="detection-header">
            <span class="detection-time">${detection.timestamp}</span>
            <span class="detection-confidence">${(detection.confidence * 100).toFixed(1)}%</span>
        </div>
        <div class="detection-body">
            <img src="data:image/jpeg;base64,${detection.image_base64}" alt="Detection" />
            <div class="detection-info">
                <p class="detection-message">${detection.message}</p>
                <p class="detection-gps">📍 ${detection.latitude.toFixed(6)}, ${detection.longitude.toFixed(6)}</p>
            </div>
        </div>
    `;
    
    feed.insertBefore(item, feed.firstChild);
    
    // Keep only last 20 items
    while (feed.children.length > 20) {
        feed.removeChild(feed.lastChild);
    }
}

// Update statistics dashboard
async function updateStatistics() {
    const stats = await API.getStatistics('today');
    
    document.getElementById('total-detections').textContent = stats.total_detections;
    document.getElementById('high-alerts').textContent = stats.high_alerts;
    document.getElementById('avg-confidence').textContent = (stats.average_confidence * 100).toFixed(1) + '%';
    document.getElementById('peak-hour').textContent = stats.peak_hour;
}

// Show notification
function showNotification(message, confidence) {
    const notification = document.createElement('div');
    notification.className = `notification ${getAlertClass(confidence)}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Update connection status
function updateConnectionStatus(connected) {
    const status = document.getElementById('connection-status');
    status.textContent = connected ? '🟢 Connected' : '🔴 Disconnected';
    status.className = connected ? 'connected' : 'disconnected';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    // Load initial detections
    const detections = await API.getLiveDetections();
    detections.forEach(detection => {
        addDetectionMarker(detection);
        addToDetectionFeed(detection);
    });
    
    // Update statistics
    updateStatistics();
    
    // Refresh statistics every 30 seconds
    setInterval(updateStatistics, 30000);
});
```

---

## 📦 Required Libraries

### For Frontend:

```html
<!-- Leaflet.js (Maps) -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<!-- Socket.IO (Real-time) -->
<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>

<!-- Optional: Chart.js (Statistics) -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

### For Backend (Already Installed):

```bash
pip install flask flask-socketio flask-cors
```

---

## 🔧 Setup Steps

### 1. **Start Backend Server**

```bash
cd CommandPanel
python server.py
```

**Expected output:**
```
🚀 AFK-ULTRON COMMAND PANEL SERVER
📡 Starting server on http://localhost:5000
✅ File watcher started
```

### 2. **Start Detection System**

```bash
cd Ultron
python app.py
```

### 3. **Open Frontend**

```bash
cd frontend
# Open index.html in browser
# Or use a local server:
python -m http.server 8000
# Then visit: http://localhost:8000
```

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    CAMERA (app.py)                          │
│  • Detects humans                                           │
│  • Draws annotations                                        │
│  • Encodes to base64                                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    Writes to JSON file
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              BACKEND SERVER (server.py)                     │
│  • File watcher detects change                              │
│  • Processes detection                                      │
│  • Stores in database                                       │
│  • Broadcasts via WebSocket                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
                ┌───────────┴───────────┐
                │                       │
         REST API                  WebSocket
                │                       │
                ↓                       ↓
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (HTML/JS)                       │
│  • Receives detection data                                  │
│  • Displays on map                                          │
│  • Shows image with annotations                             │
│  • Updates statistics                                       │
│  • Real-time notifications                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Summary

### **What Gets Exported:**

1. ✅ **Images** - Base64-encoded JPEG with detection boxes and GPS overlays
2. ✅ **GPS Coordinates** - Latitude and longitude (decimal degrees)
3. ✅ **Timestamps** - Detection time
4. ✅ **Confidence Scores** - AI confidence (0-100%)
5. ✅ **Messages** - Detection status ("TRACKING: X HUMANS")
6. ✅ **Alert Levels** - HIGH/MEDIUM/LOW
7. ✅ **Duration** - How long person was visible
8. ✅ **Statistics** - Total detections, peak hours, averages

### **Connection Methods:**

1. ✅ **REST API** - HTTP requests for data retrieval
2. ✅ **WebSocket** - Real-time push updates
3. ✅ **JSON File** - Direct file access (optional)

### **Frontend Needs:**

1. ✅ **Leaflet.js** - For map display
2. ✅ **Socket.IO** - For real-time updates
3. ✅ **Fetch API** - For HTTP requests
4. ✅ **Base64 decoder** - Built into browser

**Everything is ready for frontend integration!** 🚀
