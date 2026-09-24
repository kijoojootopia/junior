import os
import math
import requests
from datetime import datetime, timedelta, timezone

EXCHANGERATE_API_KEY = os.getenv("EXCHANGERATE_API_KEY")

# --- 캐시 보관소 (메모리 변수) ---
CACHE_RATES = None
CACHE_EXPIRY = None

def get_current_exchange_rates():
    """
    ExchangeRate-API 환율을 원화로 환산하고 제공기관의 다음 갱신 시각까지 캐싱합니다.
    """
    global CACHE_RATES, CACHE_EXPIRY
    
    # 1. 유효한 캐시가 남아있는 경우, 외부 API 호출 없이 즉시 반환
    now = datetime.now(timezone(timedelta(hours=9)))
    if CACHE_RATES and CACHE_EXPIRY and now < CACHE_EXPIRY:
        return CACHE_RATES

    rates = dict.fromkeys(('USD', 'EUR', 'RUB', 'AED'))
    rates.update(as_of=None, updated_at=None, message=None)
    if not EXCHANGERATE_API_KEY:
        rates['message'] = 'EXCHANGERATE_API_KEY가 설정되지 않았습니다.'
        return rates

    # 2. 캐시가 없거나 만료된 경우 API 호출
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API_KEY}/latest/USD"

    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if isinstance(data, dict) and data.get('result') == 'error':
            rates['message'] = {
                'invalid-key': '환율 API 인증키가 유효하지 않습니다.',
                'inactive-account': 'ExchangeRate-API 계정의 이메일 인증을 완료해 주세요.',
                'quota-reached': '환율 API의 요청 한도를 초과했습니다.',
            }.get(data.get('error-type'), '환율 제공기관이 오류를 반환했습니다.')
            return rates
        response.raise_for_status()
        if not isinstance(data, dict) or data.get('result') != 'success' or data.get('base_code') != 'USD':
            raise ValueError('Unexpected exchange rate response')
        conversions = data.get('conversion_rates')
        if not isinstance(conversions, dict):
            raise ValueError('Missing conversion rates')
        krw = float(conversions.get('KRW', 0))
        if not math.isfinite(krw) or krw <= 0:
            raise ValueError('Invalid KRW rate')
        timestamp = float(data['time_last_update_unix'])
        if not math.isfinite(timestamp) or timestamp <= 0:
            raise ValueError('Invalid update time')
        updated = datetime.fromtimestamp(timestamp, tz=now.tzinfo)

        # 응답은 1 USD 기준이므로 KRW / 해당 통화의 비율로 1 외화당 원화를 구합니다.
        for currency in ('USD', 'EUR', 'RUB', 'AED'):
            try:
                value = float(conversions.get(currency, 0))
            except (TypeError, ValueError):
                continue
            if math.isfinite(value) and value > 0 and math.isfinite(krw / value):
                rates[currency] = krw / value
        if not any(rates[currency] is not None for currency in ('USD', 'EUR', 'RUB', 'AED')):
            rates['message'] = '표시할 통화의 환율 자료가 없습니다.'
            return rates
        rates['as_of'] = updated.strftime('%Y/%m/%d')
        rates['updated_at'] = updated.strftime('%Y/%m/%d %H:%M KST')

        # 다음 갱신 시각이 누락되거나 이미 지났으면 5분 후 다시 조회합니다.
        expiry = now + timedelta(minutes=5)
        try:
            next_update = datetime.fromtimestamp(float(data['time_next_update_unix']), tz=now.tzinfo)
            if next_update > now:
                expiry = next_update
        except (KeyError, TypeError, ValueError, OverflowError, OSError):
            pass
        CACHE_RATES = rates
        CACHE_EXPIRY = expiry

    except (requests.RequestException, KeyError, TypeError, ValueError, OverflowError, OSError) as error:
        # 오류 메시지에 요청 URL의 인증키가 포함될 수 있어 오류 종류만 기록합니다.
        print(f"[환율 API 에러] {type(error).__name__}")
        rates['message'] = '환율 제공기관에 연결하지 못했거나 응답을 읽지 못했습니다. 잠시 후 다시 확인해 주세요.'

    return rates
