# 🔗 카카오 i 오픈빌더 웹훅 URL 확인 완전 가이드

## 🎯 현재 상황 분석

- ✅ 봇이 **"실행"** 상태 → 정상적으로 배포됨
- ❌ **"시작"** 버튼이 안 보임 → 정상 (이미 실행 중이라서)
- 📍 **봇 ID**가 페이지에 표시됨 → 이것을 활용해야 함

## 🔍 웹훅 URL 확인 방법들

### 방법 1: 스킬 설정에서 확인 (가장 정확)

1. **카카오 i 오픈빌더** 접속
2. 좌측 메뉴 **"스킬"** 클릭
3. 생성한 스킬 선택
4. **URL 필드** 확인

**웹훅 URL 형태:**
```
https://chatbot-api.kakao.com/v1/skill/[SKILL_ID]
```

### 방법 2: 개발자 도구로 네트워크 추적

1. **Chrome 개발자 도구** 열기 (F12)
2. **"Network"** 탭 선택
3. 카카오 i 오픈빌더에서 **"테스트"** 실행
4. 네트워크 요청 중 **skill** 관련 URL 찾기

### 방법 3: 봇 설정에서 URL 패턴 추론

봇 ID가 보인다면 다음 패턴으로 웹훅 URL 구성:

```
기본 패턴:
https://chatbot-api.kakao.com/v1/skill/[봇ID 또는 스킬ID]

또는

https://builder-bot.kakao.com/api/v1/skill/[스킬ID]
```

## 🛠️ 정확한 웹훅 URL 찾는 단계별 가이드

### Step 1: 스킬 설정 확인
1. 카카오 i 오픈빌더 로그인
2. **"스킬"** 메뉴 클릭
3. 생성한 스킬 이름 클릭
4. **"URL"** 필드의 주소 복사

### Step 2: 테스트로 웹훅 URL 검증
1. 복사한 URL을 **Postman** 또는 **curl**로 테스트
2. POST 요청으로 다음 데이터 전송:

```json
{
  "version": "2.0",
  "template": {
    "outputs": [
      {
        "simpleText": {
          "text": "테스트 메시지"
        }
      }
    ]
  }
}
```

### Step 3: GitHub Secrets에 URL 설정
정확한 웹훅 URL을 확인했다면:

1. **GitHub Repository** → **Settings** → **Secrets and variables** → **Actions**
2. **WEBHOOK_URL** 수정 또는 새로 생성
3. 확인한 웹훅 URL 입력

## 🔧 문제 해결

### "시작" 버튼이 안 보이는 경우
- **정상 상황**: 봇이 이미 **"실행"** 상태이면 시작 버튼은 숨겨짐
- **대신 확인할 것**: **"중지"** 또는 **"재시작"** 버튼이 있는지 확인

### 봇 ID와 스킬 ID가 다른 경우
- 봇 ID: 챗봇 전체의 식별자
- 스킬 ID: 개별 스킬(기능)의 식별자
- **웹훅 URL에는 스킬 ID를 사용해야 함**

### 웹훅 URL이 작동하지 않는 경우
1. **URL 형식 재확인**:
   ```
   ✅ 올바른 형태: https://chatbot-api.kakao.com/v1/skill/xxxxx
   ❌ 잘못된 형태: https://builder.kakao.com/xxxxx
   ```

2. **스킬이 폴백 블록에 연결되었는지 확인**:
   - 시나리오 → 기본 시나리오 → 폴백 블록
   - 스킬 선택 및 "스킬 데이터" 응답 설정

## 🎯 실제 웹훅 URL 예시

실제로는 다음과 같은 형태의 URL이 나와야 합니다:

```
https://chatbot-api.kakao.com/v1/skill/abcd1234-efgh-5678-ijkl-9012mnop3456

또는

https://builder-bot.kakao.com/api/v1/skill/skill_123456789
```

## 🔍 최종 확인 방법

### curl 명령어로 테스트
```bash
curl -X POST "YOUR_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "2.0",
    "template": {
      "outputs": [
        {
          "simpleText": {
            "text": "연결 테스트 성공!"
          }
        }
      ]
    }
  }'
```

**성공 응답**: HTTP 200 OK
**실패 응답**: HTTP 404 또는 500 오류

## 📞 추가 도움이 필요한 경우

1. **카카오 i 오픈빌더 화면 스크린샷** 공유
2. **현재 보이는 봇 ID** 알려주기
3. **스킬 설정 화면** 스크린샷 공유

이렇게 하면 더 정확한 웹훅 URL을 찾아드릴 수 있습니다! 🚀 