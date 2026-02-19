"""
Frame Comparison Tool
Compares the JSON exported image with what should be displayed in the camera feed
"""

import json
import base64
import cv2
import numpy as np
import os

JSON_PATH = "data/live_feed.json"

def compare_frames():
    print("=" * 70)
    print("🔍 FRAME COMPARISON TOOL")
    print("=" * 70)
    
    if not os.path.exists(JSON_PATH):
        print(f"❌ ERROR: {JSON_PATH} not found!")
        print("   Please run app.py and trigger a detection first.")
        return
    
    # Check if file is empty
    if os.path.getsize(JSON_PATH) == 0:
        print(f"\n⚠️  JSON file is empty!")
        print()
        print("💡 This means:")
        print("   • app.py is running but hasn't detected anything yet")
        print("   • Point camera at a person and wait for detection")
        print("   • The file will be populated automatically")
        return
    
    # Load JSON with error handling and retry mechanism
    max_retries = 3
    retry_delay = 0.5  # seconds
    
    for attempt in range(max_retries):
        try:
            # Add small delay to avoid race conditions
            if attempt > 0:
                import time
                print(f"   Retry {attempt}/{max_retries}...")
                time.sleep(retry_delay)
            
            with open(JSON_PATH, 'r') as f:
                content = f.read()
                if not content.strip():
                    if attempt < max_retries - 1:
                        continue  # Retry
                    print(f"\n⚠️  JSON file is empty after {max_retries} attempts!")
                    print()
                    print("💡 Possible causes:")
                    print("   • app.py is continuously rewriting the file")
                    print("   • File is being cleared between writes")
                    print()
                    print("🔧 Solution:")
                    print("   • Wait for a detection to complete")
                    print("   • Try running this script again in a few seconds")
                    return
                data = json.loads(content)
                break  # Success!
                
        except json.JSONDecodeError as e:
            if attempt < max_retries - 1:
                continue  # Retry
            print(f"\n❌ JSON parsing error after {max_retries} attempts: {e}")
            print()
            print("💡 Possible causes:")
            print("   • File is being written while we're reading it (race condition)")
            print("   • File is corrupted")
            print()
            print("🔧 Solutions:")
            print("   1. Wait a moment and try again")
            print("   2. Trigger a new detection in app.py")
            print("   3. Check if app.py is running properly")
            return
        except Exception as e:
            if attempt < max_retries - 1:
                continue  # Retry
            print(f"\n❌ Error reading JSON after {max_retries} attempts: {e}")
            return
    
    print(f"\n📋 Detection Info:")
    print(f"   Timestamp: {data['timestamp']}")
    print(f"   Message: {data['message']}")
    print(f"   GPS: ({data['latitude']:.6f}, {data['longitude']:.6f})")
    print(f"   Confidence: {data['confidence']:.2%}")
    
    # Decode base64 image
    if data.get('image_base64'):
        img_data = base64.b64decode(data['image_base64'])
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is not None:
            height, width = img.shape[:2]
            print(f"\n🖼️  Exported Image:")
            print(f"   Dimensions: {width}x{height}")
            print(f"   Size: {len(img_data):,} bytes")
            
            # Check if image has detection boxes
            # Detection boxes are typically green (0, 255, 0) or red/orange
            # Let's check for non-natural colors
            
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            # Check for green (detection boxes)
            lower_green = np.array([40, 100, 100])
            upper_green = np.array([80, 255, 255])
            green_mask = cv2.inRange(hsv, lower_green, upper_green)
            green_pixels = cv2.countNonZero(green_mask)
            
            # Check for red/orange (text overlays)
            lower_red1 = np.array([0, 100, 100])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 100, 100])
            upper_red2 = np.array([180, 255, 255])
            red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            red_pixels = cv2.countNonZero(red_mask1) + cv2.countNonZero(red_mask2)
            
            total_pixels = width * height
            
            print(f"\n🎨 Annotation Detection:")
            print(f"   Green pixels (boxes): {green_pixels:,} ({green_pixels/total_pixels*100:.2f}%)")
            print(f"   Red pixels (text): {red_pixels:,} ({red_pixels/total_pixels*100:.2f}%)")
            
            if green_pixels > 100 or red_pixels > 100:
                print(f"\n✅ MATCH: Image contains detection annotations")
                print(f"   The exported image matches the camera feed display!")
            else:
                print(f"\n⚠️  WARNING: Image appears to be clean (no annotations)")
                print(f"   The exported image is the RAW frame, not the annotated display")
                print(f"\n   This means:")
                print(f"   • JSON export: Clean frame (no boxes)")
                print(f"   • GUI display: Annotated frame (with boxes)")
                print(f"   • They DON'T match!")
            
            # Save comparison
            cv2.imwrite('data/comparison_frame.jpg', img)
            print(f"\n💾 Saved: data/comparison_frame.jpg")
            
            # Display
            print(f"\n👁️  Displaying image... (Press any key to close)")
            cv2.imshow('JSON Exported Frame', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
        else:
            print(f"❌ Failed to decode image")
    else:
        print(f"❌ No image data in JSON")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    compare_frames()
