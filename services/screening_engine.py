# 성분 판정 엔진
import os
import json
import pandas as pd

def screen_ingredients(csv_file_path, target_region):
    """
    지정된 권역(data/{target_region}/) 폴더 안의 모든 규제 JSON 파일
    (배합 금지 + 배합 한도)을 누락 없이 모두 합쳐서 대조 진단합니다.
    """
    # 1. 대상 권역 폴더 경로 설정 (절대 경로 보정)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    region_folder = os.path.join(base_dir, "data", target_region.lower())
    
    restricted_dict = {}

    # 폴더 내의 모든 .json 파일을 하나도 빠짐없이 읽어들임 (break 제거)
    if os.path.exists(region_folder):
        for file_name in os.listdir(region_folder):
            if file_name.endswith(".json"):
                full_json_path = os.path.join(region_folder, file_name)
                try:
                    with open(full_json_path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:
                            data_list = json.loads(content)
                            for item in data_list:
                                raw_name = item.get("inci_name", "")
                                if raw_name:
                                    # 공백 제거 및 소문자로 통일하여 키 등록
                                    clean_key = str(raw_name).strip().lower()
                                    restricted_dict[clean_key] = item
                except Exception as e:
                    print(f"[JSON 읽기 오류] {file_name}: {e}")

    # 2. 업로드된 CSV 파일 읽기
    df = None
    for enc in ["utf-8-sig", "utf-8", "cp949"]:
        try:
            df = pd.read_csv(csv_file_path, encoding=enc)
            break
        except Exception:
            continue

    if df is None:
        return [{
            "inci_name": "CSV 읽기 실패",
            "concentration": 0,
            "status": "ERROR",
            "is_violation": True,
            "conditions": "CSV 인코딩을 확인해주세요.",
            "source": "-"
        }]

    # 컬럼 헤더 소문자화
    df.columns = [str(c).strip().lower() for c in df.columns]

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
            raw_status = str(rule.get("status", "")).strip().upper()
            max_conc = rule.get("max_concentration")
            
            reason = rule.get("conditions") or "규제 세부 규정 확인 필요"
            source = rule.get("regulation_source") or ""

            # PROHIBITED 또는 BANNED: 배합 전면 금지
            if raw_status in ["PROHIBITED", "BANNED"]:
                results.append({
                    "inci_name": inci_raw,
                    "concentration": conc,
                    "status": "배합 금지",
                    "is_violation": True,
                    "conditions": reason,
                    "source": source
                })
            # RESTRICTED: 배합 한도 초과 여부 확인
            elif raw_status == "RESTRICTED":
                # max_conc가 문자열이거나 복잡한 경우 float 파싱 예외 처리
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
            # 규제 대상이 아닌 안전 원료
            results.append({
                "inci_name": inci_raw,
                "concentration": conc,
                "status": "미해당",
                "is_violation": False,
                "conditions": "규제 항목 미해당 (사용 가능)",
                "source": ""
            })

    return results