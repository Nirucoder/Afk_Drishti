# 🚀 AFK-Ultron Command Panel - Quick Start Guide

## ⚡ 3-Step Launch

### **Step 1: Start Backend Server**

```powershell
cd c:\Users\user\Desktop\AFK-Ultron-main\CommandPanel
python server.py
```

Expected output:
```
🚀 AFK-ULTRON COMMAND PANEL SERVER
📡 Starting server on http://localhost:5000
🔌 WebSocket enabled for real-time updates
👁️  Monitoring: data/live_feed.json
```

### **Step 2: Start Drone Detection (Optional)**

Open a **new terminal**:

```powershell
cd c:\Users\user\Desktop\AFK-Ultron-main\Ultron
python app.py
```

### **Step 3: Open Command Panel**

Open your browser and navigate to:

```
http://localhost:5000
```

---

## ✅ Verification Checklist

After opening the dashboard, verify:

- ✅ **Map loads** with geofence circle
- ✅ **Connection status** shows "Connected" (green dot)
- ✅ **Statistics** display (may show 0 if no detections yet)
- ✅ **Browser console** shows:
  ```
  🗺️ Tactical map initialized
  ✅ WebSocket connected
  ✅ Command Panel initialized successfully
  ```

---

## 🎯 Testing Real-Time Detection

1. **Point camera at a person** (if using Ultron app)
2. **Wait for detection** (YOLO will detect and export JSON)
3. **Watch dashboard update**:
   - New marker appears on map
   - Alert appears in feed with image
   - Statistics update
   - Alert sound plays
   - Toast notification shows

---

## 🔧 Troubleshooting

### **Dashboard shows "Disconnected"**

**Solution:**
- Verify backend server is running
- Check `http://localhost:5000/api` returns JSON
- Restart backend server

### **Map not loading**

**Solution:**
- Check internet connection (needs OpenStreetMap tiles)
- Check browser console for errors
- Try refreshing page (Ctrl+F5)

### **No alerts appearing**

**Solution:**
- Verify Ultron app is running and detecting
- Check `CommandPanel/data/live_feed.json` is being updated
- Check backend console for file watcher messages

### **CORS errors**

**Solution:**
```powershell
pip install flask-cors
```

---

## 📊 Features Overview

| Feature | Description |
|---------|-------------|
| **Live Map** | Interactive map with detection markers |
| **Alerts Feed** | Real-time scrolling alerts with images |
| **Statistics** | Total detections, peak hour, avg confidence |
| **Export** | CSV and PDF export buttons |
| **WebSocket** | Real-time updates without refresh |
| **Alert Sounds** | Audio notifications for new detections |

---

## 🎨 What You Should See

### **Header**
- Title: "🛡️ AFK-ULTRON COMMAND PANEL"
- Connection status: Green dot + "Connected"
- Drone ID: "ULTRON-01"

### **Left Panel (Map)**
- Interactive map centered on Delhi
- Red dashed circle (5km geofence)
- Green dot at center (Command Center)
- Detection markers (red/orange/green based on confidence)

### **Right Panel (Sidebar)**
- **Alerts Feed**: Scrolling list of detections with images
- **Statistics**: 4 cards showing metrics
- **Export Buttons**: CSV and PDF export

---

## 🔄 Data Flow

```
Camera → Ultron/app.py → live_feed.json → server.py → WebSocket → Dashboard
```

1. Camera detects person
2. Ultron exports JSON to `CommandPanel/data/live_feed.json`
3. Backend server watches file and detects change
4. After 5-second persistence, stores in database
5. Emits WebSocket event `new_detection`
6. Dashboard receives event and updates UI

---

## 📝 Configuration

### **Change Map Center**

Edit `frontend/js/app.js` (line 96):
```javascript
this.map = new TacticalMap('map', [YOUR_LAT, YOUR_LON], 14);
```

### **Change API URL**

Edit `frontend/css/js/api.js` (line 8):
```javascript
const CONFIG = {
    API_BASE_URL: 'http://YOUR_SERVER:5000',
    SOCKET_URL: 'http://YOUR_SERVER:5000'
};
```

---

## 🌐 Access from Other Devices

### **Find Your PC's IP Address**

```powershell
ipconfig
```

Look for "IPv4 Address" (e.g., `192.168.1.100`)

### **Open on Other Device**

```
http://192.168.1.100:5000
```

### **Allow Firewall Access**

```powershell
# Run as Administrator
netsh advfirewall firewall add rule name="Flask Server" dir=in action=allow protocol=TCP localport=5000
```

---

## 📚 Next Steps

1. ✅ **Customize** - Change colors, map center, thresholds
2. ✅ **Test** - Run Ultron and see real-time updates
3. ✅ **Export** - Try CSV and PDF export
4. ✅ **Deploy** - Host on server for remote access

---

## 🎉 You're Ready!

Your AFK-Ultron Command Panel is now fully operational!

**Enjoy real-time drone surveillance monitoring!** 🚁🛡️
