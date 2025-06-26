#!/usr/bin/env python3
"""
🎯 고도화된 메시지 스케줄러
- 정확한 시간 전송 보장
- 중복 방지 시스템
- 누락 감지 및 복구
- 한국시간 기준 정확한 스케줄링
"""

import json
import os
import time
from datetime import datetime, timedelta
import pytz
import logging
from typing import Dict, List, Optional, Tuple
import hashlib

# 한국시간 설정
KST = pytz.timezone('Asia/Seoul')

logger = logging.getLogger(__name__)

class MessageHistory:
    """메시지 전송 히스토리 관리"""
    
    def __init__(self, history_file='message_history.json'):
        self.history_file = history_file
        self.history = self._load_history()
    
    def _load_history(self) -> Dict:
        """히스토리 파일 로드"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"히스토리 로드 실패: {e}")
        return {}
    
    def _save_history(self):
        """히스토리 파일 저장"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"히스토리 저장 실패: {e}")
    
    def get_message_key(self, target_time: datetime) -> str:
        """메시지 키 생성 (한국시간 기준)"""
        kst_time = target_time.astimezone(KST)
        return kst_time.strftime('%Y-%m-%d-%H-%M')
    
    def is_already_sent(self, target_time: datetime) -> bool:
        """해당 시간에 이미 메시지가 전송되었는지 확인"""
        key = self.get_message_key(target_time)
        return key in self.history
    
    def record_sent(self, target_time: datetime, message_id: str, data_hash: Optional[str] = None):
        """메시지 전송 기록"""
        key = self.get_message_key(target_time)
        self.history[key] = {
            'sent_at': datetime.now(KST).isoformat(),
            'target_time': target_time.astimezone(KST).isoformat(),
            'message_id': message_id,
            'data_hash': data_hash,
            'status': 'sent'
        }
        self._save_history()
        logger.info(f"✅ 메시지 전송 기록: {key}")
    
    def get_sent_times_today(self) -> List[str]:
        """오늘 전송된 시간 목록"""
        today = datetime.now(KST).strftime('%Y-%m-%d')
        return [key for key in self.history.keys() if key.startswith(today)]
    
    def cleanup_old_history(self, days: int = 7):
        """오래된 히스토리 정리"""
        cutoff = datetime.now(KST) - timedelta(days=days)
        cutoff_str = cutoff.strftime('%Y-%m-%d')
        
        old_keys = [key for key in self.history.keys() if key < cutoff_str]
        for key in old_keys:
            del self.history[key]
        
        if old_keys:
            self._save_history()
            logger.info(f"🗑️ 오래된 히스토리 {len(old_keys)}개 정리")

class ScheduleValidator:
    """스케줄 검증 및 관리"""
    
    def __init__(self):
        self.peak_hours = {
            '아침점심피크': {'weekday': (6, 13), 'weekend': (6, 14)},
            '오후논피크': {'weekday': (13, 17), 'weekend': (14, 17)},
            '저녁피크': {'weekday': (17, 20), 'weekend': (17, 20)},
            '심야논피크': {'weekday': (20, 24), 'weekend': (20, 24)}  # 24시는 다음날 0시
        }
    
    def is_weekend_or_holiday(self, dt: datetime) -> bool:
        """주말/공휴일 판정"""
        # 토요일(5), 일요일(6)
        if dt.weekday() >= 5:
            return True
        
        # 공휴일 체크 (한국천문연구원 API 연동)
        try:
            from semiauto.core.final_solution import holiday_checker
            is_holiday, _ = holiday_checker.is_holiday_advanced(dt.date())
            return is_holiday
        except:
            return False
    
    def get_peak_type(self, dt: datetime) -> Optional[str]:
        """현재 시간의 피크 타입 반환"""
        hour = dt.hour
        is_weekend = self.is_weekend_or_holiday(dt)
        period_type = 'weekend' if is_weekend else 'weekday'
        
        for peak_name, times in self.peak_hours.items():
            start, end = times[period_type]
            if peak_name == '심야논피크':
                # 심야논피크는 20시-다음날 3시
                if hour >= 20 or hour < 3:
                    return peak_name
            else:
                if start <= hour < end:
                    return peak_name
        
        return None
    
    def get_expected_minutes(self, dt: datetime) -> List[int]:
        """해당 시간대의 예상 전송 분 목록"""
        peak_type = self.get_peak_type(dt)
        
        if peak_type:
            # 피크시간: 0, 15, 30, 45분
            return [0, 15, 30, 45]
        else:
            # 비피크시간: 0, 30분
            return [0, 30]
    
    def get_expected_send_times(self, date: datetime) -> List[datetime]:
        """해당 날짜의 모든 예상 전송 시간 생성"""
        times = []
        
        # 운영시간: 10:00 ~ 23:59
        for hour in range(10, 24):
            dt = date.replace(hour=hour, minute=0, second=0, microsecond=0)
            expected_minutes = self.get_expected_minutes(dt)
            
            for minute in expected_minutes:
                send_time = dt.replace(minute=minute)
                times.append(send_time)
        
        return times
    
    def find_missing_times(self, date: datetime, history: MessageHistory) -> List[datetime]:
        """누락된 전송 시간 찾기"""
        expected_times = self.get_expected_send_times(date)
        missing_times = []
        
        for expected_time in expected_times:
            if not history.is_already_sent(expected_time):
                # 해당 시간이 이미 지났는지 확인
                now = datetime.now(KST)
                if expected_time < now:
                    missing_times.append(expected_time)
        
        return missing_times

class EnhancedScheduler:
    """고도화된 스케줄러"""
    
    def __init__(self, auto_sender):
        self.auto_sender = auto_sender
        self.history = MessageHistory()
        self.validator = ScheduleValidator()
        
        # 시작 시 오래된 히스토리 정리
        self.history.cleanup_old_history()
    
    def should_send_now(self) -> Tuple[bool, str]:
        """현재 시간에 메시지를 보내야 하는지 판단"""
        now = datetime.now(KST)
        
        # 운영시간 체크 (10:00~23:59)
        if not (10 <= now.hour <= 23):
            return False, f"운영시간 외 ({now.hour}시)"
        
        # 정확한 전송 시간인지 체크
        expected_minutes = self.validator.get_expected_minutes(now)
        if now.minute not in expected_minutes:
            return False, f"전송 시간 아님 ({now.minute}분, 예상: {expected_minutes})"
        
        # 이미 전송했는지 체크
        target_time = now.replace(second=0, microsecond=0)
        if self.history.is_already_sent(target_time):
            return False, f"이미 전송됨 ({self.history.get_message_key(target_time)})"
        
        return True, "전송 조건 충족"
    
    def send_message_with_validation(self, force_send: bool = False) -> bool:
        """검증된 메시지 전송"""
        now = datetime.now(KST)
        target_time = now.replace(second=0, microsecond=0)
        
        if not force_send:
            should_send, reason = self.should_send_now()
            if not should_send:
                logger.info(f"⏸️ 전송 스킵: {reason}")
                return False
        
        try:
            # 메시지 전송
            logger.info(f"📤 메시지 전송 시작: {target_time.strftime('%Y-%m-%d %H:%M')}")
            success = self.auto_sender.send_report()
            
            if success:
                # 전송 성공 기록
                message_id = f"msg_{int(time.time())}"
                self.history.record_sent(target_time, message_id)
                logger.info(f"✅ 메시지 전송 성공: {target_time.strftime('%H:%M')}")
                return True
            else:
                logger.error(f"❌ 메시지 전송 실패: {target_time.strftime('%H:%M')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 메시지 전송 중 오류: {e}")
            return False
    
    def recover_missing_messages(self):
        """누락된 메시지 복구"""
        today = datetime.now(KST).replace(hour=0, minute=0, second=0, microsecond=0)
        missing_times = self.validator.find_missing_times(today, self.history)
        
        if not missing_times:
            logger.info("📋 누락된 메시지 없음")
            return
        
        logger.warning(f"⚠️ 누락된 메시지 {len(missing_times)}개 발견")
        
        for missing_time in missing_times[-3:]:  # 최근 3개만 복구
            logger.info(f"🔄 누락 메시지 복구 시도: {missing_time.strftime('%H:%M')}")
            
            # 강제 전송
            try:
                success = self.auto_sender.send_report()
                if success:
                    message_id = f"recovery_{int(time.time())}"
                    self.history.record_sent(missing_time, message_id)
                    logger.info(f"✅ 누락 메시지 복구 완료: {missing_time.strftime('%H:%M')}")
                else:
                    logger.error(f"❌ 누락 메시지 복구 실패: {missing_time.strftime('%H:%M')}")
                    
                time.sleep(30)  # 복구 간 30초 대기
                
            except Exception as e:
                logger.error(f"❌ 누락 메시지 복구 실패: {missing_time.strftime('%H:%M')}")
    
    def get_status_report(self) -> str:
        """현재 상태 리포트"""
        now = datetime.now(KST)
        today_sent = len(self.history.get_sent_times_today())
        expected_today = len(self.validator.get_expected_send_times(now))
        
        peak_type = self.validator.get_peak_type(now)
        expected_minutes = self.validator.get_expected_minutes(now)
        
        return f"""📊 스케줄러 상태 리포트
🕐 현재 시간: {now.strftime('%Y-%m-%d %H:%M:%S')}
📈 오늘 전송: {today_sent}개 / 예상: {expected_today}개
🎯 현재 피크: {peak_type or '비피크시간'}
⏰ 전송 분: {expected_minutes}
📋 다음 전송: {self._get_next_send_time()}"""
    
    def _get_next_send_time(self) -> str:
        """다음 전송 시간 계산"""
        now = datetime.now(KST)
        expected_minutes = self.validator.get_expected_minutes(now)
        
        # 현재 시간 이후의 다음 전송 시간 찾기
        for minute in expected_minutes:
            next_time = now.replace(minute=minute, second=0, microsecond=0)
            if next_time > now:
                return next_time.strftime('%H:%M')
        
        # 다음 시간대 첫 번째 시간
        next_hour = now.hour + 1
        if next_hour > 23:
            return "내일 10:00"
        
        next_dt = now.replace(hour=next_hour, minute=0, second=0, microsecond=0)
        next_minutes = self.validator.get_expected_minutes(next_dt)
        next_time = next_dt.replace(minute=next_minutes[0])
        
        return next_time.strftime('%H:%M')

def test_scheduler():
    """스케줄러 테스트"""
    print("🧪 스케줄러 테스트 시작")
    
    # Mock auto_sender
    class MockAutoSender:
        def send_report(self):
            return True
    
    scheduler = EnhancedScheduler(MockAutoSender())
    
    # 현재 상태 확인
    print(scheduler.get_status_report())
    
    # 전송 조건 체크
    should_send, reason = scheduler.should_send_now()
    print(f"전송 여부: {should_send}, 이유: {reason}")
    
    # 누락 메시지 체크
    scheduler.recover_missing_messages()

if __name__ == "__main__":
    test_scheduler() 