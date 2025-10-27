# pyright: reportMissingImports=false
"""
Este módulo contiene la lógica para realizar predicciones usando el modelo de IA.
"""
import os
import logging
import numpy as np
import tensorflow as tf
from tensorflow import keras # type: ignore
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input
import shap
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# --- Configuración de Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Variables Globales ---
model = None
explainer = None
class_names = None
# Umbrales para mejorar la UX y reducir falsas alarmas sin retrenar el modelo.
# Si la probabilidad de malignidad está por encima de HIGH_THRESHOLD -> 'maligno'
# si está por debajo de LOW_THRESHOLD -> 'benigno'
# en el intervalo intermedio -> 'indeterminado' (sugerir recorte/crop o evaluación humana)
LOW_THRESHOLD = 0.3
HIGH_THRESHOLD = 0.7

def load_model_resources(loaded_model, app_class_names):
    """
    Inicializa el modelo, el explicador SHAP y los nombres de las clases.
    Esta función es llamada una vez al inicio de la aplicación.
    """
    global model, explainer, class_names
    model = loaded_model
    class_names = app_class_names

    # Crear fondo simple (imágenes negras) con la forma correcta
    # model.input_shape puede ser (None, H, W, C)
    try:
        _, h, w, c = model.input_shape
    except Exception:
        # Fallback a 224x224x3
        h, w, c = 224, 224, 3

    background = np.zeros((1, h, w, c), dtype=np.float32)

    # Inicializar el explicador SHAP usando directamente el modelo Keras.
    # GradientExplainer espera típicamente un objeto de modelo compatible
    # (por ejemplo, tf.keras.Model). Pasar el modelo cargado evita errores
    # internos al intentar inferir la firma desde un wrapper de función.
    try:
        explainer = shap.GradientExplainer(model, background)
    except Exception as e:
        # Si SHAP no acepta el modelo directamente por versión o firma,
        # intentar crear el explicador sin crash y dejar explainer=None.
        logging.warning(f"No se pudo inicializar GradientExplainer con el modelo: {e}")
        explainer = None
    
    logging.info("Recursos del modelo (modelo, explicador SHAP) cargados exitosamente.")

def preprocess_image(img_path):
    """
    Carga y pre-procesa una imagen para que sea compatible con el modelo.
    """
    try:
        # Verificar existencia del archivo
        if not os.path.exists(img_path):
            raise FileNotFoundError(f"No se encontró el archivo: {img_path}")

        # Cargar y convertir a RGB
        img = image.load_img(img_path, target_size=(224, 224), color_mode='rgb')
        logging.info(f"Imagen cargada correctamente: {img_path}")

        # Convertir a array
        img_array = image.img_to_array(img)
        logging.info(f"Forma del array de imagen: {img_array.shape}")

        # Validar dimensiones
        if img_array.shape != (224, 224, 3):
            raise ValueError(f"Dimensiones incorrectas de imagen: {img_array.shape}")

        # Guardar copia original (uint8) para visualizaciones
        original_img = img_array.astype(np.uint8)

        # Preprocesar para ResNet50
        from tensorflow.keras.applications.resnet50 import preprocess_input
        img_array_expanded = np.expand_dims(img_array, axis=0)
        preprocessed_img = preprocess_input(img_array_expanded)

        logging.info("Preprocesamiento completado exitosamente")
        # Devolver la imagen preprocesada y la original para uso en visualizaciones
        return preprocessed_img, original_img, None

    except Exception as e:
        error_message = f"Error al pre-procesar la imagen: {str(e)}"
        logging.error(error_message)
        return None, None, error_message

def generate_shap_image(shap_values, image_original, output_path):
    """
    Genera y guarda una visualización interactiva de SHAP usando Plotly.
    """
    try:
        # La salida de GradientExplainer es una lista de arrays
        shap_values_single = shap_values[0][0]
        # image_original is expected to be an HxWx3 uint8 numpy array
        
        # Crear un subplot con dos imágenes lado a lado
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Imagen Original', 'Áreas de Interés (SHAP)'),
            horizontal_spacing=0.1
        )
        
        # Imagen original
        fig.add_trace(
            go.Image(z=image_original, name='Original'),
            row=1, col=1
        )
        
        # Mapa de calor SHAP
        shap_heatmap = np.sum(np.abs(shap_values_single), axis=-1)
        max_abs_val = np.max(np.abs(shap_heatmap))
        
        fig.add_trace(
            go.Heatmap(
                z=shap_heatmap,
                colorscale='RdBu',
                zmid=0,
                zmin=-max_abs_val,
                zmax=max_abs_val,
                showscale=True,
                colorbar=dict(
                    title='Importancia',
                    titleside='right',
                    thickness=15,
                    len=0.7
                ),
                name='Análisis SHAP'
            ),
            row=1, col=2
        )
        
        # Configurar el diseño
        fig.update_layout(
            title={
                'text': 'Análisis Visual de Características',
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': dict(size=20)
            },
            height=600,
            width=1000,
            showlegend=True,
            plot_bgcolor='rgb(13, 17, 23)',
            paper_bgcolor='rgb(13, 17, 23)',
            font=dict(color='rgb(205, 213, 224)'),
            margin=dict(l=40, r=40, t=60, b=40)
        )
        
        # Actualizar los ejes
        fig.update_xaxes(showgrid=False, zeroline=False)
        fig.update_yaxes(showgrid=False, zeroline=False)
        
        # Guardar como JSON para Plotly
        plot_json = fig.to_json()
        with open(output_path, 'w') as f:
            f.write(plot_json)
        
        logging.info(f"Visualización SHAP guardada como JSON en {output_path}")
        return output_path, None
    except Exception as e:
        error_message = f"Error al generar la imagen SHAP: {e}"
        logging.error(error_message)
        return None, error_message

def make_prediction(img_path):
    """
    Realiza una predicción sobre una imagen y devuelve un resultado en formato JSON estructurado.
    """
    logging.info(f"Iniciando predicción para imagen: {img_path}")
    
    # 1. Verificar si el modelo se cargó correctamente
    if not model:
        error_msg = "El modelo no está disponible."
        logging.error(error_msg)
        return {"status": "error", "message": error_msg}

    # Verificar si es una imagen válida antes de intentar procesarla
    if not os.path.exists(img_path):
        return {"status": "error", "message": "Archivo no encontrado"}

    # 2. Pre-procesar la imagen de entrada
    processed_image, original_img, error = preprocess_image(img_path)
    if error:
        return {"status": "error", "message": error}

    # 3. Realizar la predicción
    try:
        preds = model.predict(processed_image)
        preds = np.asarray(preds).ravel()
        logging.info(f"Raw model prediction output shape: {preds.shape}")
    except Exception as e:
        error_message = f"Error durante la inferencia del modelo: {e}"
        logging.exception(error_message)
        return {"status": "error", "message": error_message}
        
    # 4. Estructurar los resultados
    # Como es un modelo binario con una sola salida sigmoid, interpretamos:
    # predictions[0] es la probabilidad de que sea maligno
    if preds.size == 0:
        return {"status": "error", "message": "El modelo devolvió una salida vacía."}

    prob_malignant = float(preds[0])
    prob_benign = 1.0 - prob_malignant

    results = [
        {"name": "maligno", "confidence": prob_malignant},
        {"name": "benigno", "confidence": prob_benign}
    ]
    # Ordenar los resultados por confianza de mayor a menor
    results.sort(key=lambda x: x['confidence'], reverse=True)

    main_diagnosis = results[0]
    differential_diagnoses = results[1:]

    # Decisión basada en umbrales y probabilidad absoluta
    if prob_malignant >= 0.96 or prob_malignant <= 0.04:  # Confianza muy alta
        decision_label = 'maligno' if prob_malignant >= 0.96 else 'benigno'
    elif prob_malignant >= HIGH_THRESHOLD:  # Usar umbrales normales para otros casos
        decision_label = 'maligno'
    elif prob_malignant <= LOW_THRESHOLD:
        decision_label = 'benigno'
    else:
        decision_label = 'indeterminado'

    # 5. Generar explicabilidad SHAP
    try:
        if explainer is None:
            logging.warning("Explainer SHAP no inicializado; omitiendo explicación SHAP.")
            shap_plot_url = None
            reason_text = "No se generó explicación SHAP (recurso no inicializado)."
        else:
            shap_values = explainer.shap_values(processed_image) # type: ignore
            # Asegurarse de que la carpeta de salida exista
            os.makedirs("static/shap", exist_ok=True)
            # Usar el nombre base del archivo sin extensión para evitar duplicados
            base_name = os.path.splitext(os.path.basename(img_path))[0]
            shap_filename = f"shap_{base_name}.json"
            shap_output_path = os.path.join("static/shap", shap_filename)

            # Generar y guardar la visualización Plotly (JSON)
            plot_path, plot_err = generate_shap_image(shap_values, original_img, shap_output_path)
            if plot_err:
                logging.warning(f"No se pudo generar la visualización SHAP interactiva: {plot_err}")

            # Devolver la ruta relativa para el frontend (JSON para Plotly)
            shap_plot_url = f"/static/shap/{shap_filename}"

            # Construir una explicación textual breve basada en el mapa SHAP
            try:
                # shap_values_single: [height, width, channels]
                shap_values_single = shap_values[0][0]
                shap_heatmap = np.mean(np.abs(shap_values_single), axis=-1)
                # Localizar el punto de mayor importancia
                max_idx = np.unravel_index(np.argmax(shap_heatmap), shap_heatmap.shape)
                max_value = float(shap_heatmap[max_idx])
                # Normalizar por el promedio para dar contexto
                mean_val = float(np.mean(shap_heatmap))
                ratio = max_value / (mean_val + 1e-8)
                coord_text = f"en la región aproximada (fila={int(max_idx[0])}, col={int(max_idx[1])})"
                importance_text = f"valor SHAP máximo {max_value:.3f} (≈{ratio:.1f}× el promedio)"
                if main_diagnosis['name'] == 'maligno':
                    reason_text = f"El modelo favorece 'maligno' porque detectó características relevantes {coord_text} con {importance_text}."
                else:
                    reason_text = f"El modelo favorece 'benigno' porque las contribuciones locales son bajas; punto de mayor importancia {coord_text} con {importance_text}."
            except Exception as ex:
                logging.warning(f"No se pudo extraer explicación textual de SHAP: {ex}")
                reason_text = "No se pudo generar una explicación textual de SHAP." 
    except Exception as e:
        # No falle el endpoint si SHAP da error; devolver resultado sin SHAP
        error_message = f"Error durante la generación de SHAP: {e}"
        logging.exception(error_message)
        shap_plot_url = None
        reason_text = "No se pudo generar explicación SHAP debido a un error interno." 

    # 6. Ensamblar la respuesta final en el formato JSON solicitado
    final_response = {
        "status": "success",
        "prediction": {
            "main_diagnosis": main_diagnosis,
            "differential_diagnoses": differential_diagnoses,
            "shap_plot_url": shap_plot_url,
            "explanation": reason_text,
            "decision": decision_label,
            "probabilities": {
                "maligno": prob_malignant,
                "benigno": prob_benign
            }
        }
    }
    
    return final_response
