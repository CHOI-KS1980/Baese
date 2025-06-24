"""
📈 주식 뉴스 자동화 시스템 - 인증 정보 설정
보안을 위한 환경 변수 및 API 키 관리
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Credentials:
    """인증 정보 관리 클래스"""
    
    # 🤖 AI 서비스 API 키
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")  # Gemini API 키
    AI_MODEL = os.getenv("AI_MODEL", "openai")  # 사용할 AI 모델
    
    # 📱 티스토리 API 설정
    TISTORY_ACCESS_TOKEN = os.getenv("TISTORY_ACCESS_TOKEN", "")
    TISTORY_BLOG_NAME = os.getenv("TISTORY_BLOG_NAME", "")
    TISTORY_CATEGORY_ID = os.getenv("TISTORY_CATEGORY_ID", "")
    
    # 🗄️ 데이터베이스 설정
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/stock_news")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # 🔍 검색 API 키
    GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY", "")
    SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
    
    # 📊 금융 데이터 API
    ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    YAHOO_FINANCE_API_KEY = os.getenv("YAHOO_FINANCE_API_KEY", "")
    
    # 📈 트렌드 분석 API
    GOOGLE_TRENDS_API_KEY = os.getenv("GOOGLE_TRENDS_API_KEY", "")
    NAVER_TRENDS_API_KEY = os.getenv("NAVER_TRENDS_API_KEY", "")
    
    # 🔐 보안 설정
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    JWT_SECRET = os.getenv("JWT_SECRET", "your-jwt-secret-here")
    
    # 📧 알림 설정
    EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
    EMAIL_USER = os.getenv("EMAIL_USER", "")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
    
    # 📱 카카오톡 설정 (기존 시스템 연동)
    KAKAO_ACCESS_TOKEN = os.getenv("KAKAO_ACCESS_TOKEN", "")
    KAKAO_REFRESH_TOKEN = os.getenv("KAKAO_REFRESH_TOKEN", "")
    
    # 알림 시스템 API 키
    SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN', '')
    SLACK_CHANNEL_ID = os.getenv('SLACK_CHANNEL_ID', '')
    
    # 한국은행 API 키 (선택사항)
    BOK_API_KEY = os.getenv('BOK_API_KEY', '')
    
    # 기타 API 키
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
    FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY', '')
    
    def __init__(self):
        # AI 서비스 API 키
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
        self.GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
        
        # 티스토리 API 키
        self.TISTORY_ACCESS_TOKEN = os.getenv('TISTORY_ACCESS_TOKEN', '')
        self.TISTORY_BLOG_NAME = os.getenv('TISTORY_BLOG_NAME', '')
        
        # 알림 시스템 API 키
        self.SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN', '')
        self.SLACK_CHANNEL_ID = os.getenv('SLACK_CHANNEL_ID', '')
        self.KAKAO_ACCESS_TOKEN = os.getenv('KAKAO_ACCESS_TOKEN', '')
        
        # 이메일 설정
        self.EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
        self.EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
        self.EMAIL_USER = os.getenv('EMAIL_USER', '')
        self.EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
        self.EMAIL_RECIPIENT = os.getenv('EMAIL_RECIPIENT', '')
        
        # 금융 데이터 API 키
        self.ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')
        self.YAHOO_FINANCE_API_KEY = os.getenv('YAHOO_FINANCE_API_KEY', '')
        
        # 한국은행 API 키 (선택사항)
        self.BOK_API_KEY = os.getenv('BOK_API_KEY', '')
        
        # 기타 API 키
        self.NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
        self.FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY', '')
    
    def validate_required_credentials(self) -> Dict[str, Any]:
        """필수 인증 정보 검증"""
        missing_credentials = []
        available_services = []
        
        # AI 서비스 검증
        if self.OPENAI_API_KEY:
            available_services.append('OpenAI')
        elif self.GOOGLE_API_KEY:
            available_services.append('Google Gemini')
        else:
            missing_credentials.append('AI API Key (OpenAI 또는 Google)')
        
        # 티스토리 API 검증 (선택사항)
        if self.TISTORY_ACCESS_TOKEN and self.TISTORY_BLOG_NAME:
            available_services.append('Tistory')
        else:
            missing_credentials.append('Tistory API (선택사항)')
        
        # 알림 시스템 검증 (선택사항)
        if self.SLACK_BOT_TOKEN and self.SLACK_CHANNEL_ID:
            available_services.append('Slack')
        elif self.KAKAO_ACCESS_TOKEN:
            available_services.append('KakaoTalk')
        else:
            missing_credentials.append('Notification API (선택사항)')
        
        # 금융 데이터 API 검증 (선택사항)
        if self.ALPHA_VANTAGE_API_KEY:
            available_services.append('Alpha Vantage')
        if self.YAHOO_FINANCE_API_KEY:
            available_services.append('Yahoo Finance')
        
        # 이메일 설정 검증 (선택사항)
        if self.EMAIL_USER and self.EMAIL_PASSWORD:
            available_services.append('Email')
        
        return {
            "valid": len(missing_credentials) == 0,
            "missing": missing_credentials,
            "available_services": available_services,
            "has_ai_service": bool(self.OPENAI_API_KEY or self.GOOGLE_API_KEY),
            "has_upload_service": bool(self.TISTORY_ACCESS_TOKEN),
            "has_notification_service": bool(self.SLACK_BOT_TOKEN or self.KAKAO_ACCESS_TOKEN),
            "has_financial_data": bool(self.ALPHA_VANTAGE_API_KEY or self.YAHOO_FINANCE_API_KEY),
            "has_email_service": bool(self.EMAIL_USER and self.EMAIL_PASSWORD)
        }
    
    def get_ai_service_info(self) -> Dict[str, Any]:
        """AI 서비스 정보 반환"""
        if self.OPENAI_API_KEY:
            return {
                "service": "OpenAI",
                "model": "gpt-4",
                "available": True
            }
        elif self.GOOGLE_API_KEY:
            return {
                "service": "Google Gemini",
                "model": "gemini-2.0-flash-exp",
                "available": True
            }
        else:
            return {
                "service": "None",
                "model": "None",
                "available": False
            }
    
    def get_financial_data_services(self) -> Dict[str, bool]:
        """금융 데이터 서비스 정보 반환"""
        return {
            "alpha_vantage": bool(self.ALPHA_VANTAGE_API_KEY),
            "yahoo_finance": bool(self.YAHOO_FINANCE_API_KEY),
            "bank_of_korea": bool(self.BOK_API_KEY),
            "finnhub": bool(self.FINNHUB_API_KEY)
        }
    
    def get_notification_services(self) -> Dict[str, bool]:
        """알림 서비스 정보 반환"""
        return {
            "slack": bool(self.SLACK_BOT_TOKEN and self.SLACK_CHANNEL_ID),
            "kakao": bool(self.KAKAO_ACCESS_TOKEN),
            "email": bool(self.EMAIL_USER and self.EMAIL_PASSWORD)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """인증 정보를 딕셔너리로 반환 (민감한 정보는 마스킹)"""
        return {
            "openai_api_key": self._mask_api_key(self.OPENAI_API_KEY),
            "google_api_key": self._mask_api_key(self.GOOGLE_API_KEY),
            "tistory_access_token": self._mask_api_key(self.TISTORY_ACCESS_TOKEN),
            "tistory_blog_name": self.TISTORY_BLOG_NAME,
            "slack_bot_token": self._mask_api_key(self.SLACK_BOT_TOKEN),
            "slack_channel_id": self.SLACK_CHANNEL_ID,
            "kakao_access_token": self._mask_api_key(self.KAKAO_ACCESS_TOKEN),
            "email_host": self.EMAIL_HOST,
            "email_port": self.EMAIL_PORT,
            "email_user": self.EMAIL_USER,
            "alpha_vantage_api_key": self._mask_api_key(self.ALPHA_VANTAGE_API_KEY),
            "yahoo_finance_api_key": self._mask_api_key(self.YAHOO_FINANCE_API_KEY),
            "bok_api_key": self._mask_api_key(self.BOK_API_KEY),
            "news_api_key": self._mask_api_key(self.NEWS_API_KEY),
            "finnhub_api_key": self._mask_api_key(self.FINNHUB_API_KEY)
        }
    
    def _mask_api_key(self, api_key: str) -> str:
        """API 키 마스킹"""
        if not api_key:
            return ""
        if len(api_key) <= 8:
            return "*" * len(api_key)
        return api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]

# 전역 인증 정보 인스턴스
credentials = Credentials() 