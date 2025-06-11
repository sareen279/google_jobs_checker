import hashlib
import os
import requests
import smtplib
import difflib
from bs4 import BeautifulSoup, Comment
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# === Configuration ===
URL = "https://www.google.com/about/careers/applications/jobs/results/?q=%22Data%20Engineer%22&location=India"
HASH_FILE = "page_hash.txt"
CONTENT_FILE = "previous_content.txt"
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

def get_page_content_and_hash():
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    texts = soup.findAll(string=True)

    visible_texts = filter(is_visible_text, texts)

    # Normalize and clean
    cleaned_lines = [
        " ".join(line.strip().split())
        for line in visible_texts
        if len(line.strip()) > 15
    ]

    cleaned_lines.sort()
    content = "\n".join(cleaned_lines)

    return content, hashlib.sha256(content.encode()).hexdigest()

def generate_diff(old_content, new_content):
    old_lines = old_content.splitlines()
    new_lines = new_content.splitlines()
    diff = difflib.unified_diff(
        old_lines, new_lines,
        fromfile='Previous',
        tofile='Current',
        lineterm=''
    )
    return "\n".join(diff)

def send_email_alert(content, diff_text):
    subject = "🔔 Google Careers Page Changed"
    body = f"""The Google job page for 'Data Engineer - India' has changed.

URL: {URL}

=====================
VISIBLE CONTENT DIFF:
=====================

{diff_text[:3000]}...
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
        print("✅ Alert email sent with diff.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# === Main Logic ===

def main():
    new_content, new_hash = get_page_content_and_hash()

    try:
        with open(HASH_FILE, 'r') as f:
            old_hash = f.read().strip()
    except FileNotFoundError:
        old_hash = ''
        print("⚠️ No previous hash found. First run.")

    if new_hash != old_hash:
        print("🚨 Change detected!")

        try:
            with open(CONTENT_FILE, 'r') as f:
                old_content = f.read()
        except FileNotFoundError:
            old_content = ''
            print("⚠️ No previous content found.")

        diff = generate_diff(old_content, new_content)
        send_email_alert(new_content, diff)

        with open(HASH_FILE, 'w') as f:
            f.write(new_hash)
        with open(CONTENT_FILE, 'w') as f:
            f.write(new_content)

    else:
        print("✅ No change detected.")

if __name__ == "__main__":
    main()
