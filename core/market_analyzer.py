"""
📊 시장 분석기
뉴스와 금융 데이터 연계 분석 및 시장 예측
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from auto_finance.core.financial_data import FinancialDataCollector

class MarketAnalyzer:
    def __init__(self):
        self.financial_collector = FinancialDataCollector()
        
        # 분석 설정
        self.analysis_config = {
            'correlation_threshold': 0.3,  # 상관관계 임계값
            'sentiment_weight': 0.4,       # 감정 분석 가중치
            'price_weight': 0.3,           # 가격 변동 가중치
            'volume_weight': 0.3           # 거래량 가중치
        }
    
    def analyze_news_market_correlation(self, news_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """뉴스와 시장 데이터 상관관계 분석"""
        try:
            # 시장 데이터 수집
            market_data = self.financial_collector.get_comprehensive_market_data()
            
            # 뉴스 키워드 추출
            news_keywords = self._extract_news_keywords(news_data)
            
            # 섹터별 영향도 분석
            sector_impact = self._analyze_sector_impact(news_keywords, market_data)
            
            # 시장 심리와 뉴스 연관성 분석
            sentiment_correlation = self._analyze_sentiment_correlation(news_data, market_data)
            
            return {
                'news_keywords': news_keywords,
                'sector_impact': sector_impact,
                'sentiment_correlation': sentiment_correlation,
                'market_data': market_data,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ 뉴스-시장 상관관계 분석 실패: {e}")
            return {}
    
    def predict_market_trend(self, news_data: List[Dict[str, Any]], 
                           market_data: Dict[str, Any]) -> Dict[str, Any]:
        """시장 트렌드 예측"""
        try:
            # 뉴스 감정 분석
            news_sentiment = self._analyze_news_sentiment(news_data)
            
            # 기술적 지표 분석
            technical_indicators = self._calculate_technical_indicators(market_data)
            
            # 종합 예측 점수 계산
            prediction_score = self._calculate_prediction_score(
                news_sentiment, technical_indicators, market_data
            )
            
            # 예측 결과 생성
            prediction_result = self._generate_prediction_result(prediction_score)
            
            return {
                'prediction_score': prediction_score,
                'prediction_result': prediction_result,
                'news_sentiment': news_sentiment,
                'technical_indicators': technical_indicators,
                'confidence_level': self._calculate_confidence_level(prediction_score),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ 시장 트렌드 예측 실패: {e}")
            return {}
    
    def generate_investment_recommendations(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """투자 권장사항 생성"""
        recommendations = []
        
        try:
            # 섹터별 권장사항
            sector_impact = analysis_data.get('sector_impact', {})
            for sector, impact in sector_impact.items():
                if impact['score'] > 0.6:
                    recommendations.append({
                        'type': 'sector_buy',
                        'sector': sector,
                        'reason': f'{sector} 섹터 긍정적 뉴스 영향',
                        'confidence': impact['score'],
                        'action': '매수'
                    })
                elif impact['score'] < 0.4:
                    recommendations.append({
                        'type': 'sector_sell',
                        'sector': sector,
                        'reason': f'{sector} 섹터 부정적 뉴스 영향',
                        'confidence': 1 - impact['score'],
                        'action': '매도'
                    })
            
            # 개별 종목 권장사항
            market_data = analysis_data.get('market_data', {})
            stocks = market_data.get('market_overview', {}).get('stocks', {})
            
            for stock_name, stock_data in stocks.items():
                change_percent = stock_data.get('change_percent', 0)
                volume = stock_data.get('volume', 0)
                
                if change_percent > 3 and volume > 1000000:
                    recommendations.append({
                        'type': 'stock_momentum',
                        'stock': stock_name,
                        'reason': f'강한 상승 모멘텀 ({change_percent:.1f}%)',
                        'confidence': min(0.8, abs(change_percent) / 10),
                        'action': '매수'
                    })
                elif change_percent < -3:
                    recommendations.append({
                        'type': 'stock_correction',
                        'stock': stock_name,
                        'reason': f'조정 가능성 ({change_percent:.1f}%)',
                        'confidence': min(0.7, abs(change_percent) / 10),
                        'action': '관망'
                    })
            
            # 시장 전체 권장사항
            sentiment = market_data.get('market_sentiment', {})
            sentiment_score = sentiment.get('sentiment_score', 50)
            
            if sentiment_score > 70:
                recommendations.append({
                    'type': 'market_bullish',
                    'reason': '전체 시장 긍정적 분위기',
                    'confidence': sentiment_score / 100,
                    'action': '적극적 매수'
                })
            elif sentiment_score < 30:
                recommendations.append({
                    'type': 'market_bearish',
                    'reason': '전체 시장 부정적 분위기',
                    'confidence': (100 - sentiment_score) / 100,
                    'action': '관망'
                })
            
        except Exception as e:
            print(f"❌ 투자 권장사항 생성 실패: {e}")
        
        return recommendations
    
    def _extract_news_keywords(self, news_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """뉴스에서 키워드 추출 및 빈도 계산"""
        keywords = {}
        
        # 간단한 키워드 추출 (실제로는 NLP 라이브러리 사용)
        important_keywords = [
            'AI', '반도체', '전기차', '바이오', '게임', '금융', '부동산',
            '금리', '환율', '원유', '금', '달러', '엔화', '위안'
        ]
        
        for news in news_data:
            title = news.get('title', '')
            content = news.get('content', '')
            text = f"{title} {content}"
            
            for keyword in important_keywords:
                if keyword in text:
                    keywords[keyword] = keywords.get(keyword, 0) + 1
        
        return keywords
    
    def _analyze_sector_impact(self, keywords: Dict[str, int], 
                             market_data: Dict[str, Any]) -> Dict[str, Any]:
        """섹터별 영향도 분석"""
        sector_impact = {}
        
        # 섹터별 키워드 매핑
        sector_keywords = {
            '반도체': ['반도체', 'SK하이닉스', '삼성전자'],
            'AI': ['AI', '인공지능', 'NAVER', '카카오'],
            '전기차': ['전기차', 'LG에너지솔루션'],
            '바이오': ['바이오', '제약'],
            '게임': ['게임', '넥슨', '넷마블'],
            '금융': ['금융', '은행', '보험'],
            '원자재': ['원유', '금', '철강']
        }
        
        for sector, sector_kw in sector_keywords.items():
            impact_score = 0
            keyword_count = 0
            
            for kw in sector_kw:
                if kw in keywords:
                    impact_score += keywords[kw]
                    keyword_count += 1
            
            if keyword_count > 0:
                sector_impact[sector] = {
                    'score': min(1.0, impact_score / 10),  # 0-1 정규화
                    'keyword_count': keyword_count,
                    'impact_level': '높음' if impact_score > 5 else '보통' if impact_score > 2 else '낮음'
                }
        
        return sector_impact
    
    def _analyze_sentiment_correlation(self, news_data: List[Dict[str, Any]], 
                                     market_data: Dict[str, Any]) -> Dict[str, Any]:
        """뉴스 감정과 시장 심리 상관관계 분석"""
        # 간단한 감정 분석 (실제로는 감정 분석 모델 사용)
        positive_keywords = ['상승', '급등', '호재', '긍정', '성장', '개선']
        negative_keywords = ['하락', '급락', '악재', '부정', '위험', '우려']
        
        positive_count = 0
        negative_count = 0
        
        for news in news_data:
            title = news.get('title', '')
            content = news.get('content', '')
            text = f"{title} {content}"
            
            for keyword in positive_keywords:
                if keyword in text:
                    positive_count += 1
            
            for keyword in negative_keywords:
                if keyword in text:
                    negative_count += 1
        
        total_news = len(news_data)
        sentiment_ratio = positive_count / (positive_count + negative_count) if (positive_count + negative_count) > 0 else 0.5
        
        market_sentiment = market_data.get('market_sentiment', {}).get('sentiment_score', 50) / 100
        
        correlation = abs(sentiment_ratio - market_sentiment)
        
        return {
            'news_sentiment_ratio': sentiment_ratio,
            'market_sentiment_ratio': market_sentiment,
            'correlation': correlation,
            'positive_news_count': positive_count,
            'negative_news_count': negative_count,
            'total_news_count': total_news
        }
    
    def _analyze_news_sentiment(self, news_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """뉴스 감정 분석"""
        # 간단한 감정 분석 (실제로는 감정 분석 모델 사용)
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for news in news_data:
            title = news.get('title', '')
            # 간단한 키워드 기반 감정 분석
            if any(word in title for word in ['상승', '급등', '호재']):
                positive_count += 1
            elif any(word in title for word in ['하락', '급락', '악재']):
                negative_count += 1
            else:
                neutral_count += 1
        
        total = len(news_data)
        if total == 0:
            return {'sentiment_score': 0.5, 'dominant_sentiment': '중립'}
        
        sentiment_score = positive_count / total
        
        return {
            'sentiment_score': sentiment_score,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'dominant_sentiment': '긍정' if sentiment_score > 0.6 else '부정' if sentiment_score < 0.4 else '중립'
        }
    
    def _calculate_technical_indicators(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """기술적 지표 계산"""
        # 간단한 기술적 지표 (실제로는 더 복잡한 계산 필요)
        indices = market_data.get('market_overview', {}).get('indices', {})
        
        technical_indicators = {}
        
        for index_name, index_data in indices.items():
            change_percent = index_data.get('change_percent', 0)
            volume = index_data.get('volume', 0)
            
            # 모멘텀 지표
            momentum = '강한 상승' if change_percent > 2 else '상승' if change_percent > 0 else '하락' if change_percent < -2 else '약한 하락'
            
            # 거래량 지표
            volume_signal = '높음' if volume > 1000000 else '보통' if volume > 500000 else '낮음'
            
            technical_indicators[index_name] = {
                'momentum': momentum,
                'volume_signal': volume_signal,
                'trend_strength': abs(change_percent) / 5  # 0-1 정규화
            }
        
        return technical_indicators
    
    def _calculate_prediction_score(self, news_sentiment: Dict[str, Any], 
                                  technical_indicators: Dict[str, Any],
                                  market_data: Dict[str, Any]) -> float:
        """예측 점수 계산"""
        # 뉴스 감정 점수
        sentiment_score = news_sentiment.get('sentiment_score', 0.5)
        
        # 기술적 지표 점수
        technical_score = 0.5  # 기본값
        if technical_indicators:
            total_trend_strength = 0
            count = 0
            for indicator in technical_indicators.values():
                total_trend_strength += indicator.get('trend_strength', 0)
                count += 1
            technical_score = total_trend_strength / count if count > 0 else 0.5
        
        # 시장 심리 점수
        market_sentiment = market_data.get('market_sentiment', {}).get('sentiment_score', 50) / 100
        
        # 가중 평균 계산
        prediction_score = (
            sentiment_score * self.analysis_config['sentiment_weight'] +
            technical_score * self.analysis_config['price_weight'] +
            market_sentiment * self.analysis_config['volume_weight']
        )
        
        return max(0, min(1, prediction_score))  # 0-1 범위로 제한
    
    def _generate_prediction_result(self, prediction_score: float) -> Dict[str, Any]:
        """예측 결과 생성"""
        if prediction_score > 0.7:
            return {
                'trend': '강한 상승',
                'confidence': prediction_score,
                'recommendation': '적극적 매수',
                'risk_level': '보통'
            }
        elif prediction_score > 0.6:
            return {
                'trend': '상승',
                'confidence': prediction_score,
                'recommendation': '매수',
                'risk_level': '낮음'
            }
        elif prediction_score > 0.4:
            return {
                'trend': '횡보',
                'confidence': prediction_score,
                'recommendation': '관망',
                'risk_level': '보통'
            }
        elif prediction_score > 0.3:
            return {
                'trend': '하락',
                'confidence': prediction_score,
                'recommendation': '매도',
                'risk_level': '높음'
            }
        else:
            return {
                'trend': '강한 하락',
                'confidence': prediction_score,
                'recommendation': '적극적 매도',
                'risk_level': '매우 높음'
            }
    
    def _calculate_confidence_level(self, prediction_score: float) -> str:
        """신뢰도 수준 계산"""
        if prediction_score > 0.8 or prediction_score < 0.2:
            return '매우 높음'
        elif prediction_score > 0.7 or prediction_score < 0.3:
            return '높음'
        elif prediction_score > 0.6 or prediction_score < 0.4:
            return '보통'
        else:
            return '낮음' 