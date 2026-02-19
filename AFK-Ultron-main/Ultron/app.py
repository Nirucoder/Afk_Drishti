import cv2
import requests
import base64
import json
import numpy as np
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from PIL import Image, ImageTk, ImageOps, ImageDraw
from ultralytics import YOLO
import math
import datetime
import time
import threading
import winsound # For audio alerts (Windows)
from roboflow import Roboflow
import os

# ==========================================
#        USER CONFIGURATION SECTION
# ==========================================

# 1. CAMERA SETUP
CAMERA_SOURCE = 0 

# 2. ROBOFLOW SETUP (Cloud Inference)
ROBOFLOW_API_KEY = "9VFU7VpjQpvG7HkytpgA"
ROBOFLOW_WORKSPACE = "nirattayroboflow"
ROBOFLOW_WORKFLOW_ID = "find-people"
ROBOFLOW_VERSION = 1 

# 3. CAMERA & GPS CONFIGURATION (Accurate Geospatial Positioning)
# Set your camera's actual GPS location
CAMERA_LAT = 28.6139  # Replace with your actual latitude
CAMERA_LON = 77.2090  # Replace with your actual longitude

# Camera Physical Parameters
CAMERA_HEIGHT = 2.5  # Height above ground in meters (adjust based on your setup)
CAMERA_TILT_ANGLE = 15  # Downward tilt in degrees (0=horizontal, 90=straight down)
CAMERA_BEARING = 0  # Direction camera faces (0=North, 90=East, 180=South, 270=West)
CAMERA_HORIZONTAL_FOV = 60  # Horizontal field of view in degrees (typical webcam: 60-78°)
CAMERA_VERTICAL_FOV = 45  # Vertical field of view in degrees

# Frame dimensions (must match your actual frame size)
FRAME_WIDTH = 640
FRAME_HEIGHT = 360 

# 4. DETECTION TUNING
CONFIDENCE_THRESHOLD = 0.65 
IOU_THRESHOLD = 0.45

# 5. COMMAND PANEL INTEGRATION
ENABLE_COMMAND_PANEL = True  # Set to False to disable JSON export
JSON_OUTPUT_PATH = "../CommandPanel/data/live_feed.json"       

class DroneApp:
    def __init__(self, root, model_name='yolov8n.pt'):
        self.root = root
        self.root.title("Ultron Drone Command Center")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1e1e1e")

        # --- Configuration ---
        self.camera_source = CAMERA_SOURCE
        self.model_name = model_name
        self.target_class_id = 0 # 'person'
        self.confidence_threshold = CONFIDENCE_THRESHOLD
        self.iou_threshold = IOU_THRESHOLD
        
        # State
        self.is_running = False
        self.cap = None
        self.model = None
        
        # --- Roboflow Inference SDK Config (Cloud) ---
        self.use_workflow = False # Disabled to prevent 401 Errors (Using Local YOLOv8)
        self.rf_api_key = ROBOFLOW_API_KEY
        self.rf_workspace = ROBOFLOW_WORKSPACE
        self.rf_workflow_id = ROBOFLOW_WORKFLOW_ID
        
        # Initialize Inference SDK Client (Skipped due to dependency issues)
        self.rf_client = None


        # State Variables
        self.frame_count = 0
        self.last_results = [] 
        self.is_inferencing = False 
        self.last_alert_time = 0
        self.alert_cooldown = 1.5 
        self.last_human_count = 0 
        self.last_local_boxes = [] 
        self.is_local_inferencing = False 
        self.count_smoothing = []
        
        # Command Panel Integration
        self.enable_command_panel = ENABLE_COMMAND_PANEL
        self.json_output_path = JSON_OUTPUT_PATH
        self.detection_history = []
        self.current_frame = None  # Store current frame for JSON export 

        # --- UI Setup ---
        self.setup_styles()
        self.create_start_screen()
        self.create_dashboard()
        
        # Start on Start Screen
        self.show_start_screen()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Helvetica', 14, 'bold'), borderwidth=0, background="#00C851", foreground="white")
        style.map('TButton', background=[('active', '#007E33')])
        style.configure('TLabel', background='#1e1e1e', foreground='white', font=('Helvetica', 12))
        style.configure('Header.TLabel', font=('Helvetica', 24, 'bold'), background='#1e1e1e', foreground='#00C851')
        style.configure('Drishti.TEntry', fieldbackground='#001a00', foreground='#00ff00', font=('Consolas', 14), borderwidth=0)

    def create_start_screen(self):
        self.start_frame = tk.Frame(self.root, bg="#000000")
        
        # Load Background
        try:
            bg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "background.jpg")
            print(f"Loading background from: {bg_path}")
            self.bg_image = Image.open(bg_path)
            self.bg_image = self.bg_image.resize((1400, 900), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
            print("Background loaded successfully")
        except Exception as e:
            print(f"Error loading background: {e}")
            self.bg_photo = None

        self.canvas = tk.Canvas(self.start_frame, width=1400, height=900, highlightthickness=0, bg="black")
        self.canvas.pack(fill="both", expand=True)

        if self.bg_photo:
            self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
        
        # Fallback title if image fails or just as overlay
        # self.canvas.create_text(700, 100, text="DRISHTI SYSTEM", font=('Helvetica', 40, 'bold'), fill="orange")

        # Input Field (Positioned for the slot)
        # Slot appears to be around Y=265 based on reference
        self.url_entry = ttk.Entry(self.start_frame, width=40, font=('Consolas', 16), style='Drishti.TEntry')
        self.url_entry.insert(0, str(CAMERA_SOURCE))
        
        # Input Field (Positioned for the slot)
        # Slot appears to be around Y=265 based on reference
        self.url_entry = ttk.Entry(self.start_frame, width=40, font=('Consolas', 16), style='Drishti.TEntry')
        self.url_entry.insert(0, str(CAMERA_SOURCE))
        
        # Place Entry
        self.canvas.create_window(700, 265, window=self.url_entry, height=40)
        
        # Add Label for Camera Source (Since new background is clean)
        self.canvas.create_text(700, 235, text="CAMERA SOURCE (IP URL or ID):", font=('Helvetica', 14), fill="#a6a6a6")

        # Button Area - Draw a Visible "Box" as requested (Since background is clean/dark)
        # Moving UP to fit inside the "Big Box" of the background
        self.btn_area = (550, 415, 850, 485) 
        # Draw a semi-transparent or outlined box to act as "The White Box" / Button
        self.canvas.create_rectangle(self.btn_area, outline="white", width=2, fill="") 
        
        # Add TEXT for the button inside the box
        self.canvas.create_text(700, 450, text="CONNECT & VIEW", font=('Helvetica', 20, 'bold'), fill="white")
        
        self.canvas.bind('<Button-1>', self.on_start_screen_click)
        self.canvas.bind('<Motion>', self.on_mouse_move)
        
        # Status Label
        self.status_label = tk.Label(self.start_frame, text="READY TO CONNECT", font=('Consolas', 12, 'bold'), bg="black", fg="#00ff00")
        self.canvas.create_window(700, 550, window=self.status_label)

    def on_start_screen_click(self, event):
        x, y = event.x, event.y
        x1, y1, x2, y2 = self.btn_area
        if x1 < x < x2 and y1 < y < y2:
            self.start_detection()

    def on_mouse_move(self, event):
        x, y = event.x, event.y
        x1, y1, x2, y2 = self.btn_area
        if x1 < x < x2 and y1 < y < y2:
            self.canvas.config(cursor="hand2")
            # Optional: highlight effect
            # self.canvas.itemconfigure(self.btn_rect, width=4)
        else:
            self.canvas.config(cursor="")

    def create_dashboard(self):
        self.dashboard_frame = tk.Frame(self.root, bg="#2b2b2b")
        self.dashboard_frame.rowconfigure(0, weight=1) 
        self.dashboard_frame.rowconfigure(1, weight=0) 
        self.dashboard_frame.columnconfigure(0, weight=1)

        self.video_panel = tk.Label(self.dashboard_frame, bg="black")
        self.video_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.bottom_panel = tk.Frame(self.dashboard_frame, bg="#333333", height=300)
        self.bottom_panel.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.bottom_panel.grid_propagate(False) 
        self.bottom_panel.columnconfigure(0, weight=1)
        self.bottom_panel.columnconfigure(1, weight=0)
        self.bottom_panel.rowconfigure(0, weight=1)

        log_frame = tk.Frame(self.bottom_panel, bg="#333333", padx=10, pady=10)
        log_frame.grid(row=0, column=0, sticky="nsew")
        header_frame = tk.Frame(log_frame, bg="#333333")
        header_frame.pack(fill='x')
        ttk.Label(header_frame, text="⚠️ DETECTION LOG", font=('Helvetica', 14, 'bold'), background="#333333", foreground="#ffbb33").pack(side='left')
        self.count_label = tk.Label(header_frame, text="HUMANS: 0", font=('Helvetica', 20, 'bold'), bg="#333333", fg="#00C851")
        self.count_label.pack(side='right', padx=10)
        
        self.alert_status_label = tk.Label(log_frame, text="SYSTEM SECURE", font=('Helvetica', 16, 'bold'), bg="#333333", fg="#00C851")
        self.alert_status_label.pack(fill='x', pady=5)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, bg="#1e1e1e", fg="#00C851", font=('Consolas', 14))
        self.log_text.pack(fill='both', expand=True, pady=(5,0))

        radar_frame = tk.Frame(self.bottom_panel, bg="#333333", padx=20, pady=10)
        radar_frame.grid(row=0, column=1, sticky="ns")
        ttk.Label(radar_frame, text="📍 TACTICAL MAP", font=('Helvetica', 14, 'bold'), background="#333333", foreground="#33b5e5").pack()
        self.radar_size = 220
        self.radar_canvas = tk.Canvas(radar_frame, width=self.radar_size, height=self.radar_size, bg="#001a00", highlightthickness=2, highlightbackground="#004d00")
        self.radar_canvas.pack(pady=5)
        self.draw_radar_grid()

        self.gps_label = tk.Label(radar_frame, text="LOC: 28.6139, 77.2090", bg="#333333", fg="#ff4444", font=('Consolas', 10, 'bold'))
        self.gps_label.pack()
        tk.Button(radar_frame, text="STOP SYSTEM", bg="#ff4444", fg="white", font=('Helvetica', 10, 'bold'), command=self.stop_detection).pack(pady=(5,0), fill='x')

    def draw_radar_grid(self):
        c = self.radar_size // 2
        for r in [30, 60, 90]: self.radar_canvas.create_oval(c-r, c-r, c+r, c+r, outline="#003300")
        self.radar_canvas.create_line(c, 0, c, self.radar_size, fill="#003300")
        self.radar_canvas.create_line(0, c, self.radar_size, c, fill="#003300")
        self.radar_canvas.create_oval(c-4, c-4, c+4, c+4, fill="#00C851")

    def show_start_screen(self):
        self.dashboard_frame.pack_forget()
        self.start_frame.pack(fill='both', expand=True)

    def show_dashboard(self):
        self.start_frame.pack_forget()
        self.dashboard_frame.pack(fill='both', expand=True)
    
    def send_to_command_panel(self, detection_data):
        """
        Send detection data to Command Panel via JSON file export.
        
        Args:
            detection_data (dict): Dictionary containing:
                - timestamp: Detection time
                - latitude: GPS latitude
                - longitude: GPS longitude
                - confidence: Detection confidence (0.0-1.0)
                - message: Alert message
                - drone_id: Identifier for this drone
                - image_base64: Optional base64-encoded image
        """
        if not self.enable_command_panel:
            return
        
        try:
            # Ensure the directory exists
            output_dir = os.path.dirname(self.json_output_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Write JSON to file (this will be monitored by command panel)
            with open(self.json_output_path, 'w') as f:
                json.dump(detection_data, f, indent=2)
            
            # Also maintain a history (optional, for debugging)
            self.detection_history.append(detection_data)
            
            # Keep only last 100 detections in memory
            if len(self.detection_history) > 100:
                self.detection_history.pop(0)
                
        except Exception as e:
            print(f"❌ Command Panel Export Error: {e}")
            # Don't crash the app if command panel export fails
    
    def send_detection_to_panel(self, message, lat, lon, confidence, frame):
        """
        Send detection data to Command Panel WITHOUT triggering alerts.
        Used for continuous tracking updates.
        
        Args:
            message: Status message
            lat: Latitude
            lon: Longitude
            confidence: Detection confidence (0.0-1.0)
            frame: Current video frame
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Prepare detection data
        detection_data = {
            "timestamp": timestamp,
            "latitude": lat if lat is not None else CAMERA_LAT,
            "longitude": lon if lon is not None else CAMERA_LON,
            "confidence": float(confidence),
            "message": message,
            "drone_id": "ULTRON-01",
            "image_base64": None
        }
        
        # Encode current frame as base64 if available
        if frame is not None:
            try:
                # Resize frame for smaller file size
                small_frame = cv2.resize(frame, (320, 180))
                _, buffer = cv2.imencode('.jpg', small_frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                detection_data["image_base64"] = base64.b64encode(buffer).decode('utf-8')
            except Exception as e:
                print(f"⚠️ Image encoding error: {e}")
        
        # Send to command panel (no alert sound, no GUI log)
        if self.enable_command_panel:
            self.send_to_command_panel(detection_data)
            # Optional: Print to console (comment out if too verbose)
            # print(f"📡 Tracking update: {message} @ ({lat:.5f}, {lon:.5f})")

    def trigger_alert(self, message, lat=None, lon=None, confidence=0.0, frame=None):
        """
        Trigger an alert and optionally send to command panel.
        
        Args:
            message: Alert message
            lat: Latitude (optional, defaults to HOME_LAT)
            lon: Longitude (optional, defaults to HOME_LON)
            confidence: Detection confidence (0.0-1.0)
            frame: Current video frame (for image export)
        """
        if time.time() - self.last_alert_time > self.alert_cooldown:
            self.last_alert_time = time.time()
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Display in local GUI
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.log_text.see(tk.END)
            threading.Thread(target=self.play_beep, daemon=True).start()
            self.animate_alert()
            
            # Prepare detection data for command panel
            detection_data = {
                "timestamp": timestamp,
                "latitude": lat if lat is not None else CAMERA_LAT,
                "longitude": lon if lon is not None else CAMERA_LON,
                "confidence": float(confidence),
                "message": message,
                "drone_id": "ULTRON-01",
                "image_base64": None
            }
            
            # Encode current frame as base64 if available
            if frame is not None:
                try:
                    # Resize frame for smaller file size
                    small_frame = cv2.resize(frame, (320, 180))
                    _, buffer = cv2.imencode('.jpg', small_frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                    detection_data["image_base64"] = base64.b64encode(buffer).decode('utf-8')
                except Exception as e:
                    print(f"⚠️ Image encoding error: {e}")
            
            # Send to command panel
            if self.enable_command_panel:
                self.send_to_command_panel(detection_data)
                print(f"✅ Detection sent to Command Panel: {message} @ ({detection_data['latitude']:.5f}, {detection_data['longitude']:.5f})")

    def play_beep(self):
        try: winsound.Beep(2500, 150)
        except: pass

    def animate_alert(self, silent=False):
        for i in range(6):
            color = "#ff4444" if i % 2 == 0 else "#ffbb33"
            text = "⚠️ HUMAN DETECTED ⚠️" if i % 2 == 0 else "⚠️ ALERT ⚠️"
            self.root.after(i * 500, lambda c=color, t=text: self.alert_status_label.config(fg=c, text=t))
        self.root.after(3000, lambda: self.alert_status_label.config(fg="#00C851", text="SYSTEM SECURE"))

    def start_detection(self):
        url_input = self.url_entry.get().strip()
        
        # Smart URL Heuristics
        if url_input.isdigit():
            self.camera_source = int(url_input)
        else:
            # Handle IP Camera formatting (common with apps like IP Webcam)
            if not url_input.startswith("http"):
                url_input = "http://" + url_input
            
            # If user just types IP:PORT (e.g. 192.168.1.5:8080), append typical endpoints
            if ":" in url_input and url_input.count("/") < 3: 
                # Try adding /video if missing path
                url_input += "/video"
            
            self.camera_source = url_input

        print(f"Connecting to: {self.camera_source}")
        self.status_label.config(text=f"Connecting to {self.camera_source}...", foreground="cyan")
        self.root.update()
        threading.Thread(target=self.connect_camera_thread, daemon=True).start()

    def connect_camera_thread(self):
        if not self.model:
            try: self.model = YOLO('yolov8n.pt'); print("YOLOv8 Loaded.")
            except: pass
        cap = cv2.VideoCapture(self.camera_source)
        self.root.after(0, self.on_camera_connected, cap)
        self.cap = cap
        self.is_running = True
        self.show_dashboard()
        self.update_frame()

    def on_camera_connected(self, cap):
        if not cap.isOpened():
            self.status_label.config(text="Connection Failed (Check IP/Network)", foreground="red")
            messagebox.showerror("Connection Error", f"Could not connect to:\n{self.camera_source}\n\nTips:\n1. Ensure phone and PC are on same Wi-Fi.\n2. Try disabling PC Firewall.\n3. Check if URL ends in /video or /shot.jpg")

    def stop_detection(self):
        self.is_running = False
        if self.cap: self.cap.release()
        self.show_start_screen()

    def run_workflow_thread(self, frame):
        """Runs Roboflow Workflow via HTTP Requests (Fallback)."""
        try:
            self.is_inferencing = True
            
            # 1. Resize Image for Speed & Reliability (Prevent 502s)
            height, width = frame.shape[:2]
            scale = 640 / width
            new_height = int(height * scale)
            resized_frame = cv2.resize(frame, (640, new_height))
            
            # 2. Encode Image
            _, img_encoded = cv2.imencode('.jpg', resized_frame)
            jpg_as_text = base64.b64encode(img_encoded).decode('utf-8')
            
            # 3. Construct Payload
            payload = {
                "inputs": {
                    "image": {
                        "type": "base64",
                        "value": jpg_as_text
                    }
                }
            }
            
            # 4. Request
            url = f"https://api.roboflow.com/{self.rf_workspace}/{self.rf_workflow_id}?api_key={self.rf_api_key}"
            # Note: Workflows usually use a different endpoint format or require "deploy" via the python package. 
            # However, for a specific workflow ID, we can hit the Universe/Infer endpoint or the Remote Infer endpoint.
            # Let's use the standard Universe inference endpoint structure which often redirects to workflows if configured:
            # But "find-people" looks like a workflow ID.
            
            # Let's try the direct workflow execution URL if known, primarily: 
            # https://detect.roboflow.com/infer/workflows/{workspace}/{workflow_id}
            
            url = f"https://detect.roboflow.com/infer/workflows/{self.rf_workspace}/{self.rf_workflow_id}"
            
            # If that fails, we fallback to the generic project inference
            response = requests.post(url, json=payload, headers={"Authorization": f"Bearer {self.rf_api_key}"})
            
            if response.status_code == 200:
                result = response.json()
                detections = []
                
                # Standard Workflow Output parsing
                if 'outputs' in result:
                    for out in result['outputs']:
                        target = out.get('value', out)
                        if isinstance(target, dict) and 'predictions' in target:
                            # Scale back up
                            preds = target['predictions']
                            for p in preds:
                                p['x'] /= scale
                                p['y'] /= scale
                                p['width'] /= scale
                                p['height'] /= scale
                            detections.extend(preds)
                        elif isinstance(target, list):
                            # Assume list of predictions
                            for p in target:
                                if isinstance(p, dict):
                                    p['x'] /= scale
                                    p['y'] /= scale
                                    p['width'] /= scale
                                    p['height'] /= scale
                            detections.extend(target)
                            
                self.last_results = detections
            else:
                print(f"Workflow Error {response.status_code}: {response.text}")

        except Exception as e:
            print(f"Workflow Request Error: {e}")
        finally:
            self.is_inferencing = False


    def send_to_command_panel(self, detection_data):
        """
        Send detection data to Command Panel (Local JSON or Cloud HTTP).
        """
        # ---------------------------------------------------------
        # ☁️ CLOUD DEPLOYMENT CONFIGURATION
        # Paste your Render Backend URL here to send data to the cloud!
        # Example: "https://my-app.onrender.com/api/detections/live"
        # ---------------------------------------------------------
        CLOUD_BACKEND_URL = None 
        
        try:
            if CLOUD_BACKEND_URL:
                # Send to Cloud
                import requests
                # Add /api/detections/live if missing (common mistake)
                if not CLOUD_BACKEND_URL.endswith('/api/detections/live'):
                   # Handle potential / at end of base url
                   base = CLOUD_BACKEND_URL.rstrip('/')
                   CLOUD_BACKEND_URL = f"{base}/api/detections/live"

                requests.post(CLOUD_BACKEND_URL, json=detection_data)
                # print(f"☁️ Sent to Cloud: {data['message']}") # Uncomment to debug
            else:
                # Local Mode (JSON File)
                os.makedirs(os.path.dirname(self.json_output_path), exist_ok=True)
                with open(self.json_output_path, 'w') as f:
                    json.dump(detection_data, f, indent=4)
                
        except Exception as e:
            print(f"❌ Error sending data to Command Panel: {e}")

    def send_detection_to_panel(self, message, lat, lon, confidence, frame):
        """
        Helper to construct data and send to command panel (for continuous updates).
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        detection_data = {
            "timestamp": timestamp,
            "latitude": lat,
            "longitude": lon,
            "confidence": float(confidence),
            "message": message,
            "drone_id": "ULTRON-01",
            "image_base64": None
        }

        # Encode frame if available
        if frame is not None:
            try:
                small_frame = cv2.resize(frame, (320, 180))
                _, buffer = cv2.imencode('.jpg', small_frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                detection_data["image_base64"] = base64.b64encode(buffer).decode('utf-8')
            except Exception as e:
                print(f"⚠️ Image encoding error: {e}")

        # Send to panel
        if self.enable_command_panel:
            self.send_to_command_panel(detection_data)


    def calculate_gps(self, x, y):
        """
        Calculate accurate GPS coordinates from pixel position using camera geometry.
        
        This uses trigonometry to project the pixel position onto the ground plane,
        then converts the distance and bearing to GPS coordinates.
        
        Args:
            x: Pixel x-coordinate (0 to FRAME_WIDTH)
            y: Pixel y-coordinate (0 to FRAME_HEIGHT)
            
        Returns:
            (latitude, longitude) tuple
        """
        # Convert pixel coordinates to normalized coordinates (-1 to 1)
        # Center of frame is (0, 0)
        norm_x = (x - FRAME_WIDTH / 2) / (FRAME_WIDTH / 2)
        norm_y = (y - FRAME_HEIGHT / 2) / (FRAME_HEIGHT / 2)
        
        # Calculate angles from camera center
        # Horizontal angle (left-right)
        horizontal_angle = norm_x * (CAMERA_HORIZONTAL_FOV / 2)
        
        # Vertical angle (up-down), accounting for camera tilt
        vertical_angle_from_center = norm_y * (CAMERA_VERTICAL_FOV / 2)
        total_vertical_angle = CAMERA_TILT_ANGLE + vertical_angle_from_center
        
        # Calculate ground distance using trigonometry
        # For a tilted camera looking at the ground:
        # distance = height / tan(angle_from_horizontal)
        angle_from_horizontal = 90 - total_vertical_angle
        
        # Prevent division by zero and handle edge cases
        if angle_from_horizontal <= 0 or angle_from_horizontal >= 90:
            # Point is above horizon or straight down
            ground_distance = CAMERA_HEIGHT * 10  # Fallback to reasonable distance
        else:
            ground_distance = CAMERA_HEIGHT / math.tan(math.radians(angle_from_horizontal))
        
        # Adjust for horizontal angle to get actual distance in that direction
        distance_in_direction = ground_distance / math.cos(math.radians(horizontal_angle))
        
        # Calculate bearing (direction from camera)
        # Combine camera bearing with horizontal angle
        target_bearing = (CAMERA_BEARING + horizontal_angle) % 360
        
        # Convert distance and bearing to GPS offset
        # Earth's radius in meters
        EARTH_RADIUS = 6371000
        
        # Convert bearing to radians
        bearing_rad = math.radians(target_bearing)
        
        # Calculate latitude offset
        # Moving north increases latitude
        lat_offset = (distance_in_direction * math.cos(bearing_rad)) / EARTH_RADIUS
        lat_offset_degrees = math.degrees(lat_offset)
        
        # Calculate longitude offset
        # Moving east increases longitude, but this depends on latitude
        # At the equator, 1 degree longitude = 111km
        # At other latitudes: distance = 111km * cos(latitude)
        lon_offset = (distance_in_direction * math.sin(bearing_rad)) / (EARTH_RADIUS * math.cos(math.radians(CAMERA_LAT)))
        lon_offset_degrees = math.degrees(lon_offset)
        
        # Calculate final GPS coordinates
        target_lat = CAMERA_LAT + lat_offset_degrees
        target_lon = CAMERA_LON + lon_offset_degrees
        
        return target_lat, target_lon

    def update_radar_blip(self, x1, y1, x2, y2):
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        radar_x = 110 + ((cx - 320) * 0.3)
        radar_y = 110 + ((cy - 180) * 0.4)
        self.radar_canvas.create_oval(radar_x-4, radar_y-4, radar_x+4, radar_y+4, fill="#ff4444", outline="white", tags="blip")

    def draw_cloud_results(self, frame):
        for det in self.last_results:
            x, y, w, h = det.get('x', 0), det.get('y', 0), det.get('width', 0), det.get('height', 0)
            if det.get('confidence', 0) >= self.confidence_threshold:
                x1, y1, x2, y2 = int(x-w/2), int(y-h/2), int(x+w/2), int(y+h/2)
                lat, lon = self.calculate_gps(x, y)
                confidence = det.get('confidence', 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 128, 255), 2)
                cv2.putText(frame, f"CLOUD: {lat:.6f}, {lon:.6f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)
                self.update_radar_blip(x1, y1, x2, y2)
                self.gps_label.config(text=f"LOC: {lat:.4f}, {lon:.4f}")
                self.trigger_alert(f"{det.get('class', 'Person')} DETECTED", lat=lat, lon=lon, confidence=confidence, frame=frame)

    def update_frame(self):
        if not self.is_running: return
        ret, frame = self.cap.read()
        if not ret:
            self.handle_no_signal()
            self.root.after(100, self.update_frame)
            return

        frame = cv2.resize(frame, (640, 360))
        self.radar_canvas.delete("blip")
        
        valid_cloud = False
        count = 0
        
        if self.use_workflow:
            if not self.is_inferencing:
                threading.Thread(target=self.run_workflow_thread, args=(frame.copy(),), daemon=True).start()
            if self.last_results:
                cloud_dets = [d for d in self.last_results if d.get('confidence', 0) >= self.confidence_threshold]
                if cloud_dets:
                    valid_cloud = True
                    count = len(cloud_dets)
                    self.draw_cloud_results(frame)

        if not valid_cloud:
            if not self.is_local_inferencing and self.frame_count % 3 == 0:
                threading.Thread(target=self.run_local_inference_thread, args=(frame.copy(),), daemon=True).start()
            
            count = len(self.last_local_boxes)
            for det in self.last_local_boxes:
                x1, y1, x2, y2 = det['coords']
                lat, lon = self.calculate_gps((x1+x2)/2, (y1+y2)/2)
                color = (0, 255, 0)
                cv2.line(frame, (x1, y1), (x1+20, y1), color, 2)
                cv2.line(frame, (x1, y1), (x1, y1+20), color, 2)
                cv2.line(frame, (x2, y1), (x2-20, y1), color, 2)
                cv2.line(frame, (x2, y1), (x2, y1+20), color, 2)
                cv2.line(frame, (x1, y2), (x1+20, y2), color, 2)
                cv2.line(frame, (x1, y2), (x1, y2-20), color, 2)
                cv2.line(frame, (x2, y2), (x2-20, y2), color, 2)
                cv2.line(frame, (x2, y2), (x2, y2-20), color, 2)
                
                overlay = frame.copy()
                cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
                cv2.addWeighted(overlay, 0.15, frame, 0.85, 0, frame)
                cv2.putText(frame, f"THREAT LOC: {lat:.5f}, {lon:.5f}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
                self.update_radar_blip(x1, y1, x2, y2)
                self.gps_label.config(text=f"LOC: {lat:.4f}, {lon:.4f}")

        # Store annotated frame for JSON export (AFTER detection boxes are drawn)
        self.current_frame = frame.copy()

        # Smoothing
        self.count_smoothing.append(count)
        if len(self.count_smoothing) > 5: self.count_smoothing.pop(0)
        stable_count = max(self.count_smoothing) if self.count_smoothing else 0
        self.count_label.config(text=f"HUMANS: {stable_count}")
        
        # DYNAMIC JSON EXPORT: Update JSON continuously when detections are present
        if stable_count > 0 and self.last_local_boxes:
            # Get GPS from first detection
            det = self.last_local_boxes[0]
            x1, y1, x2, y2 = det['coords']
            lat, lon = self.calculate_gps((x1+x2)/2, (y1+y2)/2)
            confidence = det.get('conf', 0.0)
            
            # Determine message type
            if stable_count > self.last_human_count:
                message = f"NEW TARGET: {stable_count} TOTAL"
                # Play alert sound only for NEW detections
                self.trigger_alert(message, lat=lat, lon=lon, confidence=confidence, frame=self.current_frame)
            else:
                # Continuous update (no alert sound, just JSON update)
                message = f"TRACKING: {stable_count} HUMAN{'S' if stable_count > 1 else ''}"
                self.send_detection_to_panel(message, lat, lon, confidence, self.current_frame)
        
        self.last_human_count = stable_count
        self.frame_count += 1
        
        self.show_frame_in_gui(frame)
        self.root.after(15, self.update_frame)

    def run_local_inference_thread(self, frame):
        try:
            self.is_local_inferencing = True
            res = self.model.predict(frame, verbose=False, conf=self.confidence_threshold, classes=[0])
            if res:
                self.last_local_boxes = [{'coords': list(map(int, b.xyxy[0])), 'conf': float(b.conf[0])} for b in res[0].boxes]
        except: pass
        finally: self.is_local_inferencing = False

    def show_frame_in_gui(self, frame):
        try:
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            w, h = self.video_panel.winfo_width(), self.video_panel.winfo_height()
            if w > 10 and h > 10:
                img.thumbnail((w, h), Image.Resampling.LANCZOS)
                tk_img = ImageTk.PhotoImage(image=img)
                self.video_panel.imgtk = tk_img
                self.video_panel.configure(image=tk_img)
        except: pass

    def handle_no_signal(self):
        img = Image.new('RGB', (640, 360), color='black')
        draw = ImageDraw.Draw(img)
        draw.text((280, 170), "NO SIGNAL", fill="white")
        tk_img = ImageTk.PhotoImage(image=img)
        self.video_panel.imgtk = tk_img
        self.video_panel.configure(image=tk_img)

if __name__ == "__main__":
    root = tk.Tk()
    app = DroneApp(root)
    root.mainloop()
