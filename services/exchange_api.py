# 한국수출입은행 환율 API

import os
import requests
from datetime import datetime

EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY")

def get_current_exchange_rates():
    """USD, EUR, RUB 환율을 딕셔너리로 반환"""
    today_str = datetime.now().strftime("%Y%m%d")
    url = "https://www.koreaexim.go.kr/site/program/financial/exchangeJSON"
    params = {
        "authkey": EXCHANGE_API_KEY,
        "searchdate": today_str,
        "data": "AP01"
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        rates = {}
        # 영업일/시간 외에는 데이터가 비어있을 수 있으므로 기본값 세팅
        for item in data:
            if item.get("cur_unit") in ["USD", "EUR", "RUB"]:
                # 쉼표 제거 후 float 변환
                deal_bas_r = item.get("deal_bas_r", "0").replace(",", "")
                rates[item.get("cur_unit")] = float(deal_bas_r)
        return rates if rates else {"USD": 1330.0, "EUR": 1450.0, "RUB": 14.5}
    except Exception as e:
        print(f"[환율 API 에러] {e}")
        # 오류 발생 시 기본 Fallback 환율 반환
        return {"USD": 1330.0, "EUR": 1450.0, "RUB": 14.5}