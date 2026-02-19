"""
JSON Export Verification Script
This script validates the JSON data exported by app.py
"""

import json
import os
import base64
import cv2
import numpy as np
from datetime import datetime

JSON_PATH = "data/live_feed.json"

def verify_json_structure():
    """Verify that the JSON file has the correct structure"""
    print("=" * 70)
    print("🔍 ULTRON COMMAND PANEL - JSON EXPORT VERIFICATION")
    print("=" * 70)
    
    if not os.path.exists(JSON_PATH):
        print(f"❌ ERROR: {JSON_PATH} does not exist!")
        print("   Please run app.py and trigger a detection first.")
        return False
    
    print(f"✅ JSON file found: {JSON_PATH}")
    print()
    
    try:
        with open(JSON_PATH, 'r') as f:
            data = json.load(f)
        
        print("📋 JSON STRUCTURE VALIDATION")
        print("-" * 70)
        
        # Required fields
        required_fields = {
            'timestamp': str,
            'latitude': (int, float),
            'longitude': (int, float),
            'confidence': (int, float),
            'message': str,
            'drone_id': str,
            'image_base64': (str, type(None))
        }
        
        all_valid = True
        
        for field, expected_type in required_fields.items():
            if field in data:
                if isinstance(data[field], expected_type):
                    print(f"✅ {field:15} : {type(data[field]).__name__:10} ✓")
                else:
                    print(f"❌ {field:15} : {type(data[field]).__name__:10} (expected {expected_type})")
                    all_valid = False
            else:
                print(f"❌ {field:15} : MISSING")
                all_valid = False
        
        print()
        print("=" * 70)
        print("📊 DATA VALIDATION")
        print("=" * 70)
        
        # Validate timestamp format
        try:
            timestamp = datetime.strptime(data['timestamp'], "%Y-%m-%d %H:%M:%S")
            print(f"✅ Timestamp format valid: {data['timestamp']}")
        except:
            print(f"❌ Invalid timestamp format: {data['timestamp']}")
            all_valid = False
        
        # Validate GPS coordinates
        lat = data['latitude']
        lon = data['longitude']
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            print(f"✅ GPS coordinates valid: ({lat:.6f}, {lon:.6f})")
        else:
            print(f"❌ GPS coordinates out of range: ({lat}, {lon})")
            all_valid = False
        
        # Validate confidence
        conf = data['confidence']
        if 0.0 <= conf <= 1.0:
            print(f"✅ Confidence valid: {conf:.2%}")
        else:
            print(f"⚠️  Confidence unusual: {conf} (expected 0.0-1.0)")
        
        # Validate message
        if data['message']:
            print(f"✅ Message: \"{data['message']}\"")
        else:
            print(f"⚠️  Message is empty")
        
        # Validate drone_id
        if data['drone_id']:
            print(f"✅ Drone ID: {data['drone_id']}")
        else:
            print(f"⚠️  Drone ID is empty")
        
        print()
        print("=" * 70)
        print("🖼️  IMAGE VALIDATION")
        print("=" * 70)
        
        # Validate base64 image
        if data.get('image_base64'):
            try:
                # Decode base64
                img_data = base64.b64decode(data['image_base64'])
                print(f"✅ Base64 decoding successful")
                print(f"   Raw image size: {len(img_data):,} bytes")
                
                # Convert to numpy array
                nparr = np.frombuffer(img_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if img is not None:
                    height, width, channels = img.shape
                    print(f"✅ Image decoded successfully")
                    print(f"   Dimensions: {width}x{height}")
                    print(f"   Channels: {channels}")
                    
                    # Save test image
                    test_output = "data/test_decoded_image.jpg"
                    cv2.imwrite(test_output, img)
                    print(f"✅ Test image saved: {test_output}")
                else:
                    print(f"❌ Failed to decode image from base64")
                    all_valid = False
                    
            except Exception as e:
                print(f"❌ Image validation error: {e}")
                all_valid = False
        else:
            print(f"⚠️  No image data included (image_base64 is None)")
        
        print()
        print("=" * 70)
        print("📈 FILE STATISTICS")
        print("=" * 70)
        
        file_size = os.path.getsize(JSON_PATH)
        print(f"Total JSON file size: {file_size:,} bytes")
        
        if data.get('image_base64'):
            base64_size = len(data['image_base64'])
            print(f"Base64 image size: {base64_size:,} characters")
            print(f"Overhead: {file_size - base64_size:,} bytes (metadata)")
        
        print()
        print("=" * 70)
        
        if all_valid:
            print("✅ ALL VALIDATIONS PASSED!")
            print("   The JSON export is working correctly.")
        else:
            print("⚠️  SOME VALIDATIONS FAILED")
            print("   Please review the errors above.")
        
        print("=" * 70)
        
        return all_valid
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def display_sample_data():
    """Display a sample of the JSON data"""
    print("\n" + "=" * 70)
    print("📄 SAMPLE JSON DATA")
    print("=" * 70)
    
    try:
        with open(JSON_PATH, 'r') as f:
            data = json.load(f)
        
        # Create a copy without the image for display
        display_data = data.copy()
        if display_data.get('image_base64'):
            img_preview = display_data['image_base64'][:100] + "..."
            display_data['image_base64'] = f"<{len(data['image_base64'])} chars> {img_preview}"
        
        print(json.dumps(display_data, indent=2))
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error displaying data: {e}")

if __name__ == "__main__":
    # Ensure we're in the CommandPanel directory
    if not os.path.exists("data"):
        os.makedirs("data")
    
    success = verify_json_structure()
    
    if success:
        display_sample_data()
        
        print("\n" + "=" * 70)
        print("🎯 NEXT STEPS")
        print("=" * 70)
        print("1. Run app.py and trigger detections")
        print("2. Run test_json_viewer.py to monitor live detections")
        print("3. Check data/test_decoded_image.jpg to verify image quality")
        print("=" * 70)
