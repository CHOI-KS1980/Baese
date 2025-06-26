#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
현재 시간에서 미션 날짜 계산 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, time, timedelta
import pytz

# 한국 시간대
KST = pytz.timezone('Asia/Seoul')

def _get_mission_date():
    """미션 날짜 계산 (실제 final_solution.py의 로직)"""
    now = datetime.now(KST)
    
    # 03:00 이전이면 전날, 03:00 이후면 당일
    if now.time() < time(3, 0):
        mission_date = now.date() - timedelta(days=1)
    else:
        mission_date = now.date()
    
    return mission_date, now

def main():
    print("🕐 현재 시간 기준 미션 날짜 계산 테스트")
    print("=" * 50)
    
    mission_date, current_time = _get_mission_date()
    
    print(f"📅 현재 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"🎯 계산된 미션 날짜: {mission_date}")
    print(f"⏰ 기준 시간: 03:00 (이후면 당일, 이전이면 전날)")
    
    # 현재 시간이 03:00 이후/이전인지 확인
    current_time_only = current_time.time()
    cutoff_time = time(3, 0)
    
    if current_time_only < cutoff_time:
        print(f"✅ {current_time_only.strftime('%H:%M')} < 03:00 → 전날 ({mission_date})")
    else:
        print(f"✅ {current_time_only.strftime('%H:%M')} >= 03:00 → 당일 ({mission_date})")
    
    # 원래 문제: 08:50에 어제 데이터가 나왔다는 문제
    if current_time.hour == 8 and current_time.minute == 50:
        print("\n🚨 이 시간(08:50)에 어제 데이터가 나왔다는 문제 보고가 있었습니다!")
        print("✅ 하지만 로직상으로는 당일 데이터가 나와야 합니다.")
        print("💡 문제 원인: 크롤링 실패 또는 웹사이트에서 어제 데이터 제공")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main() 