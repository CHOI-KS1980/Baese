"""
📚 카카오톡 스케줄러 사용 예시
정확한 스케줄링과 전송 확인 시스템 사용법
"""

import asyncio
import os
from datetime import datetime, timedelta
from typing import Optional

# 스케줄러 임포트
from auto_finance.core.kakao_scheduler import KakaoScheduler, ScheduleType

async def basic_scheduler_example():
    """기본 스케줄러 사용 예시"""
    print("🚀 카카오톡 스케줄러 기본 사용 예시")
    print("=" * 60)
    
    # 1. 스케줄러 초기화
    scheduler = KakaoScheduler()
    
    # 2. 카카오 토큰 설정 (환경변수에서 가져오기)
    kakao_token = os.getenv('KAKAO_ACCESS_TOKEN')
    if kakao_token:
        scheduler.set_kakao_token(kakao_token)
        print("✅ 카카오 토큰 설정 완료")
    else:
        print("⚠️ 카카오 토큰이 설정되지 않았습니다. 시뮬레이션 모드로 실행됩니다.")
    
    # 3. 스케줄러 시작
    await scheduler.start_scheduler()
    print("✅ 스케줄러 시작 완료")
    
    # 4. 정기 메시지 스케줄링 (매시간 30분, 정각)
    print("\n📅 정기 메시지 스케줄링")
    regular_message = "🕐 정기 알림: 현재 시간은 {time}입니다."
    
    # 다음 정기 시간에 메시지 스케줄링
    message_id = scheduler.schedule_regular_message(regular_message)
    if message_id:
        print(f"✅ 정기 메시지 스케줄링 완료: {message_id}")
    else:
        print("❌ 정기 메시지 스케줄링 실패 (중복 메시지)")
    
    # 5. 피크 메시지 스케줄링 (15분 간격)
    print("\n📅 피크 메시지 스케줄링")
    peak_message = "🚨 피크 시간 알림: 현재 시간은 {time}입니다."
    
    message_id = scheduler.schedule_peak_message(peak_message)
    if message_id:
        print(f"✅ 피크 메시지 스케줄링 완료: {message_id}")
    else:
        print("❌ 피크 메시지 스케줄링 실패 (중복 메시지)")
    
    # 6. 스케줄 상태 확인
    print("\n📊 스케줄 상태 확인")
    status = scheduler.get_schedule_status()
    print(f"스케줄러 실행 상태: {'실행 중' if status['is_running'] else '중지됨'}")
    print(f"현재 시간: {status['current_time']}")
    print(f"스케줄된 메시지 수: {status['scheduled_count']}")
    print(f"전송된 메시지 수: {status['sent_count']}")
    print(f"실패한 메시지 수: {status['failed_count']}")
    print(f"다음 정기 전송 시간: {status['next_regular_time']}")
    print(f"다음 피크 전송 시간: {status['next_peak_time']}")
    print(f"피크 시간대: {status['peak_hours']}")
    
    # 7. 잠시 대기 (실제 전송 확인용)
    print("\n⏳ 10초간 대기 중... (실제 전송 확인)")
    await asyncio.sleep(10)
    
    # 8. 스케줄러 중지
    await scheduler.stop_scheduler()
    print("✅ 스케줄러 중지 완료")

async def advanced_scheduler_example():
    """고급 스케줄러 사용 예시"""
    print("\n🔧 고급 스케줄러 사용 예시")
    print("=" * 60)
    
    scheduler = KakaoScheduler()
    
    # 카카오 토큰 설정
    kakao_token = os.getenv('KAKAO_ACCESS_TOKEN')
    if kakao_token:
        scheduler.set_kakao_token(kakao_token)
    
    await scheduler.start_scheduler()
    
    # 1. 특정 시간에 메시지 스케줄링
    print("\n📅 특정 시간 메시지 스케줄링")
    target_time = datetime.now() + timedelta(minutes=2)  # 2분 후
    
    custom_message = f"⏰ 특정 시간 알림: {target_time.strftime('%H:%M')}에 전송됩니다."
    message_id = scheduler.schedule_message(
        content=custom_message,
        schedule_time=target_time,
        schedule_type=ScheduleType.CUSTOM,
        metadata={'type': 'custom_schedule', 'description': '테스트 메시지'}
    )
    
    if message_id:
        print(f"✅ 특정 시간 메시지 스케줄링 완료: {message_id}")
        print(f"   전송 예정 시간: {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 메시지 상태 확인
        message_status = scheduler.get_message_status(message_id)
        if message_status:
            print(f"   메시지 상태: {message_status['status']}")
            print(f"   재시도 횟수: {message_status['retry_count']}")
    else:
        print("❌ 특정 시간 메시지 스케줄링 실패")
    
    # 2. 여러 메시지 스케줄링
    print("\n📅 여러 메시지 스케줄링")
    messages = [
        "첫 번째 테스트 메시지",
        "두 번째 테스트 메시지", 
        "세 번째 테스트 메시지"
    ]
    
    scheduled_ids = []
    for i, message in enumerate(messages):
        # 각각 1분, 2분, 3분 후 전송
        target_time = datetime.now() + timedelta(minutes=i+1)
        message_id = scheduler.schedule_message(
            content=message,
            schedule_time=target_time,
            schedule_type=ScheduleType.CUSTOM
        )
        if message_id:
            scheduled_ids.append(message_id)
            print(f"✅ 메시지 {i+1} 스케줄링 완료: {message_id}")
    
    # 3. 중복 메시지 테스트
    print("\n🔄 중복 메시지 테스트")
    duplicate_message = "중복 테스트 메시지"
    target_time = datetime.now() + timedelta(minutes=1)
    
    # 첫 번째 스케줄링
    message_id1 = scheduler.schedule_message(duplicate_message, target_time)
    print(f"첫 번째 스케줄링: {message_id1}")
    
    # 동일한 내용으로 두 번째 스케줄링 (중복 감지)
    message_id2 = scheduler.schedule_message(duplicate_message, target_time)
    print(f"두 번째 스케줄링: {message_id2} (중복 감지됨)")
    
    # 4. 메시지 취소 테스트
    if scheduled_ids:
        print(f"\n❌ 메시지 취소 테스트: {scheduled_ids[0]}")
        cancelled = scheduler.cancel_message(scheduled_ids[0])
        print(f"취소 결과: {'성공' if cancelled else '실패'}")
    
    # 5. 실시간 모니터링
    print("\n📊 실시간 모니터링 (30초)")
    for i in range(30):
        status = scheduler.get_schedule_status()
        print(f"\r현재 시간: {status['current_time']} | 스케줄된: {status['scheduled_count']} | 전송된: {status['sent_count']} | 실패: {status['failed_count']}", end="")
        await asyncio.sleep(1)
    
    print("\n")  # 줄바꿈
    
    # 6. 최종 통계
    print("\n📈 최종 통계")
    final_status = scheduler.get_schedule_status()
    stats = final_status['stats']
    
    print(f"총 스케줄된 메시지: {stats['total_scheduled']}")
    print(f"총 전송된 메시지: {stats['total_sent']}")
    print(f"총 실패한 메시지: {stats['total_failed']}")
    print(f"총 확인된 메시지: {stats['total_confirmed']}")
    
    if stats['total_scheduled'] > 0:
        success_rate = (stats['total_sent'] / stats['total_scheduled']) * 100
        print(f"전송 성공률: {success_rate:.1f}%")
    
    await scheduler.stop_scheduler()

async def real_world_example():
    """실제 사용 시나리오 예시"""
    print("\n🌍 실제 사용 시나리오 예시")
    print("=" * 60)
    
    scheduler = KakaoScheduler()
    
    # 카카오 토큰 설정
    kakao_token = os.getenv('KAKAO_ACCESS_TOKEN')
    if kakao_token:
        scheduler.set_kakao_token(kakao_token)
    
    await scheduler.start_scheduler()
    
    # 실제 사용 시나리오: 장부 모니터링 알림
    print("\n📊 장부 모니터링 알림 시나리오")
    
    # 1. 정기 알림 (매시간 30분, 정각)
    regular_alert = """📊 장부 모니터링 정기 알림

⏰ 현재 시간: {time}
📈 총점: 95점
🎯 수락률: 93.8%
✅ 총완료: 75건

🤖 자동 모니터링 시스템"""
    
    message_id = scheduler.schedule_regular_message(regular_alert)
    if message_id:
        print(f"✅ 정기 알림 스케줄링 완료: {message_id}")
    
    # 2. 피크 시간 알림 (15분 간격)
    peak_alert = """🚨 피크 시간 장부 현황

⏰ 현재 시간: {time}
🔥 피크 시간대 활성화
📊 실시간 모니터링 중
⚡ 15분 간격 업데이트

🤖 자동 모니터링 시스템"""
    
    message_id = scheduler.schedule_peak_message(peak_alert)
    if message_id:
        print(f"✅ 피크 알림 스케줄링 완료: {message_id}")
    
    # 3. 긴급 알림 (즉시 전송)
    urgent_alert = """🚨 긴급 알림

⚠️ 시스템 이상 감지
🔧 자동 복구 시도 중
📱 관리자 확인 필요

🤖 자동 모니터링 시스템"""
    
    # 즉시 전송을 위해 현재 시간으로 스케줄링
    immediate_time = datetime.now()
    message_id = scheduler.schedule_message(
        content=urgent_alert,
        schedule_time=immediate_time,
        schedule_type=ScheduleType.CUSTOM,
        metadata={'priority': 'urgent', 'type': 'system_alert'}
    )
    
    if message_id:
        print(f"✅ 긴급 알림 스케줄링 완료: {message_id}")
    
    # 4. 모니터링 (1분간)
    print("\n📊 1분간 모니터링...")
    for i in range(60):
        status = scheduler.get_schedule_status()
        print(f"\r[{i+1:02d}/60] 전송된: {status['sent_count']} | 실패: {status['failed_count']} | 확인됨: {status['stats']['total_confirmed']}", end="")
        await asyncio.sleep(1)
    
    print("\n")  # 줄바꿈
    
    await scheduler.stop_scheduler()
    print("✅ 실제 사용 시나리오 완료")

if __name__ == "__main__":
    # 기본 예시
    asyncio.run(basic_scheduler_example())
    
    # 고급 예시
    asyncio.run(advanced_scheduler_example())
    
    # 실제 사용 시나리오
    asyncio.run(real_world_example()) 