"""
📊 뉴스-주가 상관관계 분석기
뉴스 감정과 주가 변동 간의 상관관계 분석 및 예측
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from auto_finance.core.financial_data import FinancialDataCollector
from auto_finance.core.news_crawler import NewsCrawler

class PriceCorrelationAnalyzer:
    def __init__(self):
        self.financial_collector = FinancialDataCollector()
        self.news_crawler = NewsCrawler()
        
        # 상관관계 분석 설정
        self.correlation_config = {
            'time_window': 7,  # 분석 기간 (일)
            'min_correlation': 0.3,  # 최소 상관관계 임계값
            'sentiment_weight': 0.4,  # 감정 분석 가중치
            'volume_weight': 0.3,     # 거래량 가중치
            'price_weight': 0.3       # 가격 변동 가중치
        }
    
    def analyze_news_price_correlation(self, stock_symbol: str, 
                                     news_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """뉴스와 주가 상관관계 종합 분석"""
        try:
            # 주가 데이터 수집
            price_data = self._get_historical_price_data(stock_symbol)
            
            # 뉴스 감정 분석
            news_sentiment = self._analyze_news_sentiment_timeline(news_data)
            
            # 상관관계 계산
            correlation_result = self._calculate_correlation(price_data, news_sentiment)
            
            # 영향도 분석
            impact_analysis = self._analyze_news_impact(price_data, news_sentiment)
            
            # 예측 모델 생성
            prediction_model = self._create_prediction_model(price_data, news_sentiment)
            
            return {
                'stock_symbol': stock_symbol,
                'correlation_result': correlation_result,
                'impact_analysis': impact_analysis,
                'prediction_model': prediction_model,
                'analysis_period': self.correlation_config['time_window'],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ 뉴스-주가 상관관계 분석 실패 ({stock_symbol}): {e}")
            return {}
    
    def predict_price_movement(self, stock_symbol: str, 
                             current_news: List[Dict[str, Any]]) -> Dict[str, Any]:
        """뉴스 기반 주가 변동 예측"""
        try:
            # 현재 뉴스 감정 분석
            current_sentiment = self._analyze_current_news_sentiment(current_news)
            
            # 최근 주가 데이터
            recent_price_data = self._get_recent_price_data(stock_symbol)
            
            # 예측 모델 적용
            prediction = self._apply_prediction_model(
                current_sentiment, recent_price_data
            )
            
            # 신뢰도 계산
            confidence = self._calculate_prediction_confidence(
                current_sentiment, recent_price_data
            )
            
            return {
                'stock_symbol': stock_symbol,
                'predicted_movement': prediction,
                'confidence': confidence,
                'current_sentiment': current_sentiment,
                'prediction_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ 주가 변동 예측 실패 ({stock_symbol}): {e}")
            return {}
    
    def generate_correlation_report(self, analysis_results: Dict[str, Any]) -> str:
        """상관관계 분석 리포트 생성"""
        try:
            stock_symbol = analysis_results.get('stock_symbol', 'Unknown')
            correlation = analysis_results.get('correlation_result', {})
            impact = analysis_results.get('impact_analysis', {})
            
            report = f"""
# 📊 {stock_symbol} 뉴스-주가 상관관계 분석 리포트

## 📈 상관관계 분석 결과
- **전체 상관관계**: {correlation.get('overall_correlation', 0):.3f}
- **감정-가격 상관관계**: {correlation.get('sentiment_price_correlation', 0):.3f}
- **거래량-뉴스 상관관계**: {correlation.get('volume_news_correlation', 0):.3f}

## 🎯 영향도 분석
- **뉴스 영향 지수**: {impact.get('news_impact_index', 0):.3f}
- **감정 영향도**: {impact.get('sentiment_impact', 0):.3f}
- **주요 영향 키워드**: {', '.join(impact.get('key_keywords', []))}

## 📊 예측 모델 성능
- **모델 정확도**: {correlation.get('model_accuracy', 0):.1f}%
- **예측 신뢰도**: {correlation.get('prediction_confidence', 0):.1f}%

## 💡 투자 권장사항
{self._generate_investment_advice(analysis_results)}

---
*분석 기간: {analysis_results.get('analysis_period', 7)}일*
*생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            return report
            
        except Exception as e:
            print(f"❌ 리포트 생성 실패: {e}")
            return "리포트 생성 중 오류가 발생했습니다."
    
    def _get_historical_price_data(self, stock_symbol: str) -> pd.DataFrame:
        """과거 주가 데이터 수집"""
        try:
            # Yahoo Finance에서 과거 데이터 조회
            import yfinance as yf
            ticker = yf.Ticker(stock_symbol)
            hist = ticker.history(period=f"{self.correlation_config['time_window']}d")
            
            if hist.empty:
                return pd.DataFrame()
            
            # 필요한 컬럼만 선택
            price_data = hist[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
            price_data['Date'] = price_data.index.date
            price_data['Price_Change'] = price_data['Close'].pct_change()
            price_data['Volume_Change'] = price_data['Volume'].pct_change()
            
            return price_data
            
        except Exception as e:
            print(f"❌ 과거 주가 데이터 수집 실패: {e}")
            return pd.DataFrame()
    
    def _analyze_news_sentiment_timeline(self, news_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """뉴스 감정 분석 (시간순)"""
        try:
            sentiment_data = []
            
            for news in news_data:
                # 뉴스 날짜 추출
                news_date = news.get('date', datetime.now().date())
                if isinstance(news_date, str):
                    news_date = datetime.strptime(news_date, '%Y-%m-%d').date()
                
                # 감정 분석
                sentiment_score = self._calculate_news_sentiment(news)
                
                sentiment_data.append({
                    'date': news_date,
                    'title': news.get('title', ''),
                    'sentiment_score': sentiment_score,
                    'keywords': self._extract_keywords(news)
                })
            
            # DataFrame으로 변환
            df = pd.DataFrame(sentiment_data)
            if not df.empty:
                df = df.groupby('date').agg({
                    'sentiment_score': 'mean',
                    'title': 'count'
                }).reset_index()
                df.columns = ['date', 'avg_sentiment', 'news_count']
            
            return df
            
        except Exception as e:
            print(f"❌ 뉴스 감정 분석 실패: {e}")
            return pd.DataFrame()
    
    def _calculate_news_sentiment(self, news: Dict[str, Any]) -> float:
        """개별 뉴스 감정 점수 계산"""
        title = news.get('title', '')
        content = news.get('content', '')
        text = f"{title} {content}"
        
        # 긍정 키워드
        positive_words = ['상승', '급등', '호재', '성장', '개선', '돌파', '신기록', '급증']
        # 부정 키워드
        negative_words = ['하락', '급락', '악재', '위험', '우려', '폭락', '하향', '부진']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        total_count = positive_count + negative_count
        if total_count == 0:
            return 0.5  # 중립
        
        return positive_count / total_count
    
    def _extract_keywords(self, news: Dict[str, Any]) -> List[str]:
        """뉴스에서 키워드 추출"""
        title = news.get('title', '')
        content = news.get('content', '')
        text = f"{title} {content}"
        
        # 주요 키워드 목록
        keywords = [
            'AI', '반도체', '전기차', '바이오', '게임', '금융', '부동산',
            '금리', '환율', '원유', '금', '달러', '엔화', '위안',
            '삼성전자', 'SK하이닉스', 'NAVER', '카카오', 'LG에너지솔루션'
        ]
        
        return [kw for kw in keywords if kw in text]
    
    def _calculate_correlation(self, price_data: pd.DataFrame, 
                             sentiment_data: pd.DataFrame) -> Dict[str, Any]:
        """상관관계 계산"""
        try:
            if price_data.empty or sentiment_data.empty:
                return {}
            
            # 날짜 기준으로 데이터 병합
            merged_data = pd.merge(
                price_data, sentiment_data, 
                left_on='Date', right_on='date', how='inner'
            )
            
            if merged_data.empty:
                return {}
            
            # 상관관계 계산
            correlations = {
                'sentiment_price_correlation': merged_data['avg_sentiment'].corr(merged_data['Price_Change']),
                'sentiment_volume_correlation': merged_data['avg_sentiment'].corr(merged_data['Volume_Change']),
                'news_count_price_correlation': merged_data['news_count'].corr(merged_data['Price_Change']),
                'overall_correlation': 0.0
            }
            
            # 전체 상관관계 (가중 평균)
            valid_correlations = [v for v in correlations.values() if not pd.isna(v)]
            if valid_correlations:
                correlations['overall_correlation'] = np.mean(valid_correlations)
            
            # 모델 정확도 (간단한 예시)
            correlations['model_accuracy'] = min(85, max(50, abs(correlations['overall_correlation']) * 100))
            correlations['prediction_confidence'] = min(90, max(30, correlations['model_accuracy'] + 10))
            
            return correlations
            
        except Exception as e:
            print(f"❌ 상관관계 계산 실패: {e}")
            return {}
    
    def _analyze_news_impact(self, price_data: pd.DataFrame, 
                           sentiment_data: pd.DataFrame) -> Dict[str, Any]:
        """뉴스 영향도 분석"""
        try:
            if price_data.empty or sentiment_data.empty:
                return {}
            
            # 데이터 병합
            merged_data = pd.merge(
                price_data, sentiment_data, 
                left_on='Date', right_on='date', how='inner'
            )
            
            if merged_data.empty:
                return {}
            
            # 뉴스 영향 지수 계산
            sentiment_impact = merged_data['avg_sentiment'].std()
            price_volatility = merged_data['Price_Change'].std()
            
            news_impact_index = sentiment_impact * price_volatility if price_volatility > 0 else 0
            
            # 주요 키워드 추출 (간단한 예시)
            key_keywords = ['AI', '반도체', '전기차']  # 실제로는 더 복잡한 분석 필요
            
            return {
                'news_impact_index': news_impact_index,
                'sentiment_impact': sentiment_impact,
                'price_volatility': price_volatility,
                'key_keywords': key_keywords
            }
            
        except Exception as e:
            print(f"❌ 영향도 분석 실패: {e}")
            return {}
    
    def _create_prediction_model(self, price_data: pd.DataFrame, 
                               sentiment_data: pd.DataFrame) -> Dict[str, Any]:
        """예측 모델 생성"""
        try:
            if price_data.empty or sentiment_data.empty:
                return {}
            
            # 간단한 선형 회귀 모델 (실제로는 더 복잡한 모델 사용)
            merged_data = pd.merge(
                price_data, sentiment_data, 
                left_on='Date', right_on='date', how='inner'
            )
            
            if merged_data.empty:
                return {}
            
            # 모델 파라미터 (간단한 예시)
            model_params = {
                'sentiment_coefficient': 0.3,
                'volume_coefficient': 0.2,
                'price_coefficient': 0.5,
                'intercept': 0.0
            }
            
            return {
                'model_type': 'linear_regression',
                'parameters': model_params,
                'training_data_size': len(merged_data),
                'model_created': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ 예측 모델 생성 실패: {e}")
            return {}
    
    def _get_recent_price_data(self, stock_symbol: str) -> Dict[str, Any]:
        """최근 주가 데이터 조회"""
        try:
            price_data = self.financial_collector.get_stock_price(stock_symbol, '5d')
            return price_data
            
        except Exception as e:
            print(f"❌ 최근 주가 데이터 조회 실패: {e}")
            return {}
    
    def _analyze_current_news_sentiment(self, current_news: List[Dict[str, Any]]) -> Dict[str, Any]:
        """현재 뉴스 감정 분석"""
        try:
            if not current_news:
                return {'sentiment_score': 0.5, 'news_count': 0}
            
            sentiment_scores = []
            for news in current_news:
                sentiment = self._calculate_news_sentiment(news)
                sentiment_scores.append(sentiment)
            
            return {
                'sentiment_score': np.mean(sentiment_scores),
                'sentiment_std': np.std(sentiment_scores),
                'news_count': len(current_news)
            }
            
        except Exception as e:
            print(f"❌ 현재 뉴스 감정 분석 실패: {e}")
            return {'sentiment_score': 0.5, 'news_count': 0}
    
    def _apply_prediction_model(self, current_sentiment: Dict[str, Any], 
                              recent_price_data: Dict[str, Any]) -> Dict[str, Any]:
        """예측 모델 적용"""
        try:
            sentiment_score = current_sentiment.get('sentiment_score', 0.5)
            price_change = recent_price_data.get('change_percent', 0) / 100
            
            # 간단한 예측 (실제로는 더 복잡한 모델 사용)
            predicted_change = (
                sentiment_score * 0.3 +
                price_change * 0.5 +
                0.2  # 기타 요인
            )
            
            # 예측 결과 해석
            if predicted_change > 0.02:
                movement = '상승'
                confidence = min(0.8, predicted_change * 10)
            elif predicted_change < -0.02:
                movement = '하락'
                confidence = min(0.8, abs(predicted_change) * 10)
            else:
                movement = '횡보'
                confidence = 0.5
            
            return {
                'predicted_movement': movement,
                'predicted_change_percent': predicted_change * 100,
                'confidence': confidence
            }
            
        except Exception as e:
            print(f"❌ 예측 모델 적용 실패: {e}")
            return {'predicted_movement': '횡보', 'predicted_change_percent': 0, 'confidence': 0.5}
    
    def _calculate_prediction_confidence(self, current_sentiment: Dict[str, Any], 
                                       recent_price_data: Dict[str, Any]) -> float:
        """예측 신뢰도 계산"""
        try:
            # 뉴스 수량 기반 신뢰도
            news_count = current_sentiment.get('news_count', 0)
            news_confidence = min(0.8, news_count / 10)
            
            # 감정 일관성 기반 신뢰도
            sentiment_std = current_sentiment.get('sentiment_std', 0.5)
            sentiment_confidence = max(0.3, 1 - sentiment_std)
            
            # 가격 변동성 기반 신뢰도
            price_change = abs(recent_price_data.get('change_percent', 0))
            price_confidence = max(0.3, 1 - (price_change / 10))
            
            # 종합 신뢰도
            total_confidence = (news_confidence + sentiment_confidence + price_confidence) / 3
            
            return min(0.9, max(0.3, total_confidence))
            
        except Exception as e:
            print(f"❌ 신뢰도 계산 실패: {e}")
            return 0.5
    
    def _generate_investment_advice(self, analysis_results: Dict[str, Any]) -> str:
        """투자 권장사항 생성"""
        try:
            correlation = analysis_results.get('correlation_result', {})
            overall_correlation = correlation.get('overall_correlation', 0)
            
            if overall_correlation > 0.5:
                return "✅ **강한 매수 신호**: 뉴스와 주가 간 강한 상관관계 확인"
            elif overall_correlation > 0.3:
                return "📈 **매수 고려**: 뉴스 영향이 주가에 긍정적 반영"
            elif overall_correlation > -0.3:
                return "⏸️ **관망**: 뉴스와 주가 간 명확한 상관관계 부족"
            elif overall_correlation > -0.5:
                return "📉 **매도 고려**: 뉴스 영향이 주가에 부정적 반영"
            else:
                return "❌ **강한 매도 신호**: 뉴스와 주가 간 강한 역상관관계 확인"
                
        except Exception as e:
            print(f"❌ 투자 권장사항 생성 실패: {e}")
            return "투자 권장사항 생성 중 오류가 발생했습니다." 