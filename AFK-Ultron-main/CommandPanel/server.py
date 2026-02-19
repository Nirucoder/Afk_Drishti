"""
Flask Server - Backend API for Command Panel
Provides REST API endpoints and WebSocket real-time updates
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import json
import os
import time
import threading
from datetime import datetime
from database import DetectionDatabase
from analytics import Analytics

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ultron-command-panel-secret-2026'
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for all routes

# Initialize SocketIO for real-time updates (Allow all origins)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize database and analytics
db = DetectionDatabase()
analytics = Analytics(db)

# File watcher configuration
JSON_FILE_PATH = 'data/live_feed.json'
last_modified_time = 0

# Active detections tracking (for 5-second persistence)
active_detections = {}
PERSISTENCE_THRESHOLD = 0.1  # seconds (Reduced for instant feedback)

# ==========================================
#           API ENDPOINTS (REST)
# ==========================================

@app.route('/')
def index():
    """Serve the main dashboard (frontend)"""
    try:
        return send_from_directory('frontend', 'index.html')
    except:
        # Fallback to API info if frontend not found
        return jsonify({
            'name': 'AFK-Ultron Command Panel API',
            'version': '1.0',
            'status': 'running',
            'message': 'Frontend not found. Please add frontend files to CommandPanel/frontend/',
            'endpoints': {
                'detections_live': '/api/detections/live',
                'detections_all': '/api/detections/all',
                'statistics': '/api/statistics',
                'safe_zones': '/api/safe-zones',
                'export_csv': '/api/export/csv',
                'export_pdf': '/api/export/pdf'
            }
        })

@app.route('/api')
def api_info():
    """API information endpoint"""
    return jsonify({
        'name': 'AFK-Ultron Command Panel API',
        'version': '1.0',
        'status': 'running',
        'endpoints': {
            'detections_live': '/api/detections/live',
            'detections_all': '/api/detections/all',
            'statistics': '/api/statistics',
            'safe_zones': '/api/safe-zones',
            'export_csv': '/api/export/csv',
            'export_pdf': '/api/export/pdf'
        }
    })

@app.route('/frontend/<path:filename>')
def serve_frontend_files(filename):
    """Serve static frontend files (CSS, JS, images, etc.)"""
    return send_from_directory('frontend', filename)

# DEBUG: Test route to verify server is running updated code
@app.route('/test-css-route')
def test_css_route():
    """Test route to verify CSS serving is configured"""
    return jsonify({'status': 'CSS routes are configured!', 'version': '2.0'})

# Serve CSS files
@app.route('/css/<path:filename>')
def serve_css(filename):
    """Serve CSS files"""
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(os.path.join(base_dir, 'frontend', 'css'), filename)

# Serve JavaScript files
@app.route('/js/<path:filename>')
def serve_js(filename):
    """Serve JavaScript files"""
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(os.path.join(base_dir, 'frontend', 'js'), filename)

# Serve CSS/JS subdirectory files
@app.route('/css/js/<path:filename>')
def serve_css_js(filename):
    """Serve JavaScript files from css/js directory"""
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(os.path.join(base_dir, 'frontend', 'css', 'js'), filename)


@app.route('/api/detections/live')
def get_live_detections():
    """
    Get detections from the last hour
    
    Returns:
        JSON: List of recent detections
    """
    try:
        detections = db.get_detections_last_hours(1)
        return jsonify({
            'success': True,
            'count': len(detections),
            'detections': detections
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/detections/all')
def get_all_detections():
    """
    Get all detections from database
    
    Returns:
        JSON: List of all detections
    """
    try:
        detections = db.get_all_detections()
        return jsonify({
            'success': True,
            'count': len(detections),
            'detections': detections
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/statistics')
def get_statistics():
    """
    Get detection statistics
    
    Query params:
        period: 'today', 'week', 'month', or 'all' (default: 'all')
    
    Returns:
        JSON: Statistics dictionary
    """
    try:
        period = request.args.get('period', 'all')
        stats = db.get_statistics(period)
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/safe-zones', methods=['GET', 'POST'])
def safe_zones():
    """
    GET: Get all safe zones
    POST: Add a new safe zone
    
    POST body:
        {
            "name": "Zone name",
            "center_lat": 28.6139,
            "center_lon": 77.2090,
            "radius": 50
        }
    
    Returns:
        JSON: Safe zones list or creation confirmation
    """
    if request.method == 'GET':
        try:
            zones = db.get_safe_zones()
            return jsonify({
                'success': True,
                'count': len(zones),
                'zones': zones
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
            
    elif request.method == 'POST':
        try:
            data = request.json
            zone_id = db.add_safe_zone(
                data['name'],
                data['center_lat'],
                data['center_lon'],
                data['radius']
            )
            return jsonify({
                'success': True,
                'zone_id': zone_id,
                'message': f"Safe zone '{data['name']}' created"
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/export/csv')
def export_csv():
    """
    Export detections to CSV
    
    Query params:
        period: 'today', 'week', 'month', or 'all' (default: 'all')
    
    Returns:
        JSON: File path
    """
    try:
        period = request.args.get('period', 'all')
        filepath = analytics.export_to_csv(period=period)
        return jsonify({
            'success': True,
            'filepath': filepath,
            'message': 'CSV exported successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/export/pdf')
def export_pdf():
    """
    Export detections to PDF report
    
    Query params:
        period: 'today', 'week', 'month', or 'all' (default: 'all')
    
    Returns:
        JSON: File path
    """
    try:
        period = request.args.get('period', 'all')
        filepath = analytics.export_to_pdf(period=period)
        return jsonify({
            'success': True,
            'filepath': filepath,
            'message': 'PDF report generated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/heatmap')
def get_heatmap_data():
    """
    Get heatmap data for visualization
    
    Query params:
        period: 'today', 'week', 'month', or 'all' (default: 'all')
    
    Returns:
        JSON: Heatmap data points
    """
    try:
        period = request.args.get('period', 'all')
        heatmap_data = analytics.generate_heatmap_data(period)
        return jsonify({
            'success': True,
            'data': heatmap_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==========================================
#           WEBSOCKET EVENTS
# ==========================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"🔌 Client connected: {request.sid}")
    emit('connection_response', {
        'status': 'connected',
        'message': 'Connected to AFK-Ultron Command Panel'
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"🔌 Client disconnected: {request.sid}")

@socketio.on('request_update')
def handle_update_request():
    """Handle manual update request from client"""
    try:
        detections = db.get_detections_last_hours(1)
        emit('detections_update', {
            'detections': detections,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        emit('error', {'message': str(e)})

# ==========================================
#      FILE WATCHER & SMART FILTERING
# ==========================================

def process_detection(data):
    """
    Process a new detection with smart filtering
    
    Args:
        data (dict): Detection data from JSON
        
    Returns:
        bool: True if detection should be stored, False if filtered out
    """
    # Create unique key for this detection location
    lat = data.get('latitude', 0)
    lon = data.get('longitude', 0)
    detection_key = f"{lat:.5f}_{lon:.5f}"
    
    current_time = time.time()
    
    # Check if we've seen this location before
    if detection_key in active_detections:
        # Update existing detection
        detection_info = active_detections[detection_key]
        detection_info['count'] += 1
        detection_info['last_seen'] = current_time
        detection_info['data'] = data  # Update with latest data
        
        # Calculate duration
        duration = current_time - detection_info['first_seen']
        
        # Only store if duration >= persistence threshold
        if duration >= PERSISTENCE_THRESHOLD and not detection_info.get('stored', False):
            # Mark as stored
            detection_info['stored'] = True
            
            # Update tracking in database
            db_duration = db.update_detection_tracking(lat, lon)
            
            # Add to database
            detection_id = db.add_detection(data, duration=duration)
            
            print(f"✅ Detection persisted: {detection_key} (duration: {duration:.1f}s)")
            
            # Emit to all connected clients
            socketio.emit('new_detection', {
                'detection': data,
                'duration': duration,
                'detection_id': detection_id
            })
            
            return True
    else:
        # New detection - start tracking
        active_detections[detection_key] = {
            'first_seen': current_time,
            'last_seen': current_time,
            'count': 1,
            'data': data,
            'stored': False
        }
        print(f"🆕 New detection tracked: {detection_key}")
    
    return False

def cleanup_stale_detections():
    """Remove detections that haven't been seen recently"""
    current_time = time.time()
    stale_threshold = 10.0  # seconds
    
    stale_keys = [
        key for key, info in active_detections.items()
        if current_time - info['last_seen'] > stale_threshold
    ]
    
    for key in stale_keys:
        del active_detections[key]
    
    if stale_keys:
        print(f"🧹 Cleaned up {len(stale_keys)} stale detections")
    
    # Also cleanup database tracking
    db.cleanup_old_tracking(max_age_seconds=30)

def watch_json_file():
    """
    Watch the JSON file for changes and process new detections
    This runs in a separate thread
    """
    global last_modified_time
    
    print(f"👁️  Watching file: {JSON_FILE_PATH}")
    
    while True:
        try:
            if os.path.exists(JSON_FILE_PATH):
                current_modified = os.path.getmtime(JSON_FILE_PATH)
                
                if current_modified > last_modified_time:
                    # File has been updated
                    with open(JSON_FILE_PATH, 'r') as f:
                        data = json.load(f)
                    
                    # Process the detection
                    process_detection(data)
                    
                    last_modified_time = current_modified
            
            # Cleanup stale detections every iteration
            cleanup_stale_detections()
            
            # Check every 0.5 seconds
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ File watcher error: {e}")
            time.sleep(1)

# ==========================================
#              STARTUP
# ==========================================

def start_file_watcher():
    """Start the file watcher in a background thread"""
    watcher_thread = threading.Thread(target=watch_json_file, daemon=True)
    watcher_thread.start()
    print("✅ File watcher started")

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 AFK-ULTRON COMMAND PANEL SERVER")
    print("=" * 70)
    print(f"📡 Starting server on http://localhost:5000")
    print(f"🔌 WebSocket enabled for real-time updates")
    print(f"👁️  Monitoring: {JSON_FILE_PATH}")
    print(f"⏱️  Persistence threshold: {PERSISTENCE_THRESHOLD}s")
    print("=" * 70)
    
    # Start file watcher
    start_file_watcher()
    
    # Start Flask server with SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)
