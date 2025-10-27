#!/usr/bin/env python3
"""
Herramienta de diagnóstico rápida.
Cargas:
 - backend.model.model.load_trained_model
 - backend.model.predict.preprocess_image
 - backend.model.predict.generate_shap_image

Uso:
 python tools\predict_debug.py --image uploads\imagen_piel1.png
"""
import argparse
import os
import logging
import numpy as np

# Ajustar path si es necesario (ejecutar desde repo root debería funcionar)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', required=True, help='Ruta a la imagen a diagnosticar')
    parser.add_argument('--save-shap', action='store_true', help='Intentar generar y guardar JSON SHAP')
    args = parser.parse_args()

    img_path = args.image
    if not os.path.exists(img_path):
        logging.error('Imagen no encontrada: %s', img_path)
        return

    # Importar dinámicamente para evitar problemas si tensorflow no está cargado
    from backend.model.model import load_trained_model
    from backend.model.predict import preprocess_image, generate_shap_image, LOW_THRESHOLD, HIGH_THRESHOLD

    logging.info('Cargando modelo...')
    model, class_names = load_trained_model()
    if model is None:
        logging.error('No se pudo cargar el modelo.')
        return
    logging.info('Modelo cargado. class_names=%s', class_names)

    logging.info('Preprocesando imagen...')
    preprocessed, original, err = preprocess_image(img_path)
    if err:
        logging.error('Error en preprocesado: %s', err)
        return

    logging.info('Ejecutando inferencia...')
    try:
        preds = model.predict(preprocessed)
        preds = np.asarray(preds).ravel()
        logging.info('raw preds: %s', preds)
    except Exception as e:
        logging.exception('Error durante predict: %s', e)
        return

    if preds.size == 0:
        logging.error('Salida vacía del modelo')
        return
    prob_malignant = float(preds[0])
    prob_benign = 1.0 - prob_malignant
    logging.info('Prob malignant: %0.6f, benign: %0.6f', prob_malignant, prob_benign)

    # Aplicar la regla de decisión actual (consistente con predict.py)
    if prob_malignant >= 0.96 or prob_malignant <= 0.04:
        decision = 'maligno' if prob_malignant >= 0.96 else 'benigno'
    elif prob_malignant >= HIGH_THRESHOLD:
        decision = 'maligno'
    elif prob_malignant <= LOW_THRESHOLD:
        decision = 'benigno'
    else:
        decision = 'indeterminado'

    logging.info('Decision label: %s', decision)

    if args.save_shap:
        try:
            os.makedirs('static/shap', exist_ok=True)
            base_name = os.path.splitext(os.path.basename(img_path))[0]
            out = os.path.join('static/shap', f'debug_shap_{base_name}.json')
            logging.info('Intentando generar SHAP JSON en %s', out)
            # Llama a generate_shap_image: acepta (shap_values, image_original, output_path)
            # Necesitamos un explainer: reutilizamos el code de predict.py para crear explainer si disponible
            from backend.model.predict import explainer, load_model_resources
            # Si explainer es None, intentamos inicializarlo
            if explainer is None:
                try:
                    # Inicializar resources
                    load_model_resources(model, class_names)
                except Exception:
                    logging.exception('No se pudo inicializar explainer')
            # Ahora intentar obtener explainer y calcular shap_values
            from backend.model.predict import explainer as expl
            if expl is None:
                logging.warning('Explainer no disponible; no se generará SHAP')
            else:
                shap_values = expl.shap_values(preprocessed)
                _, err = generate_shap_image(shap_values, original, out)
                if err:
                    logging.error('Error al generar SHAP: %s', err)
                else:
                    logging.info('SHAP JSON guardado en: %s', out)
        except Exception:
            logging.exception('Fallo al generar SHAP')

    logging.info('Diagnóstico completo')

if __name__ == '__main__':
    main()
