
import tensorflow as tf
import os
import logging
from backend.model.model import create_model
from backend.model.predict import MODEL_WEIGHTS_PATH

# --- Configuración y Constantes ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Directorio base donde se encuentran las carpetas 'train' y 'validation'
DATA_DIR = 'data/'

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
        logging.error("Por favor, crea la estructura de carpetas esperada: data/train/benign, data/train/malignant, etc.")
        return

    # 2. Generadores de Datos (Data Augmentation y Carga)
    # ImageDataGenerator nos permite cargar imágenes desde directorios y aplicar transformaciones.
    # La aumentación de datos (rotación, zoom, etc.) en el set de entrenamiento
    # ayuda al modelo a generalizar mejor y a no sobreajustarse.
    train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
        rescale=1./255,
        rotation_range=40,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )

    # Para el set de validación, solo necesitamos re-escalar los píxeles.
    # No aplicamos aumentación para obtener una métrica real del rendimiento.
    validation_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255)

    # Flujo de imágenes desde los directorios
    train_generator = train_datagen.flow_from_directory(
        os.path.join(DATA_DIR, 'train'),
        target_size=(IMG_SHAPE[0], IMG_SHAPE[1]),
        batch_size=BATCH_SIZE,
        class_mode='binary' # Porque es clasificación binaria (benigno/maligno)
    )

    validation_generator = validation_datagen.flow_from_directory(
        os.path.join(DATA_DIR, 'validation'),
        target_size=(IMG_SHAPE[0], IMG_SHAPE[1]),
        batch_size=BATCH_SIZE,
        class_mode='binary'
    )

    # 3. Creación y Compilación del Modelo
    model, error = create_model()
    if error:
        logging.error(f"No se pudo crear el modelo. Abortando entrenamiento. Error: {error}")
        return

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
        loss='binary_crossentropy', # Ideal para clasificación binaria
        metrics=['accuracy']
    )

    logging.info("Modelo compilado exitosamente. Iniciando entrenamiento...")

    # 4. Entrenamiento del Modelo
    history = model.fit(
        train_generator,
        epochs=EPOCHS,
        validation_data=validation_generator,
        steps_per_epoch=train_generator.samples // BATCH_SIZE, # Pasos por época
        validation_steps=validation_generator.samples // BATCH_SIZE
    )

    logging.info("Entrenamiento completado.")

    # 5. Guardado de los Pesos del Modelo
    try:
        model.save_weights(MODEL_WEIGHTS_PATH)
        logging.info(f"Los pesos del modelo han sido guardados exitosamente en: {MODEL_WEIGHTS_PATH}")
    except Exception as e:
        logging.error(f"Ocurrió un error al guardar los pesos del modelo: {e}")


if __name__ == '__main__':
    run_training()
