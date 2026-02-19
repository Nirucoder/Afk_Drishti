"""
JSON Detection Viewer - Test script for Command Panel integration
This script monitors the live_feed.json file and displays detection data
"""

import json
import os
import time
from datetime import datetime

JSON_PATH = "data/live_feed.json"

def watch_json_file():
    """Monitor the JSON file for changes and display detection data"""
    print("=" * 60)
    print("🔍 ULTRON COMMAND PANEL - JSON VIEWER")
    print("=" * 60)
    print(f"Monitoring: {JSON_PATH}")
    print("Waiting for detections from app.py...\n")
    
    last_modified = 0
    detection_count = 0
    
    while True:
        try:
            if os.path.exists(JSON_PATH):
                current_modified = os.path.getmtime(JSON_PATH)
                
                if current_modified > last_modified:
                    with open(JSON_PATH, 'r') as f:
                        data = json.load(f)
                    
                    detection_count += 1
                    
                    print(f"\n{'='*60}")
                    print(f"🚨 DETECTION #{detection_count}")
                    print(f"{'='*60}")
                    print(f"⏰ Timestamp:  {data['timestamp']}")
                    print(f"📍 GPS:        {data['latitude']:.6f}, {data['longitude']:.6f}")
                    print(f"🎯 Confidence: {data['confidence']:.2%}")
                    print(f"📢 Message:    {data['message']}")
                    print(f"🛸 Drone ID:   {data['drone_id']}")
                    
                    if data.get('image_base64'):
                        img_size = len(data['image_base64'])
                        print(f"📸 Image:      {img_size:,} bytes (base64)")
                    else:
                        print(f"📸 Image:      Not included")
                    
                    print(f"{'='*60}")
                    
                    last_modified = current_modified
            else:
                print(f"⏳ Waiting for {JSON_PATH} to be created...")
            
            time.sleep(0.5)
            
        except KeyboardInterrupt:
            print("\n\n👋 Stopping JSON viewer...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    # Ensure we're in the CommandPanel directory
    if not os.path.exists("data"):
        os.makedirs("data")
    
    watch_json_file()
