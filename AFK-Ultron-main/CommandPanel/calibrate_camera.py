"""
Camera Calibration Helper
=========================

This script helps you calibrate your camera parameters for accurate GPS positioning.
Run this to get recommended values for your setup.
"""

import math

print("=" * 70)
print("🎯 CAMERA CALIBRATION HELPER")
print("=" * 70)
print()

# Step 1: Camera Location
print("STEP 1: CAMERA LOCATION")
print("-" * 70)
print("Find your GPS coordinates:")
print("  1. Open Google Maps (maps.google.com)")
print("  2. Right-click on your location")
print("  3. Click the coordinates at the top")
print("  4. Copy the numbers")
print()
lat = input("Enter your latitude (e.g., 28.6139): ").strip()
lon = input("Enter your longitude (e.g., 77.2090): ").strip()
print(f"✅ Camera location set to: {lat}, {lon}")
print()

# Step 2: Camera Height
print("STEP 2: CAMERA HEIGHT")
print("-" * 70)
print("Measure the height of your camera above the ground.")
print()
print("Common setups:")
print("  - Laptop on desk: 1.0 - 1.5 meters")
print("  - Desktop webcam: 1.5 - 2.0 meters")
print("  - Wall-mounted: 2.0 - 3.0 meters")
print("  - Ceiling camera: 2.5 - 4.0 meters")
print()
height = input("Enter camera height in meters (e.g., 2.5): ").strip()
print(f"✅ Camera height set to: {height} meters")
print()

# Step 3: Camera Tilt
print("STEP 3: CAMERA TILT ANGLE")
print("-" * 70)
print("Estimate how much your camera is tilted downward.")
print()
print("Reference:")
print("  0° = Horizontal (looking straight ahead)")
print("  15° = Slight tilt (typical laptop webcam)")
print("  30° = Medium tilt")
print("  45° = Steep tilt")
print("  90° = Straight down (bird's eye view)")
print()
print("Tip: Most laptop webcams are tilted about 10-20° down")
print()
tilt = input("Enter tilt angle in degrees (e.g., 15): ").strip()
print(f"✅ Camera tilt set to: {tilt}°")
print()

# Step 4: Camera Bearing
print("STEP 4: CAMERA BEARING (Direction)")
print("-" * 70)
print("Which direction is your camera facing?")
print()
print("Options:")
print("  0° = North")
print("  90° = East")
print("  180° = South")
print("  270° = West")
print()
print("Tip: Use a compass app on your phone")
print("     Point phone same direction as camera and read the bearing")
print()
bearing = input("Enter bearing in degrees (e.g., 0 for North): ").strip()
print(f"✅ Camera bearing set to: {bearing}°")
print()

# Step 5: Field of View
print("STEP 5: FIELD OF VIEW")
print("-" * 70)
print("Most webcams have a 60° horizontal FOV.")
print("If you don't know, use the default values.")
print()
h_fov = input("Enter horizontal FOV in degrees (default: 60): ").strip() or "60"
v_fov = input("Enter vertical FOV in degrees (default: 45): ").strip() or "45"
print(f"✅ FOV set to: {h_fov}° horizontal, {v_fov}° vertical")
print()

# Generate configuration
print()
print("=" * 70)
print("📋 YOUR CONFIGURATION")
print("=" * 70)
print()
print("Copy these lines into your app.py (around line 31):")
print()
print("-" * 70)
print(f"CAMERA_LAT = {lat}")
print(f"CAMERA_LON = {lon}")
print(f"CAMERA_HEIGHT = {height}")
print(f"CAMERA_TILT_ANGLE = {tilt}")
print(f"CAMERA_BEARING = {bearing}")
print(f"CAMERA_HORIZONTAL_FOV = {h_fov}")
print(f"CAMERA_VERTICAL_FOV = {v_fov}")
print("-" * 70)
print()

# Calculate detection range
try:
    h = float(height)
    t = float(tilt)
    v_fov_val = float(v_fov)
    
    # Calculate max distance (bottom of frame)
    bottom_angle = t + (v_fov_val / 2)
    if bottom_angle < 90:
        max_distance = h / math.tan(math.radians(90 - bottom_angle))
        
        print("📏 ESTIMATED DETECTION RANGE")
        print("-" * 70)
        print(f"With your settings, the camera can see the ground up to:")
        print(f"  Maximum distance: {max_distance:.1f} meters")
        print(f"  Coverage area: ~{max_distance * 2:.1f}m wide × {max_distance:.1f}m deep")
        print()
except:
    pass

print("✅ Configuration complete!")
print()
print("Next steps:")
print("  1. Update app.py with these values")
print("  2. Run the app and test")
print("  3. Walk to a known location and verify GPS accuracy")
print("  4. Adjust parameters if needed")
print()
print("=" * 70)
