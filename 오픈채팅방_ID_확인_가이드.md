# 🔍 카카오톡 오픈채팅방 ID 및 사용자 ID 확인 가이드

이 가이드는 카카오톡 자동 전송 시스템에 필요한 **오픈채팅방 ID**와 **봇 사용자 ID**를 확인하는 방법을 안내합니다.

## 📋 필요한 ID들

### 1. 봇 사용자 ID (KAKAO_BOT_USER_ID)
- 카카오 API를 호출하는 주체의 고유 ID
- 메시지를 전송하는 사용자의 카카오 ID

### 2. 오픈채팅방 ID (KAKAO_OPENCHAT_ID)
- 메시지를 전송할 대상 채팅방의 고유 ID
- 친구의 UUID 또는 채팅방 고유 식별자

## 🛠️ 자동 확인 도구 사용법

### 단계 1: 확인 도구 실행
```bash
python kakao_id_finder.py
```

### 단계 2: 원하는 작업 선택
```
📋 실행할 작업을 선택하세요:
1. 사용자 정보 조회 (봇 사용자 ID 확인)
2. 친구 목록 조회
3. 테스트 메시지 전송 (나에게 보내기)
4. 앱 정보 조회
5. 모든 정보 조회        ← 추천!
6. 설정 가이드 보기
```

### 단계 3: 결과 확인 및 적용
도구 실행 후 나타나는 ID들을 `.env` 파일에 추가:

```env
KAKAO_BOT_USER_ID=123456789
KAKAO_OPENCHAT_ID=선택한_친구의_UUID
```

## 🔍 수동 확인 방법들

### 방법 1: 카카오톡 앱에서 확인

#### 오픈채팅방 ID 확인
1. **오픈채팅방 생성 또는 참여**
2. **채팅방 설정** → **관리** → **채팅방 정보**
3. **URL에서 ID 확인**
   ```
   예시: openchat.kakao.com/o/gABCDEF123
   → 'gABCDEF123' 부분이 채팅방 ID
   ```

#### 사용자 ID 확인
1. **더보기** → **설정** → **카카오계정**
2. **계정 정보** → **카카오계정 ID 확인**

### 방법 2: 브라우저 개발자 도구 사용

1. **브라우저에서 카카오톡 웹 버전 접속**
   ```
   https://web.kakao.com/
   ```

2. **오픈채팅방 입장**

3. **개발자 도구 열기** (F12)

4. **Network 탭으로 이동**

5. **메시지 전송** 후 요청에서 `room_id` 확인

### 방법 3: API 직접 호출

#### 사용자 정보 조회
```bash
curl -X GET "https://kapi.kakao.com/v2/user/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 친구 목록 조회
```bash
curl -X GET "https://kapi.kakao.com/v1/api/talk/friends" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## ⚙️ 카카오 개발자 콘솔 설정

### 필수 권한 활성화

1. **카카오 개발자 콘솔 접속**
   ```
   https://developers.kakao.com/
   ```

2. **내 애플리케이션** → **앱 선택**

3. **제품 설정** → **카카오 로그인** → **동의항목**에서 다음 권한 활성화:
   - ✅ `profile_nickname` (프로필 정보)
   - ✅ `talk_message` (메시지 전송)
   - ✅ `friends` (친구 목록)

### 플랫폼 등록
1. **앱 설정** → **플랫폼**
2. **Web 플랫폼 등록** (필요 시)
3. **사이트 도메인 추가**

## 🧪 테스트 방법

### 1. 기본 연결 테스트
```python
# kakao_id_finder.py 실행
python kakao_id_finder.py

# 옵션 3 선택 (테스트 메시지 전송)
```

### 2. 실제 메시지 전송 테스트
```python
# message_examples.py로 샘플 메시지 확인
python message_examples.py

# kakao_scheduled_sender.py로 실제 전송 테스트
python -c "
from kakao_scheduled_sender import KakaoOpenChatSender
sender = KakaoOpenChatSender()
result = sender.send_test_message()
print('테스트 결과:', result)
"
```

## 🔧 문제 해결

### 403 권한 오류
```
❌ 권한 부족 해결 방법:
1. 카카오 개발자 콘솔에서 필요 권한 활성화
2. 사용자 동의 과정 완료
3. 액세스 토큰 재발급
```

**해결 방법:**
1. 개발자 콘솔에서 권한 재확인
2. 카카오 로그인 플로우 다시 진행
3. 새로운 액세스 토큰 발급

### 404 사용자 없음 오류
```
❌ 친구를 찾을 수 없음:
1. 대상이 카카오톡 친구인지 확인
2. 차단 상태가 아닌지 확인
3. UUID가 정확한지 확인
```

### API 호출 실패
```
❌ API 호출 실패:
1. 네트워크 연결 확인
2. API 키 유효성 확인
3. 요청 형식 확인
```

## 📱 실전 적용 순서

### 1단계: 기본 설정
```bash
# 1. 환경 설정
python create_env.py

# 2. ID 확인 도구 실행
python kakao_id_finder.py
```

### 2단계: ID 확인 및 설정
```bash
# 모든 정보 조회 (옵션 5)
5

# 결과를 .env 파일에 반영
```

### 3단계: 테스트
```bash
# 기본 테스트
python kakao_id_finder.py  # 옵션 3

# 실제 메시지 테스트
python message_examples.py
```

### 4단계: 자동 전송 시작
```bash
# 스케줄 설정
python setup_kakao_schedule.py

# 수동 시작 (테스트용)
python kakao_scheduled_sender.py
```

## 💡 중요 팁

### 오픈채팅방 vs 일반 채팅
- **일반 채팅**: 친구의 UUID 사용
- **오픈채팅방**: 채팅방 고유 ID 사용
- **그룹 채팅**: 그룹 ID 사용

### 권한 관리
- **최소 권한 원칙**: 필요한 권한만 요청
- **정기 점검**: 권한 상태 주기적 확인
- **토큰 갱신**: 만료 전 미리 갱신

### 보안 고려사항
- **API 키 보호**: `.env` 파일을 git에 포함하지 않기
- **로그 관리**: 민감한 정보 로그에 기록하지 않기
- **접근 제한**: 필요한 사람만 API 키 접근 가능

## 🔗 참고 링크

- [카카오 개발자 콘솔](https://developers.kakao.com/)
- [카카오톡 메시지 API 문서](https://developers.kakao.com/docs/latest/ko/message/)
- [카카오톡 소셜 API 문서](https://developers.kakao.com/docs/latest/ko/kakaotalk-social/)
- [오픈채팅 가이드](https://cs.kakao.com/helps?category=29&locale=ko&service=8)

---

## 📞 지원

문제가 발생하면 다음 순서로 확인해보세요:

1. **도구 실행**: `python kakao_id_finder.py`
2. **권한 확인**: 카카오 개발자 콘솔
3. **로그 확인**: 상세 오류 메시지 확인
4. **테스트**: 단계별 기능 테스트

이 가이드를 따라하면 카카오톡 자동 전송 시스템에 필요한 모든 ID를 확인할 수 있습니다! 🚀 