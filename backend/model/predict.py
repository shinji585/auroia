"""
Este módulo contiene la lógica para realizar predicciones usando el modelo de IA.
"""
import os
import logging
import numpy as np
from tensorflow.keras.preprocessing import image
import shap
import matplotlib.pyplot as plt

# --- Configuración de Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Variables Globales ---
model = None
explainer = None
class_names = None

def load_model_resources(loaded_model, app_class_names):
    """
    Inicializa el modelo, el explicador SHAP y los nombres de las clases.
    Esta función es llamada una vez al inicio de la aplicación.
    """
    global model, explainer, class_names
    model = loaded_model
    class_names = app_class_names
    
    # Creamos un explicador SHAP. Los explainer de gradiente son una buena opción para modelos de Deep Learning.
    # El explainer necesita un conjunto de datos de fondo para calcular las expectativas. 
    # Usar un pequeño conjunto de imágenes negras es una aproximación común cuando no se tiene un conjunto de datos de fondo representativo a mano.
    background = np.zeros((1, model.input_shape[1], model.input_shape[2], model.input_shape[3]))
    explainer = shap.GradientExplainer(model, background)
    
    logging.info("Recursos del modelo (modelo, explicador SHAP) cargados exitosamente.")

def preprocess_image(img_path):
    """
    Carga y pre-procesa una imagen para que sea compatible con el modelo.
    """
    try:
        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array_expanded = np.expand_dims(img_array, axis=0)
        return img_array_expanded / 255., None
    except Exception as e:
        error_message = f"Error al pre-procesar la imagen: {e}"
        logging.error(error_message)
        return None, error_message

def generate_shap_image(shap_values, processed_image, output_path):
    """
    Genera y guarda una imagen de superposición de SHAP.
    """
    try:
        # La salida de GradientExplainer es una lista de arrays (uno por salida del modelo). 
        # Tomamos el primero. Las dimensiones son [batch, height, width, channels].
        shap_values_single = shap_values[0][0]
        
        # Obtenemos la imagen original para la visualización
        image_original = processed_image[0]

        # Crear la visualización de SHAP
        # plot_top_features=False para evitar que se redimensionen los ejes.
        fig, ax = plt.subplots()
        shap.image_plot(
            shap_values=[shap_values_single],
            pixel_values=np.expand_dims(image_original, axis=0),
            show=False,
            matplotlib=True,
            fig=fig,
            ax=ax
        )
        fig.savefig(output_path, bbox_inches='tight', pad_inches=0)
        plt.close(fig)
        
        logging.info(f"Imagen SHAP guardada en {output_path}")
        return output_path, None
    except Exception as e:
        error_message = f"Error al generar la imagen SHAP: {e}"
        logging.error(error_message)
        return None, error_message

def make_prediction(img_path):
    """
    Realiza una predicción sobre una imagen y devuelve un resultado en formato JSON estructurado.
    """
    # 1. Verificar si el modelo se cargó correctamente
    if not model or not explainer or not class_names:
        return {"status": "error", "message": "Los recursos del modelo no están disponibles."}

    # 2. Pre-procesar la imagen de entrada
    processed_image, error = preprocess_image(img_path)
    if error:
        return {"status": "error", "message": error}

    # 3. Realizar la predicción
    try:
        predictions = model.predict(processed_image)[0]
    except Exception as e:
        error_message = f"Error durante la inferencia del modelo: {e}"
        logging.error(error_message)
        return {"status": "error", "message": error_message}
        
    # 4. Estructurar los resultados
    results = [{"name": class_names[i], "confidence": float(predictions[i])} for i in range(len(class_names))]
    # Ordenar los resultados por confianza de mayor a menor
    results.sort(key=lambda x: x['confidence'], reverse=True)

    main_diagnosis = results[0]
    differential_diagnoses = results[1:]

    # 5. Generar explicabilidad SHAP
    try:
        shap_values = explainer.shap_values(processed_image)
        # Asegurarse de que la carpeta de salida exista
        os.makedirs("static/shap", exist_ok=True) 
        shap_image_filename = f"shap_{os.path.basename(img_path)}.png"
        shap_output_path = os.path.join("static/shap", shap_image_filename)
        
        generate_shap_image(shap_values, processed_image, shap_output_path)
        
        # Devolver la ruta relativa para el frontend
        shap_image_url = f"/static/shap/{shap_image_filename}"
        
    except Exception as e:
        error_message = f"Error durante la generación de SHAP: {e}"
        logging.error(error_message)
        return {"status": "error", "message": error_message}

    # 6. Ensamblar la respuesta final en el formato JSON solicitado
    final_response = {
        "status": "success",
        "prediction": {
            "main_diagnosis": main_diagnosis,
            "differential_diagnoses": differential_diagnoses,
            "shap_image_url": shap_image_url
        }
    }
    
    return final_response
