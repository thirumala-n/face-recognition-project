# check_camera.py - FIXED VERSION (Won't get stuck)
import cv2

def camer():
    print("🎥 Camera test starting...")
    print("CONTROLS:")
    print("- Press 'q' to quit")
    print("- Press 'ESC' to quit") 
    print("- Press SPACE to quit")
    print("- Close window with X button")
    print("- Press Ctrl+C in terminal if stuck")
    
    # Load cascade
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    cascade_face = cv2.CascadeClassifier(cascade_path)
    
    if cascade_face.empty():
        print("❌ Error: Could not load face cascade classifier")
        return

    # Open camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Error: Could not open camera")
        return

    print("✅ Camera opened successfully!")
    frame_count = 0
    
    try:
        while True:
            ret, img = cap.read()
            frame_count += 1
            
            if not ret:
                print("❌ Error: Could not read frame")
                break

            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = cascade_face.detectMultiScale(gray, 1.3, 5, minSize=(30, 30))

            # Draw rectangles around faces
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Add instructions on the image
            cv2.putText(img, "Press Q, ESC, or SPACE to quit", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(img, f"Faces detected: {len(faces)}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Show the frame
            cv2.imshow('Camera Test - Multiple ways to quit', img)

            # Multiple exit conditions - VERY IMPORTANT!
            key = cv2.waitKey(30) & 0xFF  # Increased wait time for better responsiveness
            
            if key == ord('q') or key == ord('Q'):
                print("✅ Quit with 'q' key")
                break
            elif key == 27:  # ESC key
                print("✅ Quit with ESC key")
                break
            elif key == 32:  # SPACE key
                print("✅ Quit with SPACE key")
                break
            elif key != 255:  # Any other key pressed
                print(f"Key pressed: {key}. Press Q, ESC, or SPACE to quit.")
                
            # Check if window was closed manually
            try:
                if cv2.getWindowProperty('Camera Test - Multiple ways to quit', cv2.WND_PROP_VISIBLE) < 1:
                    print("✅ Window closed manually")
                    break
            except:
                print("✅ Window closed")
                break
                
            # Safety timeout - auto-close after 2 minutes
            if frame_count > 3600:  # 30fps * 120 seconds
                print("⏰ Auto-closing after 2 minutes")
                break

    except KeyboardInterrupt:
        print("\n✅ Stopped with Ctrl+C")
    except Exception as e:
        print(f"❌ Error during camera test: {e}")
    finally:
        # ALWAYS cleanup
        try:
            cap.release()
            cv2.destroyAllWindows()
            cv2.waitKey(1)  # Extra cleanup
        except:
            pass
        print("🔧 Camera test completed - all resources cleaned up")

if __name__ == "__main__":
    camer()