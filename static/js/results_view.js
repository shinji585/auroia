/**
 * results_view.js
 * Maneja la visualización de resultados y gráficos interactivos
 */

function displayResults(data) {
    const resultsContainer = document.getElementById('resultsContent');
    
    if (data.status === 'error') {
        showErrorState(data.message);
        return;
    }

    // Limpiar contenedor de resultados
    resultsContainer.innerHTML = '';

    // Crear contenedor principal
    const resultCard = document.createElement('div');
    resultCard.className = 'bg-brand-dark-secondary border border-brand-border rounded-lg p-6 space-y-6';

    // Diagnóstico Principal
    const mainDiagnosis = data.prediction.main_diagnosis;
    const confidence = mainDiagnosis.confidence * 100;
    const isMalignant = mainDiagnosis.name === 'maligno';
    
    // Preferir la etiqueta de decisión del backend (maligno/benigno/indeterminado)
    const decision = data.prediction.decision || null;
    let riskLevel, riskClass, recommendation;
    if (decision === 'maligno') {
        riskLevel = "Alto Riesgo";
        riskClass = 'text-red-500';
        recommendation = "Se recomienda consultar a un dermatólogo inmediatamente.";
    } else if (decision === 'benigno') {
        riskLevel = "Probablemente Benigno";
        riskClass = 'text-green-500';
        recommendation = "Parece ser una lesión benigna, pero mantenga un monitoreo regular.";
    } else if (decision === 'indeterminado') {
        riskLevel = "Indeterminado";
        riskClass = 'text-yellow-500';
        recommendation = "La confianza está en un rango intermedio. Por favor recorta la lesión (centrar y acercar) y vuelva a subir la imagen, o consulte un profesional para una evaluación detallada.";
    } else {
        // Fallback a comportamiento anterior basado en confianza
        if (confidence > 90) {
            riskLevel = isMalignant ? "Alto Riesgo" : "Muy Probablemente Benigno";
            riskClass = isMalignant ? "text-red-500" : "text-green-500";
            recommendation = isMalignant ? 
                "Se recomienda consultar a un dermatólogo inmediatamente." :
                "Parece ser una lesión benigna, pero mantenga un monitoreo regular.";
        } else if (confidence > 70) {
            riskLevel = isMalignant ? "Riesgo Moderado" : "Probablemente Benigno";
            riskClass = isMalignant ? "text-orange-500" : "text-green-400";
            recommendation = "Se recomienda una evaluación profesional para mayor seguridad.";
        } else {
            riskLevel = "Resultado No Concluyente";
            riskClass = "text-yellow-500";
            recommendation = "Se requieren más análisis o mejores imágenes para un diagnóstico preciso.";
        }
    }

    const diagnosisHTML = `
        <div class="text-center mb-6">
            <h2 class="text-2xl font-bold mb-2 ${riskClass}">${riskLevel}</h2>
            <div class="text-lg mb-4">
                Nivel de Confianza: <span class="font-semibold">${confidence.toFixed(1)}%</span>
            </div>
            <p class="text-brand-light">${recommendation}</p>
        </div>

        <div class="grid grid-cols-2 gap-4 mb-6">
            <div class="bg-brand-dark p-4 rounded-lg">
                <h3 class="text-sm text-gray-400 mb-1">Probabilidad Benigno</h3>
                <div class="text-xl font-semibold text-green-500">
                    ${(data.prediction.differential_diagnoses[0].confidence * 100).toFixed(1)}%
                </div>
            </div>
            <div class="bg-brand-dark p-4 rounded-lg">
                <h3 class="text-sm text-gray-400 mb-1">Probabilidad Maligno</h3>
                <div class="text-xl font-semibold text-red-500">
                    ${(mainDiagnosis.confidence * 100).toFixed(1)}%
                </div>
            </div>
        </div>

        <div class="bg-brand-dark p-4 rounded-lg mb-4">
            <h3 class="text-lg font-semibold mb-3">Observaciones Importantes</h3>
            <ul class="list-disc list-inside space-y-2 text-brand-light">
                <li>Este es un análisis preliminar asistido por IA</li>
                <li>No reemplaza el diagnóstico profesional</li>
                <li>Consulte siempre con un dermatólogo certificado</li>
                <li>Mantenga un registro fotográfico de cambios en la piel</li>
            </ul>
        </div>
    `;

    resultCard.innerHTML = diagnosisHTML;

    // Agregar visualización SHAP si está disponible
    if (data.prediction.shap_plot_url) {
        const shapAnalysis = document.createElement('div');
        shapAnalysis.className = 'mt-6';
        shapAnalysis.innerHTML = `
            <h3 class="text-lg font-semibold mb-3">Análisis Visual de Características</h3>
            <div class="bg-brand-dark p-4 rounded-lg">
                <div id="plotlyVisualization"></div>
                <p class="text-sm text-gray-400 mt-2" id="shapExplanation">
                    Este gráfico muestra las áreas de la imagen que más influyeron en el diagnóstico.
                    Las zonas más brillantes indican características importantes para el análisis.
                </p>
            </div>
        `;
        resultCard.appendChild(shapAnalysis);

        // Cargar visualización Plotly si está disponible
        if (typeof Plotly !== 'undefined') {
            fetch(data.prediction.shap_plot_url)
                .then(response => response.json())
                .then(plotData => {
                    Plotly.newPlot('plotlyVisualization', plotData.data, plotData.layout, {responsive: true});
                })
                .catch(error => {
                    console.error('Error cargando la visualización:', error);
                });
            // Si el backend devolvió una explicación textual, mostrarla
            if (data.prediction.explanation) {
                const explEl = document.getElementById('shapExplanation');
                if (explEl) explEl.textContent = data.prediction.explanation;
            }
        }
    }

        // Botón para abrir informe detallado (nueva página)
        if (data.prediction.shap_plot_url) {
            const btnWrap = document.createElement('div');
            btnWrap.className = 'mt-4';
            const params = new URLSearchParams();
            params.set('plot', data.prediction.shap_plot_url);
            params.set('explanation', data.prediction.explanation || '');
            params.set('decision', data.prediction.decision || '');
            params.set('maligno', data.prediction.probabilities?.maligno || '');
            params.set('benigno', data.prediction.probabilities?.benigno || '');
            const href = `/shap_report.html?${params.toString()}`;
            btnWrap.innerHTML = `<a href="${href}" target="_blank" class="inline-block px-4 py-2 bg-brand-blue text-white rounded-md font-semibold">Ver informe detallado</a>`;
            resultCard.appendChild(btnWrap);
        }

    resultsContainer.appendChild(resultCard);
    resultsContainer.classList.remove('hidden');
}

// Exportar las funciones que necesitamos
window.displayResults = displayResults;