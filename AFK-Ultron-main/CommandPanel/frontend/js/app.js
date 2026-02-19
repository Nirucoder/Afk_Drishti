// ============================================
// AFK-ULTRON COMMAND PANEL - MAIN APP
// ============================================

class CommandPanel {
    constructor() {
        this.api = new UltronAPI();
        this.map = null;
        this.alerts = [];
        this.maxAlerts = 20;
        this.statsUpdateInterval = null;
        this.audioContext = null;

        // DOM Elements
        this.elements = {
            statusIndicator: document.getElementById('statusIndicator'),
            statusText: document.getElementById('statusText'),
            alertsFeed: document.getElementById('alertsFeed'),
            alertCount: document.getElementById('alertCount'),
            totalDetections: document.getElementById('totalDetections'),
            peakHour: document.getElementById('peakHour'),
            avgConfidence: document.getElementById('avgConfidence'),
            highAlerts: document.getElementById('highAlerts'),
            statsPeriod: document.getElementById('statsPeriod'),
            exportCSV: document.getElementById('exportCSV'),
            exportPDF: document.getElementById('exportPDF'),
            setLocationBtn: document.getElementById('setLocationBtn'),
            centerMapBtn: document.getElementById('centerMapBtn'),
            clearMarkersBtn: document.getElementById('clearMarkersBtn'),
            loadingOverlay: document.getElementById('loadingOverlay'),
            toast: document.getElementById('toast'),
            toastIcon: document.getElementById('toastIcon'),
            toastTitle: document.getElementById('toastTitle'),
            toastMessage: document.getElementById('toastMessage'),
            locationModal: document.getElementById('locationModal'),
            latitudeInput: document.getElementById('latitudeInput'),
            longitudeInput: document.getElementById('longitudeInput'),
            applyLocation: document.getElementById('applyLocation'),
            cancelLocation: document.getElementById('cancelLocation'),
            closeModal: document.getElementById('closeModal'),
            currentLocation: document.getElementById('currentLocation'),
            useMyLocationBtn: document.getElementById('useMyLocationBtn')
        };
    }

    /**
     * Initialize the command panel
     */
    async init() {
        console.log('🚀 Initializing AFK-Ultron Command Panel...');

        // Initialize map
        this.map = new TacticalMap('map', [28.6139, 77.2090], 14);
        this.map.init();

        // Initialize WebSocket
        this.initWebSocket();

        // Load initial data
        await this.loadInitialData();

        // Setup event listeners
        this.setupEventListeners();

        // Start statistics auto-update
        this.startStatsUpdate();

        // Initialize audio context (for alert sounds)
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();

        // Hide loading overlay
        setTimeout(() => {
            this.elements.loadingOverlay.classList.add('hidden');
        }, 1000);

        console.log('✅ Command Panel initialized successfully');
    }

    /**
     * Initialize WebSocket connection
     */
    initWebSocket() {
        const socket = this.api.initWebSocket();

        socket.on('connect', () => {
            console.log('✅ WebSocket connected');
            this.updateConnectionStatus(true);
            this.showToast('✅', 'Connected', 'Real-time updates active');
        });

        socket.on('disconnect', () => {
            console.log('❌ WebSocket disconnected');
            this.updateConnectionStatus(false);
            this.showToast('❌', 'Disconnected', 'Attempting to reconnect...');
        });

        socket.on('new_detection', (data) => {
            console.log('🚨 New detection received:', data);
            this.handleNewDetection(data);
        });

        socket.on('detections_update', (data) => {
            console.log('📊 Detections update:', data);
        });
    }

    /**
     * Load initial data
     */
    async loadInitialData() {
        try {
            // Load live detections
            const detections = await this.api.getLiveDetections();
            console.log(`📡 Loaded ${detections.length} live detections`);

            // Add markers to map
            detections.forEach(detection => {
                this.map.addMarker(detection);
            });

            // Add to alerts feed
            detections.slice(-10).reverse().forEach(detection => {
                this.addAlert(detection, false); // Don't play sound for initial load
            });

            // Load statistics
            await this.updateStatistics();

        } catch (error) {
            console.error('❌ Error loading initial data:', error);
            this.showToast('❌', 'Error', 'Failed to load initial data');
        }
    }

    /**
     * Handle new detection from WebSocket
     */
    handleNewDetection(data) {
        const { detection, duration, detection_id } = data;

        // Add marker to map
        this.map.addMarker(detection);

        // Add to alerts feed
        this.addAlert(detection, true); // Play sound

        // Update statistics
        this.updateStatistics();

        // Show toast notification
        const alertLevel = this.getAlertLevel(detection.confidence);
        this.showToast('🚨', `${alertLevel} Alert`, detection.message);
    }

    /**
     * Add alert to feed
     */
    addAlert(detection, playSound = true) {
        const { timestamp, confidence, message, latitude, longitude, image_base64 } = detection;
        const alertLevel = this.getAlertLevel(confidence);

        // Create alert element
        const alertElement = document.createElement('div');
        alertElement.className = `alert-item ${alertLevel.toLowerCase()}`;
        alertElement.innerHTML = `
            <div class="alert-header">
                <span class="alert-time">${timestamp}</span>
                <span class="alert-confidence ${alertLevel.toLowerCase()}">${(confidence * 100).toFixed(1)}%</span>
            </div>
            ${image_base64 ? `<img src="data:image/jpeg;base64,${image_base64}" class="alert-image" alt="Detection" />` : ''}
            <div class="alert-message">${message}</div>
            <div class="alert-location">📍 ${latitude.toFixed(6)}, ${longitude.toFixed(6)}</div>
        `;

        // Remove "no alerts" message if present
        const noAlerts = this.elements.alertsFeed.querySelector('.no-alerts');
        if (noAlerts) {
            noAlerts.remove();
        }

        // Add to feed (newest first)
        this.elements.alertsFeed.insertBefore(alertElement, this.elements.alertsFeed.firstChild);

        // Add to alerts array
        this.alerts.unshift(detection);

        // Remove oldest if exceeding max
        if (this.alerts.length > this.maxAlerts) {
            this.alerts.pop();
            const alertItems = this.elements.alertsFeed.querySelectorAll('.alert-item');
            if (alertItems.length > this.maxAlerts) {
                alertItems[alertItems.length - 1].remove();
            }
        }

        // Update alert count
        this.elements.alertCount.textContent = this.alerts.length;

        // Play alert sound
        if (playSound) {
            this.playAlertSound(alertLevel);
        }
    }

    /**
     * Update statistics dashboard
     */
    async updateStatistics() {
        try {
            const period = this.elements.statsPeriod.value;
            const stats = await this.api.getStatistics(period);

            if (stats) {
                // Animate number changes
                this.animateValue(this.elements.totalDetections, stats.total_detections || 0);
                this.animateValue(this.elements.highAlerts, stats.high_alerts || 0);

                // Update peak hour
                this.elements.peakHour.textContent = stats.peak_hour || '--:--';

                // Update average confidence
                const avgConf = stats.average_confidence || 0;
                this.elements.avgConfidence.textContent = `${(avgConf * 100).toFixed(0)}%`;
            }
        } catch (error) {
            console.error('❌ Error updating statistics:', error);
        }
    }

    /**
     * Animate number value change
     */
    animateValue(element, endValue) {
        const startValue = parseInt(element.textContent) || 0;
        const duration = 500;
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const currentValue = Math.floor(startValue + (endValue - startValue) * progress);
            element.textContent = currentValue;

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }

    /**
     * Start automatic statistics update
     */
    startStatsUpdate() {
        // Update every 30 seconds
        this.statsUpdateInterval = setInterval(() => {
            this.updateStatistics();
        }, 30000);
    }

    /**
     * Play alert sound using Web Audio API
     */
    playAlertSound(alertLevel) {
        if (!this.audioContext) return;

        try {
            const oscillator = this.audioContext.createOscillator();
            const gainNode = this.audioContext.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(this.audioContext.destination);

            // Set frequency based on alert level
            oscillator.frequency.value = alertLevel === 'HIGH' ? 1000 : 800;
            oscillator.type = 'sine';

            // Set volume
            gainNode.gain.setValueAtTime(0.3, this.audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.2);

            // Play sound
            oscillator.start(this.audioContext.currentTime);
            oscillator.stop(this.audioContext.currentTime + 0.2);
        } catch (error) {
            console.error('❌ Error playing alert sound:', error);
        }
    }

    /**
     * Get alert level from confidence
     */
    getAlertLevel(confidence) {
        if (confidence >= 0.85) return 'HIGH';
        if (confidence >= 0.70) return 'MEDIUM';
        return 'LOW';
    }

    /**
     * Update connection status indicator
     */
    updateConnectionStatus(connected) {
        if (connected) {
            this.elements.statusIndicator.classList.add('connected');
            this.elements.statusText.textContent = 'Connected';
        } else {
            this.elements.statusIndicator.classList.remove('connected');
            this.elements.statusText.textContent = 'Disconnected';
        }
    }

    /**
     * Show toast notification
     */
    showToast(icon, title, message) {
        this.elements.toastIcon.textContent = icon;
        this.elements.toastTitle.textContent = title;
        this.elements.toastMessage.textContent = message;

        this.elements.toast.classList.add('show');

        setTimeout(() => {
            this.elements.toast.classList.remove('show');
        }, 3000);
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Statistics period change
        this.elements.statsPeriod.addEventListener('change', () => {
            this.updateStatistics();
        });

        // Export CSV
        this.elements.exportCSV.addEventListener('click', async () => {
            try {
                const period = this.elements.statsPeriod.value;
                const filepath = await this.api.exportCSV(period);
                if (filepath) {
                    this.showToast('✅', 'Export Successful', `CSV saved to: ${filepath}`);
                }
            } catch (error) {
                this.showToast('❌', 'Export Failed', error.message);
            }
        });

        // Export PDF
        this.elements.exportPDF.addEventListener('click', async () => {
            try {
                const period = this.elements.statsPeriod.value;
                const filepath = await this.api.exportPDF(period);
                if (filepath) {
                    this.showToast('✅', 'Export Successful', `PDF saved to: ${filepath}`);
                }
            } catch (error) {
                this.showToast('❌', 'Export Failed', error.message);
            }
        });

        // Center map
        this.elements.centerMapBtn.addEventListener('click', () => {
            this.map.centerMap();
            this.showToast('🗺️', 'Map Centered', 'View reset to base location');
        });

        // Clear markers
        this.elements.clearMarkersBtn.addEventListener('click', () => {
            this.map.clearAllMarkers();
            this.showToast('🗑️', 'Markers Cleared', 'All detection markers removed');
        });

        // Set GPS Location button
        this.elements.setLocationBtn.addEventListener('click', () => {
            this.openLocationModal();
        });

        // Apply location
        this.elements.applyLocation.addEventListener('click', () => {
            this.applyCustomLocation();
        });

        // Cancel location
        this.elements.cancelLocation.addEventListener('click', () => {
            this.closeLocationModal();
        });

        // Close modal (X button)
        this.elements.closeModal.addEventListener('click', () => {
            this.closeLocationModal();
        });

        // Close modal on background click
        this.elements.locationModal.addEventListener('click', (e) => {
            if (e.target === this.elements.locationModal) {
                this.closeLocationModal();
            }
        });

        // Use My Location button
        this.elements.useMyLocationBtn.addEventListener('click', () => {
            this.requestUserLocation();
        });
    }

    /**
     * Request user's current location using browser geolocation
     */
    requestUserLocation() {
        // Check if geolocation is supported
        if (!navigator.geolocation) {
            this.showToast('❌', 'Not Supported', 'Geolocation is not supported by your browser');
            return;
        }

        // Disable button and show loading state
        this.elements.useMyLocationBtn.disabled = true;
        this.elements.useMyLocationBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="animation: spin 1s linear infinite;">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 6v6l4 2"/>
            </svg>
            Getting your location...
        `;

        // Request geolocation
        navigator.geolocation.getCurrentPosition(
            // Success callback
            (position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                const accuracy = position.coords.accuracy;

                // Update input fields
                this.elements.latitudeInput.value = lat.toFixed(6);
                this.elements.longitudeInput.value = lon.toFixed(6);

                // Re-enable button
                this.resetLocationButton();

                // Show success message
                this.showToast('✅', 'Location Found', `Accuracy: ±${Math.round(accuracy)}m`);

                console.log(`📍 User location: ${lat}, ${lon} (±${Math.round(accuracy)}m)`);
            },
            // Error callback
            (error) => {
                // Re-enable button
                this.resetLocationButton();

                // Handle different error types
                let errorMessage = 'Unable to get your location';
                switch (error.code) {
                    case error.PERMISSION_DENIED:
                        errorMessage = 'Location permission denied. Please allow location access in your browser settings.';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        errorMessage = 'Location information unavailable';
                        break;
                    case error.TIMEOUT:
                        errorMessage = 'Location request timed out';
                        break;
                }

                this.showToast('❌', 'Location Error', errorMessage);
                console.error('Geolocation error:', error);
            },
            // Options
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    }

    /**
     * Reset Use My Location button to default state
     */
    resetLocationButton() {
        this.elements.useMyLocationBtn.disabled = false;
        this.elements.useMyLocationBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <circle cx="12" cy="12" r="3"/>
                <line x1="12" y1="2" x2="12" y2="6"/>
                <line x1="12" y1="18" x2="12" y2="22"/>
                <line x1="2" y1="12" x2="6" y2="12"/>
                <line x1="18" y1="12" x2="22" y2="12"/>
            </svg>
            Use My Current Location
        `;
    }

    /**
     * Open GPS location modal
     */
    openLocationModal() {
        // Set current coordinates as defaults
        const [lat, lon] = this.map.centerCoords;
        this.elements.latitudeInput.value = lat;
        this.elements.longitudeInput.value = lon;

        // Show modal
        this.elements.locationModal.classList.add('show');
    }

    /**
     * Close GPS location modal
     */
    closeLocationModal() {
        this.elements.locationModal.classList.remove('show');
    }

    /**
     * Apply custom GPS location
     */
    applyCustomLocation() {
        const lat = parseFloat(this.elements.latitudeInput.value);
        const lon = parseFloat(this.elements.longitudeInput.value);

        // Validate coordinates
        if (isNaN(lat) || isNaN(lon)) {
            this.showToast('❌', 'Invalid Input', 'Please enter valid coordinates');
            return;
        }

        if (lat < -90 || lat > 90) {
            this.showToast('❌', 'Invalid Latitude', 'Latitude must be between -90 and 90');
            return;
        }

        if (lon < -180 || lon > 180) {
            this.showToast('❌', 'Invalid Longitude', 'Longitude must be between -180 and 180');
            return;
        }

        // Update map center
        this.map.centerCoords = [lat, lon];
        this.map.map.setView([lat, lon], this.map.zoom);

        // Update geofence
        this.map.updateGeofence(5000);

        // Update current location display
        this.elements.currentLocation.textContent = `${lat.toFixed(4)}, ${lon.toFixed(4)}`;

        // Close modal
        this.closeLocationModal();

        // Show success message
        this.showToast('📍', 'Location Updated', `Map centered at ${lat.toFixed(4)}, ${lon.toFixed(4)}`);

        console.log(`📍 Map location updated to: ${lat}, ${lon}`);
    }

    /**
     * Cleanup on page unload
     */
    cleanup() {
        if (this.statsUpdateInterval) {
            clearInterval(this.statsUpdateInterval);
        }
        if (this.audioContext) {
            this.audioContext.close();
        }
    }
}

// ============================================
// INITIALIZE APP
// ============================================

let commandPanel;

document.addEventListener('DOMContentLoaded', () => {
    commandPanel = new CommandPanel();
    commandPanel.init();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (commandPanel) {
        commandPanel.cleanup();
    }
});
