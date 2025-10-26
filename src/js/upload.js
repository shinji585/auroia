/**
 * upload.js
 * 
 * Gestiona la lógica de carga de archivos, incluyendo el drag & drop
 * y la validación del archivo seleccionado.
 */

/**
 * Inicializa los listeners para la carga de archivos.
 * @param {function(File): void} onFileReady - Callback a ejecutar cuando un archivo es válido.
 */
function initializeUpload(onFileReady) {
    const uploadArea = DOMElements.uploadArea;
    const fileInput = DOMElements.fileInput;

    // Abrir selector de archivos al hacer click
    uploadArea.addEventListener('click', () => fileInput.click());

    // Manejar archivo seleccionado desde el input
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            handleFile(file, onFileReady);
        }
    });

    // --- Lógica de Drag and Drop ---

    // Prevenir comportamientos por defecto del navegador
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Añadir/quitar clases para feedback visual
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => uploadArea.classList.add('border-brand-blue', 'bg-gray-800/20'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => uploadArea.classList.remove('border-brand-blue', 'bg-gray-800/20'), false);
    });

    // Manejar el archivo soltado
    uploadArea.addEventListener('drop', (e) => {
        const file = e.dataTransfer.files[0];
        if (file) {
            handleFile(file, onFileReady);
        }
    });
}

/**
 * Valida el archivo y, si es correcto, lo pasa a los siguientes pasos.
 * @param {File} file
 * @param {function(File): void} onFileReady 
 */
function handleFile(file, onFileReady) {
    // Validación simple (tipo y tamaño)
    const allowedTypes = ['image/jpeg', 'image/png', 'application/dicom'];
    const maxSize = 10 * 1024 * 1024; // 10 MB

    // Para DICOM, el tipo puede ser vacío, así que también comprobamos la extensión
    const isDicom = file.name.toLowerCase().endsWith('.dcm');

    if ((!allowedTypes.includes(file.type) && !isDicom) || file.size > maxSize) {
        alert("Error: Archivo no válido. Por favor, selecciona un JPG, PNG o DICOM de menos de 10MB.");
        return;
    }

    // Mostrar previsualización
    showImagePreview(file);
    
    // Iniciar el proceso de análisis
    onFileReady(file);
}
