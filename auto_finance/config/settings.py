"""
⚙️ Auto Finance 설정 파일
고도화된 주식 뉴스 자동화 시스템 설정
"""

import os
from typing import List, Dict, Any
from datetime import datetime

# 기본 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_DIR = os.path.join(DATA_DIR, "logs")

# 로깅 설정
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
LOG_FILE = os.path.join(LOG_DIR, f"auto_finance_{datetime.now().strftime('%Y%m%d')}.log")

# AI 설정
AI_CONFIG = {
    'model_name': os.getenv('AI_MODEL', 'gemini-2.0-flash-exp'),
    'api_key': os.getenv('GOOGLE_API_KEY'),
    'max_tokens': int(os.getenv('AI_MAX_TOKENS', '1000')),
    'temperature': float(os.getenv('AI_TEMPERATURE', '0.7')),
    'timeout': int(os.getenv('AI_TIMEOUT', '30')),
    'retry_attempts': int(os.getenv('AI_RETRY_ATTEMPTS', '3')),
    'rate_limit': int(os.getenv('AI_RATE_LIMIT', '10'))  # 분당 요청 수
}

# 뉴스 소스 설정
NEWS_SOURCES = [
    {
        'name': '네이버 뉴스',
        'url': 'https://news.naver.com/',
        'base_url': 'https://news.naver.com',
        'enabled': True,
        'priority': 'high',
        'category': 'general',
        'keywords': ['주식', '투자', '경제', '금융'],
        'selectors': {
            'article': 'li.cnf_news_item',
            'title': 'a.cnf_news',
            'link': 'a.cnf_news',
            'content': '',
            'date': ''
        },
        'use_selenium': False,
        'wait_time': 0
    },
    {
        'name': '한국경제',
        'url': 'https://www.hankyung.com/economy',
        'base_url': 'https://www.hankyung.com',
        'enabled': True,
        'priority': 'high',
        'category': 'economy',
        'keywords': ['주식', '투자', '경제', '금융'],
        'selectors': {
            'article': 'div.news-list',
            'title': 'a.news-tit',
            'link': 'a.news-tit',
            'content': '',
            'date': ''
        },
        'use_selenium': False,
        'wait_time': 0
    },
    {
        'name': '매일경제',
        'url': 'https://www.mk.co.kr/news/economy/',
        'base_url': 'https://www.mk.co.kr',
        'enabled': True,
        'priority': 'medium',
        'category': 'economy',
        'keywords': ['주식', '투자', '경제', '금융'],
        'selectors': {
            'article': 'div.list_area',
            'title': 'a.news_ttl',
            'link': 'a.news_ttl',
            'content': '',
            'date': ''
        },
        'use_selenium': False,
        'wait_time': 0
    }
]

# 크롤러 설정
CRAWLER_CONFIG = {
    'max_articles_per_source': int(os.getenv('CRAWLER_MAX_ARTICLES', '50')),
    'request_delay': float(os.getenv('CRAWLER_DELAY', '1.0')),
    'timeout': int(os.getenv('CRAWLER_TIMEOUT', '30')),
    'max_retries': int(os.getenv('CRAWLER_RETRIES', '3')),
    'use_cache': os.getenv('CRAWLER_USE_CACHE', 'true').lower() == 'true',
    'cache_ttl': int(os.getenv('CRAWLER_CACHE_TTL', '1800')),  # 30분
    'use_selenium': os.getenv('CRAWLER_USE_SELENIUM', 'false').lower() == 'true',
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 팩트 체크 설정
FACT_CHECK_CONFIG = {
    'confidence_threshold': float(os.getenv('FACT_CHECK_CONFIDENCE', '0.7')),
    'score_threshold': float(os.getenv('FACT_CHECK_SCORE', '0.6')),
    'max_articles_per_check': int(os.getenv('FACT_CHECK_MAX_ARTICLES', '10')),
    'cache_ttl': int(os.getenv('FACT_CHECK_CACHE_TTL', '3600')),  # 1시간
    'retry_attempts': int(os.getenv('FACT_CHECK_RETRIES', '3')),
    'timeout': int(os.getenv('FACT_CHECK_TIMEOUT', '60'))
}

# 금융 데이터 설정
FINANCIAL_CONFIG = {
    'stock_symbols': [
        '005930.KS',  # 삼성전자
        '000660.KS',  # SK하이닉스
        '035420.KS',  # NAVER
        '035720.KS',  # 카카오
        '373220.KS',  # LG에너지솔루션
        'AAPL',       # Apple
        'MSFT',       # Microsoft
        'GOOGL',      # Google
        'TSLA',       # Tesla
        'NVDA'        # NVIDIA
    ],
    'index_symbols': [
        '^KS11',      # KOSPI
        '^KQ11',      # KOSDAQ
        '^GSPC',      # S&P 500
        '^DJI',       # Dow Jones
        '^IXIC',      # NASDAQ
        '^TNX',       # 10-Year Treasury
        '^VIX',       # VIX
        'GC=F',       # Gold Futures
        'CL=F'        # Crude Oil Futures
    ],
    'update_interval': int(os.getenv('FINANCIAL_UPDATE_INTERVAL', '300')),  # 5분
    'cache_ttl': int(os.getenv('FINANCIAL_CACHE_TTL', '300')),  # 5분
    'max_retries': int(os.getenv('FINANCIAL_RETRIES', '3')),
    'timeout': int(os.getenv('FINANCIAL_TIMEOUT', '30'))
}

# 콘텐츠 생성 설정
CONTENT_CONFIG = {
    'templates': {
        'article': """
# {{title}}

{{content}}

**키워드**: {{keywords}}
**생성일시**: {{timestamp}}
        """,
        'summary': """
## 요약

{{content}}

**생성일시**: {{timestamp}}
        """,
        'analysis': """
## 분석

{{content}}

**분석일시**: {{timestamp}}
        """
    },
    'default_length': int(os.getenv('CONTENT_DEFAULT_LENGTH', '800')),
    'max_length': int(os.getenv('CONTENT_MAX_LENGTH', '2000')),
    'min_length': int(os.getenv('CONTENT_MIN_LENGTH', '300')),
    'seo_keywords': [
        '주식', '투자', '경제', '금융', '시장', '분석', '전망', '전략',
        '포트폴리오', '리스크', '수익률', '성장', '가치', '배당'
    ],
    'tone_options': ['professional', 'casual', 'technical', 'educational'],
    'content_types': ['article', 'summary', 'analysis', 'report']
}

# 업로드 설정
UPLOAD_CONFIG = {
    'platforms': {
        'tistory': {
            'enabled': os.getenv('TISTORY_ENABLED', 'false').lower() == 'true',
            'access_token': os.getenv('TISTORY_ACCESS_TOKEN'),
            'blog_name': os.getenv('TISTORY_BLOG_NAME'),
            'api_url': 'https://www.tistory.com/apis'
        },
        'wordpress': {
            'enabled': os.getenv('WORDPRESS_ENABLED', 'false').lower() == 'true',
            'site_url': os.getenv('WORDPRESS_SITE_URL'),
            'username': os.getenv('WORDPRESS_USERNAME'),
            'password': os.getenv('WORDPRESS_PASSWORD'),
            'api_url': '/wp-json/wp/v2'
        },
        'medium': {
            'enabled': os.getenv('MEDIUM_ENABLED', 'false').lower() == 'true',
            'access_token': os.getenv('MEDIUM_ACCESS_TOKEN'),
            'user_id': os.getenv('MEDIUM_USER_ID'),
            'api_url': 'https://api.medium.com/v1'
        }
    },
    'max_retries': int(os.getenv('UPLOAD_RETRIES', '3')),
    'retry_delay': int(os.getenv('UPLOAD_RETRY_DELAY', '5')),
    'timeout': int(os.getenv('UPLOAD_TIMEOUT', '30')),
    'default_platform': os.getenv('UPLOAD_DEFAULT_PLATFORM', 'tistory'),
    'auto_publish': os.getenv('UPLOAD_AUTO_PUBLISH', 'false').lower() == 'true'
}

# 알림 설정
NOTIFICATION_CONFIG = {
    'channels': {
        'email': {
            'enabled': os.getenv('EMAIL_ENABLED', 'false').lower() == 'true',
            'smtp_server': os.getenv('EMAIL_SMTP_SERVER'),
            'smtp_port': int(os.getenv('EMAIL_SMTP_PORT', '587')),
            'username': os.getenv('EMAIL_USERNAME'),
            'password': os.getenv('EMAIL_PASSWORD'),
            'from_email': os.getenv('EMAIL_FROM'),
            'to_emails': os.getenv('EMAIL_TO', '').split(',')
        },
        'slack': {
            'enabled': os.getenv('SLACK_ENABLED', 'false').lower() == 'true',
            'webhook_url': os.getenv('SLACK_WEBHOOK_URL'),
            'channel': os.getenv('SLACK_CHANNEL', '#general'),
            'username': os.getenv('SLACK_USERNAME', 'Auto Finance Bot')
        },
        'telegram': {
            'enabled': os.getenv('TELEGRAM_ENABLED', 'false').lower() == 'true',
            'bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
            'chat_id': os.getenv('TELEGRAM_CHAT_ID')
        },
        'discord': {
            'enabled': os.getenv('DISCORD_ENABLED', 'false').lower() == 'true',
            'webhook_url': os.getenv('DISCORD_WEBHOOK_URL'),
            'username': os.getenv('DISCORD_USERNAME', 'Auto Finance Bot')
        }
    },
    'rate_limits': {
        'email': int(os.getenv('EMAIL_RATE_LIMIT', '10')),  # 시간당
        'slack': int(os.getenv('SLACK_RATE_LIMIT', '100')),  # 시간당
        'telegram': int(os.getenv('TELEGRAM_RATE_LIMIT', '30')),  # 분당
        'discord': int(os.getenv('DISCORD_RATE_LIMIT', '50'))  # 시간당
    },
    'templates': {
        'email': """
<h2>{{title}}</h2>
<p>{{content}}</p>
<p><small>생성일시: {{timestamp}}</small></p>
        """,
        'slack': "**{{title}}**\n{{content}}\n\n_생성일시: {{timestamp}}_",
        'telegram': "**{{title}}**\n\n{{content}}\n\n_생성일시: {{timestamp}}_",
        'discord': "**{{title}}**\n{{content}}\n\n*생성일시: {{timestamp}}*"
    },
    'priority_levels': ['low', 'normal', 'high', 'urgent'],
    'categories': ['system', 'news', 'financial', 'error', 'warning']
}

# 대시보드 설정
DASHBOARD_CONFIG = {
    'host': os.getenv('DASHBOARD_HOST', '0.0.0.0'),
    'port': int(os.getenv('DASHBOARD_PORT', '8050')),
    'debug': os.getenv('DASHBOARD_DEBUG', 'false').lower() == 'true',
    'refresh_interval': int(os.getenv('DASHBOARD_REFRESH_INTERVAL', '30000')),  # 30초
    'max_data_points': int(os.getenv('DASHBOARD_MAX_DATA_POINTS', '1000')),
    'theme': {
        'primary_color': '#2c3e50',
        'secondary_color': '#3498db',
        'success_color': '#27ae60',
        'warning_color': '#f39c12',
        'error_color': '#e74c3c',
        'background_color': '#f8f9fa'
    }
}

# 데이터베이스 설정 (향후 확장용)
DATABASE_CONFIG = {
    'type': os.getenv('DATABASE_TYPE', 'sqlite'),  # sqlite, postgresql, mysql
    'host': os.getenv('DATABASE_HOST', 'localhost'),
    'port': int(os.getenv('DATABASE_PORT', '5432')),
    'name': os.getenv('DATABASE_NAME', 'auto_finance'),
    'username': os.getenv('DATABASE_USERNAME'),
    'password': os.getenv('DATABASE_PASSWORD'),
    'sqlite_path': os.path.join(DATA_DIR, 'auto_finance.db')
}

# 보안 설정
SECURITY_CONFIG = {
    'encryption_key': os.getenv('ENCRYPTION_KEY'),
    'jwt_secret': os.getenv('JWT_SECRET'),
    'api_rate_limit': int(os.getenv('API_RATE_LIMIT', '100')),  # 분당
    'session_timeout': int(os.getenv('SESSION_TIMEOUT', '3600')),  # 1시간
    'allowed_hosts': os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
}

# 성능 설정
PERFORMANCE_CONFIG = {
    'max_concurrent_tasks': int(os.getenv('MAX_CONCURRENT_TASKS', '10')),
    'task_timeout': int(os.getenv('TASK_TIMEOUT', '300')),  # 5분
    'memory_limit': int(os.getenv('MEMORY_LIMIT', '1024')),  # MB
    'cache_size': int(os.getenv('CACHE_SIZE', '100')),  # MB
    'log_retention_days': int(os.getenv('LOG_RETENTION_DAYS', '30')),
    'backup_retention_days': int(os.getenv('BACKUP_RETENTION_DAYS', '7'))
}

# 모니터링 설정
MONITORING_CONFIG = {
    'enabled': os.getenv('MONITORING_ENABLED', 'true').lower() == 'true',
    'metrics_interval': int(os.getenv('METRICS_INTERVAL', '60')),  # 1분
    'health_check_interval': int(os.getenv('HEALTH_CHECK_INTERVAL', '300')),  # 5분
    'alert_thresholds': {
        'cpu_usage': float(os.getenv('CPU_ALERT_THRESHOLD', '80.0')),
        'memory_usage': float(os.getenv('MEMORY_ALERT_THRESHOLD', '80.0')),
        'disk_usage': float(os.getenv('DISK_ALERT_THRESHOLD', '90.0')),
        'error_rate': float(os.getenv('ERROR_ALERT_THRESHOLD', '10.0'))
    }
}

# 백업 설정
BACKUP_CONFIG = {
    'enabled': os.getenv('BACKUP_ENABLED', 'true').lower() == 'true',
    'schedule': os.getenv('BACKUP_SCHEDULE', '0 2 * * *'),  # 매일 새벽 2시
    'backup_dir': os.path.join(DATA_DIR, 'backups'),
    'include_files': ['*.json', '*.db', '*.log'],
    'exclude_files': ['*.tmp', '*.cache'],
    'compression': os.getenv('BACKUP_COMPRESSION', 'true').lower() == 'true',
    'encryption': os.getenv('BACKUP_ENCRYPTION', 'false').lower() == 'true'
}

# 개발/테스트 설정
DEVELOPMENT_CONFIG = {
    'debug_mode': os.getenv('DEBUG_MODE', 'false').lower() == 'true',
    'test_mode': os.getenv('TEST_MODE', 'false').lower() == 'true',
    'mock_apis': os.getenv('MOCK_APIS', 'false').lower() == 'true',
    'sample_data': os.getenv('SAMPLE_DATA', 'false').lower() == 'true',
    'verbose_logging': os.getenv('VERBOSE_LOGGING', 'false').lower() == 'true'
}

# 전체 설정 통합
SETTINGS = {
    'ai': AI_CONFIG,
    'news_sources': NEWS_SOURCES,
    'crawler': CRAWLER_CONFIG,
    'fact_check': FACT_CHECK_CONFIG,
    'financial': FINANCIAL_CONFIG,
    'content': CONTENT_CONFIG,
    'upload': UPLOAD_CONFIG,
    'notification': NOTIFICATION_CONFIG,
    'dashboard': DASHBOARD_CONFIG,
    'database': DATABASE_CONFIG,
    'security': SECURITY_CONFIG,
    'performance': PERFORMANCE_CONFIG,
    'monitoring': MONITORING_CONFIG,
    'backup': BACKUP_CONFIG,
    'development': DEVELOPMENT_CONFIG
}

def get_setting(key: str, default: Any = None) -> Any:
    """설정값 조회"""
    keys = key.split('.')
    value = SETTINGS
    
    try:
        for k in keys:
            value = value[k]
        return value
    except (KeyError, TypeError):
        return default

def validate_settings() -> List[str]:
    """설정 유효성 검증"""
    errors = []
    
    # 필수 설정 검증
    if not AI_CONFIG.get('api_key'):
        errors.append("AI API 키가 설정되지 않았습니다")
    
    if not NEWS_SOURCES:
        errors.append("뉴스 소스가 설정되지 않았습니다")
    
    # 디렉토리 생성
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, 'cache'), exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, 'generated'), exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, 'backups'), exist_ok=True)
    
    return errors

# 설정 유효성 검증 실행
SETTING_ERRORS = validate_settings()
if SETTING_ERRORS:
    print("⚠️ 설정 오류:")
    for error in SETTING_ERRORS:
        print(f"  - {error}")
else:
    print("✅ 설정 검증 완료") 