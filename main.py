import feedparser
import requests
import os

KEYWORDS = [
    "AI",
    "OpenAI",
    "NVIDIA"
]

RSS_URL = "https://news.google.com/rss/search?q=AI&hl=en-US&gl=US&ceid=US:en"

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

feed = feedparser.parse(RSS_URL)

url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

sent = False

for entry in feed.entries[:20]:

    title = entry.title

    if any(keyword.lower() in title.lower() for keyword in KEYWORDS):

        message = f"📰 {title}\n{entry.link}"

        requests.post(
            url,
            data={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message
            }
        )

        sent = True

if sent:
    print("글로벌 뉴스 전송 완료")
else:
    print("키워드 뉴스 없음")
