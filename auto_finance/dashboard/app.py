"""
📊 고도화된 실시간 대시보드
실시간 모니터링, 인터랙티브 차트, 알림 관리, 성능 분석
"""

import dash
from dash import dcc, html, Input, Output, callback_context
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from auto_finance.utils.logger import setup_logger
from auto_finance.config.settings import DASHBOARD_CONFIG

logger = setup_logger(__name__)

class DashboardApp:
    """고도화된 대시보드 애플리케이션"""
    
    def __init__(self):
        self.app = dash.Dash(__name__, 
                            title="Auto Finance Dashboard",
                            update_title=None)
        
        # 설정 로드
        self.refresh_interval = DASHBOARD_CONFIG.get('refresh_interval', 30000)  # 30초
        self.max_data_points = DASHBOARD_CONFIG.get('max_data_points', 1000)
        
        # 데이터 저장소
        self.crawler_data = []
        self.fact_check_data = []
        self.financial_data = []
        self.notification_data = []
        
        # 대시보드 초기화
        self._setup_layout()
        self._setup_callbacks()
        
        logger.info("📊 대시보드 애플리케이션 초기화 완료")
    
    def _setup_layout(self):
        """대시보드 레이아웃 설정"""
        self.app.layout = html.Div([
            # 헤더
            html.Div([
                html.H1("🤖 Auto Finance Dashboard", 
                       style={'textAlign': 'center', 'color': '#2c3e50'}),
                html.P("실시간 주식 뉴스 자동화 시스템 모니터링", 
                      style={'textAlign': 'center', 'color': '#7f8c8d'})
            ], style={'backgroundColor': '#ecf0f1', 'padding': '20px', 'marginBottom': '20px'}),
            
            # 상단 통계 카드
            html.Div([
                html.Div([
                    html.H3(id='total-articles', children='0'),
                    html.P('총 수집 기사')
                ], className='stat-card'),
                html.Div([
                    html.H3(id='success-rate', children='0%'),
                    html.P('성공률')
                ], className='stat-card'),
                html.Div([
                    html.H3(id='processing-time', children='0s'),
                    html.P('평균 처리 시간')
                ], className='stat-card'),
                html.Div([
                    html.H3(id='active-alerts', children='0'),
                    html.P('활성 알림')
                ], className='stat-card')
            ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '30px'}),
            
            # 메인 차트 영역
            html.Div([
                # 왼쪽 컬럼
                html.Div([
                    # 크롤링 통계
                    html.Div([
                        html.H4("📰 뉴스 크롤링 통계"),
                        dcc.Graph(id='crawler-chart', style={'height': '300px'})
                    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '20px'}),
                    
                    # 팩트 체크 통계
                    html.Div([
                        html.H4("🔍 팩트 체크 통계"),
                        dcc.Graph(id='fact-check-chart', style={'height': '300px'})
                    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px'})
                ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                
                # 오른쪽 컬럼
                html.Div([
                    # 금융 데이터
                    html.Div([
                        html.H4("📈 금융 데이터"),
                        dcc.Graph(id='financial-chart', style={'height': '300px'})
                    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '20px'}),
                    
                    # 알림 통계
                    html.Div([
                        html.H4("🔔 알림 통계"),
                        dcc.Graph(id='notification-chart', style={'height': '300px'})
                    ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px'})
                ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'})
            ]),
            
            # 하단 상세 정보
            html.Div([
                # 최근 활동 로그
                html.Div([
                    html.H4("📋 최근 활동"),
                    html.Div(id='activity-log', style={'maxHeight': '300px', 'overflowY': 'auto'})
                ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '20px'}),
                
                # 시스템 상태
                html.Div([
                    html.H4("⚙️ 시스템 상태"),
                    html.Div(id='system-status')
                ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px'})
            ]),
            
            # 숨겨진 데이터 저장소
            dcc.Store(id='crawler-store'),
            dcc.Store(id='fact-check-store'),
            dcc.Store(id='financial-store'),
            dcc.Store(id='notification-store'),
            
            # 자동 새로고침
            dcc.Interval(
                id='interval-component',
                interval=self.refresh_interval,
                n_intervals=0
            )
        ], style={'backgroundColor': '#f8f9fa', 'minHeight': '100vh', 'padding': '20px'})
    
    def _setup_callbacks(self):
        """콜백 함수 설정"""
        
        @self.app.callback(
            [Output('total-articles', 'children'),
             Output('success-rate', 'children'),
             Output('processing-time', 'children'),
             Output('active-alerts', 'children')],
            [Input('interval-component', 'n_intervals')]
        )
        def update_statistics(n):
            """상단 통계 업데이트"""
            try:
                # 데이터 로드
                crawler_stats = self._load_crawler_stats()
                fact_check_stats = self._load_fact_check_stats()
                financial_stats = self._load_financial_stats()
                notification_stats = self._load_notification_stats()
                
                # 총 기사 수
                total_articles = crawler_stats.get('total_articles', 0)
                
                # 성공률 계산
                total_operations = (crawler_stats.get('successful_crawls', 0) + 
                                  fact_check_stats.get('successful_checks', 0))
                total_attempts = (crawler_stats.get('total_articles', 0) + 
                                fact_check_stats.get('total_checks', 0))
                success_rate = f"{(total_operations / total_attempts * 100):.1f}%" if total_attempts > 0 else "0%"
                
                # 평균 처리 시간
                avg_time = (crawler_stats.get('processing_time', 0) + 
                           fact_check_stats.get('processing_time', 0)) / 2
                processing_time = f"{avg_time:.1f}s"
                
                # 활성 알림
                active_alerts = notification_stats.get('total_notifications', 0)
                
                return total_articles, success_rate, processing_time, active_alerts
                
            except Exception as e:
                logger.error(f"❌ 통계 업데이트 실패: {e}")
                return "0", "0%", "0s", "0"
        
        @self.app.callback(
            Output('crawler-chart', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_crawler_chart(n):
            """크롤러 차트 업데이트"""
            try:
                stats = self._load_crawler_stats()
                
                # 차트 데이터 준비
                labels = ['성공', '실패']
                values = [stats.get('successful_crawls', 0), stats.get('failed_crawls', 0)]
                colors = ['#27ae60', '#e74c3c']
                
                fig = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.4,
                    marker_colors=colors
                )])
                
                fig.update_layout(
                    title="크롤링 성공률",
                    showlegend=True,
                    height=300
                )
                
                return fig
                
            except Exception as e:
                logger.error(f"❌ 크롤러 차트 업데이트 실패: {e}")
                return go.Figure()
        
        @self.app.callback(
            Output('fact-check-chart', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_fact_check_chart(n):
            """팩트 체크 차트 업데이트"""
            try:
                stats = self._load_fact_check_stats()
                
                # 검증 상태별 분포
                verified = stats.get('verified_count', 0)
                disputed = stats.get('disputed_count', 0)
                uncertain = stats.get('uncertain_count', 0)
                
                fig = go.Figure(data=[go.Bar(
                    x=['검증됨', '논란', '불확실'],
                    y=[verified, disputed, uncertain],
                    marker_color=['#27ae60', '#f39c12', '#e74c3c']
                )])
                
                fig.update_layout(
                    title="팩트 체크 결과",
                    xaxis_title="검증 상태",
                    yaxis_title="기사 수",
                    height=300
                )
                
                return fig
                
            except Exception as e:
                logger.error(f"❌ 팩트 체크 차트 업데이트 실패: {e}")
                return go.Figure()
        
        @self.app.callback(
            Output('financial-chart', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_financial_chart(n):
            """금융 데이터 차트 업데이트"""
            try:
                data = self._load_financial_data()
                
                if not data or 'stocks' not in data:
                    return go.Figure()
                
                stocks = data['stocks']
                if not stocks:
                    return go.Figure()
                
                # 상위 5개 종목의 변동률
                top_stocks = sorted(stocks.items(), key=lambda x: x[1].get('change_percent', 0), reverse=True)[:5]
                
                symbols = [stock[0] for stock in top_stocks]
                changes = [stock[1].get('change_percent', 0) for stock in top_stocks]
                colors = ['#27ae60' if change >= 0 else '#e74c3c' for change in changes]
                
                fig = go.Figure(data=[go.Bar(
                    x=symbols,
                    y=changes,
                    marker_color=colors
                )])
                
                fig.update_layout(
                    title="주요 종목 변동률",
                    xaxis_title="종목",
                    yaxis_title="변동률 (%)",
                    height=300
                )
                
                return fig
                
            except Exception as e:
                logger.error(f"❌ 금융 데이터 차트 업데이트 실패: {e}")
                return go.Figure()
        
        @self.app.callback(
            Output('notification-chart', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_notification_chart(n):
            """알림 차트 업데이트"""
            try:
                stats = self._load_notification_stats()
                
                # 채널별 알림 분포
                channel_stats = stats.get('channel_stats', {})
                
                if not channel_stats:
                    return go.Figure()
                
                channels = list(channel_stats.keys())
                successful = [channel_stats[ch]['successful'] for ch in channels]
                failed = [channel_stats[ch]['failed'] for ch in channels]
                
                fig = go.Figure(data=[
                    go.Bar(name='성공', x=channels, y=successful, marker_color='#27ae60'),
                    go.Bar(name='실패', x=channels, y=failed, marker_color='#e74c3c')
                ])
                
                fig.update_layout(
                    title="채널별 알림 통계",
                    xaxis_title="채널",
                    yaxis_title="알림 수",
                    barmode='group',
                    height=300
                )
                
                return fig
                
            except Exception as e:
                logger.error(f"❌ 알림 차트 업데이트 실패: {e}")
                return go.Figure()
        
        @self.app.callback(
            Output('activity-log', 'children'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_activity_log(n):
            """활동 로그 업데이트"""
            try:
                activities = self._load_activity_log()
                
                if not activities:
                    return html.P("활동 로그가 없습니다.")
                
                # 최근 10개 활동만 표시
                recent_activities = activities[-10:]
                
                log_items = []
                for activity in reversed(recent_activities):
                    timestamp = activity.get('timestamp', '')
                    message = activity.get('message', '')
                    level = activity.get('level', 'info')
                    
                    color_map = {
                        'info': '#3498db',
                        'success': '#27ae60',
                        'warning': '#f39c12',
                        'error': '#e74c3c'
                    }
                    
                    log_items.append(html.Div([
                        html.Span(timestamp, style={'color': '#7f8c8d', 'fontSize': '12px'}),
                        html.Span(f" {message}", style={'color': color_map.get(level, '#2c3e50')})
                    ], style={'marginBottom': '5px'}))
                
                return log_items
                
            except Exception as e:
                logger.error(f"❌ 활동 로그 업데이트 실패: {e}")
                return html.P("활동 로그를 불러올 수 없습니다.")
        
        @self.app.callback(
            Output('system-status', 'children'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_system_status(n):
            """시스템 상태 업데이트"""
            try:
                status = self._get_system_status()
                
                status_items = []
                for component, info in status.items():
                    is_healthy = info.get('healthy', False)
                    status_color = '#27ae60' if is_healthy else '#e74c3c'
                    status_text = '정상' if is_healthy else '오류'
                    
                    status_items.append(html.Div([
                        html.Span(f"{component}: ", style={'fontWeight': 'bold'}),
                        html.Span(status_text, style={'color': status_color}),
                        html.Br(),
                        html.Small(info.get('message', ''), style={'color': '#7f8c8d'})
                    ], style={'marginBottom': '10px'}))
                
                return status_items
                
            except Exception as e:
                logger.error(f"❌ 시스템 상태 업데이트 실패: {e}")
                return html.P("시스템 상태를 확인할 수 없습니다.")
    
    def _load_crawler_stats(self) -> Dict[str, Any]:
        """크롤러 통계 로드"""
        try:
            file_path = "data/crawler_stats.json"
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"❌ 크롤러 통계 로드 실패: {e}")
            return {}
    
    def _load_fact_check_stats(self) -> Dict[str, Any]:
        """팩트 체크 통계 로드"""
        try:
            file_path = "data/fact_check_results.json"
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list) and data:
                        # 최근 결과의 통계 반환
                        return data[-1] if isinstance(data[-1], dict) else {}
            return {}
        except Exception as e:
            logger.error(f"❌ 팩트 체크 통계 로드 실패: {e}")
            return {}
    
    def _load_financial_data(self) -> Dict[str, Any]:
        """금융 데이터 로드"""
        try:
            file_path = "data/financial_data.json"
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"❌ 금융 데이터 로드 실패: {e}")
            return {}
    
    def _load_notification_stats(self) -> Dict[str, Any]:
        """알림 통계 로드"""
        try:
            file_path = "data/notification_results.json"
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('statistics', {})
            return {}
        except Exception as e:
            logger.error(f"❌ 알림 통계 로드 실패: {e}")
            return {}
    
    def _load_activity_log(self) -> List[Dict[str, Any]]:
        """활동 로그 로드"""
        try:
            file_path = "data/activity_log.json"
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"❌ 활동 로그 로드 실패: {e}")
            return []
    
    def _get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 확인"""
        status = {}
        
        # 크롤러 상태
        crawler_stats = self._load_crawler_stats()
        status['크롤러'] = {
            'healthy': crawler_stats.get('total_articles', 0) > 0,
            'message': f"총 {crawler_stats.get('total_articles', 0)}개 기사 수집"
        }
        
        # 팩트 체크 상태
        fact_check_stats = self._load_fact_check_stats()
        status['팩트 체크'] = {
            'healthy': fact_check_stats.get('total_checks', 0) > 0,
            'message': f"총 {fact_check_stats.get('total_checks', 0)}개 기사 검증"
        }
        
        # 금융 데이터 상태
        financial_data = self._load_financial_data()
        status['금융 데이터'] = {
            'healthy': len(financial_data.get('stocks', {})) > 0,
            'message': f"{len(financial_data.get('stocks', {}))}개 종목 데이터"
        }
        
        # 알림 시스템 상태
        notification_stats = self._load_notification_stats()
        status['알림 시스템'] = {
            'healthy': notification_stats.get('total_notifications', 0) >= 0,
            'message': f"총 {notification_stats.get('total_notifications', 0)}개 알림 전송"
        }
        
        return status
    
    def run(self, debug: bool = False, host: str = '0.0.0.0', port: int = 8050):
        """대시보드 실행"""
        try:
            logger.info(f"🚀 대시보드 시작: http://{host}:{port}")
            self.app.run_server(debug=debug, host=host, port=port)
        except Exception as e:
            logger.error(f"❌ 대시보드 실행 실패: {e}")

# CSS 스타일 추가
app = dash.Dash(__name__)
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Auto Finance Dashboard</title>
        {%favicon%}
        {%css%}
        <style>
            .stat-card {
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                flex: 1;
                margin: 0 10px;
            }
            .stat-card h3 {
                margin: 0;
                color: #2c3e50;
                font-size: 2em;
            }
            .stat-card p {
                margin: 5px 0 0 0;
                color: #7f8c8d;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# 대시보드 인스턴스 생성
dashboard = DashboardApp()

if __name__ == '__main__':
    dashboard.run(debug=True) 