/**
 * upload.js
 * 
 * Gestiona la funcionalidad del área de carga, incluyendo el click,
 * el arrastrar y soltar, y la validación inicial del archivo.
 */

// --- PREVENCIÓN GLOBAL DE COMPORTAMIENTO INDESEADO ---
// Previene que el navegador abra el archivo si se suelta accidentalmente
// fuera del área designada. Esto es un "seguro" global que se aplica a toda la ventana.
['dragover', 'drop'].forEach(eventName => {
    window.addEventListener(eventName, (e) => {
        e.preventDefault();
    }, false);
});

/**
 * Inicializa el área de carga con los manejadores de eventos necesarios.
 * @param {function(File): void} handleFileCallback - La función a llamar cuando se obtiene un archivo válido.
 */
function initializeUpload(handleFileCallback) {
    const uploadArea = DOMElements.uploadArea;
    const fileInput = DOMElements.fileInput;

    // --- Manejador de Click ---
    // Al hacer click en el área, se activa el input de archivo oculto.
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // --- Manejador de Cambio en el Input ---
    // Cuando el usuario selecciona un archivo a través del diálogo.
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            handleFileCallback(file);
        }
    });

    // --- Manejadores de Arrastrar y Soltar (Específicos al Área) ---

    // 1. Prevenir la propagación para que no interfiera con otros elementos
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });

    // 2. Añadir feedback visual al arrastrar un archivo sobre el área.
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => {
            // Usamos las clases del HTML proporcionado
            uploadArea.classList.add('border-brand-blue', 'bg-gray-800/20'); 
        }, false);
    });

    // 3. Quitar el feedback visual cuando el archivo sale del área.
    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => {
            uploadArea.classList.remove('border-brand-blue', 'bg-gray-800/20');
        }, false);
    });

    // 4. Manejar el archivo que se ha soltado.
    uploadArea.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const file = dt.files[0];

        if (file) {
            // Asignar el archivo al input para consistencia
            fileInput.files = dt.files; 
            handleFileCallback(file);
        }
    }, false);
}
