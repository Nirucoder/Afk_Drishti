// Configuration file for API endpoints

// Automatically detect if running on same server or different
const API_BASE_URL = window.location.origin;
const WS_URL = window.location.origin;

// For development with separate servers, uncomment below:
// const API_BASE_URL = 'http://localhost:5000';
// const WS_URL = 'http://localhost:5000';

// Map configuration
const MAP_CONFIG = {
    defaultCenter: [28.6139, 77.2090], // Default to Delhi, India
    defaultZoom: 13,
    geofenceRadius: 5000, // 5km in meters
    tileLayer: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '© OpenStreetMap contributors'
};

// Alert configuration
const ALERT_CONFIG = {
    maxAlerts: 50, // Maximum alerts to display
    autoRefreshInterval: 5000 // Refresh every 5 seconds
};

console.log('📡 API Configuration loaded:', {
    API_BASE_URL,
    WS_URL,
    MAP_CONFIG
});
