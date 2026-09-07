import os
import smtplib
from email.mime.text import MIMEText
import requests

# GitHub Secrets에서 환경변수 불러오기
TARGET_URL = os.environ.get("TARGET_URL")
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")
TO_EMAIL = os.environ.get("TO_EMAIL")

# 🔍 감지할 단어 리스트
KEYWORDS = ["승아", "연아", "이솔"]

# 🔍 감지 조건 설정 ("OR" = 하나만 있어도 알림 / "AND" = 모두 있어야 알림)
MATCH_OPTION = "OR"


def send_email(found_keywords):
    """발견된 키워드 정보를 포함하여 이메일을 발송합니다."""
    found_str = ", ".join(found_keywords)
    subject = f"[알림] API에서 키워드 감지: [{found_str}]"
    body = (
        f"설정한 API URL에서 지정한 키워드가 발견되었습니다.\n\n"
        f"- 감지된 키워드: {found_str}\n"
        f"- 타겟 URL: {TARGET_URL}\n\n"
        f"지금 바로 확인해 보세요."
    )
    
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = TO_EMAIL

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, TO_EMAIL, msg.as_string())
        print(f"이메일 발송 완료! (감지된 키워드: {found_str})")
    except Exception as e:
        print(f"이메일 발송 실패: {e}")


def check_website():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    try:
        print(f"[{TARGET_URL}] 요청 송신 중...")
        response = requests.get(TARGET_URL, headers=headers, timeout=15)
        response.raise_for_status()

        # 인코딩 처리
        response.encoding = response.apparent_encoding or 'utf-8'
        response_text = response.text

        # 키워드 검색
        found_keywords = [kw for kw in KEYWORDS if kw in response_text]

        # 조건 판별 (OR / AND)
        is_matched = False
        if MATCH_OPTION.upper() == "OR" and len(found_keywords) > 0:
            is_matched = True
        elif MATCH_OPTION.upper() == "AND" and len(found_keywords) == len(KEYWORDS):
            is_matched = True

        if is_matched:
            print(f"조건 만족! 발견된 키워드: {found_keywords}")
            send_email(found_keywords)
        else:
            print(f"조건 미충족. (찾은 키워드: {found_keywords} / 전체 설정 키워드: {KEYWORDS})")

    except Exception as e:
        print(f"요청 중 오류 발생: {e}")


if __name__ == "__main__":
    check_website()
