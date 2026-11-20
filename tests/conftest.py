import os
import pytest
import numpy as np
import cv2
import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.config import settings
from app.database.connection import Base, get_db
from app.main import app

# ─── Build the test DATABASE URL ─────────────────────────────────────────────
_TEST_DB_URL = (
    f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}"
    f"/{settings.TEST_DB_NAME}?charset=utf8mb4"
)

test_engine = create_engine(_TEST_DB_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """
    Session-scoped fixture: creates all tables in face_attendance_test once,
    and drops them after the entire test session finishes.
    """
    from app.models.student import Student      # noqa: F401
    from app.models.attendance import Attendance  # noqa: F401
    from app.models.user import User            # noqa: F401

    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session(setup_test_db):
    """
    Function-scoped fixture: provides a fresh session per test.
    Cleans all rows from every table after each test so tests are isolated.
    """
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        from app.models.attendance import Attendance
        from app.models.student import Student
        from app.models.user import User
        session.query(Attendance).delete()
        session.query(Student).delete()
        session.query(User).delete()
        session.commit()
        session.close()


@pytest.fixture
def client(db_session):
    """
    Provides a FastAPI TestClient wired to the test database session.
    Overrides the get_db dependency so every request uses the test session.
    """
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def dummy_face_image_bytes():
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    img[:] = (200, 180, 170)
    cv2.ellipse(img, (150, 150), (90, 110), 0, 0, 360, (230, 200, 180), -1)
    cv2.circle(img, (110, 120), 14, (40, 40, 40), -1)
    cv2.circle(img, (190, 120), 14, (40, 40, 40), -1)
    cv2.ellipse(img, (150, 200), (35, 12), 0, 0, 180, (40, 40, 40), -1)
    _, buf = cv2.imencode(".jpg", img)
    return buf.tobytes()


@pytest.fixture
def dummy_blank_image_bytes():
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    _, buf = cv2.imencode(".jpg", img)
    return buf.tobytes()
