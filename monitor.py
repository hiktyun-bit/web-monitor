import json
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
import requests
import pytz

# GitHub Secrets에서 환경변수 불러오기
TARGET_URL = os.environ.get("TARGET_URL")
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")
TO_EMAIL = os.environ.get("TO_EMAIL")

# 🔍 감지할 단어 리스트
KEYWORDS = ["승아", "연아", "이솔", "다인"]

LOG_FILE = "sent_log.json"


def get_kr_date():
    """한국 표준시(KST) 기준 오늘 날짜(YYYY-MM-DD)를 반환합니다."""
    kr_tz = pytz.timezone("Asia/Seoul")
    return datetime.now(kr_tz).strftime("%Y-%m-%d")


def load_sent_log():
    """발송 기록 파일(sent_log.json)을 로드합니다. 날짜가 바뀌었으면 초기화합니다."""
    today = get_kr_date()

    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 기록된 날짜가 오늘과 같으면 기존 기록 사용
                if data.get("date") == today:
                    return data
        except Exception as e:
            print(f"기록 파일 로드 실패: {e}")

    # 파일이 없거나 날짜가 지난 경우 오늘 날짜로 초기화
    return {"date": today, "sent_keywords": []}


def save_sent_log(log_data):
    """발송 기록을 파일에 저장합니다."""
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
        print("발송 기록 저장 완료.")
    except Exception as e:
        print(f"기록 파일 저장 실패: {e}")


def send_email(new_keywords):
    """새로 발견된 키워드 정보를 포함하여 이메일을 발송합니다."""
    found_str = ", ".join(new_keywords)
    subject = f"[알림] API에서 신규 키워드 감지: [{found_str}]"
    body = (
        f"지정한 키워드가 오늘 처음으로 감지되었습니다.\n"
        f"(해당 키워드는 오늘 자정까지 추가 알림이 발송되지 않습니다.)\n\n"
        f"- 새로 감지된 키워드: {found_str}\n"
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
        print(f"이메일 발송 완료! (새로 발송된 키워드: {found_str})")
    except Exception as e:
        print(f"이메일 발송 실패: {e}")


def check_website():
    log_data = load_sent_log()
    already_sent = log_data["sent_keywords"]

    # 오늘 아직 메일을 안 보낸 단어들만 검사 대상으로 지정
    targets_to_check = [kw for kw in KEYWORDS if kw not in already_sent]

    if not targets_to_check:
        print(f"오늘 설정된 모든 키워드({KEYWORDS})가 이미 발송되었습니다. 검사를 스킵합니다.")
        return

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    try:
        print(f"[{TARGET_URL}] 요청 송신 중... (검사 대상: {targets_to_check})")
        response = requests.get(TARGET_URL, headers=headers, timeout=15)
        response.raise_for_status()

        response.encoding = response.apparent_encoding or "utf-8"
        response_text = response.text

        # 미발송 키워드 중 페이지에 존재하는 키워드 찾기
        newly_found = [kw for kw in targets_to_check if kw in response_text]

        if newly_found:
            print(f"새로운 키워드 발견: {newly_found}")
            send_email(newly_found)

            # 기록 업데이트 및 저장
            log_data["sent_keywords"].extend(newly_found)
            save_sent_log(log_data)
        else:
            print(f"새로 발견된 키워드 없음. (이미 발송된 키워드: {already_sent})")

    except Exception as e:
        print(f"요청 중 오류 발생: {e}")


if __name__ == "__main__":
    check_website()
