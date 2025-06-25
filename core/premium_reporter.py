"""
📄 프리미엄 리포트 생성기
PDF 형태의 전문적인 투자 분석 리포트 자동 생성
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import sqlite3
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from auto_finance.core.notifier import Notifier

class PremiumReporter:
    def __init__(self):
        self.notifier = Notifier()
        self.db_path = Path("data/stock_news.db")
        self.reports_dir = Path("data/premium_reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # PDF 스타일 설정
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """커스텀 스타일 설정"""
        # 제목 스타일
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.darkblue,
            alignment=1  # 중앙 정렬
        )
        
        # 섹션 제목 스타일
        self.section_style = ParagraphStyle(
            'SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkgreen
        )
        
        # 본문 스타일
        self.body_style = ParagraphStyle(
            'BodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leading=14
        )
    
    def generate_daily_premium_report(self) -> str:
        """일일 프리미엄 리포트 생성"""
        today = datetime.now().date()
        
        # 데이터 수집
        news_data = self._get_daily_news_data(today)
        market_data = self._get_market_summary()
        analysis_data = self._get_analysis_insights()
        
        # PDF 파일명 생성
        filename = f"premium_report_{today.strftime('%Y%m%d')}.pdf"
        filepath = self.reports_dir / filename
        
        # PDF 생성
        doc = SimpleDocTemplate(str(filepath), pagesize=A4)
        story = []
        
        # 제목
        story.append(Paragraph(f"📈 주식 뉴스 프리미엄 리포트", self.title_style))
        story.append(Paragraph(f"생성일: {today.strftime('%Y년 %m월 %d일')}", self.body_style))
        story.append(Spacer(1, 20))
        
        # 요약
        story.append(Paragraph("📊 일일 요약", self.section_style))
        summary_text = f"""
        • 수집된 뉴스: {news_data.get('total_articles', 0):,}개
        • 주요 키워드: {', '.join(news_data.get('top_keywords', []))}
        • 시장 동향: {market_data.get('trend', '중립')}
        • 투자 포인트: {analysis_data.get('investment_point', '관망')}
        """
        story.append(Paragraph(summary_text, self.body_style))
        story.append(Spacer(1, 15))
        
        # 주요 뉴스 분석
        story.append(Paragraph("📰 주요 뉴스 분석", self.section_style))
        for i, news in enumerate(news_data.get('top_news', [])[:5], 1):
            news_text = f"""
            <b>{i}. {news.get('title', '')}</b><br/>
            출처: {news.get('source', '')}<br/>
            요약: {news.get('summary', '')}<br/>
            영향도: {news.get('impact', '보통')}
            """
            story.append(Paragraph(news_text, self.body_style))
            story.append(Spacer(1, 10))
        
        # 시장 동향 분석
        story.append(Paragraph("📈 시장 동향 분석", self.section_style))
        market_text = f"""
        <b>전체 동향:</b> {market_data.get('overall_trend', '')}<br/>
        <b>주요 이슈:</b> {market_data.get('key_issues', '')}<br/>
        <b>투자 전략:</b> {market_data.get('strategy', '')}
        """
        story.append(Paragraph(market_text, self.body_style))
        story.append(Spacer(1, 15))
        
        # 투자 권장사항
        story.append(Paragraph("💡 투자 권장사항", self.section_style))
        recommendations = analysis_data.get('recommendations', [])
        for i, rec in enumerate(recommendations, 1):
            rec_text = f"{i}. {rec}"
            story.append(Paragraph(rec_text, self.body_style))
        
        # PDF 빌드
        doc.build(story)
        
        return str(filepath)
    
    def generate_weekly_premium_report(self) -> str:
        """주간 프리미엄 리포트 생성"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        
        # 데이터 수집
        weekly_data = self._get_weekly_data(start_date, end_date)
        
        # PDF 파일명 생성
        filename = f"weekly_premium_report_{end_date.strftime('%Y%m%d')}.pdf"
        filepath = self.reports_dir / filename
        
        # PDF 생성
        doc = SimpleDocTemplate(str(filepath), pagesize=A4)
        story = []
        
        # 제목
        story.append(Paragraph(f"📈 주간 주식 뉴스 프리미엄 리포트", self.title_style))
        story.append(Paragraph(f"기간: {start_date.strftime('%Y년 %m월 %d일')} ~ {end_date.strftime('%Y년 %m월 %d일')}", self.body_style))
        story.append(Spacer(1, 20))
        
        # 주간 요약
        story.append(Paragraph("📊 주간 요약", self.section_style))
        summary_text = f"""
        • 총 수집 뉴스: {weekly_data.get('total_articles', 0):,}개
        • 평균 일일 뉴스: {weekly_data.get('avg_daily_articles', 0):.1f}개
        • 주요 트렌드: {weekly_data.get('main_trend', '')}
        • 시장 전망: {weekly_data.get('market_outlook', '')}
        """
        story.append(Paragraph(summary_text, self.body_style))
        story.append(Spacer(1, 15))
        
        # 일별 통계 테이블
        story.append(Paragraph("📅 일별 통계", self.section_style))
        daily_stats = weekly_data.get('daily_stats', [])
        if daily_stats:
            table_data = [['날짜', '뉴스 수', '생성 콘텐츠', '오류']]
            for stat in daily_stats:
                table_data.append([
                    stat.get('date', ''),
                    str(stat.get('articles', 0)),
                    str(stat.get('generated', 0)),
                    str(stat.get('errors', 0))
                ])
            
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
            story.append(Spacer(1, 15))
        
        # 주간 투자 전략
        story.append(Paragraph("🎯 주간 투자 전략", self.section_style))
        strategy_text = f"""
        <b>시장 분석:</b> {weekly_data.get('market_analysis', '')}<br/>
        <b>투자 포인트:</b> {weekly_data.get('investment_points', '')}<br/>
        <b>리스크 요인:</b> {weekly_data.get('risk_factors', '')}<br/>
        <b>권장 포트폴리오:</b> {weekly_data.get('portfolio_recommendation', '')}
        """
        story.append(Paragraph(strategy_text, self.body_style))
        
        # PDF 빌드
        doc.build(story)
        
        return str(filepath)
    
    def _get_daily_news_data(self, date: datetime.date) -> Dict[str, Any]:
        """일일 뉴스 데이터 조회"""
        if not self.db_path.exists():
            return {}
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 오늘 수집된 기사
            cursor.execute("""
                SELECT title, source, url FROM crawled_articles 
                WHERE DATE(crawled_at) = ?
                ORDER BY crawled_at DESC LIMIT 10
            """, (date,))
            
            articles = []
            for row in cursor.fetchall():
                articles.append({
                    'title': row[0],
                    'source': row[1],
                    'url': row[2],
                    'summary': f"{row[0][:100]}...",
                    'impact': '보통'
                })
            
            # 키워드 분석 (간단한 예시)
            keywords = ['주식', '투자', '경제', '금융', '증시']
            
            return {
                'total_articles': len(articles),
                'top_news': articles,
                'top_keywords': keywords
            }
    
    def _get_market_summary(self) -> Dict[str, Any]:
        """시장 요약 데이터 (예시)"""
        return {
            'trend': '상승',
            'overall_trend': '긍정적인 뉴스가 우세하며 시장 분위기 개선',
            'key_issues': '금리 인하 기대감, 기업 실적 개선',
            'strategy': '적극적 매수 전략 권장'
        }
    
    def _get_analysis_insights(self) -> Dict[str, Any]:
        """분석 인사이트 (예시)"""
        return {
            'investment_point': '매수',
            'recommendations': [
                '테크주 중심 포트폴리오 구성',
                '금리 민감주 적극 매수',
                '소비재 섹터 관망',
                '에너지주 부분 매수'
            ]
        }
    
    def _get_weekly_data(self, start_date: datetime.date, end_date: datetime.date) -> Dict[str, Any]:
        """주간 데이터 조회"""
        if not self.db_path.exists():
            return {}
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 주간 통계
            cursor.execute("""
                SELECT 
                    date,
                    articles_crawled,
                    articles_generated,
                    errors
                FROM statistics 
                WHERE date BETWEEN ? AND ?
                ORDER BY date
            """, (start_date, end_date))
            
            daily_stats = []
            total_articles = 0
            
            for row in cursor.fetchall():
                daily_stats.append({
                    'date': row[0],
                    'articles': row[1],
                    'generated': row[2],
                    'errors': row[3]
                })
                total_articles += row[1]
            
            return {
                'total_articles': total_articles,
                'avg_daily_articles': total_articles / 7 if daily_stats else 0,
                'daily_stats': daily_stats,
                'main_trend': 'AI 관련주 강세, 반도체 섹터 회복',
                'market_outlook': '긍정적 전망 유지',
                'market_analysis': '기업 실적 개선과 금리 인하 기대감으로 상승 모멘텀 지속',
                'investment_points': '테크주, 금리 민감주 중심 매수',
                'risk_factors': '지정학적 리스크, 인플레이션 재부상',
                'portfolio_recommendation': '테크 40%, 금융 30%, 소비재 20%, 에너지 10%'
            }
    
    def send_premium_report(self, report_path: str, recipients: List[str] = None):
        """프리미엄 리포트 전송"""
        if recipients:
            # 이메일 전송 (구현 예정)
            pass
        
        # 슬랙 알림
        message = f"""
📄 프리미엄 리포트 생성 완료

📁 파일: {Path(report_path).name}
📅 생성일: {datetime.now().strftime('%Y-%m-%d %H:%M')}
📊 내용: 전문 투자 분석 및 권장사항

🔗 다운로드: {report_path}
        """
        
        self.notifier.send(message, channel='slack') 