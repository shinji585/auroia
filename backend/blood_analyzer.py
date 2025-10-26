"""
Modulo para el analisis de datos de sangre y prediccion de enfermedades futuras.
"""
import random
import json

# Base de conocimiento simple para la interpretacion de analisis de sangre
# En un caso real, esto vendria de una base de datos o una fuente mas robusta.
KNOWLEDGE_BASE = {
    'red_blood_cells': {'range': (4.5, 5.9), 'unit': 'millones/mcL'},
    'white_blood_cells': {'range': (4500, 11000), 'unit': 'células/mcL'},
    'platelets': {'range': (150000, 450000), 'unit': 'por mcL'},
    'hemoglobin': {'range': (13.5, 17.5), 'unit': 'g/dL'},
    'glucose': {'range': (70, 100), 'unit': 'mg/dL'},
    'bacteria_presence': {'range': (0, 0), 'unit': ''} # 0 = Ausente, 1 = Presente
}

DISEASE_PATTERNS = {
    "Anemia": lambda d: d['hemoglobin'] < KNOWLEDGE_BASE['hemoglobin']['range'][0],
    "Infeccion Bacteriana": lambda d: d['white_blood_cells'] > KNOWLEDGE_BASE['white_blood_cells']['range'][1] or d.get('bacteria_presence', 0) == 1,
    "Riesgo de Trombosis": lambda d: d['platelets'] > KNOWLEDGE_BASE['platelets']['range'][1],
    "Pre-diabetes": lambda d: d['glucose'] > 100 and d['glucose'] <= 125,
    "Posible Diabetes": lambda d: d['glucose'] > 125
}

# Modelo de Transicion de Estados (Simulacion de Cadenas de Markov)
# (Estado Actual) -> [(Estado Futuro, Probabilidad), ...]
MARKOV_TRANSITIONS = {
    'Normal': [('Normal', 0.95), ('Pre-diabetes', 0.04), ('Anemia', 0.01)],
    'Anemia': [('Anemia', 0.80), ('Normal', 0.20)],
    'Infeccion Bacteriana': [('Normal', 0.90), ('Riesgo de Trombosis', 0.10)], # Asumiendo tratamiento
    'Pre-diabetes': [('Pre-diabetes', 0.70), ('Posible Diabetes', 0.20), ('Normal', 0.10)],
    'Posible Diabetes': [('Posible Diabetes', 0.90), ('Riesgo de Trombosis', 0.10)],
    'Riesgo de Trombosis': [('Riesgo de Trombosis', 0.85), ('Normal', 0.15)],
}

def analyze_blood_data(file_content):
    """
    Analiza los datos de un archivo de analisis de sangre (JSON) y devuelve un informe estructurado.
    """
    try:
        data = json.loads(file_content)
    except json.JSONDecodeError:
        return {"status": "error", "message": "El archivo no es un JSON válido."}

    # 1. Analisis del Estado Actual
    current_anomalies = []
    report_details = []
    for key, values in KNOWLEDGE_BASE.items():
        if key in data:
            val = data[key]
            lower, upper = values['range']
            status = "Normal"
            if val < lower:
                status = "Bajo"
                current_anomalies.append(key)
            elif val > upper:
                status = "Alto"
                current_anomalies.append(key)
            report_details.append(f"{key.replace('_', ' ').title()}: {val} {values['unit']} (Estado: {status})")

    # 2. Diagnostico Basado en Patrones
    current_diagnoses = []
    for disease, check_func in DISEASE_PATTERNS.items():
        if check_func(data):
            current_diagnoses.append(disease)

    if not current_diagnoses:
        current_diagnoses.append("Normal")

    # 3. Prediccion Futura (Simulacion de Markov)
    primary_state = current_diagnoses[0] # Usamos el primer diagnostico como estado primario
    future_projections = []
    if primary_state in MARKOV_TRANSITIONS:
        # Simular una transicion
        transitions = MARKOV_TRANSITIONS[primary_state]
        states, probabilities = zip(*transitions)
        # Elegimos un estado futuro basado en las probabilidades
        # En una app real, devolveriamos las probabilidades, pero aqui simulamos un camino
        # next_state = random.choices(states, weights=probabilities, k=1)[0]
        future_projections = [{"state": s, "probability": p} for s, p in transitions]

    # 4. Ensamblar la respuesta
    response = {
        "status": "success",
        "analysis_type": "blood_analysis",
        "report": {
            "title": "Informe de Análisis de Sangre",
            "details": "\n".join(report_details),
            "current_diagnoses": current_diagnoses,
            "future_projections": {
                "title": f"Proyección a 1 año basada en el estado '{primary_state}'",
                "projections": future_projections
            }
        }
    }
    
    return response
