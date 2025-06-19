# 📸 Make.com 시각적 설정 가이드 (스크린샷 포함)

## 🎯 한눈에 보는 전체 과정

```
🏠 홈페이지 → 📝 가입 → 🚀 시나리오 생성 → ⏰ 스케줄 → 🌐 HTTP → 🔧 Tools → 📤 전송 → ✅ 완료
```

---

## 📋 1단계: Make.com 가입 및 로그인

### 🔗 **1-1. 홈페이지 접속**
```
💻 브라우저 주소창에 입력: https://make.com
```

**🔍 화면에서 찾아야 할 요소들:**
- 상단 우측 "Get started free" 파란색 버튼
- 또는 "Log in" 링크 (이미 계정이 있는 경우)

### 🔗 **1-2. 계정 생성**
```
📧 Email 입력
🔒 Password 설정 (최소 8자, 대문자/소문자/숫자 포함)
☑️ Terms of service 체크
```

**🔍 화면에서 찾아야 할 요소들:**
- 이메일 입력 필드 (Email address)
- 비밀번호 입력 필드 (Password)
- 약관 동의 체크박스
- "Create account" 파란색 버튼

### 🔗 **1-3. 이메일 인증**
```
📧 가입한 이메일 확인
✉️ Make.com에서 온 인증 메일 클릭
🔗 "Verify email" 버튼 클릭
```

---

## 🚀 2단계: 첫 번째 시나리오 생성

### 🔗 **2-1. 대시보드 접속**
**🔍 화면에서 찾아야 할 요소들:**
- 왼쪽 사이드바에 "Scenarios" 메뉴
- 중앙에 "Create your first scenario" 큰 버튼
- 또는 우측 상단 "Create scenario" 버튼

### 🔗 **2-2. 시나리오 생성**
```
🎯 시나리오 이름: "G라이더 미션 자동 전송"
📁 폴더: Personal (기본값)
🏷️ 태그: mission, automation (선택사항)
```

**🔍 화면에서 찾아야 할 요소들:**
- "Scenario name" 입력 필드
- "Folder" 드롭다운 (Personal이 기본값)
- "Create" 파란색 버튼

### 🔗 **2-3. 빈 캔버스 확인**
**🔍 화면에서 확인할 것:**
- 흰색 캔버스 배경
- 중앙에 큰 "+" 원형 버튼
- 상단 도구모음 (Save, Run once, Scheduling 등)

---

## ⏰ 3단계: Schedule 모듈 설정

### 🔗 **3-1. 첫 번째 모듈 추가**
```
🖱️ 중앙 "+" 버튼 클릭
🔍 검색창에 "schedule" 입력
📱 "Schedule" 앱 선택 (시계 아이콘)
```

**🔍 화면에서 찾아야 할 요소들:**
- 앱 검색 팝업창
- Schedule 앱 (시계 모양 아이콘)
- "Choose a trigger" 텍스트

### 🔗 **3-2. 트리거 유형 선택**
```
📊 "Every N minutes/hours" 선택
```

**🔍 화면에서 찾아야 할 요소들:**
- 트리거 옵션 목록
- "Every N minutes/hours" 옵션 (시계 아이콘 옆)

### 🔗 **3-3. 기본 스케줄 설정**
```
🔢 Interval: 1
📅 Unit: Day
📍 Start date: 오늘 날짜 (자동 설정됨)
🌍 Time zone: Asia/Seoul
```

**🔍 화면에서 입력할 필드들:**
- "Interval" 숫자 입력 (1)
- "Unit" 드롭다운 (Day 선택)
- "Time zone" 드롭다운 (Asia/Seoul 검색)

### 🔗 **3-4. 고급 시간 설정**
```
⚙️ "Advanced settings" 펼치기
☑️ "Restrict execution to specific times" 체크
⏰ 시간 추가하기:
```

**🔍 실행 시간 입력 (Add time 버튼 7번 클릭):**
```
🌅 08:00 (아침)
🌤️ 10:30 (오전 피크)
☀️ 12:00 (점심)
🌤️ 14:30 (오후 피크)
🌆 18:00 (저녁)
🌃 20:30 (저녁 피크)
🌙 22:00 (밤)
```

**🔍 화면에서 찾아야 할 요소들:**
- "Advanced settings" 접기/펼치기 버튼
- "Restrict execution to specific times" 체크박스
- "Add time" 파란색 버튼
- 시간 입력 필드들 (HH:MM 형식)

---

## 🌐 4단계: HTTP 모듈 (데이터 수집)

### 🔗 **4-1. HTTP 모듈 추가**
```
🖱️ Schedule 모듈 우측 "+" 버튼 클릭
🔍 "HTTP" 검색
🌐 "HTTP" 앱 선택 (지구 아이콘)
```

### 🔗 **4-2. 요청 유형 선택**
```
📡 "Make a request" 선택
```

**🔍 화면에서 찾아야 할 요소들:**
- HTTP 액션 목록
- "Make a request" 옵션 (가장 상단)

### 🔗 **4-3. 요청 설정**
```
🌐 URL: https://www.fanhowmission.ai.cloudbuild.app/rider/
📋 Method: GET (기본값)
📊 Parse response: Yes (체크됨)
```

**🔍 화면에서 입력할 필드들:**
- "URL" 텍스트 필드 (긴 주소 입력)
- "Method" 드롭다운 (GET이 기본값)
- "Parse response" 체크박스 (체크)

### 🔗 **4-4. 헤더 추가**
```
📋 Headers 섹션 펼치기
➕ "Add item" 클릭
📝 Name: User-Agent
📝 Value: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
```

**🔍 화면에서 찾아야 할 요소들:**
- "Headers" 접기/펼치기 섹션
- "Add item" 작은 파란색 버튼
- Name/Value 입력 필드 쌍

### 🔗 **4-5. 고급 설정**
```
⚙️ Advanced settings 펼치기
⏱️ Timeout: 40
🔄 Follow redirect: Yes (체크)
🔍 Return unsafe HTML: Yes (체크)
```

---

## 🔧 5단계: Tools 모듈 (메시지 생성)

### 🔗 **5-1. Tools 모듈 추가**
```
🖱️ HTTP 모듈 우측 "+" 버튼 클릭
🔍 "tools" 검색
🔧 "Tools" 앱 선택 (렌치 아이콘)
```

### 🔗 **5-2. 변수 설정 선택**
```
📝 "Set variable" 선택
```

**🔍 화면에서 찾아야 할 요소들:**
- Tools 액션 목록
- "Set variable" 옵션

### 🔗 **5-3. 변수 정보 입력**
```
📝 Variable name: mission_message
⏰ Variable lifetime: One execution
```

**🔍 화면에서 입력할 필드들:**
- "Variable name" 텍스트 필드
- "Variable lifetime" 드롭다운

### 🔗 **5-4. 메시지 템플릿 입력**

**🔍 큰 텍스트 영역에 다음 코드 복사 붙여넣기:**

```javascript
{{
"🤖 G라이더 미션 현황 알림 (" + formatDate(now; "MM/DD HH:mm") + ")\n" +
"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" +

"📊 **오늘의 미션 현황**\n" +
"• 전체 미션: " + (get(parseHTML(2.data); "//div[contains(@class, 'mission-total')]//text()") ?: "수집 중...") + "\n" +
"• 완료 미션: " + (get(parseHTML(2.data); "//div[contains(@class, 'mission-completed')]//text()") ?: "수집 중...") + "\n" +
"• 진행률: " + (get(parseHTML(2.data); "//div[contains(@class, 'mission-progress')]//text()") ?: "계산 중...") + "\n\n" +

"🏆 **TOP 라이더**\n" +
"• 1위: " + (get(parseHTML(2.data); "//div[contains(@class, 'top-rider-1')]//text()") ?: "집계 중...") + "\n" +
"• 2위: " + (get(parseHTML(2.data); "//div[contains(@class, 'top-rider-2')]//text()") ?: "집계 중...") + "\n" +
"• 3위: " + (get(parseHTML(2.data); "//div[contains(@class, 'top-rider-3')]//text()") ?: "집계 중...") + "\n\n" +

"🌟 **오늘의 포인트**\n" +
"• 배송 팁 적극 활용하세요!\n" +
"• 피크타임 집중 배송 권장\n" +
"• 안전 운전이 최우선입니다!\n\n" +

"💪 화이팅! 오늘도 안전 배송 부탁드려요!\n" +
"━━━━━━━━━━━━━━━━━━━━━━━━━━"
}}
```

**💡 입력 팁:**
- 코드를 정확히 복사해서 붙여넣으세요
- `{{`로 시작해서 `}}`로 끝나는 것 확인
- 중간에 공백이나 줄바꿈이 빠지지 않도록 주의

---

## 📤 6단계: HTTP 모듈 (메시지 전송)

### 🔗 **6-1. 두 번째 HTTP 모듈 추가**
```
🖱️ Tools 모듈 우측 "+" 버튼 클릭
🔍 "HTTP" 다시 검색
🌐 "HTTP" 앱 선택
📡 "Make a request" 선택
```

### 🔗 **6-2. 웹훅 요청 설정**
```
🌐 URL: (나중에 입력할 웹훅 주소)
📋 Method: POST
📊 Body type: JSON
```

**🔍 화면에서 설정할 항목들:**
- "URL" 필드 (일단 비워둠)
- "Method" 드롭다운에서 POST 선택
- "Body type" 드롭다운에서 JSON 선택

### 🔗 **6-3. JSON 본문 설정**

**🔍 Body 섹션의 JSON 텍스트 영역에 입력:**

```json
{
  "message": "{{3.mission_message}}",
  "timestamp": "{{formatDate(now; "YYYY-MM-DD HH:mm:ss")}}",
  "source": "make.com",
  "chat_id": "gt26QiBg"
}
```

### 🔗 **6-4. 헤더 설정**
```
📋 Headers 섹션 펼치기
➕ "Add item" 클릭
📝 Name: Content-Type
📝 Value: application/json
```

---

## 🧪 7단계: 테스트 실행

### 🔗 **7-1. 시나리오 저장**
```
💾 화면 왼쪽 상단 "Save" 버튼 클릭
```

### 🔗 **7-2. 테스트 실행**
```
▶️ 화면 왼쪽 하단 "Run once" 버튼 클릭
```

**🔍 실행 결과 확인:**
- ✅ 각 모듈에 녹색 체크 표시가 나타나면 성공
- ❌ 빨간색 X가 나타나면 오류 발생
- 🔍 모듈을 클릭하면 상세 실행 결과 확인 가능

### 🔗 **7-3. 오류 해결**

**🔍 일반적인 오류들:**

1. **Schedule 모듈 오류**
   ```
   ❌ 시간대 설정 오류
   ✅ Time zone을 Asia/Seoul로 다시 설정
   ```

2. **HTTP 모듈 오류**
   ```
   ❌ URL 접근 불가
   ✅ User-Agent 헤더 추가 확인
   ✅ URL 주소 정확성 재확인
   ```

3. **Tools 모듈 오류**
   ```
   ❌ 문법 오류
   ✅ {{ }} 괄호 확인
   ✅ 코드 재복사
   ```

4. **마지막 HTTP 모듈 오류**
   ```
   ❌ 웹훅 URL 없음
   ✅ 일단 테스트용 URL로 설정 (https://httpbin.org/post)
   ```

---

## 🚀 8단계: 웹훅 서버 배포

### 🔗 **8-1. Render.com 배포**

1. **GitHub 저장소 준비**
   ```
   📁 프로젝트 폴더에 다음 파일들 확인:
   ✅ make_webhook_server.py
   ✅ make_requirements.txt
   ```

2. **Render.com 가입**
   ```
   🌐 https://render.com 접속
   📝 GitHub 계정으로 가입
   ```

3. **웹 서비스 생성**
   ```
   ➕ "New +" 버튼 클릭
   🌐 "Web Service" 선택
   📂 GitHub 저장소 연결
   ```

4. **배포 설정**
   ```
   🔧 Build Command: pip install -r make_requirements.txt
   🚀 Start Command: python make_webhook_server.py
   💻 Environment: Python 3
   📍 Region: Oregon (기본값)
   ```

5. **환경변수 설정 (선택)**
   ```
   📝 Environment 탭에서 추가:
   - TELEGRAM_BOT_TOKEN: (봇 토큰)
   - DISCORD_WEBHOOK_URL: (Discord 웹훅)
   ```

6. **배포 완료**
   ```
   🚀 "Create Web Service" 클릭
   ⏳ 5-10분 대기
   🌐 배포 완료 후 URL 확인 (예: https://your-app.onrender.com)
   ```

### 🔗 **8-2. Make.com에 웹훅 URL 등록**

1. **Make.com 시나리오로 돌아가기**
2. **마지막 HTTP 모듈 편집**
   ```
   🖱️ 마지막 HTTP 모듈 클릭
   ⚙️ 톱니바퀴 아이콘으로 편집 모드 진입
   ```

3. **URL 업데이트**
   ```
   🌐 URL 필드에 입력: https://your-app.onrender.com/webhook/mission
   ```

4. **저장 및 재테스트**
   ```
   💾 "OK" 버튼으로 저장
   ▶️ "Run once"로 다시 테스트
   ```

---

## ✅ 9단계: 자동화 활성화

### 🔗 **9-1. 스케줄링 활성화**
```
🔄 화면 왼쪽 하단 "Scheduling" 토글 클릭
🟦 토글이 파란색으로 변하면 활성화됨
```

**🔍 화면에서 확인할 것:**
- Scheduling 토글이 파란색 (ON 상태)
- "Next run" 시간이 표시됨

### 🔗 **9-2. 모니터링 설정**
```
📊 "History" 탭 클릭
📋 실행 기록 실시간 확인
```

**🔍 History에서 확인할 수 있는 것:**
- 실행 시간
- 성공/실패 상태
- 처리된 데이터량
- 오류 메시지 (실패 시)

---

## 🎨 10단계: 고급 설정 (선택사항)

### 🔗 **10-1. Filter 모듈 추가**
```
🔧 모듈 사이에 "Filter" 추가
📋 조건: 평일에만 실행
```

**조건 설정 예시:**
```javascript
formatDate(now; "dddd") != "Saturday" AND formatDate(now; "dddd") != "Sunday"
```

### 🔗 **10-2. Router 모듈로 분기**
```
🛤️ "Router" 모듈 추가
⏰ 시간대별 다른 메시지 전송
```

### 🔗 **10-3. Error Handler 추가**
```
⚠️ "Error handler" 모듈 추가
📧 실패 시 이메일 알림
🔄 자동 재시도 설정
```

---

## 📱 11단계: 모바일에서 모니터링

### 🔗 **11-1. Make.com 모바일 앱**
```
📱 앱스토어에서 "Make" 검색
⬇️ Make.com 공식 앱 설치
🔑 동일한 계정으로 로그인
```

### 🔗 **11-2. 알림 설정**
```
⚙️ 앱 설정에서 Push 알림 활성화
📊 시나리오 실행 결과 실시간 확인
```

---

## 🎉 완료! 

### ✅ **최종 확인 체크리스트:**

- [ ] ⏰ Schedule 모듈: 7개 시간 모두 설정됨
- [ ] 🌐 첫 번째 HTTP: G라이더 페이지 연결 성공
- [ ] 🔧 Tools 모듈: 메시지 생성 코드 정상 작동
- [ ] 📤 두 번째 HTTP: 웹훅 전송 성공
- [ ] 🚀 웹훅 서버: Render.com 배포 완료
- [ ] 🔄 Scheduling: 자동화 활성화됨 (파란색 토글)
- [ ] 📊 History: 테스트 실행 기록 확인됨

### 🚀 **축하합니다!**

**이제 24/7 자동으로 작동합니다:**
1. 🕐 정해진 시간에 자동 실행 (08:00, 12:00, 18:00, 22:00, 10:30, 14:30, 20:30)
2. 📊 G라이더 미션 페이지에서 실시간 데이터 수집
3. 💬 예쁜 메시지 포맷으로 자동 변환
4. 📤 텔레그램/Discord/슬랙으로 자동 전송
5. 🔄 완전 무인 자동화 완성!

### 💡 **추가 도움이 필요하시면:**
- 📧 Make.com 고객지원: support@make.com
- 📚 공식 문서: https://docs.make.com
- 🎥 YouTube 튜토리얼: "Make.com tutorial" 검색

**이제 컴퓨터를 끄고 어디든 가세요! Make.com이 알아서 메시지를 보내드립니다! 🎯✨** 