"""
🚀 Auto Finance 고도화된 메인 실행 파일
AI 앙상블, 감정 분석, 고급 콘텐츠 생성을 통합한 전문가 수준 시스템
"""

import asyncio
import json
import time
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd

# 핵심 모듈 임포트
from auto_finance.core.news_crawler import NewsCrawler
from auto_finance.core.fact_checker import FactChecker
from auto_finance.core.financial_data import FinancialDataCollector
from auto_finance.core.ai_ensemble import ai_ensemble
from auto_finance.core.market_sentiment_analyzer import sentiment_analyzer
from auto_finance.core.advanced_content_generator import advanced_content_generator, ContentRequest
from auto_finance.core.upload_manager import UploadManager, UploadRequest
from auto_finance.core.notification_system import NotificationSystem, NotificationMessage

# 유틸리티 임포트
from auto_finance.utils.logger import setup_logger
from auto_finance.utils.error_handler import ErrorHandler
from auto_finance.utils.cache_manager import cache_manager
from auto_finance.utils.data_processor import data_processor
from auto_finance.utils.file_manager import file_manager

# 설정 임포트
from auto_finance.config.settings import (
    NEWS_SOURCES, AI_CONFIG, FINANCIAL_CONFIG, 
    CONTENT_CONFIG, UPLOAD_CONFIG, NOTIFICATION_CONFIG
)

logger = setup_logger(__name__)

class AdvancedAutoFinanceSystem:
    """고도화된 Auto Finance 자동화 시스템"""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        
        # 시스템 상태
        self.is_running = False
        self.start_time = None
        self.last_execution = None
        
        # 실행 통계
        self.execution_stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'total_processing_time': 0.0,
            'last_execution': None,
            'components': {},
            'ai_ensemble_stats': {},
            'sentiment_stats': {},
            'content_stats': {}
        }
        
        # 데이터 저장소
        self.crawled_articles = []
        self.fact_check_results = []
        self.sentiment_results = []
        self.generated_contents = []
        self.upload_results = []
        self.market_data = {}
        
        # 성능 모니터링
        self.performance_metrics = {
            'api_calls': 0,
            'total_cost': 0.0,
            'cache_hits': 0,
            'cache_misses': 0,
            'error_rate': 0.0
        }
        
        logger.info("🚀 고도화된 Auto Finance 시스템 초기화 완료")
    
    async def run_advanced_pipeline(self) -> Dict[str, Any]:
        """고도화된 전체 파이프라인 실행"""
        start_time = datetime.now()
        self.is_running = True
        self.start_time = start_time
        
        logger.info("🎯 고도화된 전체 파이프라인 실행 시작")
        
        try:
            # 1단계: 뉴스 크롤링
            logger.info("📰 1단계: 뉴스 크롤링 시작")
            articles = await self._run_advanced_crawler()
            self.crawled_articles = articles
            
            # 2단계: AI 앙상블 팩트 체크
            logger.info("🔍 2단계: AI 앙상블 팩트 체크 시작")
            fact_check_results = await self._run_advanced_fact_checker(articles)
            self.fact_check_results = fact_check_results
            
            # 3단계: 시장 감정 분석
            logger.info("📊 3단계: 시장 감정 분석 시작")
            sentiment_results = await self._run_sentiment_analyzer(articles)
            self.sentiment_results = sentiment_results
            
            # 4단계: 금융 데이터 수집
            logger.info("📈 4단계: 금융 데이터 수집 시작")
            financial_data = await self._run_financial_collector()
            self.market_data = financial_data
            
            # 5단계: 고급 콘텐츠 생성
            logger.info("✍️ 5단계: 고급 콘텐츠 생성 시작")
            contents = await self._run_advanced_content_generator(
                articles, fact_check_results, sentiment_results, financial_data
            )
            self.generated_contents = contents
            
            # 6단계: 업로드
            logger.info("📤 6단계: 업로드 시작")
            upload_results = await self._run_upload_manager(contents)
            self.upload_results = upload_results
            
            # 7단계: 고급 알림 전송
            logger.info("🔔 7단계: 고급 알림 전송 시작")
            notification_results = await self._run_advanced_notification_system()
            
            # 8단계: 성능 분석 및 최적화
            logger.info("⚡ 8단계: 성능 분석 및 최적화")
            await self._run_performance_analysis()
            
            # 통계 업데이트
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_execution_stats(True, processing_time)
            
            # 결과 요약
            summary = self._generate_advanced_execution_summary(
                articles, fact_check_results, sentiment_results, 
                contents, upload_results, processing_time
            )
            
            logger.info(f"✅ 고도화된 전체 파이프라인 완료: {processing_time:.2f}초")
            return summary
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_execution_stats(False, processing_time)
            self.error_handler.handle_error(e, "고도화된 전체 파이프라인 실행 실패")
            logger.error(f"❌ 고도화된 전체 파이프라인 실행 실패: {e}")
            raise
        
        finally:
            self.is_running = False
            self.last_execution = datetime.now()
    
    async def _run_advanced_crawler(self) -> List[Dict[str, Any]]:
        """고도화된 뉴스 크롤러 실행"""
        try:
            async with NewsCrawler() as crawler:
                articles = await crawler.crawl_all_sources()
                
                # 중복 제거 및 품질 필터링
                filtered_articles = self._filter_articles_by_quality(articles)
                
                # 통계 저장
                crawler.save_statistics()
                
                # 컴포넌트 통계 업데이트
                self.execution_stats['components']['crawler'] = {
                    'articles_collected': len(articles),
                    'articles_filtered': len(filtered_articles),
                    'processing_time': crawler.stats.get('processing_time', 0),
                    'success_rate': len(articles) / len(NEWS_SOURCES) * 100 if NEWS_SOURCES else 0
                }
                
                logger.info(f"✅ 고도화된 크롤링 완료: {len(filtered_articles)}개 기사 (필터링됨)")
                return filtered_articles
                
        except Exception as e:
            logger.error(f"❌ 고도화된 크롤러 실행 실패: {e}")
            return []
    
    def _filter_articles_by_quality(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """기사 품질 필터링"""
        filtered_articles = []
        
        for article in articles:
            # 기본 품질 체크
            title = article.get('title', '')
            content = article.get('content', '')
            
            # 제목 길이 체크
            if len(title) < 10 or len(title) > 200:
                continue
            
            # 내용 길이 체크
            if len(content) < 100:
                continue
            
            # 스팸 키워드 체크
            spam_keywords = ['광고', '홍보', '이벤트', '할인', '무료']
            if any(keyword in title.lower() for keyword in spam_keywords):
                continue
            
            # 중복 체크 (제목 기반)
            if not any(existing['title'] == title for existing in filtered_articles):
                filtered_articles.append(article)
        
        return filtered_articles
    
    async def _run_advanced_fact_checker(self, articles: List[Dict[str, Any]]) -> List[Any]:
        """고도화된 팩트 체커 실행 (AI 앙상블 활용)"""
        try:
            if not articles:
                logger.warning("⚠️ 팩트 체크할 기사가 없습니다")
                return []
            
            # 상위 15개 기사만 팩트 체크 (AI 앙상블 활용)
            top_articles = articles[:15]
            
            async with FactChecker() as fact_checker:
                # AI 앙상블을 활용한 팩트 체크
                results = await fact_checker.check_multiple_articles(top_articles)
                
                # 결과 저장
                fact_checker.save_results(results)
                
                # 컴포넌트 통계 업데이트
                self.execution_stats['components']['fact_checker'] = {
                    'articles_checked': len(results),
                    'verified_count': len([r for r in results if r.verification_status == 'verified']),
                    'average_score': fact_checker.stats.get('average_score', 0),
                    'success_rate': len(results) / len(top_articles) * 100 if top_articles else 0
                }
                
                # AI 앙상블 통계 업데이트
                ai_stats = ai_ensemble.get_statistics()
                self.execution_stats['ai_ensemble_stats'] = ai_stats
                
                logger.info(f"✅ 고도화된 팩트 체크 완료: {len(results)}개 기사")
                return results
                
        except Exception as e:
            logger.error(f"❌ 고도화된 팩트 체커 실행 실패: {e}")
            return []
    
    async def _run_sentiment_analyzer(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """시장 감정 분석 실행"""
        try:
            if not articles:
                logger.warning("⚠️ 감정 분석할 기사가 없습니다")
                return {}
            
            # 뉴스 감정 분석
            news_sentiments = await sentiment_analyzer.analyze_news_sentiment(articles)
            
            # 전체 시장 감정 분석
            market_sentiment = await sentiment_analyzer.analyze_market_sentiment(news_sentiments)
            
            # 감정 분석 통계 업데이트
            sentiment_stats = sentiment_analyzer.get_statistics()
            self.execution_stats['sentiment_stats'] = sentiment_stats
            
            logger.info(f"✅ 시장 감정 분석 완료: {len(news_sentiments)}개 기사 분석")
            return {
                'news_sentiments': news_sentiments,
                'market_sentiment': market_sentiment,
                'statistics': sentiment_stats
            }
            
        except Exception as e:
            logger.error(f"❌ 시장 감정 분석 실행 실패: {e}")
            return {}
    
    async def _run_financial_collector(self) -> Dict[str, Any]:
        """금융 데이터 수집기 실행"""
        try:
            async with FinancialDataCollector() as collector:
                # 주식 데이터 수집
                stocks = await collector.collect_all_stock_data()
                
                # 지수 데이터 수집
                indices = await collector.collect_all_index_data()
                
                # 데이터 저장
                collector.save_data()
                
                # 컴포넌트 통계 업데이트
                self.execution_stats['components']['financial_collector'] = {
                    'stocks_collected': len(stocks),
                    'indices_collected': len(indices),
                    'processing_time': collector.stats.get('processing_time', 0)
                }
                
                logger.info(f"✅ 금융 데이터 수집 완료: {len(stocks)}개 종목, {len(indices)}개 지수")
                return {
                    'stocks': stocks,
                    'indices': indices
                }
                
        except Exception as e:
            logger.error(f"❌ 금융 데이터 수집기 실행 실패: {e}")
            return {}
    
    async def _run_advanced_content_generator(self, articles: List[Dict[str, Any]], 
                                            fact_check_results: List[Any],
                                            sentiment_results: Dict[str, Any],
                                            financial_data: Dict[str, Any]) -> List[Any]:
        """고급 콘텐츠 생성기 실행"""
        try:
            if not articles:
                logger.warning("⚠️ 콘텐츠 생성할 기사가 없습니다")
                return []
            
            # 고급 콘텐츠 생성 요청 생성
            content_request = ContentRequest(
                articles=articles,
                sentiment_data=sentiment_results.get('market_sentiment'),
                market_data=financial_data,
                target_audience="professional",
                content_type="analysis",
                tone="professional",
                length="medium",
                include_charts=True
            )
            
            # 고급 콘텐츠 생성
            contents = await advanced_content_generator.generate_advanced_content(content_request)
            
            # 콘텐츠 통계 업데이트
            content_stats = advanced_content_generator.get_statistics()
            self.execution_stats['content_stats'] = content_stats
            
            logger.info(f"✅ 고급 콘텐츠 생성 완료: {len(contents)}개 콘텐츠")
            return contents
            
        except Exception as e:
            logger.error(f"❌ 고급 콘텐츠 생성기 실행 실패: {e}")
            return []
    
    async def _run_upload_manager(self, contents: List[Any]) -> List[Any]:
        """업로드 관리자 실행"""
        try:
            if not contents:
                logger.warning("⚠️ 업로드할 콘텐츠가 없습니다")
                return []
            
            async with UploadManager() as upload_manager:
                requests = []
                
                for content in contents:
                    # 파일 경로 생성
                    safe_title = "".join(c for c in content.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    file_path = f"data/generated/{safe_title[:50]}.md"
                    
                    request = UploadRequest(
                        content_id=f"content_{hash(content.title)}",
                        title=content.title,
                        content=content.content,
                        file_path=file_path,
                        platform="tistory",
                        tags=content.keywords,
                        category="주식뉴스",
                        metadata={
                            'sentiment_score': content.sentiment_score,
                            'market_impact': content.market_impact,
                            'seo_score': content.seo_score,
                            'readability_score': content.readability_score
                        }
                    )
                    requests.append(request)
                
                results = await upload_manager.upload_multiple_contents(requests)
                
                # 결과 저장
                upload_manager.save_results(results)
                
                # 컴포넌트 통계 업데이트
                self.execution_stats['components']['upload_manager'] = {
                    'uploads_attempted': len(results),
                    'successful_uploads': len([r for r in results if r.success]),
                    'success_rate': len([r for r in results if r.success]) / len(results) * 100 if results else 0
                }
                
                logger.info(f"✅ 업로드 완료: {len([r for r in results if r.success])}개 성공")
                return results
                
        except Exception as e:
            logger.error(f"❌ 업로드 관리자 실행 실패: {e}")
            return []
    
    async def _run_advanced_notification_system(self) -> List[Any]:
        """고급 알림 시스템 실행"""
        try:
            async with NotificationSystem() as notification_system:
                # 고급 실행 완료 알림
                message = NotificationMessage(
                    title="🚀 Auto Finance 고도화 파이프라인 완료",
                    content=self._create_advanced_notification_content(),
                    priority="high",
                    category="system",
                    channels=["slack", "email"],
                    recipients=["#general", "admin@example.com"],
                    metadata={
                        'execution_id': f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        'components_processed': len(self.execution_stats['components']),
                        'total_articles': len(self.crawled_articles),
                        'ai_ensemble_used': True,
                        'sentiment_analysis': True
                    },
                    created_at=datetime.now().isoformat()
                )
                
                results = await notification_system.send_notification(message)
                
                # 컴포넌트 통계 업데이트
                self.execution_stats['components']['notification_system'] = {
                    'notifications_sent': len(results),
                    'successful_notifications': len([r for r in results if r.success]),
                    'success_rate': len([r for r in results if r.success]) / len(results) * 100 if results else 0
                }
                
                logger.info(f"✅ 고급 알림 전송 완료: {len([r for r in results if r.success])}개 성공")
                return results
                
        except Exception as e:
            logger.error(f"❌ 고급 알림 시스템 실행 실패: {e}")
            return []
    
    def _create_advanced_notification_content(self) -> str:
        """고급 알림 콘텐츠 생성"""
        content = f"""
🎯 Auto Finance 고도화 파이프라인 완료!

📊 실행 결과:
• 수집된 기사: {len(self.crawled_articles)}개
• 팩트 체크: {len(self.fact_check_results)}개
• 감정 분석: {len(self.sentiment_results.get('news_sentiments', []))}개
• 생성된 콘텐츠: {len(self.generated_contents)}개
• 업로드 성공: {len([r for r in self.upload_results if r.success])}개

🤖 AI 앙상블 활용:
• 모델 사용: {len(ai_ensemble.models)}개
• 평균 신뢰도: {ai_ensemble.get_statistics().get('success_rate', 0):.1f}%

📈 시장 감정:
• 전체 감정: {self.sentiment_results.get('market_sentiment', {}).get('overall_sentiment', 0):.3f}
• 감정 트렌드: {self.sentiment_results.get('market_sentiment', {}).get('sentiment_trend', 'neutral')}

⚡ 성능 지표:
• 처리 시간: {self.execution_stats.get('total_processing_time', 0):.2f}초
• 성공률: {self.execution_stats.get('successful_executions', 0)}/{self.execution_stats.get('total_executions', 1)} ({(self.execution_stats.get('successful_executions', 0) / max(self.execution_stats.get('total_executions', 1), 1) * 100):.1f}%)
        """
        return content
    
    async def _run_performance_analysis(self):
        """성능 분석 및 최적화"""
        try:
            # 캐시 성능 분석
            cache_stats = cache_manager.get_statistics()
            self.performance_metrics['cache_hits'] = cache_stats.get('hits', 0)
            self.performance_metrics['cache_misses'] = cache_stats.get('misses', 0)
            
            # API 호출 분석
            self.performance_metrics['api_calls'] = (
                self.execution_stats.get('ai_ensemble_stats', {}).get('total_requests', 0) +
                self.execution_stats.get('sentiment_stats', {}).get('total_analyses', 0)
            )
            
            # 비용 분석
            self.performance_metrics['total_cost'] = (
                self.execution_stats.get('ai_ensemble_stats', {}).get('total_cost', 0.0)
            )
            
            # 오류율 계산
            total_operations = (
                self.execution_stats.get('ai_ensemble_stats', {}).get('total_requests', 0) +
                self.execution_stats.get('sentiment_stats', {}).get('total_analyses', 0) +
                self.execution_stats.get('content_stats', {}).get('total_generations', 0)
            )
            
            failed_operations = (
                self.execution_stats.get('ai_ensemble_stats', {}).get('failed_requests', 0) +
                self.execution_stats.get('sentiment_stats', {}).get('failed_analyses', 0) +
                self.execution_stats.get('content_stats', {}).get('failed_generations', 0)
            )
            
            self.performance_metrics['error_rate'] = (
                failed_operations / total_operations * 100 if total_operations > 0 else 0
            )
            
            logger.info("✅ 성능 분석 완료")
            
        except Exception as e:
            logger.error(f"❌ 성능 분석 실패: {e}")
    
    def _update_execution_stats(self, success: bool, processing_time: float):
        """실행 통계 업데이트"""
        self.execution_stats['total_executions'] += 1
        self.execution_stats['total_processing_time'] += processing_time
        
        if success:
            self.execution_stats['successful_executions'] += 1
        else:
            self.execution_stats['failed_executions'] += 1
        
        self.execution_stats['last_execution'] = datetime.now().isoformat()
    
    def _generate_advanced_execution_summary(self, articles: List[Dict[str, Any]], 
                                           fact_check_results: List[Any],
                                           sentiment_results: Dict[str, Any],
                                           contents: List[Any],
                                           upload_results: List[Any],
                                           processing_time: float) -> Dict[str, Any]:
        """고급 실행 결과 요약 생성"""
        summary = {
            'execution_id': f"advanced_exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'timestamp': datetime.now().isoformat(),
            'processing_time': processing_time,
            'components': {
                'crawler': {
                    'articles_collected': len(articles),
                    'sources_processed': len(NEWS_SOURCES),
                    'filtered_articles': len(articles)
                },
                'fact_checker': {
                    'articles_checked': len(fact_check_results),
                    'verified_count': len([r for r in fact_check_results if r.verification_status == 'verified']),
                    'ai_ensemble_used': True
                },
                'sentiment_analyzer': {
                    'articles_analyzed': len(sentiment_results.get('news_sentiments', [])),
                    'market_sentiment': sentiment_results.get('market_sentiment', {}).get('overall_sentiment', 0),
                    'sentiment_trend': sentiment_results.get('market_sentiment', {}).get('sentiment_trend', 'neutral')
                },
                'content_generator': {
                    'contents_generated': len(contents),
                    'total_words': sum(c.word_count for c in contents) if contents else 0,
                    'average_seo_score': sum(c.seo_score for c in contents) / len(contents) if contents else 0
                },
                'upload_manager': {
                    'uploads_attempted': len(upload_results),
                    'successful_uploads': len([r for r in upload_results if r.success])
                }
            },
            'ai_ensemble_stats': self.execution_stats.get('ai_ensemble_stats', {}),
            'sentiment_stats': self.execution_stats.get('sentiment_stats', {}),
            'content_stats': self.execution_stats.get('content_stats', {}),
            'performance_metrics': self.performance_metrics,
            'overall_stats': self.execution_stats,
            'error_summary': self.error_handler.get_statistics()
        }
        
        return summary
    
    def save_execution_summary(self, summary: Dict[str, Any], 
                             file_path: str = "data/advanced_execution_summary.json"):
        """고급 실행 요약 저장"""
        try:
            # 기존 요약 로드
            summaries = []
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    summaries = json.load(f)
            
            # 새 요약 추가
            summaries.append(summary)
            
            # 최근 100개만 유지
            if len(summaries) > 100:
                summaries = summaries[-100:]
            
            # 저장
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(summaries, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"💾 고급 실행 요약 저장: {file_path}")
            
        except Exception as e:
            logger.error(f"❌ 고급 실행 요약 저장 실패: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 반환"""
        return {
            'is_running': self.is_running,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'last_execution': self.last_execution.isoformat() if self.last_execution else None,
            'execution_stats': self.execution_stats,
            'performance_metrics': self.performance_metrics,
            'error_statistics': self.error_handler.get_statistics(),
            'cache_statistics': cache_manager.get_statistics(),
            'ai_ensemble_status': ai_ensemble.get_statistics(),
            'sentiment_analyzer_status': sentiment_analyzer.get_statistics(),
            'content_generator_status': advanced_content_generator.get_statistics(),
            'timestamp': datetime.now().isoformat()
        }
    
    async def run_scheduled_execution(self, interval_hours: int = 6):
        """스케줄된 실행"""
        logger.info(f"⏰ 스케줄된 실행 시작: {interval_hours}시간 간격")
        
        while True:
            try:
                await self.run_advanced_pipeline()
                logger.info(f"✅ 스케줄된 실행 완료. 다음 실행까지 {interval_hours}시간 대기")
                await asyncio.sleep(interval_hours * 3600)  # 시간을 초로 변환
                
            except Exception as e:
                logger.error(f"❌ 스케줄된 실행 실패: {e}")
                await asyncio.sleep(300)  # 5분 후 재시도

async def main():
    """메인 실행 함수"""
    logger.info("🚀 고도화된 Auto Finance 시스템 시작")
    
    # 시스템 인스턴스 생성
    system = AdvancedAutoFinanceSystem()
    
    try:
        # 고도화된 전체 파이프라인 실행
        summary = await system.run_advanced_pipeline()
        
        # 실행 요약 저장
        system.save_execution_summary(summary)
        
        # 결과 출력
        print("\n" + "="*80)
        print("🎉 고도화된 Auto Finance 파이프라인 완료!")
        print("="*80)
        print(f"📰 수집된 기사: {summary['components']['crawler']['articles_collected']}개")
        print(f"🔍 AI 앙상블 팩트 체크: {summary['components']['fact_checker']['articles_checked']}개")
        print(f"📊 감정 분석: {summary['components']['sentiment_analyzer']['articles_analyzed']}개")
        print(f"✍️ 고급 콘텐츠 생성: {summary['components']['content_generator']['contents_generated']}개")
        print(f"📤 업로드 성공: {summary['components']['upload_manager']['successful_uploads']}개")
        print(f"⏱️ 처리 시간: {summary['processing_time']:.2f}초")
        print(f"🤖 AI 앙상블 성공률: {summary['ai_ensemble_stats'].get('success_rate', 0):.1f}%")
        print(f"📈 시장 감정: {summary['components']['sentiment_analyzer']['market_sentiment']:.3f}")
        print(f"💰 총 비용: ${summary['performance_metrics']['total_cost']:.4f}")
        print("="*80)
        
        # 시스템 상태 출력
        status = system.get_system_status()
        print(f"📊 시스템 상태: {status['execution_stats']['successful_executions']}/{status['execution_stats']['total_executions']} 성공")
        print(f"⚡ 성능 지표: 캐시 히트율 {status['performance_metrics']['cache_hits']/(status['performance_metrics']['cache_hits']+status['performance_metrics']['cache_misses'])*100:.1f}%, 오류율 {status['performance_metrics']['error_rate']:.1f}%")
        
    except Exception as e:
        logger.error(f"❌ 시스템 실행 실패: {e}")
        print(f"\n❌ 시스템 실행 중 오류 발생: {e}")
    
    finally:
        logger.info("🏁 고도화된 Auto Finance 시스템 종료")

if __name__ == "__main__":
    # 비동기 실행
    asyncio.run(main()) 