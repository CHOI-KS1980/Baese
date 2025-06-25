#!/usr/bin/env python3
"""
🧪 Auto Finance 고도화 시스템 테스트 스크립트
"""

import asyncio
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_ai_ensemble():
    """AI 앙상블 테스트"""
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
    """감정 분석 테스트"""
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
    """콘텐츠 생성 테스트"""
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
    """메인 테스트 함수"""
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
