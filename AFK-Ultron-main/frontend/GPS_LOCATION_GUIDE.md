# 📍 GPS Location Feature - User Guide

## ✨ New Feature Added!

You can now **set a custom GPS location** to center the map on any coordinates you want!

---

## 🎯 How to Use

### **Step 1: Click the GPS Location Button**

Look for the **📍 pin icon** in the map controls (top-right of the map section).

### **Step 2: Enter Coordinates**

A modal dialog will appear with two input fields:
- **Latitude**: Enter value between -90 and 90
- **Longitude**: Enter value between -180 and 180

### **Step 3: Apply Location**

Click the **"Apply Location"** button to update the map center.

---

## 📊 What Happens

When you apply a new location:

1. ✅ **Map centers** on the new coordinates
2. ✅ **Geofence updates** to the new center (5km radius)
3. ✅ **Current location display** updates (bottom-right of map)
4. ✅ **Toast notification** confirms the change
5. ✅ **Console logs** the new coordinates

---

## 🗺️ Current Location Display

The **current map center** is always visible at the bottom-right of the map:

```
📍 Map Center: 28.6139, 77.2090
```

This updates automatically when you:
- Set a custom location
- Center the map (reset button)

---

## 🌍 Example Coordinates

Try these famous locations:

| Location | Latitude | Longitude |
|----------|----------|-----------|
| **New Delhi, India** | 28.6139 | 77.2090 |
| **New York, USA** | 40.7128 | -74.0060 |
| **London, UK** | 51.5074 | -0.1278 |
| **Tokyo, Japan** | 35.6762 | 139.6503 |
| **Sydney, Australia** | -33.8688 | 151.2093 |
| **Paris, France** | 48.8566 | 2.3522 |
| **Dubai, UAE** | 25.2048 | 55.2708 |

---

## ⌨️ Keyboard Shortcuts

- **ESC**: Close the modal (coming soon)
- **Enter**: Apply location (coming soon)

---

## ✅ Validation

The system validates your input:

- ❌ **Invalid numbers**: Shows error toast
- ❌ **Latitude out of range**: Must be -90 to 90
- ❌ **Longitude out of range**: Must be -180 to 180
- ✅ **Valid coordinates**: Updates map successfully

---

## 🎨 UI Features

### **Modal Dialog**
- Dark tactical theme
- Smooth slide-in animation
- Click outside to close
- Close button (×)
- Cancel button
- Apply button with gradient

### **Current Location Badge**
- Always visible on map
- Bottom-right corner
- Glassmorphism effect
- Green monospace font
- Updates in real-time

### **GPS Location Button**
- Pin icon (📍)
- Hover effect (green glow)
- Tooltip: "Set GPS Location"

---

## 🔧 Technical Details

### **Default Location**
- Latitude: 28.6139
- Longitude: 77.2090
- Location: New Delhi, India

### **Geofence**
- Radius: 5000 meters (5km)
- Color: Red (#ff4444)
- Opacity: 0.1
- Auto-updates with location

### **Precision**
- Input: 6 decimal places
- Display: 4 decimal places
- Storage: Full precision

---

## 📝 Use Cases

1. **Monitor Different Locations**: Switch between multiple surveillance areas
2. **Test Detections**: Set location to match your camera's GPS
3. **Plan Operations**: Preview different operational zones
4. **Training**: Demonstrate system with various locations
5. **Multi-Site Management**: Quickly switch between sites

---

## 🚀 Future Enhancements

Planned features:
- 🔖 **Save favorite locations**
- 🗺️ **Click on map to set location**
- 📍 **Use browser geolocation**
- 📋 **Location history**
- 🔍 **Search by address**
- ⌨️ **Keyboard shortcuts**

---

## 🐛 Troubleshooting

### **Modal won't open**
- Check browser console for errors
- Ensure JavaScript is enabled
- Refresh the page

### **Location not updating**
- Verify coordinates are valid
- Check latitude/longitude ranges
- Look for error toast messages

### **Geofence not visible**
- Zoom out to see full circle
- Check if geofence is behind other elements
- Try refreshing the page

---

## 💡 Tips

1. **Use decimal degrees** format (not degrees/minutes/seconds)
2. **Negative values** for South latitude and West longitude
3. **Copy coordinates** from Google Maps (right-click → coordinates)
4. **Test with known locations** first
5. **Check current location** display to confirm changes

---

## 📞 Quick Reference

| Action | Button | Location |
|--------|--------|----------|
| **Set Location** | 📍 Pin icon | Map controls (top-right) |
| **View Current** | Badge | Map (bottom-right) |
| **Reset to Default** | 🎯 Center icon | Map controls |
| **Close Modal** | × or Cancel | Modal dialog |

---

**Enjoy exploring different locations on your AFK-Ultron Command Panel!** 🌍🛡️
