import os
import json
import re
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'travel-planner-default-secret')

# 시스템 프롬프트: 여행 플래너 AI
SYSTEM_PROMPT = """
당신은 전 세계 여행 트렌드와 현지 핫플레이스, 최적의 동선 설계에 정통한 최고 수준의 'AI 여행 컨설턴트'입니다.
사용자가 입력한 여행지, 여행 기간, 스타일, 동행자, 예산 및 요구사항을 종합적으로 분석하여 완벽한 여행 일정을 추천해야 합니다.

반드시 오직 아래 스키마에 맞는 유효한 JSON 형식(Markdown 백틱 제외, 순수 JSON만)으로 응답하세요:
{
  "title": "여행 일정 제목 (예: 감성 충만 오사카 미식 3박 4일 여행)",
  "destination": "여행지",
  "duration": "여행 기간",
  "summary": "이번 일정의 핵심 테마 및 요약 설명 (2-3문장)",
  "estimated_budget": "예상 1인 예산 가이드",
  "daily_plans": [
    {
      "day": 1,
      "theme": "해당 일차의 테마 (예: 설레는 도착과 도톤보리 야경 투어)",
      "schedule": [
        {
          "time": "10:00",
          "place": "장소명",
          "category": "명소 | 맛집 | 카페 | 쇼핑 | 휴식 | 액티비티 | 교통 중 하나",
          "description": "구체적인 즐길 거리, 추천 메뉴, 활동 설명",
          "tip": "현지 이용 꿀팁, 대기시간 최소화 팁 등"
        }
      ]
    }
  ],
  "packing_list": [
    {"item": "준비물 항목", "essential": true 또는 false}
  ],
  "travel_tips": [
    "현지 여행 시 꼭 알아야 할 실용적인 꿀팁 3~5개"
  ]
}

주의사항:
1. 이동 동선이 비효율적으로 꼬이지 않도록 시간대별(오전, 점심, 오후, 저녁, 밤) 순서대로 자연스럽게 배치하세요.
2. 각 일자별 최소 3~5개의 세부 스케줄을 포함하세요.
3. 사용자의 요청사항(스타일, 동행자, 예산 등)을 섬세하게 반영하세요.
4. 순수한 JSON 문자열만 출력하세요. 불필요한 서론이나 결론 문구를 덧붙이지 마세요.
"""

def clean_json_response(raw_text: str) -> dict:
    """LLM 응답에서 JSON 문자열만 추출하여 파싱"""
    text = raw_text.strip()
    # 마크다운 코드 블록 제거
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    
    # 중괄호 영역 추출
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        text = json_match.group(0)
        
    return json.loads(text)

def generate_mock_plan(destination, duration, styles, companion, budget, notes):
    """API 키가 없거나 호출 실패 시 제공하는 정교한 목업 일정 데이터"""
    style_str = ", ".join(styles) if styles else "힐링 및 관광"
    return {
        "title": f"✨ 맞춤형 {destination} {duration} 여행 코스",
        "destination": destination,
        "duration": duration,
        "summary": f"{companion}와(과) 함께 떠나는 {destination} 여행! {style_str} 콘셉트로 알차고 여유롭게 구성된 추천 일정입니다.",
        "estimated_budget": f"1인 기준 약 {budget} 수준에 맞춘 가성비 & 만족도 중심 코스",
        "daily_plans": [
            {
                "day": 1,
                "theme": f"설레는 첫 만남 & {destination} 핵심 랜드마크",
                "schedule": [
                    {
                        "time": "10:30",
                        "place": f"{destination} 도착 및 체크인/짐 보관",
                        "category": "교통",
                        "description": "숙소에 짐을 맡겨 몸을 가볍게 한 뒤 첫 여정을 시작합니다.",
                        "tip": "숙소 위치에 따라 얼리 체크인이 가능한지 사전에 확인해보세요."
                    },
                    {
                        "time": "12:30",
                        "place": f"{destination} 대표 로컬 맛집",
                        "category": "맛집",
                        "description": "현지인들이 즐겨 찾는 시그니처 대표 메뉴로 든든한 점심 식사를 즐깁니다.",
                        "tip": "피크 타임(12시~1시) 전후로 방문하면 웨이팅을 줄일 수 있습니다."
                    },
                    {
                        "time": "14:30",
                        "place": f"{destination} 뷰 맛집 감성 카페",
                        "category": "카페",
                        "description": "현지 특색이 담긴 시그니처 음료와 디저트를 맛보며 여유로운 티타임.",
                        "tip": "창가 자리 또는 테라스 석이 사진 명당입니다."
                    },
                    {
                        "time": "16:30",
                        "place": f"{destination} 주요 랜드마크 명소",
                        "category": "명소",
                        "description": "지역을 대표하는 명소를 거닐며 기념사진을 남기고 주변 풍경을 감상합니다.",
                        "tip": "일몰 1시간 전에 도착하면 노을 뷰까지 함께 만끽할 수 있습니다."
                    },
                    {
                        "time": "19:00",
                        "place": f"{destination} 야경 명소 & 로컬 디너",
                        "category": "맛집",
                        "description": "밤 풍경이 아름다운 거리에서 로컬 특식과 함께 하루를 마무리합니다.",
                        "tip": "예약이 필요한 식당의 경우 당일 점심 이전에 문의해두세요."
                    }
                ]
            },
            {
                "day": 2,
                "theme": f"오감 만족 로컬 문화 & {style_str} 집중 데이",
                "schedule": [
                    {
                        "time": "09:30",
                        "place": "상쾌한 아침 산책로 / 정원",
                        "category": "휴식",
                        "description": "맑은 공기를 마시며 힐링할 수 있는 자연 친화적 쉼터 방문.",
                        "tip": "아침 시간대는 인파가 적어 한적하게 둘러보기 좋습니다."
                    },
                    {
                        "time": "12:00",
                        "place": "특색 있는 로컬 브런치 / 별미 식당",
                        "category": "맛집",
                        "description": "정갈하고 깔끔한 지역 전통 또는 트렌디한 메뉴 즐기기.",
                        "tip": "인기 사이드 메뉴도 함께 곁들여보세요."
                    },
                    {
                        "time": "14:00",
                        "place": "쇼핑 거리 & 문화 체험 공간",
                        "category": "쇼핑",
                        "description": "지역 특산품, 기념품 굿즈 및 소품샵 쇼핑 투어.",
                        "tip": "가벼운 쇼핑백이나 에코백을 지참하면 편리합니다."
                    },
                    {
                        "time": "18:00",
                        "place": "인기 야시장 / 로컬 펍",
                        "category": "명소",
                        "description": "활기찬 현지 분위기를 느끼며 다양한 길거리 음식과 음료 즐기기.",
                        "tip": "현금 결제만 가능한 곳이 있을 수 있으니 소액 현금을 준비하세요."
                    }
                ]
            }
        ],
        "packing_list": [
            {"item": "신분증 / 여권 (해외일 경우)", "essential": True},
            {"item": "보조배터리 및 충전 케이블", "essential": True},
            {"item": "편안한 워킹화 / 운동화", "essential": True},
            {"item": "계절에 맞는 겉옷 / 우산", "essential": False},
            {"item": "상비약 (소화제, 진통제)", "essential": False}
        ],
        "travel_tips": [
            f"{destination} 현지 대중교통 패스 또는 렌터카 사전 예약을 추천합니다.",
            "주요 인기 명소 및 식당은 사전 예약 또는 원격 줄서기 앱을 활용하세요.",
            "휴무일(월요일 또는 특정 요일)을 방문 전 반드시 공식 지도에서 재확인하세요."
        ],
        "is_fallback": True
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate-plan', methods=['POST'])
def api_generate_plan():
    data = request.get_json() or {}
    destination = data.get('destination', '').strip()
    duration = data.get('duration', '2박 3일').strip()
    styles = data.get('styles', [])
    companion = data.get('companion', '혼자').strip()
    budget = data.get('budget', '표준/적당히').strip()
    notes = data.get('notes', '').strip()

    if not destination:
        return jsonify({"error": "여행지를 입력해주세요."}), 400

    api_key = os.getenv('GEMINI_API_KEY', '').strip()
    styles_str = ", ".join(styles) if styles else "힐링, 관광, 맛집"

    user_prompt = f"""
여행지: {destination}
여행 기간: {duration}
선호 여행 스타일: {styles_str}
동행자: {companion}
예산 수준: {budget}
특별 요청 사항: {notes if notes else '없음 (추천 위주로 구성해주세요)'}

위 조건에 꼭 맞는 세심하고 현실적인 맞춤 여행 계획을 완벽한 JSON 포맷으로 생성해주세요.
"""

    if not api_key or api_key == "your_gemini_api_key_here":
        mock_data = generate_mock_plan(destination, duration, styles, companion, budget, notes)
        return jsonify(mock_data)

    # 1. 최신 google.genai 시도
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
                response_mime_type="application/json"
            )
        )
        if response.text:
            plan_json = clean_json_response(response.text)
            plan_json['is_fallback'] = False
            return jsonify(plan_json)
    except Exception as e:
        print(f"[google.genai 호출 에러]: {e}")

    # 2. google.generativeai 구버전 라이브러리 폴백 시도
    try:
        import google.generativeai as genai_legacy
        genai_legacy.configure(api_key=api_key)
        model = genai_legacy.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT,
            generation_config={"response_mime_type": "application/json"}
        )
        response = model.generate_content(user_prompt)
        if response.text:
            plan_json = clean_json_response(response.text)
            plan_json['is_fallback'] = False
            return jsonify(plan_json)
    except Exception as e_legacy:
        print(f"[google.generativeai 호출 에러]: {e_legacy}")

    # 3. API 호출 실패 시에도 서비스 중단 없이 스마트 Mockup 반환
    fallback_data = generate_mock_plan(destination, duration, styles, companion, budget, notes)
    return jsonify(fallback_data)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
