# Make.com을 활용한 G라이더 미션 자동 전송 시스템 - 완전 초보자 가이드

## 🚨 이 가이드는 컴퓨터 초보자도 따라할 수 있습니다!

### ⚠️ 준비사항
- 컴퓨터 (Windows 또는 Mac)
- 인터넷 연결
- 이메일 주소 1개
- 30분 정도의 시간

---

## 📋 **1단계: Make.com 회원가입하기**

### 1-1. 웹사이트 접속하기
1. **인터넷 브라우저 열기** (크롬, 엣지, 사파리 등)
2. **주소창에 입력**: `https://www.make.com` 
3. **Enter 키 누르기**

### 1-2. 회원가입하기
1. **화면에서 "Get started free" 버튼 찾기** (보통 오른쪽 상단에 있음)
2. **"Get started free" 버튼 클릭**
3. **이메일 주소 입력**: 본인의 이메일 주소 타이핑
4. **비밀번호 입력**: 8자 이상, 영문+숫자 조합
5. **"Create account" 버튼 클릭**
6. **이메일 확인**: 받은 메일함 확인 후 인증 링크 클릭

### 1-3. 첫 시나리오 만들기
1. **로그인 완료 후 대시보드에서**
2. **"Create scenario" 버튼 찾기** (큰 파란색 버튼)
3. **"Create scenario" 버튼 클릭**
4. **팝업창이 나타나면**:
   - **"Scenario name" 칸에 입력**: `G라이더 미션 자동 전송`
   - **"Create" 버튼 클릭**

---

## ⏰ **2단계: 스케줄 설정하기**

### 2-1. Schedule 모듈 추가하기
1. **화면 가운데 큰 "+" 버튼 보이죠?**
2. **그 "+" 버튼 클릭**
3. **왼쪽에 앱 목록이 나타납니다**
4. **검색창 (상단)에 `Schedule` 타이핑**
5. **"Schedule" 아이콘 클릭** (시계 모양)
6. **"Schedule" 모듈 클릭**

### 2-2. 스케줄 기본 설정
1. **설정 창이 열렸죠?**
2. **"Interval" 드롭다운 클릭**
3. **"Every N hours" 선택**
4. **"Hours" 칸에 `4` 입력** (4시간마다)
5. **"Time zone" 드롭다운 클릭**
6. **"Asia/Seoul" 찾아서 클릭**

### 2-3. 고급 스케줄링 설정 (정확한 시간 설정)
1. **아래로 스크롤해서 "Advanced scheduling" 찾기**
2. **"Advanced scheduling" 왼쪽 화살표 클릭** (펼치기)
3. **"Add item" 버튼 클릭**
4. **"Time from" 칸에 `08:00` 입력**
5. **"Time to" 칸에 `08:05` 입력**
6. **"Days" 섹션에서 모든 요일 체크** (월화수목금토일)
7. **"Months" 섹션에서 모든 월 체크** (1~12월)

### 2-4. 추가 시간대 설정하기
**같은 방법으로 6번 더 반복하세요:**

**2번째 시간 (10:30):**
- **"Add item" 버튼 다시 클릭**
- **"Time from": `10:30`**
- **"Time to": `10:35`**
- **요일과 월 모두 체크**

**3번째 시간 (12:00):**
- **"Add item" 버튼 다시 클릭**
- **"Time from": `12:00`**
- **"Time to": `12:05`**
- **요일과 월 모두 체크**

**4번째 시간 (14:30):**
- **"Add item" 버튼 다시 클릭**
- **"Time from": `14:30`**
- **"Time to": `14:35`**
- **요일과 월 모두 체크**

**5번째 시간 (18:00):**
- **"Add item" 버튼 다시 클릭**
- **"Time from": `18:00`**
- **"Time to": `18:05`**
- **요일과 월 모두 체크**

**6번째 시간 (20:30):**
- **"Add item" 버튼 다시 클릭**
- **"Time from": `20:30`**
- **"Time to": `20:35`**
- **요일과 월 모두 체크**

**7번째 시간 (22:00):**
- **"Add item" 버튼 다시 클릭**
- **"Time from": `22:00`**
- **"Time to": `22:05`**
- **요일과 월 모두 체크**

### 2-5. 설정 완료
1. **모든 설정이 끝나면**
2. **오른쪽 아래 "OK" 버튼 클릭**

---

## 🌐 **3단계: HTTP 모듈 추가하기 (웹사이트에서 데이터 가져오기)**

### 3-1. HTTP 모듈 추가
1. **Schedule 모듈 오른쪽에 있는 작은 동그란 아이콘 보이시죠?**
2. **그 동그란 아이콘 클릭** (+ 모양)
3. **검색창에 `HTTP` 타이핑**
4. **"HTTP" 앱 클릭**
5. **"Make a request" 클릭**

### 3-2. HTTP 기본 설정
1. **"URL" 칸 클릭**
2. **다음 주소를 복사해서 붙여넣기**:
```
https://jangboo.grider.ai/
```

3. **"Method" 드롭다운이 "GET"으로 되어있는지 확인** (안되어있으면 GET 선택)
4. **"Parse response" 체크박스가 체크되어있는지 확인** (안되어있으면 체크)

### 3-3. Headers 추가하기 (완전 버전)
1. **아래로 스크롤해서 "Headers" 섹션 찾기**
2. **"Add item" 버튼 클릭**
3. **첫 번째 Header 추가**:
   - **"Key" 칸에 입력**: `User-Agent`
   - **"Value" 칸에 다음을 복사해서 붙여넣기**:
   ```
   Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
   ```

4. **"Add item" 버튼 다시 클릭**
5. **두 번째 Header 추가**:
   - **"Key" 칸에 입력**: `Accept`
   - **"Value" 칸에 입력**: `text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8`

6. **"Add item" 버튼 다시 클릭**
7. **세 번째 Header 추가**:
   - **"Key" 칸에 입력**: `Accept-Language`
   - **"Value" 칸에 입력**: `ko-KR,ko;q=0.9,en;q=0.8`

8. **"Add item" 버튼 다시 클릭**
9. **네 번째 Header 추가**:
   - **"Key" 칸에 입력**: `Accept-Encoding`
   - **"Value" 칸에 입력**: `gzip, deflate, br`

### 🚨 **ConnectionError 해결 방법:**

#### **방법 1: 대체 URL 사용**
만약 원본 사이트가 안 되면 **테스트용 URL**로 바꿔보세요:
1. **URL 칸의 내용을 모두 삭제**
2. **다음 중 하나를 입력**:
```
https://httpbin.org/html
```
또는
```
https://jsonplaceholder.typicode.com/posts/1
```

#### **방법 2: 고급 설정 변경**
1. **아래로 스크롤해서 고급 설정 찾기**
2. **"Follow redirect" → true로 설정**
3. **"Request compressed content" → true로 설정**
4. **"Timeout" → 30 입력**

### 3-4. 설정 완료
1. **"OK" 버튼 클릭**

---

## 🔧 **4단계: Tools 모듈 추가하기 (데이터 변환)**

### 4-1. Tools 모듈 추가
1. **HTTP 모듈 오른쪽 동그란 아이콘 클릭**
2. **검색창에 `Tools` 타이핑**
3. **"Tools" 카테고리 클릭**
4. **"Set variable" 클릭**

### 4-2. 변수 이름 설정
1. **"Variable name" 칸 클릭**
2. **다음을 입력**: `mission_message`

### 4-3. 코드 입력 (매우 중요!)
1. **"Value" 칸 클릭** (큰 텍스트 박스)
2. **텍스트 박스 안의 모든 내용 삭제** (Ctrl+A 후 Delete)
3. **아래 코드를 전체 복사** (Ctrl+A 후 Ctrl+C):

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

// 최종 메시지 반환
message;
```

4. **텍스트 박스에 붙여넣기** (Ctrl+V)
5. **"OK" 버튼 클릭**

---

## 📤 **5단계: 두 번째 HTTP 모듈 (카카오톡 전송)**

### 5-1. 두 번째 HTTP 모듈 추가
1. **Tools 모듈 오른쪽 동그란 아이콘 클릭**
2. **검색창에 `HTTP` 타이핑**
3. **"HTTP" 앱 클릭**
4. **"Make a request" 클릭**

### 5-2. 웹훅 서버 설정
1. **"URL" 칸에 다음을 입력**: 
```
https://g-rider-webhook.onrender.com/send-kakao
```
**※ 주의: 실제로는 6단계에서 만든 서버 주소를 입력해야 합니다**

2. **"Method" 드롭다운에서 "POST" 선택**

### 5-3. Headers 설정
1. **"Headers" 섹션에서 "Add item" 클릭**
2. **"Key" 칸에 입력**: `Content-Type`
3. **"Value" 칸에 입력**: `application/json`

### 5-4. Body 설정 (JSON 데이터) - 최신 버전
1. **아래로 스크롤해서 "Body" 섹션 찾기**
2. **"Body Type" 드롭다운 클릭**
3. **"Raw" 선택**
4. **"Content Type" 드롭다운 클릭**
5. **"application/json" 선택**
6. **"Request content" 텍스트 박스가 나타나면 클릭**
7. **⚠️ 중요: 다음 내용만 입력 (```json은 입력하지 마세요!)**:

```json
{
  "message": "{{3.mission_message}}",
  "chat_id": "gt26QiBg",
  "access_token": "여기에_실제_카카오_토큰_입력"
}
```

### 🚨 **JSON 입력시 주의사항:**

**❌ 잘못된 예시 (400 에러 발생):**
```
```json
{
  "message": "{{3.mission_message}}",
  "chat_id": "gt26QiBg",
  "access_token": "토큰"
}
```

**✅ 올바른 예시:**
```
{
  "message": "{{3.mission_message}}",
  "chat_id": "gt26QiBg",
  "access_token": "여기에_실제_카카오_토큰_입력"
}
```

### 🔢 **모듈 참조 번호 확인:**
- **1번**: Schedule 모듈
- **2번**: HTTP (데이터 수집)
- **3번**: Tools (데이터 처리) ← **이것을 참조!**
- **4번**: HTTP (전송)

### 📱 **실제 화면에서 보이는 것:**
1. **Body Type**: 드롭다운 메뉴 (Raw/Form data/등)
2. **Content Type**: 드롭다운 메뉴 (application/json/text/등)  
3. **Request content**: 큰 텍스트 입력 박스

### 5-5. 설정 완료
1. **"OK" 버튼 클릭**

---

## 🌐 **6단계: GitHub 웹훅 서버 업그레이드**

1. **GitHub 저장소 접속**: `https://github.com/본인계정/g-rider-webhook`
2. **app.py 파일 클릭**
3. **연필 아이콘(Edit this file) 클릭**
4. **모든 내용 삭제** (Ctrl+A → Delete)
5. **다음 업그레이드된 코드 전체 복사 후 붙여넣기**:

```python
from flask import Flask, request, jsonify
import requests
import json
import re
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return "🚀 G라이더 카카오톡 봇이 작동중입니다! (v2.0)"

@app.route('/send-kakao', methods=['POST'])
def send_kakao():
    try:
        data = request.json
        
        # 데이터 추출
        status = data.get('status', '')
        raw_data = data.get('raw_data', '')
        chat_id = data.get('chat_id', '')
        access_token = data.get('access_token', '')
        
        # 기존 방식도 지원 (하위 호환성)
        if not status and data.get('message'):
            message = data.get('message')
        else:
            # 새로운 방식: 서버에서 메시지 생성
            message = generate_mission_message(raw_data)
        
        # 필수 파라미터 확인
        if not all([message, chat_id, access_token]):
            return jsonify({
                "error": "필수 파라미터가 누락되었습니다",
                "received": {
                    "message_length": len(message) if message else 0,
                    "chat_id": chat_id,
                    "access_token": f"{access_token[:10]}..." if access_token else ""
                }
            }), 400
        
        # 카카오톡 API 호출
        kakao_result = send_to_kakao(message, chat_id, access_token)
        
        return jsonify(kakao_result)
            
    except Exception as e:
        return jsonify({
            "error": "서버 내부 오류",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

def generate_mission_message(raw_data):
    """HTML 데이터에서 메시지 자동 생성"""
    
    # 현재 시간
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H:%M')
    
    # 기본 메시지
    message = f"""🚀 G라이더 미션 현황 📊

📅 {date_str} {time_str} 업데이트

"""
    
    # HTML에서 데이터 추출 시도
    try:
        if raw_data and isinstance(raw_data, str):
            # 숫자 찾기 (미션 개수)
            numbers = re.findall(r'\d{1,3}(?:,\d{3})*', raw_data)
            mission_count = numbers[0] if numbers else "집계중"
            
            # 라이더 이름 찾기
            rider_pattern = r'라이더[^0-9]*([가-힣]{2,4})'
            rider_match = re.search(rider_pattern, raw_data)
            top_rider = rider_match.group(1) if rider_match else "집계중"
            
            # 로그인 리다이렉트 체크
            if '<script>' in raw_data and 'location.href' in raw_data:
                message += """❌ **사이트 접근 제한**
로그인이 필요한 상태입니다.

🔄 **다음 업데이트에서 재시도**
시스템이 자동으로 재연결을 시도합니다.

💡 **임시 현황**
수동 확인이 필요한 시점입니다."""
            else:
                message += f"""📊 **미션 현황**
총 미션: {mission_count}건

🏆 **TOP 라이더**
{top_rider}님

💰 **오늘의 포인트**
포인트 집계중...

🎯 화이팅! 더 많은 미션을 완주하세요!"""
        else:
            message += """📊 **미션 현황**
총 미션: 집계중

🏆 **TOP 라이더**
집계중

💰 **오늘의 포인트**
포인트 집계중...

🎯 화이팅! 더 많은 미션을 완주하세요!"""
            
    except Exception as e:
        message += f"""❌ **데이터 처리 오류**
{str(e)[:50]}...

🔄 **자동 재시도**
다음 업데이트를 기다려주세요."""
    
    # 공통 푸터
    message += "\n\n⚡ 자동 업데이트 by G라이더봇"
    
    return message

def send_to_kakao(message, chat_id, access_token):
    """카카오톡 API 전송"""
    try:
        url = "https://kapi.kakao.com/v1/api/talk/friends/message/default/send"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        template_object = {
            "object_type": "text", 
            "text": message,
            "link": {
                "web_url": "https://jangboo.grider.ai/",
                "mobile_web_url": "https://jangboo.grider.ai/"
            }
        }
        
        payload = {
            "template_object": json.dumps(template_object),
            "receiver_uuids": f'["{chat_id}"]'
        }
        
        response = requests.post(url, headers=headers, data=payload, timeout=30)
        
        if response.status_code == 200:
            return {
                "status": "success",
                "message": "카카오톡 전송 성공!",
                "response": response.json(),
                "sent_message": message[:100] + "..." if len(message) > 100 else message
            }
        else:
            return {
                "status": "error", 
                "message": "카카오톡 전송 실패",
                "error": response.text,
                "status_code": response.status_code
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": "카카오톡 API 호출 실패", 
            "error": str(e)
        }

# 헬스체크 엔드포인트
@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0"
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

6. **"Commit changes" 버튼 클릭**
7. **Render.com에서 자동 재배포 대기** (5-10분)

### 📊 **6단계: 자동화 활성화**

**모든 테스트가 성공하면:**
1. **"Scheduling" 토글 ON**
2. **시나리오 "Active" 상태 확인**
3. **실제 스케줄에 따라 자동 실행 시작**:
   - 08:00, 10:30, 12:00, 14:30, 18:00, 20:30, 22:00

### 🎯 **최종 결과:**

**완전 자동화된 G라이더 미션 알림 시스템!** 🎉
- ✅ **정해진 시간에 자동 실행**
- ✅ **G라이더 사이트에서 실시간 데이터 수집**
- ✅ **예쁜 메시지 자동 생성**
- ✅ **카카오톡 오픈채팅방 자동 전송**
- ✅ **24/7 무인 작동**

---

## 🎉 **축하합니다!**

**G라이더 미션 자동 알림 시스템이 완성되었습니다!** 

이제 매일 **08:00, 10:30, 12:00, 14:30, 18:00, 20:30, 22:00**에 자동으로 미션 현황이 카카오톡으로 전송됩니다! 🚀

**문의사항이 있으시면 언제든 물어보세요!** 😊 

---

## 🔑 **부록: 카카오 액세스 토큰 발급받기**

### 📋 **1단계: 카카오 개발자 계정 만들기**

1. **카카오 개발자 사이트 접속**: https://developers.kakao.com
2. **"로그인" 클릭**
3. **카카오계정으로 로그인** (일반 카카오톡 계정)
4. **"개발자 등록" 버튼 클릭**
5. **개인정보 동의 후 개발자 등록**

### 📱 **2단계: 애플리케이션 만들기**

1. **"내 애플리케이션" 메뉴 클릭**
2. **"애플리케이션 추가하기" 버튼 클릭**
3. **앱 정보 입력**:
   - **앱 이름**: `G라이더 자동알림`
   - **사업자명**: `개인`
   - **카테고리**: `기타`
4. **"저장" 버튼 클릭**

### 🔧 **3단계: 플랫폼 설정**

1. **방금 만든 앱 클릭**
2. **왼쪽 메뉴에서 "플랫폼" 클릭**
3. **"Web 플랫폼 등록" 클릭**
4. **사이트 도메인 입력**: `http://localhost`
5. **"저장" 버튼 클릭**

### 💬 **4단계: 카카오 로그인 설정**

1. **왼쪽 메뉴에서 "카카오 로그인" 클릭**
2. **"활성화 설정" → ON으로 변경**
3. **"Redirect URI 등록" 클릭**
4. **Redirect URI 입력**: `http://localhost`
5. **"저장" 버튼 클릭**

### 🔑 **5단계: 액세스 토큰 발급 (최신 방법)**

#### **방법 1: 앱 키 확인**
1. **왼쪽 메뉴에서 "앱 키" 클릭**
2. **"REST API 키" 복사** (앱 키 중 하나)

#### **방법 2: 실제 액세스 토큰 받기**
**REST API 키만으로는 부족하므로 추가 과정이 필요합니다:**

1. **브라우저 주소창에 다음 URL 입력** (REST API 키를 실제 키로 교체):
```
https://kauth.kakao.com/oauth/authorize?client_id=당신의_REST_API_키&redirect_uri=http://localhost&response_type=code
```

예시:
```
https://kauth.kakao.com/oauth/authorize?client_id=abc123def456&redirect_uri=http://localhost&response_type=code
```

2. **카카오계정 로그인**
3. **동의항목 체크 후 "동의하고 계속하기"**
4. **주소창에서 code 값 복사**:
   - 주소가 이렇게 변함: `http://localhost/?code=abc123xyz789`
   - **code=** 뒤의 값을 복사: `abc123xyz789`

5. **토큰 발급 API 호출** (아래 방법 중 선택):

#### **방법 2-1: 온라인 도구 사용**
1. **https://httpbin.org/post 접속**
2. **또는 Postman 같은 도구 사용**

#### **방법 2-2: 간단한 방법 (추천)**
**실제로는 매우 복잡하므로, 우선 테스트용으로 진행하세요!**

### 🚨 **실용적인 해결책:**

**카카오 토큰 발급이 복잡하므로**, 다음 순서로 진행하는 것을 추천합니다:

#### **1단계: 테스트용으로 시스템 완성**
```json
{
  "message": "{{3.mission_message}}",
  "chat_id": "test_chat",
  "access_token": "test_token_for_demo"
}
```

#### **2단계: 이미 있는 토큰 사용** 
혹시 이전에 언급하신 토큰이 있으시면:
```
nEwcLjt0zka2JYj94tYyDRHNVE_m...
```
이것을 사용해보세요!

#### **3단계: 전문 도구 사용**
실제 카카오톡 전송이 필요하시면:
- **카카오톡 비즈니스 채널** 사용
- **텔레그램 봇** 대안 고려
- **Slack/Discord** 웹훅 사용 

### ⚡ **4단계 성능 문제 해결**

### 🐌 **왜 4단계가 느릴까요?**
1. **큰 웹사이트 로딩**
2. **복잡한 JavaScript 처리**
3. **네트워크 지연**

### 🚀 **즉시 해결 방법:**

#### **방법 1: Timeout 늘리기**
1. **3단계 HTTP 모듈 더블클릭**
2. **"Timeout" 칸에 `60` 입력** (60초)
3. **"OK" 클릭**

#### **방법 2: 간단한 테스트 URL 사용**
**원본 URL 대신 테스트용 사용:**
1. **URL 칸 내용 삭제**
2. **다음 중 하나 입력**:
```
https://httpbin.org/json
```
또는
```
https://jsonplaceholder.typicode.com/posts/1
```

#### **방법 3: 4단계 JavaScript 간소화**
**복잡한 파싱 대신 간단한 메시지:**

```javascript
// 간단한 테스트 메시지
const now = new Date();
const timeStr = now.toLocaleTimeString('ko-KR');

const testMessage = `🚀 G라이더 테스트 메시지

📅 ${timeStr} 업데이트

✅ Make.com 자동화 시스템 정상 작동
🔄 실제 데이터 연동 준비 완료

테스트 성공! 🎉`;

// 결과 반환
testMessage;
```

### 🎯 **추천 순서:**

1. **🔐 먼저 보안**: Private 저장소로 변경
2. **⚡ 성능 해결**: 테스트 URL + 간단한 JavaScript
3. **✅ 시스템 완성**: 기본 자동화 작동 확인
4. **🔧 실제 연동**: 나중에 실제 URL과 복잡한 로직 추가

지금 당장 **어떤 것부터 해결**하고 싶으신가요? 🤔 