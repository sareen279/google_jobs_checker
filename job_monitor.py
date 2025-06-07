import hashlib
import requests
import smtplib
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

URL = "https://www.google.com/about/careers/applications/jobs/results/?q=%22Data%20Engineer%22&location=India"
HASH_FILE = "page_hash.txt"
EMAIL = "sareen279@gmail.com"

def get_page_hash():
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    content = soup.get_text()
    return hashlib.sha256(content.encode()).hexdigest()

def send_email_alert():
    sender = "your-email@gmail.com"
    password = "your-app-password"  # Use App Password, not regular Gmail password
    subject = "🔔 Google Careers Page Changed"
    body = f"The Google job page for 'Data Engineer - India' has changed.\n\nCheck here: {URL}"

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, EMAIL, msg.as_string())
        print("Alert sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    new_hash = get_page_hash()
    try:
        with open(HASH_FILE, 'r') as f:
            old_hash = f.read()
    except FileNotFoundError:
        old_hash = ''

    if new_hash != old_hash:
        print("Change detected!")
        send_email_alert()
        with open(HASH_FILE, 'w') as f:
            f.write(new_hash)
    else:
        print("No change detected.")

if __name__ == "__main__":
    main()
