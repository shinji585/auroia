/**
 * api.js
 * 
 * Realiza la comunicación con el backend de Flask para obtener predicciones reales.
 */

/**
 * Envía el archivo al backend y obtiene una predicción o análisis.
 * 
 * @param {File} file - El archivo a analizar (imagen o datos).
 * @param {string} analysisType - El tipo de análisis a realizar ('piel' o 'sangre').
 * @returns {Promise<object>} Una promesa que se resuelve con los datos de la predicción del backend.
 */
async function fetchPrediction(file, analysisType) {
    console.log(`Iniciando llamada a la API para análisis de tipo: ${analysisType}`);

    const formData = new FormData();
    formData.append('file', file);
    // ¡LA LÍNEA QUE FALTABA! Añadir el tipo de análisis al formulario.
    formData.append('analysis_type', analysisType);

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            const errorMessage = errorData?.message || `Error del servidor: ${response.status}`;
            console.error("Error en la respuesta de la API:", errorMessage);
            throw new Error(errorMessage);
        }

        const data = await response.json();

        if (data.status === 'error') {
            console.error("Error reportado por el backend:", data.message);
            throw new Error(data.message);
        }

        console.log("Llamada a la API completada con éxito.", data);
        return data;

    } catch (error) {
        console.error("Fallo en la comunicación con la API:", error);
        throw new Error(error.message || "No se pudo establecer comunicación con el servidor de análisis.");
    }
}
