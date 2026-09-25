#  K-뷰티 글로벌 규제 및 수출입 파이프라인 무역 대시보드

> 중소 화장품 브랜드사 1인 실무자(해외영업/RA)를 위한 국가별 규제 진단 및 수출입 행정 관리 대시보드입니다.

---

## 1. 프로젝트 개요
* **화면에서 선택 가능한 국가·권역:** 미국(US), 유럽(EU), 유라시아(EAC/EAEU), UAE. 일본 연결은 보류 중입니다. UAE 성분 데이터·판정 로직의 검토는 별도 팀원 담당입니다.
## 2. 주요 기능 및 작동 방식

- 첫 접속(`/`)은 수출 권역 지도(`/export`)로 이동합니다.
- 지도의 ‘대시보드’ 링크를 누르면 진단 화면(`/dashboard`)으로 이동합니다. 진단 화면의 지도 링크로 돌아올 수 있습니다.
- 첫 화면 연결은 기존 `app.py`에서 변경했으며, 새 파일은 추가하지 않았습니다.

사용자가 자사 브랜드 제품의 **전성분 표(CSV 파일)**를 업로드하고 타깃 국가(미국/유럽/러시아)를 선택하면, 3개 구역으로 구성된 맞춤형 진단 리포트를 제공합니다.

* **구역 1: 국가별 화장품 성분 규제 스크리닝**
  * 업로드된 성분명(INCI/CAS) 및 함량(%)을 타깃 국가 규제 DB와 자동 대조
  * 배합 금지, 배합 한도 초과, 카테고리별 예외 규정(미국 색소 승인 여부, OTC 해당 여부 등) 진단 및 위험 플래그 표시

* **구역 2: 국가별 최신 규제 변경 추적 피드**
  * 업로드한 제품 성분 및 품목과 연관된 최신 해외 규제 개정 공지 실시간 매칭
  * 규제 시행 유예 기간, 단계별 대응 가이드 피드 제공

* **구역 3: 맞춤형 수출 서류 파이프라인 (로드맵)**
  * 타깃 권역을 선택하면 해당 국가 JSON의 단계와 준비 서류를 가로 타임라인 카드로 표시합니다. CSV 업로드 없이도 볼 수 있습니다.
  * 미국은 일반 화장품/OTC를 직접 선택하며, 유럽·EAEU에서는 제품 유형 선택칸을 숨깁니다.
  * 각 카드에 단계명, 준비 서류, 예상 기간, 필수 여부, 안내 링크를 표시합니다. 단계 수는 JSON 항목 수를 따릅니다.

*(보조 기능: 관세청 품목별 수출 실적 및 ExchangeRate-API를 통한 해당 권역 수출입 경기 동향 참고 지표 제공)*
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
```

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
| **`common`** | 공통/엔진 | [팀원 D] | 화장품 HS CODE 매핑, ExchangeRate-API, 통합 스크리닝 엔진 |

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

## 구역 3: 현재 구현과 관리 위치

진단 화면(`/dashboard`)에서 처음에는 미국·일반 화장품 안내를 표시합니다. 상단의 수출 타깃 권역이나 미국 제품 유형을 바꾸면 해당 안내로 즉시 전환됩니다. 서버가 페이지를 열 때 국가별 자료를 읽어 전달하므로, JSON을 수정한 뒤에는 페이지를 새로고침해야 합니다.

| 데이터 파일 | 현재 구성 |
| :--- | :--- |
| `data/us/pipeline_checklist.json` | `GENERAL`(일반 화장품) 4개, `OTC` 4개 목록을 담은 객체 |
| `data/eu/pipeline_checklist.json` | 6개 항목의 목록 |
| `data/eac/pipeline_checklist.json` | 7개 항목의 목록 |
| `data/uae/pipeline_checklist.json` | 5개 항목의 목록 |

- 표시 기준: `stage_step` 순서로 정렬하고 `task_name`, `required_doc`, `estimated_days`, `is_mandatory`, `guide_url`을 사용합니다.
- 예상 기간: 저장된 일수를 그대로 표시합니다. `null` 또는 누락은 `미정`, 숫자 `0`은 `0일`로 표시합니다. 전체 기간 합산이나 별도 KPI 계산은 하지 않습니다.
- 자료가 없으면 빈 상태 안내를 표시합니다. 파일을 읽지 못하거나 JSON 형식이 잘못되면 서버에 오류를 기록하고 해당 국가의 목록을 비웁니다.
- 미국 제품 유형은 사용자가 선택합니다. 성분 검사 결과에 따른 OTC 자동 분류, 서류 완료 체크·저장, 진행률 계산은 아직 연결하지 않았습니다.
- 이 기능은 저장된 안내를 보여줍니다. 원문 규제의 최신성·적용 조건을 자동 검증하는 기능은 포함하지 않습니다.

구현은 아래 기존 파일에 통합했습니다. 별도 파이프라인 HTML·CSS 파일은 병합 후 삭제했으며, 파이프라인 전용 서비스 파일은 생성하지 않았습니다.

| 파일 | 역할 |
| :--- | :--- |
| `app.py` | 국가별 JSON 읽기, 미국 분류와 유럽·EAEU·UAE 목록의 형식 통일, 템플릿에 데이터 전달 |
| `templates/index.html` | 구역 3 카드와 국가·유형별 표시 영역, 미국 제품 유형 선택칸 |
| `static/css/style.css` | 단계 연결선, 둥근 카드, 가로 스크롤 디자인 |
| `static/js/main.js` | 국가·제품 유형 변경 시 표시 영역과 제목 전환 |

## 환율 표시

- `services/exchange_api.py`에서 ExchangeRate-API의 Standard endpoint(`/v6/{API_KEY}/latest/USD`)를 한 번 호출하고, `templates/index.html`에서 1 USD/EUR/RUB/AED당 원화 금액을 표시합니다.
- 프로젝트 `.env`에 `EXCHANGERATE_API_KEY`를 설정해야 합니다. 이전 `EXCHANGE_API_KEY`는 사용하지 않습니다. 키를 변경하면 Flask 서버를 재시작하세요. 인증키는 저장소에 올리지 않습니다.
- 환산식: `conversion_rates.KRW / conversion_rates[통화]`. 동일 응답의 USD 기준 환율로 계산하고 화면에서 소수 둘째 자리까지 표시합니다. 은행의 실제 환전·송금 적용 환율과는 다를 수 있습니다.
- 화면의 `기준일시: YYYY/MM/DD HH:MM KST`는 제공기관의 `time_last_update_unix`를 한국 시간으로 변환한 값입니다. 조회한 현재 시각을 기준일로 대신 표시하지 않습니다.
- 응답의 `time_next_update_unix`까지 서버 메모리에 저장하고, 그 이후 첫 페이지 요청에서 새 자료를 조회합니다. 다음 갱신 시각이 없거나 이미 지났으면 5분간 저장합니다. 열어둔 화면이 자동으로 바뀌는 기능은 없으며 새로고침해야 반영됩니다.
- 제공기관 갱신 주기는 Free 24시간, Pro 60분, Business/Volume 5분입니다. 초 단위 실시간 시세가 아닙니다. [공식 갱신 주기 안내](https://www.exchangerate-api.com/product/our-exchange-rate-data)
- 응답에 없는 통화는 `제공 자료 없음`으로 표시합니다. 인증키 누락·통신 오류·자료 오류로 전체 조회가 실패하면 기준일시는 `확인 불가`, 환율은 `조회 불가`이며 원인 안내를 함께 표시합니다. 잘못된 키, 미인증 계정, 요청 한도 초과도 구분합니다.
- 임의 환율이나 이전 제공기관의 고정 기본값은 사용하지 않습니다. [응답 형식·오류 코드](https://www.exchangerate-api.com/docs/standard-requests)

## 화장품 해외 진출 지도

`/export`에서 미국(`US`), 유럽(`EU`), 유라시아(`EAC`), UAE(`AE`)를 볼 수 있습니다. 지구본 아이콘을 누르면 해당 권역이 선택된 진단 화면(`/dashboard?region=...`)으로 이동합니다. 지도 핀은 권역의 대표 위치이며, 진단 화면·데이터 폴더의 UAE 코드는 `uae`입니다.
화면은 왼쪽의 한국 전체 수출 통계와 오른쪽 지구본으로 구성됩니다. 현재 통계 원자료가 없어 수출액·성장률·기준연도는 모두 `자료 준비 중`으로 표시합니다. 한국 전체 통계는 권역별 수치가 아닙니다.
`GET /api/export/trade?country=US`는 국가별 연도별 수출액과 전년 대비 성장률을 반환합니다.
지도에 표시할 통계는 **한국 화장품의 전 세계 수출 합계**로 고정하기로 했으나, 실제 자료 조회·집계 코드 전환은 아직 보류 중입니다. 지도 화면은 위 국가별 API를 호출하지 않습니다. 현재 API는 국가 코드를 필터링하며 EU/EAC 회원국 합계를 계산하지 않습니다. 이전 국가 코드(DE/FR/RU/KZ) 허용도 이 전환 때 정리할 예정입니다.
HS 코드 필터는 `hs_code` 쿼리 매개변수로 전달할 수 있습니다. 화면의 HS 코드 선택 UI는 매핑 데이터가 준비된 후 추가합니다.
`/export` 안의 통관 로드맵과 Distributor 추천 화면은 아직 구현되지 않았습니다. 진단 화면(`/dashboard`)의 구역 3 서류 안내와는 별도 기능입니다.

- 성장률 산식: `(최신 연도 수출액 / 바로 전 연도 수출액 - 1) × 100`. 전년도 자료가 없거나 0이면 `null`(화면에는 산정 불가)입니다.
- 수출액은 같은 국가·연도의 품목별 금액을 합산합니다. 원자료는 `data/export/trade_stats.json`의 `records` 배열에 `country`(국가 코드), `hs_code`, `year`(정수), `export_usd`(USD 금액) 필드로 저장하도록 설계했습니다. 동일 국가·연도·HS 코드의 중복 기록은 넣지 않아야 합니다.
- 현재 수출 통계 파일은 빈 객체(`{}`)이며 실제 수출액, 성장률 또는 샘플 수치를 넣지 않았습니다. 수출적합도 KPI의 산식 및 가중치도 미정입니다.
- 세계 지도 원본은 Wikimedia Commons의 [CC0 세계 지도](https://commons.wikimedia.org/wiki/File:BlankMap-World-Equirectangular.svg)입니다. 이 SVG를 밝은 육지·바다 색으로 바꿔 `static/img/globe-surface.png`로 저장했습니다.
- `/export`의 지구본은 Globe.GL을 CDN에서 불러와 위 PNG를 표면에 입힙니다. 권역 위치는 초록 아이콘 안의 `US`·`EU`·`EAEU`·`UAE` 약자와 보라색 고리로 구분하며, 아이콘을 누르면 해당 권역의 진단 화면으로 이동합니다. 유라시아의 내부 코드는 `EAC`지만 화면에는 권역명인 `EAEU`를 표시합니다. 지구본은 지형 높이 데이터를 사용하지 않으며, CDN이나 WebGL을 사용할 수 없으면 평면 지도 이미지와 그 아래 권역 링크를 보여줍니다.

추가 파일 목록:

- `services/export_routes.py`: 지도 화면 및 수출 통계 API
- `services/export_service.py`: 수출 통계 집계 및 성장률 계산
- `templates/export_dashboard.html`: 한국 전체 통계 카드·지구본·대체 권역 링크 화면
- `static/css/export_dashboard.css`: 2열 배치와 지구본·카드 스타일
- `static/js/export_dashboard.js`: 지구본 아이콘 링크
- `static/img/world.svg`: 세계 지도 배경
- `static/img/globe-surface.png`: 지구본의 밝은 표면 이미지
- `data/export/hs_codes.json`: HS 코드 매핑 저장용
- `data/export/trade_stats.json`: 수출 통계 저장용
- `data/export/tariffs.json`: 관세 데이터 저장용
- `data/export/customs_roadmaps.json`: 통관 로드맵 저장용
- `data/export/distributors.json`: 유통사 데이터 저장용
