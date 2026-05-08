import feedparser
import requests
import os

KEYWORDS = ["AI"]

RSS_URL = "https://news.google.com/rss/search?q=AI&hl=ko&gl=KR&ceid=KR:ko"

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

feed = feedparser.parse(RSS_URL)

found_articles = []

for entry in feed.entries:

    title = entry.title

    if any(keyword.lower() in title.lower() for keyword in KEYWORDS):

        found_articles.append(
            f"📰 {title}\n{entry.link}"
        )

message = "테스트 메시지"

url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

requests.post(
    url,
    data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
)

print("텔레그램 전송 완료")

 
