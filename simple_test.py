#!/usr/bin/env python3
"""
🧪 간단한 통합 테스트
기존 프로그램과 새로운 스케줄러의 기본 기능 테스트
"""

import os
import sys
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_imports():
    """임포트 테스트"""
    logger.info("1️⃣ 임포트 테스트 시작...")
    
    try:
        # 기존 프로그램 임포트 테스트
        sys.path.append('semiauto/core')
        logger.info("✅ semiauto/core 경로 추가 완료")
        
        # 새로운 스케줄러 임포트 테스트
        sys.path.append('auto_finance')
        logger.info("✅ auto_finance 경로 추가 완료")
        
        # 실제 임포트 테스트
        try:
            from final_solution import GriderAutoSender, load_config
            logger.info("✅ 기존 프로그램 임포트 성공")
        except ImportError as e:
            logger.error(f"❌ 기존 프로그램 임포트 실패: {e}")
            return False
        
        try:
            from auto_finance.core.kakao_scheduler import KakaoScheduler
            logger.info("✅ 새로운 스케줄러 임포트 성공")
        except ImportError as e:
            logger.error(f"❌ 새로운 스케줄러 임포트 실패: {e}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 임포트 테스트 실패: {e}")
        return False

def test_config_loading():
    """설정 파일 로드 테스트"""
    logger.info("2️⃣ 설정 파일 로드 테스트...")
    
    try:
        from final_solution import load_config
        
        rest_api_key, refresh_token = load_config()
        
        if rest_api_key and refresh_token:
            logger.info("✅ 설정 파일 로드 성공")
            logger.info(f"   REST_API_KEY: {rest_api_key[:10]}...")
            logger.info(f"   REFRESH_TOKEN: {refresh_token[:10]}...")
            return True
        else:
            logger.error("❌ 설정 파일 로드 실패 - 토큰이 없습니다")
            return False
            
    except Exception as e:
        logger.error(f"❌ 설정 파일 로드 테스트 실패: {e}")
        return False

def test_scheduler_creation():
    """스케줄러 생성 테스트"""
    logger.info("3️⃣ 스케줄러 생성 테스트...")
    
    try:
        from auto_finance.core.kakao_scheduler import KakaoScheduler
        
        scheduler = KakaoScheduler()
        logger.info("✅ 스케줄러 생성 성공")
        
        # 기본 상태 확인
        status = scheduler.get_schedule_status()
        logger.info(f"   스케줄러 상태: {'실행 중' if status['is_running'] else '중지됨'}")
        logger.info(f"   스케줄된 메시지: {status['scheduled_count']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 스케줄러 생성 테스트 실패: {e}")
        return False

def test_message_scheduling():
    """메시지 스케줄링 테스트"""
    logger.info("4️⃣ 메시지 스케줄링 테스트...")
    
    try:
        from auto_finance.core.kakao_scheduler import KakaoScheduler, ScheduleType
        
        scheduler = KakaoScheduler()
        
        # 테스트 메시지 스케줄링
        test_message = "🧪 테스트 메시지 - " + datetime.now().strftime('%H:%M:%S')
        
        message_id = scheduler.schedule_message(
            content=test_message,
            schedule_time=datetime.now(),
            schedule_type=ScheduleType.CUSTOM,
            metadata={'test': True}
        )
        
        if message_id:
            logger.info(f"✅ 메시지 스케줄링 성공: {message_id}")
            
            # 메시지 상태 확인
            status = scheduler.get_message_status(message_id)
            if status:
                logger.info(f"   메시지 상태: {status['status']}")
            
            return True
        else:
            logger.error("❌ 메시지 스케줄링 실패")
            return False
            
    except Exception as e:
        logger.error(f"❌ 메시지 스케줄링 테스트 실패: {e}")
        return False

def test_legacy_system():
    """기존 시스템 테스트"""
    logger.info("5️⃣ 기존 시스템 테스트...")
    
    try:
        from final_solution import GriderAutoSender, load_config
        
        rest_api_key, refresh_token = load_config()
        if not rest_api_key or not refresh_token:
            logger.error("❌ 설정 파일 로드 실패")
            return False
        
        auto_sender = GriderAutoSender(rest_api_key, refresh_token)
        logger.info("✅ 기존 시스템 객체 생성 성공")
        
        # 연결 테스트 (실제 API 호출 없이)
        logger.info("   연결 테스트는 실제 카카오 API 호출이 필요하므로 건너뜀")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 기존 시스템 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    logger.info("🧪 통합 시스템 테스트 시작")
    logger.info("=" * 50)
    
    tests = [
        ("임포트 테스트", test_imports),
        ("설정 파일 로드 테스트", test_config_loading),
        ("스케줄러 생성 테스트", test_scheduler_creation),
        ("메시지 스케줄링 테스트", test_message_scheduling),
        ("기존 시스템 테스트", test_legacy_system)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🔍 {test_name} 실행 중...")
        if test_func():
            logger.info(f"✅ {test_name} 통과")
            passed += 1
        else:
            logger.error(f"❌ {test_name} 실패")
    
    logger.info("\n" + "=" * 50)
    logger.info(f"📊 테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        logger.info("🎉 모든 테스트 통과! 시스템이 정상적으로 작동합니다.")
        return True
    else:
        logger.error("❌ 일부 테스트 실패. 문제를 해결해주세요.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 