import os
import cv2
import numpy as np
import pandas as pd
from typing import Optional, Tuple
from pathlib import Path
from app.config import settings
from app.core.logging_config import logger

class FaceService:
    """
    Service responsible for Face Detection and Face Recognition.
    Preserves existing Haar Cascade + LBPH computer vision pipeline.
    Thread-safe and stateless per request.
    """

    def __init__(self):
        self.cascade_classifier: Optional[cv2.CascadeClassifier] = None
        self.recognizer = None
        self.label_map: dict[int, str] = {}  # numeric_label -> student_id
        self.is_model_loaded: bool = False

        self._load_cascade()
        self.load_model()

    def _load_cascade(self):
        """Loads Haar Cascade classifier from project or OpenCV builtin path."""
        cascade_path = str(settings.CASCADE_PATH)
        if not os.path.exists(cascade_path):
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

        classifier = cv2.CascadeClassifier(cascade_path)
        if classifier.empty():
            logger.error(f"Failed to load Haar Cascade from: {cascade_path}")
            self.cascade_classifier = None
        else:
            self.cascade_classifier = classifier
            logger.info("Haar Cascade classifier loaded successfully.")

    def load_model(self) -> bool:
        """
        Loads the trained LBPH model and label mapping from disk.
        Returns True if loaded successfully, False otherwise.
        """
        model_path = str(settings.MODEL_PATH)
        map_path = str(settings.LABEL_MAP_PATH)

        if not os.path.exists(model_path) or not os.path.exists(map_path):
            logger.warning(f"Trained model files not found ({model_path} / {map_path}). System will detect faces but cannot recognize.")
            self.recognizer = None
            self.label_map = {}
            self.is_model_loaded = False
            return False

        try:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.read(model_path)
            self.recognizer = recognizer

            df_map = pd.read_csv(map_path, dtype={'numeric_label': int, 'id': str})
            self.label_map = dict(zip(df_map['numeric_label'], df_map['id']))
            self.is_model_loaded = True
            logger.info(f"LBPH model and label map loaded successfully ({len(self.label_map)} identities mapped).")
            return True
        except Exception as e:
            logger.error(f"Error loading LBPH model: {e}")
            self.recognizer = None
            self.label_map = {}
            self.is_model_loaded = False
            return False

    def reload_model(self) -> bool:
        """Refreshes the model in memory after retraining."""
        return self.load_model()

    def decode_image_bytes(self, image_bytes: bytes) -> Optional[np.ndarray]:
        """Decodes raw uploaded image bytes into an OpenCV BGR image matrix."""
        try:
            np_arr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            logger.error(f"Failed to decode image bytes: {e}")
            return None

    def detect_face_roi(self, image_bgr: np.ndarray) -> Optional[Tuple[np.ndarray, Tuple[int, int, int, int]]]:
        """
        Detects the primary face in the image and returns:
        (grayscale_roi_100x100, (x, y, w, h)) or None.
        """
        if self.cascade_classifier is None:
            self._load_cascade()
            if self.cascade_classifier is None:
                raise RuntimeError("Haar Cascade Classifier unavailable.")

        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        faces = self.cascade_classifier.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(30, 30)
        )

        if len(faces) == 0:
            return None

        # Select the largest face by bounding box area (w * h)
        primary_face = max(faces, key=lambda f: f[2] * f[3])
        x, y, w, h = primary_face
        face_roi = gray[y:y+h, x:x+w]
        face_roi_resized = cv2.resize(face_roi, (100, 100))

        return face_roi_resized, (int(x), int(y), int(w), int(h))

    def recognize_face(
        self,
        face_roi: np.ndarray,
        threshold: Optional[float] = None
    ) -> Tuple[bool, Optional[str], Optional[float], str]:
        """
        Performs LBPH recognition on a preprocessed face ROI (100x100 grayscale).
        Returns:
            (is_recognized, student_id, distance, reason)
        Note:
            In LBPH, distance represents Chi-square distance between histograms.
            Lower distance = closer match (0 is identical match).
            Never creates phantom student IDs.
        """
        if not self.is_model_loaded or self.recognizer is None:
            return False, None, None, "Recognition model is not trained or loaded yet."

        active_threshold = threshold if threshold is not None else settings.CONFIDENCE_THRESHOLD

        try:
            numeric_label, distance = self.recognizer.predict(face_roi)
            distance = round(float(distance), 2)

            student_id = self.label_map.get(numeric_label)
            if student_id is None:
                logger.warning(f"Model predicted label {numeric_label} which is missing from label_map.")
                return False, None, distance, "Predicted class label is not registered."

            # Verify against distance threshold
            if distance <= active_threshold:
                logger.info(f"Face recognized: student_id={student_id}, distance={distance} (threshold={active_threshold})")
                return True, student_id, distance, "Face recognized successfully."
            else:
                logger.info(f"Face rejected: student_id={student_id}, distance={distance} exceeds threshold {active_threshold}")
                return False, None, distance, f"Face distance ({distance}) exceeds confidence threshold ({active_threshold}). Unknown person."

        except Exception as e:
            logger.error(f"Error during LBPH prediction: {e}")
            return False, None, None, f"Recognition engine error: {str(e)}"

    def process_and_recognize(
        self,
        image_bytes: bytes,
        threshold: Optional[float] = None
    ) -> Tuple[bool, Optional[str], Optional[float], str]:
        """
        End-to-end pipeline:
        1. Decode bytes to image.
        2. Detect face ROI.
        3. Run LBPH prediction.
        """
        img = self.decode_image_bytes(image_bytes)
        if img is None:
            return False, None, None, "Invalid image file format or corrupted binary data."

        detection_result = self.detect_face_roi(img)
        if detection_result is None:
            return False, None, None, "No human face detected in the provided image."

        face_roi, _ = detection_result
        return self.recognize_face(face_roi, threshold=threshold)

face_service = FaceService()
