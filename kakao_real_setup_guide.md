# 카카오톡 오픈채팅방 실제 전송 설정 가이드

## 🎯 **목표**
Make.com 테스트 성공 후 → **실제 카카오톡 오픈채팅방 메시지 전송**

---

## 📋 **1단계: 웹훅 서버 업그레이드 (5분)**

### 1-1. GitHub 파일 수정
1. **GitHub 저장소 접속**: `https://github.com/본인계정/g-rider-webhook`
2. **app.py 파일 클릭**
3. **연필 아이콘(Edit this file) 클릭**
4. **모든 내용 삭제** (Ctrl+A → Delete)
5. **아래 코드 전체 복사 후 붙여넣기**:

```python
from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

@app.route('/')
def home():
    return "🚀 G라이더 카카오톡 봇이 작동중입니다!"

@app.route('/send-kakao', methods=['POST'])
def send_kakao():
    try:
        data = request.json
        message = data.get('message', '')
        chat_id = data.get('chat_id', '')
        access_token = data.get('access_token', '')
        
        # 필수 파라미터 확인
        if not all([message, chat_id, access_token]):
            return jsonify({"error": "필수 파라미터가 누락되었습니다"}), 400
        
        # 카카오톡 API 호출
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
        
        response = requests.post(url, headers=headers, data=payload)
        
        if response.status_code == 200:
            return jsonify({
                "status": "success", 
                "message": "카카오톡 전송 성공!",
                "response": response.json()
            })
        else:
            return jsonify({
                "status": "error",
                "message": "카카오톡 전송 실패",
                "error": response.text
            }), response.status_code
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

6. **"Commit changes" 버튼 클릭**
7. **Render.com에서 자동 재배포 대기** (5-10분)

---

## 🔑 **2단계: 카카오 액세스 토큰 준비**

### 방법 1: 기존 토큰 사용 (추천)
이전에 언급하신 토큰이 있다면:
```
nEwcLjt0zka2JYj94tYyDRHNVE_m...
```

### 방법 2: REST API 키 임시 사용
1. **카카오 개발자 사이트 접속**: https://developers.kakao.com
2. **내 애플리케이션 → 앱 선택**
3. **앱 키 → REST API 키 복사**

### 방법 3: 새 액세스 토큰 발급 (고급)
1. **카카오 개발자 콘솔에서 OAuth 설정**
2. **인증 코드 받기**
3. **액세스 토큰 교환**

---

## 🔧 **3단계: Make.com HTTP 모듈 수정 (3분)**

### 3-1. 전송 모듈 업데이트
1. **Make.com 시나리오 접속**
2. **5단계 HTTP 모듈 (전송용) 더블클릭**
3. **URL 변경**:
   ```
   https://g-rider-webhook.onrender.com/send-kakao
   ```

4. **Method**: `POST` (유지)
5. **Headers**: `Content-Type: application/json` (유지)
6. **Body Type**: `Raw` (유지)
7. **Content Type**: `application/json` (유지)
8. **Request content**:
   ```json
   {
     "message": "{{3.mission_message}}",
     "chat_id": "gt26QiBg",
     "access_token": "여기에_실제_카카오_토큰_입력"
   }
   ```

9. **Timeout**: `120` (2분으로 설정)
10. **"OK" 클릭**

---

## 🌐 **4단계: G라이더 실제 데이터 연동 (2분)**

### 4-1. 데이터 수집 모듈 업데이트
1. **3단계 HTTP 모듈 (데이터 수집용) 더블클릭**
2. **URL을 실제 사이트로 변경**:
   ```
   https://jangboo.grider.ai/
   ```

3. **Headers 확인** (이미 설정되어 있을 것):
   - `User-Agent`: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36`
   - `Accept`: `text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8`

4. **Timeout**: `60` 설정
5. **"OK" 클릭**

---

## 🧪 **5단계: 전체 시스템 테스트**

### 5-1. 단계별 테스트
1. **"Run once" 버튼 클릭**
2. **각 모듈 실행 결과 확인**:

#### ✅ **1번 모듈 (Schedule)**: 
- 상태: 트리거 성공
- 결과: 스케줄 정보

#### ✅ **2번 모듈 (HTTP - 데이터 수집)**:
- 상태: G라이더 사이트 접속 성공
- 결과: HTML 데이터 수신

#### ✅ **3번 모듈 (Tools - 메시지 생성)**:
- 상태: JavaScript 실행 성공
- 결과: 예쁜 메시지 생성

#### ✅ **4번 모듈 (HTTP - 카카오톡 전송)**:
- 상태: 웹훅 서버 호출 성공
- 결과: 카카오톡 API 응답

3. **오픈채팅방에서 메시지 수신 확인**

---

## 🚨 **문제 해결 가이드**

### 문제 1: "Service is not reachable"
**원인**: Render.com 서버가 잠자기 상태
**해결**: 
1. 브라우저에서 `https://g-rider-webhook.onrender.com` 접속
2. 1-2분 대기 (서버 깨우기)
3. 다시 테스트

### 문제 2: "Timeout Error"
**원인**: 응답 시간 초과
**해결**:
1. Timeout을 120초로 증가
2. Render 무료 플랜은 첫 요청이 느림

### 문제 3: "카카오톡 전송 실패"
**원인**: 토큰 또는 채팅방 ID 문제
**해결**:
1. 액세스 토큰 재확인
2. 채팅방 ID `gt26QiBg` 정확성 확인
3. 봇이 채팅방에 참여했는지 확인

### 문제 4: "빈 메시지"
**원인**: G라이더 사이트 데이터 파싱 실패
**해결**:
1. 4단계 Tools 모듈의 JavaScript 확인
2. HTML 구조 변경 가능성 점검

---

## 📊 **6단계: 자동화 활성화**

### 6-1. 스케줄 활성화
**모든 테스트가 성공하면:**
1. **"Scheduling" 토글 스위치 ON**
2. **시나리오 상태 "Active" 확인**
3. **실행 시간 재확인**:
   - 08:00 (아침)
   - 10:30 (오전 피크)
   - 12:00 (점심)
   - 14:30 (오후 피크)
   - 18:00 (저녁)
   - 20:30 (저녁 피크)
   - 22:00 (밤)

### 6-2. 모니터링 설정
1. **History 탭에서 실행 기록 확인**
2. **Make.com 모바일 앱 설치** (선택사항)
3. **푸시 알림 설정**

---

## ✅ **완료 체크리스트**

- [ ] **GitHub app.py 파일 업데이트 완료**
- [ ] **Render.com 재배포 완료**
- [ ] **카카오 액세스 토큰 준비 완료**
- [ ] **Make.com HTTP 모듈 URL 변경 완료**
- [ ] **G라이더 실제 사이트 연동 완료**
- [ ] **전체 시스템 테스트 성공**
- [ ] **오픈채팅방 메시지 수신 확인**
- [ ] **자동화 스케줄 활성화 완료**

---

## 🎯 **최종 결과**

### 🚀 **완성된 시스템:**
- ✅ **24/7 무인 자동화**
- ✅ **7개 시간대 정확한 스케줄링**
- ✅ **G라이더 실시간 데이터 수집**
- ✅ **AI 기반 메시지 생성**
- ✅ **카카오톡 오픈채팅방 자동 전송**
- ✅ **에러 처리 및 모니터링**

### 📱 **예상 메시지 형태:**
```
🚀 G라이더 미션 현황 📊

📅 2024년 1월 15일 14:30 업데이트

📊 **미션 현황**
총 미션: 1,234건

🏆 **TOP 라이더**
김철수님

💰 **오늘의 포인트**
5,678 포인트

🎯 화이팅! 더 많은 미션을 완주하세요!
⚡ 자동 업데이트 by G라이더봇
```

---

## 📞 **지원 및 추가 도움**

### 추가 기능 구현 가능:
- **메시지 템플릿 다양화**
- **조건부 전송** (특정 조건시에만)
- **여러 채팅방 동시 전송**
- **실시간 알림** (긴급 상황시)
- **데이터 백업 및 분석**

**🎉 축하합니다! G라이더 미션 자동 알림 시스템이 완성되었습니다! 🎉** 