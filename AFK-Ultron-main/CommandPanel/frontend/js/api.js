// API Communication Module

class API {
    constructor(baseURL) {
        this.baseURL = baseURL;
    }

    async request(endpoint, options = {}) {
        try {
            const url = `${this.baseURL}${endpoint}`;
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    }

    async getLiveDetections() {
        return this.request('/api/detections/live');
    }

    async getAllDetections() {
        return this.request('/api/detections/all');
    }

    async getStatistics(period = 'all') {
        return this.request(`/api/statistics?period=${period}`);
    }

    async exportCSV(period = 'all') {
        return this.request(`/api/export/csv?period=${period}`);
    }

    async exportPDF(period = 'all') {
        return this.request(`/api/export/pdf?period=${period}`);
    }
}

const api = new API(API_BASE_URL);
console.log('✅ API module loaded');
