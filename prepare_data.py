
import os
import zipfile
import pandas as pd
import shutil
from sklearn.model_selection import train_test_split
import logging
import json
from dotenv import load_dotenv

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
    logging.info("Downloading HAM10000 dataset from Kaggle...")
    # Use -o to overwrite existing files, -q for quiet download
    os.system("kaggle datasets download -d kmader/skin-cancer-mnist-ham10000 -o -q")

    # 2. Unzip the dataset
    logging.info("Unzipping dataset...")
    with zipfile.ZipFile("skin-cancer-mnist-ham10000.zip", 'r') as zip_ref:
        zip_ref.extractall("ham10000_temp")
    os.remove("skin-cancer-mnist-ham10000.zip")

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

    # 5. --- OPTIMIZATION: Create a stratified sample of the data (10% of original) ---
    logging.info("Creating a stratified sample of 1000 images to speed up development...")
    # Using train_test_split to create a stratified sample is a common trick.
    # We are taking a 10% sample, so about 1000 images.
    _, sampled_metadata = train_test_split(metadata, test_size=0.1, random_state=42, stratify=metadata['label'])

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
    def move_images(df, source_dirs, destination_dir):
        moved_count = 0
        for _, row in df.iterrows():
            image_filename = row['image_path']
            label = row['label']
            # Find the image in one of the source directories
            for source_dir in source_dirs:
                src_path = os.path.join(source_dir, image_filename)
                if os.path.exists(src_path):
                    dest_path = os.path.join(destination_dir, label, image_filename)
                    shutil.move(src_path, dest_path)
                    moved_count += 1
                    break
        logging.info(f"Moved {moved_count} images to {destination_dir}")

    source_image_dirs = ["ham10000_temp/HAM10000_images_part_1", "ham10000_temp/HAM10000_images_part_2"]
    
    logging.info("Moving training images...")
    move_images(train_df, source_image_dirs, train_dir)
    
    logging.info("Moving validation images...")
    move_images(validation_df, source_image_dirs, validation_dir)

    # 9. Clean up temporary directory
    logging.info("Cleaning up temporary files...")
    shutil.rmtree("ham10000_temp")
    
    logging.info("Data preparation complete! The 'data' directory is ready for training.")

if __name__ == '__main__':
    download_and_prepare_data()
