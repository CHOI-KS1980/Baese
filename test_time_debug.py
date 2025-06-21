#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytz
from datetime import datetime

# 한국시간 설정
KST = pytz.timezone('Asia/Seoul')

def test_current_time():
    """현재 시간 확인"""
    print("🕐 시간 확인 테스트")
    print("=" * 50)
    
    # 다양한 방법으로 시간 확인
    now_local = datetime.now()
    now_kst = datetime.now(KST)
    now_utc = datetime.utcnow()
    
    print(f"로컬 시간: {now_local.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"KST 시간:  {now_kst.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"UTC 시간:  {now_utc.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print()
    print("🎯 현재 시간대별 인사말:")
    
    # 시간대별 인사말 테스트
    current_hour = now_kst.hour
    current_minute = now_kst.minute
    
    print(f"현재 시간: {current_hour}:{current_minute:02d}")
    
    # 시간대별 인사말 매핑
    time_greetings = {
        (10, 0): "🌅 좋은 아침입니다! 오늘도 힘찬 하루를 시작해보세요!",
        (10, 30): "☀️ 오전 업무 시작! 오늘도 화이팅하세요!",
        (11, 0): "🌅 오전 11시! 점심 피크 준비 시간입니다!",
        (11, 30): "🌅 점심 피크 시간이 다가오고 있어요!",
        (12, 0): "🍽️ 정오 12시! 점심 피크 시작!",
        (12, 30): "🍽️ 점심 피크 시간! 안전운행 부탁드려요!",
        (13, 0): "⏰ 오후 1시! 점심 피크 마무리 시간!",
        (13, 30): "⏰ 오후 시간대 접어들었습니다!",
        (14, 0): "🌇 오후 2시! 논피크 시간대!",
        (14, 30): "🌇 오후 논피크 시간이에요!",
        (15, 0): "☕ 오후 3시! 잠시 휴식 시간!",
        (15, 30): "☕ 오후 3시 30분, 잠시 휴식하세요!",
        (16, 0): "🌆 오후 4시! 저녁 피크 준비!",
        (16, 30): "🌆 저녁 피크 준비 시간입니다!",
        (17, 0): "🌃 오후 5시! 저녁 피크 시작!",
        (17, 30): "🌃 저녁 피크 시간! 주문이 많을 예정이에요!",
        (18, 0): "🍽️ 저녁 6시! 저녁 식사 시간!",
        (18, 30): "🍽️ 저녁 식사 시간! 바쁜 시간대입니다!",
        (19, 0): "🌉 저녁 7시! 피크 마무리 시간!",
        (19, 30): "🌉 저녁 피크 마무리 시간이에요!",
        (20, 0): "🌙 저녁 8시! 심야 논피크 시작!",
        (20, 30): "🌙 심야 논피크 시간대 시작!",
        (21, 0): "🌃 밤 9시! 오늘도 수고하고 계세요!",
        (21, 30): "🌃 밤 9시 30분, 오늘도 수고하고 계세요!",
        (22, 0): "🌙 밤 10시! 심야 시간대 안전운행!",
        (22, 30): "🌙 심야 시간대, 안전운행 최우선!",
        (23, 0): "🌌 밤 11시! 하루 마무리가 다가와요!",
        (23, 30): "🌌 하루 마무리 시간이 다가오고 있어요!",
        (0, 0): "🌙 오늘 하루도 정말 수고하셨습니다!"
    }
    
    greeting = time_greetings.get((current_hour, current_minute), 
                                 f"⏰ {current_hour:02d}:{current_minute:02d} 현재 상황을 알려드립니다!")
    
    print(f"인사말: {greeting}")
    
    print()
    print("📅 스케줄 확인:")
    print("다음 실행 시간들:")
    
    # 다음 몇 개의 스케줄 시간 표시
    next_times = []
    for h in range(24):
        for m in [0, 30]:
            if (h == 10 and m == 0) or (h >= 10 and h <= 23 and m == 30) or (h >= 11 and h <= 23 and m == 0) or (h == 0 and m == 0):
                time_str = f"{h:02d}:{m:02d}"
                next_times.append(time_str)
    
    current_time_str = f"{current_hour:02d}:{current_minute:02d}"
    
    # 현재 시간 이후의 다음 5개 시간 찾기
    found_current = False
    next_count = 0
    for time_str in next_times:
        if time_str == current_time_str:
            found_current = True
            print(f"   → {time_str} (현재)")
        elif found_current and next_count < 5:
            print(f"   → {time_str}")
            next_count += 1
    
    if not found_current:
        print(f"   현재 시간 {current_time_str}는 스케줄에 없습니다.")
        print("   다음 스케줄 시간들:")
        for i, time_str in enumerate(next_times[:5]):
            print(f"   → {time_str}")

if __name__ == "__main__":
    test_current_time() 