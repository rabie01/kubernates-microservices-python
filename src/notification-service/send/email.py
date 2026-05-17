import smtplib, os, json
from email.message import EmailMessage

def notification(message):
    try:
        message = json.loads(message)
        mp3_fid = message["mp3_fid"]
        sender_address = os.environ.get("GMAIL_ADDRESS")
        sender_password = os.environ.get("GMAIL_PASSWORD")
        receiver_address = message["username"]

        msg = EmailMessage()
        msg.set_content(f"mp3 file_id: {mp3_fid} is now ready!")
        msg["Subject"] = "MP3 Download"
        msg["From"] = sender_address
        msg["To"] = receiver_address

        session = smtplib.SMTP("smtp.gmail.com", 587)
        session.starttls()
        session.login(sender_address, sender_password)
        session.send_message(msg, sender_address, receiver_address)
        session.quit()
        
        print("EMail Sent")
        return None # 🚀 Success: No error to pass back
        
    except smtplib.SMTPAuthenticationError as e:
        # 🚀 Catches wrong passwords explicitly
        print(f"🔴 SMTP Auth Failed. Check your GMAIL_PASSWORD env var: {e}")
        return e 
    except Exception as e:
        # 🚀 Catches network drops or socket issues cleanly
        print(f"🔴 Email failed due to unexpected error: {e}")
        return e
