# 🤖 카카오톡 "나에게 보내기" 자동화 시스템

기존의 복잡한 오픈채팅방 전송 시스템을 **간단하고 안전한 "나에게 보내기"** 방식으로 개선한 버전입니다.

## 🎯 주요 특징

### ✅ 장점
- **설정 간소화**: 복잡한 오픈채팅방 설정 불필요
- **프라이버시 보호**: 나에게만 전송되어 안전
- **안정성 향상**: 공식 카카오 API 사용
- **백업 기능**: 클립보드 자동 복사로 수동 전송 가능
- **스케줄링**: 정해진 시간에 자동 전송

### 🔄 기존 시스템과의 차이점
| 항목 | 기존 (오픈채팅방) | 신규 (나에게 보내기) |
|------|------------------|---------------------|
| 설정 복잡도 | 높음 | 낮음 |
| 권한 요구사항 | 오픈채팅방 관리자 | 개인 계정만 |
| 안정성 | 불안정 | 안정적 |
| 프라이버시 | 공개 | 비공개 |
| API 지원 | 비공식 | 공식 |

## 📋 설치 및 설정

### 1️⃣ 초기 설정 (자동)
```bash
# 초기 설정 스크립트 실행
python3 create_env_for_memo.py
```

### 2️⃣ 패키지 설치
```bash
# 필수 패키지 설치
pip install -r requirements_memo.txt
```

### 3️⃣ 카카오 토큰 발급
```bash
# 토큰 생성기 실행
python3 카카오_토큰_생성기.py
```

### 4️⃣ 환경변수 설정
`.env` 파일에서 발급받은 토큰 설정:
```env
KAKAO_ACCESS_TOKEN=your_actual_token_here
```

## 🚀 사용 방법

### 메인 자동화 시스템
```bash
python3 kakao_memo_automation.py
```

#### 메뉴 옵션:
1. **🚀 자동화 시작** - 스케줄에 따라 자동 전송
2. **⏹️ 자동화 중지** - 스케줄 중지
3. **🧪 테스트 메시지 전송** - 동작 확인
4. **📊 상태 확인** - 전송 통계 및 스케줄 상태
5. **📄 일일 리포트 즉시 전송** - 즉시 리포트 생성/전송
6. **⏰ 시간별 업데이트 즉시 전송** - 즉시 업데이트 전송

### 간단 알림 시스템
```bash
python3 smart_notification_memo.py
```

#### 기능:
- 원클릭 G라이더 리포트 전송
- 클립보드 백업 복사
- 브라우저 자동 열기
- HTML 도우미 생성

## ⏰ 자동 스케줄

### 기본 스케줄
- **일일 리포트**: 오전 8시, 오후 6시
- **정시 업데이트**: 10시, 12시, 14시, 16시, 20시 (업무시간)

### 스케줄 커스터마이징
`.env` 파일에서 시간 조정 가능:
```env
MORNING_REPORT_TIME=08:00
EVENING_REPORT_TIME=18:00
HOURLY_UPDATE_TIMES=10:00,12:00,14:00,16:00,20:00
```

## 📊 전송 내용

### 일일 종합 리포트
```
📊 일일 종합 리포트

🌅 아침점심피크: 30/21 ✅ (달성)
🌇 오후논피크: 26/20 ✅ (달성)  
🌃 저녁피크: 71/30 ✅ (달성)
🌙 심야논피크: 5/29 ❌ (24건 부족)

🏆 TOP 3 라이더
🥇 정재민 | 25.5% (24건)
🥈 김정열 | 19.4% (20건)  
🥉 김공열 | 17.5% (18건)

━━━━━━━━━━━━━━━━━━━━━━━━

🌤️ 안산시 날씨
🌡️ 21°C (맑음)
💧 습도: 90%

━━━━━━━━━━━━━━━━━━━━━━━━
🤖 카카오톡 자동화 시스템
```

## 🔧 고급 설정

### 환경변수 전체 목록
```env
# 필수 설정
KAKAO_ACCESS_TOKEN=your_token_here

# 선택 설정
OPENWEATHER_API_KEY=your_weather_api_key
AUTO_SCHEDULE=true
BACKUP_TO_CLIPBOARD=true
SEND_WEATHER_INFO=true
DUPLICATE_PREVENTION_MINUTES=30

# 로그 설정
LOG_LEVEL=INFO
LOG_FILE_PATH=./logs/kakao_memo_automation.log
```

### 자동 시작 설정

#### Linux/macOS
```bash
# 시작 스크립트 사용
./start_memo_automation.sh

# 또는 cron 등록
crontab -e
# 매일 오전 8시에 자동 시작
0 8 * * * /path/to/your/project/start_memo_automation.sh
```

#### Windows
```batch
# 작업 스케줄러에 등록하거나
# 시작 프로그램에 추가
```

## 🛠️ 개발자 정보

### 파일 구조
```
├── kakao_memo_automation.py      # 메인 자동화 시스템
├── smart_notification_memo.py    # 간단 알림 시스템
├── create_env_for_memo.py        # 초기 설정 스크립트
├── 카카오_토큰_생성기.py          # 토큰 발급 도구
├── requirements_memo.txt         # 필수 패키지 목록
├── start_memo_automation.sh      # 시작 스크립트
├── .env                         # 환경변수 (사용자 생성)
├── logs/                        # 로그 디렉토리
└── backup/                      # 백업 디렉토리
```

### API 사용량
- **카카오톡 메시지 API**: 월 1,000건 무료 (개인용)
- **OpenWeather API**: 일 1,000건 무료 (선택사항)

### 로그 파일
- 위치: `logs/kakao_memo_automation.log`
- 내용: 전송 성공/실패, 스케줄 실행, 오류 정보
- 자동 로테이션: 파일 크기 제한

## ❓ 문제 해결

### 일반적인 문제

#### 1. 토큰 오류
```
❌ 메시지 전송 실패: 401
```
**해결**: 카카오_토큰_생성기.py로 새 토큰 발급

#### 2. 패키지 오류
```
ModuleNotFoundError: No module named 'schedule'
```
**해결**: `pip install -r requirements_memo.txt`

#### 3. 권한 오류
```
❌ 카카오톡 전송 오류: Forbidden
```
**해결**: 카카오 개발자 콘솔에서 메시지 API 권한 확인

### 디버깅 모드
```bash
# 상세 로그로 실행
LOG_LEVEL=DEBUG python3 kakao_memo_automation.py
```

## 🔒 보안 고려사항

### 토큰 보안
- `.env` 파일을 Git에 커밋하지 마세요
- 토큰은 주기적으로 갱신하세요
- 개인 서버에서만 사용하세요

### 데이터 프라이버시
- 모든 메시지는 본인에게만 전송됩니다
- 외부 서버로 데이터가 전송되지 않습니다
- 로컬에서만 처리됩니다

## 📈 업데이트 계획

### v2.0 (계획)
- [ ] 웹 대시보드 추가
- [ ] 다중 계정 지원
- [ ] 커스텀 메시지 템플릿
- [ ] 통계 차트 생성
- [ ] 이메일 백업 전송

### v1.1 (현재)
- [x] 나에게 보내기 구현
- [x] 스케줄링 시스템
- [x] 클립보드 백업
- [x] 날씨 정보 연동
- [x] HTML 도우미

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

## 📞 지원

- **GitHub Issues**: 버그 리포트 및 기능 요청
- **Email**: 기술 문의
- **Wiki**: 상세 문서 및 FAQ

---

## 🎉 마이그레이션 가이드 (기존 사용자)

기존 오픈채팅방 시스템에서 이전하는 방법:

### 1단계: 백업
```bash
# 기존 설정 백업
cp .env .env.old
cp requirements.txt requirements.old.txt
```

### 2단계: 새 시스템 설정
```bash
# 초기 설정 실행
python3 create_env_for_memo.py

# 패키지 재설치
pip install -r requirements_memo.txt
```

### 3단계: 토큰 재발급
```bash
# 나에게 보내기용 토큰 발급
python3 카카오_토큰_생성기.py
```

### 4단계: 테스트
```bash
# 새 시스템 테스트
python3 kakao_memo_automation.py
# 메뉴에서 "3. 테스트 메시지 전송" 선택
```

### 5단계: 기존 시스템 중지
- 기존 오픈채팅방 봇 비활성화
- 크론 작업 제거
- 새 시스템으로 완전 이전

**🎯 이전 완료! 이제 더 간단하고 안전한 "나에게 보내기" 시스템을 사용하세요!** 