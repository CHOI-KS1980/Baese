# G-Rider 웹사이트 CSS 선택자 및 데이터 위치 참조 가이드

이 문서는 G-Rider 데이터 스크래핑에 사용되는 주요 URL, CSS 선택자 및 데이터 계산 로직을 정리한 것입니다.
웹사이트 구조가 변경될 경우 이 파일을 업데이트하여 스크립트의 유지보수성을 높입니다.

---

## 1. 공통 정보

- **베이스 URL**: `https://jangboo.grider.ai`
- **로그인 URL**: `https://jangboo.grider.ai/login`

---

## 2. 일간 데이터 (Daily Data)

- **페이지 URL**: `https://jangboo.grider.ai/dashboard` (로그인 후 이동되는 기본 페이지)
- **설명**: 매일의 라이더별 실적 데이터를 수집합니다.
- **관련 함수**: `_parse_daily_rider_data`

### 데이터 구조:

- **라이더 목록 컨테이너**: `div.rider_list`
- **개별 라이더 행**: `.rider_item`

#### 개별 라이더 데이터 선택자:
- **이름**: `.rider_name`
- **아이디**: `.user_id`
- **운행 상태**: `.working_status .rider_info_text`
- **완료 건수**: `.complete_count`
- **거절 건수**: `.reject_count`
- **배차 취소 건수**: `.accept_cancel_count`
- **배달 취소 건수**: `.accept_cancel_rider_fault_count`

---

## 3. 주간 데이터 및 일일 미션 (Weekly & Mission Data)

- **페이지 URL**: `https://jangboo.grider.ai/orders/sla/list`
- **설명**: 주간 예상 점수 및 실적, 일별 미션 달성 현황을 수집합니다.

### 3.1. 주간 미션 예상 점수 (Weekly Score Summary)
- **관련 함수**: `_parse_weekly_data`

#### 데이터 소스 1: 요약 카드 (`div.summary_area`)
- **예상 총 점수**: `span.summary_score_text[data-text='total']`
- **물량 점수**: `span.summary_score_text[data-text='quantity']`
- **수락률 점수**: `span.summary_score_text[data-text='acceptance']`

#### 데이터 소스 2: 주간 라이더 목록 (`div.rider_list`)
- **설명**: 이 목록의 데이터를 합산하여 '총 완료', '총 거절', '수락률'을 **재계산**합니다.
- **계산 로직**:
    1.  목록에서 각 라이더(`.rider_item`)의 실적(완료, 거절, 배차취소, 배달취소)을 가져옵니다.
    2.  모든 실적이 0인 라이더는 계산에서 제외합니다.
    3.  `총 완료` = 필터링된 라이더들의 `완료` 건수 합계
    4.  `총 거절` = 필터링된 라이더들의 (`거절` + `배차취소` + `배달취소`) 건수 합계
    5.  `수락률` = `총 완료` / (`총 완료` + `총 거절`) * 100

### 3.2. 일일 미션 데이터 (Daily Mission Table)
- **관련 함수**: `_parse_mission_data`

- **테이블 선택자**: `table.sla_table`
- **설명**: '물량 점수관리' 테이블에서 오늘 날짜에 해당하는 행의 데이터를 가져옵니다.
- **탐색 로직**:
    1. `tbody` 안의 모든 `tr`을 순회합니다.
    2. 각 `tr`의 두 번째 `td`에 오늘 날짜(예: `2025-06-28`)가 포함되어 있는지 확인하여 대상 행을 찾습니다.
- **데이터 추출**:
    - `날짜`: 두 번째 `td`
    - `일별 물량 점수`: 세 번째 `td`
    - `아침점심피크`: 네 번째 `td` (내부의 `숫자/숫자` 형식 텍스트만 추출)
    - `오후논피크`: 다섯 번째 `td` (내부의 `숫자/숫자` 형식 텍스트만 추출)
    - `저녁피크`: 여섯 번째 `td` (내부의 `숫자/숫자` 형식 텍스트만 추출)
    - `심야논피크`: 일곱 번째 `td` (내부의 `숫자/숫자` 형식 텍스트만 추출) 