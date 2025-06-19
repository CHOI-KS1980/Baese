# 🚀 카카오톡 오픈채팅방 자동 미션 전송 시스템

> **한국천문연구원 KASI API 연동**으로 정확한 공휴일 감지와 함께하는 스마트 자동화 시스템

[![GitHub Actions](https://img.shields.io/badge/GitHub-Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![KakaoTalk](https://img.shields.io/badge/KakaoTalk-FFCD00?style=for-the-badge&logo=kakao&logoColor=black)](https://www.kakaocorp.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![KASI API](https://img.shields.io/badge/KASI-API-0052CC?style=for-the-badge)](https://astro.kasi.re.kr/)

## ✨ 주요 특징

🕘 **한국시간 기준 정확한 스케줄링**
- 평일/주말/공휴일 자동 구분
- 피크타임 15분 간격, 일반 30분 간격 지능형 스케줄

🏛️ **한국천문연구원 공식 API 연동**
- 정확한 공휴일, 임시공휴일, 대체공휴일 감지
- 국경일, 기념일 정보 실시간 반영

🤖 **카카오 i 오픈빌더 완전 연동**
- 웹훅 기반 실시간 메시지 전송
- 상황별 맞춤 메시지 자동 생성

💰 **완전 무료 운영**
- GitHub Actions 무료 할당량 활용
- 서버 없이 클라우드 자동화

## 📅 자동 스케줄

### 평일 (월-금)
- **09:00** - 🌅 활기찬 아침 인사 + 날씨 정보
- **09:30-23:30** - 🎯 30분 간격 미션 메시지
- **06:00-13:00, 17:00-20:00** - ⚡ 15분 간격 피크타임
- **00:00** - 🌙 따뜻한 마무리 인사

### 주말/공휴일
- **09:00** - 🎉 특별한 휴일 인사
- **09:30-23:30** - 🛋️ 30분 간격 여유로운 메시지  
- **06:00-14:00, 17:00-20:00** - 🌿 15분 간격 여가 활동 추천
- **00:00** - ✨ 평안한 밤 인사

## 🎯 메시지 유형

### 🌅 아침 인사 (09:00)
```
🌅 좋은 아침이에요! 오늘도 화이팅! ✨

☀️ 현재 날씨: 맑음 22°C

📅 3일 후 어린이날이 있어요!

⏰ 2024년 05월 02일 (목) 09:00
```

### 🎯 일반 미션 메시지
```
💡 창의적인 아이디어로 문제를 해결해보세요! 🧠

⏰ 2024년 05월 02일 (목) 14:30
```

### 🎉 공휴일 특별 메시지
```
🎉 즐거운 어린이날이에요! 소중한 사람들과 행복한 시간 보내세요! 💖

🇰🇷 뜻깊은 국경일이네요!

⏰ 2024년 05월 05일 (일) 11:00
```

## 🚀 빠른 시작

### 1️⃣ Repository 복사
```bash
git clone https://github.com/your-username/kakao-auto-sender.git
cd kakao-auto-sender
```

### 2️⃣ 필수 계정 준비
- [카카오 i 오픈빌더](https://i.kakao.com/) 계정
- [공공데이터 포털](https://www.data.go.kr/) 계정
- GitHub 계정

### 3️⃣ API 키 발급
1. **한국천문연구원 API**: 공공데이터 포털에서 "한국천문연구원 특일 정보" 신청
2. **카카오 웹훅 URL**: i 오픈빌더에서 스킬 생성 후 웹훅 URL 복사

### 4️⃣ GitHub Secrets 설정
Repository Settings → Secrets and variables → Actions
```
WEBHOOK_URL=your-kakao-webhook-url
KOREA_HOLIDAY_API_KEY=your-kasi-api-key
OPENWEATHER_API_KEY=your-weather-api-key (선택)
```

### 5️⃣ 실행 확인
Actions 탭에서 "Run workflow" 클릭하여 테스트!

## 📂 프로젝트 구조

```
kakao-auto-sender/
├── .github/
│   └── workflows/
│       └── auto-send-mission.yml    # GitHub Actions 워크플로우
├── github_actions_sender.py         # 메인 실행 스크립트
├── requirements.txt                 # Python 의존성
├── 카카오톡_자동전송_사용법.md           # 상세 설정 가이드
└── README.md                       # 프로젝트 소개
```

## 🔧 고급 설정

### 환경 변수 전체 목록
```bash
# 필수
WEBHOOK_URL=카카오톡_웹훅_URL
KOREA_HOLIDAY_API_KEY=한국천문연구원_API_키

# 선택사항
OPENWEATHER_API_KEY=날씨_API_키
KAKAO_REST_API_KEY=카카오_REST_API_키
KAKAO_CHANNEL_ID=카카오톡_채널_ID
DEBUG_MODE=false
```

### 스케줄 커스터마이징
`auto-send-mission.yml`에서 cron 표현식 수정 가능:
```yaml
# 예: 매 시간 정각에 실행
- cron: '0 * * * *'

# 예: 평일 오전 9시-6시 1시간 간격
- cron: '0 9-18 * * 1-5'
```

## 📊 모니터링

### GitHub Actions 로그
- Actions 탭에서 실행 상태 실시간 확인
- 성공/실패 알림 이메일 자동 발송
- 상세 실행 로그로 디버깅 가능

### 시스템 상태 확인
```
✅ 메시지 전송 성공!
📝 전송된 메시지: 🌅 좋은 아침이에요! 오늘도 화이팅! ✨...
🕐 현재 시간: 2024-05-02 09:00:00 KST
📅 날짜 정보: 2024년 05월 02일 (목요일)
💼 평일입니다!
🎉 전송 완료!
```

## 🛠️ 문제 해결

### 자주 묻는 질문

**Q: 메시지가 전송되지 않아요**
```bash
# 1. 환경 변수 확인
echo $WEBHOOK_URL

# 2. 디버그 모드 활성화
DEBUG_MODE=true

# 3. 수동 실행으로 로그 확인
```

**Q: 공휴일이 인식되지 않아요**
- 한국천문연구원 API 키가 올바른지 확인
- 공공데이터 포털에서 API 활용신청 상태 확인

**Q: 시간이 맞지 않아요**
- 모든 시간은 한국시간(KST) 기준으로 자동 변환됩니다
- GitHub Actions는 UTC 기준이지만 코드에서 자동 변환 처리

## 🏗️ 기술 스택

- **Python 3.9+**: 메인 실행 언어
- **GitHub Actions**: 무료 서버리스 스케줄러
- **카카오 i 오픈빌더**: 메시지 전송 플랫폼
- **한국천문연구원 API**: 정확한 공휴일 정보
- **OpenWeather API**: 실시간 날씨 정보
- **pytz**: 한국시간 처리

## 🔄 업데이트 내역

### v3.0 (2024.12) - KASI API 통합
- ✅ 한국천문연구원 공식 API 연동
- ✅ 임시공휴일, 대체공휴일 정확 감지
- ✅ 한국시간 기준 완전 자동화

### v2.1 (2024.11) - 스케줄 개선
- ✅ 피크타임 15분 간격 적용
- ✅ 시간대별 맞춤 메시지 강화

### v2.0 (2024.10) - 다중 기능 추가
- ✅ 날씨 정보 연동
- ✅ 공휴일별 특별 메시지
- ✅ 디버그 모드 추가

## 📜 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

## 🤝 기여하기

1. Fork 프로젝트
2. Feature 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 Push (`git push origin feature/amazing-feature`)
5. Pull Request 생성

## 📞 지원

- 🐛 **버그 리포트**: [GitHub Issues](https://github.com/your-username/repo/issues)
- 💡 **기능 제안**: [GitHub Discussions](https://github.com/your-username/repo/discussions)
- 📧 **문의**: your-email@example.com

## 🙏 감사인사

- [한국천문연구원](https://astro.kasi.re.kr/) - 정확한 공휴일 API 제공
- [카카오](https://www.kakaocorp.com/) - i 오픈빌더 플랫폼 제공
- [GitHub](https://github.com/) - Actions 무료 서비스 제공

---

<div align="center">

**⭐ 이 프로젝트가 도움이 되셨다면 Star를 눌러주세요! ⭐**

Made with ❤️ by AI Assistant & Korean Time Zone 🇰🇷

</div> 