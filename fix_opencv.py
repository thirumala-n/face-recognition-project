# fix_opencv.py - Run this if you have OpenCV issues
def fix_opencv_installation():
    """Guide to fix OpenCV installation"""
    print("🔧 OPENCV INSTALLATION FIX")
    print("=" * 40)
    print("\nIf you're having OpenCV issues, try these steps:")
    print("\n1. UNINSTALL ALL OPENCV PACKAGES:")
    print("   pip uninstall opencv-python")
    print("   pip uninstall opencv-contrib-python")
    print("   pip uninstall opencv-python-headless")
    
    print("\n2. CLEAN INSTALL:")
    print("   pip install opencv-contrib-python")
    print("   (This includes both opencv-python and contrib modules)")
    
    print("\n3. VERIFY INSTALLATION:")
    print("   python -c \"import cv2; print(cv2.__version__)\"")
    print("   python -c \"import cv2; cv2.face.LBPHFaceRecognizer_create()\"")
    
    print("\n4. IF STILL NOT WORKING:")
    print("   pip install opencv-contrib-python==4.8.1.78")
    print("   (Use specific version)")