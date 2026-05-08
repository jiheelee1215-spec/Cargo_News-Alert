import feedparser
import requests
import os
from newspaper import Article
from groq import Groq

# ✅ 키워드 목록
KEYWORDS = [
    "Eng Kong",
    "EKH",
    "Navis Capital",
    "永康"
]

# ✅ 국가별 구글 뉴스 RSS URL
RSS_SOURCES = {
    "🇺🇸 미국": "https://news.google.com/rss/search?q=AI&hl=en-US&gl=US&ceid=US:en",
    "🇰🇷 한국": "https://news.google.com/rss/search?q=AI&hl=ko&gl=KR&ceid=KR:ko",
    "🇸🇬 싱가포르": "https://news.google.com/rss/search?q=AI&hl=en-SG&gl=SG&ceid=SG:en",
    "🇨🇳 중국": "https://news.google.com/rss/search?q=AI&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
}

# ✅ 환경 변수
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]

client = Groq(api_key=GROQ_API_KEY)
telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

sent = False

# ✅ 각 국가별 뉴스 피드 순회
for country, rss_url in RSS_SOURCES.items():
    feed = feedparser.parse(rss_url)
    print(f"📡 {country} 뉴스 {len(feed.entries)}개 확인 중...")

    for entry in feed.entries[:5]:  # 각 나라당 최대 5개 기사
        title = entry.title

        try:
            article = Article(entry.link)
            article.download()
            article.parse()

            # ✅ 키워드 포함 여부 확인
            if any(keyword.lower() in (title.lower() + article.text.lower()) for keyword in KEYWORDS):
                text = f"""
                Title:
                {entry.title}

                Description:
                {entry.summary}

                Content:
                {article.text[:3000]}
                """

                # ✅ 요약 요청 (한국어 3줄)
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

                summary = response.choices[0].message.content.strip()

                # ✅ 텔레그램 메시지 포맷
                message = f"""
📰 {title}

{summary}

🌏 출처: {country} 뉴스
🔗 {entry.link}
"""

                requests.post(
                    telegram_url,
                    data={
                        "chat_id": TELEGRAM_CHAT_ID,
                        "text": message
                    }
                )

                print(f"✅ 전송 완료: {country} | {title}")
                sent = True

        except Exception as e:
            print(f"❌ {country} 뉴스 처리 중 에러:", str(e))

if not sent:
    print("🔍 키워드 뉴스 없음")
