
import os
import logging
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator # type: ignore
from tensorflow.keras.optimizers import Adam # type: ignore
from backend.model.model import create_model

# --- Configuración y Constantes ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- CONSTANTES CLAVE ---
# Directorio base donde se encuentran las carpetas 'train' y 'validation'
DATA_DIR = 'data/'
# Ruta donde se guardará el modelo entrenado. Esta es la que la app espera.
MODEL_SAVE_PATH = 'backend/model/model.h5'

# Parámetros del modelo y entrenamiento
IMG_SHAPE = (224, 224, 3)
BATCH_SIZE = 32
EPOCHS = 15 # Número de veces que el modelo verá todo el dataset

def run_training():
    """
    Función principal que ejecuta todo el proceso de entrenamiento del modelo.
    """
    # 1. Verificación del directorio de datos
    if not os.path.isdir(DATA_DIR):
        logging.error(f"El directorio de datos '{DATA_DIR}' no fue encontrado.")
        logging.error("Por favor, crea la estructura de carpetas: data/train/benign, data/train/malignant y data/validation/benign, data/validation/malignant.")
        return

    # 2. Generadores de Datos (Data Augmentation y Carga)
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=40,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )

    validation_datagen = ImageDataGenerator(rescale=1./255)

    try:
        train_generator = train_datagen.flow_from_directory(
            os.path.join(DATA_DIR, 'train'),
            target_size=(IMG_SHAPE[0], IMG_SHAPE[1]),
            batch_size=BATCH_SIZE,
            class_mode='binary'
        )

        validation_generator = validation_datagen.flow_from_directory(
            os.path.join(DATA_DIR, 'validation'),
            target_size=(IMG_SHAPE[0], IMG_SHAPE[1]),
            batch_size=BATCH_SIZE,
            class_mode='binary'
        )
    except FileNotFoundError as e:
        logging.error(f"Error al buscar las carpetas de imágenes: {e}")
        logging.error("Asegúrate de que la estructura 'data/train/[clases]' y 'data/validation/[clases]' existe.")
        return

    # 3. Creación y Compilación del Modelo
    model, error = create_model()
    if error:
        logging.error(f"No se pudo crear el modelo. Abortando entrenamiento. Error: {error}")
        return

    if model is None:
        logging.error("No se pudo crear el modelo")
        return
        
    optimizer = Adam(learning_rate=0.0001)
    model.compile(
        optimizer=optimizer,
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    # Asegurar que el modelo base esté en modo de inferencia
    for layer in model.layers:
        if 'resnet' in layer.name.lower():
            layer.trainable = False

    logging.info("Modelo compilado exitosamente. Iniciando entrenamiento...")

    # 4. Entrenamiento del Modelo
    history = model.fit(
        train_generator,
        epochs=EPOCHS,
        validation_data=validation_generator,
        steps_per_epoch=train_generator.samples // BATCH_SIZE,
        validation_steps=validation_generator.samples // BATCH_SIZE
    )

    logging.info("Entrenamiento completado.")

    # 5. Guardado del Modelo Completo
    try:
        # Asegurarse de que el directorio del modelo exista
        os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
        # Guardar el modelo completo (arquitectura + pesos)
        model.save(MODEL_SAVE_PATH)
        logging.info(f"El modelo completo ha sido guardado exitosamente en: {MODEL_SAVE_PATH}")
    except Exception as e:
        logging.error(f"Ocurrió un error al guardar el modelo: {e}")


if __name__ == '__main__':
    run_training()
