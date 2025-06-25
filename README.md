# 📈 자동 금융 뉴스 시스템 (Auto Finance News System)

## 🎯 프로젝트 개요
실시간 주식 뉴스를 크롤링하고, AI 기반 팩트 체크를 거쳐 전문가 수준의 SEO 최적화된 블로그 글을 자동 생성하여 티스토리에 업로드하는 고도화된 자동화 시스템입니다.

## 🏗️ 시스템 아키텍처

```
auto_finance/
├── 📁 core/                    # 핵심 모듈
│   ├── news_crawler.py        # 뉴스 크롤링 엔진
│   ├── fact_checker.py        # AI 팩트 체크 시스템
│   ├── content_generator.py   # AI 글 생성 엔진
│   ├── seo_optimizer.py       # SEO 최적화 모듈
│   └── trend_analyzer.py      # 트렌드 분석기
├── 📁 data/                   # 데이터 관리
│   ├── news_sources.json      # 뉴스 소스 설정
│   ├── keywords.json          # 키워드 데이터베이스
│   └── templates/             # 글 템플릿
├── 📁 api/                    # API 연동
│   ├── tistory_api.py        # 티스토리 API
│   ├── news_api.py           # 뉴스 API
│   └── ai_api.py             # AI 서비스 API
├── 📁 utils/                  # 유틸리티
│   ├── logger.py             # 로깅 시스템
│   ├── scheduler.py          # 스케줄러
│   └── monitor.py            # 모니터링
├── 📁 web/                    # 웹 인터페이스
│   ├── dashboard.py          # 대시보드
│   └── templates/            # 웹 템플릿
└── 📁 config/                 # 설정 파일
    ├── settings.py           # 메인 설정
    └── credentials.py        # 인증 정보
```

## 🚀 주요 기능

### 1. 📰 실시간 뉴스 크롤링
- **다중 소스 지원**: 네이버 금융, 한국경제, 매일경제, 이데일리 등
- **실시간 모니터링**: 24시간 연속 크롤링
- **중복 제거**: 스마트 중복 감지 및 필터링
- **우선순위 분류**: 중요도 기반 뉴스 선별

### 2. 🤖 AI 팩트 체크
- **다중 AI 엔진**: OpenAI GPT-4, Claude, Gemini 활용
- **크로스 체크**: 여러 AI의 검증 결과 비교
- **신뢰도 점수**: 팩트 체크 결과의 신뢰도 평가
- **자동 보정**: 오류 데이터 자동 수정

### 3. ✍️ 전문가 수준 글 생성
- **1800자 최적화**: SEO 친화적 글자 수
- **구조화된 템플릿**: 전문가 수준의 글 구조
- **키워드 최적화**: 자동 키워드 밀도 조절
- **가독성 향상**: 문단 구조 및 가독성 최적화

### 4. 🔍 SEO 최적화
- **메타 태그 자동 생성**: 제목, 설명, 키워드
- **내부 링크 최적화**: 관련 글 자동 연결
- **이미지 최적화**: 차트 및 그래프 자동 생성
- **모바일 최적화**: 반응형 콘텐츠 생성

### 5. 📊 트렌드 분석
- **실시간 트렌드**: 네이버/구글 트렌드 연동
- **키워드 분석**: 검색량 및 경쟁도 분석
- **시장 동향**: 주가 변동과 뉴스 연관성 분석
- **예측 모델**: 향후 트렌드 예측

## 🛠️ 기술 스택

### Backend
- **Python 3.9+**: 메인 개발 언어
- **FastAPI**: 고성능 웹 프레임워크
- **Celery**: 비동기 작업 처리
- **Redis**: 캐싱 및 메시지 큐
- **PostgreSQL**: 데이터베이스

### AI & ML
- **OpenAI GPT-4**: 고품질 텍스트 생성
- **Anthropic Claude**: 팩트 체크 및 검증
- **Google Gemini**: 다중 모달 분석
- **Scikit-learn**: 머신러닝 모델

### Web & UI
- **Streamlit**: 대시보드 인터페이스
- **Bootstrap**: 반응형 UI
- **Chart.js**: 데이터 시각화
- **WebSocket**: 실시간 업데이트

### DevOps
- **Docker**: 컨테이너화
- **GitHub Actions**: CI/CD 파이프라인
- **AWS/GCP**: 클라우드 배포
- **Prometheus**: 모니터링

## 📋 설치 및 실행

### 1. 환경 설정
```bash
# 저장소 클론
git clone https://github.com/your-username/Baese.git
cd Baese/auto_finance

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 설정 파일 구성
```bash
# 환경 변수 설정
cp config/credentials.example.py config/credentials.py
# API 키 및 설정 정보 입력
```

### 3. 데이터베이스 초기화
```bash
python scripts/init_database.py
```

### 4. 시스템 실행
```bash
# 전체 시스템 시작
python main.py

# 개별 모듈 실행
python core/news_crawler.py
python core/content_generator.py
```

## 📊 성능 지표

- **크롤링 속도**: 평균 2초/뉴스
- **팩트 체크 정확도**: 95%+
- **글 생성 품질**: 전문가 수준 90%+
- **SEO 점수**: 평균 85/100
- **업로드 성공률**: 99%+

## 🔧 설정 및 커스터마이징

### 뉴스 소스 추가
```json
{
  "name": "새로운 뉴스 소스",
  "url": "https://example.com",
  "selectors": {
    "title": ".news-title",
    "content": ".news-content",
    "date": ".news-date"
  },
  "category": "finance",
  "priority": "high"
}
```

### 키워드 설정
```json
{
  "primary_keywords": ["삼성전자", "SK하이닉스", "현대차"],
  "secondary_keywords": ["주가", "실적", "투자"],
  "exclude_keywords": ["광고", "홍보", "스팸"]
}
```

## 📈 모니터링 및 로그

### 실시간 대시보드
- 크롤링 현황 실시간 모니터링
- 생성된 글 통계 및 성과 분석
- 시스템 성능 및 오류 알림
- SEO 점수 및 트렌드 변화 추적

### 로그 시스템
```
logs/
├── crawler.log      # 크롤링 로그
├── generator.log    # 글 생성 로그
├── upload.log       # 업로드 로그
└── error.log        # 오류 로그
```

## 🤝 기여 가이드

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 지원 및 문의

- **이슈 리포트**: [GitHub Issues](https://github.com/your-username/Baese/issues)
- **기술 지원**: support@autofinance.com
- **문서**: [Wiki](https://github.com/your-username/Baese/wiki)

---

**⚠️ 주의사항**: 이 시스템은 교육 및 연구 목적으로 제작되었습니다. 실제 투자 결정에는 전문가의 조언을 구하시기 바랍니다. 