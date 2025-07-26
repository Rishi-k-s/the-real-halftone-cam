const API_BASE_URL = 'http://localhost:5000';

class APIService {
  async makeRequest(endpoint, options = {}) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Handle different response types
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      } else if (contentType && contentType.includes('image/')) {
        return response.blob();
      } else {
        return response.text();
      }
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Camera operations
  async capturePhoto(params = {}) {
    return this.makeRequest('/capture', {
      method: 'POST',
      body: JSON.stringify({
        width: params.width || 1280,
        height: params.height || 720,
        camera_preference: params.camera_preference || 'auto',
      }),
    });
  }

  // Image processing
  async convertImage(params) {
    return this.makeRequest('/convert', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  // Get preview image
  async getPreview() {
    return this.makeRequest('/preview');
  }

  // Get last captured photo
  async getLastPhoto() {
    return this.makeRequest('/static/photo.jpg');
  }

  // Printing operations
  async getPrinters() {
    return this.makeRequest('/printers');
  }

  async printImage(printerName, options = {}) {
    return this.makeRequest('/print', {
      method: 'POST',
      body: JSON.stringify({
        printer: printerName,
        ...options,
      }),
    });
  }

  // System status
  async getStatus() {
    return this.makeRequest('/status');
  }

  // History operations
  async getHistory(page = 1, limit = 12) {
    return this.makeRequest(`/history?page=${page}&limit=${limit}`);
  }
}

export default new APIService();
