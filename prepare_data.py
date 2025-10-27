
import os
import zipfile
import pandas as pd
import shutil
from sklearn.model_selection import train_test_split
import logging
import json
from dotenv import load_dotenv
from collections import Counter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_and_prepare_data():
    """
    Downloads the HAM10000 dataset, creates a smaller, stratified sample, 
    and organizes the images for training.
    """
    # 0. Load environment variables and set up Kaggle credentials
    load_dotenv()
    kaggle_username = os.getenv("KAGGLE_USERNAME")
    kaggle_key = os.getenv("KAGGLE_KEY")

    if not kaggle_username or not kaggle_key:
        logging.error("Kaggle credentials not found in .env file. Please create .env with KAGGLE_USERNAME and KAGGLE_KEY.")
        return

    # Ensure the .kaggle directory exists and write the credentials file
    kaggle_dir = os.path.expanduser("~/.kaggle")
    os.makedirs(kaggle_dir, exist_ok=True)
    kaggle_json_path = os.path.join(kaggle_dir, "kaggle.json")
    with open(kaggle_json_path, "w") as f:
        json.dump({"username": kaggle_username, "key": kaggle_key}, f)
    os.chmod(kaggle_json_path, 0o600)  # Set file permissions for security

    # 1. Download the dataset
    # 1. Download metadata and then only the sampled images using KaggleApi
    logging.info("Downloading HAM10000 metadata and sampled images from Kaggle (no full-zip)...")
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except Exception:
        logging.error("kaggle package not available in the environment. Please install it (pip install kaggle) and try again.")
        return

    api = KaggleApi()
    api.authenticate()

    # Download metadata CSV first
    os.makedirs("ham10000_temp", exist_ok=True)
    metadata_file = "HAM10000_metadata.csv"
    try:
        logging.info("Downloading HAM10000 dataset from Kaggle...")
        api.dataset_download_files('kmader/skin-cancer-mnist-ham10000', path='ham10000_temp', force=True)
        
        # Extract the downloaded zip
        zip_path = os.path.join('ham10000_temp', 'skin-cancer-mnist-ham10000.zip')
        if os.path.exists(zip_path):
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall('ham10000_temp')
            os.remove(zip_path)  # Clean up the zip file after extraction
        else:
            logging.error("Downloaded zip file not found!")
            return
    except Exception as e:
        logging.error(f"Failed to download metadata via KaggleApi: {e}")
        return

    # Load metadata
    logging.info("Loading metadata...")
    metadata = pd.read_csv(os.path.join('ham10000_temp', metadata_file))

    # 5. Create exact stratified sample of up to 1000 images (same logic as before)

    # 3. Load metadata
    logging.info("Loading metadata...")
    metadata = pd.read_csv("ham10000_temp/HAM10000_metadata.csv")

    # 4. Map diagnoses to 'benign' or 'malignant'
    logging.info("Mapping diagnoses to benign/malignant...")
    metadata['label'] = metadata['dx'].map({
        'nv': 'benign', 'bkl': 'benign', 'df': 'benign', 'vasc': 'benign',
        'mel': 'malignant', 'bcc': 'malignant', 'akiec': 'malignant'
    })
    metadata['image_path'] = metadata['image_id'].apply(lambda x: f"{x}.jpg")

    # 5. --- Create an exact stratified sample of up to 1000 images ---
    sample_size = min(1000, len(metadata))
    logging.info(f"Creating a stratified sample of {sample_size} images to speed up development...")

    # Determine per-class sample counts proportionally (min 1 per class) and adjust to sum exactly sample_size
    label_counts = metadata['label'].value_counts().to_dict()
    total = len(metadata)
    per_class = {label: max(1, int(round((count / total) * sample_size))) for label, count in label_counts.items()}
    current = sum(per_class.values())
    labels = list(per_class.keys())
    # If we need to add samples, add to the largest classes
    while current < sample_size:
        # choose class with largest original count
        target = max(labels, key=lambda l: label_counts[l])
        per_class[target] += 1
        current += 1
    # If we need to remove samples, remove from classes with allocation > 1
    while current > sample_size:
        candidate = max(labels, key=lambda l: per_class[l] if per_class[l] > 1 else -1)
        if per_class[candidate] > 1:
            per_class[candidate] -= 1
            current -= 1
        else:
            break

    # Build the sampled metadata by sampling exactly per-class counts
    sampled_frames = []
    for label, n in per_class.items():
        group = metadata[metadata['label'] == label]
        if len(group) <= n:
            sampled_frames.append(group)
        else:
            sampled_frames.append(group.sample(n=n, random_state=42))
    sampled_metadata = pd.concat(sampled_frames).sample(frac=1, random_state=42).reset_index(drop=True)

    # No need to download images individually since we already have the full dataset extracted
    logging.info("Using images from the downloaded dataset...")

    # 6. Create train/validation directories
    logging.info("Creating training and validation directories...")
    base_dir = 'data'
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir) # Clean up previous runs
    train_dir = os.path.join(base_dir, 'train')
    validation_dir = os.path.join(base_dir, 'validation')
    os.makedirs(os.path.join(train_dir, 'benign'), exist_ok=True)
    os.makedirs(os.path.join(train_dir, 'malignant'), exist_ok=True)
    os.makedirs(os.path.join(validation_dir, 'benign'), exist_ok=True)
    os.makedirs(os.path.join(validation_dir, 'malignant'), exist_ok=True)

    # 7. Split the *sampled* data into training and validation sets
    logging.info("Splitting the sampled data into training (80%) and validation (20%) sets...")
    train_df, validation_df = train_test_split(sampled_metadata, test_size=0.2, random_state=42, stratify=sampled_metadata['label'])

    # 8. Move images to the correct directories
    def move_images(df, source_dirs, destination_dir, total_to_move):
        from PIL import Image
        moved_count = 0
        for _, row in df.iterrows():
            image_filename = row['image_path']
            label = row['label']
            found = False
            for source_dir in source_dirs:
                src_path = os.path.join(source_dir, image_filename)
                if os.path.exists(src_path):
                    dest_path = os.path.join(destination_dir, label, image_filename)
                    try:
                        # Resize the image before saving
                        with Image.open(src_path) as img:
                            img = img.resize((224, 224))  # Resize to 224x224 for ResNet50
                            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                            img.save(dest_path)
                        moved_count += 1
                        found = True
                        # Log progress: every 10 images and the final image to reduce spam
                        if moved_count % 10 == 0 or moved_count == total_to_move:
                            logging.info(f"Progress: {moved_count}/{total_to_move} images processed and moved to {destination_dir}")
                        else:
                            logging.debug(f"Processed and moved {image_filename} ({moved_count}/{total_to_move})")
                    except Exception as e:
                        logging.error(f"Failed to process/move {src_path} -> {dest_path}: {e}")
                    break
            if not found:
                logging.warning(f"Image not found in source dirs: {image_filename}")
        logging.info(f"Finished processing and moving to {destination_dir}: {moved_count}/{total_to_move} moved")

    source_image_dirs = [os.path.join("ham10000_temp", "HAM10000_images_part_1"), 
                   os.path.join("ham10000_temp", "HAM10000_images_part_2")]
    
    # Ensure source directories exist
    for dir_path in source_image_dirs:
        if not os.path.exists(dir_path):
            logging.warning(f"Source directory not found: {dir_path}")
            source_image_dirs.remove(dir_path)
    
    if not source_image_dirs:
        logging.error("No source image directories found! The dataset might not have been downloaded correctly.")
        return

    logging.info("Moving and resizing training images...")
    expected_train = len(train_df)
    move_images(train_df, source_image_dirs, train_dir, expected_train)

    logging.info("Moving and resizing validation images...")
    expected_val = len(validation_df)
    move_images(validation_df, source_image_dirs, validation_dir, expected_val)

    # Verify the final dataset structure
    total_train = sum(len(os.listdir(os.path.join(train_dir, label))) for label in ['benign', 'malignant'])
    total_val = sum(len(os.listdir(os.path.join(validation_dir, label))) for label in ['benign', 'malignant'])
    
    logging.info(f"Final dataset statistics:")
    logging.info(f"- Training images: {total_train}")
    logging.info(f"- Validation images: {total_val}")
    
    # 9. Clean up temporary directory
    logging.info("Cleaning up temporary files...")
    shutil.rmtree("ham10000_temp")
    
    logging.info("Data preparation complete! The 'data' directory is ready for training.")

if __name__ == '__main__':
    download_and_prepare_data()
