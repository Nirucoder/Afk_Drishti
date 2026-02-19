"""
PHASE 1 - DATA FLOW VISUALIZATION
==================================

This diagram shows how detection data flows from the camera to the JSON file.


┌─────────────────────────────────────────────────────────────────────┐
│                         ULTRON APP (app.py)                         │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────┐
    │  CAMERA  │  (Webcam or IP Camera)
    └────┬─────┘
         │ Video Stream
         ▼
    ┌─────────────────┐
    │  cv2.VideoCapture│  Read frame
    └────┬────────────┘
         │ Frame (640x360)
         ▼
    ┌─────────────────┐
    │  YOLOv8 Model   │  OR  ┌──────────────┐
    │  (Local Edge)   │◄─────┤  Roboflow    │
    └────┬────────────┘      │  (Cloud API) │
         │                   └──────────────┘
         │ Detections
         ▼
    ┌──────────────────────────────────────┐
    │  Detection Found!                    │
    │  - Bounding box: [x1, y1, x2, y2]   │
    │  - Confidence: 0.87                  │
    │  - Class: Person                     │
    └────┬─────────────────────────────────┘
         │
         ▼
    ┌──────────────────────────────────────┐
    │  calculate_gps(x, y)                 │
    │  Convert pixel coords → GPS          │
    │  lat = 28.6139 + (y-180)*0.00001    │
    │  lon = 77.2090 + (x-320)*0.00001    │
    └────┬─────────────────────────────────┘
         │ GPS: (28.613912, 77.209045)
         ▼
    ┌──────────────────────────────────────┐
    │  trigger_alert()                     │
    │  - message: "HUMAN DETECTED"         │
    │  - lat: 28.613912                    │
    │  - lon: 77.209045                    │
    │  - confidence: 0.87                  │
    │  - frame: [numpy array]              │
    └────┬─────────────────────────────────┘
         │
         ▼
    ┌──────────────────────────────────────┐
    │  Encode Image                        │
    │  1. Resize: 640x360 → 320x180       │
    │  2. JPEG compress (70% quality)      │
    │  3. Base64 encode                    │
    └────┬─────────────────────────────────┘
         │ image_base64: "/9j/4AAQ..."
         ▼
    ┌──────────────────────────────────────┐
    │  Create JSON Dictionary              │
    │  {                                   │
    │    "timestamp": "2026-01-29 21:15",  │
    │    "latitude": 28.613912,            │
    │    "longitude": 77.209045,           │
    │    "confidence": 0.87,               │
    │    "message": "HUMAN DETECTED",      │
    │    "drone_id": "ULTRON-01",          │
    │    "image_base64": "/9j/4AAQ..."     │
    │  }                                   │
    └────┬─────────────────────────────────┘
         │
         ▼
    ┌──────────────────────────────────────┐
    │  send_to_command_panel()             │
    │  - Check if enabled                  │
    │  - Create directory if needed        │
    │  - Write JSON to file                │
    └────┬─────────────────────────────────┘
         │
         ▼
    ┌──────────────────────────────────────┐
    │  FILE SYSTEM                         │
    │  CommandPanel/data/live_feed.json    │
    │  [File is created/updated]           │
    └────┬─────────────────────────────────┘
         │
         │ ◄─── Phase 1 ends here
         │
         ▼
    ┌──────────────────────────────────────┐
    │  COMMAND PANEL (Phase 2)             │
    │  - Reads JSON file                   │
    │  - Stores in database                │
    │  - Displays on map                   │
    └──────────────────────────────────────┘


TIMING BREAKDOWN
================

Event                          Time (ms)    Cumulative
─────────────────────────────────────────────────────
Frame capture                      5           5
YOLOv8 inference                  50          55
GPS calculation                   <1          55
Image resize                       2          57
JPEG encode                        5          62
Base64 encode                      3          65
JSON creation                     <1          65
File write                         2          67
─────────────────────────────────────────────────────
TOTAL per detection              ~67ms

Note: This happens in parallel with video display,
so it doesn't slow down the GUI.


DATA SIZE BREAKDOWN
===================

Component              Size (bytes)    Percentage
───────────────────────────────────────────────────
timestamp                    20          0.1%
latitude                      8          0.04%
longitude                     8          0.04%
confidence                    4          0.02%
message                      20          0.1%
drone_id                     10          0.05%
image_base64             18,000         99.7%
───────────────────────────────────────────────────
TOTAL                   ~18,070 bytes   (~18 KB)

The image is the largest component. You can:
- Reduce image size (currently 320x180)
- Lower JPEG quality (currently 70%)
- Skip image entirely (set frame=None)


CONFIGURATION OPTIONS
======================

In app.py, you can customize:

1. Enable/Disable Export:
   ENABLE_COMMAND_PANEL = True/False

2. Output Path:
   JSON_OUTPUT_PATH = "../CommandPanel/data/live_feed.json"

3. Image Size (in trigger_alert):
   small_frame = cv2.resize(frame, (320, 180))
   Change to: (160, 90) for smaller files
              (640, 360) for better quality

4. JPEG Quality (in trigger_alert):
   [cv2.IMWRITE_JPEG_QUALITY, 70]
   Change to: 50 (smaller), 90 (better quality)

5. Drone ID (in trigger_alert):
   "drone_id": "ULTRON-01"
   Change to: "ULTRON-02" for second drone


ERROR HANDLING
==============

The system handles these errors gracefully:

❌ Directory doesn't exist
   → Auto-creates it

❌ Image encoding fails
   → Sends JSON without image

❌ JSON write fails
   → Prints error, continues running

❌ Command panel disabled
   → Skips export, no overhead

This ensures the main detection app never crashes
due to command panel issues.
"""

print(__doc__)
