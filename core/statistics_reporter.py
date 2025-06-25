"""
📊 통계 리포트 생성기
일일/주간/월간 통계 리포트 자동 생성
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
from auto_finance.core.notifier import Notifier

class StatisticsReporter:
    def __init__(self):
        self.notifier = Notifier()
        self.db_path = Path("data/stock_news.db")
    
    def generate_daily_report(self) -> Dict[str, Any]:
        """일일 통계 리포트 생성"""
        today = datetime.now().date()
        
        # DB에서 오늘 데이터 조회
        stats = self._get_daily_stats(today)
        
        # 리포트 생성
        report = {
            "date": today.strftime("%Y-%m-%d"),
            "type": "daily",
            "summary": self._generate_summary(stats),
            "details": stats,
            "trends": self._analyze_trends(stats),
            "recommendations": self._generate_recommendations(stats)
        }
        
        # 리포트 저장
        self._save_report(report)
        
        return report
    
    def generate_weekly_report(self) -> Dict[str, Any]:
        """주간 통계 리포트 생성"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        
        # DB에서 주간 데이터 조회
        stats = self._get_period_stats(start_date, end_date)
        
        # 리포트 생성
        report = {
            "period": f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}",
            "type": "weekly",
            "summary": self._generate_summary(stats),
            "details": stats,
            "trends": self._analyze_trends(stats),
            "recommendations": self._generate_recommendations(stats)
        }
        
        # 리포트 저장
        self._save_report(report)
        
        return report
    
    def _get_daily_stats(self, date: datetime.date) -> Dict[str, Any]:
        """일일 통계 조회"""
        if not self.db_path.exists():
            return {}
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 크롤링된 기사 수
            cursor.execute("""
                SELECT COUNT(*) FROM crawled_articles 
                WHERE DATE(crawled_at) = ?
            """, (date,))
            articles_crawled = cursor.fetchone()[0]
            
            # 생성된 콘텐츠 수
            cursor.execute("""
                SELECT COUNT(*) FROM generated_contents 
                WHERE DATE(generated_at) = ?
            """, (date,))
            articles_generated = cursor.fetchone()[0]
            
            # 통계 테이블에서 조회
            cursor.execute("""
                SELECT * FROM statistics WHERE date = ?
            """, (date,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "articles_crawled": articles_crawled,
                    "articles_generated": articles_generated,
                    "articles_verified": row[2],
                    "articles_saved": row[4],
                    "errors": row[5]
                }
            else:
                return {
                    "articles_crawled": articles_crawled,
                    "articles_generated": articles_generated,
                    "articles_verified": 0,
                    "articles_saved": 0,
                    "errors": 0
                }
    
    def _get_period_stats(self, start_date: datetime.date, end_date: datetime.date) -> Dict[str, Any]:
        """기간별 통계 조회"""
        if not self.db_path.exists():
            return {}
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 기간별 통계 집계
            cursor.execute("""
                SELECT 
                    SUM(articles_crawled) as total_crawled,
                    SUM(articles_generated) as total_generated,
                    SUM(articles_verified) as total_verified,
                    SUM(articles_saved) as total_saved,
                    SUM(errors) as total_errors,
                    COUNT(*) as days_count
                FROM statistics 
                WHERE date BETWEEN ? AND ?
            """, (start_date, end_date))
            
            row = cursor.fetchone()
            if row:
                return {
                    "articles_crawled": row[0] or 0,
                    "articles_generated": row[1] or 0,
                    "articles_verified": row[2] or 0,
                    "articles_saved": row[3] or 0,
                    "errors": row[4] or 0,
                    "days_count": row[5] or 0
                }
            else:
                return {
                    "articles_crawled": 0,
                    "articles_generated": 0,
                    "articles_verified": 0,
                    "articles_saved": 0,
                    "errors": 0,
                    "days_count": 0
                }
    
    def _generate_summary(self, stats: Dict[str, Any]) -> str:
        """통계 요약 생성"""
        total_crawled = stats.get('articles_crawled', 0)
        total_generated = stats.get('articles_generated', 0)
        total_errors = stats.get('errors', 0)
        
        success_rate = 0
        if total_crawled > 0:
            success_rate = (total_generated / total_crawled) * 100
        
        return f"""
📊 통계 요약

📰 크롤링된 기사: {total_crawled:,}개
✍️ 생성된 콘텐츠: {total_generated:,}개
❌ 발생한 오류: {total_errors:,}개
📈 성공률: {success_rate:.1f}%
        """
    
    def _analyze_trends(self, stats: Dict[str, Any]) -> List[str]:
        """트렌드 분석"""
        trends = []
        
        # 간단한 트렌드 분석 (실제로는 이전 데이터와 비교)
        if stats.get('articles_crawled', 0) > 100:
            trends.append("📈 크롤링 성과 양호")
        else:
            trends.append("📉 크롤링 성과 개선 필요")
        
        if stats.get('errors', 0) > 5:
            trends.append("⚠️ 오류 발생 빈도 높음")
        else:
            trends.append("✅ 안정적인 운영")
        
        return trends
    
    def _generate_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """개선 권장사항 생성"""
        recommendations = []
        
        if stats.get('articles_crawled', 0) < 50:
            recommendations.append("🔍 크롤링 소스 추가 검토")
        
        if stats.get('errors', 0) > 3:
            recommendations.append("🛠️ 오류 로그 분석 및 수정")
        
        if stats.get('articles_generated', 0) == 0:
            recommendations.append("🤖 AI 모델 설정 점검")
        
        return recommendations
    
    def _save_report(self, report: Dict[str, Any]):
        """리포트 저장"""
        reports_dir = Path("data/reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{report['type']}_report_{datetime.now().strftime('%Y%m%d')}.json"
        filepath = reports_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    def send_report_notification(self, report: Dict[str, Any]):
        """리포트 알림 전송"""
        message = f"""
📊 {report['type'].title()} 리포트 완료

{report['summary']}

🔍 주요 트렌드:
{chr(10).join(report['trends'])}

💡 권장사항:
{chr(10).join(report['recommendations'])}
        """
        
        self.notifier.send(message, channel='slack') 