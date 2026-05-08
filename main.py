import feedparser
import requests
import os

KEYWORDS = ["AI","인공지능","챗GPT","삼성전자","하이닉스"]

RSS_URL = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

feed = feedparser.parse(RSS_URL)

url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

sent = False

for entry in feed.entries[:10]:

    title = entry.title

    if any(keyword.lower() in title.lower() for keyword in KEYWORDS):

        message = entry.link

        requests.post(
            url,
            data={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message
            }
        )

        sent = True

if sent:
    print("링크 전송 완료")
else:
    print("키워드 뉴스 없음")
