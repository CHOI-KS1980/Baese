"""
🧪 Auto Finance 고도화 시스템 빠른 테스트
"""

import asyncio
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_basic_imports():
    """기본 모듈 임포트 테스트"""
    print("🔍 기본 모듈 임포트 테스트...")
    
    try:
        # 핵심 모듈 임포트 테스트
        from auto_finance.core.news_crawler import NewsCrawler
        from auto_finance.core.fact_checker import FactChecker
        from auto_finance.core.financial_data import FinancialDataCollector
        from auto_finance.core.upload_manager import UploadManager
        from auto_finance.core.notification_system import NotificationSystem
        
        print("✅ 기본 모듈 임포트 성공")
        return True
        
    except ImportError as e:
        print(f"❌ 기본 모듈 임포트 실패: {e}")
        return False

async def test_advanced_modules():
    """고도화 모듈 임포트 테스트"""
    print("🔍 고도화 모듈 임포트 테스트...")
    
    try:
        # 고도화 모듈 임포트 테스트
        from auto_finance.core.ai_ensemble import ai_ensemble
        from auto_finance.core.market_sentiment_analyzer import sentiment_analyzer
        from auto_finance.core.advanced_content_generator import advanced_content_generator
        
        print("✅ 고도화 모듈 임포트 성공")
        return True
        
    except ImportError as e:
        print(f"❌ 고도화 모듈 임포트 실패: {e}")
        return False

async def test_ai_ensemble():
    """AI 앙상블 테스트"""
    print("🤖 AI 앙상블 테스트...")
    
    try:
        from auto_finance.core.ai_ensemble import ai_ensemble
        
        # 간단한 프롬프트로 테스트
        test_prompt = "주식 시장에 대한 간단한 분석을 한 문장으로 작성해주세요."
        
        result = await ai_ensemble.generate_content_ensemble(
            test_prompt, 
            task_type='content_generation'
        )
        
        print(f"✅ AI 앙상블 테스트 성공")
        print(f"생성된 콘텐츠: {result.final_content[:100]}...")
        print(f"신뢰도 점수: {result.confidence_score:.3f}")
        print(f"처리 시간: {result.processing_time:.2f}초")
        
        return True
        
    except Exception as e:
        print(f"❌ AI 앙상블 테스트 실패: {e}")
        return False

async def test_sentiment_analyzer():
    """감정 분석 테스트"""
    print("📊 감정 분석 테스트...")
    
    try:
        from auto_finance.core.market_sentiment_analyzer import sentiment_analyzer
        
        # 테스트 기사
        test_articles = [
            {
                'title': '삼성전자 실적 호조로 주가 상승',
                'content': '삼성전자가 예상보다 좋은 실적을 발표하여 주가가 상승했습니다. 시장 전문가들은 긍정적인 전망을 내놓고 있습니다.',
                'source': '테스트 소스'
            },
            {
                'title': '경제 불안으로 시장 하락',
                'content': '경제 불안 요소가 증가하면서 주식 시장이 하락했습니다. 투자자들의 우려가 커지고 있습니다.',
                'source': '테스트 소스'
            }
        ]
        
        # 뉴스 감정 분석
        news_sentiments = await sentiment_analyzer.analyze_news_sentiment(test_articles)
        
        # 전체 시장 감정 분석
        market_sentiment = await sentiment_analyzer.analyze_market_sentiment(news_sentiments)
        
        print(f"✅ 감정 분석 테스트 성공")
        print(f"분석된 기사 수: {len(news_sentiments)}개")
        print(f"전체 시장 감정: {market_sentiment.overall_sentiment:.3f}")
        print(f"감정 트렌드: {market_sentiment.sentiment_trend}")
        
        return True
        
    except Exception as e:
        print(f"❌ 감정 분석 테스트 실패: {e}")
        return False

async def test_content_generator():
    """고급 콘텐츠 생성 테스트"""
    print("✍️ 고급 콘텐츠 생성 테스트...")
    
    try:
        from auto_finance.core.advanced_content_generator import advanced_content_generator, ContentRequest
        
        # 테스트 기사
        test_articles = [
            {
                'title': '테스트 기사: 주식 시장 동향',
                'content': '최근 주식 시장에서 다양한 변화가 일어나고 있습니다. 투자자들은 신중한 접근이 필요합니다.',
                'source': '테스트 소스'
            }
        ]
        
        # 콘텐츠 생성 요청
        request = ContentRequest(
            articles=test_articles,
            target_audience="general",
            content_type="summary",
            tone="professional",
            length="short"
        )
        
        # 콘텐츠 생성
        contents = await advanced_content_generator.generate_advanced_content(request)
        
        print(f"✅ 고급 콘텐츠 생성 테스트 성공")
        print(f"생성된 콘텐츠 수: {len(contents)}개")
        
        if contents:
            content = contents[0]
            print(f"제목: {content.title}")
            print(f"단어 수: {content.word_count}개")
            print(f"SEO 점수: {content.seo_score:.1f}")
            print(f"가독성 점수: {content.readability_score:.1f}")
            print(f"감정 점수: {content.sentiment_score:.3f}")
            print(f"시장 영향도: {content.market_impact}")
        
        return True
        
    except Exception as e:
        print(f"❌ 고급 콘텐츠 생성 테스트 실패: {e}")
        return False

async def test_system_integration():
    """시스템 통합 테스트"""
    print("🔗 시스템 통합 테스트...")
    
    try:
        from auto_finance.main_advanced import AdvancedAutoFinanceSystem
        
        # 시스템 인스턴스 생성
        system = AdvancedAutoFinanceSystem()
        
        # 시스템 상태 확인
        status = system.get_system_status()
        
        print(f"✅ 시스템 통합 테스트 성공")
        print(f"시스템 실행 상태: {status.get('is_running', False)}")
        print(f"AI 앙상블 상태: {status.get('ai_ensemble_status', {}).get('total_requests', 0)} 요청")
        print(f"감정 분석 상태: {status.get('sentiment_analyzer_status', {}).get('total_analyses', 0)} 분석")
        print(f"콘텐츠 생성 상태: {status.get('content_generator_status', {}).get('total_generations', 0)} 생성")
        
        return True
        
    except Exception as e:
        print(f"❌ 시스템 통합 테스트 실패: {e}")
        return False

async def main():
    """메인 테스트 함수"""
    print("🧪 Auto Finance 고도화 시스템 빠른 테스트")
    print("="*60)
    
    test_results = []
    
    # 1. 기본 모듈 테스트
    result = await test_basic_imports()
    test_results.append(("기본 모듈", result))
    print()
    
    # 2. 고도화 모듈 테스트
    result = await test_advanced_modules()
    test_results.append(("고도화 모듈", result))
    print()
    
    # 3. AI 앙상블 테스트
    result = await test_ai_ensemble()
    test_results.append(("AI 앙상블", result))
    print()
    
    # 4. 감정 분석 테스트
    result = await test_sentiment_analyzer()
    test_results.append(("감정 분석", result))
    print()
    
    # 5. 고급 콘텐츠 생성 테스트
    result = await test_content_generator()
    test_results.append(("고급 콘텐츠 생성", result))
    print()
    
    # 6. 시스템 통합 테스트
    result = await test_system_integration()
    test_results.append(("시스템 통합", result))
    print()
    
    # 결과 요약
    print("="*60)
    print("📊 테스트 결과 요약")
    print("="*60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n전체 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 테스트가 성공했습니다!")
        print("\n🚀 다음 단계:")
        print("1. python main_advanced.py - 고도화된 시스템 실행")
        print("2. python start_dashboard.py - 대시보드 실행")
        print("3. 브라우저에서 http://localhost:8050 접속")
    else:
        print("⚠️ 일부 테스트가 실패했습니다.")
        print("API 키 설정과 의존성 설치를 확인해주세요.")
    
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main()) 