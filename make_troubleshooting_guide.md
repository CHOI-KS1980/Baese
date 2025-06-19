# 🚨 Make.com 문제해결 완전 가이드

## 🎯 빠른 문제 진단

### ⚡ **긴급 체크리스트 (30초 점검)**
```
✅ 인터넷 연결 확인
✅ Make.com 로그인 상태 확인
✅ 시나리오 저장 상태 확인
✅ Scheduling 토글 상태 (파란색인지)
✅ 웹훅 서버 작동 상태 확인
```

---

## 🔧 1단계 문제: 계정 및 로그인

### ❌ **1-1. 가입이 안 됨**

**🔍 증상:**
- "Email already exists" 오류
- 인증 이메일이 안 옴
- 비밀번호가 약하다는 메시지

**✅ 해결 방법:**

1. **이메일 중복 오류**
   ```
   💡 해결: 다른 이메일 주소 사용
   💡 또는: "Sign in" 버튼으로 기존 계정 로그인
   ```

2. **인증 메일 안 옴**
   ```
   📧 스팸 폴더 확인
   📧 프로모션 탭 확인 (Gmail)
   📧 5분 후 "Resend email" 클릭
   ```

3. **비밀번호 조건 미달**
   ```
   🔒 최소 8자 이상
   🔒 대문자 1개 이상
   🔒 소문자 1개 이상
   🔒 숫자 1개 이상
   ✅ 예시: MakeBot123!
   ```

### ❌ **1-2. 로그인이 안 됨**

**🔍 증상:**
- "Invalid credentials" 오류
- 2FA 문제
- 계정이 잠김

**✅ 해결 방법:**

1. **비밀번호 재설정**
   ```
   🔗 "Forgot password?" 클릭
   📧 이메일로 재설정 링크 받기
   🔒 새 비밀번호 설정
   ```

2. **2FA 문제**
   ```
   📱 인증 앱 시간 동기화 확인
   📱 백업 코드 사용
   💬 고객지원에 연락
   ```

---

## 🚀 2단계 문제: 시나리오 생성

### ❌ **2-1. 시나리오가 안 만들어짐**

**🔍 증상:**
- "Create" 버튼이 비활성화
- 오류 메시지 없이 진행 안 됨
- 페이지가 멈춤

**✅ 해결 방법:**

1. **브라우저 문제**
   ```
   🔄 페이지 새로고침 (F5)
   🧹 브라우저 캐시 삭제
   🌐 Chrome/Firefox 사용 권장
   🚫 IE/Safari 사용 지양
   ```

2. **네트워크 문제**
   ```
   📶 인터넷 연결 확인
   🔒 회사 방화벽 확인
   📱 모바일 핫스팟으로 테스트
   ```

3. **계정 권한 문제**
   ```
   💰 무료 계정 한도 확인
   📊 기존 시나리오 개수 확인 (무료: 2개)
   🗑️ 불필요한 시나리오 삭제
   ```

---

## ⏰ 3단계 문제: Schedule 모듈

### ❌ **3-1. 시간대 설정 오류**

**🔍 증상:**
- 시간이 다르게 실행됨
- 한국 시간이 아님
- "Invalid timezone" 오류

**✅ 해결 방법:**

1. **시간대 재설정**
   ```
   🌍 Time zone 필드 클릭
   🔍 "Seoul" 검색
   ✅ "Asia/Seoul" 선택
   💾 저장 후 확인
   ```

2. **시간 형식 확인**
   ```
   ⏰ 24시간 형식 사용: 18:00 (O), 6:00 PM (X)
   ⏰ 0시는 00:00으로 입력
   ⏰ 분은 반드시 2자리: 08:05 (O), 8:5 (X)
   ```

### ❌ **3-2. 실행 시간 추가 안 됨**

**🔍 증상:**
- "Add time" 버튼이 안 보임
- 시간 입력 후 사라짐
- 7개 시간 모두 입력 안 됨

**✅ 해결 방법:**

1. **Advanced settings 확인**
   ```
   ⚙️ "Advanced settings" 반드시 펼치기
   ☑️ "Restrict execution to specific times" 체크
   ➕ 그 다음에 "Add time" 버튼 보임
   ```

2. **시간 입력 순서**
   ```
   1️⃣ Add time 클릭
   2️⃣ 시간 입력 (예: 08:00)
   3️⃣ 다른 곳 클릭해서 저장
   4️⃣ 다시 Add time 클릭해서 다음 시간 추가
   ```

3. **브라우저별 문제**
   ```
   🌐 Chrome 권장
   🔄 페이지 새로고침 후 재시도
   📱 모바일에서는 설정 어려움 (PC 권장)
   ```

---

## 🌐 4단계 문제: HTTP 모듈 (데이터 수집)

### ❌ **4-1. 연결 타임아웃**

**🔍 증상:**
- "Connection timeout" 오류
- "Request failed" 메시지
- 무한 로딩

**✅ 해결 방법:**

1. **타임아웃 시간 증가**
   ```
   ⚙️ Advanced settings 펼치기
   ⏱️ Timeout을 40에서 60으로 증가
   🔄 Follow redirect: Yes 체크
   ```

2. **User-Agent 헤더 필수 추가**
   ```
   📋 Headers 섹션 펼치기
   ➕ Add item 클릭
   
   Name: User-Agent
   Value: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
   ```

3. **URL 정확성 확인**
   ```
   🌐 정확한 URL: https://www.fanhowmission.ai.cloudbuild.app/rider/
   ❌ 잘못된 예: http://... (s 빠짐)
   ❌ 잘못된 예: .../riders/ (s 추가됨)
   ```

### ❌ **4-2. 403 Forbidden 오류**

**🔍 증상:**
- "403 Forbidden" 오류
- "Access denied"
- "Bot detected"

**✅ 해결 방법:**

1. **User-Agent 변경**
   ```
   📝 현재 User-Agent를 다른 브라우저로 변경:
   
   Edge: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0
   
   Firefox: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0
   ```

2. **추가 헤더 설정**
   ```
   Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
   Accept-Language: ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3
   Accept-Encoding: gzip, deflate
   ```

### ❌ **4-3. 데이터 파싱 불가**

**🔍 증상:**
- "Cannot parse HTML" 오류
- 빈 데이터 반환
- parseHTML 함수 오류

**✅ 해결 방법:**

1. **Parse response 설정 확인**
   ```
   📊 Parse response: Yes (반드시 체크)
   🔍 Return unsafe HTML: Yes (체크)
   ```

2. **HTML 구조 변경 대응**
   ```
   🔧 웹사이트 구조가 바뀌면 XPath 수정 필요
   💡 브라우저에서 F12 → Elements 탭에서 실제 구조 확인
   💡 개발자 도구로 CSS 클래스명 확인
   ```

### ❌ **4-4. 400 Bad Request - "필수 파라미터가 누락되었습니다"**

**증상:**
```json
{"error":"필수 파라미터가 누락되었습니다"}
```

**주요 원인:** 메시지가 빈 문자열로 전달됨

**해결 방법:**

#### **1단계: 3번 Tools 모듈 변수명 확인**
1. **3번 Tools 모듈 더블클릭**
2. **Variable name 확인**: 정확히 `mission_message` 입력 (공백/특수문자 없이)
3. **Variable lifetime**: `one execution cycle` 선택

#### **2단계: 4번 HTTP 모듈 참조 확인**
1. **4번 HTTP 모듈 더블클릭**
2. **Request content에서 다음 확인**:
```json
{
  "message": "{{3.mission_message}}",
  "chat_id": "gt26QiBg", 
  "access_token": "실제_토큰"
}
```

**❌ 잘못된 예시들:**
- `{{2.mission_message}}` (2번이 아닌 3번!)
- `{{mission_message}}` (모듈 번호 없음!)
- `{{3.data}}` (data가 아닌 mission_message!)

#### **3단계: 3번 모듈 출력 재확인**
1. **Run once 실행**
2. **3번 모듈 클릭해서 출력 확인**
3. **정상 출력 예시**:
```json
[
    {
        "mission_message": "🚀 G라이더 미션 현황 📊\n\n📅 2024-01-15 14:30 업데이트\n\n📊 **미션 현황**\n총 미션: 125건..."
    }
]
```

**❌ 문제 출력 예시:**
```json
[
    {
        "mission_message\n​": "// JavaScript 코드 전체가 문자열로..."
    }
]
```

#### **4단계: JavaScript 코드 수정**
3번 Tools 모듈에서 다음 코드로 교체:

```javascript
// 🚀 G라이더 메시지 자동 생성기 (수정된 버전)
const htmlData = {{2.data}};  // HTTP 모듈 2번의 데이터

// 현재 날짜와 시간 가져오기
const now = new Date();
const dateStr = now.toLocaleDateString('ko-KR');
const timeStr = now.toLocaleTimeString('ko-KR', {hour: '2-digit', minute: '2-digit'});

// 기본 메시지 템플릿
let message = `🚀 G라이더 미션 현황 📊

📅 ${dateStr} ${timeStr} 업데이트

`;

try {
    // HTML에서 숫자 찾기 (미션 개수)
    const numbers = htmlData.match(/\d{1,3}(,\d{3})*/g) || [];
    const missionCount = numbers.length > 0 ? numbers[0] : "집계중";
    
    // HTML에서 이름 찾기 (TOP 라이더)
    const namePattern = /라이더[^0-9]*([가-힣]{2,4})/;
    const nameMatch = htmlData.match(namePattern);
    const topRider = nameMatch ? nameMatch[1] : "집계중";
    
    // 메시지 완성
    message += `📊 **미션 현황**
총 미션: ${missionCount}건

🏆 **TOP 라이더**
${topRider}님

💰 **오늘의 포인트**
포인트 집계중...

🎯 화이팅! 더 많은 미션을 완주하세요!
⚡ 자동 업데이트 by G라이더봇`;

} catch (error) {
    // 에러가 나면 기본 메시지
    message += `❌ 데이터 처리 중 오류 발생
다음 업데이트를 기다려주세요.

🔄 자동으로 재시도합니다.`;
}

// 최종 메시지 반환 (중요!)
message;
```

#### **5단계: 즉시 테스트**
1. **Save** 클릭
2. **Run once** 실행  
3. **3번 모듈 출력에서 실제 메시지 텍스트 확인**
4. **4번 모듈에서 message 필드에 내용이 있는지 확인**

---

## 📤 6단계 문제: HTTP 모듈 (전송)

### ❌ **6-1. 웹훅 URL 오류**

**🔍 증상:**
- "404 Not Found" 오류
- "Connection refused"
- "Invalid URL" 메시지

**✅ 해결 방법:**

1. **테스트용 URL 사용**
   ```
   🧪 임시 테스트: https://httpbin.org/post
   📝 이 URL로 먼저 테스트해보세요
   ✅ 성공하면 웹훅 문제, 실패하면 설정 문제
   ```

2. **실제 웹훅 URL 확인**
   ```
   🌐 Render.com 배포 상태 확인
   🌐 URL 끝에 /webhook/mission 경로 확인
   ✅ 예시: https://your-app.onrender.com/webhook/mission
   ```

3. **서버 상태 확인**
   ```
   🔗 브라우저에서 직접 접속해보기
   📊 200 OK 또는 405 Method Not Allowed면 정상
   ❌ 404면 경로 오류, 500이면 서버 오류
   ```

### ❌ **6-2. JSON 형식 오류**

**🔍 증상:**
- "Invalid JSON" 오류
- "Malformed request" 메시지
- 데이터가 안 보내짐

**✅ 해결 방법:**

1. **JSON 문법 확인**
   ```
   ✅ 올바른 예:
   {
     "message": "{{3.mission_message}}",
     "timestamp": "{{formatDate(now; "YYYY-MM-DD HH:mm:ss")}}"
   }
   
   ❌ 잘못된 예:
   {
     message: {{3.mission_message}},  // 따옴표 빠짐
     timestamp: {{formatDate(now; "YYYY-MM-DD HH:mm:ss")}}  // 쉼표 빠짐
   }
   ```

2. **Content-Type 헤더 확인**
   ```
   📋 Headers에 반드시 추가:
   Name: Content-Type
   Value: application/json
   ```

### ❌ **6-3. 변수 참조 오류**

**🔍 증상:**
- "Variable not found" 오류
- {{3.mission_message}} 텍스트가 그대로 전송됨
- 빈 메시지 전송

**✅ 해결 방법:**

1. **모듈 번호 확인**
   ```
   🔢 {{3.mission_message}}에서 3은 Tools 모듈 번호
   📊 Tools 모듈이 실제로 3번째인지 확인
   🔄 모듈 순서 변경 시 번호도 수정
   ```

2. **변수명 정확성 확인**
   ```
   📝 Tools 모듈의 Variable name과 정확히 일치해야 함
   ✅ mission_message (정확)
   ❌ missionMessage, mission-message (잘못됨)
   ```

---

## 🚀 7단계 문제: 웹훅 서버 배포

### ❌ **7-1. Render.com 배포 실패**

**🔍 증상:**
- "Build failed" 오류
- "Deploy failed" 메시지
- 서버가 시작되지 않음

**✅ 해결 방법:**

1. **requirements.txt 확인**
   ```
   📁 파일 위치: 프로젝트 루트 폴더
   📝 내용 확인:
   flask==2.3.3
   requests==2.31.0
   python-telegram-bot==20.6
   
   ❌ 버전 충돌 시 버전 번호 제거:
   flask
   requests
   python-telegram-bot
   ```

2. **빌드 명령어 확인**
   ```
   🔧 Build Command: pip install -r make_requirements.txt
   ❌ requirements.txt가 아니라 make_requirements.txt인지 확인
   ```

3. **시작 명령어 확인**
   ```
   🚀 Start Command: python make_webhook_server.py
   📁 파일명이 정확한지 확인
   ```

4. **Python 버전 설정**
   ```
   💻 Environment: Python 3
   🔧 또는 Environment Variables에서:
   PYTHON_VERSION: 3.11.0
   ```

### ❌ **7-2. 서버 시작 후 바로 종료**

**🔍 증상:**
- "Application failed to respond" 오류
- 서버가 시작되자마자 종료됨
- 로그에 에러 메시지

**✅ 해결 방법:**

1. **포트 설정 확인**
   ```python
   # make_webhook_server.py 마지막 줄 확인:
   if __name__ == '__main__':
       port = int(os.environ.get('PORT', 10000))  # Render는 PORT 환경변수 사용
       app.run(host='0.0.0.0', port=port, debug=True)
   ```

2. **환경변수 설정**
   ```
   🔧 Render.com Environment 탭에서:
   PORT: 10000 (자동 설정됨, 수동 설정 불필요)
   ```

3. **코드 오류 확인**
   ```
   📝 로그에서 Python 에러 확인
   🔍 문법 에러, import 에러 등 수정
   🔄 코드 수정 후 재배포
   ```

### ❌ **7-3. 무료 배포 한도 초과**

**🔍 증상:**
- "Free tier limit exceeded" 메시지
- 새 서비스 생성 불가
- 기존 서비스 정지

**✅ 해결 방법:**

1. **다른 무료 서비스 사용**
   ```
   🌐 Railway.app (매월 $5 크레딧 제공)
   🌐 Vercel.com (서버리스 함수)
   🌐 Heroku.com (제한적 무료)
   ```

2. **기존 서비스 정리**
   ```
   🗑️ 사용하지 않는 Render 서비스 삭제
   📊 월 750시간 한도 확인
   ⏰ 슬립 모드로 리소스 절약
   ```

---

## ✅ 8단계 문제: 자동화 활성화

### ❌ **8-1. Scheduling이 켜지지 않음**

**🔍 증상:**
- Scheduling 토글이 회색
- "Cannot enable scheduling" 오류
- 토글을 클릭해도 반응 없음

**✅ 해결 방법:**

1. **시나리오 저장 확인**
   ```
   💾 반드시 "Save" 버튼으로 저장 후 활성화
   ✅ 저장된 상태에서만 Scheduling 가능
   ```

2. **무료 계정 한도 확인**
   ```
   📊 무료 계정: 월 1,000 operations
   💰 한도 초과 시 유료 플랜 필요
   📈 Usage 탭에서 사용량 확인
   ```

3. **모든 모듈 정상 확인**
   ```
   ✅ 모든 모듈이 녹색 체크 상태여야 함
   ❌ 빨간색 X가 있으면 해결 후 활성화
   ```