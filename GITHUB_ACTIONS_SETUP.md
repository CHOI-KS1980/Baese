# 🚀 GitHub Actions 완전 자동화 설정 가이드

## 📋 **설정 개요**

GitHub Actions를 사용하여 G라이더 미션 현황을 **24/7 완전 자동으로** 카카오톡 오픈채팅방에 전송하는 시스템입니다.

**✅ 장점:**
- 완전 무료 (월 2,000분 제공)
- 24/7 자동 실행
- 서버 관리 불필요
- 안정적인 클라우드 환경

**📅 자동 전송 시간:**
- **주요 시간**: 08:00, 12:00, 18:00, 22:00 (일 4회)
- **피크 시간**: 10:30, 14:30, 20:30 (일 3회)
- **총 7회/일** 자동 실행

---

## 🔧 **1단계: GitHub 저장소 생성**

### 1-1. 새 저장소 만들기
1. **브라우저에서 https://github.com/new 접속**
2. **저장소 설정:**
   - **Repository name**: `g-rider-automation`
   - **Description**: `G라이더 미션 현황 자동 전송 시스템`
   - **Visibility**: `Private` ✅ (보안상 추천)
   - **Add a README file**: ✅ 체크
3. **"Create repository" 클릭**

### 1-2. 로컬 코드 업로드
터미널에서 다음 명령어 실행:
```bash
cd /Users/choikwangsoon/Desktop/cursor
./upload_to_github.sh
```

---

## 🔐 **2단계: GitHub Secrets 설정 (중요!)**

### 2-1. Secrets 페이지 접속
1. **GitHub 저장소 → Settings 탭 클릭**
2. **왼쪽 메뉴에서 "Secrets and variables" → "Actions" 클릭**
3. **"New repository secret" 버튼 클릭**

### 2-2. 필수 Secrets 추가

다음 3개의 Secret을 **정확히** 추가해주세요:

#### **Secret 1: KAKAO_ACCESS_TOKEN**
- **Name**: `KAKAO_ACCESS_TOKEN`
- **Secret**: `a42a7d49082706c3e7241271f9fe3d00`

#### **Secret 2: KAKAO_OPENCHAT_ID**
- **Name**: `KAKAO_OPENCHAT_ID` 
- **Secret**: `gt26QiBg`

#### **Secret 3: WEBHOOK_URL**
- **Name**: `WEBHOOK_URL`
- **Secret**: `https://g-rider-webhook.onrender.com/send-kakao`

### 2-3. 선택적 Secrets (추가 기능용)

#### **Secret 4: FALLBACK_WEBHOOK_URL** (선택사항)
- **Name**: `FALLBACK_WEBHOOK_URL`
- **Secret**: `https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK` (Slack 알림용)

#### **Secret 5: WEATHER_API_KEY** (선택사항)
- **Name**: `WEATHER_API_KEY` 
- **Secret**: `your_openweather_api_key` (날씨 정보용)

---

## ⚡ **3단계: 자동화 활성화 및 테스트**

### 3-1. Actions 활성화 확인
1. **GitHub 저장소 → Actions 탭 클릭**
2. **"🚀 G라이더 미션 자동 전송" 워크플로우 확인**
3. **"Enable workflow" 버튼이 있다면 클릭**

### 3-2. 수동 테스트 실행
1. **Actions 탭 → "🚀 G라이더 미션 자동 전송" 클릭**
2. **"Run workflow" 버튼 클릭**
3. **"Use workflow from" → "main" 선택**
4. **"Run workflow" 확인 버튼 클릭**

### 3-3. 실행 결과 확인
1. **Actions 탭에서 실행 중인 워크플로우 클릭**
2. **"send-mission-update" Job 클릭**
3. **로그에서 다음 메시지 확인:**
   ```
   ✅ 웹훅 서버 응답 성공
   📝 생성된 메시지: 🚀 G라이더 미션 현황...
   📊 카카오톡 전송: success
   ```

---

## 📊 **4단계: 모니터링 및 관리**

### 4-1. 자동 실행 확인
- **Actions 탭에서 매일 7회 자동 실행되는지 확인**
- **"Schedule" 이벤트로 실행되는 로그 확인**

### 4-2. 실패 시 대응
- **Actions 탭에서 빨간색 X 표시가 있으면 클릭하여 오류 확인**
- **대부분 토큰 만료나 네트워크 문제**

### 4-3. 수동 실행
- **필요 시 "Run workflow" 버튼으로 즉시 실행 가능**
- **테스트, 긴급 전송 등에 활용**

---

## 🔧 **5단계: 고급 설정 (선택사항)**

### 5-1. 전송 시간 변경
`.github/workflows/auto-send-mission.yml` 파일의 cron 설정 수정:
```yaml
schedule:
  - cron: '0 23,3,9,13 * * *'  # 08:00, 12:00, 18:00, 22:00 KST
  - cron: '30 1,5,11 * * *'    # 10:30, 14:30, 20:30 KST
```

### 5-2. 알림 추가
Slack, Discord 등 추가 알림 채널 설정

### 5-3. 백업 시스템
웹훅 서버와 함께 이중 백업 시스템 구축

---

## 🚨 **문제 해결**

### 문제 1: Actions가 실행되지 않음
**해결책:**
- Settings → Actions → General → "Allow all actions" 선택
- 저장소가 Private인 경우 Actions 활성화 확인

### 문제 2: Secret 관련 오류
**해결책:**
- Secret 이름이 정확한지 확인 (대소문자 구분)
- Secret 값에 공백이나 특수문자가 들어가지 않았는지 확인

### 문제 3: 카카오톡 전송 실패
**해결책:**
- 액세스 토큰 유효성 확인
- 웹훅 서버 상태 확인 (`https://g-rider-webhook.onrender.com/`)

---

## 🎉 **완료! 이제 완전 자동화됩니다**

✅ **GitHub Actions가 24/7 자동으로 실행**  
✅ **하루 7회 정확한 시간에 메시지 전송**  
✅ **서버 관리나 컴퓨터 켜둘 필요 없음**  
✅ **완전 무료로 운영 가능**  

**🎯 결과:** Make.com 없이도 완전 자동화된 카카오톡 전송 시스템 완성! 🚀

---

## 📞 **지원 및 문의**

- **Actions 로그 확인**: GitHub → Actions 탭
- **웹훅 서버 상태**: https://g-rider-webhook.onrender.com/health
- **수동 테스트**: Actions → Run workflow 