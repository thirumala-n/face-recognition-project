# main.py - Fixed version
import os
import sys
import check_camera
import capture_image
import train_image
import recognize
import automail

def title_bar():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\t***** Face Recognition Attendance System *****")

def mainMenu():
    while True:
        title_bar()
        print("\n", "*"*10, "WELCOME MENU", "*"*10)
        print("[1] Check Camera")
        print("[2] Capture Faces")
        print("[3] Train Images")
        print("[4] Recognize & Attendance")
        print("[5] Auto Mail")
        print("[6] Update Student Images")
        print("[7] Delete Student Data")  
        print("[8] Quit")

        try:
            choice = int(input("Enter Choice: "))
            if choice == 1: 
                checkCamera()
            elif choice == 2: 
                CaptureFaces()
            elif choice == 3: 
                Trainimages()
            elif choice == 4: 
                recognizeFaces()
            elif choice == 5: 
                autoMail()
            elif choice == 6: 
                updateStudent()
            elif choice == 7: 
                deleteStudentData() 
            elif choice == 8:
                print("Thank You")
                break
            else: 
                print("Invalid Choice. Enter 1-8")
                input("Press Enter to continue...")
        except ValueError:
            print("Invalid Choice. Enter 1-8\nTry Again")
            input("Press Enter to continue...")

def checkCamera():
    check_camera.camer()
    input("Enter any key to return main menu: ")

def CaptureFaces():
    capture_image.takeImages()
    input("Enter any key to return main menu: ")

def updateStudent():
    capture_image.updateImages()
    input("Enter any key to return main menu: ")

def Trainimages():
    train_image.TrainImages()
    input("Enter any key to return main menu: ")

def recognizeFaces():
    recognize.recognize_attendance()
    input("Enter any key to return main menu: ")

def autoMail():
    automail.send_attendance_email()
    input("Enter any key to return main menu: ")

def deleteStudentData():
    import delete_student
    delete_student.main_delete_menu()
    input("Enter any key to return main menu: ")

if __name__ == "__main__":
    mainMenu()
