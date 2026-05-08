import feedparser
import smtplib
import os
from email.mime.text import MIMEText

KEYWORDS = ["AI", "반도체", "엔비디아"]

RSS_URL = "https://news.google.com/rss/search?q=AI&hl=ko&gl=KR&ceid=KR:ko"

EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
TO_EMAIL = os.environ["TO_EMAIL"]

feed = feedparser.parse(RSS_URL)

found_articles = []

for entry in feed.entries:
    title = entry.title

    if any(keyword.lower() in title.lower() for keyword in KEYWORDS):
        found_articles.append(f"{title}\n{entry.link}")

if found_articles:

    body = "\n\n".join(found_articles)

    msg = MIMEText(body)

    msg["Subject"] = "뉴스 키워드 알림"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

    print("메일 발송 완료")

else:
    print("조건에 맞는 뉴스 없음")
