2#!/usr/bin/env python3
"""
실제 장부 데이터를 사용한 카카오톡 메시지 테스트
현재 미션 상황을 실시간으로 크롤링하여 메시지 생성
"""

import sys
import importlib.util
from datetime import datetime

def load_main_module():
    """main_(2).py 모듈을 동적으로 로드"""
    try:
        spec = importlib.util.spec_from_file_location("main_module", "main_(2).py")
        main_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_module)
        return main_module
    except Exception as e:
        print(f"❌ 메인 모듈 로드 실패: {e}")
        return None

def test_real_data_message():
    """실제 데이터로 메시지 테스트"""
    print("🔍 실제 장부 데이터 크롤링 및 메시지 생성 테스트")
    print("=" * 60)
    
    # 1. 메인 모듈 로드
    print("1️⃣ 메인 모듈 로드 중...")
    main_module = load_main_module()
    if not main_module:
        return
    
    print("✅ 메인 모듈 로드 완료")
    
    # 2. 실제 데이터 크롤링
    print("\n2️⃣ 실제 장부 데이터 크롤링 중...")
    try:
        html = main_module.crawl_jangboo()
        if not html:
            print("❌ 크롤링 실패")
            return
        print("✅ 크롤링 완료")
    except Exception as e:
        print(f"❌ 크롤링 오류: {e}")
        return
    
    # 3. 데이터 파싱
    print("\n3️⃣ 데이터 파싱 중...")
    try:
        data = main_module.parse_data(html)
        if not data:
            print("❌ 파싱 실패")
            return
        print("✅ 파싱 완료")
    except Exception as e:
        print(f"❌ 파싱 오류: {e}")
        return
    
    # 4. 데이터 요약 출력
    print("\n4️⃣ 현재 실제 데이터 요약:")
    print(f"   📊 총점: {data.get('총점', 0)}점")
    print(f"   🎯 수락률: {data.get('수락률', 0)}%")
    print(f"   ✅ 총완료: {data.get('총완료', 0)}건")
    print(f"   ❌ 총거절: {data.get('총거절', 0)}건")
    print(f"   👥 라이더 수: {len(data.get('riders', []))}명")
    
    # 피크별 현황
    peak_order = ['아침점심피크', '오후논피크', '저녁피크', '심야논피크']
    print("\n   📈 피크별 현황:")
    for peak in peak_order:
        peak_data = data.get(peak, {})
        current = peak_data.get('current', 0)
        target = peak_data.get('target', 0)
        progress = peak_data.get('progress', 0)
        status = "✅ 달성" if current >= target else f"❌ {target-current}건 부족"
        print(f"      {peak}: {current}/{target} ({progress:.1f}%) {status}")
    
    # 5. 메시지 생성
    print("\n5️⃣ 카카오톡 메시지 생성 중...")
    try:
        message = main_module.make_message(data)
        print("✅ 메시지 생성 완료")
    except Exception as e:
        print(f"❌ 메시지 생성 오류: {e}")
        return
    
    # 6. 실제 메시지 출력
    print("\n" + "="*60)
    print("📱 실제 데이터 기반 카카오톡 메시지")
    print("="*60)
    print()
    print("📊 미션 현황 리포트")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()
    print(message)
    print()
    print("🔄 자동 업데이트 | 🤖 G라이더 미션봇")
    print("="*60)
    
    # 7. 상세 라이더 정보
    print("\n📋 상세 라이더 정보:")
    riders = data.get('riders', [])
    if riders:
        # 기여도 순으로 정렬
        sorted_riders = sorted(riders, key=lambda x: x.get('contribution', 0), reverse=True)
        
        for i, rider in enumerate(sorted_riders[:5], 1):  # 상위 5명만
            print(f"\n{i}. {rider.get('name', '이름없음')}")
            print(f"   총 완료: {rider.get('complete', 0)}건")
            print(f"   아침점심피크: {rider.get('아침점심피크', 0)}건")
            print(f"   오후논피크: {rider.get('오후논피크', 0)}건")
            print(f"   저녁피크: {rider.get('저녁피크', 0)}건")
            print(f"   심야논피크: {rider.get('심야논피크', 0)}건")
            print(f"   수락률: {rider.get('acceptance_rate', 0)}%")
            print(f"   거절: {rider.get('reject', 0)}건, 취소: {rider.get('cancel', 0)}건")
            print(f"   기여도: {rider.get('contribution', 0)}%")
    
    print(f"\n✅ 실제 데이터 기반 메시지 테스트 완료!")
    print(f"📊 총 {len(riders)}명의 라이더 데이터를 기반으로 생성되었습니다.")

def test_weather_integration():
    """날씨 정보 통합 테스트"""
    print("\n🌤️ 날씨 정보 통합 테스트")
    print("-" * 30)
    
    try:
        # weather_service 모듈 로드 시도
        spec = importlib.util.spec_from_file_location("weather_module", "weather_service.py")
        weather_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(weather_module)
        
        weather_info = weather_module.get_ansan_weather()
        print("✅ 날씨 정보 조회 성공:")
        print(weather_info)
    except Exception as e:
        print(f"⚠️ 날씨 정보 조회 실패: {e}")
        print("기본 날씨 정보를 사용합니다.")

def quick_test():
    """빠른 테스트 (크롤링 없이 캐시 데이터 사용)"""
    print("⚡ 빠른 테스트 (캐시 데이터 사용)")
    print("=" * 40)
    
    main_module = load_main_module()
    if not main_module:
        return
    
    # 캐시된 데이터 로드 시도
    try:
        cached_data = main_module.load_mission_data_cache()
        if cached_data:
            print("✅ 캐시된 미션 데이터 발견")
            
            # 기본 데이터 구조 생성
            data = {
                "총점": 850,
                "물량점수": 520,
                "수락률점수": 330,
                "총완료": 210,
                "총거절": 25,
                "수락률": 89.4,
                "riders": []  # 간단한 테스트용
            }
            
            # 캐시 데이터 통합
            data.update(cached_data)
            
            message = main_module.make_message(data)
            
            print("\n📱 캐시 데이터 기반 메시지:")
            print("-" * 40)
            print("📊 미션 현황 리포트")
            print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            print()
            print(message)
            print()
            print("🔄 자동 업데이트 | 🤖 G라이더 미션봇")
        else:
            print("❌ 캐시된 데이터가 없습니다. 실제 크롤링이 필요합니다.")
    except Exception as e:
        print(f"❌ 캐시 데이터 로드 실패: {e}")

if __name__ == "__main__":
    print("🤖 실제 데이터 기반 카카오톡 메시지 테스트")
    print("1. 실제 데이터 크롤링 및 메시지 생성 (전체)")
    print("2. 빠른 테스트 (캐시 데이터 사용)")
    print("3. 날씨 정보 테스트")
    print("4. 모든 테스트 실행")
    
    choice = input("\n선택 (1-4): ").strip()
    
    if choice == "1":
        test_real_data_message()
    elif choice == "2":
        quick_test()
    elif choice == "3":
        test_weather_integration()
    elif choice == "4":
        test_real_data_message()
        test_weather_integration()
    else:
        print("잘못된 선택입니다. 빠른 테스트를 실행합니다.")
        quick_test() 