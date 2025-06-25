"""
🚀 Auto Finance 메인 실행 파일
고도화된 주식 뉴스 자동화 시스템
"""

import asyncio
import json
import os
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# 핵심 모듈 임포트
from auto_finance.core.news_crawler import NewsCrawler
from auto_finance.core.fact_checker import FactChecker
from auto_finance.core.financial_data import FinancialDataCollector
from auto_finance.core.content_generator import ContentGenerator, ContentRequest
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

class AutoFinanceSystem:
    """Auto Finance 자동화 시스템"""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        
        # 시스템 상태
        self.is_running = False
        self.start_time = None
        
        # 실행 통계
        self.execution_stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'total_processing_time': 0.0,
            'last_execution': None,
            'components': {}
        }
        
        # 데이터 저장소
        self.crawled_articles = []
        self.fact_check_results = []
        self.generated_contents = []
        self.upload_results = []
        
        logger.info("🚀 Auto Finance 시스템 초기화 완료")
    
    async def run_full_pipeline(self) -> Dict[str, Any]:
        """전체 파이프라인 실행"""
        start_time = datetime.now()
        self.is_running = True
        
        logger.info("🎯 전체 파이프라인 실행 시작")
        
        try:
            # 1단계: 뉴스 크롤링
            logger.info("📰 1단계: 뉴스 크롤링 시작")
            articles = await self._run_crawler()
            self.crawled_articles = articles
            
            # 2단계: AI 팩트 체크
            logger.info("🔍 2단계: AI 팩트 체크 시작")
            fact_check_results = await self._run_fact_checker(articles)
            self.fact_check_results = fact_check_results
            
            # 3단계: 금융 데이터 수집
            logger.info("📈 3단계: 금융 데이터 수집 시작")
            financial_data = await self._run_financial_collector()
            
            # 4단계: 콘텐츠 생성
            logger.info("✍️ 4단계: 콘텐츠 생성 시작")
            contents = await self._run_content_generator(articles, fact_check_results)
            self.generated_contents = contents
            
            # 5단계: 업로드
            logger.info("📤 5단계: 업로드 시작")
            upload_results = await self._run_upload_manager(contents)
            self.upload_results = upload_results
            
            # 6단계: 알림 전송
            logger.info("🔔 6단계: 알림 전송 시작")
            notification_results = await self._run_notification_system()
            
            # 통계 업데이트
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_execution_stats(True, processing_time)
            
            # 결과 요약
            summary = self._generate_execution_summary(
                articles, fact_check_results, contents, upload_results, processing_time
            )
            
            logger.info(f"✅ 전체 파이프라인 완료: {processing_time:.2f}초")
            return summary
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_execution_stats(False, processing_time)
            self.error_handler.handle_error(e, "전체 파이프라인 실행 실패")
            logger.error(f"❌ 전체 파이프라인 실행 실패: {e}")
            raise
        
        finally:
            self.is_running = False
    
    async def _run_crawler(self) -> List[Dict[str, Any]]:
        """뉴스 크롤러 실행"""
        try:
            async with NewsCrawler() as crawler:
                articles = await crawler.crawl_all_sources()
                
                # 통계 저장
                crawler.save_statistics()
                
                # 컴포넌트 통계 업데이트
                self.execution_stats['components']['crawler'] = {
                    'articles_collected': len(articles),
                    'processing_time': crawler.stats.get('processing_time', 0),
                    'success_rate': len(articles) / len(NEWS_SOURCES) * 100 if NEWS_SOURCES else 0
                }
                
                logger.info(f"✅ 크롤링 완료: {len(articles)}개 기사")
                return articles
                
        except Exception as e:
            logger.error(f"❌ 크롤러 실행 실패: {e}")
            return []
    
    async def _run_fact_checker(self, articles: List[Dict[str, Any]]) -> List[Any]:
        """팩트 체커 실행"""
        try:
            if not articles:
                logger.warning("⚠️ 팩트 체크할 기사가 없습니다")
                return []
            
            # 상위 10개 기사만 팩트 체크 (API 비용 절약)
            top_articles = articles[:10]
            
            async with FactChecker() as fact_checker:
                results = await fact_checker.check_multiple_articles(top_articles)
                
                # 결과 저장
                fact_checker.save_results(results)
                
                # 컴포넌트 통계 업데이트
                self.execution_stats['components']['fact_checker'] = {
                    'articles_checked': len(results),
                    'average_score': fact_checker.stats.get('average_score', 0),
                    'success_rate': len(results) / len(top_articles) * 100 if top_articles else 0
                }
                
                logger.info(f"✅ 팩트 체크 완료: {len(results)}개 기사")
                return results
                
        except Exception as e:
            logger.error(f"❌ 팩트 체커 실행 실패: {e}")
            return []
    
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
                return {'stocks': stocks, 'indices': indices}
                
        except Exception as e:
            logger.error(f"❌ 금융 데이터 수집기 실행 실패: {e}")
            return {}
    
    async def _run_content_generator(self, articles: List[Dict[str, Any]], 
                                   fact_check_results: List[Any]) -> List[Any]:
        """콘텐츠 생성기 실행"""
        try:
            if not articles:
                logger.warning("⚠️ 생성할 콘텐츠가 없습니다")
                return []
            
            # 상위 5개 기사로 콘텐츠 생성
            top_articles = articles[:5]
            
            async with ContentGenerator() as generator:
                requests = []
                
                for i, article in enumerate(top_articles):
                    request = ContentRequest(
                        title=article['title'],
                        content=article.get('content', article['title']),
                        keywords=article.get('keywords', []),
                        content_type="article",
                        target_length=800,
                        tone="professional"
                    )
                    requests.append(request)
                
                contents = await generator.generate_multiple_contents(requests)
                
                # 콘텐츠 저장
                for content in contents:
                    generator.save_content(content)
                
                # 컴포넌트 통계 업데이트
                self.execution_stats['components']['content_generator'] = {
                    'contents_generated': len(contents),
                    'total_words': sum(c.word_count for c in contents),
                    'average_seo_score': sum(c.seo_score for c in contents) / len(contents) if contents else 0
                }
                
                logger.info(f"✅ 콘텐츠 생성 완료: {len(contents)}개")
                return contents
                
        except Exception as e:
            logger.error(f"❌ 콘텐츠 생성기 실행 실패: {e}")
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
                    file_path = f"data/generated/{content.title.replace(' ', '_')[:50]}.md"
                    
                    request = UploadRequest(
                        content_id=f"content_{hash(content.title)}",
                        title=content.title,
                        content=content.content,
                        file_path=file_path,
                        platform="tistory",  # 기본 플랫폼
                        tags=content.keywords,
                        category="주식뉴스"
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
    
    async def _run_notification_system(self) -> List[Any]:
        """알림 시스템 실행"""
        try:
            async with NotificationSystem() as notification_system:
                # 실행 완료 알림
                message = NotificationMessage(
                    title="Auto Finance 파이프라인 완료",
                    content=f"전체 파이프라인이 성공적으로 완료되었습니다. 처리된 기사: {len(self.crawled_articles)}개",
                    priority="normal",
                    category="system",
                    channels=["slack"],
                    recipients=["#general"],
                    metadata={},
                    created_at=datetime.now().isoformat()
                )
                
                results = await notification_system.send_notification(message)
                
                # 컴포넌트 통계 업데이트
                self.execution_stats['components']['notification_system'] = {
                    'notifications_sent': len(results),
                    'successful_notifications': len([r for r in results if r.success]),
                    'success_rate': len([r for r in results if r.success]) / len(results) * 100 if results else 0
                }
                
                logger.info(f"✅ 알림 전송 완료: {len([r for r in results if r.success])}개 성공")
                return results
                
        except Exception as e:
            logger.error(f"❌ 알림 시스템 실행 실패: {e}")
            return []
    
    def _update_execution_stats(self, success: bool, processing_time: float):
        """실행 통계 업데이트"""
        self.execution_stats['total_executions'] += 1
        self.execution_stats['total_processing_time'] += processing_time
        
        if success:
            self.execution_stats['successful_executions'] += 1
        else:
            self.execution_stats['failed_executions'] += 1
        
        self.execution_stats['last_execution'] = datetime.now().isoformat()
    
    def _generate_execution_summary(self, articles: List[Dict[str, Any]], 
                                  fact_check_results: List[Any],
                                  contents: List[Any],
                                  upload_results: List[Any],
                                  processing_time: float) -> Dict[str, Any]:
        """실행 결과 요약 생성"""
        summary = {
            'execution_id': f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'timestamp': datetime.now().isoformat(),
            'processing_time': processing_time,
            'components': {
                'crawler': {
                    'articles_collected': len(articles),
                    'sources_processed': len(NEWS_SOURCES)
                },
                'fact_checker': {
                    'articles_checked': len(fact_check_results),
                    'verified_count': len([r for r in fact_check_results if r.verification_status == 'verified'])
                },
                'content_generator': {
                    'contents_generated': len(contents),
                    'total_words': sum(c.word_count for c in contents) if contents else 0
                },
                'upload_manager': {
                    'uploads_attempted': len(upload_results),
                    'successful_uploads': len([r for r in upload_results if r.success])
                }
            },
            'overall_stats': self.execution_stats,
            'error_summary': self.error_handler.get_statistics()
        }
        
        return summary
    
    def save_execution_summary(self, summary: Dict[str, Any], 
                             file_path: str = "data/execution_summary.json"):
        """실행 요약 저장"""
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
            
            logger.info(f"💾 실행 요약 저장: {file_path}")
            
        except Exception as e:
            logger.error(f"❌ 실행 요약 저장 실패: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 반환"""
        return {
            'is_running': self.is_running,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'execution_stats': self.execution_stats,
            'error_statistics': self.error_handler.get_statistics(),
            'cache_statistics': cache_manager.get_statistics(),
            'timestamp': datetime.now().isoformat()
        }

async def main():
    """메인 실행 함수"""
    logger.info("🚀 Auto Finance 시스템 시작")
    
    # 시스템 인스턴스 생성
    system = AutoFinanceSystem()
    
    try:
        # 전체 파이프라인 실행
        summary = await system.run_full_pipeline()
        
        # 실행 요약 저장
        system.save_execution_summary(summary)
        
        # 결과 출력
        print("\n" + "="*60)
        print("🎉 Auto Finance 파이프라인 완료!")
        print("="*60)
        print(f"📰 수집된 기사: {summary['components']['crawler']['articles_collected']}개")
        print(f"🔍 팩트 체크: {summary['components']['fact_checker']['articles_checked']}개")
        print(f"✍️ 생성된 콘텐츠: {summary['components']['content_generator']['contents_generated']}개")
        print(f"📤 업로드 성공: {summary['components']['upload_manager']['successful_uploads']}개")
        print(f"⏱️ 처리 시간: {summary['processing_time']:.2f}초")
        print("="*60)
        
        # 시스템 상태 출력
        status = system.get_system_status()
        print(f"📊 시스템 상태: {status['execution_stats']['successful_executions']}/{status['execution_stats']['total_executions']} 성공")
        
    except Exception as e:
        logger.error(f"❌ 시스템 실행 실패: {e}")
        print(f"\n❌ 시스템 실행 중 오류 발생: {e}")
    
    finally:
        logger.info("🏁 Auto Finance 시스템 종료")

if __name__ == "__main__":
    # 비동기 실행
    asyncio.run(main()) 