#!/usr/bin/env python3
"""
미션 날짜 계산 및 크롤링 테스트
"""

from datetime import datetime, timedelta, time
import pytz

def test_mission_date():
    """미션 날짜 계산 테스트"""
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst)
    
    print(f"🕐 현재 시간: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 미션 날짜 계산 (03:00 기준)
    if now.time() < time(3, 0):
        mission_date = now.date() - timedelta(days=1)
        print(f"📅 미션 날짜: {mission_date} (전날 - 03:00 이전)")
    else:
        mission_date = now.date()
        print(f"📅 미션 날짜: {mission_date} (당일 - 03:00 이후)")
    
    return mission_date

def test_crawling():
    """크롤링 테스트"""
    print("\n🔍 크롤링 테스트 시작...")
    
    try:
        # final_solution.py의 크롤링 로직 테스트
        from semiauto.core.final_solution import GriderDataCollector
        
        collector = GriderDataCollector()
        data = collector.get_grider_data()
        
        print("✅ 크롤링 완료!")
        print(f"📊 수집된 데이터: {data}")
        
        return data
        
    except Exception as e:
        print(f"❌ 크롤링 실패: {e}")
        return None

if __name__ == "__main__":
    print("🚀 미션 날짜 및 크롤링 테스트")
    print("=" * 50)
    
    # 1. 미션 날짜 계산 테스트
    mission_date = test_mission_date()
    
    # 2. 크롤링 테스트
    data = test_crawling()
    
    print("\n" + "=" * 50)
    print("📋 테스트 결과 요약:")
    print(f"   • 미션 날짜: {mission_date}")
    print(f"   • 크롤링 성공: {'예' if data else '아니오'}")
    
    if data:
        print(f"   • 데이터 타입: {type(data)}")
        print(f"   • 데이터 키: {list(data.keys()) if isinstance(data, dict) else 'N/A'}") 