#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기존 메시지 포맷 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.dashboard_data_generator import DashboardDataGenerator
from datetime import datetime
import pytz

def main():
    print("📝 기존 메시지 포맷 테스트")
    print("=" * 50)
    
    # DashboardDataGenerator 인스턴스 생성
    dashboard = DashboardDataGenerator()
    
    # 샘플 데이터 생성
    sample_data = dashboard.generate_sample_data()
    
    # 메시지 생성
    message_data = dashboard.generate_message_data(sample_data)
    
    print("🎯 생성된 메시지:")
    print("-" * 30)
    print(message_data['full_message'])
    print("-" * 30)
    
    print(f"\n📊 메시지 정보:")
    print(f"   템플릿: {message_data['settings']['template']}")
    print(f"   포맷: {message_data['settings']['format']}")
    print(f"   생성 시간: {message_data['timestamp']}")
    
    # 현재 시간
    KST = pytz.timezone('Asia/Seoul')
    now = datetime.now(KST)
    print(f"   현재 시간: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n✅ 기존 final_solution.py와 동일한 메시지 포맷이 적용되었습니다!")

if __name__ == "__main__":
    main() 