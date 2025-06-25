# 📈 자동 금융 뉴스 시스템 - 설정 가이드

## 🎯 개요

이 가이드는 **자동 금융 뉴스 시스템**을 완전히 설정하고 실행하는 방법을 단계별로 설명합니다.

## 📋 사전 요구사항

### 1. 시스템 요구사항
- **Python 3.9+**
- **Git**
- **GitHub 계정**
- **최소 4GB RAM**
- **안정적인 인터넷 연결**

### 2. API 키 준비
다음 API 키들을 미리 준비해주세요:

#### 🤖 AI 서비스 API
- **OpenAI API Key** (필수)
  - https://platform.openai.com/api-keys
  - GPT-4 모델 사용 가능한 계정 필요

- **Anthropic Claude API Key** (선택)
  - https://console.anthropic.com/
  - 팩트 체크 강화용

- **Google Gemini API Key** (선택)
  - https://makersuite.google.com/app/apikey
  - 다중 AI 검증용

#### 📱 티스토리 API
- **티스토리 액세스 토큰** (필수)
  - https://www.tistory.com/guide/api/manage/register
  - 블로그 이름과 카테고리 ID도 필요

#### 🗄️ 데이터베이스 (선택)
- **PostgreSQL** 또는 **SQLite**
- **Redis** (캐싱용)

## 🚀 설치 및 설정

### 1단계: 저장소 클론

```bash
# 저장소 클론
git clone https://github.com/your-username/Baese.git
cd Baese/auto_finance

# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate
```

### 2단계: 의존성 설치

```bash
# 기본 의존성 설치
pip install -r requirements.txt

# 한국어 자연어 처리 라이브러리 설치
pip install konlpy
pip install soynlp

# 추가 개발 도구 (선택)
pip install black flake8 mypy
```

### 3단계: 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하세요:

```env
# 🤖 AI 서비스 API 키
OPENAI_API_KEY=your_openai_api_key
CLAUDE_API_KEY=your_claude_api_key
GEMINI_API_KEY=your_gemini_api_key

# 📱 티스토리 API 설정
TISTORY_ACCESS_TOKEN=your_tistory_access_token
TISTORY_BLOG_NAME=your_blog_name
TISTORY_CATEGORY_ID=your_category_id

# 🗄️ 데이터베이스 설정
DATABASE_URL=postgresql://user:pass@localhost/stock_news
REDIS_URL=redis://localhost:6379/0

# 🔍 검색 API (선택)
GOOGLE_SEARCH_API_KEY=your_google_search_api_key
SERPAPI_KEY=your_serpapi_key

# 📊 금융 데이터 API (선택)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key

# 🔐 보안 설정
SECRET_KEY=your_secret_key_here
JWT_SECRET=your_jwt_secret_here

# 📧 알림 설정 (선택)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here

# 📱 카카오톡 설정 (기존 시스템 연동)
KAKAO_ACCESS_TOKEN=your_kakao_access_token_here
KAKAO_REFRESH_TOKEN=your_kakao_refresh_token_here
```

### 4단계: 티스토리 API 설정

#### 4.1 티스토리 앱 등록
1. https://www.tistory.com/guide/api/manage/register 접속
2. 새 앱 등록
3. **Redirect URI**: `http://localhost:8080/callback`
4. **Scope**: `post` 권한 선택

#### 4.2 액세스 토큰 발급
```bash
# 브라우저에서 다음 URL 접속
https://www.tistory.com/oauth/authorize?client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:8080/callback&response_type=token&scope=post
```

#### 4.3 블로그 정보 확인
```bash
# 액세스 토큰으로 블로그 정보 조회
curl "https://www.tistory.com/apis/blog/info?access_token=YOUR_ACCESS_TOKEN&output=json"
```

### 5단계: 설정 검증

```bash
# 환경 검증 실행
python -c "
import sys
sys.path.append('.')
from config.settings import settings
from config.credentials import credentials

print('🔍 설정 검증 중...')
if settings.validate_config():
    print('✅ 설정 검증 완료')
else:
    print('❌ 설정 검증 실패')
    sys.exit(1)

print('🔑 인증 정보 검증 중...')
validation = credentials.validate_required_credentials()
if validation['valid']:
    print('✅ 인증 정보 검증 완료')
else:
    print(f'❌ 인증 정보 누락: {validation[\"missing\"]}')
    sys.exit(1)
"
```

## 🧪 테스트 실행

### 1. 개별 모듈 테스트

```bash
# 뉴스 크롤링 테스트
python core/news_crawler.py

# 팩트 체크 테스트
python core/fact_checker.py

# 콘텐츠 생성 테스트
python core/content_generator.py

# 티스토리 업로드 테스트
python api/tistory_api.py
```

### 2. 전체 시스템 테스트

```bash
# 단일 실행 모드
python main.py

# 연속 실행 모드 (백그라운드)
python main.py --continuous
```

## 🔧 GitHub Actions 설정

### 1. GitHub Secrets 설정

GitHub 저장소의 **Settings > Secrets and variables > Actions**에서 다음 시크릿을 추가하세요:

```
OPENAI_API_KEY=your_openai_api_key
TISTORY_ACCESS_TOKEN=your_tistory_access_token
TISTORY_BLOG_NAME=your_blog_name
TISTORY_CATEGORY_ID=your_category_id
CLAUDE_API_KEY=your_claude_api_key
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=your_database_url
REDIS_URL=your_redis_url
```

### 2. 워크플로우 활성화

1. `.github/workflows/auto_finance.yml` 파일이 저장소에 있는지 확인
2. GitHub Actions 탭에서 워크플로우가 활성화되었는지 확인
3. **Actions > Auto Finance > Run workflow**로 수동 테스트

## 📊 모니터링 및 관리

### 1. 로그 확인

```bash
# 실시간 로그 모니터링
tail -f logs/crawler.log
tail -f logs/error.log

# 특정 시간대 로그 확인
grep "$(date +%Y-%m-%d)" logs/crawler.log
```

### 2. 통계 확인

```bash
# 통계 파일 확인
cat data/statistics.json | python -m json.tool

# 성과 리포트 생성
python scripts/generate_report.py
```

### 3. 성능 모니터링

```bash
# 시스템 리소스 사용량 확인
python utils/monitor.py

# API 사용량 확인
python utils/api_usage.py
```

## 🔧 커스터마이징

### 1. 뉴스 소스 추가

`config/settings.py`의 `NEWS_SOURCES` 리스트에 새 소스를 추가:

```python
NewsSource(
    name="새로운 뉴스 소스",
    url="https://example.com/news",
    category="finance",
    priority="medium",
    selectors={
        "title": ".news-title",
        "content": ".news-content",
        "date": ".news-date",
        "link": ".news-title a"
    },
    crawl_interval=15
)
```

### 2. 키워드 설정

`config/settings.py`의 `KEYWORDS` 섹션 수정:

```python
KEYWORDS = {
    "primary": ["삼성전자", "SK하이닉스", "현대차"],
    "secondary": ["주가", "실적", "투자"],
    "exclude": ["광고", "홍보", "스팸"]
}
```

### 3. 스케줄링 설정

`config/settings.py`의 `SCHEDULE_CONFIG` 수정:

```python
SCHEDULE_CONFIG = {
    "crawl_interval": 5,      # 크롤링 간격 (분)
    "generation_interval": 15, # 글 생성 간격 (분)
    "upload_interval": 30,     # 업로드 간격 (분)
    "peak_hours": {
        "start": "09:00",
        "end": "18:00"
    }
}
```

## 🚨 문제 해결

### 1. 일반적인 오류

#### API 키 오류
```
❌ OpenAI API 키가 유효하지 않습니다.
```
**해결책**: API 키를 확인하고 재발급

#### 네트워크 오류
```
❌ 뉴스 사이트에 접근할 수 없습니다.
```
**해결책**: 인터넷 연결 확인, User-Agent 설정 확인

#### 메모리 부족
```
❌ 메모리 부족으로 인한 오류
```
**해결책**: 가상 메모리 증가, 배치 크기 줄이기

### 2. 디버깅 모드

```bash
# 디버그 모드로 실행
DEBUG=true python main.py

# 상세 로그 출력
python main.py --verbose
```

### 3. 로그 분석

```bash
# 오류 로그 분석
grep "ERROR" logs/error.log | tail -20

# 성능 분석
python utils/analyze_performance.py
```

## 📈 성능 최적화

### 1. 병렬 처리 설정

```python
# config/settings.py
PARALLEL_CONFIG = {
    "max_workers": 4,
    "chunk_size": 10,
    "timeout": 30
}
```

### 2. 캐싱 설정

```python
# config/settings.py
CACHE_CONFIG = {
    "enabled": True,
    "ttl": 3600,  # 1시간
    "max_size": 1000
}
```

### 3. 리소스 제한

```python
# config/settings.py
RESOURCE_CONFIG = {
    "max_memory_mb": 2048,
    "max_cpu_percent": 80,
    "rate_limit_per_minute": 60
}
```

## 🔒 보안 고려사항

### 1. API 키 보안
- API 키를 절대 코드에 하드코딩하지 마세요
- 환경 변수나 시크릿 관리 시스템 사용
- 정기적으로 API 키 로테이션

### 2. 네트워크 보안
- HTTPS 연결만 사용
- 방화벽 설정으로 불필요한 포트 차단
- VPN 사용 권장

### 3. 데이터 보안
- 민감한 데이터 암호화
- 정기적인 백업
- 접근 권한 제한

## 📞 지원 및 문의

### 1. 문서
- [API 문서](docs/api.md)
- [아키텍처 가이드](docs/architecture.md)
- [트러블슈팅 가이드](docs/troubleshooting.md)

### 2. 커뮤니티
- [GitHub Issues](https://github.com/your-username/Baese/issues)
- [Discussions](https://github.com/your-username/Baese/discussions)

### 3. 연락처
- **이메일**: support@autofinance.com
- **텔레그램**: @auto_finance_support

---

**⚠️ 주의사항**: 이 시스템은 교육 및 연구 목적으로 제작되었습니다. 실제 투자 결정에는 전문가의 조언을 구하시기 바랍니다. 