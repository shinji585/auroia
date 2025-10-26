/**
 * ui.js
 * 
 * Controla todas las manipulaciones del DOM, gestiona los estados de la interfaz
 * y actualiza los elementos visuales con los datos de la API.
 */

const DOMElements = {
    // Contenedores principales
    uploadArea: document.getElementById('uploadArea'),
    imagePreview: document.getElementById('imagePreview'),
    resultsContainer: document.getElementById('resultsContainer'),

    // Vistas de resultados
    resultsEmpty: document.getElementById('resultsEmpty'),
    resultsLoading: document.getElementById('resultsLoading'),
    resultsError: document.getElementById('resultsError'),
    resultsContent: document.getElementById('resultsContent'),

    // Input y botones
    fileInput: document.getElementById('fileInput'),
    clearBtn: document.getElementById('clearBtn'),
    retryBtn: document.getElementById('retryBtn'),
    newAnalysisBtn: document.getElementById('newAnalysisBtn'),

    // Elementos de datos
    previewImg: document.getElementById('previewImg'),
    errorMessage: document.getElementById('errorMessage'),
    diagnosisTitle: document.getElementById('diagnosisTitle'),
    confidencePercent: document.getElementById('confidencePercent'),
    confidenceFill: document.getElementById('confidenceFill'),
    differentialList: document.getElementById('differentialList'),
    shapImage: document.getElementById('shapImage'),
};

/**
 * Gestiona la visibilidad de los diferentes estados de la UI.
 * @param {'initial' | 'preview' | 'loading' | 'content' | 'error'} state
 * @param {string} [message] - Mensaje de error opcional.
 */
function setUIState(state, message = '') {
    // Ocultar todas las vistas de la columna de resultados
    DOMElements.resultsEmpty.classList.add('hidden');
    DOMElements.resultsLoading.classList.add('hidden');
    DOMElements.resultsError.classList.add('hidden');
    DOMElements.resultsContent.classList.add('hidden');
    
    // Quitar animación de los elementos clave
    DOMElements.diagnosisTitle.classList.remove('animate-text-glow');
    DOMElements.confidencePercent.classList.remove('animate-text-glow');

    // Gestionar visibilidad de la columna de carga
    const isPreview = state === 'preview' || state === 'loading' || state === 'content' || state === 'error';
    DOMElements.uploadArea.classList.toggle('hidden', isPreview);
    DOMElements.imagePreview.classList.toggle('hidden', !isPreview);

    switch (state) {
        case 'initial':
            DOMElements.resultsEmpty.classList.remove('hidden');
            break;
        case 'loading':
            DOMElements.resultsLoading.classList.remove('hidden');
            break;
        case 'content':
            DOMElements.resultsContent.classList.remove('hidden');
            // Añadir animación a los elementos clave
            DOMElements.diagnosisTitle.classList.add('animate-text-glow');
            DOMElements.confidencePercent.classList.add('animate-text-glow');
            break;
        case 'error':
            DOMElements.resultsError.classList.remove('hidden');
            DOMElements.errorMessage.textContent = message;
            break;
    }
}

/**
 * Muestra la previsualización de la imagen seleccionada.
 * @param {File} file
 */
function showImagePreview(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        DOMElements.previewImg.src = e.target.result;
        setUIState('preview');
    };
    reader.readAsDataURL(file);
}

/**
 * Rellena la UI con los resultados de la predicción.
 * @param {object} apiResponse
 */
function updateResults(apiResponse) {
    const { prediction } = apiResponse;
    const { main_diagnosis, differential_diagnoses, shap_image_url } = prediction;

    // Diagnóstico Principal
    DOMElements.diagnosisTitle.textContent = main_diagnosis.name;
    DOMElements.confidencePercent.textContent = `${Math.round(main_diagnosis.confidence * 100)}%`;
    
    // Barra de confianza con color dinámico
    const confidence = main_diagnosis.confidence;
    let barColorClass = 'bg-green-500'; // High confidence
    if (confidence < 0.8) barColorClass = 'bg-yellow-500'; // Medium
    if (confidence < 0.6) barColorClass = 'bg-red-500'; // Low
    
    DOMElements.confidenceFill.style.width = `0%`; // Reset inicial para animación
    setTimeout(() => {
        DOMElements.confidenceFill.style.width = `${confidence * 100}%`;
        DOMElements.confidenceFill.className = `h-2.5 rounded-full transition-all duration-1000 ease-out ${barColorClass}`;
    }, 100); // Pequeño delay para asegurar que la transición se aplique

    // Diagnósticos Diferenciales
    DOMElements.differentialList.innerHTML = ''; // Limpiar lista anterior
    differential_diagnoses.forEach(diag => {
        const item = document.createElement('div');
        item.className = 'grid grid-cols-2 items-center gap-4';
        item.innerHTML = `
            <p class="text-sm font-medium text-gray-300">${diag.name}</p>
            <div class="flex items-center justify-end">
                <div class="w-2/3 bg-brand-border rounded-full h-1.5 mr-3">
                    <div class="bg-brand-blue h-1.5 rounded-full" style="width: ${diag.confidence * 100}%"></div>
                </div>
                <p class="text-sm font-mono text-gray-400">${(diag.confidence * 100).toFixed(0)}%</p>
            </div>
        `;
        DOMElements.differentialList.appendChild(item);
    });

    // Imagen SHAP
    DOMElements.shapImage.src = shap_image_url;
}

/**
 * Resetea la UI a su estado inicial.
 */
function resetUI() {
    DOMElements.fileInput.value = ''; // Permite seleccionar el mismo archivo de nuevo
    DOMElements.previewImg.src = '';
    setUIState('initial');
}
