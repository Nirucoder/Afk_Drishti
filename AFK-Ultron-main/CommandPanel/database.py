"""
Database Module - SQLite Database for Detection Storage
Handles all database operations for the Command Panel
"""

import sqlite3
import json
from datetime import datetime, timedelta
import os

class DetectionDatabase:
    def __init__(self, db_path='data/detections.db'):
        """Initialize database connection and create tables if needed"""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        self.create_tables()
        
    def create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Table 1: Detections
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                confidence REAL NOT NULL,
                message TEXT,
                drone_id TEXT,
                alert_level TEXT,
                duration REAL DEFAULT 0,
                in_safe_zone BOOLEAN DEFAULT 0,
                image_base64 TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table 2: Safe Zones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS safe_zones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                center_lat REAL NOT NULL,
                center_lon REAL NOT NULL,
                radius REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table 3: Detection History (for tracking duration)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detection_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location_key TEXT UNIQUE,
                first_seen DATETIME,
                last_seen DATETIME,
                count INTEGER DEFAULT 1,
                latitude REAL,
                longitude REAL
            )
        ''')
        
        self.conn.commit()
        print("✅ Database tables created/verified")
        
    def calculate_alert_level(self, confidence):
        """
        Calculate alert level based on confidence score
        
        Args:
            confidence (float): Detection confidence (0.0 to 1.0)
            
        Returns:
            str: "HIGH", "MEDIUM", or "LOW"
        """
        if confidence >= 0.85:
            return "HIGH"      # Very certain it's a person
        elif confidence >= 0.70:
            return "MEDIUM"    # Fairly certain
        else:
            return "LOW"       # Uncertain
            
    def is_in_safe_zone(self, lat, lon):
        """
        Check if coordinates are within any safe zone
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            
        Returns:
            bool: True if in safe zone, False otherwise
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM safe_zones')
        zones = cursor.fetchall()
        
        for zone in zones:
            # Calculate distance using Haversine formula (simplified)
            # For small distances, we can use Pythagorean approximation
            lat_diff = abs(lat - zone['center_lat'])
            lon_diff = abs(lon - zone['center_lon'])
            
            # Convert to meters (approximate)
            lat_meters = lat_diff * 111000  # 1 degree ≈ 111km
            lon_meters = lon_diff * 111000 * 0.9  # Adjust for latitude
            
            distance = (lat_meters**2 + lon_meters**2)**0.5
            
            if distance <= zone['radius']:
                return True
                
        return False
        
    def add_detection(self, data, duration=0):
        """
        Add a new detection to the database
        
        Args:
            data (dict): Detection data from JSON
            duration (float): How long person was visible (seconds)
            
        Returns:
            int: ID of inserted detection
        """
        cursor = self.conn.cursor()
        
        # Calculate alert level
        alert_level = self.calculate_alert_level(data.get('confidence', 0))
        
        # Check if in safe zone
        in_safe_zone = self.is_in_safe_zone(
            data.get('latitude', 0),
            data.get('longitude', 0)
        )
        
        # Insert detection
        cursor.execute('''
            INSERT INTO detections 
            (timestamp, latitude, longitude, confidence, message, drone_id, 
             alert_level, duration, in_safe_zone, image_base64)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('timestamp'),
            data.get('latitude'),
            data.get('longitude'),
            data.get('confidence'),
            data.get('message'),
            data.get('drone_id'),
            alert_level,
            duration,
            in_safe_zone,
            data.get('image_base64')
        ))
        
        self.conn.commit()
        detection_id = cursor.lastrowid
        
        print(f"✅ Detection #{detection_id} added: {data.get('message')} "
              f"[{alert_level}] @ ({data.get('latitude'):.5f}, {data.get('longitude'):.5f})")
        
        return detection_id
        
    def get_detections_last_hours(self, hours=1):
        """
        Get detections from the last N hours
        
        Args:
            hours (int): Number of hours to look back
            
        Returns:
            list: List of detection dictionaries
        """
        cursor = self.conn.cursor()
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT * FROM detections 
            WHERE datetime(timestamp) >= datetime(?)
            ORDER BY timestamp DESC
        ''', (cutoff_time.strftime('%Y-%m-%d %H:%M:%S'),))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
        
    def get_all_detections(self):
        """Get all detections from database"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM detections ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
        
    def get_statistics(self, period='all'):
        """
        Calculate detection statistics
        
        Args:
            period (str): 'today', 'week', 'month', or 'all'
            
        Returns:
            dict: Statistics dictionary
        """
        cursor = self.conn.cursor()
        
        # Determine time filter
        if period == 'today':
            cutoff = datetime.now().replace(hour=0, minute=0, second=0)
        elif period == 'week':
            cutoff = datetime.now() - timedelta(days=7)
        elif period == 'month':
            cutoff = datetime.now() - timedelta(days=30)
        else:
            cutoff = datetime(2000, 1, 1)  # All time
            
        cutoff_str = cutoff.strftime('%Y-%m-%d %H:%M:%S')
        
        # Total detections
        cursor.execute('''
            SELECT COUNT(*) as total FROM detections 
            WHERE datetime(timestamp) >= datetime(?)
        ''', (cutoff_str,))
        total = cursor.fetchone()['total']
        
        # High alert count
        cursor.execute('''
            SELECT COUNT(*) as high_alerts FROM detections 
            WHERE datetime(timestamp) >= datetime(?) AND alert_level = 'HIGH'
        ''', (cutoff_str,))
        high_alerts = cursor.fetchone()['high_alerts']
        
        # Average confidence
        cursor.execute('''
            SELECT AVG(confidence) as avg_conf FROM detections 
            WHERE datetime(timestamp) >= datetime(?)
        ''', (cutoff_str,))
        avg_conf = cursor.fetchone()['avg_conf'] or 0
        
        # Peak hour
        cursor.execute('''
            SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
            FROM detections
            WHERE datetime(timestamp) >= datetime(?)
            GROUP BY hour
            ORDER BY count DESC
            LIMIT 1
        ''', (cutoff_str,))
        peak_hour_row = cursor.fetchone()
        peak_hour = f"{peak_hour_row['hour']}:00" if peak_hour_row else "N/A"
        peak_count = peak_hour_row['count'] if peak_hour_row else 0
        
        # Detections by alert level
        cursor.execute('''
            SELECT alert_level, COUNT(*) as count
            FROM detections
            WHERE datetime(timestamp) >= datetime(?)
            GROUP BY alert_level
        ''', (cutoff_str,))
        alert_breakdown = {row['alert_level']: row['count'] for row in cursor.fetchall()}
        
        return {
            'total_detections': total,
            'high_alerts': high_alerts,
            'average_confidence': round(avg_conf, 4),
            'peak_hour': peak_hour,
            'peak_hour_count': peak_count,
            'alert_breakdown': alert_breakdown,
            'period': period
        }
        
    def add_safe_zone(self, name, center_lat, center_lon, radius):
        """
        Add a safe zone to the database
        
        Args:
            name (str): Zone name
            center_lat (float): Center latitude
            center_lon (float): Center longitude
            radius (float): Radius in meters
            
        Returns:
            int: Zone ID
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO safe_zones (name, center_lat, center_lon, radius)
            VALUES (?, ?, ?, ?)
        ''', (name, center_lat, center_lon, radius))
        
        self.conn.commit()
        zone_id = cursor.lastrowid
        print(f"✅ Safe zone '{name}' added (ID: {zone_id})")
        return zone_id
        
    def get_safe_zones(self):
        """Get all safe zones"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM safe_zones')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
        
    def update_detection_tracking(self, lat, lon):
        """
        Update detection tracking for duration calculation
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            
        Returns:
            float: Duration in seconds
        """
        cursor = self.conn.cursor()
        
        # Create unique key for this location (rounded to 5 decimal places)
        location_key = f"{lat:.5f}_{lon:.5f}"
        
        # Check if we've seen this location before
        cursor.execute('''
            SELECT * FROM detection_tracking WHERE location_key = ?
        ''', (location_key,))
        
        row = cursor.fetchone()
        
        now = datetime.now()
        
        if row:
            # Update existing tracking
            first_seen = datetime.fromisoformat(row['first_seen'])
            duration = (now - first_seen).total_seconds()
            
            cursor.execute('''
                UPDATE detection_tracking 
                SET last_seen = ?, count = count + 1
                WHERE location_key = ?
            ''', (now.isoformat(), location_key))
            
        else:
            # New location
            duration = 0
            cursor.execute('''
                INSERT INTO detection_tracking 
                (location_key, first_seen, last_seen, latitude, longitude)
                VALUES (?, ?, ?, ?, ?)
            ''', (location_key, now.isoformat(), now.isoformat(), lat, lon))
            
        self.conn.commit()
        return duration
        
    def cleanup_old_tracking(self, max_age_seconds=30):
        """
        Remove old tracking entries (person has left the area)
        
        Args:
            max_age_seconds (int): Max age in seconds
        """
        cursor = self.conn.cursor()
        cutoff = datetime.now() - timedelta(seconds=max_age_seconds)
        
        cursor.execute('''
            DELETE FROM detection_tracking 
            WHERE datetime(last_seen) < datetime(?)
        ''', (cutoff.isoformat(),))
        
        deleted = cursor.rowcount
        self.conn.commit()
        
        if deleted > 0:
            print(f"🧹 Cleaned up {deleted} old tracking entries")
            
    def close(self):
        """Close database connection"""
        self.conn.close()
        print("✅ Database connection closed")


# Test the database
if __name__ == "__main__":
    print("=" * 70)
    print("🗄️  DATABASE MODULE TEST")
    print("=" * 70)
    
    # Initialize database
    db = DetectionDatabase()
    
    # Add a test safe zone
    db.add_safe_zone("Main Entrance", 28.6139, 77.2090, 50)
    
    # Add a test detection
    test_data = {
        'timestamp': '2026-01-29 23:00:00',
        'latitude': 28.6140,
        'longitude': 77.2091,
        'confidence': 0.92,
        'message': 'TEST DETECTION',
        'drone_id': 'ULTRON-01',
        'image_base64': None
    }
    
    db.add_detection(test_data, duration=5.2)
    
    # Get statistics
    stats = db.get_statistics('all')
    print(f"\n📊 Statistics:")
    print(f"   Total Detections: {stats['total_detections']}")
    print(f"   High Alerts: {stats['high_alerts']}")
    print(f"   Average Confidence: {stats['average_confidence']:.2%}")
    print(f"   Peak Hour: {stats['peak_hour']} ({stats['peak_hour_count']} detections)")
    
    print("\n" + "=" * 70)
    print("✅ Database test complete!")
