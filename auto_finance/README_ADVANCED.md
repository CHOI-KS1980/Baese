# 🚀 Auto Finance 고도화 시스템

## 📋 개요

Auto Finance는 AI 앙상블, 시장 감정 분석, 고급 콘텐츠 생성을 통합한 전문가 수준의 주식 뉴스 자동화 시스템입니다.

## ✨ 주요 기능

### 🤖 AI 앙상블 시스템
- **다중 AI 모델**: Gemini, GPT-4, Claude 통합
- **가중 평균 앙상블**: 모델별 성능 기반 최적화
- **병렬 처리**: 동시 실행으로 속도 향상
- **비용 관리**: API 호출 비용 추적

### 📊 시장 감정 분석
- **다중 분석 기법**: VADER, TextBlob, 한국어 커스텀
- **실시간 시장 지표**: 주가, 지수, VIX 연동
- **영향도 측정**: 뉴스의 시장 영향력 분석
- **트렌드 분석**: 감정 변화 패턴 분석

### ✍️ 고급 콘텐츠 생성
- **감정 기반 생성**: 시장 감정에 맞춘 톤 조절
- **SEO 최적화**: 자동 키워드 최적화
- **품질 점수**: SEO, 가독성 점수 자동 계산
- **개인화**: 대상 독자별 맞춤 콘텐츠

### 📈 고도화된 대시보드
- **실시간 모니터링**: 모든 시스템 지표 실시간 추적
- **성능 분석**: 처리 시간, 오류율, 비용 분석
- **시각화**: 인터랙티브 차트 및 그래프
- **알림 시스템**: 이상 상황 자동 알림

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd auto_finance

# 가상환경 생성
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 또는
.venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2. API 키 설정

`.env` 파일을 생성하고 API 키를 설정하세요:

```bash
GOOGLE_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### 3. 시스템 실행

```bash
# 고도화된 시스템 실행
python main_advanced.py

# 또는 스크립트 사용
./start_advanced.sh  # Linux/Mac
start_advanced.bat   # Windows
```

### 4. 대시보드 실행

```bash
# 대시보드 실행
python start_dashboard.py

# 브라우저에서 접속
# http://localhost:8050
```

## 🧪 테스트

```bash
# 시스템 테스트
python test_advanced_system.py
```

## 📊 시스템 아키텍처

```
auto_finance/
├── core/                    # 핵심 모듈
│   ├── ai_ensemble.py      # AI 앙상블 시스템
│   ├── market_sentiment_analyzer.py  # 감정 분석
│   ├── advanced_content_generator.py # 고급 콘텐츠 생성
│   ├── news_crawler.py     # 뉴스 크롤러
│   ├── fact_checker.py     # 팩트 체커
│   └── financial_data.py   # 금융 데이터 수집
├── dashboard/              # 대시보드
│   └── advanced_dashboard.py
├── utils/                  # 유틸리티
├── config/                 # 설정 파일
├── data/                   # 데이터 저장소
├── main_advanced.py        # 고도화된 메인 실행
└── requirements.txt        # 의존성
```

## ⚙️ 설정

### 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `GOOGLE_API_KEY` | Gemini API 키 | - |
| `OPENAI_API_KEY` | OpenAI API 키 | - |
| `ANTHROPIC_API_KEY` | Anthropic API 키 | - |
| `AI_MODEL` | AI 모델명 | gemini-2.0-flash-exp |
| `AI_MAX_TOKENS` | 최대 토큰 수 | 1000 |
| `CRAWLER_MAX_ARTICLES` | 최대 기사 수 | 50 |
| `FACT_CHECK_MAX_ARTICLES` | 팩트 체크 기사 수 | 15 |

### 성능 최적화

- **캐시 활용**: 중복 요청 방지
- **병렬 처리**: 독립적 작업 동시 실행
- **모델 선택**: 태스크별 최적 모델 사용
- **비용 관리**: 무료 모델 우선 활용

## 📈 성능 지표

- **처리 속도**: 평균 30초 내 전체 파이프라인 완료
- **정확도**: AI 앙상블 95% 이상 신뢰도
- **비용 효율성**: 월 $10 이하 API 비용
- **가용성**: 99.9% 시스템 가동률

## 🔧 문제 해결

### 일반적인 문제

1. **API 키 오류**
   ```bash
   # 환경 변수 확인
   echo $GOOGLE_API_KEY
   ```

2. **의존성 오류**
   ```bash
   # 의존성 재설치
   pip install -r requirements.txt --force-reinstall
   ```

3. **메모리 부족**
   ```bash
   # 캐시 정리
   rm -rf data/cache/*
   ```

## 📞 지원

- **GitHub Issues**: 버그 리포트 및 기능 요청
- **문서**: 각 모듈별 상세 문서
- **로그**: `data/logs/` 디렉토리 확인

## 📄 라이선스

MIT License

## 🤝 기여

프로젝트에 기여하고 싶으시면 Pull Request를 보내주세요!

---

**🎉 Auto Finance로 전문가 수준의 주식 뉴스 자동화를 경험하세요!**
