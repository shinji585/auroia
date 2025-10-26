/**
 * main.js
 * 
 * Punto de entrada principal. Orquesta la inicialización de la UI,
 * la carga de archivos y el flujo de análisis.
 */

document.addEventListener('DOMContentLoaded', () => {

    // 1. Inicializar la UI en su estado por defecto.
    setUIState('initial');

    // 2. Preparar el área de carga para recibir un archivo.
    initializeUpload(handleAnalysisRequest);

    // 3. Configurar listeners para los botones de la UI.
    DOMElements.clearBtn.addEventListener('click', resetUI);
    DOMElements.retryBtn.addEventListener('click', () => {
        // Reintenta usando el último archivo válido (si existe)
        const lastFile = DOMElements.fileInput.files[0];
        if (lastFile) {
            handleAnalysisRequest(lastFile);
        }
    });
    DOMElements.newAnalysisBtn.addEventListener('click', resetUI);
});

/**
 * Orquesta el proceso de análisis de una imagen.
 * @param {File} file El archivo a analizar.
 */
async function handleAnalysisRequest(file) {
    // Mostrar estado de carga
    setUIState('loading');

    try {
        // No necesitamos convertir a base64 para la simulación,
        // pero esta línea será útil en el futuro.
        // const imageBase64 = await toBase64(file);

        // Llamar a la API simulada
        const response = await fetchPrediction(null);

        // Actualizar la UI con los resultados
        updateResults(response);

        // Mostrar el contenido de los resultados
        setUIState('content');

    } catch (error) {
        console.error("Error en el flujo de análisis:", error);
        setUIState('error', error.message || "Ocurrió un error desconocido.");
    }
}

/**
 * Utilidad para convertir un archivo a formato base64.
 * @param {File} file
 * @returns {Promise<string>}
 */
function toBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
    });
}
