# 성분 판정 엔진
import os
import json
import pandas as pd

def screen_ingredients(csv_file_path, target_region):
    # 1. 국가별 규제 JSON 파일 로드 (파일명 유연하게 대응)
    possible_files = [
        f"data/{target_region}/restricted_ingredients.json",
        f"data/{target_region}/prohibited_ingredients.json",
        f"data/{target_region}/ingredients.json"
    ]
    
    restricted_dict = {}
    for json_path in possible_files:
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        data_list = json.loads(content)
                        for item in data_list:
                            name = str(item.get("inci_name", "")).strip().lower()
                            if name:
                                restricted_dict[name] = item
                break
            except Exception as e:
                print(f"[JSON 읽기 오류] {e}")

    # 2. CSV 파일 읽기
    try:
        df = pd.read_csv(csv_file_path, encoding="utf-8-sig")
    except Exception:
        df = pd.read_csv(csv_file_path, encoding="cp949")

    results = []
    for _, row in df.iterrows():
        inci_raw = str(row.get("inci_name", "")).strip()
        if not inci_raw or inci_raw.lower() == "nan":
            continue
            
        inci_lower = inci_raw.lower()
        try:
            conc = float(str(row.get("concentration", 0.0)).replace("%", "").strip())
        except ValueError:
            conc = 0.0

        # 규제 DB 대조
        if inci_lower in restricted_dict:
            rule = restricted_dict[inci_lower]
            raw_status = str(rule.get("status", "")).upper()
            max_conc = rule.get("max_concentration")
            
            # 사유(conditions)와 규제 출처(regulation_source) 추출
            reason = rule.get("conditions") or "규제 세부 규정 확인 필요"
            source = rule.get("regulation_source") or ""

            # BANNED 또는 PROHIBITED인 경우 전면 배합 금지
            if raw_status in ["BANNED", "PROHIBITED"]:
                results.append({
                    "inci_name": inci_raw,
                    "concentration": conc,
                    "status": "배합 금지",
                    "is_violation": True,
                    "conditions": reason,
                    "source": source
                })
            # RESTRICTED(배합 한도)인 경우 농도 초과 검사
            elif raw_status == "RESTRICTED":
                if max_conc is not None and conc > float(max_conc):
                    results.append({
                        "inci_name": inci_raw,
                        "concentration": conc,
                        "status": "한도 초과",
                        "is_violation": True,
                        "conditions": f"[최대 한도 {max_conc}% 초과] {reason}",
                        "source": source
                    })
                else:
                    results.append({
                        "inci_name": inci_raw,
                        "concentration": conc,
                        "status": "배합 한도 이내",
                        "is_violation": False,
                        "conditions": f"[허용 한도 {max_conc}% 이하 준수] {reason}",
                        "source": source
                    })
            else:
                results.append({
                    "inci_name": inci_raw,
                    "concentration": conc,
                    "status": raw_status,
                    "is_violation": False,
                    "conditions": reason,
                    "source": source
                })
        else:
            # 안전한 미해당 성분
            results.append({
                "inci_name": inci_raw,
                "concentration": conc,
                "status": "미해당",
                "is_violation": False,
                "conditions": "규제 항목 미해당 (사용 가능)",
                "source": ""
            })

    return results