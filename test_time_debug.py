#!/usr/bin/env python3
"""
시간 계산 로직 테스트 스크립트
한국시간 기준으로 미션 날짜와 피크시간 계산을 확인
"""

import datetime as dt
import pytz
from datetime import timedelta

def get_korean_time():
    """한국시간 반환"""
    try:
        kst = pytz.timezone('Asia/Seoul')
        return dt.datetime.now(kst)
    except ImportError:
        # pytz가 없으면 UTC+9로 계산
        utc_now = dt.datetime.utcnow()
        kst_now = utc_now + timedelta(hours=9)
        return kst_now

def get_mission_date():
    """미션 기준 날짜 계산 (16:00~다음날 15:59를 하나의 미션 날짜로 간주)"""
    now = get_korean_time()
    
    # 현재 시간이 16:00 이전이면 전날을 미션 날짜로 계산
    if now.time() < dt.time(16, 0):
        mission_date = now.date() - timedelta(days=1)
    else:
        mission_date = now.date()
    
    return mission_date.strftime('%Y-%m-%d')

# 피크시간 정의 (한국시간 기준)
PEAK_TIMES = {
    '아침점심피크': {'start': 7, 'end': 13},    # 07:00-13:00
    '오후논피크': {'start': 13, 'end': 17},     # 13:00-17:00  
    '저녁피크': {'start': 17, 'end': 21},       # 17:00-21:00
    '심야논피크': {'start': 21, 'end': 7}       # 21:00-07:00 (다음날)
}

def is_peak_time():
    """현재가 피크시간인지 확인"""
    now = get_korean_time()
    current_hour = now.hour
    
    for peak_name, time_range in PEAK_TIMES.items():
        start_hour = time_range['start']
        end_hour = time_range['end']
        
        if start_hour <= end_hour:
            # 일반적인 시간대 (예: 07:00-13:00)
            if start_hour <= current_hour < end_hour:
                return True
        else:
            # 심야시간대 (예: 21:00-07:00)
            if current_hour >= start_hour or current_hour < end_hour:
                return True
    
    return False

def get_current_peak_name():
    """현재 피크시간 이름 반환"""
    now = get_korean_time()
    current_hour = now.hour
    
    for peak_name, time_range in PEAK_TIMES.items():
        start_hour = time_range['start']
        end_hour = time_range['end']
        
        if start_hour <= end_hour:
            if start_hour <= current_hour < end_hour:
                return peak_name
        else:
            if current_hour >= start_hour or current_hour < end_hour:
                return peak_name
    
    return "일반시간"

def test_time_calculations():
    """시간 계산 테스트"""
    print("🕐 시간 계산 로직 테스트")
    print("=" * 50)
    
    # 현재 시간
    kst_now = get_korean_time()
    print(f"⏰ 현재 한국시간: {kst_now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 미션 날짜
    mission_date = get_mission_date()
    print(f"🎯 현재 미션 날짜: {mission_date}")
    
    # 피크시간 확인
    is_peak = is_peak_time()
    current_peak = get_current_peak_name()
    print(f"📈 현재 피크시간: {current_peak}")
    print(f"🚀 피크시간 여부: {'예' if is_peak else '아니오'}")
    
    print("\n📅 시간대별 테스트:")
    print("-" * 30)
    
    # 다양한 시간대 테스트
    test_hours = [9, 10, 15, 16, 17, 20, 23, 0, 3, 6]
    
    for hour in test_hours:
        # 테스트용 시간 생성
        test_time = kst_now.replace(hour=hour, minute=0, second=0, microsecond=0)
        
        # 미션 날짜 계산
        if test_time.time() < dt.time(16, 0):
            test_mission_date = (test_time.date() - timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            test_mission_date = test_time.date().strftime('%Y-%m-%d')
        
        # 피크시간 확인
        test_current_hour = test_time.hour
        test_peak_name = "일반시간"
        
        for peak_name, time_range in PEAK_TIMES.items():
            start_hour = time_range['start']
            end_hour = time_range['end']
            
            if start_hour <= end_hour:
                if start_hour <= test_current_hour < end_hour:
                    test_peak_name = peak_name
                    break
            else:
                if test_current_hour >= start_hour or test_current_hour < end_hour:
                    test_peak_name = peak_name
                    break
        
        print(f"{test_time.strftime('%H:%M')} → 미션: {test_mission_date}, 피크: {test_peak_name}")

def test_schedule_times():
    """스케줄 시간 테스트"""
    print("\n📋 스케줄 시간 테스트")
    print("=" * 50)
    
    # 기본 30분 간격 (10:00-00:00)
    print("🕐 기본 30분 간격:")
    for hour in range(10, 24):
        for minute in [0, 30]:
            print(f"   {hour:02d}:{minute:02d}")
    print("   00:00")
    
    # 피크시간 15분 간격
    print("\n🚀 피크시간 15분 간격:")
    peak_hours = {
        '아침점심피크': range(7, 13),
        '오후논피크': range(13, 17),
        '저녁피크': range(17, 21),
        '심야논피크': list(range(21, 24)) + list(range(0, 7))
    }
    
    for peak_name, hours in peak_hours.items():
        print(f"   {peak_name}:")
        for hour in hours:
            for minute in [15, 45]:
                if hour == 0 and minute == 45:
                    continue
                print(f"     {hour:02d}:{minute:02d}")

if __name__ == "__main__":
    test_time_calculations()
    test_schedule_times()
    
    print("\n✅ 테스트 완료!")
    print("\n💡 참고사항:")
    print("   • 16:00 이전: 전날 미션 데이터")
    print("   • 16:00 이후: 오늘 미션 데이터")
    print("   • 피크시간: 15분 간격 추가 알림")
    print("   • 일반시간: 30분 간격 기본 알림") 