# dependency_checker.py - Run this to verify your installation
import sys

def check_dependencies():
    """Check if all required packages are installed and working"""
    print("🔍 Checking dependencies...")
    print("=" * 50)
    
    required_packages = [
        ('cv2', 'opencv-python'),
        ('pandas', 'pandas'), 
        ('PIL', 'pillow'),
        ('numpy', 'numpy'),
        ('yagmail', 'yagmail')
    ]
    
    missing_packages = []
    working_packages = []
    
    for package_name, pip_name in required_packages:
        try:
            if package_name == 'PIL':
                import PIL
                from PIL import Image
                print(f"✅ {pip_name}: {PIL.__version__}")
                working_packages.append(pip_name)
            elif package_name == 'cv2':
                import cv2
                print(f"✅ opencv-python: {cv2.__version__}")
                
                # Test if face recognition is available
                try:
                    recognizer = cv2.face.LBPHFaceRecognizer_create()
                    print(f"✅ opencv-contrib-python: Face recognition module working")
                    working_packages.append('opencv-contrib-python')
                except AttributeError:
                    print(f"❌ opencv-contrib-python: Face recognition module NOT available")
                    print(f"   Run: pip uninstall opencv-python")
                    print(f"   Then: pip install opencv-contrib-python")
                    missing_packages.append('opencv-contrib-python')
                
            else:
                module = __import__(package_name)
                version = getattr(module, '__version__', 'Unknown version')
                print(f"✅ {pip_name}: {version}")
                working_packages.append(pip_name)
                
        except ImportError:
            print(f"❌ {pip_name}: NOT INSTALLED")
            missing_packages.append(pip_name)
    
    print("\n" + "=" * 50)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("\n💡 To install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    else:
        print("✅ All dependencies are installed and working!")
        return True

def test_camera():
    """Quick camera test"""
    print("\n🎥 Testing camera...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                print("✅ Camera working!")
                return True
            else:
                print("❌ Camera found but can't read frames")
                return False
        else:
            print("❌ Camera not accessible")
            print("💡 Try different camera index: cv2.VideoCapture(1) or cv2.VideoCapture(2)")
            return False
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        return False

def test_haar_cascade():
    """Test if Haar cascade is available"""
    print("\n🔍 Testing Haar cascade...")
    try:
        import cv2
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        detector = cv2.CascadeClassifier(cascade_path)
        if detector.empty():
            print("❌ Haar cascade not loaded")
            print(f"   Path: {cascade_path}")
            return False
        else:
            print("✅ Haar cascade loaded successfully!")
            print(f"   Path: {cascade_path}")
            return True
    except Exception as e:
        print(f"❌ Haar cascade test failed: {e}")
        return False

def quick_system_test():
    """Run all tests"""
    print("🚀 FACE RECOGNITION SYSTEM - DEPENDENCY CHECK")
    print("=" * 60)
    
    deps_ok = check_dependencies()
    camera_ok = test_camera()
    cascade_ok = test_haar_cascade()
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY:")
    print(f"Dependencies: {'✅ OK' if deps_ok else '❌ ISSUES'}")
    print(f"Camera:       {'✅ OK' if camera_ok else '❌ ISSUES'}")  
    print(f"Haar Cascade: {'✅ OK' if cascade_ok else '❌ ISSUES'}")
    
    if deps_ok and camera_ok and cascade_ok:
        print("\n🎉 SYSTEM READY! You can run main.py")
        print("\n📋 Next steps:")
        print("1. Run: python main.py")
        print("2. Choose option 1 to test camera")
        print("3. Choose option 2 to capture student faces")
        print("4. Choose option 3 to train the model")
        print("5. Choose option 4 for attendance recognition")
    else:
        print("\n⚠️  SYSTEM NEEDS ATTENTION")
        print("Please fix the issues above before running main.py")
    
    return deps_ok and camera_ok and cascade_ok

if __name__ == "__main__":
    quick_system_test()
