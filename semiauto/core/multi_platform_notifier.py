#!/usr/bin/env python3
"""
🎯 다중 플랫폼 확장 시스템
- 슬랙, 디스코드, 텔레그램, 이메일 지원
- 플랫폼별 맞춤형 메시지 포맷
- 우선순위 기반 알림 시스템
- 백업 플랫폼 자동 전환
"""

import json
import logging
import smtplib
from abc import ABC, abstractmethod
from datetime import datetime
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import Dict, List, Optional, Union
import requests
import pytz

logger = logging.getLogger(__name__)
KST = pytz.timezone('Asia/Seoul')

class NotificationPlatform(ABC):
    """알림 플랫폼 기본 클래스"""
    
    @abstractmethod
    def send_message(self, message: str, title: str = "", priority: str = "normal") -> bool:
        """메시지 전송"""
        pass
    
    @abstractmethod
    def format_grider_data(self, data: Dict) -> str:
        """G라이더 데이터 포맷팅"""
        pass

class SlackNotifier(NotificationPlatform):
    """슬랙 알림"""
    
    def __init__(self, webhook_url: str, channel: str = "#grider-alerts"):
        self.webhook_url = webhook_url
        self.channel = channel
        self.platform_name = "Slack"
    
    def send_message(self, message: str, title: str = "", priority: str = "normal") -> bool:
        """슬랙 메시지 전송"""
        try:
            color = {"high": "danger", "medium": "warning", "normal": "good"}.get(priority, "good")
            
            payload = {
                "channel": self.channel,
                "attachments": [{
                    "color": color,
                    "title": title or "🎯 G라이더 자동화 알림",
                    "text": message,
                    "footer": "G라이더 자동화 시스템",
                    "ts": int(datetime.now().timestamp())
                }]
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✅ 슬랙 메시지 전송 성공")
                return True
            else:
                logger.error(f"❌ 슬랙 메시지 전송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 슬랙 알림 오류: {e}")
            return False
    
    def format_grider_data(self, data: Dict) -> str:
        """슬랙용 G라이더 데이터 포맷팅"""
        now = datetime.now(KST)
        
        # 기본 정보
        message = f"""🚚 *G라이더 현황 리포트*
📅 {now.strftime('%Y-%m-%d %H:%M')} 기준

📊 *총 현황*
• 총 점수: `{data.get('total_score', 0):,}점`
• 총 완료: `{data.get('total_completed', 0):,}건`

🎯 *미션 현황*"""
        
        # 미션별 상세
        missions = data.get('missions', {})
        for mission_name, mission_data in missions.items():
            current = mission_data.get('current', 0)
            target = mission_data.get('target', 0)
            percentage = (current / target * 100) if target > 0 else 0
            
            progress_bar = self._create_progress_bar(percentage)
            message += f"\n• {mission_name}: `{current:,}/{target:,}` {progress_bar} {percentage:.1f}%"
        
        # 라이더 정보 (상위 5명)
        riders = data.get('riders', [])
        active_riders = [r for r in riders if r.get('completed', 0) > 0]
        
        if active_riders:
            top_riders = sorted(active_riders, key=lambda x: x.get('completed', 0), reverse=True)[:5]
            message += f"\n\n🏆 *TOP 라이더*"
            
            for i, rider in enumerate(top_riders, 1):
                name = rider.get('name', '이름없음')
                completed = rider.get('completed', 0)
                acceptance_rate = rider.get('acceptance_rate', 0)
                message += f"\n{i}. {name}: `{completed:,}건` (수락률 {acceptance_rate:.1f}%)"
        
        return message
    
    def _create_progress_bar(self, percentage: float, length: int = 10) -> str:
        """진행률 바 생성"""
        filled = int(percentage / 100 * length)
        return "█" * filled + "░" * (length - filled)

class DiscordNotifier(NotificationPlatform):
    """디스코드 알림"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.platform_name = "Discord"
    
    def send_message(self, message: str, title: str = "", priority: str = "normal") -> bool:
        """디스코드 메시지 전송"""
        try:
            color = {"high": 0xff0000, "medium": 0xffa500, "normal": 0x00ff00}.get(priority, 0x00ff00)
            
            embed = {
                "title": title or "🎯 G라이더 자동화 알림",
                "description": message,
                "color": color,
                "footer": {"text": "G라이더 자동화 시스템"},
                "timestamp": datetime.now().isoformat()
            }
            
            payload = {"embeds": [embed]}
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            
            if response.status_code == 204:
                logger.info(f"✅ 디스코드 메시지 전송 성공")
                return True
            else:
                logger.error(f"❌ 디스코드 메시지 전송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 디스코드 알림 오류: {e}")
            return False
    
    def format_grider_data(self, data: Dict) -> str:
        """디스코드용 G라이더 데이터 포맷팅"""
        now = datetime.now(KST)
        
        message = f"""🚚 **G라이더 현황 리포트**
📅 {now.strftime('%Y-%m-%d %H:%M')} 기준

```
📊 총 현황
├─ 총 점수: {data.get('total_score', 0):,}점
└─ 총 완료: {data.get('total_completed', 0):,}건
```

🎯 **미션 현황**
```"""
        
        missions = data.get('missions', {})
        for mission_name, mission_data in missions.items():
            current = mission_data.get('current', 0)
            target = mission_data.get('target', 0)
            percentage = (current / target * 100) if target > 0 else 0
            message += f"\n• {mission_name}: {current:,}/{target:,} ({percentage:.1f}%)"
        
        message += "```"
        
        # 라이더 정보
        riders = data.get('riders', [])
        active_riders = [r for r in riders if r.get('completed', 0) > 0]
        
        if active_riders:
            message += f"\n\n🏆 **TOP 라이더** ({len(active_riders)}명 활동중)"
            top_riders = sorted(active_riders, key=lambda x: x.get('completed', 0), reverse=True)[:3]
            
            for i, rider in enumerate(top_riders, 1):
                name = rider.get('name', '이름없음')
                completed = rider.get('completed', 0)
                message += f"\n`{i}.` **{name}** - {completed:,}건"
        
        return message

class TelegramNotifier(NotificationPlatform):
    """텔레그램 알림"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.platform_name = "Telegram"
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    def send_message(self, message: str, title: str = "", priority: str = "normal") -> bool:
        """텔레그램 메시지 전송"""
        try:
            priority_emoji = {"high": "🚨", "medium": "⚠️", "normal": "ℹ️"}.get(priority, "ℹ️")
            full_message = f"{priority_emoji} {title}\n\n{message}" if title else message
            
            payload = {
                "chat_id": self.chat_id,
                "text": full_message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(self.api_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✅ 텔레그램 메시지 전송 성공")
                return True
            else:
                logger.error(f"❌ 텔레그램 메시지 전송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 텔레그램 알림 오류: {e}")
            return False
    
    def format_grider_data(self, data: Dict) -> str:
        """텔레그램용 G라이더 데이터 포맷팅"""
        now = datetime.now(KST)
        
        message = f"""🚚 *G라이더 현황 리포트*
📅 {now.strftime('%Y-%m-%d %H:%M')} 기준

📊 *총 현황*
• 총 점수: `{data.get('total_score', 0):,}점`
• 총 완료: `{data.get('total_completed', 0):,}건`

🎯 *미션 현황*"""
        
        missions = data.get('missions', {})
        for mission_name, mission_data in missions.items():
            current = mission_data.get('current', 0)
            target = mission_data.get('target', 0)
            percentage = (current / target * 100) if target > 0 else 0
            message += f"\n• {mission_name}: `{current:,}/{target:,}` ({percentage:.1f}%)"
        
        return message

class EmailNotifier(NotificationPlatform):
    """이메일 알림"""
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, recipients: List[str]):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.recipients = recipients
        self.platform_name = "Email"
    
    def send_message(self, message: str, title: str = "", priority: str = "normal") -> bool:
        """이메일 메시지 전송"""
        try:
            msg = MimeMultipart('alternative')
            msg['From'] = self.username
            msg['To'] = ', '.join(self.recipients)
            msg['Subject'] = title or "🎯 G라이더 자동화 알림"
            
            # HTML 버전
            html_message = self._format_html_message(message, priority)
            html_part = MimeText(html_message, 'html', 'utf-8')
            
            # 텍스트 버전
            text_part = MimeText(message, 'plain', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"✅ 이메일 전송 성공: {len(self.recipients)}명")
            return True
            
        except Exception as e:
            logger.error(f"❌ 이메일 알림 오류: {e}")
            return False
    
    def format_grider_data(self, data: Dict) -> str:
        """이메일용 G라이더 데이터 포맷팅"""
        now = datetime.now(KST)
        
        message = f"""G라이더 현황 리포트 - {now.strftime('%Y-%m-%d %H:%M')} 기준

총 현황:
- 총 점수: {data.get('total_score', 0):,}점
- 총 완료: {data.get('total_completed', 0):,}건

미션 현황:"""
        
        missions = data.get('missions', {})
        for mission_name, mission_data in missions.items():
            current = mission_data.get('current', 0)
            target = mission_data.get('target', 0)
            percentage = (current / target * 100) if target > 0 else 0
            message += f"\n- {mission_name}: {current:,}/{target:,} ({percentage:.1f}%)"
        
        # 라이더 정보
        riders = data.get('riders', [])
        active_riders = [r for r in riders if r.get('completed', 0) > 0]
        
        if active_riders:
            message += f"\n\n활동 중인 라이더: {len(active_riders)}명"
            top_riders = sorted(active_riders, key=lambda x: x.get('completed', 0), reverse=True)[:10]
            
            for i, rider in enumerate(top_riders, 1):
                name = rider.get('name', '이름없음')
                completed = rider.get('completed', 0)
                acceptance_rate = rider.get('acceptance_rate', 0)
                message += f"\n{i:2d}. {name}: {completed:,}건 (수락률 {acceptance_rate:.1f}%)"
        
        return message
    
    def _format_html_message(self, message: str, priority: str) -> str:
        """HTML 형식 메시지 생성"""
        color = {"high": "#ff4444", "medium": "#ffaa00", "normal": "#44aa44"}.get(priority, "#44aa44")
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
            <div style="border-left: 4px solid {color}; padding-left: 15px; margin-bottom: 20px;">
                <h2 style="color: {color}; margin: 0;">🎯 G라이더 자동화 알림</h2>
            </div>
            <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; font-family: 'Courier New', monospace;">
{message}
            </pre>
            <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
            <p style="color: #666; font-size: 12px;">
                G라이더 자동화 시스템 | {datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')}
            </p>
        </body>
        </html>
        """
        return html

class MultiPlatformNotifier:
    """다중 플랫폼 알림 관리자"""
    
    def __init__(self, config_file: str = "notification_config.json"):
        self.platforms: List[NotificationPlatform] = []
        self.config_file = config_file
        self.load_config()
        
        logger.info(f"🎯 다중 플랫폼 알림 시스템 초기화: {len(self.platforms)}개 플랫폼")
    
    def load_config(self):
        """설정 로드"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 슬랙 설정
            if config.get('slack', {}).get('enabled'):
                slack_config = config['slack']
                self.platforms.append(SlackNotifier(
                    webhook_url=slack_config['webhook_url'],
                    channel=slack_config.get('channel', '#grider-alerts')
                ))
            
            # 디스코드 설정
            if config.get('discord', {}).get('enabled'):
                discord_config = config['discord']
                self.platforms.append(DiscordNotifier(
                    webhook_url=discord_config['webhook_url']
                ))
            
            # 텔레그램 설정
            if config.get('telegram', {}).get('enabled'):
                telegram_config = config['telegram']
                self.platforms.append(TelegramNotifier(
                    bot_token=telegram_config['bot_token'],
                    chat_id=telegram_config['chat_id']
                ))
            
            # 이메일 설정
            if config.get('email', {}).get('enabled'):
                email_config = config['email']
                self.platforms.append(EmailNotifier(
                    smtp_server=email_config['smtp_server'],
                    smtp_port=email_config['smtp_port'],
                    username=email_config['username'],
                    password=email_config['password'],
                    recipients=email_config['recipients']
                ))
                
        except FileNotFoundError:
            logger.warning("⚠️ 알림 설정 파일이 없습니다. 기본 설정으로 생성합니다.")
            self.create_default_config()
        except Exception as e:
            logger.error(f"❌ 알림 설정 로드 실패: {e}")
    
    def create_default_config(self):
        """기본 설정 파일 생성"""
        default_config = {
            "slack": {
                "enabled": False,
                "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
                "channel": "#grider-alerts"
            },
            "discord": {
                "enabled": False,
                "webhook_url": "https://discord.com/api/webhooks/YOUR/WEBHOOK/URL"
            },
            "telegram": {
                "enabled": False,
                "bot_token": "YOUR_BOT_TOKEN",
                "chat_id": "YOUR_CHAT_ID"
            },
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "your-email@gmail.com",
                "password": "your-app-password",
                "recipients": ["recipient@example.com"]
            }
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            logger.info(f"📝 기본 알림 설정 파일 생성: {self.config_file}")
        except Exception as e:
            logger.error(f"❌ 기본 설정 파일 생성 실패: {e}")
    
    def send_grider_report(self, data: Dict, priority: str = "normal") -> Dict[str, bool]:
        """G라이더 리포트 전송"""
        results = {}
        
        for platform in self.platforms:
            try:
                message = platform.format_grider_data(data)
                title = f"📊 G라이더 현황 ({datetime.now(KST).strftime('%H:%M')})"
                
                success = platform.send_message(message, title, priority)
                results[platform.platform_name] = success
                
            except Exception as e:
                logger.error(f"❌ {platform.platform_name} 전송 실패: {e}")
                results[platform.platform_name] = False
        
        success_count = sum(results.values())
        logger.info(f"📤 알림 전송 완료: {success_count}/{len(self.platforms)}개 플랫폼 성공")
        
        return results
    
    def send_alert(self, message: str, title: str = "", priority: str = "high") -> Dict[str, bool]:
        """긴급 알림 전송"""
        results = {}
        
        for platform in self.platforms:
            try:
                success = platform.send_message(message, title, priority)
                results[platform.platform_name] = success
                
            except Exception as e:
                logger.error(f"❌ {platform.platform_name} 알림 실패: {e}")
                results[platform.platform_name] = False
        
        return results
    
    def get_status(self) -> Dict:
        """알림 시스템 상태"""
        return {
            "active_platforms": len(self.platforms),
            "platform_list": [p.platform_name for p in self.platforms],
            "config_file": self.config_file,
            "timestamp": datetime.now(KST).isoformat()
        } 