import feedparser
import requests
import os

from newspaper import Article
from openai import OpenAI

KEYWORDS = [
    "OpenAI",
    "NVIDIA",
    "Anthropic"
]

RSS_URL = "https://news.google.com/rss/search?q=AI&hl=en-US&gl=US&ceid=US:en"

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

feed = feedparser.parse(RSS_URL)

url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

for entry in feed.entries[:3]:

    title = entry.title

    if any(keyword.lower() in title.lower() for keyword in KEYWORDS):

        try:

            article = Article(entry.link)
            article.download()
            article.parse()

            text = article.text[:4000]

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Summarize this news article in 3 short bullet points."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ]
            )

            summary = response.choices[0].message.content

            message = f"""
📰 {title}

{summary}

🔗 {entry.link}
"""

            requests.post(
                url,
                data={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": message
                }
            )

            print(f"전송 완료: {title}")

        except Exception as e:
            print(e)
