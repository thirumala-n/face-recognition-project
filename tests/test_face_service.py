import pytest
import numpy as np
import cv2
from app.services.face_service import FaceService


def test_face_service_loads_cascade():
    """FaceService must load a Haar Cascade classifier on initialisation."""
    svc = FaceService()
    assert svc.cascade_classifier is not None, \
        "cascade_classifier should not be None — check opencv-contrib-python install"


def test_decode_valid_jpeg(dummy_face_image_bytes):
    """Decoding a valid JPEG returns a 3-channel BGR numpy array."""
    svc = FaceService()
    img = svc.decode_image_bytes(dummy_face_image_bytes)
    assert img is not None
    assert isinstance(img, np.ndarray)
    assert len(img.shape) == 3
    assert img.shape[2] == 3  # BGR channels


def test_decode_corrupted_bytes():
    """Decoding random non-image bytes returns None (no crash)."""
    svc = FaceService()
    img = svc.decode_image_bytes(b"not_an_image_xyz_corrupted_data_!!!")
    assert img is None


def test_detect_face_roi_blank_image(dummy_blank_image_bytes):
    """A plain black image with no face features returns None detection."""
    svc = FaceService()
    img = svc.decode_image_bytes(dummy_blank_image_bytes)
    result = svc.detect_face_roi(img)
    assert result is None


def test_recognize_when_model_not_loaded():
    """
    When recognizer is None (model not trained yet),
    recognize_face must return False with a human-readable reason.
    """
    svc = FaceService()
    svc.is_model_loaded = False
    svc.recognizer = None

    dummy_roi = np.zeros((100, 100), dtype=np.uint8)
    recognized, student_id, distance, msg = svc.recognize_face(dummy_roi)

    assert recognized is False
    assert student_id is None
    assert "not trained" in msg.lower() or "not loaded" in msg.lower()


def test_process_and_recognize_blank_image(dummy_blank_image_bytes):
    """
    End-to-end: blank image → no face detected → returns (False, None, None, message).
    """
    svc = FaceService()
    recognized, student_id, dist, msg = svc.process_and_recognize(dummy_blank_image_bytes)
    assert recognized is False
    assert student_id is None
    assert "No human face detected" in msg


def test_process_and_recognize_corrupted_bytes():
    """Corrupted bytes must return (False, None, None, message) gracefully."""
    svc = FaceService()
    recognized, student_id, dist, msg = svc.process_and_recognize(b"\x00\xff\x00corrupted")
    assert recognized is False
    assert student_id is None
    assert len(msg) > 0
