import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file from project root if present
load_dotenv(BASE_DIR / ".env")

class Settings:
    """
    Centralized Configuration Settings.
    Reads environment variables with sensible defaults.
    Analogous to application.properties / application.yml in Spring Boot.
    """
    APP_NAME: str = "Face Recognition Attendance API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

    # Database Configuration (MySQL)
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "face_attendance")
    TEST_DB_NAME: str = os.getenv("TEST_DB_NAME", "face_attendance_test")

    # JWT Authentication Configuration
    JWT_SECRET: str = os.getenv("JWT_SECRET", "face-attendance-system-secure-jwt-secret-key-2026")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24 hours

    # Constructed MySQL Connection URL
    @property
    def DATABASE_URL(self) -> str:
        if self.DB_PASSWORD:
            return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        return f"mysql+pymysql://{self.DB_USER}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    @property
    def TEST_DATABASE_URL(self) -> str:
        if self.DB_PASSWORD:
            return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        return f"mysql+pymysql://{self.DB_USER}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    # Computer Vision & File Storage Paths
    CASCADE_PATH: Path = BASE_DIR / "haarcascade_frontalface_default.xml"
    TRAINING_IMAGES_DIR: Path = BASE_DIR / "TrainingImage"
    TRAINING_LABEL_DIR: Path = BASE_DIR / "TrainingImageLabel"
    MODEL_PATH: Path = TRAINING_LABEL_DIR / "Trainner.yml"
    LABEL_MAP_PATH: Path = TRAINING_LABEL_DIR / "label_map.csv"
    ATTENDANCE_CSV_DIR: Path = BASE_DIR / "Attendance"
    STUDENT_DETAILS_CSV: Path = BASE_DIR / "StudentDetails" / "StudentDetails.csv"

    # Face Recognition Thresholds
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "60.0"))
    MAX_SAMPLES_PER_STUDENT: int = int(os.getenv("MAX_SAMPLES_PER_STUDENT", "50"))

    def ensure_directories(self):
        """Ensure runtime directories exist."""
        self.TRAINING_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        self.TRAINING_LABEL_DIR.mkdir(parents=True, exist_ok=True)
        self.ATTENDANCE_CSV_DIR.mkdir(parents=True, exist_ok=True)
        self.STUDENT_DETAILS_CSV.parent.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.ensure_directories()
