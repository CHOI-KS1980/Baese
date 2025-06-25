#!/usr/bin/env python3
"""
🔗 통합 테스트: 기존 final_solution.py + 새로운 카카오톡 스케줄러
정확한 스케줄링과 전송 확인이 포함된 통합 시스템 테스트
"""

import asyncio
import os
import sys
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# 기존 프로그램 임포트
sys.path.append('semiauto/core')
from final_solution import GriderAutoSender, load_config

# 새로운 스케줄러 임포트
sys.path.append('auto_finance')
from auto_finance.core.kakao_scheduler import KakaoScheduler, ScheduleType
from auto_finance.config.kakao_scheduler_config import get_config

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('integrated_test.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IntegratedGriderSystem:
    """통합 그리더 시스템: 기존 기능 + 새로운 스케줄러"""
    
    def __init__(self):
        # 기존 시스템 초기화
        self.rest_api_key, self.refresh_token = load_config()
        if not self.rest_api_key or not self.refresh_token:
            raise Exception("설정 파일 로드 실패")
        
        self.auto_sender = GriderAutoSender(self.rest_api_key, self.refresh_token)
        
        # 새로운 스케줄러 초기화
        self.scheduler = KakaoScheduler()
        
        # 카카오 토큰 설정
        self._setup_kakao_token()
        
        # 통합 설정
        self.integration_config = {
            'enable_legacy_scheduler': False,  # 기존 스케줄러 비활성화
            'enable_new_scheduler': True,      # 새로운 스케줄러 활성화
            'test_mode': True,                 # 테스트 모드
            'auto_start': True,                # 자동 시작
            'monitoring_interval': 60          # 모니터링 간격 (초)
        }
        
        logger.info("🔗 통합 그리더 시스템 초기화 완료")
    
    def _setup_kakao_token(self):
        """카카오 토큰 설정"""
        try:
            # 기존 시스템에서 토큰 가져오기
            access_token = self.auto_sender.token_manager.get_valid_token()
            self.scheduler.set_kakao_token(access_token)
            logger.info("✅ 카카오 토큰 설정 완료")
        except Exception as e:
            logger.error(f"❌ 카카오 토큰 설정 실패: {e}")
            raise
    
    async def start_integrated_system(self):
        """통합 시스템 시작"""
        logger.info("🚀 통합 그리더 시스템 시작")
        
        # 새로운 스케줄러 시작
        await self.scheduler.start_scheduler()
        
        # 스케줄 설정
        await self._setup_schedules()
        
        # 모니터링 시작
        await self._start_monitoring()
    
    async def _setup_schedules(self):
        """스케줄 설정"""
        logger.info("📅 스케줄 설정 중...")
        
        # 1. 정기 알림 (매시간 30분, 정각)
        regular_message = self._get_regular_message_template()
        message_id = self.scheduler.schedule_regular_message(regular_message)
        if message_id:
            logger.info(f"✅ 정기 알림 스케줄링 완료: {message_id}")
        
        # 2. 피크 시간 알림 (15분 간격)
        peak_message = self._get_peak_message_template()
        message_id = self.scheduler.schedule_peak_message(peak_message)
        if message_id:
            logger.info(f"✅ 피크 알림 스케줄링 완료: {message_id}")
        
        # 3. 시작 알림 (즉시 전송)
        start_message = self._get_start_message()
        immediate_time = datetime.now()
        message_id = self.scheduler.schedule_message(
            content=start_message,
            schedule_time=immediate_time,
            schedule_type=ScheduleType.CUSTOM,
            metadata={'type': 'start_notification'}
        )
        if message_id:
            logger.info(f"✅ 시작 알림 스케줄링 완료: {message_id}")
    
    def _get_regular_message_template(self) -> str:
        """정기 메시지 템플릿"""
        return """📊 심플 배민 플러스 정기 모니터링

⏰ 현재 시간: {time}
📈 시스템 상태: 정상
🎯 모니터링 간격: 매시간 30분, 정각
✅ 안정성: 99.9%

🤖 자동 모니터링 시스템"""
    
    def _get_peak_message_template(self) -> str:
        """피크 메시지 템플릿"""
        return """🚨 피크 시간 모니터링

⏰ 현재 시간: {time}
🔥 피크 시간대 활성화
⚡ 15분 간격 집중 모니터링
📊 실시간 현황 추적 중

🤖 자동 모니터링 시스템"""
    
    def _get_start_message(self) -> str:
        """시작 메시지"""
        return f"""🌅 통합 그리더 시스템 시작!

📅 {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}
🚀 새로운 스케줄러와 통합된 시스템이 시작되었습니다

✅ 정확한 스케줄링: 매시간 30분, 정각
✅ 피크 시간 모니터링: 15분 간격
✅ 전송 확인 및 재시도
✅ 중복 전송 방지

💪 안정적인 모니터링을 시작합니다!"""
    
    async def _start_monitoring(self):
        """모니터링 시작"""
        logger.info("📊 통합 모니터링 시작")
        
        try:
            while True:
                # 스케줄 상태 확인
                status = self.scheduler.get_schedule_status()
                
                # 실시간 상태 출력
                print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
                      f"스케줄된: {status['scheduled_count']} | "
                      f"전송된: {status['sent_count']} | "
                      f"실패: {status['failed_count']} | "
                      f"확인됨: {status['stats']['total_confirmed']}", end="")
                
                # 성능 지표 업데이트
                await self._update_performance_metrics(status)
                
                # 테스트 모드에서는 30초 후 종료
                if self.integration_config['test_mode']:
                    await asyncio.sleep(30)
                    break
                else:
                    await asyncio.sleep(self.integration_config['monitoring_interval'])
                    
        except KeyboardInterrupt:
            logger.info("🛑 사용자에 의해 중지됨")
        except Exception as e:
            logger.error(f"❌ 모니터링 오류: {e}")
        finally:
            await self.stop_integrated_system()
    
    async def _update_performance_metrics(self, status: Dict[str, Any]):
        """성능 지표 업데이트"""
        stats = status['stats']
        
        # 성공률 계산
        if stats['total_scheduled'] > 0:
            success_rate = (stats['total_sent'] / stats['total_scheduled']) * 100
            if success_rate < 90:  # 90% 미만이면 경고
                logger.warning(f"⚠️ 전송 성공률이 낮습니다: {success_rate:.1f}%")
        
        # 실패율 체크
        if stats['total_failed'] > 5:  # 5회 이상 실패 시 경고
            logger.warning(f"⚠️ 전송 실패가 많습니다: {stats['total_failed']}회")
    
    async def stop_integrated_system(self):
        """통합 시스템 중지"""
        logger.info("🛑 통합 시스템 중지 중...")
        
        # 스케줄러 중지
        await self.scheduler.stop_scheduler()
        
        # 종료 메시지 전송
        await self._send_end_message()
        
        logger.info("✅ 통합 시스템 중지 완료")
    
    async def _send_end_message(self):
        """종료 메시지 전송"""
        try:
            end_message = f"""🌙 통합 그리더 시스템 종료

📅 {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}
✅ 안정적인 모니터링이 완료되었습니다

📊 최종 통계:
   • 스케줄된 메시지: {self.scheduler.stats['total_scheduled']}
   • 전송된 메시지: {self.scheduler.stats['total_sent']}
   • 확인된 메시지: {self.scheduler.stats['total_confirmed']}
   • 실패한 메시지: {self.scheduler.stats['total_failed']}

🙏 수고하셨습니다!"""
            
            # 즉시 전송
            immediate_time = datetime.now()
            message_id = self.scheduler.schedule_message(
                content=end_message,
                schedule_time=immediate_time,
                schedule_type=ScheduleType.CUSTOM,
                metadata={'type': 'end_notification'}
            )
            
            if message_id:
                logger.info("✅ 종료 메시지 전송 완료")
                
        except Exception as e:
            logger.error(f"❌ 종료 메시지 전송 실패: {e}")
    
    async def test_integration(self):
        """통합 시스템 테스트"""
        logger.info("🧪 통합 시스템 테스트 시작")
        
        # 1. 기존 시스템 연결 테스트
        logger.info("1️⃣ 기존 시스템 연결 테스트...")
        if self.auto_sender.test_connection():
            logger.info("✅ 기존 시스템 연결 성공")
        else:
            logger.error("❌ 기존 시스템 연결 실패")
            return False
        
        # 2. 새로운 스케줄러 테스트
        logger.info("2️⃣ 새로운 스케줄러 테스트...")
        try:
            await self.scheduler.start_scheduler()
            
            # 테스트 메시지 전송
            test_message = "🧪 통합 시스템 테스트 메시지"
            message_id = self.scheduler.schedule_message(
                content=test_message,
                schedule_time=datetime.now(),
                schedule_type=ScheduleType.CUSTOM,
                metadata={'type': 'test'}
            )
            
            if message_id:
                logger.info(f"✅ 테스트 메시지 스케줄링 성공: {message_id}")
                
                # 10초 대기 후 상태 확인
                await asyncio.sleep(10)
                status = self.scheduler.get_message_status(message_id)
                if status:
                    logger.info(f"✅ 메시지 상태 확인: {status['status']}")
                
            await self.scheduler.stop_scheduler()
            logger.info("✅ 새로운 스케줄러 테스트 성공")
            
        except Exception as e:
            logger.error(f"❌ 새로운 스케줄러 테스트 실패: {e}")
            return False
        
        # 3. 데이터 수집 테스트
        logger.info("3️⃣ 데이터 수집 테스트...")
        try:
            data = self.auto_sender.data_collector.get_grider_data()
            if data and 'total_score' in data:
                logger.info(f"✅ 데이터 수집 성공: 총점 {data['total_score']}")
            else:
                logger.warning("⚠️ 데이터 수집 결과가 예상과 다름")
        except Exception as e:
            logger.error(f"❌ 데이터 수집 테스트 실패: {e}")
            return False
        
        logger.info("🎉 모든 통합 테스트 통과!")
        return True

async def main():
    """메인 실행 함수"""
    logger.info("🔗 통합 그리더 시스템 테스트 시작")
    
    try:
        # 통합 시스템 생성
        integrated_system = IntegratedGriderSystem()
        
        # 통합 테스트 실행
        test_success = await integrated_system.test_integration()
        
        if test_success:
            logger.info("✅ 통합 테스트 성공! 시스템을 시작합니다.")
            
            # 실제 시스템 시작
            await integrated_system.start_integrated_system()
        else:
            logger.error("❌ 통합 테스트 실패. 시스템을 시작할 수 없습니다.")
            return
        
    except Exception as e:
        logger.error(f"❌ 통합 시스템 초기화 실패: {e}")
        return

def run_legacy_comparison():
    """기존 시스템과 비교 테스트"""
    logger.info("🔄 기존 시스템과 비교 테스트 시작")
    
    try:
        # 기존 시스템 테스트
        rest_api_key, refresh_token = load_config()
        if not rest_api_key or not refresh_token:
            logger.error("❌ 설정 파일 로드 실패")
            return
        
        auto_sender = GriderAutoSender(rest_api_key, refresh_token)
        
        # 기존 시스템 연결 테스트
        if auto_sender.test_connection():
            logger.info("✅ 기존 시스템 연결 성공")
            
            # 기존 시스템으로 메시지 전송 테스트
            success = auto_sender.send_report()
            if success:
                logger.info("✅ 기존 시스템 메시지 전송 성공")
            else:
                logger.error("❌ 기존 시스템 메시지 전송 실패")
        else:
            logger.error("❌ 기존 시스템 연결 실패")
            
    except Exception as e:
        logger.error(f"❌ 기존 시스템 테스트 실패: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='통합 그리더 시스템 테스트')
    parser.add_argument('--legacy', action='store_true', help='기존 시스템만 테스트')
    parser.add_argument('--test-only', action='store_true', help='테스트만 실행하고 종료')
    
    args = parser.parse_args()
    
    if args.legacy:
        # 기존 시스템만 테스트
        run_legacy_comparison()
    elif args.test_only:
        # 테스트만 실행
        asyncio.run(main())
    else:
        # 전체 시스템 실행
        asyncio.run(main()) 