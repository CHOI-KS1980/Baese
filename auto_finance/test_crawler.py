"""
크롤러 테스트 스크립트
"""

import asyncio
from core.news_crawler import NewsCrawler
from config.settings import settings

async def test_crawler():
    """크롤러 직접 테스트"""
    print("🔍 크롤러 테스트 시작")
    
    async with NewsCrawler() as crawler:
        # 네이버 뉴스 메인만 테스트
        test_source = settings.NEWS_SOURCES[-1]  # 마지막 추가된 네이버 뉴스 메인
        
        print(f"📰 테스트 소스: {test_source.name}")
        print(f"🔗 URL: {test_source.url}")
        print(f"🎯 셀렉터: {test_source.selectors}")
        
        # HTML 가져오기
        html = await crawler.fetch_page(test_source.url)
        if html:
            print(f"✅ HTML 가져오기 성공: {len(html)} 문자")
            
            # BeautifulSoup으로 파싱
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # 셀렉터로 요소 찾기
            title_elements = soup.select(test_source.selectors["title"])
            print(f"📰 제목 요소 찾음: {len(title_elements)}개")
            
            for i, elem in enumerate(title_elements[:3]):  # 처음 3개만
                title = elem.get_text().strip()
                print(f"  {i+1}. {title}")
                
                # 링크 찾기
                link_elem = elem.find_parent('a') or elem
                link = link_elem.get('href', '')
                if link:
                    print(f"     🔗 {link}")
                else:
                    print(f"     ❌ 링크 없음")
        else:
            print("❌ HTML 가져오기 실패")

if __name__ == "__main__":
    asyncio.run(test_crawler()) 