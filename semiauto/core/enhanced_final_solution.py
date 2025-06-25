#!/usr/bin/env python3
"""
🎯 고도화된 최종 솔루션
- 정확한 시간 전송 보장
- 데이터 검증 시스템
- 중복 방지 및 누락 복구
- 한국시간 기준 정확한 스케줄링
"""

import sys
import os
import logging
from datetime import datetime
import pytz

# 현재 디렉토리를 파이썬 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# 기존 모듈들 import
from core.final_solution import (
    TokenManager, KakaoSender, GriderDataCollector, 
    GriderAutoSender, load_config, KST
)

# 새로운 모듈들 import
from core.enhanced_scheduler import EnhancedScheduler
from core.data_validator import EnhancedDataValidator

logger = logging.getLogger(__name__)

class EnhancedGriderAutoSender(GriderAutoSender):
    """고도화된 G라이더 자동 전송 시스템"""
    
    def __init__(self, rest_api_key, refresh_token):
        super().__init__(rest_api_key, refresh_token)
        
        # 고도화된 컴포넌트 추가
        self.scheduler = EnhancedScheduler(self)
        self.data_validator = EnhancedDataValidator()
        
        logger.info("🚀 고도화된 G라이더 자동 전송 시스템 초기화 완료")
    
    def send_report_with_validation(self) -> bool:
        """검증이 강화된 리포트 전송"""
        try:
            # 1. 전송 시간 검증
            should_send, reason = self.scheduler.should_send_now()
            if not should_send:
                logger.info(f"⏸️ 전송 스킵: {reason}")
                return False
            
            # 2. 데이터 수집
            logger.info("📊 데이터 수집 시작...")
            data = self.data_collector.get_grider_data()
            
            if not data:
                logger.error("❌ 데이터 수집 실패")
                return False
            
            # 3. 데이터 검증
            logger.info("🔍 데이터 검증 시작...")
            is_valid, validation_result = self.data_validator.validate_data(data, "crawler")
            
            if not is_valid:
                logger.warning("⚠️ 데이터 검증 실패, 자동 수정 시도...")
                data = self.data_validator.fix_data_issues(data, validation_result)
                
                # 재검증
                is_valid, _ = self.data_validator.validate_data(data, "auto_fixed")
                if not is_valid:
                    logger.error("❌ 데이터 자동 수정 실패, 전송 중단")
                    return False
            
            # 4. 메시지 생성 및 전송
            access_token = self.token_manager.get_valid_token()
            self.sender = KakaoSender(access_token)
            
            message = self.format_message(data)
            result = self.sender.send_text_message(message)
            
            if result.get('result_code') == 0:
                # 5. 전송 성공 기록
                target_time = datetime.now(KST).replace(second=0, microsecond=0)
                message_id = str(result.get('result_id', f"msg_{int(datetime.now().timestamp())}"))
                data_hash = self.data_validator.freshness_checker.get_data_hash(data)
                
                self.scheduler.history.record_sent(target_time, message_id, data_hash)
                
                logger.info("✅ 검증된 메시지 전송 성공!")
                return True
            else:
                logger.error(f"❌ 메시지 전송 실패: {result}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 검증된 리포트 전송 중 오류: {e}")
            return False
    
    def run_single_validated_send(self) -> bool:
        """단일 검증 전송 (GitHub Actions용)"""
        logger.info("🤖 GitHub Actions 검증 전송 모드")
        
        # 누락된 메시지 복구 먼저 시도
        recovered_count = self.scheduler.recover_missing_messages()
        
        # 현재 시간 전송 시도
        should_send, reason = self.scheduler.should_send_now()
        
        if not should_send:
            logger.info(f"⏸️ 전송 스킵: {reason}")
            
            # 운영시간 외는 정상적인 상황으로 처리
            if "운영시간 외" in reason:
                logger.info("✅ 운영시간 외 - 정상 완료")
                success = True
            else:
                # 기타 이유로 스킵하는 경우 실제 전송 시도
                success = self.send_report_with_validation()
        else:
            # 전송 시간인 경우 실제 전송
            success = self.send_report_with_validation()
        
        # 상태 리포트 출력
        status = self.scheduler.get_status_report()
        logger.info(f"📊 실행 완료 상태:\n{status}")
        
        # 검증 통계 출력
        validation_stats = self.data_validator.get_validation_stats()
        logger.info(f"🔍 검증 통계: {validation_stats}")
        
        # 복구된 메시지가 있는 경우 로깅
        if recovered_count and recovered_count > 0:
            logger.info(f"✅ {recovered_count}개 메시지 복구 완료")
            
        return success
    
    def start_enhanced_scheduler(self):
        """고도화된 스케줄러 시작"""
        logger.info("🚀 고도화된 스케줄러 시작!")
        
        # 시작 시 상태 출력
        status = self.scheduler.get_status_report()
        logger.info(f"📊 시작 상태:\n{status}")
        
        try:
            while True:
                # 현재 시간에 전송해야 하는지 확인
                now = datetime.now(KST)
                
                # 운영시간 체크 (10:00~23:59)
                if 10 <= now.hour <= 23:
                    # 정확한 분에 실행 (0, 15, 30, 45분 또는 0, 30분)
                    expected_minutes = self.scheduler.validator.get_expected_minutes(now)
                    
                    if now.minute in expected_minutes and now.second < 30:
                        # 전송 시도
                        success = self.send_report_with_validation()
                        
                        if success:
                            logger.info(f"✅ 정시 전송 완료: {now.strftime('%H:%M')}")
                        
                        # 전송 후 60초 대기 (중복 방지)
                        import time
                        time.sleep(60)
                    
                    # 5분마다 누락 메시지 체크
                    elif now.minute % 5 == 0 and now.second < 30:
                        self.scheduler.recover_missing_messages()
                        import time
                        time.sleep(60)
                
                # 30초마다 체크
                import time
                time.sleep(30)
                
        except KeyboardInterrupt:
            logger.info("🛑 사용자에 의해 중지됨")
        except Exception as e:
            logger.error(f"❌ 고도화된 스케줄러 오류: {e}")
    
    def get_comprehensive_status(self) -> str:
        """종합 상태 리포트"""
        scheduler_status = self.scheduler.get_status_report()
        validation_stats = self.data_validator.get_validation_stats()
        
        return f"""
🎯 고도화된 G라이더 자동화 시스템 상태

{scheduler_status}

🔍 데이터 검증 통계:
📊 총 검증: {validation_stats['total']}회
✅ 성공: {validation_stats['valid']}회
❌ 실패: {validation_stats['invalid']}회
📈 성공률: {validation_stats['success_rate']:.1f}%

💡 시스템 특징:
✓ 정확한 시간 전송 보장
✓ 중복 전송 방지
✓ 누락 메시지 자동 복구
✓ 실시간 데이터 검증
✓ 한국시간 기준 스케줄링
        """.strip()

def main():
    """고도화된 메인 실행 함수"""
    import sys
    
    # GitHub Actions용 실행 모드 체크
    single_run = '--single-run' in sys.argv
    validation_mode = '--validation' in sys.argv
    recovery_mode = '--recovery' in sys.argv
    
    logger.info("🎯 고도화된 심플 배민 플러스 카카오톡 자동화 시작")
    
    # 설정 로드
    rest_api_key, refresh_token = load_config()
    if not rest_api_key or not refresh_token:
        logger.error("❌ 설정 로드 실패")
        return
    
    # 고도화된 자동화 객체 생성
    enhanced_sender = EnhancedGriderAutoSender(rest_api_key, refresh_token)
    
    # 연결 테스트
    if not enhanced_sender.test_connection():
        logger.error("❌ 연결 테스트 실패. 설정을 확인해주세요.")
        return
    
    if single_run:
        # GitHub Actions용 단일 실행
        logger.info("🤖 GitHub Actions 고도화 모드")
        success = enhanced_sender.run_single_validated_send()
        
        if success:
            logger.info("✅ GitHub Actions 고도화 실행 완료")
        else:
            logger.error("❌ GitHub Actions 고도화 실행 실패")
            sys.exit(1)
            
    elif validation_mode:
        # 검증 모드 (테스트용)
        logger.info("🔍 검증 모드 실행")
        
        # 현재 상태 출력
        status = enhanced_sender.get_comprehensive_status()
        print(status)
        
        # 검증 테스트 (실제 전송 없이 검증만)
        logger.info("📊 데이터 수집 및 검증 테스트...")
        data = enhanced_sender.data_collector.get_grider_data()
        if data:
            is_valid, validation_result = enhanced_sender.data_validator.validate_data(data, "validation_test")
            print(f"🔍 데이터 검증 결과: {'✅ 통과' if is_valid else '❌ 실패'}")
            if validation_result:
                print(f"📋 검증 세부사항: {validation_result}")
        else:
            print("❌ 데이터 수집 실패")
            
    elif recovery_mode:
        # 복구 모드
        logger.info("🔄 복구 모드 실행")
        
        # 누락된 메시지만 복구
        recovered = enhanced_sender.scheduler.recover_missing_messages()
        print(f"🔄 복구된 메시지: {recovered}개")
        
        # 복구 후 상태 출력
        status = enhanced_sender.get_comprehensive_status()
        print(status)
        
    else:
        # 로컬 고도화 스케줄러 모드
        logger.info("🧪 고도화된 연결 테스트 완료. 고도화 스케줄러에서 자동 시작됩니다.")
        
        # 종합 상태 출력
        status = enhanced_sender.get_comprehensive_status()
        logger.info(f"\n{status}")
        
        enhanced_sender.start_enhanced_scheduler()

if __name__ == "__main__":
    main() 