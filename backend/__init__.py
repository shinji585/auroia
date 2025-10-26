"""
Archivo principal de la aplicación Flask.
"""
import os
import logging
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model

# Importar los dos tipos de lógica de análisis
from .model.predict import load_model_resources, make_prediction
from .blood_analyzer import analyze_blood_data

# --- Configuración de Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Constantes ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS_IMG = {'png', 'jpg', 'jpeg', 'dcm'}
ALLOWED_EXTENSIONS_DATA = {'json', 'csv'} # Ampliamos para datos
MODEL_PATH = 'backend/model/model.h5'

# Nombres de las clases para el modelo de PIEL (antes pulmonar)
CLASS_NAMES_SKIN = [
    "Benigno",
    "Maligno"
]

def create_app():
    """Crea y configura una instancia de la aplicación Flask."""
    app = Flask(__name__, static_folder='../src/static', template_folder='../src')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['SECRET_KEY'] = 'tu_super_secreto_aqui' # Cambiar en producción

    # Crear el directorio de subidas si no existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # --- Carga del Modelo de Imagen al iniciar ---
    try:
        logging.info("Cargando modelo de Keras para análisis de piel...")
        skin_model = load_model(MODEL_PATH)
        logging.info("Modelo de piel cargado. Inicializando recursos...")
        load_model_resources(skin_model, CLASS_NAMES_SKIN)
    except Exception as e:
        logging.error(f"Error fatal al cargar el modelo de piel: {e}")
        skin_model = None

    def is_file_allowed(filename, analysis_type):
        """Verifica si la extensión del archivo es válida para el tipo de análisis."""
        if not '.' in filename:
            return False
        ext = filename.rsplit('.', 1)[1].lower()
        if analysis_type == 'piel':
            return ext in ALLOWED_EXTENSIONS_IMG
        elif analysis_type == 'sangre':
            return ext in ALLOWED_EXTENSIONS_DATA
        return False

    # --- Rutas de la Aplicación ---
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/api/predict', methods=['POST'])
    def predict():
        """Endpoint unificado para manejar todos los tipos de análisis."""
        # 1. Validar la solicitud
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No se encontró el archivo."}), 400
        
        file = request.files['file']
        analysis_type = request.form.get('analysis_type')

        if not analysis_type or analysis_type not in ['piel', 'sangre']:
            return jsonify({"status": "error", "message": "Tipo de análisis no especificado o inválido."}), 400
            
        if file.filename == '' or not is_file_allowed(file.filename, analysis_type):
            return jsonify({"status": "error", "message": "Archivo no válido o tipo de archivo no permitido para este análisis."}), 400

        # 2. Procesar según el tipo de análisis
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        logging.info(f"Archivo guardado en: {filepath} para análisis de tipo: {analysis_type}")

        try:
            if analysis_type == 'piel':
                if skin_model is None:
                     return jsonify({"status": "error", "message": "El modelo de IA para piel no está disponible."}), 500
                # Llamar a la lógica de predicción de imágenes
                prediction_result = make_prediction(filepath)
                return jsonify(prediction_result)

            elif analysis_type == 'sangre':
                # Leer el contenido del archivo de texto/json
                with open(filepath, 'r') as f:
                    content = f.read()
                # Llamar a la nueva lógica de análisis de sangre
                analysis_result = analyze_blood_data(content)
                return jsonify(analysis_result)

        except Exception as e:
            logging.error(f"Error durante el análisis del archivo {filename}: {e}")
            return jsonify({"status": "error", "message": f"Error interno del servidor: {e}"}), 500

    return app
