# 성분 판정 엔진
# services/screening_engine.py
import os
import json
import pandas as pd

def screen_ingredients(csv_file_path, target_region):
    """
    선택된 국가(target_region) 폴더 내의 규제 DB만 독립적으로 로드하여
    CSV의 INCI 명칭 및 상단 CAS 번호를 2중 교차 대조합니다.
    """
    # 1. 오직 선택된 국가의 폴더(data/{target_region})만 특정하여 접근
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    region_folder = os.path.join(base_dir, "data", target_region.lower())
    
    inci_dict = {}
    cas_dict = {}

    if os.path.exists(region_folder):
        for file_name in os.listdir(region_folder):
            if file_name.endswith(".json"):
                full_path = os.path.join(region_folder, file_name)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:
                            data_list = json.loads(content)
                            for item in data_list:
                                # 1) 순수 INCI명 등록 (소문자/공백제거 정규화)
                                raw_inci = item.get("inci_name")
                                if raw_inci:
                                    inci_key = str(raw_inci).strip().lower()
                                    inci_dict[inci_key] = item

                                # 2) JSON 상단의 cas_no 등록 (세미콜론 복수 번호 분리 대응)
                                raw_cas = item.get("cas_no")
                                if raw_cas:
                                    for c in str(raw_cas).split(";"):
                                        c_clean = c.strip()
                                        if c_clean and c_clean != "-":
                                            cas_dict[c_clean] = item
                except Exception as e:
                    print(f"[{target_region.upper()} JSON 로드 오류] {file_name}: {e}")

    # 2. 업로드된 CSV 파일 로드
    df = None
    for enc in ["utf-8-sig", "utf-8", "cp949"]:
        try:
            df = pd.read_csv(csv_file_path, encoding=enc)
            break
        except Exception:
            continue

    if df is None:
        return [{"inci_name": "CSV 읽기 실패", "concentration": 0, "status": "ERROR", "is_violation": True, "conditions": "인코딩 오류", "source": "-"}]

    df.columns = [str(c).strip().lower() for c in df.columns]

    results = []
    for _, row in df.iterrows():
        inci_raw = str(row.get("inci_name", "")).strip()
        cas_raw = str(row.get("cas_no", "")).strip()
        
        if not inci_raw or inci_raw.lower() == "nan":
            continue

        inci_clean = inci_raw.lower()
        
        # 농도 파싱
        try:
            conc = float(str(row.get("concentration", 0.0)).replace("%", "").strip())
        except ValueError:
            conc = 0.0

        # 해당 국가 DB 내에서 INCI -> CAS 순서로 대조
        rule = inci_dict.get(inci_clean)
        if not rule and cas_raw and cas_raw != "-" and cas_raw.lower() != "nan":
            rule = cas_dict.get(cas_raw)

        if rule:
            raw_status = str(rule.get("status", "")).strip().upper()
            max_conc = rule.get("max_concentration")
            
            # 사유(conditions_kr 우선) 및 출처
            reason = rule.get("conditions_kr") or rule.get("conditions") or "규제 세부 규정 확인 필요"
            source = rule.get("regulation_source") or ""

            # 배합 금지 상태
            if raw_status in ["PROHIBITED", "BANNED"]:
                results.append({
                    "inci_name": inci_raw,
                    "concentration": conc,
                    "status": "배합 금지",
                    "is_violation": True,
                    "conditions": reason,
                    "source": source
                })
            # 배합 한도 상태
            elif raw_status == "RESTRICTED":
                limit_val = None
                if max_conc is not None:
                    try:
                        limit_val = float(str(max_conc).replace("%", "").strip())
                    except ValueError:
                        limit_val = None

                if limit_val is not None and conc > limit_val:
                    results.append({
                        "inci_name": inci_raw,
                        "concentration": conc,
                        "status": "한도 초과",
                        "is_violation": True,
                        "conditions": f"[최대 허용 한도 {limit_val}% 초과] {reason}",
                        "source": source
                    })
                else:
                    results.append({
                        "inci_name": inci_raw,
                        "concentration": conc,
                        "status": "배합 한도 준수",
                        "is_violation": False,
                        "conditions": reason,
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
            # 해당 국가에서는 규제되지 않는 원료
            results.append({
                "inci_name": inci_raw,
                "concentration": conc,
                "status": "미해당",
                "is_violation": False,
                "conditions": "규제 항목 미해당 (사용 가능)",
                "source": ""
            })

    return results