# train_image.py - Fixed version
import os
import time
import cv2
import numpy as np
from PIL import Image
import pandas as pd

def getImagesAndLabels(path):
    if not os.path.exists(path):
        print(f"Training image directory '{path}' does not exist!")
        return [], [], []
        
    imagePaths = [os.path.join(path, f) for f in os.listdir(path) 
                  if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if not imagePaths:
        print("No training images found!")
        return [], [], []
    
    faces = []
    alphanumeric_ids = []

    for imagePath in imagePaths:
        try:
            pilImage = Image.open(imagePath).convert('L')
            imageNp = np.array(pilImage, 'uint8')

            filename = os.path.split(imagePath)[-1]
            parts = filename.split(".")  # expect filename like 'name.id.number.jpg'
            if len(parts) >= 3:
                student_id = parts[1]  # Extract ID from filename
            else:
                print(f"Skipping file with invalid format: {filename}")
                continue

            faces.append(imageNp)
            alphanumeric_ids.append(student_id)
        except Exception as e:
            print(f"Error processing {imagePath}: {e}")
            continue
    
    if not faces:
        return [], [], []
    
    # Map alphanumeric IDs to numeric labels
    unique_ids = list(sorted(set(alphanumeric_ids)))
    id_to_numeric = {uid: i for i, uid in enumerate(unique_ids)}
    numeric_labels = [id_to_numeric[uid] for uid in alphanumeric_ids]

    return faces, numeric_labels, unique_ids

def counter_img(path):
    if not os.path.exists(path):
        return
    imagePaths = [os.path.join(path, f) for f in os.listdir(path) 
                  if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    total_images = len(imagePaths)
    for idx, imagePath in enumerate(imagePaths, 1):
        print(f"Processing image {idx}/{total_images}: {os.path.basename(imagePath)}", end="\r")
        time.sleep(0.02)

def TrainImages():
    training_path = "TrainingImage"
    
    # Check if training directory exists
    if not os.path.exists(training_path):
        print(f"❌ Training directory '{training_path}' not found!")
        print("Please capture some faces first using option 2.")
        return

    # Check OpenCV version and create appropriate recognizer
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
    except AttributeError:
        print("❌ OpenCV face module not available!")
        print("Install opencv-contrib-python: pip install opencv-contrib-python")
        return

    # Load cascade classifier
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    detector = cv2.CascadeClassifier(cascade_path)
    if detector.empty():
        print("❌ Cannot load cascade file!")
        print(f"Looking for file at: {cascade_path}")
        return

    print("📚 Loading training images...")
    faces, numeric_labels, unique_ids = getImagesAndLabels(training_path)
    
    if len(faces) == 0:
        print("❌ No valid training images found!")
        print("Please capture some faces first using option 2.")
        return

    print(f"✅ Found {len(faces)} training images for {len(unique_ids)} students")
    print("🔄 Training model...")
    
    # Show progress
    counter_img(training_path)
    print()  # New line after progress

    try:
        # Train the recognizer
        recognizer.train(faces, np.array(numeric_labels))
        
        # Create output directory
        output_dir = "TrainingImageLabel"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save the trained model
        model_path = os.path.join(output_dir, "Trainner.yml")
        recognizer.save(model_path)

        # Save label mapping
        label_map = pd.DataFrame({
            'numeric_label': list(range(len(unique_ids))),
            'id': unique_ids
        })
        map_path = os.path.join(output_dir, "label_map.csv")
        label_map.to_csv(map_path, index=False)

        print("✅ Training completed successfully!")
        print(f"📁 Model saved to: {model_path}")
        print(f"📁 Label map saved to: {map_path}")
        print(f"👥 Trained for students: {', '.join(unique_ids)}")
        
    except Exception as e:
        print(f"❌ Training failed: {e}")

if __name__ == "__main__":
    TrainImages()