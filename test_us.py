import streamlit as st
import pandas as pd
import json
import re
import os
from openai import OpenAI

# -------------------------------------------------------------------
# 1. 페이지 설정 및 API 키 입력부 (에러 방지)
# -------------------------------------------------------------------
st.set_page_config(page_title="US 성분 스크리닝 엔진", page_icon="🧪", layout="wide")

st.sidebar.title("⚙️ 설정")
api_key = st.sidebar.text_input("OpenAI API Key를 입력하세요 (sk-...)", type="password")

if not api_key.startswith("sk-"):
    st.warning("👈 좌측 사이드바에 유효한 OpenAI API 키를 입력해야 스크리닝이 활성화됩니다.")
    st.stop() # 키가 없으면 아래 코드를 실행하지 않고 안전하게 멈춤

client = OpenAI(api_key=api_key)

# -------------------------------------------------------------------
# 2. 데이터 로드 및 판별 함수
# -------------------------------------------------------------------
@st.cache_data # 파일 읽기 속도 최적화
def load_restricted_ingredients():
    """US 성분 규제 JSON 파일 로드"""
    file_path = "data/us/restricted_ingredients.json"
    if not os.path.exists(file_path):
        st.error(f"⚠️ 규제 DB 파일이 없습니다. '{file_path}' 경로를 확인하세요.")
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_ingredients(raw_text):
    """LLM을 이용해 한국어 전성분을 영문(INCI)으로 자동 번역하여 JSON 배열로 추출"""
    prompt = f"""
    아래 화장품 전성분 텍스트에서 성분명만 추출해서 파이썬 리스트 형태의 JSON 배열(예: ["Water", "Glycerin", "1,2-Hexanediol"])로 반환해.
    
    핵심 지시사항: 
    1. 만약 입력된 성분명이 한국어라면, 반드시 국제 표준 명칭(INCI Name) 기준의 영문으로 완벽하게 번역해서 추출해.
    2. '1,2-Hexanediol'처럼 성분명 자체에 포함된 쉼표는 절대 분리하지 마.
    3. 응답은 반드시 `[` 로 시작하고 `]` 로 끝나는 JSON 포맷이어야 하며, 부연 설명은 절대 출력하지 마.
    
    텍스트: {raw_text}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        raw_result = response.choices[0].message.content.strip()
        
        if raw_result.startswith("```"):
            raw_result = raw_result.replace("```json", "").replace("```", "").strip()
            
        ingredients_list = json.loads(raw_result)
        
        return [ing.strip().lower() for ing in ingredients_list if ing.strip()]
    except Exception as e:
        st.error(f"LLM 텍스트 분석 중 오류가 발생했습니다: {e}")
        return []

def check_otc_status(ingredients, description):
    """FDA OTC (자외선 차단제 / 여드름) 규정 위반 여부 확인"""
    sun_actives = {"zinc oxide", "titanium dioxide", "avobenzone", "octinoxate", "oxybenzone", "octisalate", "octocrylene", "homosalate"}
    acne_actives = {"salicylic acid", "benzoyl peroxide", "sulfur", "resorcinol"}
    
    sun_claims = ["spf", "sunscreen", "broad spectrum", "sunblock"]
    acne_claims = ["acne", "blemish", "pimple"]
    
    desc_lower = description.lower()
    detected_otc = []
    
    # 선케어 검사
    if any(any(s in ing for s in sun_actives) for ing in ingredients) or any(c in desc_lower for c in sun_claims):
        detected_otc.append("Sunscreen OTC (FDA M020)")
        
    # 여드름 검사
    if any(any(a in ing for a in acne_actives) for ing in ingredients) or any(c in desc_lower for c in acne_claims):
        detected_otc.append("Acne OTC (FDA M006)")
        
    return detected_otc

# -------------------------------------------------------------------
# 3. 메인 대시보드 UI
# -------------------------------------------------------------------
st.title("🧪 미국(US) 화장품 성분 및 OTC 스크리닝")
st.markdown("전성분과 제품 설명을 입력하면, LLM이 성분을 분리하고 FDA DB 및 OTC 룰셋과 대조합니다.")

col1, col2 = st.columns(2)
with col1:
    raw_ingredients = st.text_area("📦 전성분표 텍스트 입력 (자유 양식)", height=150, 
                                   placeholder="예: Water, Glycerin, Titanium Dioxide, Salicylic Acid, 1,2-Hexanediol...")
with col2:
    raw_description = st.text_area("📝 제품 마케팅 설명 (OTC 클레임 감지용)", height=150, 
                                   placeholder="예: SPF 50+ Broad spectrum. Helps clear acne blemishes.")

if st.button("진단 시작", type="primary"):
    if not raw_ingredients:
        st.warning("전성분 텍스트를 입력해주세요.")
    else:
        with st.spinner("LLM이 성분을 분석하고 FDA 규정과 대조 중입니다..."):
            
            # 1. 성분 추출
            extracted_list = extract_ingredients(raw_ingredients)
            
            if extracted_list:
                st.success(f"✅ 총 {len(extracted_list)}개의 성분이 성공적으로 추출되었습니다.")
                st.write("**추출된 성분:**", ", ".join(extracted_list))
                
                # 2. OTC(일반의약품) 판별
                otc_results = check_otc_status(extracted_list, raw_description)
                if otc_results:
                    st.error(f"🚨 **OTC 주의:** 이 제품은 일반 화장품이 아닌 **일반의약품(OTC)**으로 분류될 위험이 있습니다! ({', '.join(otc_results)})")
                    st.info("💡 실무 가이드: 시설의 FDA Drug Establishment 등록 및 NDC 라벨링 획득 등 추가적인 파이프라인(Step 3)이 요구됩니다.")
                else:
                    st.success("✅ **OTC 통과:** 선케어 및 여드름 관련 의약품 규제에 해당하지 않는 일반 화장품입니다.")
                
                # 3. 착색제 및 배합 금지 성분 스크리닝
                st.markdown("---")
                st.subheader("📋 세부 성분 규제 스크리닝 결과")
                
                db_data = load_restricted_ingredients()
                match_results = []
                
                for ext_ing in extracted_list:
                    matched_item = next((item for item in db_data if item["inci_name"].lower() in ext_ing), None)
                    
                    if matched_item:
                        match_results.append({
                            "입력 성분": ext_ing,
                            "매칭된 DB 성분": matched_item["inci_name"],
                            "상태": matched_item["status"],
                            "조건 및 한도": matched_item["conditions"],
                            "근거": matched_item["regulation_source"]
                        })
                    else:
                        match_results.append({
                            "입력 성분": ext_ing,
                            "매칭된 DB 성분": "-",
                            "상태": "PASS",
                            "조건 및 한도": "일반 성분 (제한 없음)",
                            "근거": "-"
                        })
                
                # 결과 테이블 출력
                df_results = pd.DataFrame(match_results)
                
                # 표 스타일링 (RESTRICTED인 경우 빨간색 강조)
                def highlight_restricted(val):
                    color = '#ffcccc' if val == 'RESTRICTED' else ''
                    return f'background-color: {color}'
                    
                st.dataframe(df_results.style.map(highlight_restricted, subset=['상태']), use_container_width=True)