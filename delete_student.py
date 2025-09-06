# delete_student.py - Function to delete specific student data
import os
import pandas as pd

def delete_student():
    """Delete a specific student's data completely"""
    print("\n=== DELETE STUDENT DATA ===")
    
    # Get student details to delete
    student_id = input("Enter Student ID to delete: ").strip()
    student_name = input("Enter Student Name to delete: ").strip()
    
    if not student_id or not student_name:
        print("❌ Error: Both ID and Name are required!")
        return
    
    # File paths
    student_file = os.path.join("StudentDetails", "StudentDetails.csv")
    training_path = "TrainingImage"
    training_label_path = "TrainingImageLabel"
    
    deleted_items = []
    
    # 1. Delete from StudentDetails.csv
    if os.path.exists(student_file):
        try:
            df = pd.read_csv(student_file, dtype=str)
            
            # Find student
            student_exists = ((df["Id"].astype(str) == student_id) & 
                            (df["Name"].str.lower() == student_name.lower())).any()
            
            if student_exists:
                # Remove student from dataframe
                df = df[~((df["Id"].astype(str) == student_id) & 
                         (df["Name"].str.lower() == student_name.lower()))]
                
                # Save updated CSV
                df.to_csv(student_file, index=False)
                deleted_items.append("Student record from CSV")
                print(f"✅ Removed {student_id} - {student_name} from student records")
            else:
                print(f"⚠️ Student {student_id} - {student_name} not found in records")
                
        except Exception as e:
            print(f"❌ Error updating student file: {e}")
    else:
        print("⚠️ No student records file found")
    
    # 2. Delete training images
    if os.path.exists(training_path):
        deleted_images = 0
        for filename in os.listdir(training_path):
            # Check if filename contains the student ID
            parts = filename.split(".")
            if len(parts) >= 3 and parts[1] == student_id:
                try:
                    os.remove(os.path.join(training_path, filename))
                    deleted_images += 1
                except Exception as e:
                    print(f"❌ Error deleting {filename}: {e}")
        
        if deleted_images > 0:
            deleted_items.append(f"{deleted_images} training images")
            print(f"✅ Deleted {deleted_images} training images")
        else:
            print(f"⚠️ No training images found for ID: {student_id}")
    else:
        print("⚠️ No training images folder found")
    
    # 3. Ask if user wants to retrain model
    if deleted_items:
        print(f"\n🗑️ Successfully deleted: {', '.join(deleted_items)}")
        print("\n⚠️ IMPORTANT: You should retrain the model now!")
        retrain = input("Do you want to retrain the model now? (y/n): ").lower()
        
        if retrain == 'y' or retrain == 'yes':
            print("🔄 Retraining model...")
            try:
                import train_image
                train_image.TrainImages()
            except Exception as e:
                print(f"❌ Error during retraining: {e}")
                print("💡 Please run option 3 (Train Images) manually from main menu")
        else:
            print("⚠️ Remember to retrain the model (option 3) before taking attendance!")
    else:
        print("❌ No data was deleted")
    
    print("\n" + "="*50)

def list_all_students():
    """Show all registered students"""
    print("\n=== ALL REGISTERED STUDENTS ===")
    
    student_file = os.path.join("StudentDetails", "StudentDetails.csv")
    
    if not os.path.exists(student_file):
        print("❌ No student records found!")
        return
    
    try:
        df = pd.read_csv(student_file, dtype=str)
        if df.empty:
            print("❌ No students registered!")
            return
        
        print(f"📋 Total students: {len(df)}")
        print("-" * 30)
        for index, row in df.iterrows():
            print(f"ID: {row['Id']} | Name: {row['Name']}")
        
    except Exception as e:
        print(f"❌ Error reading student file: {e}")

def delete_all_data():
    """Delete ALL student data - complete reset"""
    print("\n=== DELETE ALL STUDENT DATA ===")
    print("⚠️ WARNING: This will delete ALL students and training data!")
    
    confirm = input("Are you sure? Type 'DELETE ALL' to confirm: ")
    
    if confirm != "DELETE ALL":
        print("❌ Deletion cancelled")
        return
    
    deleted_items = []
    
    # Delete student records
    student_file = os.path.join("StudentDetails", "StudentDetails.csv")
    if os.path.exists(student_file):
        try:
            # Create empty CSV with headers
            import csv
            with open(student_file, 'w', newline='') as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow(["Id", "Name"])
            deleted_items.append("All student records")
        except Exception as e:
            print(f"❌ Error clearing student file: {e}")
    
    # Delete all training images
    training_path = "TrainingImage"
    if os.path.exists(training_path):
        deleted_images = 0
        for filename in os.listdir(training_path):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                try:
                    os.remove(os.path.join(training_path, filename))
                    deleted_images += 1
                except Exception as e:
                    print(f"❌ Error deleting {filename}: {e}")
        
        if deleted_images > 0:
            deleted_items.append(f"{deleted_images} training images")
    
    # Delete training model
    training_label_path = "TrainingImageLabel"
    if os.path.exists(training_label_path):
        model_files = ["Trainner.yml", "label_map.csv"]
        deleted_models = 0
        for model_file in model_files:
            file_path = os.path.join(training_label_path, model_file)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    deleted_models += 1
                except Exception as e:
                    print(f"❌ Error deleting {model_file}: {e}")
        
        if deleted_models > 0:
            deleted_items.append("Training model files")
    
    if deleted_items:
        print(f"✅ Successfully deleted: {', '.join(deleted_items)}")
        print("🔄 System reset complete! You can start fresh now.")
    else:
        print("⚠️ No data found to delete")

def main_delete_menu():
    """Main menu for delete operations"""
    while True:
        print("\n" + "="*50)
        print("🗑️ STUDENT DATA MANAGEMENT")
        print("="*50)
        print("[1] View All Students")
        print("[2] Delete Specific Student")
        print("[3] Delete ALL Student Data (Reset)")
        print("[4] Return to Main Menu")
        
        try:
            choice = int(input("\nEnter your choice (1-4): "))
            
            if choice == 1:
                list_all_students()
            elif choice == 2:
                delete_student()
            elif choice == 3:
                delete_all_data()
            elif choice == 4:
                print("Returning to main menu...")
                break
            else:
                print("❌ Invalid choice! Please enter 1-4")
                
        except ValueError:
            print("❌ Invalid input! Please enter a number 1-4")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main_delete_menu()