"""
🕷️ 고도화된 뉴스 크롤러
다중 소스 지원, 스마트 필터링, 중복 제거, 실시간 모니터링
"""

import asyncio
import aiohttp
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from auto_finance.utils.logger import setup_logger
from auto_finance.utils.error_handler import retry_on_error, ErrorHandler
from auto_finance.utils.cache_manager import cache_manager
from auto_finance.utils.data_processor import data_processor
from auto_finance.config.settings import NEWS_SOURCES, CRAWLER_CONFIG

logger = setup_logger(__name__)

class NewsCrawler:
    """고도화된 뉴스 크롤러"""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.session = None
        self.driver = None
        self.crawled_count = 0
        self.error_count = 0
        self.start_time = None
        
        # 크롤링 통계
        self.stats = {
            'total_articles': 0,
            'successful_crawls': 0,
            'failed_crawls': 0,
            'processing_time': 0,
            'sources_processed': 0
        }
    
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        await self.cleanup()
    
    async def initialize(self):
        """크롤러 초기화"""
        try:
            # aiohttp 세션 생성
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
            
            # Selenium 드라이버 설정 (필요시)
            if CRAWLER_CONFIG.get('use_selenium', False):
                await self._setup_selenium()
            
            self.start_time = datetime.now()
            logger.info("🕷️ 뉴스 크롤러 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ 크롤러 초기화 실패: {e}")
            raise
    
    async def cleanup(self):
        """크롤러 정리"""
        try:
            if self.session:
                await self.session.close()
            
            if self.driver:
                self.driver.quit()
            
            # 통계 계산
            if self.start_time:
                self.stats['processing_time'] = (datetime.now() - self.start_time).total_seconds()
            
            logger.info(f"🧹 크롤러 정리 완료 - 통계: {self.stats}")
            
        except Exception as e:
            logger.error(f"❌ 크롤러 정리 실패: {e}")
    
    async def _setup_selenium(self):
        """Selenium 드라이버 설정"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            
            logger.info("🔧 Selenium 드라이버 설정 완료")
            
        except Exception as e:
            logger.error(f"❌ Selenium 설정 실패: {e}")
            raise
    
    @retry_on_error(max_retries=3, delay=2.0)
    async def crawl_source(self, source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """단일 소스 크롤링"""
        source_name = source_config['name']
        source_url = source_config['url']
        
        logger.info(f"📰 {source_name} 크롤링 시작: {source_url}")
        
        try:
            # 캐시 확인
            cache_key = f"crawl_{source_name}_{datetime.now().strftime('%Y%m%d_%H')}"
            cached_data = cache_manager.get(cache_key)
            
            if cached_data and CRAWLER_CONFIG.get('use_cache', True):
                logger.info(f"💾 캐시된 데이터 사용: {source_name}")
                return cached_data
            
            # 크롤링 방식 선택
            if source_config.get('use_selenium', False):
                articles = await self._crawl_with_selenium(source_config)
            else:
                articles = await self._crawl_with_requests(source_config)
            
            # 데이터 정제 및 필터링
            articles = await self._process_articles(articles, source_config)
            
            # 캐시 저장
            if articles:
                cache_manager.set(cache_key, articles, ttl=1800)  # 30분
            
            self.stats['successful_crawls'] += 1
            self.stats['total_articles'] += len(articles)
            
            logger.info(f"✅ {source_name} 크롤링 완료: {len(articles)}개 기사")
            return articles
            
        except Exception as e:
            self.stats['failed_crawls'] += 1
            self.error_handler.handle_error(e, f"크롤링 실패 ({source_name})")
            logger.error(f"❌ {source_name} 크롤링 실패: {e}")
            return []
    
    async def _crawl_with_requests(self, source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """requests 기반 크롤링"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with self.session.get(source_config['url'], headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}")
                
                html = await response.text()
                
            return self._parse_html(html, source_config)
            
        except Exception as e:
            logger.error(f"❌ requests 크롤링 실패: {e}")
            raise
    
    async def _crawl_with_selenium(self, source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Selenium 기반 크롤링"""
        try:
            if not self.driver:
                raise Exception("Selenium 드라이버가 초기화되지 않았습니다")
            
            self.driver.get(source_config['url'])
            
            # 페이지 로딩 대기
            wait_time = source_config.get('wait_time', 5)
            await asyncio.sleep(wait_time)
            
            # 동적 콘텐츠 로딩 대기
            if source_config.get('wait_for_element'):
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, source_config['wait_for_element']))
                )
            
            html = self.driver.page_source
            return self._parse_html(html, source_config)
            
        except Exception as e:
            logger.error(f"❌ Selenium 크롤링 실패: {e}")
            raise
    
    def _parse_html(self, html: str, source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """HTML 파싱"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            articles = []
            
            # 셀렉터 설정
            article_selector = source_config['selectors']['article']
            title_selector = source_config['selectors']['title']
            link_selector = source_config['selectors']['link']
            content_selector = source_config['selectors'].get('content', '')
            date_selector = source_config['selectors'].get('date', '')
            
            # 기사 요소 찾기
            article_elements = soup.select(article_selector)
            
            for element in article_elements:
                try:
                    # 제목 추출
                    title_elem = element.select_one(title_selector)
                    title = title_elem.get_text(strip=True) if title_elem else ""
                    
                    # 링크 추출
                    link_elem = element.select_one(link_selector)
                    link = link_elem.get('href') if link_elem else ""
                    
                    # 상대 URL을 절대 URL로 변환
                    if link and not link.startswith('http'):
                        link = source_config['base_url'] + link if link.startswith('/') else source_config['base_url'] + '/' + link
                    
                    # 내용 추출 (선택적)
                    content = ""
                    if content_selector:
                        content_elem = element.select_one(content_selector)
                        content = content_elem.get_text(strip=True) if content_elem else ""
                    
                    # 날짜 추출 (선택적)
                    date = ""
                    if date_selector:
                        date_elem = element.select_one(date_selector)
                        date = date_elem.get_text(strip=True) if date_elem else ""
                    
                    # 기사 데이터 구성
                    if title and link:
                        article = {
                            'title': data_processor.clean_text(title),
                            'link': link,
                            'content': data_processor.clean_text(content),
                            'date': date,
                            'source': source_config['name'],
                            'crawled_at': datetime.now().isoformat()
                        }
                        
                        articles.append(article)
                
                except Exception as e:
                    logger.warning(f"⚠️ 기사 파싱 실패: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            logger.error(f"❌ HTML 파싱 실패: {e}")
            raise
    
    async def _process_articles(self, articles: List[Dict[str, Any]], 
                               source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """기사 데이터 후처리"""
        if not articles:
            return []
        
        processed_articles = []
        
        for article in articles:
            try:
                # 키워드 필터링
                if not self._check_keywords(article, source_config.get('keywords', [])):
                    continue
                
                # 중복 제거
                if not self._is_duplicate(article, processed_articles):
                    processed_articles.append(article)
                
            except Exception as e:
                logger.warning(f"⚠️ 기사 후처리 실패: {e}")
                continue
        
        return processed_articles
    
    def _check_keywords(self, article: Dict[str, Any], keywords: List[str]) -> bool:
        """키워드 필터링"""
        if not keywords:
            return True
        
        text = f"{article['title']} {article.get('content', '')}".lower()
        
        for keyword in keywords:
            if keyword.lower() in text:
                return True
        
        return False
    
    def _is_duplicate(self, article: Dict[str, Any], existing_articles: List[Dict[str, Any]]) -> bool:
        """중복 검사"""
        title = article['title'].lower()
        
        for existing in existing_articles:
            existing_title = existing['title'].lower()
            similarity = data_processor.calculate_similarity(title, existing_title)
            
            if similarity > 0.8:  # 80% 이상 유사하면 중복으로 판단
                return True
        
        return False
    
    async def crawl_all_sources(self) -> List[Dict[str, Any]]:
        """모든 소스 크롤링"""
        all_articles = []
        
        logger.info(f"🚀 전체 소스 크롤링 시작: {len(NEWS_SOURCES)}개 소스")
        
        # 병렬 크롤링
        tasks = []
        for source_config in NEWS_SOURCES:
            task = asyncio.create_task(self.crawl_source(source_config))
            tasks.append(task)
        
        # 결과 수집
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"❌ 소스 {i+1} 크롤링 실패: {result}")
                continue
            
            all_articles.extend(result)
        
        # 전체 중복 제거
        all_articles = data_processor.remove_duplicates(all_articles, 'title', 0.8)
        
        # 정렬 (최신순)
        all_articles.sort(key=lambda x: x.get('crawled_at', ''), reverse=True)
        
        self.stats['sources_processed'] = len(NEWS_SOURCES)
        
        logger.info(f"🎉 전체 크롤링 완료: {len(all_articles)}개 기사")
        return all_articles
    
    def get_statistics(self) -> Dict[str, Any]:
        """크롤링 통계 반환"""
        return {
            **self.stats,
            'error_statistics': self.error_handler.get_statistics(),
            'timestamp': datetime.now().isoformat()
        }
    
    def save_statistics(self, file_path: str = "data/crawler_stats.json"):
        """통계 저장"""
        try:
            stats = self.get_statistics()
            data_processor.save_to_file(stats, file_path, 'json')
            logger.info(f"💾 크롤링 통계 저장: {file_path}")
        except Exception as e:
            logger.error(f"❌ 통계 저장 실패: {e}")

# 사용 예시
async def main():
    """크롤러 테스트"""
    async with NewsCrawler() as crawler:
        articles = await crawler.crawl_all_sources()
        
        print(f"📰 크롤링 결과: {len(articles)}개 기사")
        for article in articles[:5]:  # 상위 5개만 출력
            print(f"- {article['title']} ({article['source']})")
        
        crawler.save_statistics()

if __name__ == "__main__":
    asyncio.run(main()) 