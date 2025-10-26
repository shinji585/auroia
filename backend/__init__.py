"""
Archivo principal de la aplicación Flask.
"""
import os
import logging
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
from .model.predict import load_model_resources, make_prediction

# --- Configuración de Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Constantes ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'dcm'}
MODEL_PATH = 'backend/model/model.h5'

# Nombres de las clases que el modelo puede predecir
CLASS_NAMES = [
    "Atelectasia",
    "Cardiomegalia",
    "Derrame Pleural",
    "Infiltración",
    "Masa",
    "Nódulo",
    "Neumonía",
    "Neumotórax",
    "Normal"
]

def create_app():
    """Crea y configura una instancia de la aplicación Flask."""
    app = Flask(__name__, static_folder='../src/static', template_folder='../src')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['SECRET_KEY'] = 'tu_super_secreto_aqui' # Cambiar en producción

    # Crear el directorio de subidas si no existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # --- Carga del Modelo al iniciar ---
    try:
        logging.info("Cargando modelo de Keras...")
        model = load_model(MODEL_PATH)
        logging.info("Modelo cargado exitosamente. Inicializando recursos...")
        # Carga el modelo y el explainer en la memoria para un acceso rápido
        load_model_resources(model, CLASS_NAMES)
    except Exception as e:
        logging.error(f"Error fatal al cargar el modelo: {e}")
        # Si el modelo no se carga, la aplicación no puede funcionar.
        # Podríamos manejar esto de forma más elegante, pero por ahora es un punto crítico.
        model = None

    def allowed_file(filename):
        """Verifica si la extensión del archivo es válida."""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    # --- Rutas de la Aplicación ---
    @app.route('/')
    def index():
        """Sirve la página principal de la aplicación."""
        return render_template('index.html')

    @app.route('/about')
    def about():
        """Sirve la página 'Sobre el proyecto'."""
        return render_template('about.html')

    @app.route('/api/predict', methods=['POST'])
    def predict():
        """Recibe una imagen y devuelve una predicción del modelo."""
        if model is None:
            logging.warning("Se recibió una solicitud de predicción, pero el modelo no está cargado.")
            return jsonify({"status": "error", "message": "El modelo de IA no está disponible."}), 500
            
        # Verificar si se envió un archivo
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No se encontró el archivo en la solicitud."}), 400
        
        file = request.files['file']
        
        # Verificar si el archivo tiene un nombre
        if file.filename == '':
            return jsonify({"status": "error", "message": "No se seleccionó ningún archivo."}), 400
            
        # Verificar si el archivo es del tipo permitido
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                file.save(filepath)
                logging.info(f"Archivo guardado en: {filepath}")
                
                # Realizar la predicción con la nueva lógica
                prediction_result = make_prediction(filepath)
                
                return jsonify(prediction_result)

            except Exception as e:
                logging.error(f"Error al procesar el archivo {filename}: {e}")
                return jsonify({"status": "error", "message": f"Error interno al procesar el archivo: {e}"}), 500
        else:
            return jsonify({"status": "error", "message": "Tipo de archivo no permitido."}), 400

    return app
