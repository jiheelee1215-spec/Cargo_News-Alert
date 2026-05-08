import feedparser
import requests
import os

from newspaper import Article
from groq import Groq

KEYWORDS = [
    "Nvidia",
    "AI",
    "Samsung",
    "Hynix"
]

RSS_URL = "https://news.google.com/rss/search?q=AI&hl=en-US&gl=US&ceid=US:en"

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]

client = Groq(
    api_key=GROQ_API_KEY
)

feed = feedparser.parse(RSS_URL)

telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

sent = False

for entry in feed.entries[:5]:

    title = entry.title

    if any(keyword.lower() in title.lower() for keyword in KEYWORDS):

        try:

            text = f"""
            Title:
            {entry.title}
            
            Description:
            {entry.summary}
            """

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": """
                        이 뉴스 기사를 한국어로 3줄로 짧게 요약해줘.
                        조건 :
                        - 핵심만 3줄
                        - 쉬운 한국어
                        - 불필요한 설명 금지
                        """
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
                telegram_url,
                data={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": message
                }
            )

            print(f"전송 완료: {title}")

            sent = True

        except Exception as e:
            print("에러 발생:")
            print(str(e))

if not sent:
    print("키워드 뉴스 없음")
