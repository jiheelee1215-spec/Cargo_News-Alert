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

# ✅ 2️⃣ 구글 뉴스 RSS URL
RSS_URL = "https://news.google.com/rss/search?q=AI&hl=en-US&gl=US&ceid=US:en"

# ✅ 3️⃣ 환경변수 불러오기
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]

# ✅ 4️⃣ Groq 클라이언트 생성
client = Groq(api_key=GROQ_API_KEY)

# ✅ 5️⃣ RSS 파싱
feed = feedparser.parse(RSS_URL)
telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

sent = False

# ✅ 6️⃣ 뉴스 루프
for entry in feed.entries[:5]:
    title = entry.title

    try:
        # 뉴스 본문 추출
        article = Article(entry.link)
        article.download()
        article.parse()

        # ✅ 제목 + 본문 둘 다에서 키워드 검색
        if any(keyword.lower() in (title.lower() + article.text.lower()) for keyword in KEYWORDS):

            # 요약할 텍스트 구성
            text = f"""
            Title:
            {entry.title}
            
            Description:
            {entry.summary}
            
            Content:
            {article.text[:3000]}
            """

            # ✅ Groq 모델로 요약 요청
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": """
                        이 뉴스 기사를 한국어로 3줄로 짧게 요약해줘.
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

            # ✅ 텔레그램 메시지 전송
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

# ✅ 7️⃣ 키워드 기사 없을 때 출력
if not sent:
    print("키워드 뉴스 없음")
