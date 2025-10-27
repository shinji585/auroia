// API endpoints
const API_ENDPOINTS = {
    ANALYZE: '/api/analyze',
};

// Función para enviar imagen al servidor
async function analyzeImage(formData) {
    try {
        const response = await fetch(API_ENDPOINTS.ANALYZE, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}