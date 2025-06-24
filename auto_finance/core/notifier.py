"""
🔔 실시간 알림 시스템
슬랙, 카카오톡, 이메일 등 다양한 채널 지원
"""

import os
import requests
from typing import List, Dict, Any, Optional
from config.settings import settings
from config.credentials import credentials

class Notifier:
    def __init__(self):
        # 슬랙 웹훅 URL
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL', '')
        # 카카오톡 토큰 (예시)
        self.kakao_token = credentials.KAKAO_ACCESS_TOKEN
        # 이메일 설정 (예시)
        self.email_user = os.getenv('EMAIL_USER', '')
        self.email_password = os.getenv('EMAIL_PASSWORD', '')
        self.email_host = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
        self.email_port = int(os.getenv('EMAIL_PORT', '587'))

    def send(self, message: str, channel: str = 'slack') -> bool:
        """채널별로 메시지 전송"""
        if channel == 'slack' and self.slack_webhook:
            return self._send_slack(message)
        elif channel == 'kakao' and self.kakao_token:
            return self._send_kakao(message)
        elif channel == 'email' and self.email_user:
            return self._send_email(message)
        else:
            print(f"[알림] {channel} 채널 미설정 또는 지원하지 않음")
            return False

    def _send_slack(self, message: str) -> bool:
        try:
            resp = requests.post(self.slack_webhook, json={"text": message})
            return resp.status_code == 200
        except Exception as e:
            print(f"[알림] 슬랙 전송 실패: {e}")
            return False

    def _send_kakao(self, message: str) -> bool:
        # 실제 카카오톡 API 연동은 별도 구현 필요
        print(f"[알림] (카카오톡) {message}")
        return True

    def _send_email(self, message: str) -> bool:
        # 실제 이메일 전송은 별도 구현 필요
        print(f"[알림] (이메일) {message}")
        return True 