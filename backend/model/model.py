import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
import logging


IMG_SHAPE = (224,224,3)
NUM_CLASSES = 1 # numero de neuronas de salida 

# creamos el logging 
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
        # 1. Cargar el modelo base pre-entrenado
        base_model = ResNet50(
            input_shape=IMG_SHAPE,
            include_top=False,
            weights='imagenet'
        )

        # 2. Congelar las capas del modelo base
        base_model.trainable = False

        # 3. Añadir cabeza de clasificación personalizada
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(1024, activation='relu')(x) # Capa densa adicional
        predictions = Dense(NUM_CLASSES, activation='sigmoid')(x)

        # 4. Construir el modelo final
        model = Model(inputs=base_model.input, outputs=predictions)

        logging.info("Modelo creado exitosamente.")
        return model, None

    except Exception as e:
        error_message = f"Error al crear el modelo: {e}"
        logging.error(error_message)
        return None, error_message


