# Face Recognition Attendance System (FastAPI + MySQL Backend)

A production-ready REST API backend for automated classroom and enterprise attendance management using Computer Vision (OpenCV, Haar Cascade, LBPH Face Recognizer) and modern Python backend engineering (FastAPI, SQLAlchemy 2.0, MySQL, Pydantic v2).

---

## 1. Project Overview

This project transforms a classical computer vision attendance script into an enterprise-structured, decoupled REST API service. It automates student registration, multi-sample face enrollment, model training, live facial recognition from client image uploads, attendance deduplication, and automated reporting.

### Core Capabilities
- **Decoupled REST API Architecture:** Clear separation of concerns across Routers, Services, Repositories, and ORM Entities.
- **Relational Persistence (MySQL):** Replaced legacy flat CSV logs with an ACID-compliant MySQL database managed via SQLAlchemy 2.0.
- **Daily Attendance Deduplication:** Database-level composite unique constraint on `(student_id, attendance_date)` guarantees zero duplicate attendance records per student per day.
- **Computer Vision Pipeline:** Preserves classical, lightweight Haar Feature-based Cascade Classifiers for face localization and Local Binary Patterns Histograms (LBPH) for texture-based facial recognition.
- **Non-blocking Execution:** Synchronous OpenCV operations are offloaded to Python worker threads (`asyncio.to_thread`), preventing CPU-bound image decoding from freezing the FastAPI asynchronous event loop.
- **Interactive Documentation:** Automatic OpenAPI / Swagger UI at `/docs`.

---

## 2. Technology Stack

| Layer / Component | Technology | Version | Description |
| :--- | :--- | :--- | :--- |
| **Language** | Python | 3.12+ | Core programming runtime |
| **Web Framework** | FastAPI | >= 0.110.0 | High-performance async ASGI web framework |
| **ASGI Server** | Uvicorn | >= 0.28.0 | Lightning-fast ASGI web server implementation |
| **Database** | MySQL | 8.0+ | Relational Database Management System |
| **ORM** | SQLAlchemy | >= 2.0.0 | Object Relational Mapper (Unit of Work & Repository) |
| **DB Driver** | PyMySQL | >= 1.1.0 | Pure Python MySQL client library |
| **Data Validation** | Pydantic | >= 2.6.0 | Request/Response parsing and schema validation (DTOs) |
| **Computer Vision** | OpenCV Contrib | >= 4.8.0 | Video decoding, Haar Cascade, and LBPH Face Recognizer |
| **Numerical Processing**| NumPy | >= 1.26.0 | Image matrix manipulation |
| **Image Loading** | Pillow (PIL) | >= 10.0.0 | Image file I/O and format normalization |
| **Config Management** | python-dotenv | >= 1.0.0 | Environment-variable management via `.env` |
| **Testing** | Pytest & HTTPX | >= 8.0.0 | Automated unit and integration testing suite |

---

## 3. Architecture and Folder Structure

The project implements a **Layered Architecture** adhering to SOLID principles:

```text
face-attendance-system/
│
├── app/
│   ├── main.py                     # FastAPI application factory & lifecycle management
│   ├── config.py                   # Centralized configuration loaded from .env
│   │
│   ├── api/                        # Presentation Layer (FastAPI Routers / Controllers)
│   │   ├── __init__.py
│   │   ├── students.py             # Student management and face sample enrollment routes
│   │   └── attendance.py           # Face recognition and attendance verification routes
│   │
│   ├── models/                     # Domain Layer (SQLAlchemy ORM Entities)
│   │   ├── __init__.py
│   │   ├── student.py              # Student database entity definition
│   │   └── attendance.py           # Attendance database entity with unique constraints
│   │
│   ├── schemas/                    # Data Transfer Objects (Pydantic v2 DTOs)
│   │   ├── __init__.py
│   │   ├── student.py              # Request/Response schemas for student domain
│   │   └── attendance.py           # Request/Response schemas for attendance & recognition
│   │
│   ├── services/                   # Business Logic Layer (Domain Services)
│   │   ├── __init__.py
│   │   ├── face_service.py         # Face detection, grayscale normalization, LBPH inference
│   │   ├── training_service.py     # Image dataset management, LBPH training, model export
│   │   └── attendance_service.py   # Attendance rules, deduplication, CSV backup sync
│   │
│   ├── database/                   # Data Access Layer (Repositories & Connection)
│   │   ├── __init__.py
│   │   ├── connection.py           # Engine, SessionLocal, Base, get_db dependency
│   │   └── repositories.py         # StudentRepository and AttendanceRepository DAOs
│   │
│   └── core/
│       ├── __init__.py
│       └── logging_config.py       # Centralized logging configuration
│
├── Attendance/                     # Legacy CSV backup directory (preserved)
├── StudentDetails/                 # Legacy CSV student master directory (preserved)
├── TrainingImage/                  # Directory containing face sample photos for training
├── TrainingImageLabel/             # Serialized model weights (Trainner.yml, label_map.csv)
├── tests/                          # Automated Pytest suite
│   ├── __init__.py
│   ├── conftest.py                 # Test database fixtures, client overrides, mock images
│   ├── test_students.py            # Student API unit and integration tests
│   ├── test_attendance.py          # Attendance API and deduplication tests
│   └── test_face_service.py        # Computer vision service isolated tests
│
├── .env.example                    # Template for environment configuration
├── .gitignore                      # Git exclusion rules (ignores .env and caches)
├── requirements.txt                # Pinned production and test dependencies
└── README.md                       # Comprehensive system documentation
```

---

## 4. Installation Instructions

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd face-recognition-project
```

### Step 2: Create and Activate Virtual Environment
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 5. MySQL Database Setup

1. Start your local MySQL Server service.
2. The application will **automatically create** the `face_attendance` database on startup if your MySQL user has `CREATE DATABASE` privileges.
3. Alternatively, you can create it manually via MySQL CLI:
```sql
CREATE DATABASE face_attendance CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE face_attendance_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## 6. Environment Variable Configuration

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` with your actual MySQL credentials:
```ini
# Application Configuration
DEBUG=False

# MySQL Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password_here
DB_NAME=face_attendance
TEST_DB_NAME=face_attendance_test

# Face Recognition Settings
CONFIDENCE_THRESHOLD=60.0
MAX_SAMPLES_PER_STUDENT=50
```

> **Security Note:** The `.env` file is excluded in `.gitignore` and must never be committed to source control.

---

## 7. How to Run the Application (Backend & Frontend)

### 7.1 Start the FastAPI Backend
Start the Uvicorn ASGI server from the project root:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive API documentation will be available at:
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### 7.2 Start the React Frontend
Open a new terminal window, navigate into the `frontend/` directory, and run:
```bash
cd frontend
npm install
npm run dev
```

The frontend dashboard will be live at:
- **Dashboard UI:** [http://127.0.0.1:5173](http://127.0.0.1:5173)

---

## 8. API Endpoint Documentation

### Authentication APIs

| Method | Endpoint | Description | Request Body | Status Code |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Register an administrator user | JSON (`full_name`, `email`, `username`, `password`) | `201 Created` |
| `POST` | `/api/v1/auth/login` | Authenticate user & receive JWT token | JSON (`email_or_username`, `password`) | `200 OK` |
| `GET` | `/api/v1/auth/me` | Fetch authenticated user profile | Bearer Token in `Authorization` header | `200 OK` / `401` |

### Student Management APIs

| Method | Endpoint | Description | Request Body | Status Code |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/students` | Register a new student | JSON (`student_id`, `name`) | `201 Created` |
| `GET` | `/api/v1/students` | List all students | Query (`skip`, `limit`) | `200 OK` |
| `GET` | `/api/v1/students/{student_id}` | Get student by ID | Path parameter | `200 OK` / `404` |
| `DELETE` | `/api/v1/students/{student_id}` | Delete student and sample images | Path parameter | `200 OK` / `404` |
| `POST` | `/api/v1/students/{student_id}/images` | Upload face sample images | Multipart Form (`files`) | `200 OK` |
| `POST` | `/api/v1/students/train/model` | Trigger LBPH model retraining | None | `200 OK` |

### Attendance APIs

| Method | Endpoint | Description | Request Body | Status Code |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/attendance/recognize` | Upload photo, recognize face, and mark attendance | Multipart Form (`file`) | `200 OK` |
| `GET` | `/api/v1/attendance/today` | Get today's attendance summary | None | `200 OK` |
| `GET` | `/api/v1/attendance/student/{student_id}`| Get student's attendance history | Path parameter | `200 OK` |
| `GET` | `/api/v1/attendance/date/{target_date}` | Get attendance for specific date | Path parameter (`YYYY-MM-DD`) | `200 OK` |

---

## 9. Example Requests and Responses

### 1. Register a Student
**Request:**
`POST http://127.0.0.1:8000/api/v1/students`
```json
{
  "student_id": "CS101",
  "name": "Alex Mercer"
}
```
**Response (`201 Created`):**
```json
{
  "student_id": "CS101",
  "name": "Alex Mercer",
  "id": 1,
  "created_at": "2026-11-19T22:30:00.000Z"
}
```

### 2. Recognize Face and Mark Attendance
**Request:**
`POST http://127.0.0.1:8000/api/v1/attendance/recognize`  
Header: `Content-Type: multipart/form-data`  
Body: `file=@snapshot.jpg`

**Response (`200 OK` — Recognized & Marked):**
```json
{
  "recognized": true,
  "student_id": "CS101",
  "student_name": "Alex Mercer",
  "confidence_distance": 43.25,
  "threshold": 60.0,
  "attendance_marked": true,
  "status": "Present",
  "message": "Attendance marked successfully for Alex Mercer."
}
```

**Response (`200 OK` — Duplicate Attempt Today):**
```json
{
  "recognized": true,
  "student_id": "CS101",
  "student_name": "Alex Mercer",
  "confidence_distance": 41.80,
  "threshold": 60.0,
  "attendance_marked": false,
  "status": "Present",
  "message": "Attendance already marked for today at 09:14:22."
}
```

**Response (`200 OK` — Unknown Person):**
```json
{
  "recognized": false,
  "student_id": null,
  "student_name": null,
  "confidence_distance": 84.60,
  "threshold": 60.0,
  "attendance_marked": false,
  "status": null,
  "message": "Face distance (84.6) exceeds confidence threshold (60.0). Unknown person."
}
```

---

## 10. How Computer Vision Works (Haar Cascade & LBPH)

### 1. Face Detection (Haar Feature-based Cascade Classifier)
- **Algorithm:** Developed by Paul Viola and Michael Jones.
- **Mechanism:** Evaluates rectangular gradient features (edge, line, center-surround) across the integral image.
- **Cascade Stages:** Millions of features are filtered down to a cascade of strong AdaBoost classifiers. Sub-windows lacking face features are rejected in initial stages, making detection fast ($O(1)$ box evaluation).
- **Output:** Bounding rectangle coordinates `(x, y, w, h)`.

### 2. Preprocessing
- The facial Region of Interest (ROI) is cropped: `gray[y:y+h, x:x+w]`.
- Resized to standard dimensions of $100 \times 100$ pixels for consistent spatial histogram binning.

### 3. Face Recognition (Local Binary Patterns Histograms - LBPH)
- **Mechanism:**
  1. For every pixel, compares intensity against its 8 neighbors in a $3 \times 3$ window.
  2. If `neighbor >= center`, bit = `1`, else `0`.
  3. Forms an 8-bit binary number, converted to decimal ($0–255$).
  4. Divides the image into an $8 \times 8$ grid of local cells.
  5. Computes a histogram of LBP codes for each cell and concatenates them into a unified spatial feature vector.
- **Matching:** Calculates the **Chi-square distance** between the input face histogram and stored training histograms.
- **Interpretation:**
  - **Lower distance = Closer match** ($0.0$ is an exact identical match).
  - If `distance <= 60.0` (configurable), the face is verified as the matched student.
  - If `distance > 60.0`, the system classifies the face as Unknown.

---

## 11. Database Schema in MySQL

```mermaid
erDiagram
    STUDENTS ||--o{ ATTENDANCE : has
    STUDENTS {
        int id PK "Auto-increment"
        varchar student_id UK "Indexed, Unique"
        varchar name "Student Full Name"
        datetime created_at "Registration Timestamp"
    }
    ATTENDANCE {
        int id PK "Auto-increment"
        varchar student_id FK "References STUDENTS(student_id)"
        date attendance_date "Indexed, Calendar Date"
        time attendance_time "Time of Recognition"
        varchar status "'Present' or 'Absent'"
    }
```

### Table DDL
```sql
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_student_id (student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    attendance_date DATE NOT NULL,
    attendance_time TIME NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Present',
    CONSTRAINT fk_attendance_student FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    CONSTRAINT uq_student_daily_attendance UNIQUE (student_id, attendance_date),
    INDEX idx_attendance_date (attendance_date),
    INDEX idx_attendance_student (student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## 12. Running Automated Tests

Run the full pytest suite:
```bash
pytest -v
```

All unit tests:
- Execute in an isolated test database (`face_attendance_test`).
- Mock computer vision frames using synthetic NumPy image matrices.
- Require zero physical hardware webcam connections.

---

## 13. Known Limitations

1. **Illumination Sensitivity:** LBPH is more robust to uniform lighting shifts than Eigenfaces, but severe directional shadows across one half of the face can alter gradient codes and elevate distance scores.
2. **Pose Invariance:** Haar Cascade and LBPH operate best on frontal faces ($\pm 15^\circ$ head yaw/pitch). Profile faces ($>45^\circ$) will not be detected by `haarcascade_frontalface_default.xml`.
3. **No Hardware Anti-Spoofing:** Classical LBPH does not perform depth analysis or infrared pulse detection. A printed 2D photograph can pass verification if it matches the texture threshold. Future enterprise enhancements can integrate eye-blink detection or Deep Learning embeddings (FaceNet / InsightFace).
