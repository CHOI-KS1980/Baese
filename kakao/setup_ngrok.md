# 🌐 ngrok으로 실제 웹훅 URL 생성하기

## 1️⃣ ngrok 설치

### macOS (Homebrew)
```bash
brew install ngrok/ngrok/ngrok
```

### 직접 다운로드
1. https://ngrok.com/download 방문
2. macOS용 다운로드
3. 압축 해제 후 PATH에 추가

## 2️⃣ ngrok 계정 생성 (무료)

1. https://ngrok.com 방문
2. 회원가입 (무료)
3. Dashboard에서 Authtoken 복사
4. 터미널에서 인증:
```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

## 3️⃣ 웹훅 서버 실행

### 터미널 1: Flask 서버 실행
```bash
cd kakao
pip3 install flask
python3 temp_webhook_server.py
```

### 터미널 2: ngrok으로 공개 URL 생성
```bash
ngrok http 5000
```

## 4️⃣ 생성된 URL 확인

ngrok 실행 후 나타나는 화면에서:
```
Forwarding    https://abcd1234.ngrok.io -> http://localhost:5000
```

**실제 웹훅 URL**: `https://abcd1234.ngrok.io/webhook`

## 5️⃣ 카카오 i 오픈빌더에 URL 설정

1. 카카오 i 오픈빌더 → 스킬
2. URL 필드에 입력: `https://abcd1234.ngrok.io/webhook`
3. 저장

## 6️⃣ 테스트

카카오톡에서 챗봇에게 메시지 보내기 → Flask 서버 로그에서 요청 확인

## ⚠️ 주의사항

- ngrok 무료버전은 세션 종료 시 URL이 변경됩니다
- 실제 운영을 위해서는 GitHub Actions를 사용하세요
- 이 방법은 테스트 및 웹훅 URL 형식 확인용입니다 