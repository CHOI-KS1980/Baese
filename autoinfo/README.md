# 🚀 AutoInfo - 안드로이드 카카오톡 완전 자동화 프로젝트

## 📖 프로젝트 개요

기존 **웹 크롤링 → 웹훅 서버 → 카카오톡 전송**이 실패했던 문제를 **안드로이드 폰**을 이용해 완전 자동화로 해결하는 프로젝트입니다.

### 🔄 기존 문제점
- ✅ 웹 크롤링: 정상 동작
- ✅ 웹훅 서버: 정상 동작 (데이터 도달)
- ❌ **카카오톡 전송**: 실패 (웹훅에서 카카오톡으로 전송 안됨)

### 🎯 새로운 해결책
**안드로이드 폰 + MacroDroid**를 이용한 완전 자동화
- 🔄 웹 크롤링 → 웹훅 서버 → **안드로이드 MacroDroid** → **카카오톡 UI 자동화** → ✅ 성공!

## 📁 폴더 구조

```
autoinfo/
├── core/                           # 핵심 파일들
│   ├── direct_openchat_sender.py   # 오픈채팅방 직접 전송
│   ├── 카카오톡_직접전송.py         # 카카오톡 직접 전송
│   ├── kakao_scheduled_sender.py   # 스케줄러
│   └── main_*.py                   # 메인 로직
├── webhook/                        # 웹훅 관련
│   ├── webhook_to_android.py       # 안드로이드 연동 웹훅
│   └── (기타 웹훅 파일들)
├── android_automation/             # 안드로이드 자동화
│   ├── 완전자동화_가이드.md        # 상세 가이드
│   └── macrodroid_setup.js         # MacroDroid 스크립트
├── examples/                       # 예제 파일들
└── README.md                       # 이 파일
```

## 🚀 빠른 시작 가이드

### 1단계: 안드로이드 폰 준비
```bash
# 필요한 것들
- Android 7.0 이상
- WiFi 연결
- 카카오톡 설치
- 오픈채팅방 가입 완료
```

### 2단계: MacroDroid 설치
```bash
# Google Play Store에서 설치
1. "MacroDroid" 검색 및 설치
2. Pro 버전 구매 (무제한 매크로)
3. 권한 허용:
   - 접근성 서비스
   - 알림 액세스
   - 기기 관리
```

### 3단계: 매크로 설정
```javascript
// android_automation/macrodroid_setup.js 파일 참조
// MacroDroid 앱에서 JavaScript 액션에 복사
```

### 4단계: 웹훅 서버 수정
```python
# webhook/webhook_to_android.py 파일 사용
python webhook_to_android.py
```

### 5단계: 테스트 실행
```bash
# 테스트 URL 호출
curl -X POST http://localhost:5000/test
```

## 🔧 환경 변수 설정

`.env` 파일 생성:
```env
# MacroDroid 웹훅 설정
MACRODROID_WEBHOOK_KEY=your_macrodroid_key_here
MACRODROID_IDENTIFIER=grider_report
OPENCHAT_ROOM_NAME=G라이더 미션방

# 기존 설정 (유지)
KAKAO_ACCESS_TOKEN=your_token_here
KAKAO_OPENCHAT_ID=GT26QIBG
```

## 📱 MacroDroid 설정 단계

### 1. 웹훅 트리거 생성
```
트리거: Webhook (URL)
- 식별자: grider_report
- 변수: message, chat_room
```

### 2. JavaScript 액션 추가
```javascript
// macrodroid_setup.js 스크립트 복사
```

### 3. 테스트 및 확인
```
1. 웹훅 URL 복사
2. 환경변수에 설정
3. 테스트 실행
```

## 🧪 테스트 방법

### 로컬 테스트
```bash
# 웹훅 서버 실행
cd autoinfo/webhook
python webhook_to_android.py

# 테스트 요청
curl -X POST http://localhost:5000/test
```

### End-to-End 테스트
```bash
# GitHub Actions나 크론잡에서 실제 웹훅 호출
curl -X POST http://your-server.com:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

## 🔍 문제 해결

### 자주 발생하는 문제들

#### 1. MacroDroid 권한 문제
```bash
해결: 설정 → 접근성 → MacroDroid → 켜기
```

#### 2. 카카오톡 UI 변경
```bash
해결: macrodroid_setup.js에서 UI 요소 이름 확인 및 수정
```

#### 3. 웹훅 연결 실패
```bash
해결: MACRODROID_WEBHOOK_KEY 환경변수 확인
```

#### 4. 배터리 최적화
```bash
해결: 설정 → 배터리 → MacroDroid → 배터리 최적화 제외
```

## 📊 모니터링

### 로그 확인
```bash
# 웹훅 서버 로그
tail -f webhook_android.log

# MacroDroid 로그
# MacroDroid 앱 → 로그 탭에서 확인
```

### 상태 확인
```bash
# 서버 상태
curl http://localhost:5000/status

# 설정 확인
curl http://localhost:5000/config
```

## 🎉 완전 자동화 달성!

이제 다음과 같은 플로우가 **완전 자동화**됩니다:

```
1. 웹 크롤링 (기존)
      ↓
2. 데이터 처리 (기존)
      ↓
3. 웹훅 서버 (기존)
      ↓
4. 안드로이드 MacroDroid ← 새로운 해결책!
      ↓
5. 카카오톡 UI 자동화 ← 새로운 해결책!
      ↓
6. 오픈채팅방 메시지 전송 ✅ 성공!
```

## 💡 추가 기능

### 고급 설정
- 여러 채팅방 동시 전송
- 메시지 포맷 커스터마이징
- 실패시 재시도 로직
- 전송 상태 모니터링

### 확장 가능성
- 다른 메신저 앱 지원 (텔레그램, 슬랙 등)
- 음성 메시지 전송
- 이미지/파일 첨부
- 스케줄링 고도화

## 🙋‍♂️ 지원 및 문의

문제가 발생하거나 추가 기능이 필요한 경우:

1. **로그 확인**: 상세한 오류 로그 수집
2. **환경 점검**: 권한, 네트워크, 앱 버전 확인
3. **테스트 진행**: 단계별 테스트로 문제 지점 파악

---

**축하합니다! 🎉 이제 완전 자동화 시스템이 24시간 가동됩니다!** 