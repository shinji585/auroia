/**
 * main.js
 * 
 * Orquesta la lógica principal, manejando eventos del usuario y 
 * coordinando entre la UI, el manejador de subidas y la API.
 */

document.addEventListener('DOMContentLoaded', () => {
    
    // Función principal de manejo de archivo
    const handleFile = async (file) => {
        if (!file) return;

        const analysisType = DOMElements.analysisType.value;
        
        // Mostrar previsualización (solo para imágenes)
        if (analysisType === 'piel') {
            showImagePreview(file);
        }
        
        setUIState('loading');
        
        try {
            // Llamar a la API con el archivo y el tipo de análisis
            const response = await fetchPrediction(file, analysisType);
            
            // Actualizar la UI con la respuesta, pasando el tipo de análisis
            updateResults(response, analysisType);
            setUIState('content');

        } catch (error) {
            console.error("Error en el flujo principal:", error);
            setUIState('error', error.message);
        }
    };

    // Inicializar el manejador de subidas
    initializeUpload(handleFile);
    
    // --- Event Listeners ---

    // Cambiar imagen o archivo
    DOMElements.clearBtn.addEventListener('click', resetUI);
    DOMElements.newAnalysisBtn?.addEventListener('click', resetUI); // El botón puede no existir al inicio

    // Reintentar en caso de error
    DOMElements.retryBtn.addEventListener('click', () => {
        // Intenta reenviar el último archivo seleccionado si existe
        if (DOMElements.fileInput.files.length > 0) {
            handleFile(DOMElements.fileInput.files[0]);
        }
    });

    // Listener para el cambio de tipo de análisis
    DOMElements.analysisType.addEventListener('change', (event) => {
        const selectedType = event.target.value;
        updateUploadAreaForType(selectedType);
        resetUI(); // Resetea el estado al cambiar de tipo
    });

    // Inicializar el área de subida según el valor por defecto
    updateUploadAreaForType(DOMElements.analysisType.value);
});
