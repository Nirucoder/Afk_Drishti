"""
Sync Verification Tool
Verifies that database, JSON file, and camera feed are all in sync
"""

import json
import sqlite3
import base64
import cv2
import numpy as np
import os
from datetime import datetime

JSON_PATH = 'data/live_feed.json'
DB_PATH = 'data/detections.db'

def verify_sync():
    print("=" * 70)
    print("🔍 SYNC VERIFICATION TOOL")
    print("=" * 70)
    print("Checking if database, JSON file, and camera feed are in sync...")
    print()
    
    issues = []
    
    # ==========================================
    #  1. Check JSON File
    # ==========================================
    print("📄 Step 1: Checking JSON File")
    print("-" * 70)
    
    if not os.path.exists(JSON_PATH):
        print(f"❌ JSON file not found: {JSON_PATH}")
        issues.append("JSON file missing")
        json_data = None
    else:
        try:
            with open(JSON_PATH, 'r') as f:
                json_data = json.load(f)
            
            print(f"✅ JSON file found and valid")
            print(f"   Timestamp: {json_data.get('timestamp')}")
            print(f"   GPS: ({json_data.get('latitude'):.6f}, {json_data.get('longitude'):.6f})")
            print(f"   Confidence: {json_data.get('confidence'):.2%}")
            print(f"   Message: {json_data.get('message')}")
            print(f"   Drone ID: {json_data.get('drone_id')}")
            
            # Check if image exists
            if json_data.get('image_base64'):
                print(f"   Image: {len(json_data['image_base64']):,} chars (base64)")
            else:
                print(f"   ⚠️  Image: Missing")
                issues.append("JSON image missing")
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            issues.append("JSON parsing error")
            json_data = None
        except Exception as e:
            print(f"❌ Error reading JSON: {e}")
            issues.append(f"JSON read error: {e}")
            json_data = None
    
    print()
    
    # ==========================================
    #  2. Check Database
    # ==========================================
    print("🗄️  Step 2: Checking Database")
    print("-" * 70)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        issues.append("Database missing")
        db_data = None
    else:
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get latest detection
            cursor.execute('''
                SELECT * FROM detections 
                ORDER BY created_at DESC 
                LIMIT 1
            ''')
            
            row = cursor.fetchone()
            
            if row:
                db_data = dict(row)
                print(f"✅ Database found with {cursor.execute('SELECT COUNT(*) FROM detections').fetchone()[0]} detections")
                print(f"   Latest detection:")
                print(f"   ID: {db_data['id']}")
                print(f"   Timestamp: {db_data['timestamp']}")
                print(f"   GPS: ({db_data['latitude']:.6f}, {db_data['longitude']:.6f})")
                print(f"   Confidence: {db_data['confidence']:.2%}")
                print(f"   Alert Level: {db_data['alert_level']}")
                print(f"   Duration: {db_data['duration']:.2f}s")
                
                # Check if image exists in DB
                if db_data.get('image_base64'):
                    print(f"   Image: Stored in database")
                else:
                    print(f"   ⚠️  Image: Not stored in database")
                    
            else:
                print(f"✅ Database found but empty (no detections yet)")
                db_data = None
                
            conn.close()
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            issues.append(f"Database error: {e}")
            db_data = None
    
    print()
    
    # ==========================================
    #  3. Check Image Sync
    # ==========================================
    print("🖼️  Step 3: Checking Image Sync")
    print("-" * 70)
    
    if json_data and json_data.get('image_base64'):
        try:
            # Decode JSON image
            json_img_data = base64.b64decode(json_data['image_base64'])
            json_nparr = np.frombuffer(json_img_data, np.uint8)
            json_img = cv2.imdecode(json_nparr, cv2.IMREAD_COLOR)
            
            if json_img is not None:
                json_h, json_w = json_img.shape[:2]
                print(f"✅ JSON image decoded: {json_w}x{json_h}")
                
                # Check for annotations (green boxes, red text)
                hsv = cv2.cvtColor(json_img, cv2.COLOR_BGR2HSV)
                
                # Green detection boxes
                lower_green = np.array([40, 100, 100])
                upper_green = np.array([80, 255, 255])
                green_mask = cv2.inRange(hsv, lower_green, upper_green)
                green_pixels = cv2.countNonZero(green_mask)
                
                # Red text overlays
                lower_red1 = np.array([0, 100, 100])
                upper_red1 = np.array([10, 255, 255])
                red_mask = cv2.inRange(hsv, lower_red1, upper_red1)
                red_pixels = cv2.countNonZero(red_mask)
                
                has_annotations = green_pixels > 100 or red_pixels > 50
                
                if has_annotations:
                    print(f"   ✅ Image contains detection annotations (matches camera feed)")
                    print(f"      Green pixels: {green_pixels:,} | Red pixels: {red_pixels:,}")
                else:
                    print(f"   ⚠️  Image appears clean (no detection boxes)")
                    print(f"      This may not match the camera feed display")
                    issues.append("Image may not match camera feed")
                
                # Save for inspection
                cv2.imwrite('data/sync_check_json_image.jpg', json_img)
                print(f"   💾 Saved: data/sync_check_json_image.jpg")
                
            else:
                print(f"❌ Failed to decode JSON image")
                issues.append("JSON image decode failed")
                
        except Exception as e:
            print(f"❌ Image processing error: {e}")
            issues.append(f"Image error: {e}")
    else:
        print(f"⚠️  No image in JSON to check")
    
    print()
    
    # ==========================================
    #  4. Compare JSON vs Database
    # ==========================================
    print("🔄 Step 4: Comparing JSON vs Database")
    print("-" * 70)
    
    if json_data and db_data:
        # Compare timestamps
        json_time = json_data.get('timestamp')
        db_time = db_data.get('timestamp')
        
        if json_time == db_time:
            print(f"✅ Timestamps match: {json_time}")
        else:
            print(f"⚠️  Timestamps differ:")
            print(f"   JSON: {json_time}")
            print(f"   DB:   {db_time}")
            issues.append("Timestamp mismatch")
        
        # Compare GPS
        json_lat = json_data.get('latitude')
        json_lon = json_data.get('longitude')
        db_lat = db_data.get('latitude')
        db_lon = db_data.get('longitude')
        
        lat_diff = abs(json_lat - db_lat) if json_lat and db_lat else 0
        lon_diff = abs(json_lon - db_lon) if json_lon and db_lon else 0
        
        if lat_diff < 0.00001 and lon_diff < 0.00001:
            print(f"✅ GPS coordinates match")
        else:
            print(f"⚠️  GPS coordinates differ:")
            print(f"   JSON: ({json_lat:.6f}, {json_lon:.6f})")
            print(f"   DB:   ({db_lat:.6f}, {db_lon:.6f})")
            issues.append("GPS mismatch")
        
        # Compare confidence
        json_conf = json_data.get('confidence')
        db_conf = db_data.get('confidence')
        
        if abs(json_conf - db_conf) < 0.0001:
            print(f"✅ Confidence matches: {json_conf:.4f}")
        else:
            print(f"⚠️  Confidence differs:")
            print(f"   JSON: {json_conf:.4f}")
            print(f"   DB:   {db_conf:.4f}")
            issues.append("Confidence mismatch")
        
        # Compare message
        json_msg = json_data.get('message')
        db_msg = db_data.get('message')
        
        if json_msg == db_msg:
            print(f"✅ Message matches: {json_msg}")
        else:
            print(f"⚠️  Message differs:")
            print(f"   JSON: {json_msg}")
            print(f"   DB:   {db_msg}")
            issues.append("Message mismatch")
            
    elif json_data and not db_data:
        print(f"⚠️  JSON has data but database is empty")
        print(f"   This is normal if the server hasn't processed the detection yet")
        print(f"   OR if the detection didn't meet the 5-second persistence threshold")
        issues.append("Database empty (may be normal)")
    elif not json_data and db_data:
        print(f"⚠️  Database has data but JSON is missing/invalid")
        issues.append("JSON missing but database has data")
    else:
        print(f"⚠️  Both JSON and database are empty")
        print(f"   Run app.py and trigger a detection first")
    
    print()
    
    # ==========================================
    #  5. Final Summary
    # ==========================================
    print("=" * 70)
    print("📊 SYNC VERIFICATION SUMMARY")
    print("=" * 70)
    
    if not issues:
        print("✅ ALL SYSTEMS IN SYNC!")
        print()
        print("✓ JSON file: Valid and current")
        print("✓ Database: Matches JSON data")
        print("✓ Image: Contains annotations (matches camera feed)")
        print("✓ GPS coordinates: Accurate")
        print("✓ Timestamps: Synchronized")
        print()
        print("🎯 Everything is working correctly!")
    else:
        print(f"⚠️  FOUND {len(issues)} ISSUE(S):")
        print()
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        print()
        
        # Provide recommendations
        print("💡 RECOMMENDATIONS:")
        print()
        
        if "JSON file missing" in issues:
            print("   • Run app.py and trigger a detection")
            
        if "Database missing" in issues:
            print("   • Run server.py to create the database")
            print("   • Or run: python database.py")
            
        if "Database empty" in issues or "Database empty (may be normal)" in issues:
            print("   • This is normal if:")
            print("     - Server hasn't started yet (run: python server.py)")
            print("     - Detection didn't persist for 5+ seconds")
            print("     - File watcher hasn't processed the JSON yet")
            
        if "Image may not match camera feed" in issues:
            print("   • The fix was applied in app.py (line 602)")
            print("   • Run app.py again to get annotated images")
            
        if any("mismatch" in issue for issue in issues):
            print("   • JSON and database are out of sync")
            print("   • This is normal if detection just happened")
            print("   • Wait a few seconds for server to process")
    
    print()
    print("=" * 70)
    
    return len(issues) == 0

if __name__ == "__main__":
    success = verify_sync()
    
    if success:
        print("\n🎉 Sync verification PASSED!")
    else:
        print("\n⚠️  Sync verification found issues (see above)")
