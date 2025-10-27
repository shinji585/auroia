# pyright: reportMissingImports=false
import os
import logging
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Input
from tensorflow.keras import Model

# Configuración básica
IMG_SHAPE = (224, 224, 3)
NUM_CLASSES = 1  # número de neuronas de salida 
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.h5')

# Nombres de las clases para las predicciones
CLASS_NAMES = ['benigno', 'maligno']

# Configuración de logging 
logging.basicConfig(level=logging.INFO)


def create_model():
    """
    Crea un modelo de clasificación de imágenes usando ResNet50 como base.

    Retorna:
        Una tupla. En caso de éxito: (model, None).
        En caso de error: (None, error_message_string).
    """
    try:
        logging.info("Iniciando la creación del modelo...")
        
        # 1. Crear la entrada
        inputs = Input(shape=IMG_SHAPE, name='input_layer')
        
        # 2. Modelo base ResNet50 (pre-entrenado)
        base_model = ResNet50(
            include_top=False,
            weights='imagenet',
            input_shape=IMG_SHAPE
        )
        base_model.trainable = False
        
        # 3. Construir el modelo
        x = base_model(inputs)
        x = GlobalAveragePooling2D(name='gap')(x)
        x = Dense(1024, activation='relu', name='dense_1')(x)
        outputs = Dense(NUM_CLASSES, activation='sigmoid', name='output')(x)
        
        # 4. Crear el modelo final
        model = Model(inputs=inputs, outputs=outputs, name='skin_cancer_model')

        logging.info("Modelo creado exitosamente.")
        return model, None

    except Exception as e:
        error_message = f"Error al crear el modelo: {e}"
        logging.error(error_message)
        return None, error_message

def load_trained_model():
    """
    Carga el modelo entrenado desde el archivo guardado.
    
    Retorna:
        Una tupla (model, class_names) en caso de éxito.
        Una tupla (None, None) en caso de error.
    """
    try:
        if not os.path.exists(MODEL_PATH):
            logging.error(f"No se encontró el modelo en {MODEL_PATH}")
            return None, None
            
        logging.info(f"Cargando modelo desde {MODEL_PATH}...")

        # Cargar el modelo completo guardado (incluye arquitectura y pesos).
        # Esto evita inconsistencias entre la arquitectura esperada y la estructura
        # real del modelo almacenado en el HDF5.
        model = tf.keras.models.load_model(MODEL_PATH)
        # (Opcional) compilar para mantener compatibilidad con .evaluate() o entrenamiento
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        logging.info("Modelo cargado exitosamente usando tf.keras.models.load_model.")

        return model, CLASS_NAMES
        
    except Exception as e:
        logging.error(f"Error al cargar el modelo: {e}")
        return None, None

