# ✅ HOW TO TEST IF EVERYTHING IS WORKING

## 🎯 Quick Test Guide

Follow these steps **IN ORDER** to verify everything is working:

---

## Step 1: Run Detection System

**Open Terminal 1:**
```bash
cd C:\Users\user\Desktop\AFK-Ultron-main\Ultron
python app.py
```

**What to do:**
1. Point camera at a person
2. Wait for detection (you'll see green boxes on screen)
3. Keep the app running

**Expected output:**
- Window opens showing camera feed
- Green detection boxes appear around people
- Red GPS text shows coordinates
- Console shows "✅ Detection sent to Command Panel"

---

## Step 2: Verify JSON Export

**Open Terminal 2:**
```bash
cd C:\Users\user\Desktop\AFK-Ultron-main\CommandPanel
dir data\live_feed.json
```

**Expected output:**
```
 Volume in drive C is Windows
 Directory of C:\Users\user\Desktop\AFK-Ultron-main\CommandPanel\data

29-01-2026  23:37         9,019 live_feed.json
```

**If you see the file:** ✅ JSON export is working!

**If file is missing:** ❌ Check:
- Is `app.py` running?
- Did you trigger a detection?
- Check `ENABLE_COMMAND_PANEL = True` in app.py (line 52)

---

## Step 3: Check JSON Content

**In Terminal 2:**
```bash
cd C:\Users\user\Desktop\AFK-Ultron-main\CommandPanel
python -c "import json; print(json.dumps(json.load(open('data/live_feed.json')), indent=2)[:500])"
```

**Expected output:**
```json
{
  "timestamp": "2026-01-29 23:37:56",
  "latitude": 28.613909,
  "longitude": 77.209002,
  "confidence": 0.9262,
  "message": "NEW TARGET: 4 TOTAL",
  "drone_id": "ULTRON-01",
  "image_base64": "/9j/4AAQSkZJRg..."
}
```

**If you see this:** ✅ JSON structure is correct!

---

## Step 4: Verify Image Annotations

**In Terminal 2:**
```bash
cd C:\Users\user\Desktop\AFK-Ultron-main\CommandPanel
python compare_frames.py
```

**Expected output:**
```
✅ Image contains detection annotations (matches camera feed)
   Green pixels: 8,508 | Red pixels: 1,982
```

**If you see this:** ✅ Frame matching is working! Images have detection boxes!

---

## Step 5: Run Full Sync Verification

**In Terminal 2 (IMPORTANT: Must be in CommandPanel directory):**
```bash
cd C:\Users\user\Desktop\AFK-Ultron-main\CommandPanel
python verify_sync.py
```

**Expected output (without server):**
```
✅ JSON file found and valid
   Timestamp: 2026-01-29 23:37:56
   GPS: (28.613909, 77.209002)
   Confidence: 92.62%
   
✅ Image contains detection annotations (matches camera feed)
   Green pixels: 8,508 | Red pixels: 1,982

⚠️ Database has old data (server not running yet)
```

**If you see this:** ✅ Phase 1 (JSON Export) is working perfectly!

---

## Step 6: Start Backend Server (Optional - Phase 2)

**Open Terminal 3:**
```bash
cd C:\Users\user\Desktop\AFK-Ultron-main\CommandPanel
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

**If you see this:** ✅ Backend server is running!

---

## Step 7: Verify Full System Integration

**In Terminal 2:**
```bash
cd C:\Users\user\Desktop\AFK-Ultron-main\CommandPanel
python verify_sync.py
```

**Expected output (with server running):**
```
✅ ALL SYSTEMS IN SYNC!

✓ JSON file: Valid and current
✓ Database: Matches JSON data
✓ Image: Contains annotations (matches camera feed)
✓ GPS coordinates: Accurate
✓ Timestamps: Synchronized

🎯 Everything is working correctly!
```

**If you see this:** ✅ **EVERYTHING IS WORKING PERFECTLY!**

---

## 🚨 Common Issues & Solutions

### Issue 1: "JSON file not found"

**Cause:** Running verify_sync.py from wrong directory

**Solution:**
```bash
# WRONG (from project root)
cd C:\Users\user\Desktop\AFK-Ultron-main
python CommandPanel\verify_sync.py  # ❌ FAILS

# CORRECT (from CommandPanel directory)
cd C:\Users\user\Desktop\AFK-Ultron-main\CommandPanel
python verify_sync.py  # ✅ WORKS
```

### Issue 2: "Database not found"

**Cause:** Server hasn't run yet

**Solution:**
```bash
cd CommandPanel
python server.py
```

### Issue 3: "Image appears clean (no detection boxes)"

**Cause:** Using old JSON from before the fix

**Solution:**
```bash
cd Ultron
python app.py
# Trigger a NEW detection
```

---

## 📊 Quick Checklist

Use this to verify each component:

### Phase 1: JSON Export
- [ ] `app.py` runs without errors
- [ ] Detection boxes appear on camera feed
- [ ] `data/live_feed.json` file exists
- [ ] JSON contains all fields (timestamp, GPS, confidence, message, image_base64)
- [ ] Image has annotations (green boxes, red text)

### Phase 2: Backend (Optional)
- [ ] `server.py` starts without errors
- [ ] Server shows "File watcher started"
- [ ] Database file created (`data/detections.db`)
- [ ] API accessible at `http://localhost:5000`

### Full Integration
- [ ] `verify_sync.py` shows "ALL SYSTEMS IN SYNC"
- [ ] JSON and database timestamps match
- [ ] Images contain detection annotations

---

## 🎯 Minimal Test (Just Phase 1)

If you only want to test Phase 1 (JSON export):

```bash
# Terminal 1
cd C:\Users\user\Desktop\AFK-Ultron-main\Ultron
python app.py

# Terminal 2 (after detection)
cd C:\Users\user\Desktop\AFK-Ultron-main\CommandPanel
dir data\live_feed.json
python compare_frames.py
```

**Success criteria:**
- ✅ `live_feed.json` exists
- ✅ Image has green boxes and red text
- ✅ Console shows "✅ Detection sent to Command Panel"

---

## 🏆 Success Indicators

### You know it's working when:

1. **app.py console shows:**
   ```
   ✅ Detection sent to Command Panel: NEW TARGET: 5 TOTAL @ (28.61467, 77.20891)
   ```

2. **Camera feed shows:**
   - Green corner brackets around people
   - Red text: "THREAT LOC: 28.61467, 77.20891"

3. **compare_frames.py shows:**
   ```
   ✅ Image contains detection annotations (matches camera feed)
   ```

4. **verify_sync.py shows:**
   ```
   ✅ JSON file found and valid
   ✅ Image contains detection annotations
   ```

---

## 📝 Summary

**To test if everything is working:**

1. **Run app.py** (in Ultron directory)
2. **Trigger detection** (point camera at person)
3. **Check JSON exists** (`dir CommandPanel\data\live_feed.json`)
4. **Verify annotations** (`python compare_frames.py` in CommandPanel)
5. **Run sync check** (`python verify_sync.py` in CommandPanel)

**If all 5 steps pass:** ✅ **EVERYTHING IS WORKING PERFECTLY!**

---

**Important:** Always run `verify_sync.py` from the **CommandPanel** directory, not the project root!

```bash
# CORRECT ✅
cd CommandPanel
python verify_sync.py

# WRONG ❌
python CommandPanel\verify_sync.py
```
