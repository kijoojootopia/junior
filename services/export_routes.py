"""화장품 해외 진출 화면과 국가별 통계 API."""

import re

from flask import Blueprint, jsonify, render_template, request

from services.export_service import get_trade_stats


export_bp = Blueprint("export", __name__)
REGIONS = {"US": "미국", "EU": "유럽(EU)", "EAC": "유라시아(EAEU)", "AE": "UAE"}
# 기존 지도 핀과 국가별 API는 화면·전체 수출 통계 전환을 마칠 때 정리합니다.
COUNTRIES = {"US": "미국", "DE": "독일", "FR": "프랑스", "RU": "러시아", "KZ": "카자흐스탄", "AE": "UAE"}


@export_bp.get("/export")
def dashboard():
    return render_template("export_dashboard.html", countries=REGIONS)


@export_bp.get("/api/export/trade")
def trade():
    country = request.args.get("country", "").upper()
    hs_code = request.args.get("hs_code") or None
    if country not in COUNTRIES and country not in REGIONS:
        return jsonify({"error": "지원하지 않는 국가 코드입니다."}), 400
    if hs_code and not re.fullmatch(r"\d{4,10}", hs_code):
        return jsonify({"error": "HS 코드는 4~10자리 숫자여야 합니다."}), 400
    return jsonify(get_trade_stats(country, hs_code))
