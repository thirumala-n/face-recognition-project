# recognize.py - FIXED VERSION
import os
import cv2
import pandas as pd
import datetime
import time

def recognize_attendance(timeout=5, conf_threshold=60):
    # Paths
    training_file = os.path.join("TrainingImageLabel", "Trainner.yml")
    label_map_file = os.path.join("TrainingImageLabel", "label_map.csv")
    student_file = os.path.join("StudentDetails", "StudentDetails.csv")
    
    # Create attendance directory
    os.makedirs("Attendance", exist_ok=True)

    # Check required files
    if not os.path.exists(training_file):
        print("❌ ERROR: Trainner.yml not found!")
        print("Please train the model first using option 3.")
        return
        
    if not os.path.exists(label_map_file):
        print("❌ ERROR: label_map.csv not found!")
        print("Please train the model first using option 3.")
        return
        
    if not os.path.exists(student_file):
        print("❌ ERROR: StudentDetails.csv not found!")
        print("Please add students first using option 2.")
        return

    try:
        # Load recognizer and label map
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(training_file)
        
        label_map = pd.read_csv(label_map_file)
        if label_map.empty:
            print("❌ ERROR: Empty label map!")
            return
            
        numeric_to_id = dict(zip(label_map['numeric_label'], label_map['id']))

        # Load student details
        df_students = pd.read_csv(student_file, dtype=str)
        if df_students.empty:
            print("❌ ERROR: No students found!")
            return
            
        id_to_name = dict(zip(df_students['Id'], df_students['Name']))
        
    except Exception as e:
        print(f"❌ ERROR loading files: {e}")
        return

    # Initialize attendance dataframe
    col_names = ['Id', 'Name', 'Date', 'Time']
    attendance = pd.DataFrame(columns=col_names)
    
    # Check if attendance already exists for today
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    attendance_file = os.path.join("Attendance", f"Attendance_{date_str}.csv")
    existing_marked_today = set()
    
    if os.path.exists(attendance_file):
        try:
            existing_df = pd.read_csv(attendance_file, dtype=str)
            # Get students already marked present today
            present_today = existing_df[existing_df['Status'] == "Present"]
            existing_marked_today = set(present_today['Id'].tolist())
            print(f"📂 Found existing attendance: {len(existing_marked_today)} students already present")
            for student_id in existing_marked_today:
                student_name = id_to_name.get(student_id, "Unknown")
                if not present_today.empty:
                    student_record = present_today[present_today['Id'] == student_id]
                    if not student_record.empty:
                        student_time = student_record['Time'].iloc[0]
                        print(f"   ✅ {student_id} - {student_name} (already present at {student_time})")
        except Exception as e:
            print(f"⚠️ Could not load existing attendance: {e}")

    # Open camera
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("❌ ERROR: Cannot open camera!")
        return
        
    cam.set(3, 640)  # Set width
    cam.set(4, 480)  # Set height
    minW = 0.1 * cam.get(3)
    minH = 0.1 * cam.get(4)

    # Load face cascade
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    faceCascade = cv2.CascadeClassifier(cascade_path)
    if faceCascade.empty():
        print("❌ ERROR: Cannot load face cascade!")
        cam.release()
        return

    print("🎥 Face recognition started - BALANCED MODE")
    print(f"⏰ Recognition will run for {timeout} seconds.")
    print(f"🔒 SECURITY: Confidence must be < {conf_threshold} to mark attendance")
    print("📋 Only trained students will be recognized.")
    print("Press 'q' to quit early.")
    
    start_time = time.time()
    unknown_count = 0
    recognition_attempts = {}  # Track multiple recognitions
    marked_today = existing_marked_today.copy()  # Start with existing attendance

    try:
        while True:
            ret, frame = cam.read()
            if not ret:
                print("❌ ERROR: Cannot read frame")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(
                gray, 
                scaleFactor=1.2,  # Less sensitive
                minNeighbors=5,   # Balanced
                minSize=(int(minW), int(minH))
            )

            for (x, y, w, h) in faces:
                face_roi = gray[y:y+h, x:x+w]
                
                # Resize face for better recognition
                face_roi = cv2.resize(face_roi, (100, 100))
                
                try:
                    # Predict the face
                    numeric_id, confidence = recognizer.predict(face_roi)
                    original_id = numeric_to_id.get(numeric_id, None)
                    
                    # Debug print (remove in production)
                    print(f"DEBUG: NumericID={numeric_id}, OriginalID={original_id}, Confidence={confidence:.1f}")
                    
                    # EMERGENCY FIX - Very permissive
                    is_valid_student = (
                        numeric_id is not None and            # Got a prediction
                        confidence < conf_threshold and       # Confidence is reasonable
                        confidence > 0                        # Confidence is not zero
                    )
                    
                    # Try to get student info even if mapping is broken
                    if original_id is None and numeric_id is not None:
                        original_id = f"STU{numeric_id:03d}"  # Create ID if missing
                        
                    if original_id and original_id not in id_to_name:
                        id_to_name[original_id] = f"Student_{numeric_id}"  # Create name if missing
                    
                    if is_valid_student:
                        # SIMPLIFIED: Require fewer consistent recognitions
                        if original_id not in recognition_attempts:
                            recognition_attempts[original_id] = []
                        
                        recognition_attempts[original_id].append(confidence)
                        
                        # Keep only last 5 attempts
                        if len(recognition_attempts[original_id]) > 5:
                            recognition_attempts[original_id] = recognition_attempts[original_id][-5:]
                        
                        # Require at least 2 consistent recognitions (REDUCED from 5)
                        recent_attempts = recognition_attempts[original_id]
                        if len(recent_attempts) >= 2:
                            avg_confidence = sum(recent_attempts) / len(recent_attempts)
                            
                            # FIXED: More reasonable confidence check
                            if avg_confidence < conf_threshold and original_id not in marked_today:
                                # RECOGNIZED STUDENT - MARK ATTENDANCE
                                name = id_to_name.get(original_id, "Unknown")
                                current_date = datetime.datetime.now().strftime('%Y-%m-%d')
                                time_str = datetime.datetime.now().strftime('%H:%M:%S')

                                # Add to attendance
                                new_row = pd.DataFrame([[original_id, name, current_date, time_str]], 
                                                     columns=col_names)
                                attendance = pd.concat([attendance, new_row], ignore_index=True)
                                marked_today.add(original_id)  # Track marked students
                                print(f"✅ ATTENDANCE MARKED: {original_id} - {name} (Avg Conf: {avg_confidence:.1f})")
                                
                                display_name = f"✅ {name}"
                                display_id = f"ID: {original_id}"
                                display_conf = f"PRESENT - NEW"
                                rect_color = (0, 255, 0)  # Green
                                text_color = (0, 255, 0)  # Green
                            elif original_id in marked_today:
                                # Already marked today (either this session or previous)
                                name = id_to_name.get(original_id, "Unknown")
                                display_name = f"✅ {name}"
                                display_id = f"ID: {original_id}"
                                if original_id in existing_marked_today:
                                    display_conf = f"PRESENT - EARLIER"
                                else:
                                    display_conf = f"PRESENT - TODAY"
                                rect_color = (0, 255, 0)  # Green
                                text_color = (0, 255, 0)  # Green
                            else:
                                # Building confidence
                                display_name = "🔍 Verifying..."
                                display_id = f"ID: {original_id}"
                                display_conf = f"Conf: {avg_confidence:.1f}"
                                rect_color = (255, 255, 0)  # Yellow
                                text_color = (255, 255, 0)  # Yellow
                        else:
                            # Need more recognitions
                            display_name = "🔍 Scanning..."
                            display_id = f"ID: {original_id}"
                            display_conf = f"Attempts: {len(recent_attempts)}/1"
                            rect_color = (255, 255, 0)  # Yellow
                            text_color = (255, 255, 0)  # Yellow
                    else:
                        # UNKNOWN PERSON OR POOR CONFIDENCE
                        unknown_count += 1
                        display_name = "❌ UNKNOWN"
                        display_id = "ACCESS DENIED"
                        display_conf = f"Conf: {confidence:.1f}"
                        rect_color = (0, 0, 255)  # Red
                        text_color = (0, 0, 255)  # Red
                        
                        # Log unknown attempts less frequently
                        if unknown_count % 30 == 0:  # Every 30 frames
                            print(f"🚫 Unknown person detected (Confidence: {confidence:.1f})")
                        
                except Exception as e:
                    display_name = "❌ ERROR"
                    display_id = "Recognition Failed"
                    display_conf = str(e)[:15]
                    rect_color = (0, 0, 255)  # Red
                    text_color = (0, 0, 255)  # Red

                # Draw rectangle around face
                cv2.rectangle(frame, (x, y), (x + w, y + h), rect_color, 3)
                
                # Display information
                cv2.putText(frame, display_name, (x+5, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 2)
                cv2.putText(frame, display_id, (x+5, y+h+20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1)
                cv2.putText(frame, display_conf, (x+5, y+h+40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1)

            # Show timer and stats
            elapsed = time.time() - start_time
            remaining = max(0, int(timeout - elapsed))
            cv2.putText(frame, f"Time: {remaining}s", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            
            # Show attendance count
            total_present = len(marked_today)
            new_present = len(marked_today - existing_marked_today)
            cv2.putText(frame, f"Present: {total_present} (New: {new_present})", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Show security level
            cv2.putText(frame, f"BALANCED MODE", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
            cv2.putText(frame, f"Threshold: {conf_threshold}", (10, 110),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)

            cv2.imshow('Attendance System - Press q to quit', frame)

            # Check for quit conditions
            if cv2.waitKey(1) & 0xFF == ord('q') or elapsed > timeout:
                break

    except KeyboardInterrupt:
        print("\n⏹️ Recognition stopped by user.")
    finally:
        cam.release()
        cv2.destroyAllWindows()

    # Generate final attendance report
    print("\n📊 Generating attendance report...")
    
    # Check if attendance file already exists for today
    attendance_file = os.path.join("Attendance", f"Attendance_{date_str}.csv")
    existing_attendance = pd.DataFrame()
    
    if os.path.exists(attendance_file):
        try:
            existing_attendance = pd.read_csv(attendance_file, dtype=str)
            print(f"📂 Loading existing attendance for {date_str}")
        except Exception as e:
            print(f"⚠️ Could not load existing attendance: {e}")
    
    # Get all registered students
    all_students = df_students[['Id', 'Name']].copy()
    
    # Mark attendance
    final_attendance = []
    for _, student in all_students.iterrows():
        student_id = student['Id']
        student_name = student['Name']
        
        # Check if student was marked present in this session
        if student_id in marked_today:
            # Check if it's a new attendance or existing
            if student_id not in existing_marked_today:
                # Find the time they were marked in this session
                student_record = attendance[attendance['Id'] == student_id]
                if not student_record.empty:
                    time_present = student_record.iloc[0]['Time']
                    final_attendance.append([student_id, student_name, date_str, time_present, "Present"])
                    print(f"📝 NEW: {student_id} - {student_name} marked present at {time_present}")
                else:
                    final_attendance.append([student_id, student_name, date_str, "Unknown", "Present"])
            else:
                # Keep existing present record
                existing_record = existing_attendance[
                    (existing_attendance['Id'] == student_id) & 
                    (existing_attendance['Status'] == "Present")
                ]
                if not existing_record.empty:
                    time_present = existing_record.iloc[0]['Time']
                    final_attendance.append([student_id, student_name, date_str, time_present, "Present"])
                    print(f"📋 EXISTING: {student_id} - {student_name} already present at {time_present}")
        
        # Check if student was already marked present in existing file
        elif not existing_attendance.empty:
            existing_record = existing_attendance[
                (existing_attendance['Id'] == student_id) & 
                (existing_attendance['Status'] == "Present")
            ]
            if not existing_record.empty:
                # Keep existing present record
                time_present = existing_record.iloc[0]['Time']
                final_attendance.append([student_id, student_name, date_str, time_present, "Present"])
                print(f"📋 EXISTING: {student_id} - {student_name} already present at {time_present}")
            else:
                # Was absent in existing file, still absent
                final_attendance.append([student_id, student_name, date_str, "Absent", "Absent"])
        else:
            # No existing file, mark as absent
            final_attendance.append([student_id, student_name, date_str, "Absent", "Absent"])
    
    # Create final dataframe
    final_df = pd.DataFrame(final_attendance, 
                           columns=['Id', 'Name', 'Date', 'Time', 'Status'])
    
    # Save to file
    final_df.to_csv(attendance_file, index=False)
    print(f"📁 Attendance saved to: {attendance_file}")

    # Display results
    present_df = final_df[final_df['Status'] == "Present"]
    absent_df = final_df[final_df['Status'] == "Absent"]
    
    print(f"\n✅ PRESENT STUDENTS ({len(present_df)}):")
    if not present_df.empty:
        for _, row in present_df.iterrows():
            print(f"   ✅ {row['Id']} - {row['Name']} (Time: {row['Time']})")
    else:
        print("   None")
    
    print(f"\n❌ ABSENT STUDENTS ({len(absent_df)}):")
    if not absent_df.empty:
        for _, row in absent_df.iterrows():
            print(f"   ❌ {row['Id']} - {row['Name']}")
    else:
        print("   None")
    
    print(f"\n📊 FINAL: {len(final_df)} students, {len(present_df)} present, {len(absent_df)} absent")

if __name__ == "__main__":
    recognize_attendance()