# capture_image.py - Fixed version
import csv
import cv2
import os
import pandas as pd

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False

# === Capture Faces (New Student) ===
def takeImages():
    Id = input("Enter Your Id: ").strip()
    name = input("Enter Your Name: ").strip()
    max_images = 50  # fixed number of images per student

    # Validate inputs
    if not Id or not name:
        print("❌ Error: ID and Name cannot be empty")
        return
        
    if not Id.replace(" ", "").replace("-", "").replace("_", "").isalnum():
        print("❌ Error: ID must contain only alphanumeric characters, spaces, hyphens, or underscores")
        return
        
    if not name.replace(" ", "").isalpha():
        print("❌ Error: Name must contain only alphabetic characters (spaces allowed)")
        return

    student_file = os.path.join("StudentDetails", "StudentDetails.csv")
    training_path = "TrainingImage"
    os.makedirs("StudentDetails", exist_ok=True)
    os.makedirs(training_path, exist_ok=True)

    # Pre-check for existing student
    if os.path.exists(student_file):
        try:
            df = pd.read_csv(student_file, dtype=str)
            if not df.empty and (df["Id"].astype(str) == Id).any():
                existing_name = df.loc[df["Id"].astype(str) == Id, "Name"].values[0]
                if existing_name.lower() == name.lower():
                    print(f"⚠️ Student already exists: ID={Id}, Name={name}. Use Update option instead.")
                else:
                    print(f"❌ ID {Id} is already registered with another name: {existing_name}.")
                return
        except Exception as e:
            print(f"Error reading student file: {e}")
    else:
        # Create CSV if not exists
        try:
            with open(student_file, 'w', newline='') as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow(["Id", "Name"])
        except Exception as e:
            print(f"Error creating student file: {e}")
            return

    # Open camera
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("❌ Error: Could not open camera")
        return

    # Use OpenCV's built-in cascade path
    harcascadePath = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    detector = cv2.CascadeClassifier(harcascadePath)
    if detector.empty():
        print("❌ Error: Haar Cascade not loaded")
        cam.release()
        return

    sampleNum = 0
    print(f"🎥 Capturing new student: ID={Id}, Name={name}")
    print(f"Capturing {max_images} images...")
    print("Position your face in front of the camera. Press 'q' to quit early.\n")

    while True:
        ret, img = cam.read()
        if not ret:
            print("❌ Error: Could not read from camera")
            break

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.3, 5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            sampleNum += 1
            file_path = os.path.join(training_path, f"{name}.{Id}.{sampleNum}.jpg")
            cv2.imwrite(file_path, gray[y:y+h, x:x+w])
            print(f"📸 Captured image {sampleNum}/{max_images}", end="\r")

        cv2.imshow('Face Capture - Press q to quit', img)

        if cv2.waitKey(100) & 0xFF == ord('q'):
            print("\n🛑 Capture stopped by user.")
            break
        elif sampleNum >= max_images:
            print(f"\n✅ Reached {max_images} samples, stopping capture.")
            break

    cam.release()
    cv2.destroyAllWindows()

    if sampleNum > 0:
        # Save student details
        try:
            with open(student_file, 'a+', newline='') as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow([Id, name])
            print(f"\n✅ Student added: ID={Id}, Name={name}")
            print(f"📂 Total images captured: {sampleNum}")
        except Exception as e:
            print(f"Error saving student details: {e}")
    else:
        print("❌ No images captured. Please try again.")

# === Update Existing Student (Delete + Recapture) ===
def updateImages():
    Id = input("Enter Your Id: ").strip()
    name = input("Enter Your Name: ").strip()
    max_images = 50

    if not Id or not name:
        print("❌ Error: ID and Name cannot be empty")
        return

    student_file = os.path.join("StudentDetails", "StudentDetails.csv")
    training_path = "TrainingImage"

    if not os.path.exists(student_file):
        print("❌ No students found. Add one first using Capture Faces.")
        return

    try:
        df = pd.read_csv(student_file, dtype=str)
        if df.empty:
            print("❌ No students found. Add one first using Capture Faces.")
            return
    except Exception as e:
        print(f"Error reading student file: {e}")
        return

    # Verify student
    if (df["Id"].astype(str) == Id).any():
        existing_name = df.loc[df["Id"].astype(str) == Id, "Name"].values[0]
        if existing_name.lower() != name.lower():
            print(f"❌ ID {Id} belongs to another student: {existing_name}")
            return
    else:
        print(f"❌ Student with ID={Id} not found. Use Capture Faces to add new.")
        return

    # Delete old images
    print(f"🔄 Updating student (ID={Id}, Name={name})")
    deleted = 0
    if os.path.exists(training_path):
        for file in os.listdir(training_path):
            parts = file.split(".")
            if len(parts) >= 3 and parts[1] == Id:
                try:
                    os.remove(os.path.join(training_path, file))
                    deleted += 1
                except Exception as e:
                    print(f"Error deleting {file}: {e}")
    
    print(f"🗑️ Deleted {deleted} old images. Capturing {max_images} new ones...\n")

    # Capture new images (same logic as takeImages)
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("❌ Error: Could not open camera")
        return

    harcascadePath = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    detector = cv2.CascadeClassifier(harcascadePath)
    if detector.empty():
        print("❌ Error: Haar Cascade not loaded")
        cam.release()
        return

    sampleNum = 0
    print("Position your face in front of the camera. Press 'q' to quit early.")
    
    while True:
        ret, img = cam.read()
        if not ret:
            print("❌ Error: Could not read from camera")
            break

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.3, 5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            sampleNum += 1
            file_path = os.path.join(training_path, f"{name}.{Id}.{sampleNum}.jpg")
            cv2.imwrite(file_path, gray[y:y+h, x:x+w])
            print(f"📸 Captured image {sampleNum}/{max_images}", end="\r")

        cv2.imshow('Face Capture - Press q to quit', img)

        if cv2.waitKey(100) & 0xFF == ord('q'):
            print("\n🛑 Update stopped by user.")
            break
        elif sampleNum >= max_images:
            print(f"\n✅ Reached {max_images} samples, stopping update.")
            break

    cam.release()
    cv2.destroyAllWindows()
    print(f"\n✅ Images updated for ID={Id}, Name={name}")
    print(f"📂 Total new images captured: {sampleNum}")