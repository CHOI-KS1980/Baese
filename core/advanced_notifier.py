"""
🔔 고급 알림 시스템
조건부 알림, 이상탐지, 통계 기반 알림 지원
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
from auto_finance.core.notifier import Notifier

class AdvancedNotifier:
    def __init__(self):
        self.notifier = Notifier()
        self.alert_history = []
        self.alert_config = {
            "error_threshold": 3,  # 오류 임계값
            "success_rate_threshold": 0.8,  # 성공률 임계값
            "keywords": ["주식", "투자", "경제", "금융"],  # 중요 키워드
            "daily_report_time": "18:00",  # 일일 리포트 시간
            "weekly_report_day": "monday"  # 주간 리포트 요일
        }
    
    def check_and_alert(self, event_type: str, data: Dict[str, Any]) -> bool:
        """이벤트 타입에 따른 조건부 알림 체크 및 전송"""
        
        if event_type == "crawling_complete":
            return self._check_crawling_alerts(data)
        elif event_type == "fact_check_complete":
            return self._check_fact_check_alerts(data)
        elif event_type == "generation_complete":
            return self._check_generation_alerts(data)
        elif event_type == "upload_complete":
            return self._check_upload_alerts(data)
        elif event_type == "error_occurred":
            return self._check_error_alerts(data)
        elif event_type == "daily_summary":
            return self._send_daily_summary(data)
        
        return False
    
    def _check_crawling_alerts(self, data: Dict[str, Any]) -> bool:
        """크롤링 완료 알림 체크"""
        articles_count = data.get('articles_crawled', 0)
        
        # 기사 수가 너무 적으면 경고
        if articles_count < 50:
            message = f"⚠️ 크롤링 기사 수 부족: {articles_count}개 (기준: 50개)"
            return self.notifier.send(message, channel='slack')
        
        # 중요 키워드가 포함된 기사가 많으면 알림
        keyword_articles = data.get('keyword_articles', 0)
        if keyword_articles > 10:
            message = f"🔥 중요 키워드 기사 다수 발견: {keyword_articles}개"
            return self.notifier.send(message, channel='slack')
        
        return True
    
    def _check_fact_check_alerts(self, data: Dict[str, Any]) -> bool:
        """팩트 체크 완료 알림 체크"""
        verified_count = data.get('articles_verified', 0)
        total_count = data.get('total_articles', 0)
        
        if total_count > 0:
            success_rate = verified_count / total_count
            
            # 신뢰도가 낮으면 경고
            if success_rate < self.alert_config["success_rate_threshold"]:
                message = f"⚠️ 팩트 체크 신뢰도 낮음: {success_rate:.1%} (기준: {self.alert_config['success_rate_threshold']:.1%})"
                return self.notifier.send(message, channel='slack')
        
        return True
    
    def _check_generation_alerts(self, data: Dict[str, Any]) -> bool:
        """콘텐츠 생성 완료 알림 체크"""
        generated_count = data.get('articles_generated', 0)
        
        # 생성된 기사가 없으면 경고
        if generated_count == 0:
            message = "❌ 콘텐츠 생성 실패: 생성된 기사가 없습니다"
            return self.notifier.send(message, channel='slack')
        
        # 생성 성공 시 알림
        message = f"✅ 콘텐츠 생성 완료: {generated_count}개 기사 생성"
        return self.notifier.send(message, channel='slack')
    
    def _check_upload_alerts(self, data: Dict[str, Any]) -> bool:
        """업로드 완료 알림 체크"""
        success_count = data.get('successful', 0)
        failed_count = data.get('failed', 0)
        total_count = success_count + failed_count
        
        if total_count > 0:
            success_rate = success_count / total_count
            
            # 업로드 실패율이 높으면 경고
            if success_rate < 0.9:
                message = f"⚠️ 업로드 실패율 높음: {success_rate:.1%} (기준: 90%)"
                return self.notifier.send(message, channel='slack')
        
        return True
    
    def _check_error_alerts(self, data: Dict[str, Any]) -> bool:
        """오류 발생 알림 체크"""
        error_count = data.get('errors', 0)
        
        # 오류가 임계값을 넘으면 경고
        if error_count >= self.alert_config["error_threshold"]:
            message = f"🚨 오류 발생 임계값 초과: {error_count}개 (기준: {self.alert_config['error_threshold']}개)"
            return self.notifier.send(message, channel='slack')
        
        return True
    
    def _send_daily_summary(self, data: Dict[str, Any]) -> bool:
        """일일 요약 리포트 전송"""
        message = f"""
📊 일일 요약 리포트 ({datetime.now().strftime('%Y-%m-%d')})

📰 크롤링: {data.get('articles_crawled', 0)}개
🔍 팩트 체크: {data.get('articles_verified', 0)}개
✍️ 콘텐츠 생성: {data.get('articles_generated', 0)}개
📤 업로드: {data.get('articles_uploaded', 0)}개
❌ 오류: {data.get('errors', 0)}개

성공률: {data.get('success_rate', 0):.1%}
        """
        return self.notifier.send(message, channel='slack')
    
    def detect_anomalies(self, current_stats: Dict[str, Any]) -> List[str]:
        """이상탐지 수행"""
        anomalies = []
        
        # 이전 통계와 비교 (간단한 예시)
        previous_stats = self._load_previous_stats()
        
        if previous_stats:
            # 크롤링 기사 수 급감
            current_crawled = current_stats.get('articles_crawled', 0)
            previous_crawled = previous_stats.get('articles_crawled', 0)
            
            if previous_crawled > 0 and current_crawled < previous_crawled * 0.5:
                anomalies.append(f"크롤링 기사 수 급감: {current_crawled}개 (이전: {previous_crawled}개)")
            
            # 오류율 급증
            current_errors = current_stats.get('errors', 0)
            previous_errors = previous_stats.get('errors', 0)
            
            if current_errors > previous_errors * 2:
                anomalies.append(f"오류율 급증: {current_errors}개 (이전: {previous_errors}개)")
        
        return anomalies
    
    def _load_previous_stats(self) -> Optional[Dict[str, Any]]:
        """이전 통계 로드"""
        stats_file = Path("data/statistics.json")
        if stats_file.exists():
            try:
                with open(stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('stats', {})
            except:
                pass
        return None 