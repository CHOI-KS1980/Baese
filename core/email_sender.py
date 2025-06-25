"""
📧 이메일 발송 시스템
프리미엄 리포트 자동 이메일 발송
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from config.credentials import credentials

class EmailSender:
    def __init__(self):
        self.smtp_host = credentials.EMAIL_HOST
        self.smtp_port = credentials.EMAIL_PORT
        self.email_user = credentials.EMAIL_USER
        self.email_password = credentials.EMAIL_PASSWORD
        
        # 기본 구독자 목록 (실제로는 DB에서 관리)
        self.default_subscribers = [
            "investor1@example.com",
            "investor2@example.com",
            "analyst@example.com"
        ]
    
    def send_premium_report(self, report_path: str, recipients: Optional[List[str]] = None) -> bool:
        """프리미엄 리포트 이메일 발송"""
        if not recipients:
            recipients = self.default_subscribers
        
        if not self._validate_email_config():
            print("⚠️ 이메일 설정이 완료되지 않았습니다.")
            return False
        
        try:
            # 이메일 메시지 생성
            msg = self._create_email_message(report_path, recipients)
            
            # SMTP 서버 연결 및 발송
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                
                for recipient in recipients:
                    msg['To'] = recipient
                    server.send_message(msg)
                    print(f"✅ 이메일 발송 완료: {recipient}")
            
            return True
            
        except Exception as e:
            print(f"❌ 이메일 발송 실패: {e}")
            return False
    
    def _create_email_message(self, report_path: str, recipients: List[str]) -> MIMEMultipart:
        """이메일 메시지 생성"""
        msg = MIMEMultipart()
        msg['From'] = self.email_user
        msg['Subject'] = f"📈 주식 뉴스 프리미엄 리포트 - {datetime.now().strftime('%Y년 %m월 %d일')}"
        
        # 이메일 본문
        body = f"""
안녕하세요,

주식 뉴스 자동화 시스템에서 생성된 프리미엄 리포트를 첨부합니다.

📊 리포트 내용:
• 일일 주요 뉴스 분석
• 시장 동향 및 전망
• 투자 권장사항
• 포트폴리오 전략

📅 생성일: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}
📁 파일명: {Path(report_path).name}

감사합니다.
주식 뉴스 자동화 시스템
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # PDF 첨부
        self._attach_pdf(msg, report_path)
        
        return msg
    
    def _attach_pdf(self, msg: MIMEMultipart, pdf_path: str):
        """PDF 파일 첨부"""
        try:
            with open(pdf_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {Path(pdf_path).name}'
            )
            
            msg.attach(part)
            
        except Exception as e:
            print(f"❌ PDF 첨부 실패: {e}")
    
    def _validate_email_config(self) -> bool:
        """이메일 설정 검증"""
        return all([
            self.smtp_host,
            self.smtp_port,
            self.email_user,
            self.email_password
        ])
    
    def send_daily_summary(self, summary_data: dict, recipients: Optional[List[str]] = None) -> bool:
        """일일 요약 이메일 발송"""
        if not recipients:
            recipients = self.default_subscribers
        
        if not self._validate_email_config():
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['Subject'] = f"📊 주식 뉴스 일일 요약 - {datetime.now().strftime('%Y년 %m월 %d일')}"
            
            # 요약 본문 생성
            body = f"""
📈 주식 뉴스 일일 요약

📰 크롤링된 기사: {summary_data.get('articles_crawled', 0):,}개
✍️ 생성된 콘텐츠: {summary_data.get('articles_generated', 0):,}개
❌ 발생한 오류: {summary_data.get('errors', 0):,}개
📈 성공률: {summary_data.get('success_rate', 0):.1f}%

🔍 주요 트렌드:
{chr(10).join(summary_data.get('trends', []))}

💡 권장사항:
{chr(10).join(summary_data.get('recommendations', []))}

감사합니다.
주식 뉴스 자동화 시스템
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 이메일 발송
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                
                for recipient in recipients:
                    msg['To'] = recipient
                    server.send_message(msg)
                    print(f"✅ 일일 요약 이메일 발송 완료: {recipient}")
            
            return True
            
        except Exception as e:
            print(f"❌ 일일 요약 이메일 발송 실패: {e}")
            return False 