"""
Database Module - Relational SQLite Database for Search & Rescue Command Center
"""

import sqlite3
import json
from datetime import datetime, timedelta
import os
import math

class DetectionDatabase:
    def __init__(self, db_path='data/detections.db'):
        """Initialize database connection and create relational tables"""
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        # Enforce Foreign Keys
        self.conn.execute("PRAGMA foreign_keys = 1")
        self.create_tables()
        self._ensure_default_operation()
        
    def create_tables(self):
        """Create structured relational tables for S&R workflow"""
        cursor = self.conn.cursor()
        
        # Table 1: Search & Rescue Operations (Missions)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                status TEXT DEFAULT 'ACTIVE',
                start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                end_time DATETIME
            )
        ''')
        
        # Table 2: Active Drones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS drones (
                id TEXT PRIMARY KEY,
                model TEXT,
                battery_level REAL DEFAULT 100.0,
                status TEXT DEFAULT 'DEPLOYED',
                last_ping DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table 3: Detected Targets (Victims)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_id INTEGER,
                rescue_status TEXT DEFAULT 'PENDING',
                first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_lat REAL NOT NULL,
                last_lon REAL NOT NULL,
                FOREIGN KEY (operation_id) REFERENCES operations(id)
            )
        ''')
        
        # Table 4: Raw Detections (Linked to Targets and Drones)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_id INTEGER,
                target_id INTEGER,
                drone_id TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                confidence REAL NOT NULL,
                message TEXT,
                in_safe_zone BOOLEAN DEFAULT 0,
                image_base64 TEXT,
                FOREIGN KEY (operation_id) REFERENCES operations(id),
                FOREIGN KEY (target_id) REFERENCES targets(id),
                FOREIGN KEY (drone_id) REFERENCES drones(id)
            )
        ''')
        
        # Table 5: Safe Zones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS safe_zones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_id INTEGER,
                name TEXT NOT NULL,
                center_lat REAL NOT NULL,
                center_lon REAL NOT NULL,
                radius REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (operation_id) REFERENCES operations(id)
            )
        ''')
        
        self.conn.commit()
        print("[SUCCESS] Relational Database Architecture Deployed")

    def _ensure_default_operation(self):
        """Creates a default active operation if none exist."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM operations WHERE status='ACTIVE' LIMIT 1")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO operations (name) VALUES ('HACKATHON DEFAULT OP')")
            self.conn.commit()

    def _get_active_operation_id(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM operations WHERE status='ACTIVE' ORDER BY start_time DESC LIMIT 1")
        row = cursor.fetchone()
        return row['id'] if row else 1

    def _calculate_distance_meters(self, lat1, lon1, lat2, lon2):
        """Haversine formula approximation"""
        lat_diff = abs(lat1 - lat2) * 111000
        lon_diff = abs(lon1 - lon2) * 111000 * math.cos(math.radians(lat1))
        return math.sqrt(lat_diff**2 + lon_diff**2)
        
    def _ensure_drone_exists(self, drone_id):
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO drones (id, model) VALUES (?, ?)", (drone_id, 'AFK-ULTRON-X1'))
        cursor.execute("UPDATE drones SET last_ping = CURRENT_TIMESTAMP WHERE id = ?", (drone_id,))
        self.conn.commit()

    def _map_detection_to_target(self, op_id, lat, lon):
        """Intelligently groups nearby detections into distinct physical 'Targets/Victims'"""
        cursor = self.conn.cursor()
        # Look for pending/in_progress targets within 30 meters
        cursor.execute('''
            SELECT id, last_lat, last_lon FROM targets 
            WHERE operation_id = ? AND rescue_status != 'RESCUED'
        ''', (op_id,))
        
        closest_target_id = None
        min_dist = float('inf')
        
        for row in cursor.fetchall():
            dist = self._calculate_distance_meters(lat, lon, row['last_lat'], row['last_lon'])
            if dist < 30 and dist < min_dist:
                min_dist = dist
                closest_target_id = row['id']
                
        if closest_target_id:
            # Update target last seen location
            cursor.execute('''
                UPDATE targets SET last_seen = CURRENT_TIMESTAMP, last_lat = ?, last_lon = ? WHERE id = ?
            ''', (lat, lon, closest_target_id))
            return closest_target_id
        else:
            # Create a brand new distinct target
            cursor.execute('''
                INSERT INTO targets (operation_id, last_lat, last_lon) VALUES (?, ?, ?)
            ''', (op_id, lat, lon))
            return cursor.lastrowid

    def add_detection(self, data, duration=0):
        """
        Unified insertion tracking the S&R relational flow.
        Provides backward compatibility with the flat structure dict passed by old codes.
        """
        self.conn.execute("BEGIN TRANSACTION")
        try:
            cursor = self.conn.cursor()
            op_id = self._get_active_operation_id()
            drone_id = data.get('drone_id', 'UNKNOWN-DRONE')
            
            # Ensure Drone exists
            self._ensure_drone_exists(drone_id)
            
            lat = data.get('latitude', 0.0)
            lon = data.get('longitude', 0.0)
            
            # Intelligent Target Mapping
            target_id = self._map_detection_to_target(op_id, lat, lon)
            
            # Check Safe Zones
            in_safe_zone = 0
            cursor.execute("SELECT center_lat, center_lon, radius FROM safe_zones WHERE operation_id = ?", (op_id,))
            for z in cursor.fetchall():
                if self._calculate_distance_meters(lat, lon, z['center_lat'], z['center_lon']) <= z['radius']:
                    in_safe_zone = 1
                    break
            
            # Final Detection Log
            cursor.execute('''
                INSERT INTO detections 
                (operation_id, target_id, drone_id, timestamp, latitude, longitude, confidence, message, in_safe_zone, image_base64)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                op_id,
                target_id,
                drone_id,
                data.get('timestamp', datetime.now().isoformat()),
                lat,
                lon,
                data.get('confidence', 0.0),
                data.get('message', ''),
                in_safe_zone,
                data.get('image_base64')
            ))
            
            self.conn.commit()
            print(f"[SUCCESS] Detection logged for Target {target_id} by {drone_id}")
            return cursor.lastrowid
        except Exception as e:
            self.conn.rollback()
            print(f"[ERROR] Database Error: {e}")
            return None

    def get_active_targets(self):
        """Returns physical locations of unrescued targets to deploy ground teams"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM targets WHERE rescue_status != 'RESCUED' ORDER BY last_seen DESC")
        return [dict(row) for row in cursor.fetchall()]

    def mark_target_rescued(self, target_id):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE targets SET rescue_status = 'RESCUED' WHERE id = ?", (target_id,))
        self.conn.commit()

    def get_statistics(self, period='all'):
        """Retains UI compatibility but processes better analytics"""
        cursor = self.conn.cursor()
        op_id = self._get_active_operation_id()
        
        cursor.execute("SELECT COUNT(*) as count FROM targets WHERE operation_id = ?", (op_id,))
        distinct_targets = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM targets WHERE operation_id = ? AND rescue_status = 'RESCUED'", (op_id,))
        rescued = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM detections WHERE operation_id = ?", (op_id,))
        total_pings = cursor.fetchone()['count']
        
        return {
            'total_detections': distinct_targets,  # We return distinctly found humans now instead of messy logs
            'high_alerts': distinct_targets - rescued, # Pending rescues
            'average_confidence': float(rescued), # Overriding for API formatting compatibility
            'peak_hour': 'ACTIVE',
            'peak_hour_count': total_pings, # Total historical pings
            'alert_breakdown': {'PENDING': distinct_targets - rescued, 'RESCUED': rescued},
            'period': period
        }
    
    # Keeping old wrappers for backward compatibility with older server routes
    def get_detections_last_hours(self, hours=1):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM detections ORDER BY timestamp DESC LIMIT 50")
        return [dict(row) for row in cursor.fetchall()]
        
    def get_all_detections(self):
        return self.get_detections_last_hours()

    def add_safe_zone(self, name, center_lat, center_lon, radius):
        cursor = self.conn.cursor()
        op_id = self._get_active_operation_id()
        cursor.execute("INSERT INTO safe_zones (operation_id, name, center_lat, center_lon, radius) VALUES (?, ?, ?, ?, ?)",
                       (op_id, name, center_lat, center_lon, radius))
        self.conn.commit()
        return cursor.lastrowid

    def get_safe_zones(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM safe_zones")
        return [dict(row) for row in cursor.fetchall()]

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    print("Testing S&R Database Schema Build...")
    db = DetectionDatabase("test_relational.db")
    db.add_detection({"drone_id": "UAV-1", "latitude": 28.6139, "longitude": 77.2090, "confidence": 0.88})
    db.add_detection({"drone_id": "UAV-1", "latitude": 28.61391, "longitude": 77.20901, "confidence": 0.90}) # Should group into target 1
    db.add_detection({"drone_id": "UAV-2", "latitude": 40.7128, "longitude": -74.0060, "confidence": 0.95}) # Target 2
    
    targets = db.get_active_targets()
    print(f"Distinct Targets tracked: {len(targets)} (Expected: 2)")
    print(db.get_statistics())
    
    # Cleanup test db
    db.close()
    if os.path.exists("test_relational.db"):
        os.remove("test_relational.db")
