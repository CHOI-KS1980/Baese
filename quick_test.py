#!/usr/bin/env python3
"""
빠른 테스트 스크립트
"""

import datetime as dt
import pytz

def get_korean_time():
    """한국시간 반환"""
    try:
        kst = pytz.timezone('Asia/Seoul')
        return dt.datetime.now(kst)
    except ImportError:
        utc_now = dt.datetime.utcnow()
        kst_now = utc_now + dt.timedelta(hours=9)
        return kst_now

def get_mission_date():
    """미션 기준 날짜 계산 (03:00~다음날 02:59를 하나의 미션 날짜로 간주)"""
    now = get_korean_time()
    if now.time() < dt.time(3, 0):
        mission_date = now.date() - dt.timedelta(days=1)
    else:
        mission_date = now.date()
    return mission_date.strftime('%Y-%m-%d')

def is_message_time():
    """메시지 전송 시간대(00:00~02:59, 10:00~23:59)인지 확인"""
    now = get_korean_time()
    t = now.time()
    return (dt.time(0, 0) <= t < dt.time(3, 0)) or (dt.time(10, 0) <= t <= dt.time(23, 59, 59))

if __name__ == "__main__":
    print("🕐 빠른 테스트 결과")
    print("=" * 30)
    
    kst_now = get_korean_time()
    mission_date = get_mission_date()
    message_time = is_message_time()
    
    print(f"⏰ 현재 한국시간: {kst_now}")
    print(f"🎯 미션 날짜: {mission_date}")
    print(f"📤 메시지 전송 시간: {'예' if message_time else '아니오'}")
    
    # 시간대별 테스트
    print("\n📅 시간대별 테스트:")
    test_times = [0, 2, 3, 9, 10, 15, 23]
    for hour in test_times:
        test_time = kst_now.replace(hour=hour, minute=0, second=0, microsecond=0)
        if test_time.time() < dt.time(3, 0):
            test_mission = (test_time.date() - dt.timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            test_mission = test_time.date().strftime('%Y-%m-%d')
        
        test_message = (dt.time(0, 0) <= test_time.time() < dt.time(3, 0)) or (dt.time(10, 0) <= test_time.time() <= dt.time(23, 59, 59))
        
        print(f"  {hour:02d}:00 → 미션: {test_mission}, 전송: {'예' if test_message else '아니오'}")
    
    print("\n✅ 테스트 완료!") 