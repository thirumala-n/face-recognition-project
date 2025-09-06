# test_individual_components.py - Test each component separately
def test_face_detection():
    """Test basic face detection"""
    print("🧪 Testing face detection...")
    try:
        import cv2
        import numpy as np
        
        # Create a dummy image with face-like features
        img = np.zeros((300, 300, 3), dtype=np.uint8)
        
        # Load cascade
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(cascade_path)
        
        if face_cascade.empty():
            print("❌ Face cascade not loaded")
            return False
        
        print("✅ Face detection setup working!")
        return True
        
    except Exception as e:
        print(f"❌ Face detection test failed: {e}")
        return False

def test_face_recognition():
    """Test face recognition module"""
    print("🧪 Testing face recognition...")
    try:
        import cv2
        
        # Try to create recognizer
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        print("✅ Face recognition module working!")
        return True
        
    except AttributeError:
        print("❌ Face recognition module not available")
        print("💡 Install: pip install opencv-contrib-python")
        return False
    except Exception as e:
        print(f"❌ Face recognition test failed: {e}")
        return False

def test_email_setup():
    """Test email capabilities"""
    print("🧪 Testing email setup...")
    try:
        import yagmail
        import smtplib
        from email.mime.multipart import MIMEMultipart
        print("✅ Email modules available!")
        return True
    except ImportError as e:
        print(f"❌ Email module missing: {e}")
        print("💡 Install: pip install yagmail")
        return False

def run_component_tests():
    """Run all component tests"""
    print("🔬 COMPONENT TESTING")
    print("=" * 30)
    
    tests = [
        test_face_detection,
        test_face_recognition, 
        test_email_setup
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()
    
    print("=" * 30)
    if all(results):
        print("✅ All components working!")
    else:
        print("❌ Some components need attention")

if __name__ == "__main__":
    print("Choose test:")
    print("1. Full system check")
    print("2. Component tests only") 
    print("3. OpenCV fix guide")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        quick_system_test()
    elif choice == "2":
        run_component_tests()
    elif choice == "3":
        fix_opencv_installation()
    else:
        print("Running full system check...")
        quick_system_test()