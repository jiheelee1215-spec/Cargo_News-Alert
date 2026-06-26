
# AI News Alert 🤖

특정 키워드 관련 뉴스를 자동으로 수집·요약하여  
텔레그램으로 실시간 알림을 제공하는 AI 기반 챗봇입니다.

---

## 📌 Overview
본 프로젝트는 Google News RSS를 기반으로 특정 키워드(예: 엔콩) 관련 뉴스를 수집하고,  
LLM(Groq API)을 활용해 핵심 내용을 요약한 뒤 Telegram Bot을 통해 전달하는 자동화 시스템입니다.

AI를 활용하여 반복적인 뉴스 검색 업무를 줄이고,  
보다 효율적으로 최신 동향을 파악하는 것을 목표로 합니다.

---

## 🚀 Features
- 🔍 키워드 기반 뉴스 자동 수집 (Google News RSS)
- 🧠 LLM 기반 뉴스 요약 (Groq API)
- 📩 텔레그램 알림 자동 발송
- ⏱ GitHub Actions 기반 스케줄 자동 실행
- 🌍 다국어 뉴스 모니터링 가능

---

## 🛠 Tech Stack
- Python
- Groq API (LLM)
- Telegram Bot API
- GitHub Actions
- RSS Feed (Google News)

---

## ⚙️ How It Works
1. 설정한 키워드 기반으로 Google News RSS에서 뉴스 수집
2. 수집된 뉴스 데이터를 LLM을 활용해 요약
3. 요약된 내용을 Telegram Bot으로 전송
4. GitHub Actions를 통해 정해진 시간마다 자동 실행

---

## 📷 Sample Output
(텔레그램으로 아래와 같은 형태로 뉴스 요약 알림이 전송됩니다)

- 기사 제목
- 요약 내용
- 원문 링크

---

## ✅ Expected Benefits
- 반복적인 뉴스 검색 업무 자동화
- 최신 정보 실시간 모니터링 가능
- 글로벌 뉴스 동향 효율적 파악
- 업무 생산성 향상
