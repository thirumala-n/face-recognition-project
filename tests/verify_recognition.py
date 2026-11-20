"""
Verifies the /api/v1/attendance/recognize multipart endpoint using httpx.
Run after the server is started: uvicorn app.main:app --port 8000
"""
import httpx
import cv2
import numpy as np

BASE = "http://127.0.0.1:8000"

def make_blank_jpg():
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    _, buf = cv2.imencode(".jpg", img)
    return buf.tobytes()

def make_valid_jpg():
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    img[:] = (200, 180, 170)
    cv2.ellipse(img, (150, 150), (90, 110), 0, 0, 360, (230, 200, 180), -1)
    cv2.circle(img, (110, 120), 14, (40, 40, 40), -1)
    cv2.circle(img, (190, 120), 14, (40, 40, 40), -1)
    cv2.ellipse(img, (150, 200), (35, 12), 0, 0, 180, (40, 40, 40), -1)
    _, buf = cv2.imencode(".jpg", img)
    return buf.tobytes()

client = httpx.Client(base_url=BASE)

print("\n--- /api/v1/attendance/recognize endpoint tests ---")

# Test 1: empty file
r = client.post("/api/v1/attendance/recognize",
    files={"file": ("empty.jpg", b"", "image/jpeg")})
print(f"[{r.status_code}] Empty file => {r.json()}")

# Test 2: wrong content type
r = client.post("/api/v1/attendance/recognize",
    files={"file": ("doc.txt", b"hello world", "text/plain")})
print(f"[{r.status_code}] Wrong type => {r.json()}")

# Test 3: blank image (no face)
blank = make_blank_jpg()
r = client.post("/api/v1/attendance/recognize",
    files={"file": ("blank.jpg", blank, "image/jpeg")})
data = r.json()
print(f"[{r.status_code}] Blank image => recognized={data['recognized']}, msg={data['message']}")

# Test 4: synthetic face image (no model loaded yet)
face_img = make_valid_jpg()
r = client.post("/api/v1/attendance/recognize",
    files={"file": ("face.jpg", face_img, "image/jpeg")})
data = r.json()
print(f"[{r.status_code}] Face image (no model) => recognized={data['recognized']}, msg={data['message']}")

client.close()
print("\nRecognition endpoint verification done.")
