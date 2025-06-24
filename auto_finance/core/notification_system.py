"""
🔔 고도화된 알림 시스템
다중 채널 지원, 스마트 필터링, 실시간 모니터링, 통계 관리
"""

import asyncio
import json
import smtplib
import requests
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from auto_finance.utils.logger import setup_logger
from auto_finance.utils.error_handler import retry_on_error, ErrorHandler
from auto_finance.utils.cache_manager import cache_manager
from auto_finance.config.settings import NOTIFICATION_CONFIG

logger = setup_logger(__name__)

@dataclass
class NotificationMessage:
    """알림 메시지"""
    title: str
    content: str
    priority: str  # low, normal, high, urgent
    category: str  # system, news, financial, error
    channels: List[str]  # email, slack, telegram, etc.
    recipients: List[str]
    metadata: Dict[str, Any]
    created_at: str

@dataclass
class NotificationResult:
    """알림 전송 결과"""
    message_id: str
    channel: str
    success: bool
    recipient: str
    sent_at: str
    error_message: Optional[str]
    processing_time: float

class NotificationSystem:
    """고도화된 알림 시스템"""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        
        # 설정 로드
        self.channels = NOTIFICATION_CONFIG.get('channels', {})
        self.templates = NOTIFICATION_CONFIG.get('templates', {})
        self.rate_limits = NOTIFICATION_CONFIG.get('rate_limits', {})
        
        # 알림 통계
        self.stats = {
            'total_notifications': 0,
            'successful_notifications': 0,
            'failed_notifications': 0,
            'channel_stats': {},
            'priority_stats': {}
        }
        
        # 채널별 클라이언트
        self.clients = {}
        
        # 알림 큐
        self.notification_queue = asyncio.Queue()
        
        logger.info(f"🔔 알림 시스템 초기화: {len(self.channels)}개 채널")
    
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        await self.cleanup()
    
    async def initialize(self):
        """알림 시스템 초기화"""
        try:
            # 채널별 클라이언트 초기화
            for channel, config in self.channels.items():
                if config.get('enabled', False):
                    client = await self._create_channel_client(channel, config)
                    if client:
                        self.clients[channel] = client
                        logger.info(f"✅ {channel} 클라이언트 초기화 완료")
            
            # 알림 처리 태스크 시작
            asyncio.create_task(self._process_notification_queue())
            
            logger.info(f"🔔 알림 시스템 초기화 완료: {len(self.clients)}개 채널")
            
        except Exception as e:
            logger.error(f"❌ 알림 시스템 초기화 실패: {e}")
            raise
    
    async def cleanup(self):
        """리소스 정리"""
        try:
            # 클라이언트 정리
            for channel, client in self.clients.items():
                if hasattr(client, 'close'):
                    await client.close()
            
            logger.info("🧹 알림 시스템 정리 완료")
            
        except Exception as e:
            logger.error(f"❌ 알림 시스템 정리 실패: {e}")
    
    async def _create_channel_client(self, channel: str, config: Dict[str, Any]):
        """채널별 클라이언트 생성"""
        try:
            if channel == "email":
                return await self._create_email_client(config)
            elif channel == "slack":
                return await self._create_slack_client(config)
            elif channel == "telegram":
                return await self._create_telegram_client(config)
            elif channel == "discord":
                return await self._create_discord_client(config)
            else:
                logger.warning(f"⚠️ 지원하지 않는 채널: {channel}")
                return None
                
        except Exception as e:
            logger.error(f"❌ {channel} 클라이언트 생성 실패: {e}")
            return None
    
    async def _create_email_client(self, config: Dict[str, Any]):
        """이메일 클라이언트 생성"""
        try:
            class EmailClient:
                def __init__(self, config):
                    self.smtp_server = config.get('smtp_server')
                    self.smtp_port = config.get('smtp_port', 587)
                    self.username = config.get('username')
                    self.password = config.get('password')
                    self.from_email = config.get('from_email')
                
                async def send_message(self, to_email, subject, content):
                    try:
                        msg = MIMEMultipart()
                        msg['From'] = self.from_email
                        msg['To'] = to_email
                        msg['Subject'] = subject
                        
                        msg.attach(MIMEText(content, 'html'))
                        
                        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                            server.starttls()
                            server.login(self.username, self.password)
                            server.send_message(msg)
                        
                        return {'success': True}
                    except Exception as e:
                        return {'success': False, 'error': str(e)}
                
                async def close(self):
                    pass
            
            return EmailClient(config)
            
        except Exception as e:
            logger.error(f"❌ 이메일 클라이언트 생성 실패: {e}")
            return None
    
    async def _create_slack_client(self, config: Dict[str, Any]):
        """슬랙 클라이언트 생성"""
        try:
            class SlackClient:
                def __init__(self, config):
                    self.webhook_url = config.get('webhook_url')
                    self.channel = config.get('channel', '#general')
                
                async def send_message(self, content, title=None):
                    try:
                        payload = {
                            'channel': self.channel,
                            'text': content
                        }
                        
                        if title:
                            payload['attachments'] = [{
                                'title': title,
                                'text': content,
                                'color': 'good'
                            }]
                        
                        response = requests.post(self.webhook_url, json=payload)
                        response.raise_for_status()
                        
                        return {'success': True}
                    except Exception as e:
                        return {'success': False, 'error': str(e)}
                
                async def close(self):
                    pass
            
            return SlackClient(config)
            
        except Exception as e:
            logger.error(f"❌ 슬랙 클라이언트 생성 실패: {e}")
            return None
    
    async def _create_telegram_client(self, config: Dict[str, Any]):
        """텔레그램 클라이언트 생성"""
        try:
            class TelegramClient:
                def __init__(self, config):
                    self.bot_token = config.get('bot_token')
                    self.chat_id = config.get('chat_id')
                    self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
                
                async def send_message(self, content, title=None):
                    try:
                        message = f"**{title}**\n\n{content}" if title else content
                        
                        payload = {
                            'chat_id': self.chat_id,
                            'text': message,
                            'parse_mode': 'Markdown'
                        }
                        
                        response = requests.post(f"{self.api_url}/sendMessage", json=payload)
                        response.raise_for_status()
                        
                        return {'success': True}
                    except Exception as e:
                        return {'success': False, 'error': str(e)}
                
                async def close(self):
                    pass
            
            return TelegramClient(config)
            
        except Exception as e:
            logger.error(f"❌ 텔레그램 클라이언트 생성 실패: {e}")
            return None
    
    async def _create_discord_client(self, config: Dict[str, Any]):
        """디스코드 클라이언트 생성"""
        try:
            class DiscordClient:
                def __init__(self, config):
                    self.webhook_url = config.get('webhook_url')
                    self.username = config.get('username', 'Auto Finance Bot')
                
                async def send_message(self, content, title=None):
                    try:
                        payload = {
                            'username': self.username,
                            'content': content
                        }
                        
                        if title:
                            payload['embeds'] = [{
                                'title': title,
                                'description': content,
                                'color': 0x00ff00
                            }]
                        
                        response = requests.post(self.webhook_url, json=payload)
                        response.raise_for_status()
                        
                        return {'success': True}
                    except Exception as e:
                        return {'success': False, 'error': str(e)}
                
                async def close(self):
                    pass
            
            return DiscordClient(config)
            
        except Exception as e:
            logger.error(f"❌ 디스코드 클라이언트 생성 실패: {e}")
            return None
    
    async def send_notification(self, message: NotificationMessage) -> List[NotificationResult]:
        """알림 전송"""
        results = []
        
        for channel in message.channels:
            if channel not in self.clients:
                logger.warning(f"⚠️ 채널 클라이언트 없음: {channel}")
                continue
            
            client = self.clients[channel]
            
            for recipient in message.recipients:
                result = await self._send_to_channel(
                    client, channel, message, recipient
                )
                results.append(result)
        
        return results
    
    @retry_on_error(max_retries=3, delay=2.0)
    async def _send_to_channel(self, client, channel: str, message: NotificationMessage, 
                              recipient: str) -> NotificationResult:
        """채널별 알림 전송"""
        start_time = datetime.now()
        
        try:
            # 템플릿 적용
            content = self._apply_template(message, channel)
            
            # 채널별 전송
            if channel == "email":
                result = await client.send_message(
                    recipient, message.title, content
                )
            else:
                result = await client.send_message(content, message.title)
            
            # 결과 생성
            processing_time = (datetime.now() - start_time).total_seconds()
            notification_result = NotificationResult(
                message_id=f"{message.created_at}_{channel}_{recipient}",
                channel=channel,
                success=result.get('success', False),
                recipient=recipient,
                sent_at=datetime.now().isoformat(),
                error_message=result.get('error'),
                processing_time=processing_time
            )
            
            # 통계 업데이트
            self._update_statistics(notification_result, message.priority)
            
            if notification_result.success:
                logger.info(f"✅ 알림 전송 완료: {channel} → {recipient}")
            else:
                logger.error(f"❌ 알림 전송 실패: {channel} → {recipient}")
            
            return notification_result
            
        except Exception as e:
            self.error_handler.handle_error(e, f"알림 전송 실패 ({channel})")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            return NotificationResult(
                message_id=f"{message.created_at}_{channel}_{recipient}",
                channel=channel,
                success=False,
                recipient=recipient,
                sent_at=datetime.now().isoformat(),
                error_message=str(e),
                processing_time=processing_time
            )
    
    def _apply_template(self, message: NotificationMessage, channel: str) -> str:
        """템플릿 적용"""
        template = self.templates.get(channel, "{{content}}")
        
        # 변수 치환
        content = template.replace("{{title}}", message.title)
        content = content.replace("{{content}}", message.content)
        content = content.replace("{{priority}}", message.priority)
        content = content.replace("{{category}}", message.category)
        content = content.replace("{{timestamp}}", message.created_at)
        
        return content
    
    async def _process_notification_queue(self):
        """알림 큐 처리"""
        while True:
            try:
                message = await self.notification_queue.get()
                await self.send_notification(message)
                self.notification_queue.task_done()
                
            except Exception as e:
                logger.error(f"❌ 알림 큐 처리 실패: {e}")
                await asyncio.sleep(1)
    
    async def queue_notification(self, message: NotificationMessage):
        """알림을 큐에 추가"""
        await self.notification_queue.put(message)
        logger.info(f"📬 알림 큐에 추가: {message.title}")
    
    async def send_immediate_notification(self, title: str, content: str, 
                                        priority: str = "normal", 
                                        channels: List[str] = None,
                                        recipients: List[str] = None) -> List[NotificationResult]:
        """즉시 알림 전송"""
        if channels is None:
            channels = list(self.clients.keys())
        
        if recipients is None:
            recipients = ["default"]
        
        message = NotificationMessage(
            title=title,
            content=content,
            priority=priority,
            category="system",
            channels=channels,
            recipients=recipients,
            metadata={},
            created_at=datetime.now().isoformat()
        )
        
        return await self.send_notification(message)
    
    def _update_statistics(self, result: NotificationResult, priority: str):
        """통계 업데이트"""
        self.stats['total_notifications'] += 1
        
        if result.success:
            self.stats['successful_notifications'] += 1
        else:
            self.stats['failed_notifications'] += 1
        
        # 채널별 통계
        channel = result.channel
        if channel not in self.stats['channel_stats']:
            self.stats['channel_stats'][channel] = {
                'total': 0,
                'successful': 0,
                'failed': 0
            }
        
        self.stats['channel_stats'][channel]['total'] += 1
        if result.success:
            self.stats['channel_stats'][channel]['successful'] += 1
        else:
            self.stats['channel_stats'][channel]['failed'] += 1
        
        # 우선순위별 통계
        if priority not in self.stats['priority_stats']:
            self.stats['priority_stats'][priority] = {
                'total': 0,
                'successful': 0,
                'failed': 0
            }
        
        self.stats['priority_stats'][priority]['total'] += 1
        if result.success:
            self.stats['priority_stats'][priority]['successful'] += 1
        else:
            self.stats['priority_stats'][priority]['failed'] += 1
    
    def get_notification_summary(self, results: List[NotificationResult]) -> Dict[str, Any]:
        """알림 결과 요약"""
        if not results:
            return {}
        
        summary = {
            'total_notifications': len(results),
            'successful_notifications': len([r for r in results if r.success]),
            'failed_notifications': len([r for r in results if not r.success]),
            'success_rate': len([r for r in results if r.success]) / len(results) * 100,
            'channel_breakdown': {},
            'average_processing_time': sum(r.processing_time for r in results) / len(results),
            'timestamp': datetime.now().isoformat()
        }
        
        # 채널별 분석
        for result in results:
            channel = result.channel
            if channel not in summary['channel_breakdown']:
                summary['channel_breakdown'][channel] = {
                    'total': 0,
                    'successful': 0,
                    'failed': 0
                }
            
            summary['channel_breakdown'][channel]['total'] += 1
            if result.success:
                summary['channel_breakdown'][channel]['successful'] += 1
            else:
                summary['channel_breakdown'][channel]['failed'] += 1
        
        return summary
    
    def save_results(self, results: List[NotificationResult], file_path: str = "data/notification_results.json"):
        """알림 결과 저장"""
        try:
            data = {
                'results': [result.__dict__ for result in results],
                'summary': self.get_notification_summary(results),
                'statistics': self.stats,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"💾 알림 결과 저장: {file_path}")
            
        except Exception as e:
            logger.error(f"❌ 알림 결과 저장 실패: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """알림 통계 반환"""
        return {
            **self.stats,
            'error_statistics': self.error_handler.get_statistics(),
            'success_rate': (
                self.stats['successful_notifications'] / self.stats['total_notifications'] * 100
                if self.stats['total_notifications'] > 0 else 0.0
            ),
            'timestamp': datetime.now().isoformat()
        }

# 사용 예시
async def main():
    """알림 시스템 테스트"""
    async with NotificationSystem() as notification_system:
        # 즉시 알림 전송
        results = await notification_system.send_immediate_notification(
            title="시스템 테스트",
            content="알림 시스템이 정상적으로 작동하고 있습니다.",
            priority="normal",
            channels=["slack"],
            recipients=["#general"]
        )
        
        print(f"🔔 알림 전송 결과: {len(results)}개")
        for result in results:
            status = "✅ 성공" if result.success else "❌ 실패"
            print(f"- {result.channel} → {result.recipient}: {status}")
        
        # 큐에 알림 추가
        message = NotificationMessage(
            title="큐 테스트",
            content="큐를 통한 알림 전송 테스트입니다.",
            priority="low",
            category="test",
            channels=["slack"],
            recipients=["#test"],
            metadata={},
            created_at=datetime.now().isoformat()
        )
        
        await notification_system.queue_notification(message)
        
        # 잠시 대기 후 결과 확인
        await asyncio.sleep(2)
        
        stats = notification_system.get_statistics()
        print(f"📊 통계: {stats}")

if __name__ == "__main__":
    asyncio.run(main()) 