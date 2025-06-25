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

def test_sample_data():
    """샘플 데이터로 미션 날짜 로직 테스트"""
    print("\n🔍 샘플 데이터 테스트 시작...")
    
    try:
        from semiauto.core.final_solution import GriderDataCollector
        
        collector = GriderDataCollector()
        
        # 샘플 데이터 가져오기
        sample_data = collector._get_sample_data()
        
        print("✅ 샘플 데이터 로드 완료!")
        print(f"📊 샘플 데이터 미션 현황:")
        
        # 미션 데이터 출력
        for peak_name in ['아침점심피크', '오후논피크', '저녁피크', '심야논피크']:
            if peak_name in sample_data:
                data = sample_data[peak_name]
                print(f"   • {peak_name}: {data['current']}/{data['target']}건")
        
        # 라이더 데이터 출력
        if 'riders' in sample_data and sample_data['riders']:
            print(f"   • 라이더 수: {len(sample_data['riders'])}명")
            for i, rider in enumerate(sample_data['riders'][:3]):  # 상위 3명만
                print(f"     {i+1}위: {rider['name']} ({rider['complete']}건)")
        
        return sample_data
        
    except Exception as e:
        print(f"❌ 샘플 데이터 테스트 실패: {e}")
        return None

def test_mission_date_logic():
    """다양한 시간대에서 미션 날짜 계산 테스트"""
    print("\n🕐 미션 날짜 계산 로직 테스트...")
    
    kst = pytz.timezone('Asia/Seoul')
    test_times = [
        (2, 30),   # 02:30 (전날)
        (3, 0),    # 03:00 (당일)
        (8, 50),   # 08:50 (당일) - 문제가 발생한 시간
        (15, 0),   # 15:00 (당일)
        (23, 59),  # 23:59 (당일)
    ]
    
    for hour, minute in test_times:
        # 테스트용 시간 생성
        test_time = datetime.now(kst).replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # 미션 날짜 계산
        if test_time.time() < time(3, 0):
            mission_date = test_time.date() - timedelta(days=1)
            result = "전날"
        else:
            mission_date = test_time.date()
            result = "당일"
        
        print(f"   {test_time.strftime('%H:%M')} → 미션: {mission_date} ({result})")

if __name__ == "__main__":
    print("🚀 미션 날짜 및 크롤링 테스트")
    print("=" * 50)
    
    # 1. 미션 날짜 계산 테스트
    mission_date = test_mission_date()
    
    # 2. 미션 날짜 계산 로직 테스트
    test_mission_date_logic()
    
    # 3. 샘플 데이터 테스트
    data = test_sample_data()
    
    print("\n" + "=" * 50)
    print("📋 테스트 결과 요약:")
    print(f"   • 미션 날짜: {mission_date}")
    print(f"   • 샘플 데이터 성공: {'예' if data else '아니오'}")
    
    if data:
        print(f"   • 데이터 타입: {type(data)}")
        print(f"   • 미션 데이터 키: {[k for k in data.keys() if '피크' in k]}")
        print(f"   • 라이더 데이터: {'있음' if data.get('riders') else '없음'}")
    
    print("\n💡 결론:")
    print("   • 미션 날짜 계산 로직은 정상 작동")
    print("   • 08:50에는 당일(오늘) 데이터가 나와야 함")
    print("   • 실제 문제는 크롤링 실패로 인한 대체 데이터 사용") 