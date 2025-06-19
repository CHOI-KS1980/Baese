# 🎯 Make.com으로 G라이더 미션 완전 자동화

## 📋 1단계: Make.com 계정 생성

1. https://make.com 접속
2. "Get started free" 클릭
3. 이메일 또는 구글 계정으로 가입
4. 이메일 인증 완료
5. 대시보드 접속

---

## 🔧 2단계: 새 시나리오 생성

1. 대시보드에서 "Create a new scenario" 클릭
2. 시나리오 이름: "G라이더 미션 자동 전송" 입력
3. "Blank scenario" 선택
4. 시각적 편집기 열림

---

## ⏰ 3단계: 스케줄 트리거 설정

1. 첫 번째 모듈에서 "Schedule" 검색 후 선택
2. "Every N hours" 선택
3. 설정:
   - Interval: 1
   - Unit: hour
   - Start time: 08:00
   - Timezone: Asia/Seoul
4. Advanced settings에서 특정 시간 설정:
   - 08:00, 12:00, 18:00, 22:00
   - 10:30, 14:30, 20:30

---

## 🌐 4단계: HTTP 요청 모듈 추가

1. "+" 버튼 클릭하여 새 모듈 추가
2. "HTTP" 검색 후 선택
3. "Make a request" 선택
4. 설정:
   - URL: `https://www.fanhowmission.ai.cloudbuild.app/rider/`
   - Method: GET
   - Headers: 
     - User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)

---

## 🔧 5단계: 데이터 파싱 모듈

1. "Tools" 모듈 추가
2. "Set variable" 선택
3. Variable name: `mission_data`
4. Variable value: HTML 파싱 함수 적용
5. JavaScript 함수로 데이터 추출

---

## 📤 6단계: 웹훅 전송 모듈

1. "HTTP" 모듈 추가 (전송용)
2. "Make a request" 선택
3. 설정:
   - URL: 웹훅 엔드포인트 URL
   - Method: POST
   - Headers: Content-Type: application/json
   - Body: JSON 형태로 메시지 데이터

---

## 🚀 7단계: 웹훅 서버 배포

### Render.com 배포 (추천):

1. https://render.com 가입
2. "New Web Service" 클릭
3. GitHub 저장소 연결
4. 설정:
   - Build Command: `pip install -r make_requirements.txt`
   - Start Command: `python make_webhook_server.py`
5. 환경변수 설정:
   - TELEGRAM_BOT_TOKEN (옵션)
   - DISCORD_WEBHOOK_URL (옵션)
6. 배포 완료 후 URL 확인

---

## ✅ 8단계: 테스트 및 활성화

1. Make.com에서 "Run once" 클릭
2. 각 모듈 실행 결과 확인
3. 오류 수정
4. "Scheduling" 토글을 ON으로 설정
5. 자동화 시작!

---

## 📊 모니터링

- **Make.com 대시보드**: 실행 로그 및 통계
- **웹훅 서버 로그**: 실시간 메시지 처리 현황
- **텔레그램/Discord**: 실제 전송 결과 확인

---

## 🔧 고급 설정

### 조건부 실행:
- Router 모듈로 분기 처리
- Filter로 조건 설정
- 시간대별 다른 메시지

### 오류 처리:
- Error handler 설정
- 재시도 로직
- 실패 시 알림

### 다중 플랫폼:
- 여러 웹훅 동시 전송
- 플랫폼별 메시지 포맷
- 우선순위 설정

---

## 💰 비용

- **Make.com**: 무료 (월 1,000 operations)
- **웹훅 서버**: 무료 (Render.com)
- **총 비용**: 완전 무료! 🎉

---

**🎉 축하합니다! 이제 Make.com으로 완전 자동화된 시스템이 구축되었습니다!**
