# 🌟 G라이더 실시간 대시보드 & 맞춤형 메시지 시스템

## 📋 개요

G라이더 차세대 자동화 시스템과 통합된 실시간 웹 대시보드입니다. 인터넷을 통해 언제 어디서나 G라이더 현황을 모니터링하고, 카카오톡 메시지 형식을 자유롭게 설정할 수 있습니다.

### 🎯 주요 기능

- **🌐 실시간 웹 대시보드**: 언제 어디서나 접근 가능한 온라인 모니터링
- **📊 인터랙티브 차트**: 시간대별 성과 추이, 미션 분포 등 시각화
- **📱 맞춤형 메시지**: 5가지 기본 템플릿 + 사용자 정의 JSON 형식
- **⚡ 실시간 업데이트**: 30초마다 자동 새로고침
- **📈 성과 분석**: AI 기반 트렌드 분석 및 예측
- **🎨 반응형 디자인**: PC, 태블릿, 모바일 모든 기기 지원

## 🚀 접속 방법

### 웹 대시보드 URL
```
https://[사용자명].github.io/[저장소명]/
```

예시: `https://choi-ks1980.github.io/Baese/`

## 📱 메시지 템플릿 설정 가이드

### 기본 제공 템플릿

#### 1. 🚀 표준 형식 (standard)
```
🚀 G라이더 현황 알림

📊 현재 점수: 785점
✅ 완료 미션: 23개
🏍️ 활성 라이더: 31명
💰 예상 수익: 94,200원

📅 2025-06-26 13:30:00
```

#### 2. 📈 상세 형식 (detailed)
```
📈 G라이더 상세 현황 리포트

🎯 성과 지표
━━━━━━━━━━━━━━━━━━━━━
📊 현재 점수: 785점 (+25)
✅ 완료 미션: 23개 (+3)
🏍️ 활성 라이더: 31명 (+2)
💰 예상 수익: 94,200원 (+3,000)

📈 시간대별 추이
━━━━━━━━━━━━━━━━━━━━━
🕒 피크시간 성과율: 92%
⏰ 평균 응답시간: 3.2분
🎯 목표 달성률: 78%

📅 2025-06-26 13:30:00 | 다음 업데이트: 14:00
```

#### 3. ⚡ 간단 형식 (simple)
```
G라이더

점수 785점 | 미션 23개 | 라이더 31명

2025-06-26 13:30:00
```

#### 4. 🌟 이모지 형식 (emoji_rich)
```
🌟 G라이더 실시간 현황 🌟

🎯 오늘의 성과
📊 점수: 785점 ⭐
✅ 미션: 23개 완료 🎉
🏍️ 라이더: 31명 활동중 🚀
💰 수익: 94,200원 예상 💎

📈 실시간 트렌드
📈 성과가 크게 상승했습니다! 🎉

⏰ 2025-06-26 13:30:00 | 💪 화이팅!
```

#### 5. 📋 비즈니스 형식 (business)
```
G라이더 운영 현황 보고

■ 당일 성과 요약
- 현재 점수: 785점
- 완료 미션: 23건
- 활성 라이더: 31명
- 예상 수익: 94,200원

■ 주요 지표
- 목표 달성률: 78%
- 평균 응답시간: 3.2분
- 시스템 상태: 정상 운영

보고일시: 2025-06-26 13:30:00
```

### 🛠️ 사용자 정의 템플릿

JSON 형식으로 완전히 맞춤형 메시지를 만들 수 있습니다:

```json
{
  "title": "🎯 내 스타일 G라이더",
  "content": "오늘 벌어들인 돈: {estimated_income:,}원 💰\n완성한 일: {completed_missions}개 ✨\n함께한 라이더: {active_riders}명 🤝\n\n현재 점수: {score}점 ({score_change:+d}) 📊",
  "footer": "⏰ {timestamp} | 다음엔 더 잘할게요! 💪"
}
```

#### 사용 가능한 변수들

| 변수명 | 설명 | 예시 |
|--------|------|------|
| `{score}` | 현재 점수 | 785 |
| `{completed_missions}` | 완료 미션 수 | 23 |
| `{active_riders}` | 활성 라이더 수 | 31 |
| `{estimated_income}` | 예상 수익 | 94200 |
| `{score_change}` | 점수 변화량 | +25 |
| `{mission_change}` | 미션 변화량 | +3 |
| `{riders_change}` | 라이더 변화량 | +2 |
| `{income_change}` | 수익 변화량 | +3000 |
| `{peak_performance}` | 피크시간 성과율 | 92.5 |
| `{avg_response_time}` | 평균 응답시간 | 3.2 |
| `{goal_achievement}` | 목표 달성률 | 78.5 |
| `{timestamp}` | 현재 시간 | 2025-06-26 13:30:00 |
| `{next_update}` | 다음 업데이트 시간 | 14:00 |
| `{trend_emoji}` | 트렌드 이모지 | 📈 |
| `{trend_description}` | 트렌드 설명 | 성과가 상승했습니다! |

## 🎛️ 대시보드 사용법

### 1. 실시간 통계 카드
- **현재 점수**: 실시간 G라이더 점수 및 변화량
- **완료 미션**: 오늘 완료한 미션 수
- **활성 라이더**: 현재 활동중인 라이더 수
- **예상 수익**: 점수 기반 예상 수익 (점수 × 120원)

### 2. 성과 차트
- **시간대별 추이**: 24시간 점수/미션 변화 그래프
- **미션 분포**: 완료/진행중/대기중 미션 비율

### 3. 활동 로그
- 최근 10개 활동 기록
- 실시간 시스템 상태 업데이트

### 4. 메시지 설정 패널
1. **설정 버튼** 클릭하여 패널 열기
2. **메시지 템플릿** 선택 (5가지 기본 + 사용자 정의)
3. **전송 조건** 설정:
   - 데이터 변경시: 점수/미션 변화가 있을 때 전송
   - 스케줄 전송: 정해진 시간에 정기 전송
   - 알림 상황시: 비정상 상황 감지시 전송
4. **사용자 정의 메시지** 작성 (JSON 형식)
5. **설정 저장** 버튼으로 적용

### 5. 메시지 미리보기
- 현재 설정으로 생성될 메시지를 실시간 미리보기
- 변수가 실제 데이터로 치환된 모습 확인 가능

## ⚙️ 설정 동기화

### 자동 동기화
- 웹 대시보드에서 설정한 메시지 형식이 GitHub Actions에 자동 반영
- 30분마다 실행되는 자동화 시스템이 새 설정 적용

### 수동 동기화
GitHub Actions에서 수동 실행:
1. Actions 탭 접속
2. "차세대 G라이더 자동화 시스템" 선택
3. "Run workflow" 클릭
4. 실행 모드 선택하여 즉시 적용

## 📊 모니터링 가이드

### 시스템 상태 확인
- **정상 운영**: 🟢 초록색 원 + "정상 운영"
- **연결 끊김**: 🔴 빨간색 원 + "연결 끊김"
- **오류 발생**: 🟡 노란색 원 + "오류 발생"

### 데이터 신선도
- **마지막 업데이트**: 헤더에 표시되는 최종 업데이트 시간
- **자동 새로고침**: 30초마다 자동으로 데이터 갱신
- **수동 새로고침**: 활동 로그의 새로고침 버튼 사용

### 성능 지표
- **목표 달성률**: 일일 목표 점수(1000점) 대비 현재 달성률
- **피크시간 성과율**: 최근 6시간 평균 성과 대비 목표 성과율
- **평균 응답시간**: 시스템 응답 속도 (낮을수록 좋음)

## 🔧 문제 해결

### 대시보드 접속 불가
1. GitHub Pages 활성화 확인:
   - 저장소 Settings → Pages
   - Source를 "GitHub Actions"로 설정
2. 배포 상태 확인:
   - Actions 탭에서 "대시보드 배포" 워크플로우 확인
3. URL 확인:
   - `https://[사용자명].github.io/[저장소명]/`

### 데이터가 업데이트되지 않음
1. GitHub Actions 실행 상태 확인
2. 시크릿 키 설정 확인:
   - `KAKAO_REST_API_KEY`
   - `KAKAO_REFRESH_TOKEN`
   - `KOREA_HOLIDAY_API_KEY`
3. 수동 실행으로 테스트

### 메시지 설정이 적용되지 않음
1. JSON 형식 유효성 확인 (사용자 정의 메시지)
2. 브라우저 캐시 새로고침 (Ctrl + F5)
3. 설정 저장 후 다음 스케줄까지 대기 (최대 30분)

### 차트가 표시되지 않음
1. JavaScript 활성화 확인
2. 브라우저 호환성 확인 (Chrome, Firefox, Safari, Edge 지원)
3. 네트워크 연결 상태 확인

## 🌟 고급 활용법

### 1. 알림 조건 커스터마이징
```json
{
  "title": "🚨 {score}점 돌파!",
  "content": "목표 점수를 달성했어요! 🎉\n\n현재 성과:\n📊 점수: {score}점\n✅ 미션: {completed_missions}개\n🏍️ 라이더: {active_riders}명\n\n다음 목표를 향해 달려봐요! 💪",
  "footer": "⏰ {timestamp} | 축하합니다! 🎊"
}
```

### 2. 시간대별 메시지 변경
점심시간용 메시지:
```json
{
  "title": "🍽️ 점심시간 G라이더 현황",
  "content": "점심 먹기 전 마지막 체크! 🥤\n\n오전 성과: {score}점 ({score_change:+d})\n완료한 일: {completed_missions}개\n\n맛있는 점심 드세요! 😋",
  "footer": "🕐 {timestamp} | 오후도 화이팅! 💪"
}
```

### 3. 성과 기반 동적 메시지
```json
{
  "title": "{trend_emoji} G라이더 현황",
  "content": "📊 점수: {score}점\n✅ 미션: {completed_missions}개\n\n{trend_description}\n\n목표 달성률: {goal_achievement}%",
  "footer": "⏰ {timestamp}"
}
```

## 📈 성능 최적화

### 브라우저 성능
- 최신 브라우저 사용 권장
- 하드웨어 가속 활성화
- 캐시 주기적 정리

### 네트워크 최적화
- CDN을 통한 리소스 로딩
- 압축된 데이터 전송
- 효율적인 캐싱 전략

### 데이터 최적화
- 중복 요청 방지
- 배치 업데이트
- 델타 데이터 전송

## 🔐 보안 고려사항

### 데이터 보호
- GitHub Secrets를 통한 민감 정보 보호
- HTTPS 강제 사용
- 클라이언트 사이드 데이터 검증

### 접근 제어
- GitHub Pages 공개 저장소 특성상 누구나 접근 가능
- 민감한 정보는 대시보드에 노출하지 않음
- 실제 API 키는 서버 사이드에서만 사용

## 📞 지원 및 문의

### GitHub Issues
- 버그 리포트: [GitHub Issues](https://github.com/CHOI-KS1980/Baese/issues)
- 기능 요청: Feature Request 라벨 사용
- 질문: Question 라벨 사용

### 문서 업데이트
- 이 문서는 시스템 업데이트와 함께 지속적으로 개선됩니다
- 최신 정보는 GitHub 저장소에서 확인하세요

---

## 🎉 완성된 시스템 요약

### ✅ 구현 완료 기능
- [x] 실시간 웹 대시보드
- [x] 5가지 기본 메시지 템플릿
- [x] 사용자 정의 JSON 메시지
- [x] 인터랙티브 차트 및 시각화
- [x] 자동 데이터 동기화
- [x] 반응형 모바일 지원
- [x] AI 기반 트렌드 분석
- [x] GitHub Pages 자동 배포
- [x] 실시간 성능 모니터링

### 🌟 특별 기능
- **차세대 통합**: 기존 모든 고도화 기능과 완벽 통합
- **무중단 서비스**: GitHub Pages를 통한 24/7 접근
- **맞춤형 경험**: 개인 취향에 맞는 메시지 스타일
- **실시간 분석**: AI 기반 성과 예측 및 이상 감지
- **완전 자동화**: 설정 한 번으로 모든 것이 자동 운영

---

**🌟 G라이더 차세대 자동화 시스템과 함께 더 스마트한 배달을 경험하세요!** 