/**
 * main.js
 * 
 * El script principal que orquesta toda la aplicación.
 * Inicializa los manejadores de eventos y coordina la interacción entre la UI,
 * la carga de archivos y la comunicación con la API.
 */

document.addEventListener('DOMContentLoaded', () => {

    // --- ESTADO INICIAL DE LA UI ---
    // Al cargar la página, asegura que la UI coincida con el valor seleccionado por defecto.
    const initialAnalysisType = DOMElements.analysisTypeSelect.value;
    updateUIForAnalysisType(initialAnalysisType);

    // --- MANEJADOR DE CAMBIO DE TIPO DE ANÁLISIS ---
    // La clave para que la UI reaccione y cambie el `accept` del input.
    DOMElements.analysisTypeSelect.addEventListener('change', (e) => {
        updateUIForAnalysisType(e.target.value);
    });

    // --- MANEJADOR DEL ARCHIVO RECIBIDO ---
    // Esta función se pasa a `initializeUpload` y se ejecuta cuando se recibe un archivo válido.
    const handleFile = (file) => {
        const analysisType = DOMElements.analysisTypeSelect.value;

        // Validación básica del lado del cliente
        if (analysisType === 'piel') {
            if (!['image/jpeg', 'image/png'].includes(file.type)) {
                alert('Error: Por favor, selecciona un archivo de imagen JPG o PNG.');
                return;
            }
            const reader = new FileReader();
            reader.onload = (e) => showImagePreview(e.target.result);
            reader.readAsDataURL(file);
        } else {
            // Para análisis de datos, podrías mostrar el nombre del archivo si quisieras,
            // pero por ahora simplemente procedemos.
            showImagePreview('/static/assets/data-icon.svg'); // Muestra un ícono genérico
        }

        // Inicia el proceso de análisis
        processFile(file, analysisType);
    };

    // --- FUNCIÓN DE PROCESAMIENTO ---
    const processFile = async (file, analysisType) => {
        showLoadingState();
        try {
            const result = await analyzeFile(file, analysisType);
            showResultsState(result);
        } catch (error) {
            showErrorState(error.message || 'Un error desconocido ocurrió durante el análisis.');
        }
    };

    // --- INICIALIZACIÓN DEL ÁREA DE CARGA ---
    initializeUpload(handleFile);

    // --- MANEJADORES DE BOTONES DE REINTENTO Y LIMPIEZA ---
    DOMElements.clearBtn.addEventListener('click', resetUI);
    DOMElements.retryBtn.addEventListener('click', resetUI);
});
