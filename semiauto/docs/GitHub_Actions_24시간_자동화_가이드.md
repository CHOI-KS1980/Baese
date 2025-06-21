# 🤖 GitHub Actions 24시간 자동화 설정 가이드

## 📋 개요
GitHub Actions를 이용해 컴퓨터를 켜두지 않아도 24시간 자동으로 심플 배민 플러스 리포트를 전송하는 방법입니다.

## 🎯 자동화 스케줄
- **운영 시간**: 매일 10:00 ~ 23:50
- **전송 간격**: 10분마다 (하루 약 84회)
- **특별 알림**: 
  - 10:00 시작 알림
  - 00:00 종료 알림

## 🔧 설정 단계

### 1. GitHub Repository 생성
1. GitHub에 로그인
2. 새 Repository 생성 (Public 또는 Private 가능)
3. 로컬 코드를 GitHub에 업로드

### 2. GitHub Secrets 설정
Repository → Settings → Secrets and variables → Actions에서 다음 Secrets를 추가:

#### 필수 Secrets:
- `KAKAO_REST_API_KEY`: 카카오 REST API 키
- `KAKAO_REFRESH_TOKEN`: 카카오 Refresh Token
- `GRIDER_ID`: G라이더 로그인 ID
- `GRIDER_PASSWORD`: G라이더 로그인 비밀번호

### 3. Secrets 값 확인 방법

#### 카카오 정보 확인:
```bash
# 현재 설정된 토큰 확인
cd semiauto
cat config.txt
```

#### G라이더 정보:
- G라이더 웹사이트 로그인에 사용하는 ID/비밀번호

### 4. 워크플로우 파일 확인
`.github/workflows/semiauto-grider-24h.yml` 파일이 생성되어 있는지 확인

### 5. 자동화 활성화
1. GitHub Repository → Actions 탭
2. "심플 배민 플러스 24시간 자동화" 워크플로우 확인
3. "Enable workflow" 클릭 (비활성화 상태인 경우)

## 🧪 테스트 실행

### 수동 테스트:
1. Actions 탭 → "심플 배민 플러스 24시간 자동화"
2. "Run workflow" 버튼 클릭
3. 실행 결과 확인

### 로그 확인:
- Actions 탭에서 실행 기록 확인
- 실패 시 에러 로그 다운로드 가능

## 📊 모니터링

### 실행 현황 확인:
- GitHub Actions 탭에서 실행 기록 확인
- 성공/실패 여부 모니터링

### 카카오톡 메시지:
- "나에게 보내기"로 리포트 수신
- 클립보드에 자동 복사 (로컬 실행시에만)

## ⚠️ 주의사항

### GitHub Actions 제한:
- **Public Repository**: 무제한 사용
- **Private Repository**: 월 2,000분 제한 (초과시 과금)

### 예상 사용량:
- 1회 실행: 약 2-3분
- 하루 84회: 약 168-252분
- **월 사용량**: 약 5,000-7,500분

### 권장사항:
1. **Public Repository 사용** (무제한)
2. 민감한 정보는 Secrets로 관리
3. 정기적인 실행 로그 확인

## 🔄 업데이트 방법

### 코드 수정시:
1. 로컬에서 코드 수정
2. Git commit & push
3. 자동으로 새 코드 적용

### 설정 변경시:
1. GitHub Secrets 업데이트
2. 워크플로우 파일 수정 (필요시)

## 🛠️ 문제 해결

### 실행 실패시:
1. Actions 탭에서 에러 로그 확인
2. Secrets 설정 재확인
3. 토큰 만료 여부 확인

### 메시지 미수신시:
1. 카카오 토큰 상태 확인
2. G라이더 로그인 정보 확인
3. 네트워크 연결 상태 확인

## 📞 지원

문제 발생시:
1. GitHub Issues에 문의
2. 로그 파일 첨부
3. 실행 환경 정보 제공

---

🎉 **설정 완료 후 24시간 자동 모니터링이 시작됩니다!** 