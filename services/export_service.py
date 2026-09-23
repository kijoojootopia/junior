"""국가별 화장품 수출 통계 조회."""

import json
from pathlib import Path


TRADE_FILE = Path(__file__).resolve().parent.parent / "data" / "export" / "trade_stats.json"


def get_trade_stats(country, hs_code=None):
    with TRADE_FILE.open(encoding="utf-8") as source:
        data = json.load(source)
    records = data.get("records", [])
    if not isinstance(records, list):
        raise ValueError("trade_stats.json의 records는 배열이어야 합니다.")
    totals = {}
    for row in records:
        if row["country"] == country and (hs_code is None or row["hs_code"] == hs_code):
            year = row["year"]
            totals[year] = totals.get(year, 0) + row["export_usd"]
    series = [{"year": year, "export_usd": totals[year]} for year in sorted(totals)]
    latest = series[-1] if series else None
    previous = series[-2] if len(series) > 1 and series[-2]["year"] == latest["year"] - 1 else None
    growth_pct = (round((latest["export_usd"] / previous["export_usd"] - 1) * 100, 2)
                  if previous and previous["export_usd"] > 0 else None)
    return {"country": country, "hs_code": hs_code, "series": series,
            "latest": latest, "growth_pct": growth_pct}
