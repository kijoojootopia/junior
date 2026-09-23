# 성분 판정 엔진
import os
import json
import pandas as pd

def screen_ingredients(csv_file_path, target_region):
    """
    csv_file_path: 업로드된 CSV 파일 경로
    target_region: 'us', 'eu', 'eac' 중 하나
    """
    # 1. 대상 국가의 규제 JSON 로드
    json_path = os.path.join("data", target_region, "restricted_ingredients.json")
    if not os.path.exists(json_path):
        return {"error": "해당 국가의 규제 데이터가 없습니다."}
        
    with open(json_path, "r", encoding="utf-8") as f:
        restricted_db = json.load(f)
        
    # 빠른 검색을 위해 INCI 명칭과 CAS 번호 기준 인덱싱
    restricted_dict = {item["inci_name"].lower().strip(): item for item in restricted_db if "inci_name" in item}

    # 2. 업로드된 CSV 읽기
    df = pd.read_csv(csv_file_path)
    
    results = []
    for _, row in df.iterrows():
        inci = str(row.get("inci_name", "")).lower().strip()
        conc = float(row.get("concentration", 0.0))
        
        # 규제 DB 대조
        if inci in restricted_dict:
            rule = restricted_dict[inci]
            status = rule.get("status")
            max_conc = rule.get("max_concentration")
            
            # 한도 초과 여부 확인
            is_violation = False
            if status == "PROHIBITED":
                is_violation = True
            elif max_conc is not None and conc > max_conc:
                is_violation = True
                
            results.append({
                "inci_name": row.get("inci_name"),
                "concentration": conc,
                "status": status,
                "is_violation": is_violation,
                "conditions": rule.get("conditions", ""),
                "source": rule.get("regulation_source", "")
            })
        else:
            results.append({
                "inci_name": row.get("inci_name"),
                "concentration": conc,
                "status": "PASS",
                "is_violation": False,
                "conditions": "규제 항목 미해당",
                "source": "-"
            })
            
    return results