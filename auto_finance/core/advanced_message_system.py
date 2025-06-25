"""
📤 고도화된 메시지 전송 시스템
재시도 로직, 상태 추적, 다중 채널 백업을 통한 안정적인 메시지 전송
"""

import asyncio
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import requests

# 유틸리티 임포트
from auto_finance.utils.logger import setup_logger
from auto_finance.utils.error_handler import ErrorHandler
from auto_finance.utils.cache_manager import cache_manager

logger = setup_logger(__name__)

class MessageStatus(Enum):
    """메시지 상태"""
    PENDING = "pending"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"
    RETRYING = "retrying"
    EXPIRED = "expired"

class MessagePriority(Enum):
    """메시지 우선순위"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

@dataclass
class MessageRequest:
    """메시지 요청 데이터"""
    id: str
    content: str
    channels: List[str]
    priority: MessagePriority = MessagePriority.NORMAL
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MessageResult:
    """메시지 전송 결과"""
    message_id: str
    channel: str
    status: MessageStatus
    success: bool
    sent_at: datetime
    processing_time: float
    error_message: Optional[str] = None
    retry_count: int = 0

class AdvancedMessageSystem:
    """고도화된 메시지 전송 시스템"""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        
        # 메시지 큐 및 상태 관리
        self.message_queue: List[MessageRequest] = []
        self.sent_messages: Dict[str, MessageResult] = {}
        self.failed_messages: Dict[str, List[MessageResult]] = {}
        
        # 채널별 클라이언트
        self.channel_clients: Dict[str, Callable] = {}
        self.channel_priorities: Dict[str, int] = {}
        
        # 통계
        self.stats = {
            'total_messages': 0,
            'successful_sends': 0,
            'failed_sends': 0,
            'retry_count': 0,
            'average_processing_time': 0.0,
            'channel_stats': {}
        }
        
        # 설정
        self.max_queue_size = 1000
        self.retry_delays = [1, 5, 15, 30, 60]  # 재시도 간격 (초)
        self.message_ttl = 3600  # 메시지 TTL (초)
        
        # 초기화
        self._setup_channel_clients()
        logger.info("📤 고도화된 메시지 시스템 초기화 완료")
    
    def _setup_channel_clients(self):
        """채널별 클라이언트 설정"""
        self.channel_clients = {
            'kakao': self._send_to_kakao,
            'telegram': self._send_to_telegram,
            'slack': self._send_to_slack,
            'discord': self._send_to_discord,
            'email': self._send_to_email,
            'console': self._send_to_console
        }
        
        # 채널 우선순위 설정
        self.channel_priorities = {
            'kakao': 1,
            'telegram': 2,
            'slack': 3,
            'discord': 4,
            'email': 5,
            'console': 6
        }
    
    async def send_message(self, content: str, channels: List[str], 
                          priority: MessagePriority = MessagePriority.NORMAL,
                          metadata: Optional[Dict[str, Any]] = None) -> str:
        """메시지 전송 요청"""
        message_id = self._generate_message_id(content, channels)
        
        # 만료 시간 설정
        expires_at = datetime.now() + timedelta(seconds=self.message_ttl)
        
        # 메시지 요청 생성
        request = MessageRequest(
            id=message_id,
            content=content,
            channels=channels,
            priority=priority,
            expires_at=expires_at,
            metadata=metadata or {}
        )
        
        # 큐에 추가
        await self._add_to_queue(request)
        
        logger.info(f"📨 메시지 전송 요청: {message_id} (채널: {channels})")
        return message_id
    
    async def _add_to_queue(self, request: MessageRequest):
        """메시지 큐에 추가"""
        if len(self.message_queue) >= self.max_queue_size:
            # 가장 낮은 우선순위 메시지 제거
            self.message_queue.sort(key=lambda x: x.priority.value)
            removed = self.message_queue.pop(0)
            logger.warning(f"⚠️ 큐 가득참, 메시지 제거: {removed.id}")
        
        # 우선순위에 따라 정렬하여 추가
        self.message_queue.append(request)
        self.message_queue.sort(key=lambda x: x.priority.value, reverse=True)
    
    async def process_message_queue(self):
        """메시지 큐 처리"""
        while self.message_queue:
            request = self.message_queue.pop(0)
            
            # 만료 체크
            if request.expires_at and datetime.now() > request.expires_at:
                logger.warning(f"⚠️ 메시지 만료: {request.id}")
                continue
            
            # 메시지 전송
            await self._send_message(request)
            
            # 처리 간격
            await asyncio.sleep(0.1)
    
    async def _send_message(self, request: MessageRequest):
        """개별 메시지 전송"""
        start_time = time.time()
        
        # 채널별 전송 시도
        for channel in request.channels:
            if channel not in self.channel_clients:
                logger.warning(f"⚠️ 지원하지 않는 채널: {channel}")
                continue
            
            try:
                # 전송 시도
                success = await self._send_to_channel(request, channel)
                
                if success:
                    # 성공 시 다른 채널로 전송 중단
                    processing_time = time.time() - start_time
                    result = MessageResult(
                        message_id=request.id,
                        channel=channel,
                        status=MessageStatus.SENT,
                        success=True,
                        sent_at=datetime.now(),
                        processing_time=processing_time
                    )
                    
                    self.sent_messages[request.id] = result
                    self._update_stats(True, processing_time, channel)
                    
                    logger.info(f"✅ 메시지 전송 성공: {request.id} → {channel}")
                    return
                
            except Exception as e:
                logger.error(f"❌ 채널 전송 실패: {channel} - {e}")
                continue
        
        # 모든 채널 실패 시 재시도 로직
        await self._handle_send_failure(request, start_time)
    
    async def _send_to_channel(self, request: MessageRequest, channel: str) -> bool:
        """채널별 전송"""
        client = self.channel_clients[channel]
        
        # 재시도 로직
        for attempt in range(request.max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(client):
                    success = await client(request.content, request.metadata)
                else:
                    success = client(request.content, request.metadata)
                
                if success:
                    return True
                
            except Exception as e:
                logger.warning(f"⚠️ {channel} 전송 시도 {attempt + 1} 실패: {e}")
                
                if attempt < request.max_retries:
                    delay = self.retry_delays[min(attempt, len(self.retry_delays) - 1)]
                    await asyncio.sleep(delay)
        
        return False
    
    async def _handle_send_failure(self, request: MessageRequest, start_time: float):
        """전송 실패 처리"""
        processing_time = time.time() - start_time
        
        # 실패 결과 기록
        result = MessageResult(
            message_id=request.id,
            channel="all",
            status=MessageStatus.FAILED,
            success=False,
            sent_at=datetime.now(),
            processing_time=processing_time,
            error_message="모든 채널 전송 실패",
            retry_count=request.retry_count
        )
        
        # 재시도 가능 여부 확인
        if request.retry_count < request.max_retries:
            request.retry_count += 1
            request.priority = MessagePriority.HIGH  # 재시도 시 우선순위 상승
            
            # 지연 후 재시도
            delay = self.retry_delays[min(request.retry_count - 1, len(self.retry_delays) - 1)]
            await asyncio.sleep(delay)
            
            # 큐에 다시 추가
            await self._add_to_queue(request)
            
            logger.info(f"🔄 메시지 재시도: {request.id} (시도 {request.retry_count})")
        else:
            # 최종 실패
            if request.id not in self.failed_messages:
                self.failed_messages[request.id] = []
            self.failed_messages[request.id].append(result)
            
            self._update_stats(False, processing_time, "all")
            logger.error(f"❌ 메시지 최종 실패: {request.id}")
    
    # 채널별 전송 메서드들
    async def _send_to_kakao(self, content: str, metadata: Dict[str, Any]) -> bool:
        """카카오톡 전송"""
        try:
            # 카카오 API 설정
            access_token = metadata.get('kakao_token') or self._get_env_token('KAKAO_ACCESS_TOKEN')
            if not access_token:
                return False
            
            url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
            headers = {
                "Authorization": f"Bearer {access_token}",
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
            
            response = requests.post(url, headers=headers, data=data, timeout=10)
            return response.status_code == 200
                    
        except Exception as e:
            logger.error(f"❌ 카카오톡 전송 오류: {e}")
            return False
    
    async def _send_to_telegram(self, content: str, metadata: Dict[str, Any]) -> bool:
        """텔레그램 전송"""
        try:
            token = metadata.get('telegram_token') or self._get_env_token('TELEGRAM_BOT_TOKEN')
            chat_id = metadata.get('telegram_chat_id') or self._get_env_token('TELEGRAM_CHAT_ID')
            
            if not token or not chat_id:
                return False
            
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': content,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
                    
        except Exception as e:
            logger.error(f"❌ 텔레그램 전송 오류: {e}")
            return False
    
    async def _send_to_slack(self, content: str, metadata: Dict[str, Any]) -> bool:
        """슬랙 전송"""
        try:
            webhook_url = metadata.get('slack_webhook') or self._get_env_token('SLACK_WEBHOOK_URL')
            if not webhook_url:
                return False
            
            payload = {
                "text": "🚚 자동 알림",
                "blocks": [{"type": "section", "text": {"type": "mrkdwn", "text": content}}]
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            return response.status_code == 200
                    
        except Exception as e:
            logger.error(f"❌ 슬랙 전송 오류: {e}")
            return False
    
    async def _send_to_discord(self, content: str, metadata: Dict[str, Any]) -> bool:
        """디스코드 전송"""
        try:
            webhook_url = metadata.get('discord_webhook') or self._get_env_token('DISCORD_WEBHOOK_URL')
            if not webhook_url:
                return False
            
            payload = {
                "content": content,
                "username": "Auto Finance Bot"
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            return response.status_code == 200
                    
        except Exception as e:
            logger.error(f"❌ 디스코드 전송 오류: {e}")
            return False
    
    async def _send_to_email(self, content: str, metadata: Dict[str, Any]) -> bool:
        """이메일 전송 (구현 예정)"""
        logger.warning("⚠️ 이메일 전송은 아직 구현되지 않았습니다")
        return False
    
    def _send_to_console(self, content: str, metadata: Dict[str, Any]) -> bool:
        """콘솔 출력 (백업용)"""
        try:
            print("=" * 60)
            print("📱 자동 알림 메시지")
            print("=" * 60)
            print(content)
            print("=" * 60)
            return True
        except Exception as e:
            logger.error(f"❌ 콘솔 출력 오류: {e}")
            return False
    
    def _get_env_token(self, key: str) -> Optional[str]:
        """환경변수에서 토큰 가져오기"""
        import os
        token = os.getenv(key)
        if token and token.startswith('YOUR_'):
            return None
        return token
    
    def _generate_message_id(self, content: str, channels: List[str]) -> str:
        """메시지 ID 생성"""
        data = f"{content}_{channels}_{datetime.now().isoformat()}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    def _update_stats(self, success: bool, processing_time: float, channel: str):
        """통계 업데이트"""
        self.stats['total_messages'] += 1
        
        if success:
            self.stats['successful_sends'] += 1
        else:
            self.stats['failed_sends'] += 1
        
        # 평균 처리 시간 업데이트
        total_time = self.stats['average_processing_time'] * (self.stats['total_messages'] - 1)
        self.stats['average_processing_time'] = (total_time + processing_time) / self.stats['total_messages']
        
        # 채널별 통계
        if channel not in self.stats['channel_stats']:
            self.stats['channel_stats'][channel] = {'success': 0, 'failed': 0}
        
        if success:
            self.stats['channel_stats'][channel]['success'] += 1
        else:
            self.stats['channel_stats'][channel]['failed'] += 1
    
    def get_message_status(self, message_id: str) -> Optional[MessageResult]:
        """메시지 상태 조회"""
        return self.sent_messages.get(message_id)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """시스템 통계 반환"""
        return {
            'stats': self.stats,
            'queue_size': len(self.message_queue),
            'sent_count': len(self.sent_messages),
            'failed_count': len(self.failed_messages),
            'success_rate': (self.stats['successful_sends'] / self.stats['total_messages'] * 100) 
                           if self.stats['total_messages'] > 0 else 0
        }
    
    async def cleanup_expired_messages(self):
        """만료된 메시지 정리"""
        now = datetime.now()
        expired_count = 0
        
        # 큐에서 만료된 메시지 제거
        self.message_queue = [
            msg for msg in self.message_queue 
            if not msg.expires_at or msg.expires_at > now
        ]
        
        # 오래된 성공 메시지 정리 (24시간)
        cutoff_time = now - timedelta(hours=24)
        self.sent_messages = {
            k: v for k, v in self.sent_messages.items() 
            if v.sent_at > cutoff_time
        }
        
        logger.info(f"🧹 만료된 메시지 정리 완료: {expired_count}개")
    
    async def run_continuous_processing(self):
        """연속 메시지 처리"""
        logger.info("🔄 연속 메시지 처리 시작")
        
        while True:
            try:
                # 메시지 큐 처리
                await self.process_message_queue()
                
                # 만료된 메시지 정리
                await self.cleanup_expired_messages()
                
                # 대기
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ 메시지 처리 중 오류: {e}")
                await asyncio.sleep(5) 