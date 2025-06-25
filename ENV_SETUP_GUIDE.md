# 🔐 환경 변수 설정 가이드

## 📝 .env 파일 생성 방법

`auto_finance` 폴더에 `.env` 파일을 생성하고 다음 내용을 입력하세요:

```env
# 🔐 API 키 설정
# OpenAI API 키 (필수)
OPENAI_API_KEY=your_openai_api_key_here

# 티스토리 API 설정 (필수)
TISTORY_ACCESS_TOKEN=your_tistory_access_token_here
TISTORY_BLOG_NAME=your_blog_name_here

# 선택적 API 키들
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# 데이터베이스 설정 (선택사항)
DATABASE_URL=sqlite:///auto_finance.db

# 로깅 설정
LOG_LEVEL=INFO
LOG_FILE=logs/auto_finance.log

# 크롤링 설정
CRAWLING_INTERVAL=3600  # 1시간마다
MAX_NEWS_COUNT=10       # 최대 뉴스 개수

# AI 설정
AI_MODEL=gpt-4
MAX_TOKENS=2000
TEMPERATURE=0.7

# SEO 설정
SEO_KEYWORDS=주식,투자,금융,경제,뉴스
TARGET_WORD_COUNT=1800
```

## 🔑 API 키 발급 방법

### 1. OpenAI API 키
1. https://platform.openai.com 접속
2. 계정 생성 또는 로그인
3. API Keys 메뉴에서 새 키 생성
4. 생성된 키를 `OPENAI_API_KEY`에 입력

### 2. 티스토리 API 키
1. https://www.tistory.com/guide/api/manage/consumer 접속
2. 앱 등록 및 API 키 발급
3. Access Token 발급
4. 블로그 이름 확인

## ⚡ 빠른 시작을 위한 최소 설정

테스트를 위해 다음만 설정해도 됩니다:

```env
OPENAI_API_KEY=your_openai_api_key_here
TISTORY_ACCESS_TOKEN=your_tistory_access_token_here
TISTORY_BLOG_NAME=your_blog_name_here
```

## 🚀 설정 완료 후 실행

```bash
python main.py
```

## 📊 설정 확인

시스템이 정상적으로 실행되면 다음과 같은 메시지가 나타납니다:

```
✅ 환경 검증 성공
🚀 주식 뉴스 자동화 시스템 시작
�� 뉴스 크롤링 시작...
``` 