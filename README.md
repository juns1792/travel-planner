# ✈️ AI 트래블 플래너 (Travel Planner)

Google Gemini 기반 맞춤형 여행 일정 설계 웹 애플리케이션입니다.  
사용자의 여행지, 기간, 스타일, 동행자, 예산에 맞춰 최적의 동선과 시간대별 일정, 추천 맛집/명소, 준비물 체크리스트를 자동으로 생성해 줍니다.

---

## 🌟 주요 기능
- **맞춤형 일정 생성**: 여행지, 여행 기간(당일치기~일주일), 여행 스타일(힐링, 맛집, 관광, 액티비티, 쇼핑 등), 동행자, 예산에 따른 코스 설계
- **일자별 타임라인**: Day 1, Day 2 등 탭으로 구분된 시간대별 상세 동선 및 현지 방문 팁
- **준비물 체크리스트**: 여행 필수품 및 추천 준비물 대화형 체크리스트
- **현지 꿀팁 제공**: 교통 패스, 예약 팁, 주의사항 등 유용한 여행 가이드
- **편의 기능**: 전체 일정 클립보드 원클릭 복사 & 일정 인쇄/PDF 저장 지원

---

## 🛠 기술 스택
- **Backend**: Python 3.10+, Flask
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla ES6), Bootstrap 5, Font Awesome
- **AI Model**: Google Gemini API (`gemini-2.5-flash` / `gemini-1.5-flash`)

---

## 🚀 시작하기

### 1. 레포지토리 클론
```bash
git clone https://github.com/your-username/travel-planner.git
cd travel-planner
```

### 2. 가상환경 생성 및 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정 (.env)
`.env.example` 파일을 복사하여 `.env` 파일을 생성하고 본인의 Gemini API 키를 입력합니다:
```bash
# Windows
copy .env.example .env

# Mac / Linux
cp .env.example .env
```

`.env` 파일 내용:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
PORT=5000
SECRET_KEY=your_secret_key_here
```
> ⚠️ **주의**: `.env` 파일은 개인 API 키가 포함되어 있으므로 절대 GitHub에 커밋하거나 공개하지 마세요! (.gitignore에 이미 등록되어 있습니다)

### 4. 서버 실행
```bash
python app.py
```
브라우저에서 `http://localhost:5000`으로 접속하여 사용합니다.
