# setup_project.py - Script to set up project structure
import os

def setup_project_structure():
    """Create necessary directories for the project"""
    directories = [
        "StudentDetails",
        "TrainingImage", 
        "TrainingImageLabel",
        "Attendance"
    ]
    
    print("🔧 Setting up project structure...")
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    print("\n📁 Project structure created successfully!")
    print("📋 Next steps:")
    print("1. Install dependencies: pip install opencv-python opencv-contrib-python pandas pillow numpy yagmail")
    print("2. Run main.py to start the attendance system")
    print("3. Use option 1 to test your camera first")
    print("4. Use option 2 to capture student faces")
    print("5. Use option 3 to train the model")
    print("6. Use option 4 to start attendance recognition")

if __name__ == "__main__":
    setup_project_structure()