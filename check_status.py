#!/usr/bin/env python3
import sys
import os
sys.path.append('.')

# main_(2).py 파일을 임포트
import importlib.util
spec = importlib.util.spec_from_file_location("main", "main_(2).py")
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)

import datetime

print("=== 현재 시스템 상황 체크 ===")
print(f"현재 시각: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"미션 날짜: {main.get_mission_date()}")
print(f"활성 피크: {main.get_active_peaks()}")

# 캐시 상태 확인
try:
    cached_data = main.load_mission_data_cache()
    if cached_data:
        print("\n=== 캐시된 미션 데이터 ===")
        for peak, data in cached_data.items():
            if isinstance(data, dict) and 'current' in data:
                print(f"{peak}: {data['current']}/{data['target']}건")
    else:
        print("\n캐시된 데이터 없음")
except Exception as e:
    print(f"\n캐시 확인 실패: {e}")

# 기존 용어 사용 현황 분석
print("\n=== 기존 용어 사용 현황 분석 ===")
with open("main_(2).py", "r", encoding="utf-8") as f:
    content = f.read()
    
legacy_terms = ["오전피크", "오후피크", "심야피크"]
for term in legacy_terms:
    count = content.count(term)
    print(f"{term}: {count}회 사용")

print("\n=== 최적화 필요 사항 ===")
print("1. 기존 용어 완전 제거")
print("2. 코드 중복 제거")
print("3. 성능 최적화")
print("4. 메모리 사용량 최적화") 