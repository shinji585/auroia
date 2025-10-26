/**
 * api.js
 * 
 * Simula la comunicación con el backend. En el futuro, este archivo
 * contendrá la lógica para realizar llamadas reales al servidor Flask.
 */

/**
 * Simula una llamada a la API para obtener una predicción de diagnóstico.
 * 
 * @param {string | null} imageBase64 - La imagen codificada en base64 (actualmente no se usa).
 * @returns {Promise<object>} Una promesa que se resuelve con los datos de la predicción.
 */
async function fetchPrediction(imageBase64) {
    console.log("Iniciando simulación de llamada a la API...");

    // Simular el tiempo de espera de la red (entre 1.5 y 3 segundos)
    const delay = ms => new Promise(res => setTimeout(res, ms));
    await delay(1500 + Math.random() * 1500);

    // Simular una posible falla de la API (20% de probabilidad)
    if (Math.random() < 0.2) {
        console.error("Simulación de error de API.");
        throw new Error("El modelo de IA no pudo procesar la imagen. Inténtelo de nuevo.");
    }

    // Datos de ejemplo que simulan la respuesta del backend
    const mockApiResponse = {
        status: "success",
        prediction: {
            main_diagnosis: {
                name: "Neumonía Viral",
                confidence: 0.86
            },
            differential_diagnoses: [
                { name: "Neumonía Bacteriana", confidence: 0.11 },
                { name: "Edema Pulmonar", confidence: 0.02 },
                { name: "Normal", confidence: 0.01 }
            ],
            // Usamos una URL de placeholder para la imagen SHAP
            shap_image_url: "https://i.imgur.com/IRs42dD.png"
        }
    };

    console.log("Simulación de API completada con éxito.", mockApiResponse);
    return mockApiResponse;
}
