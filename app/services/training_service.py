import os
import cv2
import numpy as np
import pandas as pd
from PIL import Image
from typing import Tuple, List, Dict
from pathlib import Path
from app.config import settings
from app.core.logging_config import logger
from app.services.face_service import face_service

class TrainingService:
    """
    Handles Face Enrollment image management and LBPH model training.
    Produces Trainner.yml and label_map.csv.
    """

    @staticmethod
    def save_student_face_samples(
        student_id: str,
        student_name: str,
        image_bytes_list: List[bytes]
    ) -> int:
        """
        Saves a list of uploaded face image samples for a student into TrainingImage/.
        Extracts face ROI, converts to grayscale, and names according to standard convention:
        {student_name}.{student_id}.{sampleNum}.jpg
        """
        saved_count = 0
        settings.TRAINING_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

        # Determine next sample number
        existing_files = [
            f for f in os.listdir(settings.TRAINING_IMAGES_DIR)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ]
        student_samples = [
            f for f in existing_files
            if len(f.split('.')) >= 3 and f.split('.')[1] == student_id
        ]
        start_idx = len(student_samples) + 1

        for idx, img_bytes in enumerate(image_bytes_list, start=start_idx):
            img_bgr = face_service.decode_image_bytes(img_bytes)
            if img_bgr is None:
                continue

            # Detect face
            detection = face_service.detect_face_roi(img_bgr)
            if detection is None:
                # If cascade did not catch it, convert whole image to 100x100 grayscale as fallback
                gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
                roi = cv2.resize(gray, (100, 100))
            else:
                roi, _ = detection

            filename = f"{student_name}.{student_id}.{idx}.jpg"
            target_path = settings.TRAINING_IMAGES_DIR / filename
            cv2.imwrite(str(target_path), roi)
            saved_count += 1

        logger.info(f"Saved {saved_count} face samples for student {student_id} ({student_name}).")
        return saved_count

    @staticmethod
    def delete_student_images(student_id: str) -> int:
        """Removes all stored face images for a specific student."""
        deleted_count = 0
        if not settings.TRAINING_IMAGES_DIR.exists():
            return 0

        for file in os.listdir(settings.TRAINING_IMAGES_DIR):
            parts = file.split('.')
            if len(parts) >= 3 and parts[1] == student_id:
                try:
                    (settings.TRAINING_IMAGES_DIR / file).unlink()
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Error deleting training image {file}: {e}")

        logger.info(f"Deleted {deleted_count} training images for student {student_id}.")
        return deleted_count

    @classmethod
    def train_model(cls) -> Tuple[bool, int, List[str], str]:
        """
        Trains the LBPH model on all images located in TrainingImage/.
        Saves Trainner.yml and label_map.csv in TrainingImageLabel/.
        Reloads the in-memory model in FaceService.
        Returns:
            (success, total_images_trained, list_of_student_ids, message)
        """
        training_path = settings.TRAINING_IMAGES_DIR
        if not training_path.exists():
            return False, 0, [], "Training directory does not exist."

        image_files = [
            training_path / f for f in os.listdir(training_path)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ]

        if not image_files:
            return False, 0, [], "No face training images found in TrainingImage directory."

        faces = []
        alphanumeric_ids = []

        for img_path in image_files:
            try:
                # Open with Pillow in grayscale mode ('L') and convert to uint8 numpy array
                pil_img = Image.open(img_path).convert('L')
                img_np = np.array(pil_img, 'uint8')

                filename = img_path.name
                parts = filename.split('.')
                if len(parts) >= 3:
                    student_id = parts[1]
                else:
                    logger.warning(f"Skipping malformed filename: {filename}")
                    continue

                faces.append(img_np)
                alphanumeric_ids.append(student_id)
            except Exception as e:
                logger.error(f"Failed processing {img_path}: {e}")
                continue

        if not faces:
            return False, 0, [], "No valid face arrays could be parsed."

        try:
            # Map unique alphanumeric IDs to contiguous integer labels [0, 1, 2...]
            unique_ids = sorted(list(set(alphanumeric_ids)))
            id_to_numeric: Dict[str, int] = {uid: i for i, uid in enumerate(unique_ids)}
            numeric_labels = [id_to_numeric[uid] for uid in alphanumeric_ids]

            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.train(faces, np.array(numeric_labels, dtype=np.int32))

            settings.TRAINING_LABEL_DIR.mkdir(parents=True, exist_ok=True)
            recognizer.save(str(settings.MODEL_PATH))

            # Save label map
            df_label_map = pd.DataFrame({
                'numeric_label': list(range(len(unique_ids))),
                'id': unique_ids
            })
            df_label_map.to_csv(settings.LABEL_MAP_PATH, index=False)

            # Reload model inside face service
            face_service.reload_model()

            logger.info(f"Model trained successfully on {len(faces)} images for {len(unique_ids)} students.")
            return True, len(faces), unique_ids, "Model trained successfully."

        except Exception as e:
            logger.error(f"Training failed: {e}")
            return False, 0, [], f"Training error: {str(e)}"

training_service = TrainingService()
