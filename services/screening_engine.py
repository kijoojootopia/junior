# 성분 판정 엔진
import os
import json
import pandas as pd

def load_json_db(file_path):
    """JSON 파일을 안전하게 로드하는 헬퍼 함수"""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def screen_ingredients(csv_file_path, target_region):
    """
    csv_file_path: 업로드된 CSV 파일 경로[cite: 1]
    target_region: 'us', 'eu', 'eac' 중 하나[cite: 1]
    """
    base_dir = os.path.join("data", target_region)
    prohibited_path = os.path.join(base_dir, "prohibited_ingredients.json")
    restricted_path = os.path.join(base_dir, "restricted_ingredients.json")
    
    # 1. 금지 및 규제 JSON DB 로드 및 딕셔너리 구축
    prohibited_db = load_json_db(prohibited_path)
    restricted_db = load_json_db(restricted_path)
    
    if not prohibited_db and not restricted_db:
        return {"error": "해당 국가의 규제 데이터가 없습니다."} #[cite: 1]

    # 빠른 검색을 위한 딕셔너리 인덱싱 (금지 목록 우선 적용)
    rules_dict = {}
    for item in restricted_db:
        if "inci_name" in item:
            rules_dict[item["inci_name"].lower().strip()] = item
            
    for item in prohibited_db:
        if "inci_name" in item:
            # 금지 성분이 우선 적용되도록 덮어씀
            rules_dict[item["inci_name"].lower().strip()] = item

    # 2. 업로드된 CSV 읽기
    df = pd.read_csv(csv_file_path) #[cite: 1]
    
    results = []
    for _, row in df.iterrows(): #[cite: 1]
        inci = str(row.get("inci_name", "")).lower().strip() #[cite: 1]
        conc = float(row.get("concentration", 0.0)) #[cite: 1]
        
        # 규제 DB 매칭
        if inci in rules_dict: #[cite: 1]
            rule = rules_dict[inci] #[cite: 1]
            status = rule.get("status") #[cite: 1]
            max_conc = rule.get("max_concentration") #[cite: 1]
            
            is_violation = False
            violation_reason = "통과"
            
            # --- 1차 판정: 금지 원료(PROHIBITED) 필터링 ---
            if status == "PROHIBITED": #[cite: 1]
                is_violation = True #[cite: 1]
                violation_reason = "배합 금지 성분 검출"
                
            # --- 2차 판정: 배합한도(max_concentration) 필터링 ---
            elif max_conc is not None:
                if conc > max_conc: #[cite: 1]
                    is_violation = True #[cite: 1]
                    violation_reason = f"배합한도 초과 (기준: {max_conc}%, 입력: {conc}%)"
                else:
                    violation_reason = f"배합한도 준수 (기준: {max_conc}%)"
            else:
                # status는 RESTRICTED이나 농도 기준이 아닌 조건부 허용 항목일 경우
                violation_reason = "조건부 허용 (용도 및 부위 제한 확인 필요)"

            results.append({
                "inci_name": row.get("inci_name"), #[cite: 1]
                "concentration": conc, #[cite: 1]
                "status": status, #[cite: 1]
                "is_violation": is_violation, #[cite: 1]
                "reason": violation_reason,
                "conditions": rule.get("conditions", ""), #[cite: 1]
                "source": rule.get("regulation_source", "") #[cite: 1]
            }) #[cite: 1]
        else:
            results.append({
                "inci_name": row.get("inci_name"), #[cite: 1]
                "concentration": conc, #[cite: 1]
                "status": "PASS", #[cite: 1]
                "is_violation": False, #[cite: 1]
                "reason": "규제 항목 미해당",
                "conditions": "규제 항목 미해당", #[cite: 1]
                "source": "-" #[cite: 1]
            }) #[cite: 1]
            
    return results #[cite: 1]