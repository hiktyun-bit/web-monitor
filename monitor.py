import os
import smtplib
from email.mime.text import MIMEText
import requests
from bs4 import BeautifulSoup

# Secrets에서 환경변수 불러오기
TARGET_URL = os.environ.get("TARGET_URL")
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")
TO_EMAIL = os.environ.get("TO_EMAIL")

# 🔍 웹페이지에서 감지할 특정 단어를 입력하세요
KEYWORD = "보라" 

def send_email():
    subject = f"[알림] 웹페이지에서 '{KEYWORD}' 단어가 감지되었습니다!"
    body = f"설정한 URL ({TARGET_URL})에서 키워드 '{KEYWORD}'를 찾았습니다.\n지금 페이지를 확인해 보세요."
    
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = TO_EMAIL

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, TO_EMAIL, msg.as_string())
        print("이메일 발송 완료!")
    except Exception as e:
        print(f"이메일 발송 실패: {e}")

def check_website():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 한글 깨짐 방지
        response.encoding = response.apparent_encoding
        
        soup = BeautifulSoup(response.text, "html.parser")
        text_content = soup.get_text()

        if KEYWORD in text_content:
            print(f"키워드 '{KEYWORD}' 발견!")
            send_email()
        else:
            print(f"키워드 '{KEYWORD}' 미발견.")

    except Exception as e:
        print(f"웹페이지 조회 중 오류 발생: {e}")

if __name__ == "__main__":
    check_website()
