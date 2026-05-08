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

if found_articles:

    message = "\n\n".join(found_articles)

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }
    )

    print("텔레그램 전송 완료")

else:
    print("조건에 맞는 뉴스 없음")
 
