import feedparser
import requests
import os
import urllib.parse
from bs4 import BeautifulSoup
from newspaper import Article
from groq import Groq
import time
from datetime import datetime, timedelta

# ✅ 키워드 목록 (콤마 누락 수정)
KEYWORDS = [
    "Eng Kong",
    "EKH",
    "Navis Capital",
    "永康",
    "Tianjin Keyun",
    "天津科韵"
]

# ✅ 국가별 구글 뉴스 RSS URL (검색어 없이)
RSS_SOURCES = {
    "🇺🇸 미국": "https://news.google.com/rss/search?hl=en-US&gl=US&ceid=US:en",
    "🇰🇷 한국": "https://news.google.com/rss/search?hl=ko&gl=KR&ceid=KR:ko",
    "🇸🇬 싱가포르": "https://news.google.com/rss/search?hl=en-SG&gl=SG&ceid=SG:en",
    "🇨🇳 중국": "https://news.google.com/rss/search?hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
    "🇲🇾 말레이시아": "https://news.google.com/rss/search?hl=en-MY&gl=MY&ceid=MY:en"
}

# ✅ 환경 변수
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]

client = Groq(api_key=GROQ_API_KEY)
telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# ✅ 최근 24시간 내 기사만 알림
NOW = datetime.utcnow()
TIME_LIMIT = NOW - timedelta(hours=24)

sent = False

# ✅ 중복 기사 방지용 파일
HISTORY_FILE = "sent_links.txt"

# ✅ 이전에 전송된 링크 불러오기
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        sent_links = set(f.read().splitlines())
else:
    sent_links = set()

# ✅ 실행 중 중복 방지용
seen_links = set()

# ✅ 국가별 + 키워드별 RSS 순회
for country, base_rss_url in RSS_SOURCES.items():
    for keyword in KEYWORDS:
        encoded_keyword = urllib.parse.quote(keyword)
        rss_url = f"{base_rss_url}&q={encoded_keyword}"

        feed = feedparser.parse(rss_url)
        print(f"📡 {country} ({keyword}) 뉴스 {len(feed.entries)}개 확인 중...")

        for entry in feed.entries[:5]:
            title = entry.title
            link = entry.link

            # ✅ 중복 기사 필터링 (이전 실행 + 현재 실행)
            if link in sent_links or link in seen_links:
                print(f"⚠️ 중복 기사 건너뜀: {title}")
                continue
            seen_links.add(link)

            # ✅ 발행 시각 확인 (24시간 이내만)
            if hasattr(entry, "published_parsed"):
                published_time = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                if published_time < TIME_LIMIT:
                    print(f"⏩ 오래된 기사 건너뜀: {title} ({published_time})")
                    continue
            else:
                print(f"⚠️ 발행 시각 정보 없음, 스킵: {title}")
                continue

            try:
                # ✅ 1차: newspaper3k 파싱
                article = Article(entry.link)
                article.download()
                article.parse()
                content = article.text.strip()

                # ✅ 2차: 본문이 짧으면 BeautifulSoup 보완
                if len(content) < 300:
                    resp = requests.get(entry.link, headers={"User-Agent": "Mozilla/5.0"})
                    soup = BeautifulSoup(resp.text, "html.parser")
                    paragraphs = soup.find_all("p")
                    content = " ".join(p.get_text() for p in paragraphs if p.get_text())

                # ✅ 키워드 포함 기사만 처리
                if any(k.lower() in (title.lower() + content.lower()) for k in KEYWORDS):
                    text = f"""
                    Title:
                    {entry.title}

                    Description:
                    {entry.summary}

                    Content:
                    {content[:3000]}
                    """

                    # ✅ Groq API로 한국어 3줄 요약
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
🔍 키워드: {keyword}
🔗 {entry.link}
"""

                    # ✅ 텔레그램 전송
                    requests.post(
                        telegram_url,
                        data={
                            "chat_id": TELEGRAM_CHAT_ID,
                            "text": message
                        }
                    )

                    # ✅ 전송 완료 후 링크 저장
                    sent_links.add(link)

                    print(f"✅ 전송 완료: {country} | {keyword} | {title}")
                    sent = True

            except Exception as e:
                print(f"❌ {country} | {keyword} 뉴스 처리 중 에러:", str(e))

# ✅ 실행 종료 후 전송된 링크 기록 저장
with open(HISTORY_FILE, "w") as f:
    f.write("\n".join(sent_links))

if not sent:
    print("🔍 최근 24시간 내 키워드 관련 뉴스 없음")
