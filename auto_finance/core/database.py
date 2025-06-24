"""
🗄️ 데이터베이스 관리 시스템
SQLite를 사용한 기사 데이터 저장 및 관리
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

class Database:
    def __init__(self, db_path: str = "data/stock_news.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 크롤링된 기사 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS crawled_articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    summary TEXT,
                    source TEXT,
                    url TEXT UNIQUE,
                    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 생성된 콘텐츠 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS generated_contents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    body TEXT,
                    summary TEXT,
                    source TEXT,
                    url TEXT,
                    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 통계 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE UNIQUE,
                    articles_crawled INTEGER DEFAULT 0,
                    articles_generated INTEGER DEFAULT 0,
                    articles_saved INTEGER DEFAULT 0,
                    errors INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def save_crawled_articles(self, articles: List[Dict[str, Any]]) -> int:
        """크롤링된 기사들을 데이터베이스에 저장"""
        saved_count = 0
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for article in articles:
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO crawled_articles 
                        (title, content, summary, source, url)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        article.get('title', ''),
                        article.get('content', ''),
                        article.get('summary', ''),
                        article.get('source', ''),
                        article.get('url', '')
                    ))
                    if cursor.rowcount > 0:
                        saved_count += 1
                except Exception as e:
                    print(f"❌ 기사 저장 실패: {e}")
            conn.commit()
        return saved_count
    
    def save_generated_content(self, content: Dict[str, Any]) -> bool:
        """생성된 콘텐츠를 데이터베이스에 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO generated_contents 
                    (title, body, summary, source, url)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    content.get('title', ''),
                    content.get('body', ''),
                    content.get('summary', ''),
                    content.get('source', ''),
                    content.get('url', '')
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ 콘텐츠 저장 실패: {e}")
            return False
    
    def save_statistics(self, stats: Dict[str, Any]):
        """일일 통계를 데이터베이스에 저장"""
        today = datetime.now().date()
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO statistics 
                    (date, articles_crawled, articles_generated, articles_saved, errors)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    today,
                    stats.get('articles_crawled', 0),
                    stats.get('articles_generated', 0),
                    stats.get('articles_saved', 0),
                    stats.get('errors', 0)
                ))
                conn.commit()
        except Exception as e:
            print(f"❌ 통계 저장 실패: {e}")
    
    def get_recent_articles(self, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 크롤링된 기사 조회"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM crawled_articles 
                ORDER BY crawled_at DESC 
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_recent_contents(self, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 생성된 콘텐츠 조회"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM generated_contents 
                ORDER BY generated_at DESC 
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()] 