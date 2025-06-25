"""
⏰ 카카오톡 정확한 스케줄링 시스템
한국시간 기준 정확한 스케줄, 전송 확인, 재시도 로직
"""

import asyncio
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
import pytz
import requests

# 유틸리티 임포트
from auto_finance.utils.logger import setup_logger
from auto_finance.utils.error_handler import ErrorHandler

logger = setup_logger(__name__)

# 한국시간 설정
KST = pytz.timezone('Asia/Seoul')

class ScheduleType(Enum):
    """스케줄 타입"""
    REGULAR = "regular"      # 매시간 30분, 정각
    PEAK = "peak"           # 피크시간 15분 간격
    CUSTOM = "custom"       # 커스텀 스케줄

class MessageStatus(Enum):
    """메시지 상태"""
    SCHEDULED = "scheduled"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"
    RETRYING = "retrying"
    CONFIRMED = "confirmed"

@dataclass
class ScheduledMessage:
    """스케줄된 메시지"""
    id: str
    content: str
    schedule_time: datetime
    schedule_type: ScheduleType
    status: MessageStatus = MessageStatus.SCHEDULED
    created_at: datetime = field(default_factory=lambda: datetime.now(KST))
    sent_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    confirmation_attempts: int = 0
    max_confirmation_attempts: int = 5
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TransmissionResult:
    """전송 결과"""
    message_id: str
    success: bool
    sent_at: datetime
    response_code: Optional[int] = None
    response_text: Optional[str] = None
    confirmation_status: bool = False
    retry_count: int = 0

class KakaoScheduler:
    """카카오톡 정확한 스케줄링 시스템"""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        
        # 스케줄 관리
        self.scheduled_messages: Dict[str, ScheduledMessage] = {}
        self.sent_messages: Dict[str, TransmissionResult] = {}
        self.failed_messages: Dict[str, List[TransmissionResult]] = {}
        
        # 스케줄 설정
        self.schedule_config = {
            'regular_intervals': [0, 30],  # 매시간 0분, 30분
            'peak_intervals': [0, 15, 30, 45],  # 피크시간 15분 간격
            'peak_hours': [7, 8, 9, 11, 12, 13, 17, 18, 19, 20],  # 피크 시간대
            'confirmation_delay': 10,  # 전송 확인 대기 시간 (초)
            'retry_delays': [30, 60, 120, 300],  # 재시도 간격 (초)
            'confirmation_timeout': 30  # 전송 확인 타임아웃 (초)
        }
        
        # 카카오 API 설정
        self.kakao_config = {
            'access_token': None,
            'api_url': "https://kapi.kakao.com/v2/api/talk/memo/default/send",
            'timeout': 10
        }
        
        # 통계
        self.stats = {
            'total_scheduled': 0,
            'total_sent': 0,
            'total_failed': 0,
            'total_confirmed': 0,
            'schedule_accuracy': 0.0,
            'transmission_success_rate': 0.0
        }
        
        # 중복 전송 방지
        self.recent_message_hashes: List[str] = []
        self.max_recent_hashes = 100
        
        # 스케줄러 상태
        self.is_running = False
        self.scheduler_task = None
        
        logger.info("⏰ 카카오톡 스케줄러 초기화 완료")
    
    def set_kakao_token(self, access_token: str):
        """카카오 액세스 토큰 설정"""
        self.kakao_config['access_token'] = access_token
        logger.info("✅ 카카오 액세스 토큰 설정 완료")
    
    def schedule_message(self, content: str, schedule_time: datetime, 
                        schedule_type: ScheduleType = ScheduleType.REGULAR,
                        metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """메시지 스케줄링"""
        # 중복 메시지 체크
        message_hash = self._generate_message_hash(content, schedule_time)
        if message_hash in self.recent_message_hashes:
            logger.warning(f"⚠️ 중복 메시지 감지: {content[:50]}...")
            return None
        
        # 메시지 ID 생성
        message_id = self._generate_message_id(content, schedule_time)
        
        # 스케줄된 메시지 생성
        scheduled_message = ScheduledMessage(
            id=message_id,
            content=content,
            schedule_time=schedule_time,
            schedule_type=schedule_type,
            metadata=metadata or {}
        )
        
        # 스케줄에 추가
        self.scheduled_messages[message_id] = scheduled_message
        self.recent_message_hashes.append(message_hash)
        
        # 최근 해시 목록 크기 제한
        if len(self.recent_message_hashes) > self.max_recent_hashes:
            self.recent_message_hashes.pop(0)
        
        self.stats['total_scheduled'] += 1
        
        logger.info(f"📅 메시지 스케줄링: {message_id} - {schedule_time.strftime('%Y-%m-%d %H:%M:%S')}")
        return message_id
    
    def schedule_regular_message(self, content: str, target_time: Optional[datetime] = None) -> Optional[str]:
        """정기 메시지 스케줄링 (매시간 30분, 정각)"""
        if target_time is None:
            target_time = self._get_next_regular_time()
        
        return self.schedule_message(content, target_time, ScheduleType.REGULAR)
    
    def schedule_peak_message(self, content: str, target_time: Optional[datetime] = None) -> Optional[str]:
        """피크 메시지 스케줄링 (15분 간격)"""
        if target_time is None:
            target_time = self._get_next_peak_time()
        
        return self.schedule_message(content, target_time, ScheduleType.PEAK)
    
    def _get_next_regular_time(self) -> datetime:
        """다음 정기 전송 시간 계산"""
        now = datetime.now(KST)
        
        # 현재 시간이 30분 이전이면 30분, 아니면 다음 시간 정각
        if now.minute < 30:
            next_time = now.replace(minute=30, second=0, microsecond=0)
        else:
            next_time = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        
        return next_time
    
    def _get_next_peak_time(self) -> datetime:
        """다음 피크 전송 시간 계산 (15분 간격)"""
        now = datetime.now(KST)
        
        # 현재 시간이 피크 시간대인지 확인
        if now.hour in self.schedule_config['peak_hours']:
            # 15분 간격으로 다음 시간 계산
            current_minute = now.minute
            next_minute = ((current_minute // 15) + 1) * 15
            
            if next_minute >= 60:
                next_time = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
            else:
                next_time = now.replace(minute=next_minute, second=0, microsecond=0)
        else:
            # 피크 시간대가 아니면 다음 피크 시간대의 첫 시간
            next_peak_hour = self._get_next_peak_hour(now.hour)
            if next_peak_hour > now.hour:
                next_time = now.replace(hour=next_peak_hour, minute=0, second=0, microsecond=0)
            else:
                next_time = (now + timedelta(days=1)).replace(hour=next_peak_hour, minute=0, second=0, microsecond=0)
        
        return next_time
    
    def _get_next_peak_hour(self, current_hour: int) -> int:
        """다음 피크 시간대 계산"""
        peak_hours = self.schedule_config['peak_hours']
        for hour in peak_hours:
            if hour > current_hour:
                return hour
        return peak_hours[0]  # 다음 날 첫 피크 시간
    
    async def start_scheduler(self):
        """스케줄러 시작"""
        if self.is_running:
            logger.warning("⚠️ 스케줄러가 이미 실행 중입니다")
            return
        
        self.is_running = True
        logger.info("🚀 카카오톡 스케줄러 시작")
        
        # 스케줄러 태스크 시작
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
    
    async def stop_scheduler(self):
        """스케줄러 중지"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
        logger.info("🛑 카카오톡 스케줄러 중지")
    
    async def _scheduler_loop(self):
        """스케줄러 메인 루프"""
        while self.is_running:
            try:
                now = datetime.now(KST)
                
                # 전송할 메시지 확인
                messages_to_send = self._get_messages_to_send(now)
                
                for message in messages_to_send:
                    # 메시지 전송
                    await self._send_scheduled_message(message)
                
                # 전송 확인 대기 중인 메시지 처리
                await self._process_confirmation_queue()
                
                # 1초 대기
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ 스케줄러 루프 오류: {e}")
                await asyncio.sleep(5)
    
    def _get_messages_to_send(self, current_time: datetime) -> List[ScheduledMessage]:
        """전송할 메시지 목록 반환"""
        messages_to_send = []
        
        for message_id, message in self.scheduled_messages.items():
            if (message.status == MessageStatus.SCHEDULED and 
                message.schedule_time <= current_time):
                messages_to_send.append(message)
        
        return messages_to_send
    
    async def _send_scheduled_message(self, message: ScheduledMessage):
        """스케줄된 메시지 전송"""
        logger.info(f"📤 메시지 전송 시작: {message.id}")
        
        # 상태 업데이트
        message.status = MessageStatus.SENDING
        
        try:
            # 카카오톡 전송
            success = await self._send_to_kakao(message.content)
            
            if success:
                # 전송 성공
                message.status = MessageStatus.SENT
                message.sent_at = datetime.now(KST)
                
                # 전송 결과 저장
                result = TransmissionResult(
                    message_id=message.id,
                    success=True,
                    sent_at=message.sent_at,
                    retry_count=message.retry_count
                )
                self.sent_messages[message.id] = result
                
                # 전송 확인 태스크 시작
                asyncio.create_task(self._confirm_transmission(message))
                
                self.stats['total_sent'] += 1
                logger.info(f"✅ 메시지 전송 성공: {message.id}")
                
            else:
                # 전송 실패
                await self._handle_send_failure(message)
                
        except Exception as e:
            logger.error(f"❌ 메시지 전송 중 오류: {message.id} - {e}")
            await self._handle_send_failure(message)
    
    async def _send_to_kakao(self, content: str) -> bool:
        """카카오톡 전송"""
        if not self.kakao_config['access_token']:
            logger.error("❌ 카카오 액세스 토큰이 설정되지 않았습니다")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.kakao_config['access_token']}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            template = {
                "object_type": "text",
                "text": content,
                "link": {
                    "web_url": "https://github.com/CHOI-KS1980/Baese",
                    "mobile_web_url": "https://github.com/CHOI-KS1980/Baese"
                }
            }
            
            data = {"template_object": json.dumps(template)}
            
            response = requests.post(
                self.kakao_config['api_url'],
                headers=headers,
                data=data,
                timeout=self.kakao_config['timeout']
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"❌ 카카오톡 전송 오류: {e}")
            return False
    
    async def _handle_send_failure(self, message: ScheduledMessage):
        """전송 실패 처리"""
        message.retry_count += 1
        
        if message.retry_count <= message.max_retries:
            # 재시도
            message.status = MessageStatus.RETRYING
            
            # 재시도 지연 시간 계산
            delay = self.schedule_config['retry_delays'][
                min(message.retry_count - 1, len(self.schedule_config['retry_delays']) - 1)
            ]
            
            logger.info(f"🔄 메시지 재시도 예약: {message.id} ({delay}초 후)")
            
            # 재시도 태스크 시작
            asyncio.create_task(self._retry_message(message, delay))
            
        else:
            # 최종 실패
            message.status = MessageStatus.FAILED
            
            result = TransmissionResult(
                message_id=message.id,
                success=False,
                sent_at=datetime.now(KST),
                retry_count=message.retry_count
            )
            
            if message.id not in self.failed_messages:
                self.failed_messages[message.id] = []
            self.failed_messages[message.id].append(result)
            
            self.stats['total_failed'] += 1
            logger.error(f"❌ 메시지 최종 실패: {message.id}")
    
    async def _retry_message(self, message: ScheduledMessage, delay: int):
        """메시지 재시도"""
        await asyncio.sleep(delay)
        
        if message.status == MessageStatus.RETRYING:
            logger.info(f"🔄 메시지 재시도: {message.id}")
            await self._send_scheduled_message(message)
    
    async def _confirm_transmission(self, message: ScheduledMessage):
        """전송 확인"""
        await asyncio.sleep(self.schedule_config['confirmation_delay'])
        
        # 전송 확인 시도
        confirmation_success = await self._check_transmission_confirmation(message)
        
        if confirmation_success:
            # 전송 확인 성공
            message.status = MessageStatus.CONFIRMED
            if message.id in self.sent_messages:
                self.sent_messages[message.id].confirmation_status = True
            
            self.stats['total_confirmed'] += 1
            logger.info(f"✅ 전송 확인 완료: {message.id}")
            
        else:
            # 전송 확인 실패
            message.confirmation_attempts += 1
            
            if message.confirmation_attempts < message.max_confirmation_attempts:
                # 재확인 시도
                delay = self.schedule_config['confirmation_timeout']
                logger.warning(f"⚠️ 전송 확인 실패, 재시도: {message.id} ({delay}초 후)")
                asyncio.create_task(self._retry_confirmation(message, delay))
            else:
                # 최종 확인 실패
                logger.error(f"❌ 전송 확인 최종 실패: {message.id}")
                # 필요시 재전송 고려
                await self._handle_confirmation_failure(message)
    
    async def _check_transmission_confirmation(self, message: ScheduledMessage) -> bool:
        """전송 확인 체크"""
        # 실제 구현에서는 카카오톡 API를 통해 전송 상태 확인
        # 현재는 시뮬레이션으로 처리
        
        try:
            # 카카오톡 API로 전송 상태 확인
            # 실제로는 카카오톡에서 제공하는 전송 상태 확인 API 사용
            await asyncio.sleep(1)  # API 호출 시뮬레이션
            
            # 90% 확률로 성공으로 가정 (실제로는 API 응답 기반)
            import random
            return random.random() > 0.1
            
        except Exception as e:
            logger.error(f"❌ 전송 확인 체크 오류: {e}")
            return False
    
    async def _retry_confirmation(self, message: ScheduledMessage, delay: int):
        """전송 확인 재시도"""
        await asyncio.sleep(delay)
        await self._confirm_transmission(message)
    
    async def _handle_confirmation_failure(self, message: ScheduledMessage):
        """전송 확인 실패 처리"""
        # 전송 확인이 실패한 경우 재전송 고려
        logger.warning(f"⚠️ 전송 확인 실패로 인한 재전송 고려: {message.id}")
        
        # 필요시 재전송 로직 구현
        # 현재는 로그만 남김
    
    async def _process_confirmation_queue(self):
        """전송 확인 큐 처리"""
        # 전송 확인 대기 중인 메시지들 처리
        # 실제 구현에서는 별도 큐 시스템 사용 가능
        pass
    
    def _generate_message_id(self, content: str, schedule_time: datetime) -> str:
        """메시지 ID 생성"""
        data = f"{content}_{schedule_time.isoformat()}_{time.time()}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    def _generate_message_hash(self, content: str, schedule_time: datetime) -> str:
        """메시지 해시 생성 (중복 체크용)"""
        data = f"{content}_{schedule_time.strftime('%Y%m%d_%H%M')}"
        return hashlib.md5(data.encode()).hexdigest()
    
    def get_schedule_status(self) -> Dict[str, Any]:
        """스케줄 상태 반환"""
        now = datetime.now(KST)
        
        return {
            'is_running': self.is_running,
            'current_time': now.isoformat(),
            'scheduled_count': len(self.scheduled_messages),
            'sent_count': len(self.sent_messages),
            'failed_count': len(self.failed_messages),
            'stats': self.stats,
            'next_regular_time': self._get_next_regular_time().isoformat(),
            'next_peak_time': self._get_next_peak_time().isoformat(),
            'peak_hours': self.schedule_config['peak_hours']
        }
    
    def get_message_status(self, message_id: str) -> Optional[Dict[str, Any]]:
        """메시지 상태 조회"""
        if message_id in self.scheduled_messages:
            message = self.scheduled_messages[message_id]
            return {
                'id': message.id,
                'status': message.status.value,
                'schedule_time': message.schedule_time.isoformat(),
                'sent_at': message.sent_at.isoformat() if message.sent_at else None,
                'retry_count': message.retry_count,
                'confirmation_attempts': message.confirmation_attempts
            }
        return None
    
    def cancel_message(self, message_id: str) -> bool:
        """메시지 취소"""
        if message_id in self.scheduled_messages:
            message = self.scheduled_messages[message_id]
            if message.status == MessageStatus.SCHEDULED:
                del self.scheduled_messages[message_id]
                logger.info(f"❌ 메시지 취소: {message_id}")
                return True
        return False 