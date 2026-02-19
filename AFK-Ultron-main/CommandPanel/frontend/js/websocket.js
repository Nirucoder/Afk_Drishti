// WebSocket Module for Real-Time Updates

let socket = null;
let isConnected = false;

function initWebSocket() {
    socket = io(WS_URL);

    socket.on('connect', () => {
        console.log('✅ WebSocket connected');
        isConnected = true;
        updateConnectionStatus(true);
    });

    socket.on('disconnect', () => {
        console.log('❌ WebSocket disconnected');
        isConnected = false;
        updateConnectionStatus(false);
    });

    socket.on('new_detection', (data) => {
        console.log('🚨 New detection received:', data);
        handleNewDetection(data);
    });

    socket.on('connection_response', (data) => {
        console.log('📡 Connection response:', data);
    });
}

function updateConnectionStatus(connected) {
    const statusDot = document.getElementById('connectionStatus');
    const statusText = document.getElementById('statusText');

    if (connected) {
        statusDot.classList.add('connected');
        statusText.textContent = 'Connected';
    } else {
        statusDot.classList.remove('connected');
        statusText.textContent = 'Disconnected';
    }
}

console.log('✅ WebSocket module loaded');
