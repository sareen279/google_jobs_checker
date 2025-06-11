import hashlib
import os
import requests
import smtplib
from bs4 import BeautifulSoup, Comment
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# === Configuration ===
URL = "https://www.google.com/about/careers/applications/jobs/results/?q=%22Data%20Engineer%22&location=India"
HASH_FILE = "page_hash.txt"
sender = os.environ['SENDER_EMAIL']
password = os.environ['EMAIL_PASSWORD']
receiver = os.environ['RECEIVER_EMAIL']


# === Helpers ===
def is_visible_text(element):
    return (
        element.parent.name not in ['style', 'script', 'head', 'meta', '[document]']
        and not isinstance(element, Comment)
        and element.strip()
    )

def get_visible_text_from_page():
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    texts = soup.findAll(string=True)
    visible_texts = filter(is_visible_text, texts)
    return "\n".join(t.strip() for t in visible_texts if t.strip())

def get_page_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()

def send_email_alert(content: str):
    subject = "🔔 Google Careers Page Changed (Single Hash)"
    body = f"""
    The monitored Google job page for 'Data Engineer - India' has changed.

    URL: {URL}

    === New Visible Content ===
    {content[:2000]}...
    """

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        print("✅ Alert email sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")


# === Main Logic ===
def main():
    content = get_visible_text_from_page()
    new_hash = get_page_hash(content)

    try:
        with open(HASH_FILE, 'r') as f:
            old_hash = f.read().strip()
    except FileNotFoundError:
        old_hash = ''
        print("⚠️ No previous hash found (first run).")

    print(f"🧾 Old hash: {old_hash}")
    print(f"🆕 New hash: {new_hash}")

    if new_hash != old_hash:
        print("🚨 Change detected!")
        send_email_alert(content)
        with open(HASH_FILE, 'w') as f:
            f.write(new_hash)
    else:
        print("✅ No change detected.")


if __name__ == "__main__":
    main()
    
