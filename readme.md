#  K-뷰티 글로벌 규제 및 수출입 파이프라인 무역 대시보드

> 중소 화장품 브랜드사 1인 실무자(해외영업/RA)를 위한 국가별 규제 진단 및 수출입 행정 관리 대시보드입니다.

---

## 1. 프로젝트 개요
* **타깃 국가:** 미국(US - MoCRA/OTC), 유럽(EU - CosIng/CPNP), 유라시아(EAC - CU TR 009)
## 2. 주요 기능 및 작동 방식

사용자가 자사 브랜드 제품의 **전성분 표(CSV 파일)**를 업로드하고 타깃 국가(미국/유럽/러시아)를 선택하면, 3개 구역으로 구성된 맞춤형 진단 리포트를 제공합니다.

* **구역 1: 국가별 화장품 성분 규제 스크리닝**
  * 업로드된 성분명(INCI/CAS) 및 함량(%)을 타깃 국가 규제 DB와 자동 대조
  * 배합 금지, 배합 한도 초과, 카테고리별 예외 규정(미국 색소 승인 여부, OTC 해당 여부 등) 진단 및 위험 플래그 표시

* **구역 2: 국가별 최신 규제 변경 추적 피드**
  * 업로드한 제품 성분 및 품목과 연관된 최신 해외 규제 개정 공지 실시간 매칭
  * 규제 시행 유예 기간, 단계별 대응 가이드 피드 제공

* **구역 3: 맞춤형 수출 서류 파이프라인 (로드맵)**
  * [1단계: 성분 검토] ➔ [2단계: 서류 준비] ➔ [3단계: 인증/신고] ➔ [4단계: 현지 통관] 4단계 마일스톤 제시
  * 국가별·카테고리별 필수 구비 서류(MoCRA 리스팅, CPNP 보고서, EAC 인증서 등) 체크리스트 및 예상 소요 기간 출력

*(보조 기능: 관세청 품목별 수출 실적 및 한국수출입은행 환율 API를 통한 해당 권역 수출입 경기 동향 참고 지표 제공)*
* **기술 스택:** Python Flask, Jinja2, Chart.js, SQLite/JSON

---

## 3. 4인 팀 역할 분담

| 권역/도메인 | 담당자 | 주요 업무 및 산출물 |
| :--- | :--- | :--- |
| **미국 (US)** | [팀원 A] | MoCRA 4대 요건, FDA 착색제 DB, 선케어 OTC 분류 (`data/us/`) |
| **유럽 (EU)** | [팀원 B] | CosIng Annex II/III DB, CPNP 서류 절차 (`data/eu/`) |
| **유라시아 (EAC)** | [팀원 C] | CU TR 009 기술규정, EAC DoC/SGR 서류 절차 (`data/eac/`) |
| **공통 (Common)** | [팀원 D] | 관세청/환율 API 연동, Flask 라우팅 및 스크리닝 판정 엔진 |

---

## 4. 폴더 구조
```text
beauty-trade-dashboard/
├── README.md
├── app.py
├── data/
│   ├── us/
│   │   ├── restricted_ingredients.json
│   │   └── pipeline_checklist.json
│   ├── eu/
│   │   ├── restricted_ingredients.json
│   │   └── pipeline_checklist.json
│   └── eac/
│       ├── restricted_ingredients.json
│       └── pipeline_checklist.json
└── services/

각 권역 담당자는 `data/{region_code}/` 폴더에 아래 2개의 JSON 파일을 필수로 생성합니다.


# 📋 글로벌 뷰티 규제 데이터 구축 가이드라인

본 문서는 미국(US), 유럽(EU), 유라시아(EAC) 권역별 규제 데이터 수집 및 JSON 구조 표준화를 위한 대시보드입니다. 4명의 팀으로 협업을 진행합니다.

4명의 팀원은 본 규격에 맞추어 `data/{region}/` 하위 파일을 작성해야 합니다.

---

## 1. 권역별 담당자 및 주요 조사 대상

| 권역 코드 | 국가/지역 | 담당자 | 핵심 규제 및 데이터 타깃 |
| :--- | :--- | :--- | :--- |
| **`us`** | 미국 | [팀원 A] | MoCRA 시설/제품 등록, FDA 승인 착색제(Positive List), 선케어 OTC 분류 기준 |
| **`eu`** | 유럽연합 | [팀원 B] | CosIng Annex II(금지)/Annex III(한도), CPNP 등록 및 RP 지정 요건, 알레르기 유발 향료 |
| **`eac`** | 유라시아/러시아 | [팀원 C] | CU TR 009/2011 기술규정, EAC 적합성 선언(DoC) vs 국가등록(SGR) 구분 기준, 키릴 라벨링 |
| **`common`** | 공통/엔진 | [팀원 D] | 화장품 HS CODE 매핑, 한국수출입은행 환율 API, 통합 스크리닝 엔진 |

---

## 🎨 디자인 및 UI 컨셉 (요약)
* **벤치마킹:** 직관적인 의료 진단 차트 및 환자 바이탈 타임라인 UI
* **톤앤매너:** 신뢰감을 주는 깔끔한 대시보드 (파스텔톤 뱃지, 둥근 카드 레이아웃, 직관적인 상태 인디케이터)
* **프레임워크:** Flask Jinja2 + Chart.js (상세 UI 컴포넌트 규격은 추후 공유)

## ⚙️ 개발 환경 세팅 (Miniforge / Conda)

본 프로젝트는 팀원 간 패키지 버전 불일치를 방지하기 위해 **Miniforge (Conda)** 기반의 통일된 가상환경을 사용합니다.

* **가상환경 이름:** `junior`
* **파이썬 권장 버전:** `Python 3.10`

### 1 가상환경 생성 및 활성화
터미널(또는 Miniforge Prompt)에서 아래 명령어를 순서대로 실행합니다.

```bash
# 1. 가상환경 생성 (Python 3.10 권장)
conda create -n junior python=3.10 -y

# 2. 가상환경 활성화
conda activate junior
```

## 화장품 해외 진출 탭 — 파일 구조 준비

현재는 전용 파일만 준비한 상태이며 화면, API, 계산 및 추천 기능은 구현되지 않았습니다.
예정 기능은 유사도·수출적합도 KPI 카드, HS 코드별 국가별 수출액·성장률·관세 차트,
통관 로드맵, 현지 Distributor 추천 목록입니다.

- KPI 산출 방식: 미정. 비교 기준, 산식 및 가중치 확정 후 구현합니다.
- 데이터: `data/export/`의 JSON 파일은 모두 빈 객체(`{}`)입니다. 스키마와 데이터 기준은 미정이며 임의 수치, 업체, 규제 정보 또는 샘플 데이터는 포함하지 않았습니다.
- 연결 상태: 기존 `app.py` 및 화면 템플릿에는 아직 연결하지 않았습니다.

추가 파일 목록:

- `services/export_routes.py`: 화면 및 API 라우트 작성용
- `services/export_service.py`: 계산 및 추천 로직 작성용
- `templates/export_dashboard.html`: 전용 화면 작성용
- `static/css/export_dashboard.css`: 전용 스타일 작성용
- `static/js/export_dashboard.js`: 화면 동작 및 차트 작성용
- `data/export/hs_codes.json`: HS 코드 매핑 저장용
- `data/export/trade_stats.json`: 수출 통계 저장용
- `data/export/tariffs.json`: 관세 데이터 저장용
- `data/export/product_profiles.json`: 비교 제품 데이터 저장용
- `data/export/customs_roadmaps.json`: 통관 로드맵 저장용
- `data/export/distributors.json`: 유통사 데이터 저장용
