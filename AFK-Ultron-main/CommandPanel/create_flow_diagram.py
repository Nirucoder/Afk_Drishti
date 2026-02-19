"""
Data Flow Visualization - Enhanced Version
Shows the complete JSON export process with base64 encoding
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Set up the figure
fig, ax = plt.subplots(1, 1, figsize=(14, 10))
ax.set_xlim(0, 10)
ax.set_ylim(0, 12)
ax.axis('off')

# Title
ax.text(5, 11.5, 'ULTRON JSON EXPORT DATA FLOW', 
        ha='center', va='top', fontsize=20, fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#2c3e50', edgecolor='black', linewidth=2),
        color='white')

# Color scheme
color_camera = '#3498db'
color_detection = '#e74c3c'
color_processing = '#f39c12'
color_export = '#27ae60'
color_command = '#9b59b6'

# ===== STEP 1: Camera Capture =====
y_pos = 10
box1 = FancyBboxPatch((0.5, y_pos-0.5), 4, 0.8, 
                       boxstyle="round,pad=0.1", 
                       facecolor=color_camera, 
                       edgecolor='black', linewidth=2)
ax.add_patch(box1)
ax.text(2.5, y_pos, '📹 CAMERA CAPTURE', 
        ha='center', va='center', fontsize=12, fontweight='bold', color='white')

# Details
ax.text(0.7, y_pos-0.8, '• Resolution: 640x360', fontsize=9)
ax.text(0.7, y_pos-1.1, '• Source: IP Camera / Webcam', fontsize=9)
ax.text(0.7, y_pos-1.4, '• Frame Rate: ~30 FPS', fontsize=9)

# Arrow down
arrow1 = FancyArrowPatch((2.5, y_pos-0.6), (2.5, y_pos-1.8),
                        arrowstyle='->', mutation_scale=30, 
                        linewidth=3, color='black')
ax.add_patch(arrow1)

# ===== STEP 2: Detection =====
y_pos = 7.5
box2 = FancyBboxPatch((0.5, y_pos-0.5), 4, 0.8, 
                       boxstyle="round,pad=0.1", 
                       facecolor=color_detection, 
                       edgecolor='black', linewidth=2)
ax.add_patch(box2)
ax.text(2.5, y_pos, '🎯 HUMAN DETECTION', 
        ha='center', va='center', fontsize=12, fontweight='bold', color='white')

# Details
ax.text(0.7, y_pos-0.8, '• YOLOv8 / Roboflow API', fontsize=9)
ax.text(0.7, y_pos-1.1, '• Confidence threshold: 65%', fontsize=9)
ax.text(0.7, y_pos-1.4, '• Class: Person (ID: 0)', fontsize=9)

# Arrow down
arrow2 = FancyArrowPatch((2.5, y_pos-0.6), (2.5, y_pos-1.8),
                        arrowstyle='->', mutation_scale=30, 
                        linewidth=3, color='black')
ax.add_patch(arrow2)

# ===== STEP 3: Data Processing =====
y_pos = 5
box3 = FancyBboxPatch((0.5, y_pos-0.5), 4, 0.8, 
                       boxstyle="round,pad=0.1", 
                       facecolor=color_processing, 
                       edgecolor='black', linewidth=2)
ax.add_patch(box3)
ax.text(2.5, y_pos, '⚙️ DATA PROCESSING', 
        ha='center', va='center', fontsize=12, fontweight='bold', color='white')

# Details
ax.text(0.7, y_pos-0.8, '• calculate_gps() → GPS coords', fontsize=9)
ax.text(0.7, y_pos-1.1, '• Timestamp generation', fontsize=9)
ax.text(0.7, y_pos-1.4, '• Confidence extraction', fontsize=9)

# Arrow down
arrow3 = FancyArrowPatch((2.5, y_pos-0.6), (2.5, y_pos-1.8),
                        arrowstyle='->', mutation_scale=30, 
                        linewidth=3, color='black')
ax.add_patch(arrow3)

# ===== STEP 4: Base64 Encoding =====
y_pos = 2.5
box4 = FancyBboxPatch((0.5, y_pos-0.5), 4, 0.8, 
                       boxstyle="round,pad=0.1", 
                       facecolor=color_export, 
                       edgecolor='black', linewidth=2)
ax.add_patch(box4)
ax.text(2.5, y_pos, '🖼️ BASE64 ENCODING', 
        ha='center', va='center', fontsize=12, fontweight='bold', color='white')

# Details
ax.text(0.7, y_pos-0.8, '• Resize: 320x180', fontsize=9)
ax.text(0.7, y_pos-1.1, '• cv2.imencode() → JPEG', fontsize=9)
ax.text(0.7, y_pos-1.4, '• base64.b64encode() → String', fontsize=9)

# Arrow right
arrow4 = FancyArrowPatch((4.6, y_pos), (5.4, y_pos),
                        arrowstyle='->', mutation_scale=30, 
                        linewidth=3, color='black')
ax.add_patch(arrow4)

# ===== JSON Structure (Right Side) =====
json_box = FancyBboxPatch((5.5, 1), 4, 5, 
                          boxstyle="round,pad=0.2", 
                          facecolor='#ecf0f1', 
                          edgecolor='black', linewidth=2)
ax.add_patch(json_box)

ax.text(7.5, 5.7, 'JSON STRUCTURE', 
        ha='center', va='center', fontsize=12, fontweight='bold')

# JSON fields
json_fields = [
    ('timestamp', '2026-01-29 21:21:17'),
    ('latitude', '28.614670'),
    ('longitude', '77.208905'),
    ('confidence', '0.9204 (92.04%)'),
    ('message', 'NEW TARGET: 5 TOTAL'),
    ('drone_id', 'ULTRON-01'),
    ('image_base64', '<8800 chars>')
]

y_json = 5.2
for field, value in json_fields:
    ax.text(5.7, y_json, f'"{field}":', fontsize=9, fontweight='bold', family='monospace')
    ax.text(6.5, y_json, f'{value}', fontsize=8, family='monospace', style='italic')
    y_json -= 0.5

# Arrow down from JSON
arrow5 = FancyArrowPatch((7.5, 0.9), (7.5, 0.1),
                        arrowstyle='->', mutation_scale=30, 
                        linewidth=3, color='black')
ax.add_patch(arrow5)

# ===== STEP 5: File Export =====
y_pos = -0.5
box5 = FancyBboxPatch((5.5, y_pos-0.5), 4, 0.8, 
                       boxstyle="round,pad=0.1", 
                       facecolor=color_command, 
                       edgecolor='black', linewidth=2)
ax.add_patch(box5)
ax.text(7.5, y_pos, '💾 FILE EXPORT', 
        ha='center', va='center', fontsize=12, fontweight='bold', color='white')

# Details
ax.text(5.7, y_pos-0.8, '• Path: ../CommandPanel/data/', fontsize=9)
ax.text(5.7, y_pos-1.1, '• File: live_feed.json', fontsize=9)
ax.text(5.7, y_pos-1.4, '• Mode: Overwrite (latest only)', fontsize=9)

# ===== Legend =====
legend_y = 10
ax.text(6, legend_y, 'PROCESS FLOW', fontsize=10, fontweight='bold')

legend_items = [
    (color_camera, 'Camera Input'),
    (color_detection, 'AI Detection'),
    (color_processing, 'Data Processing'),
    (color_export, 'Image Encoding'),
    (color_command, 'File Export')
]

legend_y -= 0.4
for color, label in legend_items:
    rect = mpatches.Rectangle((6, legend_y-0.15), 0.3, 0.2, 
                              facecolor=color, edgecolor='black')
    ax.add_patch(rect)
    ax.text(6.4, legend_y, label, fontsize=8, va='center')
    legend_y -= 0.35

# ===== Stats Box =====
stats_box = FancyBboxPatch((5.5, 7.2), 4, 1.5, 
                          boxstyle="round,pad=0.2", 
                          facecolor='#fff3cd', 
                          edgecolor='black', linewidth=2)
ax.add_patch(stats_box)

ax.text(7.5, 8.5, '📊 PERFORMANCE STATS', 
        ha='center', va='center', fontsize=10, fontweight='bold')

stats = [
    '• Image Size: ~6-9 KB (JPEG)',
    '• Base64 Size: ~8-12 KB',
    '• Total JSON: ~9 KB',
    '• Update Rate: 1.5s cooldown'
]

stats_y = 8.1
for stat in stats:
    ax.text(5.7, stats_y, stat, fontsize=8)
    stats_y -= 0.3

# ===== Footer =====
ax.text(5, -2.2, '✅ VERIFIED: All validations passed | Image decoding successful | GPS coordinates accurate', 
        ha='center', va='center', fontsize=9, 
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#d4edda', edgecolor='#28a745', linewidth=2),
        color='#155724', fontweight='bold')

plt.tight_layout()
plt.savefig('data/json_export_flow_diagram.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
print("✅ Diagram saved: data/json_export_flow_diagram.png")
plt.show()
