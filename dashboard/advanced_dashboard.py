"""
📊 고도화된 Auto Finance 대시보드
AI 앙상블, 감정 분석, 고급 콘텐츠 생성을 통합 모니터링
"""

import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
import asyncio
import threading
import time

# Auto Finance 모듈 임포트
from auto_finance.core.ai_ensemble import ai_ensemble
from auto_finance.core.market_sentiment_analyzer import sentiment_analyzer
from auto_finance.core.advanced_content_generator import advanced_content_generator
from auto_finance.utils.logger import setup_logger

logger = setup_logger(__name__)

# Dash 앱 초기화
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Auto Finance 고도화 대시보드"

# 전역 변수
system_status = {}
last_update = datetime.now()

class AdvancedDashboard:
    """고도화된 대시보드 클래스"""
    
    def __init__(self):
        self.app = app
        self.setup_layout()
        self.setup_callbacks()
        
    def setup_layout(self):
        """대시보드 레이아웃 설정"""
        self.app.layout = dbc.Container([
            # 헤더
            dbc.Row([
                dbc.Col([
                    html.H1("🚀 Auto Finance 고도화 대시보드", 
                           className="text-center mb-4"),
                    html.P("AI 앙상블, 감정 분석, 고급 콘텐츠 생성을 통합 모니터링",
                           className="text-center text-muted")
                ])
            ]),
            
            # 실시간 상태 카드
            dbc.Row([
                dbc.Col(self.create_status_card("시스템 상태", "system"), width=3),
                dbc.Col(self.create_status_card("AI 앙상블", "ai_ensemble"), width=3),
                dbc.Col(self.create_status_card("감정 분석", "sentiment"), width=3),
                dbc.Col(self.create_status_card("콘텐츠 생성", "content"), width=3)
            ], className="mb-4"),
            
            # 메인 차트 영역
            dbc.Row([
                # 왼쪽 컬럼
                dbc.Col([
                    # AI 앙상블 성능 차트
                    dbc.Card([
                        dbc.CardHeader("🤖 AI 앙상블 성능"),
                        dbc.CardBody([
                            dcc.Graph(id='ai-ensemble-chart', style={'height': '300px'})
                        ])
                    ], className="mb-4"),
                    
                    # 감정 분석 트렌드
                    dbc.Card([
                        dbc.CardHeader("📊 시장 감정 트렌드"),
                        dbc.CardBody([
                            dcc.Graph(id='sentiment-trend-chart', style={'height': '300px'})
                        ])
                    ])
                ], width=6),
                
                # 오른쪽 컬럼
                dbc.Col([
                    # 콘텐츠 품질 분석
                    dbc.Card([
                        dbc.CardHeader("✍️ 콘텐츠 품질 분석"),
                        dbc.CardBody([
                            dcc.Graph(id='content-quality-chart', style={'height': '300px'})
                        ])
                    ], className="mb-4"),
                    
                    # 성능 지표
                    dbc.Card([
                        dbc.CardHeader("⚡ 성능 지표"),
                        dbc.CardBody([
                            dcc.Graph(id='performance-metrics-chart', style={'height': '300px'})
                        ])
                    ])
                ], width=6)
            ]),
            
            # 상세 통계 테이블
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("📋 상세 통계"),
                        dbc.CardBody([
                            html.Div(id='detailed-stats-table')
                        ])
                    ])
                ])
            ], className="mt-4"),
            
            # 자동 새로고침
            dcc.Interval(
                id='interval-component',
                interval=30*1000,  # 30초마다 새로고침
                n_intervals=0
            ),
            
            # 숨겨진 div (데이터 저장용)
            html.Div(id='hidden-data', style={'display': 'none'})
            
        ], fluid=True)
    
    def create_status_card(self, title: str, card_type: str) -> dbc.Card:
        """상태 카드 생성"""
        return dbc.Card([
            dbc.CardBody([
                html.H4(title, className="card-title"),
                html.H2(id=f'{card_type}-status', className="text-center"),
                html.P(id=f'{card_type}-description', className="card-text text-center")
            ])
        ])
    
    def setup_callbacks(self):
        """콜백 함수 설정"""
        
        @self.app.callback(
            [Output('hidden-data', 'children')],
            [Input('interval-component', 'n_intervals')]
        )
        def update_data(n):
            """데이터 업데이트"""
            global system_status, last_update
            
            try:
                # 시스템 상태 수집
                system_status = self.collect_system_status()
                last_update = datetime.now()
                
                return [json.dumps(system_status)]
                
            except Exception as e:
                logger.error(f"데이터 업데이트 실패: {e}")
                return [json.dumps({})]
        
        @self.app.callback(
            [Output('system-status', 'children'),
             Output('system-description', 'children')],
            [Input('hidden-data', 'children')]
        )
        def update_system_status(data):
            """시스템 상태 업데이트"""
            if not data:
                return "❌", "데이터 없음"
            
            try:
                status = json.loads(data)
                is_running = status.get('is_running', False)
                success_rate = status.get('execution_stats', {}).get('success_rate', 0)
                
                if is_running:
                    return "🟢 실행 중", f"성공률: {success_rate:.1f}%"
                else:
                    return "🔴 정지", f"마지막 실행: {success_rate:.1f}% 성공"
                    
            except Exception as e:
                return "❌", f"오류: {e}"
        
        @self.app.callback(
            [Output('ai-ensemble-status', 'children'),
             Output('ai-ensemble-description', 'children')],
            [Input('hidden-data', 'children')]
        )
        def update_ai_ensemble_status(data):
            """AI 앙상블 상태 업데이트"""
            if not data:
                return "❌", "데이터 없음"
            
            try:
                status = json.loads(data)
                ai_stats = status.get('ai_ensemble_status', {})
                success_rate = ai_stats.get('success_rate', 0)
                total_cost = ai_stats.get('total_cost', 0)
                
                return f"{success_rate:.1f}%", f"비용: ${total_cost:.4f}"
                
            except Exception as e:
                return "❌", f"오류: {e}"
        
        @self.app.callback(
            [Output('sentiment-status', 'children'),
             Output('sentiment-description', 'children')],
            [Input('hidden-data', 'children')]
        )
        def update_sentiment_status(data):
            """감정 분석 상태 업데이트"""
            if not data:
                return "❌", "데이터 없음"
            
            try:
                status = json.loads(data)
                sentiment_stats = status.get('sentiment_analyzer_status', {})
                total_analyses = sentiment_stats.get('total_analyses', 0)
                success_rate = sentiment_stats.get('success_rate', 0)
                
                return f"{total_analyses}개", f"성공률: {success_rate:.1f}%"
                
            except Exception as e:
                return "❌", f"오류: {e}"
        
        @self.app.callback(
            [Output('content-status', 'children'),
             Output('content-description', 'children')],
            [Input('hidden-data', 'children')]
        )
        def update_content_status(data):
            """콘텐츠 생성 상태 업데이트"""
            if not data:
                return "❌", "데이터 없음"
            
            try:
                status = json.loads(data)
                content_stats = status.get('content_generator_status', {})
                total_generations = content_stats.get('total_generations', 0)
                success_rate = content_stats.get('success_rate', 0)
                
                return f"{total_generations}개", f"성공률: {success_rate:.1f}%"
                
            except Exception as e:
                return "❌", f"오류: {e}"
        
        @self.app.callback(
            Output('ai-ensemble-chart', 'figure'),
            [Input('hidden-data', 'children')]
        )
        def update_ai_ensemble_chart(data):
            """AI 앙상블 차트 업데이트"""
            if not data:
                return self.create_empty_chart("AI 앙상블 데이터 없음")
            
            try:
                status = json.loads(data)
                ai_stats = status.get('ai_ensemble_status', {})
                
                # 모델별 성능 데이터
                models = ['Gemini', 'GPT-4', 'Claude']
                success_rates = [
                    ai_stats.get('success_rate', 0),
                    ai_stats.get('success_rate', 0),
                    ai_stats.get('success_rate', 0)
                ]
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=models,
                        y=success_rates,
                        marker_color=['#4285F4', '#10A37F', '#FF6B35'],
                        text=[f'{rate:.1f}%' for rate in success_rates],
                        textposition='auto'
                    )
                ])
                
                fig.update_layout(
                    title="AI 모델별 성공률",
                    xaxis_title="모델",
                    yaxis_title="성공률 (%)",
                    yaxis_range=[0, 100],
                    showlegend=False
                )
                
                return fig
                
            except Exception as e:
                return self.create_empty_chart(f"AI 앙상블 차트 오류: {e}")
        
        @self.app.callback(
            Output('sentiment-trend-chart', 'figure'),
            [Input('hidden-data', 'children')]
        )
        def update_sentiment_trend_chart(data):
            """감정 트렌드 차트 업데이트"""
            if not data:
                return self.create_empty_chart("감정 분석 데이터 없음")
            
            try:
                # 최근 실행 데이터 로드
                sentiment_data = self.load_recent_sentiment_data()
                
                if not sentiment_data:
                    return self.create_empty_chart("감정 데이터 없음")
                
                df = pd.DataFrame(sentiment_data)
                
                fig = go.Figure()
                
                # 감정 점수 트렌드
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=df['overall_sentiment'],
                    mode='lines+markers',
                    name='시장 감정',
                    line=dict(color='#1f77b4', width=2)
                ))
                
                fig.update_layout(
                    title="시장 감정 트렌드",
                    xaxis_title="시간",
                    yaxis_title="감정 점수",
                    yaxis_range=[-1, 1],
                    hovermode='x unified'
                )
                
                return fig
                
            except Exception as e:
                return self.create_empty_chart(f"감정 트렌드 차트 오류: {e}")
        
        @self.app.callback(
            Output('content-quality-chart', 'figure'),
            [Input('hidden-data', 'children')]
        )
        def update_content_quality_chart(data):
            """콘텐츠 품질 차트 업데이트"""
            if not data:
                return self.create_empty_chart("콘텐츠 데이터 없음")
            
            try:
                # 최근 콘텐츠 데이터 로드
                content_data = self.load_recent_content_data()
                
                if not content_data:
                    return self.create_empty_chart("콘텐츠 데이터 없음")
                
                df = pd.DataFrame(content_data)
                
                fig = make_subplots(
                    rows=2, cols=1,
                    subplot_titles=('SEO 점수 분포', '가독성 점수 분포'),
                    vertical_spacing=0.1
                )
                
                # SEO 점수 히스토그램
                fig.add_trace(
                    go.Histogram(x=df['seo_score'], name='SEO 점수', nbinsx=10),
                    row=1, col=1
                )
                
                # 가독성 점수 히스토그램
                fig.add_trace(
                    go.Histogram(x=df['readability_score'], name='가독성 점수', nbinsx=10),
                    row=2, col=1
                )
                
                fig.update_layout(
                    title="콘텐츠 품질 분석",
                    height=400,
                    showlegend=False
                )
                
                return fig
                
            except Exception as e:
                return self.create_empty_chart(f"콘텐츠 품질 차트 오류: {e}")
        
        @self.app.callback(
            Output('performance-metrics-chart', 'figure'),
            [Input('hidden-data', 'children')]
        )
        def update_performance_metrics_chart(data):
            """성능 지표 차트 업데이트"""
            if not data:
                return self.create_empty_chart("성능 데이터 없음")
            
            try:
                status = json.loads(data)
                performance = status.get('performance_metrics', {})
                
                metrics = ['캐시 히트율', 'API 호출', '오류율', '총 비용']
                values = [
                    performance.get('cache_hits', 0) / max(performance.get('cache_hits', 0) + performance.get('cache_misses', 1), 1) * 100,
                    performance.get('api_calls', 0),
                    performance.get('error_rate', 0),
                    performance.get('total_cost', 0) * 1000  # 시각화를 위해 1000배
                ]
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=metrics,
                        y=values,
                        marker_color=['#2E8B57', '#4682B4', '#DC143C', '#FFD700'],
                        text=[f'{v:.1f}' for v in values],
                        textposition='auto'
                    )
                ])
                
                fig.update_layout(
                    title="성능 지표",
                    xaxis_title="지표",
                    yaxis_title="값",
                    showlegend=False
                )
                
                return fig
                
            except Exception as e:
                return self.create_empty_chart(f"성능 지표 차트 오류: {e}")
        
        @self.app.callback(
            Output('detailed-stats-table', 'children'),
            [Input('hidden-data', 'children')]
        )
        def update_detailed_stats_table(data):
            """상세 통계 테이블 업데이트"""
            if not data:
                return html.P("데이터 없음")
            
            try:
                status = json.loads(data)
                
                # 테이블 데이터 생성
                table_data = [
                    ["시스템 실행 횟수", f"{status.get('execution_stats', {}).get('total_executions', 0)}회"],
                    ["성공률", f"{status.get('execution_stats', {}).get('success_rate', 0):.1f}%"],
                    ["AI 앙상블 요청", f"{status.get('ai_ensemble_status', {}).get('total_requests', 0)}회"],
                    ["감정 분석", f"{status.get('sentiment_analyzer_status', {}).get('total_analyses', 0)}회"],
                    ["콘텐츠 생성", f"{status.get('content_generator_status', {}).get('total_generations', 0)}개"],
                    ["총 API 비용", f"${status.get('performance_metrics', {}).get('total_cost', 0):.4f}"],
                    ["캐시 히트율", f"{status.get('performance_metrics', {}).get('cache_hits', 0)}/{status.get('performance_metrics', {}).get('cache_hits', 0) + status.get('performance_metrics', {}).get('cache_misses', 0)}"],
                    ["마지막 업데이트", last_update.strftime('%Y-%m-%d %H:%M:%S')]
                ]
                
                # 테이블 생성
                table_rows = []
                for row in table_data:
                    table_rows.append(html.Tr([
                        html.Td(row[0], style={'font-weight': 'bold'}),
                        html.Td(row[1])
                    ]))
                
                return dbc.Table([
                    html.Thead(html.Tr([
                        html.Th("지표"),
                        html.Th("값")
                    ])),
                    html.Tbody(table_rows)
                ], bordered=True, hover=True)
                
            except Exception as e:
                return html.P(f"테이블 생성 오류: {e}")
    
    def collect_system_status(self) -> Dict[str, Any]:
        """시스템 상태 수집"""
        try:
            # 각 모듈의 통계 수집
            ai_stats = ai_ensemble.get_statistics()
            sentiment_stats = sentiment_analyzer.get_statistics()
            content_stats = advanced_content_generator.get_statistics()
            
            # 성능 지표 계산
            performance_metrics = {
                'api_calls': ai_stats.get('total_requests', 0) + sentiment_stats.get('total_analyses', 0),
                'total_cost': ai_stats.get('total_cost', 0.0),
                'cache_hits': 0,  # 캐시 매니저에서 가져와야 함
                'cache_misses': 0,
                'error_rate': 0.0
            }
            
            # 오류율 계산
            total_operations = performance_metrics['api_calls']
            failed_operations = (
                ai_stats.get('failed_requests', 0) +
                sentiment_stats.get('failed_analyses', 0) +
                content_stats.get('failed_generations', 0)
            )
            
            if total_operations > 0:
                performance_metrics['error_rate'] = (failed_operations / total_operations) * 100
            
            return {
                'is_running': False,  # 실제로는 시스템 상태 확인 필요
                'execution_stats': {
                    'total_executions': 0,
                    'successful_executions': 0,
                    'failed_executions': 0,
                    'success_rate': 0.0
                },
                'ai_ensemble_status': ai_stats,
                'sentiment_analyzer_status': sentiment_stats,
                'content_generator_status': content_stats,
                'performance_metrics': performance_metrics
            }
            
        except Exception as e:
            logger.error(f"시스템 상태 수집 실패: {e}")
            return {}
    
    def load_recent_sentiment_data(self) -> List[Dict[str, Any]]:
        """최근 감정 데이터 로드"""
        try:
            # 실제로는 데이터베이스나 파일에서 로드
            # 여기서는 샘플 데이터 반환
            return [
                {
                    'timestamp': (datetime.now() - timedelta(hours=i)).isoformat(),
                    'overall_sentiment': 0.1 + (i * 0.05),
                    'sentiment_trend': 'positive' if i % 2 == 0 else 'negative'
                }
                for i in range(24, 0, -1)
            ]
        except Exception as e:
            logger.error(f"감정 데이터 로드 실패: {e}")
            return []
    
    def load_recent_content_data(self) -> List[Dict[str, Any]]:
        """최근 콘텐츠 데이터 로드"""
        try:
            # 실제로는 데이터베이스나 파일에서 로드
            # 여기서는 샘플 데이터 반환
            return [
                {
                    'seo_score': 75 + (i * 2),
                    'readability_score': 0.8 + (i * 0.01),
                    'word_count': 800 + (i * 50),
                    'sentiment_score': 0.1 + (i * 0.02)
                }
                for i in range(20)
            ]
        except Exception as e:
            logger.error(f"콘텐츠 데이터 로드 실패: {e}")
            return []
    
    def create_empty_chart(self, message: str) -> go.Figure:
        """빈 차트 생성"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='white'
        )
        return fig
    
    def run(self, host: str = '0.0.0.0', port: int = 8050, debug: bool = False):
        """대시보드 실행"""
        logger.info(f"🚀 고도화된 대시보드 시작: http://{host}:{port}")
        self.app.run_server(host=host, port=port, debug=debug)

# 전역 인스턴스
advanced_dashboard = AdvancedDashboard()

if __name__ == '__main__':
    advanced_dashboard.run(debug=True) 