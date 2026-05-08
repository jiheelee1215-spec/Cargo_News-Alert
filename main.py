import feedparser
import requests
import os
from newspaper import Article
from groq import Groq

# ✅ 1️⃣ 키워드 목록
KEYWORDS = [
    "Nvidia",
    "Samsung",
    "Eng Kong",
    "EKH",
    "Navis Capital",
    "永康"
]

# ✅ 2️⃣ 여러 국가의 구글 뉴스 RSS URL
RSS_URLS = [
    # 미국 (영어)
    "https://news.google.com/rss/search?q=AI&hl=en-US&gl=US&ceid=US:en",

    # 한국 (한국어)
    "https://news.google.com/rss/search?q=AI&hl=ko&gl=KR&ceid=KR:ko",

    # 싱가포르 (영어)
    "https://news.google.com/rss/search?q=AI&hl=en-SG&gl=SG&ceid=SG:en",

    # 중국 (간체)
    "https://news.google.com/rss/search?q=AI&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
]

# ✅ 3️⃣ 환경변수
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]

client = Groq(api_key=GROQ_API_KEY)
telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

sent = False

# ✅ 4️⃣ 각 국가별 뉴스 피드 순회
for rss_url in RSS_URLS:
    feed = feedparser.parse(rss_url)
    print(f"📡 {rss_url} 뉴스 {len(feed.entries)}개 확인 중...")

    for entry in feed.entries[:5]:  # 각 국가당 최신 5개 기사만
        title = entry.title

        try:
            article = Article(entry.link)
            article.download()
            article.parse()

            # ✅ 제목 + 본문에 키워드가 포함된 기사만 필터
            if any(keyword.lower() in (title.lower() + article.text.lower()) for keyword in KEYWORDS):
                text = f"""
                Title:
                {entry.title}
                
                Description:
                {entry.summary}
                
                Content:
                {article.text[:3000]}
                """

                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {
                            "role": "system",
                            "content": """
                            이 뉴스 기사를 한국어로 3줄로 요약해줘.
                            조건:
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
🌍 Source: {rss_url}
"""

                requests.post(
                    telegram_url,
                    data={
                        "chat_id": TELEGRAM_CHAT_ID,
                        "text": message
                    }
                )

                print(f"✅ 전송 완료: {title}")
                sent = True

        except Exception as e:
            print("❌ 에러 발생:", str(e))

if not sent:
    print("🔍 키워드 뉴스 없음")
