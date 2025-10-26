/**
 * ui.js
 * 
 * Gestiona todos los elementos del DOM y las actualizaciones de la interfaz de usuario.
 */

// Objeto central para acceder a todos los elementos importantes del DOM.
// AHORA los nombres de las variables y los IDs coinciden perfectamente.
const DOMElements = {
    // --- Columna Izquierda ---
    analysisTypeSelect: document.getElementById('analysisType'),
    uploadArea: document.getElementById('uploadArea'),
    fileInput: document.getElementById('fileInput'),
    uploadTitle: document.getElementById('uploadTitle'),
    uploadHint: document.querySelector('#uploadArea p.text-gray-400'), // Selector más específico para "o haz click"
    uploadFormats: document.getElementById('uploadFormats'), // <-- ¡LA CORRECCIÓN CLAVE!
    imagePreview: document.getElementById('imagePreview'),
    previewImg: document.getElementById('previewImg'),
    clearBtn: document.getElementById('clearBtn'),
    
    // --- Columna Derecha ---
    resultsContainer: document.getElementById('resultsContainer'),
    resultsEmpty: document.getElementById('resultsEmpty'),
    resultsLoading: document.getElementById('resultsLoading'),
    resultsError: document.getElementById('resultsError'),
    errorMessage: document.getElementById('errorMessage'),
    retryBtn: document.getElementById('retryBtn'),
    resultsContent: document.getElementById('resultsContent'),
    resultsHint: document.getElementById('resultsHint')
};

/**
 * Envía el archivo al backend para su análisis.
 * @param {File} file - El archivo a analizar.
 * @param {string} analysisType - 'piel' o 'sangre'.
 * @returns {Promise<object>} - Una promesa que se resuelve con los resultados del análisis.
 */
async function analyzeFile(file, analysisType) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('analysis_type', analysisType);

    const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Error desconocido en el servidor' }));
        throw new Error(errorData.error || `Error del servidor: ${response.statusText}`);
    }

    return response.json();
}


/**
 * Actualiza la UI del área de carga según el tipo de análisis seleccionado.
 * @param {string} analysisType - 'piel' o 'sangre'.
 */
function updateUIForAnalysisType(analysisType) {
    if (analysisType === 'piel') {
        DOMElements.uploadTitle.textContent = 'Arrastra tu imagen de piel aquí';
        DOMElements.uploadFormats.textContent = 'Formatos soportados: JPG, PNG (hasta 10MB)';
        DOMElements.fileInput.accept = 'image/jpeg,image/png';
        DOMElements.resultsHint.textContent = 'Selecciona una imagen de piel para iniciar el diagnóstico.';
    } else { // 'sangre'
        DOMElements.uploadTitle.textContent = 'Arrastra tu archivo de datos aquí';
        DOMElements.uploadFormats.textContent = 'Formatos soportados: CSV, JSON (hasta 1MB)';
        DOMElements.fileInput.accept = '.csv,application/json';
        DOMElements.resultsHint.textContent = 'Selecciona un archivo de datos para iniciar el análisis.';
    }
    resetUI();
}

/**
 * Muestra el área de carga y oculta la vista previa de la imagen.
 */
function showUploadArea() {
    DOMElements.uploadArea.classList.remove('hidden');
    DOMElements.imagePreview.classList.add('hidden');
}

/**
 * Muestra la vista previa de la imagen y oculta el área de carga.
 * @param {string} imageUrl - La URL de la imagen a previsualizar.
 */
function showImagePreview(imageUrl) {
    DOMElements.previewImg.src = imageUrl;
    DOMElements.uploadArea.classList.add('hidden');
    DOMElements.imagePreview.classList.remove('hidden');
}

/**
 * Cambia la vista de resultados al estado de "cargando".
 */
function showLoadingState() {
    DOMElements.resultsEmpty.classList.add('hidden');
    DOMElements.resultsError.classList.add('hidden');
    DOMElements.resultsContent.classList.add('hidden');
    DOMElements.resultsLoading.classList.remove('hidden');
}

/**
 * Muestra un mensaje de error en la sección de resultados.
 * @param {string} message - El mensaje de error a mostrar.
 */
function showErrorState(message) {
    DOMElements.errorMessage.textContent = message;
    DOMElements.resultsEmpty.classList.add('hidden');
    DOMElements.resultsLoading.classList.add('hidden');
    DOMElements.resultsContent.classList.add('hidden');
    DOMElements.resultsError.classList.remove('hidden');
}

/**
 * Muestra los resultados del análisis y los renderiza en la UI.
 * @param {object} data - El objeto con los datos del resultado.
 */
function showResultsState(data) {
    // Lógica para renderizar los resultados
    const formattedJson = JSON.stringify(data, null, 4); // Indentación de 4 espacios
    DOMElements.resultsContent.innerHTML = `<pre class="whitespace-pre-wrap text-sm bg-brand-dark p-4 rounded-lg"><code>${formattedJson}</code></pre>`;
    
    DOMElements.resultsEmpty.classList.add('hidden');
    DOMElements.resultsLoading.classList.add('hidden');
    DOMElements.resultsError.classList.add('hidden');
    DOMElements.resultsContent.classList.remove('hidden');
}

/**
 * Resetea toda la interfaz a su estado inicial.
 */
function resetUI() {
    showUploadArea();
    DOMElements.resultsContent.innerHTML = '';
    DOMElements.resultsContent.classList.add('hidden');
    DOMElements.resultsError.classList.add('hidden');
    DOMElements.resultsLoading.classList.add('hidden');
    DOMElements.resultsEmpty.classList.remove('hidden');
    DOMElements.fileInput.value = '';
}
