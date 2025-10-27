// shap_report.js
// Renderiza el informe detallado a partir de query params: plot (URL al JSON), explanation, decision, probabilities

function q(name){
  return decodeURIComponent((new URLSearchParams(window.location.search)).get(name) || '');
}

async function renderReport(){
  const plotUrl = q('plot');
  const explanation = q('explanation');
  const decision = q('decision');
  const mal = q('maligno');
  const ben = q('benigno');

  const summary = document.getElementById('summary');
  summary.innerHTML = `
    <div class="flex justify-between items-center">
      <div>
        <h3 class="text-lg font-semibold">Decisión del modelo: <span class="ml-2">${decision || 'N/A'}</span></h3>
        <p class="text-sm text-gray-300 mt-1">Probabilidades — Maligno: <strong>${(parseFloat(mal)||0).toFixed(3)}</strong>, Benigno: <strong>${(parseFloat(ben)||0).toFixed(3)}</strong></p>
      </div>
    </div>
    <p class="text-sm text-gray-300 mt-3">${explanation || 'Sin explicación disponible.'}</p>
  `;

  // Load plot JSON and render
  if (plotUrl) {
    try {
      const res = await fetch(plotUrl);
      const fig = await res.json();
      // fig should have .data and .layout
      Plotly.newPlot('plotlyReport', fig.data, fig.layout, {responsive:true});
    } catch (err){
      console.error('No se pudo cargar el plot JSON', err);
      document.getElementById('plotlyReport').textContent = 'Error cargando la visualización interactiva.';
    }
  }

  // Steps: generate generic step-by-step guidance
  const steps = [];
  steps.push('1. Se cargó la imagen y se preprocesó a tamaño 224×224 para el modelo.');
  steps.push('2. El modelo calculó probabilidades para cada clase.');
  steps.push('3. Se generó un mapa SHAP que estima la contribución local de cada píxel/característica al resultado.');
  steps.push('4. El punto de mayor importancia se muestra en la visualización; las áreas más brillantes/rojas son las que más influyeron.');
  steps.push('5. Recomendación: si la decisión es "indeterminado" o te parece incorrecta, recorta la lesión y vuelve a subirla, o consulta un profesional.');

  const list = document.getElementById('stepList');
  list.innerHTML = steps.map(s=>`<li>${s}</li>`).join('');
}

document.addEventListener('DOMContentLoaded', renderReport);
