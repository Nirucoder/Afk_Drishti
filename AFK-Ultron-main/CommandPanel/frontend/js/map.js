// ============================================
// AFK-ULTRON COMMAND PANEL - MAP MODULE
// ============================================

class TacticalMap {
    constructor(containerId, centerCoords = [28.6139, 77.2090], zoom = 14) {
        this.map = null;
        this.markers = [];
        this.geofence = null;
        this.centerCoords = centerCoords;
        this.zoom = zoom;
        this.containerId = containerId;
        this.markerTimeout = 300000; // 5 minutes in milliseconds
    }

    /**
     * Initialize the map
     */
    init() {
        // Create map
        this.map = L.map(this.containerId).setView(this.centerCoords, this.zoom);

        // Add dark tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(this.map);

        // Add geofence circle (5km radius)
        this.geofence = L.circle(this.centerCoords, {
            radius: 5000,
            color: '#ff4444',
            fillColor: '#ff4444',
            fillOpacity: 0.1,
            weight: 2,
            dashArray: '10, 5'
        }).addTo(this.map);

        // Add center marker
        L.circleMarker(this.centerCoords, {
            radius: 6,
            fillColor: '#00ff88',
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 1
        }).addTo(this.map).bindPopup('<b>Command Center</b><br>ULTRON-01 Base');

        console.log('🗺️ Tactical map initialized');
    }

    /**
     * Add detection marker to map
     * @param {Object} detection - Detection data
     */
    addMarker(detection) {
        const { latitude, longitude, confidence, message, timestamp, image_base64, alert_level } = detection;

        // Determine marker color based on alert level
        let color;
        if (alert_level === 'HIGH' || confidence >= 0.85) {
            color = '#ff4444';
        } else if (alert_level === 'MEDIUM' || confidence >= 0.70) {
            color = '#ffbb33';
        } else {
            color = '#00ff88';
        }

        // Create circle marker
        const marker = L.circleMarker([latitude, longitude], {
            radius: 8,
            fillColor: color,
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        }).addTo(this.map);

        // Create popup content
        const popupContent = `
            <div style="min-width: 200px;">
                ${image_base64 ? `<img src="data:image/jpeg;base64,${image_base64}" style="width: 100%; height: 120px; object-fit: cover; border-radius: 4px; margin-bottom: 8px;" />` : ''}
                <div style="font-weight: 700; margin-bottom: 4px; color: ${color};">${message}</div>
                <div style="font-size: 0.75rem; color: #666; margin-bottom: 2px;">
                    <strong>Confidence:</strong> ${(confidence * 100).toFixed(1)}%
                </div>
                <div style="font-size: 0.75rem; color: #666; margin-bottom: 2px;">
                    <strong>GPS:</strong> ${latitude.toFixed(6)}, ${longitude.toFixed(6)}
                </div>
                <div style="font-size: 0.75rem; color: #666;">
                    <strong>Time:</strong> ${timestamp}
                </div>
            </div>
        `;

        marker.bindPopup(popupContent);

        // Add pulsing animation for high alerts
        if (alert_level === 'HIGH' || confidence >= 0.85) {
            marker.getElement()?.classList.add('pulse-marker');
        }

        // Store marker with timestamp
        const markerData = {
            marker: marker,
            timestamp: Date.now(),
            detection: detection
        };

        this.markers.push(markerData);

        // Auto-remove after 5 minutes
        setTimeout(() => {
            this.removeMarker(markerData);
        }, this.markerTimeout);

        // Pan to marker if it's a high alert
        if (alert_level === 'HIGH' || confidence >= 0.85) {
            this.map.panTo([latitude, longitude]);
        }

        console.log(`📍 Marker added: ${latitude.toFixed(6)}, ${longitude.toFixed(6)}`);
    }

    /**
     * Remove a specific marker
     * @param {Object} markerData - Marker data object
     */
    removeMarker(markerData) {
        const index = this.markers.indexOf(markerData);
        if (index > -1) {
            this.map.removeLayer(markerData.marker);
            this.markers.splice(index, 1);
            console.log('🗑️ Marker removed (timeout)');
        }
    }

    /**
     * Clear all markers
     */
    clearAllMarkers() {
        this.markers.forEach(markerData => {
            this.map.removeLayer(markerData.marker);
        });
        this.markers = [];
        console.log('🗑️ All markers cleared');
    }

    /**
     * Center map on base coordinates
     */
    centerMap() {
        this.map.setView(this.centerCoords, this.zoom);
    }

    /**
     * Get marker count
     */
    getMarkerCount() {
        return this.markers.length;
    }

    /**
     * Update geofence radius
     * @param {number} radius - Radius in meters
     */
    updateGeofence(radius) {
        if (this.geofence) {
            this.map.removeLayer(this.geofence);
        }

        this.geofence = L.circle(this.centerCoords, {
            radius: radius,
            color: '#ff4444',
            fillColor: '#ff4444',
            fillOpacity: 0.1,
            weight: 2,
            dashArray: '10, 5'
        }).addTo(this.map);
    }

    /**
     * Add heatmap layer (if needed in future)
     * @param {Array} heatmapData - Array of [lat, lon, intensity]
     */
    addHeatmap(heatmapData) {
        // Placeholder for heatmap functionality
        // Would require leaflet-heat plugin
        console.log('Heatmap data received:', heatmapData.length, 'points');
    }
}

// Add CSS for pulsing markers
const style = document.createElement('style');
style.textContent = `
    .pulse-marker {
        animation: pulse-ring 2s infinite;
    }
    
    @keyframes pulse-ring {
        0% {
            box-shadow: 0 0 0 0 rgba(255, 68, 68, 0.7);
        }
        70% {
            box-shadow: 0 0 0 10px rgba(255, 68, 68, 0);
        }
        100% {
            box-shadow: 0 0 0 0 rgba(255, 68, 68, 0);
        }
    }
`;
document.head.appendChild(style);
