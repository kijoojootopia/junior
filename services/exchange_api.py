import os
import requests
from datetime import datetime, timedelta

EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY")

# --- 캐시 보관소 (메모리 변수) ---
CACHE_RATES = None
CACHE_EXPIRY = None

def get_current_exchange_rates():
    """
    USD, EUR, RUB 환율을 반환하며, 1시간 동안 로컬 메모리에 캐싱합니다.
    """
    global CACHE_RATES, CACHE_EXPIRY
    
    # 1. 유효한 캐시가 남아있는 경우, 외부 API 호출 없이 즉시 반환
    now = datetime.now()
    if CACHE_RATES and CACHE_EXPIRY and now < CACHE_EXPIRY:
        return CACHE_RATES

    # 2. 캐시가 없거나 만료된 경우 API 호출
    today_str = now.strftime("%Y%m%d")
    url = "https://oapi.koreaexim.go.kr/site/program/financial/exchangeJSON"
    params = {
        "authkey": EXCHANGE_API_KEY,
        "searchdate": today_str,
        "data": "AP01"
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        rates = {}

        if isinstance(data, list):
            for item in data:
                cur_unit = item.get("cur_unit")
                if cur_unit in ["USD", "EUR", "RUB"]:
                    # 쉼표(,) 제거 후 실수(float) 변환
                    deal_bas_r = item.get("deal_bas_r", "0").replace(",", "")
                    rates[cur_unit] = float(deal_bas_r)

        # 데이터가 정상 수집되었으면 캐시에 1시간(60분) 저장
        if rates and len(rates) >= 3:
            CACHE_RATES = rates
            CACHE_EXPIRY = now + timedelta(hours=1)
            return CACHE_RATES

        # 주말/영업일 11시 이전이라 비어있는 경우 기본값 사용
        fallback = {"USD": 1330.0, "EUR": 1450.0, "RUB": 14.5}
        return fallback

    except Exception as e:
        print(f"[환율 API 에러] {e}")
        # 에러 발생 시 기존 캐시가 있으면 쓰고, 없으면 기본값 반환
        return CACHE_RATES if CACHE_RATES else {"USD": 1330.0, "EUR": 1450.0, "RUB": 14.5}