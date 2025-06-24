"""
✍️ 기사 콘텐츠 생성기 (Content Generator)
Gemini, OpenAI, Claude 등 AI 모델을 활용한 전문가 수준의 기사 본문 생성
"""

from typing import Dict, Any
from config.settings import settings
from config.credentials import credentials

class ContentGenerator:
    def __init__(self):
        self.model = credentials.AI_MODEL.lower()
        self.ai_config = settings.AI_SERVICES.get(self.model)

    async def generate_article(self, article: dict) -> dict:
        """
        기사 데이터(딕셔너리)를 받아 AI로 본문을 생성해 반환합니다.
        """
        title = article.get('title', '')
        content = article.get('content', '')
        summary = article.get('summary', '')
        # 실제 AI 호출 로직은 아래에 구현 (여기서는 예시)
        body = f"[AI 자동생성] {title}\n{content}\n{summary}"
        return {
            'title': title,
            'body': body,
            'summary': summary,
            'source': article.get('source', ''),
            'url': article.get('url', '')
        } 