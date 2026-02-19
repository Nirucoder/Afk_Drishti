
import sys

try:
    import cv2
    print("cv2: OK")
except ImportError as e:
    print(f"cv2: FAILED ({e})")

try:
    import torch
    print("torch: OK")
except ImportError as e:
    print(f"torch: FAILED ({e})")

try:
    from ultralytics import YOLO
    print("ultralytics: OK")
except ImportError as e:
    print(f"ultralytics: FAILED ({e})")

try:
    import roboflow
    print("roboflow: OK")
except ImportError as e:
    print(f"roboflow: FAILED ({e})")
