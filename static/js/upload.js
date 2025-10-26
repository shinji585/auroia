/**
 * upload.js
 * 
 * Gestiona la funcionalidad del área de carga, incluyendo el click,
 * el arrastrar y soltar, y la validación inicial del archivo.
 */

// --- PREVENCIÓN GLOBAL DE COMPORTAMIENTO INDESEADO ---
// Previene que el navegador abra el archivo si se suelta accidentalmente fuera del área designada.
['dragover', 'drop'].forEach(eventName => {
    window.addEventListener(eventName, e => e.preventDefault(), false);
});

/**
 * Inicializa el área de carga con los manejadores de eventos necesarios.
 * @param {function(File): void} handleFileCallback - La función a llamar cuando se obtiene un archivo válido.
 */
function initializeUpload(handleFileCallback) {
    const { uploadArea, fileInput } = DOMElements;

    // --- Manejador de Click ---
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // --- Manejador de Cambio en el Input ---
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            handleFileCallback(file);
        }
    });

    // --- Manejadores de Arrastrar y Soltar (Específicos al Área) ---

    // Prevenir la propagación para que nuestros manejadores funcionen
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, e => {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });

    // Feedback visual al arrastrar sobre el área
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => {
            uploadArea.classList.add('border-brand-blue', 'bg-gray-800/20');
        }, false);
    });

    // Quitar feedback visual al salir o soltar
    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => {
            uploadArea.classList.remove('border-brand-blue', 'bg-gray-800/20');
        }, false);
    });

    // Manejar el archivo soltado
    uploadArea.addEventListener('drop', (e) => {
        const file = e.dataTransfer.files[0];
        if (file) {
            fileInput.files = e.dataTransfer.files; // Asignar al input para consistencia
            handleFileCallback(file);
        }
    }, false);
}
