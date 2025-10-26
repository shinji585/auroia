
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration ---
IMG_HEIGHT = 224
IMG_WIDTH = 224
BATCH_SIZE = 32 # Number of images to process in a batch
EPOCHS = 15     # Number of times to iterate over the entire dataset

TRAIN_DIR = 'data/train'
VALIDATION_DIR = 'data/validation'
MODEL_SAVE_PATH = 'backend/model/model.h5'

def create_model():
    """
    Defines and compiles the CNN model architecture.
    """
    model = Sequential([
        # Layer 1: Convolutional layer
        Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)),
        MaxPooling2D(2, 2),

        # Layer 2: Convolutional layer
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D(2, 2),

        # Layer 3: Convolutional layer
        Conv2D(128, (3, 3), activation='relu'),
        MaxPooling2D(2, 2),
        
        # Flatten the results to feed into a dense layer
        Flatten(),
        
        # Dense Layer with Dropout for regularization
        Dense(512, activation='relu'),
        Dropout(0.5),
        
        # Output Layer: 2 neurons for 'benign' and 'malignant'
        # Using 'softmax' for multi-class classification probability distribution
        Dense(2, activation='softmax')
    ])
    
    # Compile the model
    model.compile(optimizer='adam', 
                  loss='categorical_crossentropy', 
                  metrics=['accuracy'])
    
    logging.info("Model created and compiled successfully.")
    model.summary() # Print model summary
    return model

def train_model():
    """
    Trains the model using data from the data/train and data/validation directories.
    """
    # 1. Create Data Generators
    # Rescale pixel values from [0, 255] to [0, 1]
    train_datagen = ImageDataGenerator(rescale=1./255)
    validation_datagen = ImageDataGenerator(rescale=1./255)

    train_generator = train_datagen.flow_from_directory(
        TRAIN_DIR,
        target_size=(IMG_WIDTH, IMG_HEIGHT),
        batch_size=BATCH_SIZE,
        class_mode='categorical' # for categorical_crossentropy
    )

    validation_generator = validation_datagen.flow_from_directory(
        VALIDATION_DIR,
        target_size=(IMG_WIDTH, IMG_HEIGHT),
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )

    # 2. Create and train the model
    model = create_model()

    logging.info("Starting model training...")
    history = model.fit(
        train_generator,
        epochs=EPOCHS,
        validation_data=validation_generator,
        # Steps per epoch = Total Train Images / Batch Size
        steps_per_epoch=train_generator.samples // BATCH_SIZE,
        # Validation Steps = Total Validation Images / Batch Size
        validation_steps=validation_generator.samples // BATCH_SIZE
    )

    logging.info("Model training completed.")

    # 3. Save the trained model
    # Ensure the target directory exists
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    model.save(MODEL_SAVE_PATH)
    logging.info(f"Model saved to {MODEL_SAVE_PATH}")

if __name__ == '__main__':
    # Check if data directory exists
    if not os.path.isdir(TRAIN_DIR) or not os.path.isdir(VALIDATION_DIR):
        logging.error("Data directories not found. Please run `prepare_data.py` first.")
    else:
        train_model()
