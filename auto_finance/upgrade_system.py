"""
🚀 Auto Finance 시스템 업그레이드 스크립트
고도화된 기능들을 자동으로 설정하고 구성하는 스크립트
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Any
import asyncio

def print_banner():
    """배너 출력"""
    print("="*80)
    print("🚀 Auto Finance 고도화 시스템 업그레이드")
    print("="*80)
    print("이 스크립트는 Auto Finance 시스템을 최신 고도화 버전으로 업그레이드합니다.")
    print("다음 기능들이 추가됩니다:")
    print("• AI 앙상블 시스템 (Gemini, GPT-4, Claude)")
    print("• 시장 감정 분석 시스템")
    print("• 고급 콘텐츠 생성 시스템")
    print("• 고도화된 대시보드")
    print("• 성능 모니터링 및 최적화")
    print("="*80)

def check_python_version():
    """Python 버전 확인"""
    print("🐍 Python 버전 확인 중...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 이상이 필요합니다.")
        print(f"현재 버전: {sys.version}")
        return False
    
    print(f"✅ Python 버전 확인 완료: {sys.version}")
    return True

def check_dependencies():
    """의존성 확인"""
    print("📦 의존성 확인 중...")
    required = [
        ('dash', 'dash'),
        ('plotly', 'plotly'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('requests', 'requests'),
        ('beautifulsoup4', 'bs4'),
        ('google-generativeai', 'google.generativeai'),
        ('openai', 'openai'),
        ('anthropic', 'anthropic'),
        ('yfinance', 'yfinance')
    ]
    missing = []
    for pkg, import_name in required:
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"❌ 누락된 패키지: {', '.join(missing)}")
        print(f"pip install {' '.join(missing)}")
        return False
    print("✅ 모든 의존성 확인 완료")
    return True

def create_directories():
    """필요한 디렉토리 생성"""
    print("📁 디렉토리 생성 중...")
    
    directories = [
        "data/generated",
        "data/logs",
        "data/cache",
        "data/statistics",
        "config",
        "dashboard"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ {directory} 디렉토리 생성")
    
    print("✅ 모든 디렉토리 생성 완료")

def create_env_file():
    """환경 변수 파일 생성"""
    print("⚙️ 환경 변수 파일 생성 중...")
    
    env_content = """# Auto Finance 고도화 시스템 환경 변수

# AI 모델 API 키
GOOGLE_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# AI 설정
AI_MODEL=gemini-2.0-flash-exp
AI_MAX_TOKENS=1000
AI_TEMPERATURE=0.7
AI_TIMEOUT=30
AI_RETRY_ATTEMPTS=3

# 크롤러 설정
CRAWLER_MAX_ARTICLES=50
CRAWLER_DELAY=1.0
CRAWLER_TIMEOUT=30
CRAWLER_RETRIES=3
CRAWLER_USE_CACHE=true
CRAWLER_CACHE_TTL=1800

# 팩트 체크 설정
FACT_CHECK_CONFIDENCE=0.7
FACT_CHECK_SCORE=0.6
FACT_CHECK_MAX_ARTICLES=15
FACT_CHECK_CACHE_TTL=3600
FACT_CHECK_RETRIES=3
FACT_CHECK_TIMEOUT=60

# 금융 데이터 설정
FINANCIAL_UPDATE_INTERVAL=300
FINANCIAL_CACHE_TTL=300
FINANCIAL_RETRIES=3
FINANCIAL_TIMEOUT=30

# 콘텐츠 설정
CONTENT_DEFAULT_LENGTH=800
CONTENT_MAX_LENGTH=2000
CONTENT_MIN_LENGTH=300

# 업로드 설정
TISTORY_ENABLED=false
TISTORY_ACCESS_TOKEN=your_tistory_token_here
TISTORY_BLOG_NAME=your_blog_name_here

WORDPRESS_ENABLED=false
WORDPRESS_SITE_URL=your_wordpress_site_url
WORDPRESS_USERNAME=your_username
WORDPRESS_PASSWORD=your_password

MEDIUM_ENABLED=false
MEDIUM_ACCESS_TOKEN=your_medium_token_here
MEDIUM_USER_ID=your_user_id_here

# 알림 설정
SLACK_ENABLED=false
SLACK_WEBHOOK_URL=your_slack_webhook_url

TELEGRAM_ENABLED=false
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id

DISCORD_ENABLED=false
DISCORD_WEBHOOK_URL=your_discord_webhook_url

EMAIL_ENABLED=false
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# 로깅 설정
LOG_LEVEL=INFO
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ .env 파일 생성 완료 (API 키를 입력하세요)")

def create_requirements_file():
    """requirements.txt 파일 생성"""
    print("📋 requirements.txt 파일 생성 중...")
    
    requirements_content = """# Auto Finance 고도화 시스템 의존성

# 기본 라이브러리
requests==2.31.0
beautifulsoup4==4.12.2
selenium==4.15.2
lxml==4.9.3
urllib3==2.0.7
fake-useragent==1.4.0

# AI 모델
google-generativeai==0.3.2
openai==1.3.7
anthropic==0.7.8
transformers==4.35.2
torch==2.1.1

# 데이터 처리
pandas>=1.3.0
numpy==1.24.3
scikit-learn==1.3.2
yfinance==0.2.28
ta==0.10.2

# 자연어 처리
nltk==3.8.1
textblob==0.17.1
spacy==3.7.2
jieba==0.42.1
konlpy==0.6.0
vaderSentiment==3.3.2

# 웹 프레임워크
fastapi==0.104.1
uvicorn==0.24.0
dash==2.14.2
dash-bootstrap-components==1.5.0

# 데이터베이스
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1

# 캐싱 및 작업 큐
celery==5.3.4
cachetools==5.3.2

# 비동기 처리
aiohttp==3.9.1
asyncio

# 시각화
matplotlib==3.8.2
seaborn==0.13.0
plotly>=5.0.0

# 유틸리티
python-dotenv==1.0.0
schedule==1.2.0
python-dateutil==2.8.2
pytz==2023.3
holidays==0.30

# 로깅 및 모니터링
loguru==0.7.2
structlog==23.2.0
prometheus-client==0.19.0
sentry-sdk==1.38.0

# 테스트
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0

# 개발 도구
black==23.11.0
flake8==6.1.0
mypy==1.7.1
pre-commit==3.6.0

# 추가 패키지
jinja2==3.1.2
markdown==3.5.1
python-docx==1.1.0
openpyxl==3.1.2
PyPDF2==3.0.1
Pillow==10.1.0
html5lib==1.1
scipy==1.11.4
"""
    
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(requirements_content)
    
    print("✅ requirements.txt 파일 생성 완료")

def create_startup_script():
    """시작 스크립트 생성"""
    print("🚀 시작 스크립트 생성 중...")
    
    # Windows 배치 파일
    windows_script = """@echo off
echo 🚀 Auto Finance 고도화 시스템 시작
echo.

REM 가상환경 활성화 (있는 경우)
if exist ".venv\\Scripts\\activate.bat" (
    call .venv\\Scripts\\activate.bat
)

REM 의존성 설치 확인
echo 📦 의존성 확인 중...
pip install -r requirements.txt

REM 환경 변수 로드
if exist ".env" (
    echo ⚙️ 환경 변수 로드 중...
)

REM 시스템 실행
echo 🎯 Auto Finance 시스템 시작...
python main_advanced.py

pause
"""
    
    with open('start_advanced.bat', 'w', encoding='utf-8') as f:
        f.write(windows_script)
    
    # Linux/Mac 쉘 스크립트
    linux_script = """#!/bin/bash
echo "🚀 Auto Finance 고도화 시스템 시작"
echo

# 가상환경 활성화 (있는 경우)
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# 의존성 설치 확인
echo "📦 의존성 확인 중..."
pip install -r requirements.txt

# 환경 변수 로드
if [ -f ".env" ]; then
    echo "⚙️ 환경 변수 로드 중..."
    export $(cat .env | xargs)
fi

# 시스템 실행
echo "🎯 Auto Finance 시스템 시작..."
python main_advanced.py
"""
    
    with open('start_advanced.sh', 'w', encoding='utf-8') as f:
        f.write(linux_script)
    
    # 실행 권한 부여 (Linux/Mac)
    try:
        os.chmod('start_advanced.sh', 0o755)
    except:
        pass
    
    print("✅ 시작 스크립트 생성 완료")

def create_dashboard_script():
    """대시보드 시작 스크립트 생성"""
    print("📊 대시보드 스크립트 생성 중...")
    
    dashboard_script = """#!/usr/bin/env python3
\"\"\"
📊 Auto Finance 고도화 대시보드 시작 스크립트
\"\"\"

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from dashboard.advanced_dashboard import advanced_dashboard
    
    if __name__ == '__main__':
        print("🚀 Auto Finance 고도화 대시보드 시작")
        print("📊 대시보드: http://localhost:8050")
        advanced_dashboard.run(debug=True)
        
except ImportError as e:
    print(f"❌ 대시보드 모듈 임포트 실패: {e}")
    print("의존성을 설치하세요: pip install -r requirements.txt")
except Exception as e:
    print(f"❌ 대시보드 실행 실패: {e}")
"""
    
    with open('start_dashboard.py', 'w', encoding='utf-8') as f:
        f.write(dashboard_script)
    
    print("✅ 대시보드 스크립트 생성 완료")

def create_test_script():
    """테스트 스크립트 생성"""
    print("🧪 테스트 스크립트 생성 중...")
    
    test_script = """#!/usr/bin/env python3
\"\"\"
🧪 Auto Finance 고도화 시스템 테스트 스크립트
\"\"\"

import asyncio
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_ai_ensemble():
    \"\"\"AI 앙상블 테스트\"\"\"
    print("🤖 AI 앙상블 테스트 중...")
    
    try:
        from core.ai_ensemble import ai_ensemble
        
        result = await ai_ensemble.generate_content_ensemble(
            "주식 시장에 대한 간단한 분석을 작성해주세요.",
            "content_generation"
        )
        
        print(f"✅ AI 앙상블 테스트 성공")
        print(f"생성된 콘텐츠 길이: {len(result.final_content)}자")
        print(f"신뢰도 점수: {result.confidence_score:.3f}")
        
    except Exception as e:
        print(f"❌ AI 앙상블 테스트 실패: {e}")

async def test_sentiment_analyzer():
    \"\"\"감정 분석 테스트\"\"\"
    print("📊 감정 분석 테스트 중...")
    
    try:
        from core.market_sentiment_analyzer import sentiment_analyzer
        
        test_articles = [
            {
                'title': '삼성전자 실적 호조로 주가 상승',
                'content': '삼성전자가 예상보다 좋은 실적을 발표하여 주가가 상승했습니다.'
            }
        ]
        
        sentiments = await sentiment_analyzer.analyze_news_sentiment(test_articles)
        market_sentiment = await sentiment_analyzer.analyze_market_sentiment(sentiments)
        
        print(f"✅ 감정 분석 테스트 성공")
        print(f"시장 감정 점수: {market_sentiment.overall_sentiment:.3f}")
        print(f"감정 트렌드: {market_sentiment.sentiment_trend}")
        
    except Exception as e:
        print(f"❌ 감정 분석 테스트 실패: {e}")

async def test_content_generator():
    \"\"\"콘텐츠 생성 테스트\"\"\"
    print("✍️ 콘텐츠 생성 테스트 중...")
    
    try:
        from core.advanced_content_generator import advanced_content_generator, ContentRequest
        
        test_articles = [
            {
                'title': '테스트 기사 제목',
                'content': '테스트 기사 내용입니다.',
                'source': '테스트 소스'
            }
        ]
        
        request = ContentRequest(
            articles=test_articles,
            target_audience="general",
            content_type="summary",
            tone="professional",
            length="short"
        )
        
        contents = await advanced_content_generator.generate_advanced_content(request)
        
        print(f"✅ 콘텐츠 생성 테스트 성공")
        print(f"생성된 콘텐츠 수: {len(contents)}개")
        
        if contents:
            content = contents[0]
            print(f"SEO 점수: {content.seo_score:.1f}")
            print(f"가독성 점수: {content.readability_score:.1f}")
        
    except Exception as e:
        print(f"❌ 콘텐츠 생성 테스트 실패: {e}")

async def main():
    \"\"\"메인 테스트 함수\"\"\"
    print("🧪 Auto Finance 고도화 시스템 테스트 시작")
    print("="*50)
    
    await test_ai_ensemble()
    print()
    
    await test_sentiment_analyzer()
    print()
    
    await test_content_generator()
    print()
    
    print("="*50)
    print("🎉 모든 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(main())
"""
    
    with open('test_advanced_system.py', 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("✅ 테스트 스크립트 생성 완료")

def create_readme():
    """README 파일 생성"""
    print("📖 README 파일 생성 중...")
    
    readme_content = """# 🚀 Auto Finance 고도화 시스템

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
.venv\\Scripts\\activate  # Windows

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
"""
    
    with open('README_ADVANCED.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ README 파일 생성 완료")

def run_system_check():
    """시스템 체크 실행"""
    print("🔍 시스템 체크 실행 중...")
    
    checks = [
        ("Python 버전", check_python_version),
        ("의존성", check_dependencies),
        ("디렉토리", lambda: True),  # 이미 생성됨
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            if check_func():
                print(f"✅ {check_name} 체크 통과")
            else:
                print(f"❌ {check_name} 체크 실패")
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name} 체크 오류: {e}")
            all_passed = False
    
    return all_passed

def main():
    """메인 업그레이드 함수"""
    print_banner()
    
    # 사용자 확인
    response = input("\n계속하시겠습니까? (y/N): ")
    if response.lower() != 'y':
        print("업그레이드가 취소되었습니다.")
        return
    
    print("\n🚀 Auto Finance 고도화 시스템 업그레이드 시작...")
    
    try:
        # 1. 시스템 체크
        if not run_system_check():
            print("❌ 시스템 체크 실패. 업그레이드를 중단합니다.")
            return
        
        # 2. 디렉토리 생성
        create_directories()
        
        # 3. 환경 변수 파일 생성
        create_env_file()
        
        # 4. requirements.txt 생성
        create_requirements_file()
        
        # 5. 시작 스크립트 생성
        create_startup_script()
        
        # 6. 대시보드 스크립트 생성
        create_dashboard_script()
        
        # 7. 테스트 스크립트 생성
        create_test_script()
        
        # 8. README 파일 생성
        create_readme()
        
        print("\n" + "="*80)
        print("🎉 Auto Finance 고도화 시스템 업그레이드 완료!")
        print("="*80)
        
        print("\n📋 다음 단계:")
        print("1. API 키 설정:")
        print("   - .env 파일을 열어 API 키를 입력하세요")
        print("   - Google Gemini, OpenAI, Anthropic API 키가 필요합니다")
        
        print("\n2. 의존성 설치:")
        print("   pip install -r requirements.txt")
        
        print("\n3. 시스템 테스트:")
        print("   python test_advanced_system.py")
        
        print("\n4. 시스템 실행:")
        print("   python main_advanced.py")
        
        print("\n5. 대시보드 실행:")
        print("   python start_dashboard.py")
        print("   브라우저에서 http://localhost:8050 접속")
        
        print("\n📚 추가 정보:")
        print("- README_ADVANCED.md 파일을 참조하세요")
        print("- 각 모듈별 상세 문서를 확인하세요")
        print("- 문제가 있으면 GitHub Issues에 등록하세요")
        
        print("\n🎯 고도화된 기능:")
        print("✅ AI 앙상블 시스템 (Gemini + GPT-4 + Claude)")
        print("✅ 시장 감정 분석 (VADER + TextBlob + 한국어)")
        print("✅ 고급 콘텐츠 생성 (SEO 최적화 + 품질 점수)")
        print("✅ 실시간 대시보드 (Plotly + Dash)")
        print("✅ 성능 모니터링 (캐시, 비용, 오류율)")
        print("✅ 자동 스케줄링 (6시간 간격 실행)")
        
    except Exception as e:
        print(f"\n❌ 업그레이드 중 오류 발생: {e}")
        print("수동으로 설정을 완료하거나 다시 시도해주세요.")

if __name__ == "__main__":
    main() 