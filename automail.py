# automail.py - Fixed version
import yagmail
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from getpass import getpass

def send_attendance_email():
    print("\n=== Email Configuration ===")
    
    # Get email details
    receiver = input("Enter receiver email address: ").strip()
    if not receiver:
        print("❌ Receiver email cannot be empty!")
        return
        
    sender_email = input("Enter sender email address: ").strip()
    if not sender_email:
        print("❌ Sender email cannot be empty!")
        return
    
    # Get password securely
    print("Enter sender email password (password will be hidden):")
    sender_password = getpass()
    if not sender_password:
        print("❌ Password cannot be empty!")
        return
    
    # Find the latest attendance file
    attendance_dir = "Attendance"
    if not os.path.exists(attendance_dir):
        print("❌ Error: No attendance directory found!")
        print("Please run attendance recognition first (option 4).")
        return
        
    files = [f for f in os.listdir(attendance_dir) 
             if f.startswith("Attendance_") and f.endswith(".csv")]
    if not files:
        print("❌ Error: No attendance files found!")
        print("Please run attendance recognition first (option 4).")
        return
        
    # Get the most recent file
    latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(attendance_dir, x)))
    filepath = os.path.join(attendance_dir, latest_file)
    
    print(f"📎 Sending file: {latest_file}")
    
    # Try yagmail first (simpler)
    try:
        print("🔄 Attempting to send email using yagmail...")
        yag = yagmail.SMTP(sender_email, sender_password)
        
        subject = "Attendance Report - " + latest_file.replace("Attendance_", "").replace(".csv", "")
        body = """Dear Recipient,

Please find the latest attendance report attached to this email.

The report contains the following information:
- Student ID and Name
- Date of attendance
- Time of attendance (or 'Absent' if not present)
- Attendance Status

Best regards,
Attendance System"""
        
        yag.send(
            to=receiver,
            subject=subject,
            contents=body,
            attachments=filepath
        )
        yag.close()
        print("✅ Email sent successfully using yagmail!")
        return
        
    except Exception as e:
        print(f"⚠️ yagmail failed: {e}")
        print("🔄 Trying alternative method...")
    
    # Fallback to smtplib
    try:
        print("🔄 Using standard SMTP method...")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver
        msg['Subject'] = "Attendance Report - " + latest_file.replace("Attendance_", "").replace(".csv", "")
        
        body = """Dear Recipient,

Please find the latest attendance report attached to this email.

The report contains the following information:
- Student ID and Name
- Date of attendance
- Time of attendance (or 'Absent' if not present)
- Attendance Status

Best regards,
Attendance System"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach file
        with open(filepath, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {latest_file}',
        )
        msg.attach(part)
        
        # Determine SMTP server based on email provider
        if 'gmail.com' in sender_email.lower():
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
        elif 'yahoo.com' in sender_email.lower():
            smtp_server = "smtp.mail.yahoo.com"
            smtp_port = 587
        elif 'outlook.com' in sender_email.lower() or 'hotmail.com' in sender_email.lower():
            smtp_server = "smtp-mail.outlook.com"
            smtp_port = 587
        else:
            smtp_server = input("Enter SMTP server (e.g., smtp.gmail.com): ").strip()
            smtp_port = int(input("Enter SMTP port (usually 587): ") or "587")
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver, text)
        server.quit()
        
        print("✅ Email sent successfully using SMTP!")
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure your email and password are correct")
        print("2. For Gmail users:")
        print("   - Enable 2-factor authentication")
        print("   - Generate an 'App Password' and use that instead of your regular password")
        print("   - Go to: Google Account > Security > App passwords")
        print("3. For other providers, check if 'Less secure app access' needs to be enabled")
        print("4. Make sure you have internet connection")
        print("5. Some corporate networks may block SMTP ports")

if __name__ == "__main__":
    send_attendance_email()