"""
📊 실시간 대시보드 (초기 버전)
Plotly Dash 기반 기사/통계/오류 현황 시각화
"""

import dash
from dash import html, dcc, dash_table
import plotly.express as px
import pandas as pd
from pathlib import Path
import json

# 데이터 로딩 함수

def load_statistics():
    stats_file = Path("data/statistics.json")
    if stats_file.exists():
        with open(stats_file, encoding="utf-8") as f:
            return json.load(f)
    return {}

def load_recent_articles():
    db_file = Path("data/stock_news.db")
    if not db_file.exists():
        return []
    import sqlite3
    with sqlite3.connect(db_file) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM crawled_articles ORDER BY crawled_at DESC LIMIT 20")
        return [dict(row) for row in cursor.fetchall()]

# 대시보드 앱 생성
app = dash.Dash(__name__)

stats = load_statistics()
articles = load_recent_articles()

# 통계 데이터 프레임
stats_df = pd.DataFrame([stats['stats']]) if 'stats' in stats else pd.DataFrame([])

# 레이아웃
app.layout = html.Div([
    html.H1("📈 주식 뉴스 자동화 대시보드"),
    html.H2("최근 통계"),
    dash_table.DataTable(
        data=stats_df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in stats_df.columns],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center'},
    ),
    html.H2("최근 기사 20건"),
    dash_table.DataTable(
        data=articles,
        columns=[{"name": i, "id": i} for i in articles[0].keys()] if articles else [],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left'},
        page_size=20
    ),
])

if __name__ == "__main__":
    app.run(debug=True, port=8050) 