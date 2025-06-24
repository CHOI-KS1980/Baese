"""
📊 시장 감정 분석 시스템
다중 기법을 활용한 고도화된 시장 감정 분석
"""

import asyncio
import json
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from textblob import TextBlob
import yfinance as yf
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from auto_finance.utils.logger import setup_logger
from auto_finance.config.settings import FINANCIAL_CONFIG

logger = setup_logger(__name__)

@dataclass
class SentimentScore:
    """감정 점수 데이터 클래스"""
    positive: float
    negative: float
    neutral: float
    compound: float
    confidence: float
    source: str
    timestamp: datetime

@dataclass
class MarketSentiment:
    """시장 감정 데이터 클래스"""
    overall_sentiment: float
    sentiment_trend: str
    confidence_score: float
    sources_analyzed: int
    sentiment_scores: List[SentimentScore]
    market_indicators: Dict[str, Any]
    timestamp: datetime

@dataclass
class NewsSentiment:
    """뉴스 감정 데이터 클래스"""
    article_id: str
    title_sentiment: SentimentScore
    content_sentiment: SentimentScore
    overall_sentiment: SentimentScore
    keywords: List[str]
    impact_score: float
    timestamp: datetime

class MarketSentimentAnalyzer:
    """시장 감정 분석 시스템"""
    
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
        
        # 한국어 감정 사전 확장
        self.korean_sentiment_words = {
            'positive': [
                '상승', '급등', '호재', '성장', '실적', '수익', '이익', '증가', '개선', '회복',
                '강세', '돌파', '상향', '긍정', '낙관', '기대', '희망', '성공', '돌파', '신기록'
            ],
            'negative': [
                '하락', '급락', '악재', '손실', '감소', '악화', '위험', '우려', '불안', '공포',
                '약세', '하향', '부정', '비관', '실망', '실패', '위기', '폭락', '침체', '파산'
            ]
        }
        
        # 감정 분석 가중치
        self.sentiment_weights = {
            'vader': 0.3,
            'textblob': 0.2,
            'custom_korean': 0.3,
            'market_indicators': 0.2
        }
        
        self.stats = {
            'total_analyses': 0,
            'successful_analyses': 0,
            'failed_analyses': 0,
            'average_processing_time': 0.0,
            'sentiment_trends': {
                'positive': 0,
                'neutral': 0,
                'negative': 0
            }
        }
    
    async def analyze_news_sentiment(self, articles: List[Dict[str, Any]]) -> List[NewsSentiment]:
        """뉴스 기사 감정 분석"""
        logger.info(f"📊 뉴스 감정 분석 시작: {len(articles)}개 기사")
        
        results = []
        start_time = time.time()
        
        try:
            for article in articles:
                try:
                    sentiment = await self._analyze_single_article(article)
                    results.append(sentiment)
                    self.stats['successful_analyses'] += 1
                    
                except Exception as e:
                    logger.error(f"❌ 기사 감정 분석 실패: {e}")
                    self.stats['failed_analyses'] += 1
                    continue
            
            processing_time = time.time() - start_time
            self.stats['total_analyses'] += len(articles)
            self.stats['average_processing_time'] = processing_time / len(articles) if articles else 0
            
            logger.info(f"✅ 뉴스 감정 분석 완료: {len(results)}개 성공, {processing_time:.2f}초")
            return results
            
        except Exception as e:
            logger.error(f"❌ 뉴스 감정 분석 실패: {e}")
            return []
    
    async def _analyze_single_article(self, article: Dict[str, Any]) -> NewsSentiment:
        """단일 기사 감정 분석"""
        article_id = article.get('id', str(hash(article.get('title', ''))))
        title = article.get('title', '')
        content = article.get('content', '')
        
        # 제목 감정 분석
        title_sentiment = await self._analyze_text_sentiment(title)
        
        # 본문 감정 분석
        content_sentiment = await self._analyze_text_sentiment(content)
        
        # 전체 감정 점수 계산
        overall_sentiment = self._calculate_overall_sentiment(title_sentiment, content_sentiment)
        
        # 키워드 추출
        keywords = self._extract_keywords(title + ' ' + content)
        
        # 영향도 점수 계산
        impact_score = self._calculate_impact_score(article, overall_sentiment)
        
        return NewsSentiment(
            article_id=article_id,
            title_sentiment=title_sentiment,
            content_sentiment=content_sentiment,
            overall_sentiment=overall_sentiment,
            keywords=keywords,
            impact_score=impact_score,
            timestamp=datetime.now()
        )
    
    async def _analyze_text_sentiment(self, text: str) -> SentimentScore:
        """텍스트 감정 분석"""
        if not text or len(text.strip()) < 10:
            return SentimentScore(0.0, 0.0, 1.0, 0.0, 0.0, 'empty_text', datetime.now())
        
        # VADER 감정 분석
        vader_scores = self.vader_analyzer.polarity_scores(text)
        
        # TextBlob 감정 분석
        blob = TextBlob(text)
        textblob_sentiment = blob.sentiment.polarity
        
        # 한국어 커스텀 감정 분석
        korean_sentiment = self._analyze_korean_sentiment(text)
        
        # 가중 평균 계산
        compound_score = (
            vader_scores['compound'] * self.sentiment_weights['vader'] +
            textblob_sentiment * self.sentiment_weights['textblob'] +
            korean_sentiment * self.sentiment_weights['custom_korean']
        )
        
        # 신뢰도 계산
        confidence = self._calculate_sentiment_confidence(text, vader_scores, textblob_sentiment)
        
        return SentimentScore(
            positive=vader_scores['pos'],
            negative=vader_scores['neg'],
            neutral=vader_scores['neu'],
            compound=compound_score,
            confidence=confidence,
            source='ensemble',
            timestamp=datetime.now()
        )
    
    def _analyze_korean_sentiment(self, text: str) -> float:
        """한국어 커스텀 감정 분석"""
        positive_count = 0
        negative_count = 0
        
        for word in self.korean_sentiment_words['positive']:
            if word in text:
                positive_count += 1
        
        for word in self.korean_sentiment_words['negative']:
            if word in text:
                negative_count += 1
        
        total_words = len(text.split())
        if total_words == 0:
            return 0.0
        
        # 감정 점수 계산
        sentiment_score = (positive_count - negative_count) / total_words
        
        # -1에서 1 사이로 정규화
        return max(-1.0, min(1.0, sentiment_score * 10))
    
    def _calculate_sentiment_confidence(self, text: str, vader_scores: Dict, textblob_sentiment: float) -> float:
        """감정 분석 신뢰도 계산"""
        # 텍스트 길이 기반 신뢰도
        length_confidence = min(len(text) / 100, 1.0)
        
        # VADER 신뢰도
        vader_confidence = abs(vader_scores['compound'])
        
        # TextBlob 신뢰도
        textblob_confidence = abs(textblob_sentiment)
        
        # 평균 신뢰도
        avg_confidence = (length_confidence + vader_confidence + textblob_confidence) / 3
        
        return min(avg_confidence, 1.0)
    
    def _calculate_overall_sentiment(self, title_sentiment: SentimentScore, content_sentiment: SentimentScore) -> SentimentScore:
        """전체 감정 점수 계산 (제목 가중치 40%, 본문 60%)"""
        title_weight = 0.4
        content_weight = 0.6
        
        compound = (title_sentiment.compound * title_weight + 
                   content_sentiment.compound * content_weight)
        
        positive = (title_sentiment.positive * title_weight + 
                   content_sentiment.positive * content_weight)
        
        negative = (title_sentiment.negative * title_weight + 
                   content_sentiment.negative * content_weight)
        
        neutral = (title_sentiment.neutral * title_weight + 
                  content_sentiment.neutral * content_weight)
        
        confidence = (title_sentiment.confidence * title_weight + 
                     content_sentiment.confidence * content_weight)
        
        return SentimentScore(
            positive=positive,
            negative=negative,
            neutral=neutral,
            compound=compound,
            confidence=confidence,
            source='weighted_ensemble',
            timestamp=datetime.now()
        )
    
    def _extract_keywords(self, text: str) -> List[str]:
        """키워드 추출"""
        # 간단한 키워드 추출 (실제로는 더 정교한 NLP 사용)
        keywords = []
        
        # 금융 관련 키워드
        financial_keywords = [
            '주식', '투자', '경제', '금융', '시장', '분석', '전망', '전략',
            '포트폴리오', '리스크', '수익률', '성장', '가치', '배당',
            '상승', '하락', '급등', '급락', '호재', '악재'
        ]
        
        for keyword in financial_keywords:
            if keyword in text:
                keywords.append(keyword)
        
        return keywords[:10]  # 최대 10개
    
    def _calculate_impact_score(self, article: Dict[str, Any], sentiment: SentimentScore) -> float:
        """영향도 점수 계산"""
        impact_score = 0.0
        
        # 감정 강도
        impact_score += abs(sentiment.compound) * 0.3
        
        # 기사 길이
        content_length = len(article.get('content', ''))
        if content_length > 500:
            impact_score += 0.2
        elif content_length > 200:
            impact_score += 0.1
        
        # 소스 신뢰도
        source = article.get('source', '').lower()
        if '네이버' in source or '한국경제' in source:
            impact_score += 0.2
        elif '매일경제' in source or '이데일리' in source:
            impact_score += 0.15
        
        # 키워드 중요도
        keywords = self._extract_keywords(article.get('title', '') + ' ' + article.get('content', ''))
        important_keywords = ['급등', '급락', '호재', '악재', '돌파', '폭락']
        for keyword in important_keywords:
            if keyword in keywords:
                impact_score += 0.1
        
        return min(impact_score, 1.0)
    
    async def analyze_market_sentiment(self, news_sentiments: List[NewsSentiment]) -> MarketSentiment:
        """전체 시장 감정 분석"""
        logger.info("📈 전체 시장 감정 분석 시작")
        
        try:
            if not news_sentiments:
                return self._create_empty_market_sentiment()
            
            # 뉴스 감정 집계
            overall_sentiment = self._aggregate_news_sentiments(news_sentiments)
            
            # 시장 지표 수집
            market_indicators = await self._collect_market_indicators()
            
            # 감정 트렌드 분석
            sentiment_trend = self._analyze_sentiment_trend(news_sentiments)
            
            # 신뢰도 계산
            confidence_score = self._calculate_market_confidence(news_sentiments, market_indicators)
            
            # 통계 업데이트
            self._update_sentiment_trends(overall_sentiment)
            
            market_sentiment = MarketSentiment(
                overall_sentiment=overall_sentiment,
                sentiment_trend=sentiment_trend,
                confidence_score=confidence_score,
                sources_analyzed=len(news_sentiments),
                sentiment_scores=[ns.overall_sentiment for ns in news_sentiments],
                market_indicators=market_indicators,
                timestamp=datetime.now()
            )
            
            logger.info(f"✅ 시장 감정 분석 완료: {overall_sentiment:.3f} ({sentiment_trend})")
            return market_sentiment
            
        except Exception as e:
            logger.error(f"❌ 시장 감정 분석 실패: {e}")
            return self._create_empty_market_sentiment()
    
    def _aggregate_news_sentiments(self, news_sentiments: List[NewsSentiment]) -> float:
        """뉴스 감정 집계"""
        if not news_sentiments:
            return 0.0
        
        # 영향도 가중 평균
        total_weight = 0
        weighted_sum = 0
        
        for sentiment in news_sentiments:
            weight = sentiment.impact_score
            total_weight += weight
            weighted_sum += sentiment.overall_sentiment.compound * weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    async def _collect_market_indicators(self) -> Dict[str, Any]:
        """시장 지표 수집"""
        indicators = {}
        
        try:
            # 주요 지수 데이터
            indices = ['^KS11', '^KQ11', '^GSPC', '^DJI', '^IXIC']
            
            for index in indices:
                try:
                    ticker = yf.Ticker(index)
                    hist = ticker.history(period='5d')
                    
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                        prev_price = hist['Close'].iloc[-2]
                        change_pct = ((current_price - prev_price) / prev_price) * 100
                        
                        indicators[index] = {
                            'current_price': current_price,
                            'change_pct': change_pct,
                            'trend': 'up' if change_pct > 0 else 'down' if change_pct < 0 else 'flat'
                        }
                        
                except Exception as e:
                    logger.warning(f"지수 데이터 수집 실패 {index}: {e}")
                    continue
            
            # VIX 지수 (변동성)
            try:
                vix = yf.Ticker('^VIX')
                vix_hist = vix.history(period='5d')
                if not vix_hist.empty:
                    indicators['vix'] = {
                        'current_value': vix_hist['Close'].iloc[-1],
                        'trend': 'high' if vix_hist['Close'].iloc[-1] > 20 else 'low'
                    }
            except Exception as e:
                logger.warning(f"VIX 데이터 수집 실패: {e}")
            
        except Exception as e:
            logger.error(f"시장 지표 수집 실패: {e}")
        
        return indicators
    
    def _analyze_sentiment_trend(self, news_sentiments: List[NewsSentiment]) -> str:
        """감정 트렌드 분석"""
        if not news_sentiments:
            return 'neutral'
        
        # 최근 기사들의 감정 분석
        recent_sentiments = news_sentiments[-10:]  # 최근 10개
        
        positive_count = 0
        negative_count = 0
        
        for sentiment in recent_sentiments:
            if sentiment.overall_sentiment.compound > 0.1:
                positive_count += 1
            elif sentiment.overall_sentiment.compound < -0.1:
                negative_count += 1
        
        if positive_count > negative_count * 1.5:
            return 'strongly_positive'
        elif positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count * 1.5:
            return 'strongly_negative'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _calculate_market_confidence(self, news_sentiments: List[NewsSentiment], market_indicators: Dict[str, Any]) -> float:
        """시장 신뢰도 계산"""
        confidence = 0.0
        
        # 뉴스 신뢰도
        if news_sentiments:
            avg_news_confidence = sum(ns.overall_sentiment.confidence for ns in news_sentiments) / len(news_sentiments)
            confidence += avg_news_confidence * 0.6
        
        # 시장 지표 신뢰도
        if market_indicators:
            confidence += 0.4
        
        return min(confidence, 1.0)
    
    def _update_sentiment_trends(self, overall_sentiment: float):
        """감정 트렌드 통계 업데이트"""
        if overall_sentiment > 0.1:
            self.stats['sentiment_trends']['positive'] += 1
        elif overall_sentiment < -0.1:
            self.stats['sentiment_trends']['negative'] += 1
        else:
            self.stats['sentiment_trends']['neutral'] += 1
    
    def _create_empty_market_sentiment(self) -> MarketSentiment:
        """빈 시장 감정 객체 생성"""
        return MarketSentiment(
            overall_sentiment=0.0,
            sentiment_trend='neutral',
            confidence_score=0.0,
            sources_analyzed=0,
            sentiment_scores=[],
            market_indicators={},
            timestamp=datetime.now()
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """시스템 통계 반환"""
        total_trends = sum(self.stats['sentiment_trends'].values())
        
        return {
            'total_analyses': self.stats['total_analyses'],
            'successful_analyses': self.stats['successful_analyses'],
            'failed_analyses': self.stats['failed_analyses'],
            'success_rate': (self.stats['successful_analyses'] / self.stats['total_analyses'] * 100) if self.stats['total_analyses'] > 0 else 0,
            'average_processing_time': self.stats['average_processing_time'],
            'sentiment_distribution': {
                'positive': (self.stats['sentiment_trends']['positive'] / total_trends * 100) if total_trends > 0 else 0,
                'neutral': (self.stats['sentiment_trends']['neutral'] / total_trends * 100) if total_trends > 0 else 0,
                'negative': (self.stats['sentiment_trends']['negative'] / total_trends * 100) if total_trends > 0 else 0
            }
        }
    
    def save_statistics(self, file_path: str = "data/sentiment_analysis_stats.json"):
        """통계 저장"""
        try:
            stats = self.get_statistics()
            stats['timestamp'] = datetime.now().isoformat()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"💾 감정 분석 통계 저장: {file_path}")
            
        except Exception as e:
            logger.error(f"❌ 감정 분석 통계 저장 실패: {e}")

# 전역 인스턴스
sentiment_analyzer = MarketSentimentAnalyzer() 