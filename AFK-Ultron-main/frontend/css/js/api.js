// ============================================
// AFK-ULTRON COMMAND PANEL - API CLIENT
// ============================================

/**
 * API Configuration
 */
const CONFIG = {
    API_BASE_URL: 'http://localhost:5000',
    SOCKET_URL: 'http://localhost:5000',
    UPDATE_INTERVAL: 30000 // 30 seconds
};

/**
 * API Client for AFK-Ultron Command Panel
 */
class UltronAPI {
    constructor(baseURL = CONFIG.API_BASE_URL) {
        this.baseURL = baseURL;
        this.socket = null;
    }

    /**
     * Initialize WebSocket connection
     */
    initWebSocket(socketURL = CONFIG.SOCKET_URL) {
        if (typeof io === 'undefined') {
            console.error('Socket.IO library not loaded!');
            return null;
        }

        this.socket = io(socketURL);

        this.socket.on('connect', () => {
            console.log('✅ Connected to AFK-Ultron Command Panel');
        });

        this.socket.on('disconnect', () => {
            console.log('❌ Disconnected from Command Panel');
        });

        return this.socket;
    }

    /**
     * Get live detections (last hour)
     * @returns {Promise<Array>} Array of detection objects
     */
    async getLiveDetections() {
        try {
            const response = await fetch(`${this.baseURL}/api/detections/live`);
            const data = await response.json();

            if (data.success) {
                return data.detections;
            } else {
                throw new Error(data.error || 'Failed to fetch detections');
            }
        } catch (error) {
            console.error('Error fetching live detections:', error);
            return [];
        }
    }

    /**
     * Get all detections
     * @returns {Promise<Array>} Array of all detection objects
     */
    async getAllDetections() {
        try {
            const response = await fetch(`${this.baseURL}/api/detections/all`);
            const data = await response.json();

            if (data.success) {
                return data.detections;
            } else {
                throw new Error(data.error || 'Failed to fetch all detections');
            }
        } catch (error) {
            console.error('Error fetching all detections:', error);
            return [];
        }
    }

    /**
     * Get statistics
     * @param {string} period - 'today', 'week', 'month', or 'all'
     * @returns {Promise<Object>} Statistics object
     */
    async getStatistics(period = 'today') {
        try {
            const response = await fetch(`${this.baseURL}/api/statistics?period=${period}`);
            const data = await response.json();

            if (data.success) {
                return data.statistics;
            } else {
                throw new Error(data.error || 'Failed to fetch statistics');
            }
        } catch (error) {
            console.error('Error fetching statistics:', error);
            return null;
        }
    }

    /**
     * Get safe zones
     * @returns {Promise<Array>} Array of safe zone objects
     */
    async getSafeZones() {
        try {
            const response = await fetch(`${this.baseURL}/api/safe-zones`);
            const data = await response.json();

            if (data.success) {
                return data.zones;
            } else {
                throw new Error(data.error || 'Failed to fetch safe zones');
            }
        } catch (error) {
            console.error('Error fetching safe zones:', error);
            return [];
        }
    }

    /**
     * Add a safe zone
     * @param {string} name - Zone name
     * @param {number} centerLat - Center latitude
     * @param {number} centerLon - Center longitude
     * @param {number} radius - Radius in meters
     * @returns {Promise<Object>} Created zone object
     */
    async addSafeZone(name, centerLat, centerLon, radius) {
        try {
            const response = await fetch(`${this.baseURL}/api/safe-zones`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name,
                    center_lat: centerLat,
                    center_lon: centerLon,
                    radius
                })
            });

            const data = await response.json();

            if (data.success) {
                return data;
            } else {
                throw new Error(data.error || 'Failed to add safe zone');
            }
        } catch (error) {
            console.error('Error adding safe zone:', error);
            return null;
        }
    }

    /**
     * Get heatmap data
     * @param {string} period - 'today', 'week', 'month', or 'all'
     * @returns {Promise<Array>} Array of [lat, lon, intensity]
     */
    async getHeatmapData(period = 'all') {
        try {
            const response = await fetch(`${this.baseURL}/api/heatmap?period=${period}`);
            const data = await response.json();

            if (data.success) {
                return data.data;
            } else {
                throw new Error(data.error || 'Failed to fetch heatmap data');
            }
        } catch (error) {
            console.error('Error fetching heatmap data:', error);
            return [];
        }
    }

    /**
     * Export detections to CSV
     * @param {string} period - 'today', 'week', 'month', or 'all'
     * @returns {Promise<string>} Filepath to CSV
     */
    async exportCSV(period = 'all') {
        try {
            const response = await fetch(`${this.baseURL}/api/export/csv?period=${period}`);
            const data = await response.json();

            if (data.success) {
                return data.filepath;
            } else {
                throw new Error(data.error || 'Failed to export CSV');
            }
        } catch (error) {
            console.error('Error exporting CSV:', error);
            return null;
        }
    }

    /**
     * Export detections to PDF
     * @param {string} period - 'today', 'week', 'month', or 'all'
     * @returns {Promise<string>} Filepath to PDF
     */
    async exportPDF(period = 'all') {
        try {
            const response = await fetch(`${this.baseURL}/api/export/pdf?period=${period}`);
            const data = await response.json();

            if (data.success) {
                return data.filepath;
            } else {
                throw new Error(data.error || 'Failed to export PDF');
            }
        } catch (error) {
            console.error('Error exporting PDF:', error);
            return null;
        }
    }

    /**
     * Listen for new detections (WebSocket)
     * @param {Function} callback - Function to call when new detection arrives
     */
    onNewDetection(callback) {
        if (!this.socket) {
            console.error('WebSocket not initialized! Call initWebSocket() first.');
            return;
        }

        this.socket.on('new_detection', (data) => {
            callback(data);
        });
    }

    /**
     * Request manual update (WebSocket)
     */
    requestUpdate() {
        if (!this.socket) {
            console.error('WebSocket not initialized! Call initWebSocket() first.');
            return;
        }

        this.socket.emit('request_update');
    }

    /**
     * Listen for detection updates (WebSocket)
     * @param {Function} callback - Function to call when update arrives
     */
    onDetectionsUpdate(callback) {
        if (!this.socket) {
            console.error('WebSocket not initialized! Call initWebSocket() first.');
            return;
        }

        this.socket.on('detections_update', (data) => {
            callback(data);
        });
    }

    /**
     * Convert base64 image to data URL
     * @param {string} base64 - Base64 encoded image
     * @returns {string} Data URL
     */
    static imageToDataURL(base64) {
        return `data:image/jpeg;base64,${base64}`;
    }

    /**
     * Get alert level class based on confidence
     * @param {number} confidence - Confidence score (0-1)
     * @returns {string} CSS class name
     */
    static getAlertLevel(confidence) {
        if (confidence >= 0.85) return 'HIGH';
        if (confidence >= 0.70) return 'MEDIUM';
        return 'LOW';
    }

    /**
     * Format timestamp
     * @param {string} timestamp - Timestamp string
     * @returns {string} Formatted time
     */
    static formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleString();
    }

    /**
     * Format GPS coordinates
     * @param {number} lat - Latitude
     * @param {number} lon - Longitude
     * @returns {string} Formatted coordinates
     */
    static formatGPS(lat, lon) {
        return `${lat.toFixed(6)}, ${lon.toFixed(6)}`;
    }
}

// ============================================
// USAGE EXAMPLES
// ============================================

/*
// Initialize API
const api = new UltronAPI();

// Initialize WebSocket
const socket = api.initWebSocket();

// Get live detections
const detections = await api.getLiveDetections();
console.log('Live detections:', detections);

// Get statistics
const stats = await api.getStatistics('today');
console.log('Statistics:', stats);

// Listen for new detections
api.onNewDetection((data) => {
    console.log('New detection:', data);
    
    // Display on map
    const { detection, duration, detection_id } = data;
    addMarkerToMap(detection.latitude, detection.longitude);
    
    // Show image
    const imgURL = UltronAPI.imageToDataURL(detection.image_base64);
    document.getElementById('detection-image').src = imgURL;
    
    // Show alert
    const alertLevel = UltronAPI.getAlertLevel(detection.confidence);
    showAlert(detection.message, alertLevel);
});

// Export CSV
const csvPath = await api.exportCSV('week');
console.log('CSV exported to:', csvPath);

// Add safe zone
await api.addSafeZone('Main Entrance', 28.6139, 77.2090, 50);
*/

// Export API class
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UltronAPI;
} else {
    window.UltronAPI = UltronAPI;
}
