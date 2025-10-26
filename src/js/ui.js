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
    analysisType: document.getElementById('analysisType'),
    clearBtn: document.getElementById('clearBtn'),
    retryBtn: document.getElementById('retryBtn'),
    // newAnalysisBtn se crea dinámicamente

    // Elementos de UI de carga
    uploadTitle: document.getElementById('uploadTitle'),
    uploadHint: document.getElementById('uploadHint'),

    // Elementos de datos
    previewImg: document.getElementById('previewImg'),
    errorMessage: document.getElementById('errorMessage'),
    resultsHint: document.getElementById('resultsHint'),
}; 

/**
 * Gestiona la visibilidad de los diferentes estados de la UI.
 * @param {'initial' | 'preview' | 'loading' | 'content' | 'error'} state
 * @param {string} [message] - Mensaje de error opcional.
 */
function setUIState(state, message = '') {
    DOMElements.resultsEmpty.classList.add('hidden');
    DOMElements.resultsLoading.classList.add('hidden');
    DOMElements.resultsError.classList.add('hidden');
    DOMElements.resultsContent.classList.add('hidden');

    const analysisType = DOMElements.analysisType.value;
    const isImageAnalysis = analysisType === 'piel';
    
    // La previsualización de imagen solo se muestra para análisis de piel
    const showPreview = isImageAnalysis && (state === 'preview' || state === 'loading' || state === 'content' || state === 'error');
    DOMElements.uploadArea.classList.toggle('hidden', showPreview);
    DOMElements.imagePreview.classList.toggle('hidden', !showPreview);

    switch (state) {
        case 'initial':
            DOMElements.resultsEmpty.classList.remove('hidden');
            break;
        case 'loading':
            // Si no es análisis de imagen, el área de carga no se oculta
            if (!isImageAnalysis) {
                DOMElements.uploadArea.classList.remove('hidden');
            }
            DOMElements.resultsLoading.classList.remove('hidden');
            break;
        case 'content':
            DOMElements.resultsContent.classList.remove('hidden');
            break;
        case 'error':
            DOMElements.resultsError.classList.remove('hidden');
            DOMElements.errorMessage.textContent = message;
            break;
    }
}

/**
 * Actualiza el área de carga según el tipo de análisis seleccionado.
 * @param {string} type - 'sangre' o 'piel'
 */
function updateUploadAreaForType(type) {
    if (type === 'sangre') {
        DOMElements.uploadTitle.textContent = "Arrastra tu archivo de datos aquí";
        DOMElements.uploadHint.textContent = "Formatos soportados: JSON (hasta 1MB)";
        DOMElements.fileInput.accept = "application/json";
        DOMElements.resultsHint.textContent = "Selecciona un archivo de análisis de sangre para comenzar.";
    } else { // piel
        DOMElements.uploadTitle.textContent = "Arrastra tu imagen de piel aquí";
        DOMElements.uploadHint.textContent = "Formatos soportados: JPG, PNG (hasta 10MB)";
        DOMElements.fileInput.accept = "image/jpeg,image/png";
        DOMElements.resultsHint.textContent = "Selecciona una imagen de piel para iniciar el diagnóstico.";
    }
}

/**
 * Muestra la previsualización de la imagen seleccionada (solo para análisis de piel).
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
 * Enrutador principal para mostrar los resultados según el tipo de análisis.
 * @param {object} apiResponse - La respuesta completa de la API.
 * @param {string} analysisType - El tipo de análisis realizado ('sangre' o 'piel').
 */
function updateResults(apiResponse, analysisType) {
    DOMElements.resultsContent.innerHTML = ''; // Limpiar resultados anteriores

    if (analysisType === 'piel' && apiResponse.prediction) {
        renderSkinAnalysisResults(apiResponse.prediction);
    } else if (analysisType === 'sangre' && apiResponse.report) {
        renderBloodAnalysisResults(apiResponse.report);
    } else {
        throw new Error("La respuesta de la API no tiene el formato esperado.");
    }

    // Añadir botón de nuevo análisis al final
    const newAnalysisBtn = document.createElement('button');
    newAnalysisBtn.id = 'newAnalysisBtn';
    newAnalysisBtn.className = "w-full mt-4 py-3 bg-brand-blue text-white rounded-lg font-semibold hover:bg-blue-600 transition-colors duration-300";
    newAnalysisBtn.textContent = "Analizar Otro Archivo";
    newAnalysisBtn.addEventListener('click', resetUI);
    DOMElements.resultsContent.appendChild(newAnalysisBtn);
}

/**
 * Renderiza los resultados para el análisis de piel (formato imagen).
 * @param {object} predictionData
 */
function renderSkinAnalysisResults(predictionData) {
    const { main_diagnosis, differential_diagnoses, shap_image_url } = predictionData;
    
    const confidence = main_diagnosis.confidence;
    let barColorClass = 'bg-green-500';
    if (confidence < 0.8) barColorClass = 'bg-yellow-500';
    if (confidence < 0.6) barColorClass = 'bg-red-500';

    let contentHTML = `
        <!-- Diagnóstico Principal -->
        <div class="bg-brand-dark p-6 rounded-lg border border-brand-border">
            <div class="flex justify-between items-center">
                <h2 class="text-3xl font-bold text-white animate-text-glow">${main_diagnosis.name}</h2>
                <p class="text-4xl font-mono font-bold text-brand-blue animate-text-glow">${Math.round(confidence * 100)}%</p>
            </div>
            <p class="text-sm text-gray-400 uppercase tracking-wider mt-2 mb-3">Confianza del Diagnóstico</p>
            <div class="w-full bg-brand-border rounded-full h-2.5">
                <div class="${barColorClass} h-2.5 rounded-full" style="width: ${confidence * 100}%"></div>
            </div>
        </div>

        <!-- Explicabilidad SHAP -->
        <div>
            <h3 class="text-xl font-semibold text-white mb-2">¿Por qué este diagnóstico?</h3>
            <p class="text-sm text-gray-400 mb-3">Las áreas resaltadas en la imagen influyeron más en la decisión del modelo.</p>
            <img src="${shap_image_url}" alt="Explicación SHAP" class="rounded-lg border border-brand-border w-full">
        </div>
    `;

    DOMElements.resultsContent.innerHTML = contentHTML;
}

/**
 * Renderiza los resultados para el análisis de sangre (formato texto).
 * @param {object} reportData
 */
function renderBloodAnalysisResults(reportData) {
    const { title, details, current_diagnoses, future_projections } = reportData;

    let futureProjectionsHTML = future_projections.projections.map(p => `
        <div class="flex justify-between items-center text-gray-300">
            <span>${p.state}</span>
            <span class="font-mono text-brand-blue">${(p.probability * 100).toFixed(0)}%</span>
        </div>
    `).join('');

    let contentHTML = `
        <!-- Título del Informe -->
        <h2 class="text-3xl font-bold text-white text-center mb-4">${title}</h2>

        <!-- Detalles del Análisis -->
        <div class="bg-brand-dark p-4 rounded-lg border border-brand-border">
            <h3 class="text-xl font-semibold text-white mb-3">Análisis de Valores</h3>
            <pre class="text-sm text-gray-300 whitespace-pre-wrap font-mono">${details}</pre>
        </div>

        <!-- Diagnóstico Actual -->
        <div class="bg-brand-dark p-4 rounded-lg border border-brand-border">
            <h3 class="text-xl font-semibold text-white mb-3">Diagnóstico Actual Probable</h3>
            <div class="flex flex-wrap gap-2">
                ${current_diagnoses.map(d => `<span class="bg-brand-blue/20 text-brand-blue text-sm font-semibold px-3 py-1 rounded-full">${d}</span>`).join('')}
            </div>
        </div>

        <!-- Proyecciones Futuras (Markov) -->
        <div class="bg-brand-dark p-4 rounded-lg border border-brand-border">
            <h3 class="text-xl font-semibold text-white mb-3">${future_projections.title}</h3>
            <div class="space-y-2">${futureProjectionsHTML}</div>
        </div>
    `;
    
    DOMElements.resultsContent.innerHTML = contentHTML;
}

/**
 * Resetea la UI a su estado inicial.
 */
function resetUI() {
    DOMElements.fileInput.value = ''; 
    DOMElements.previewImg.src = '';
    setUIState('initial');
}
