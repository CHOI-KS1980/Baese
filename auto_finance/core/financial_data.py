"""
📈 고도화된 금융 데이터 수집기
실시간 주가, 지수, 환율, 경제지표, 기술적 분석 등
"""

import asyncio
import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from auto_finance.utils.logger import setup_logger
from auto_finance.utils.error_handler import retry_on_error, ErrorHandler
from auto_finance.utils.cache_manager import cache_manager
from auto_finance.config.settings import FINANCIAL_CONFIG

logger = setup_logger(__name__)

@dataclass
class StockData:
    """주식 데이터"""
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[float]
    pe_ratio: Optional[float]
    dividend_yield: Optional[float]
    high_52w: Optional[float]
    low_52w: Optional[float]
    timestamp: str

@dataclass
class IndexData:
    """지수 데이터"""
    symbol: str
    name: str
    value: float
    change: float
    change_percent: float
    volume: Optional[int]
    timestamp: str

@dataclass
class EconomicIndicator:
    """경제지표 데이터"""
    name: str
    value: float
    unit: str
    period: str
    change: Optional[float]
    change_percent: Optional[float]
    timestamp: str

class FinancialDataCollector:
    """고도화된 금융 데이터 수집기"""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        
        # 설정 로드
        self.stock_symbols = FINANCIAL_CONFIG.get('stock_symbols', [])
        self.index_symbols = FINANCIAL_CONFIG.get('index_symbols', [])
        self.update_interval = FINANCIAL_CONFIG.get('update_interval', 300)  # 5분
        
        # 데이터 저장소
        self.stock_data: Dict[str, StockData] = {}
        self.index_data: Dict[str, IndexData] = {}
        self.economic_data: Dict[str, EconomicIndicator] = {}
        
        # 수집 통계
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'last_update': None,
            'processing_time': 0.0
        }
        
        logger.info(f"📈 금융 데이터 수집기 초기화: {len(self.stock_symbols)}개 종목, {len(self.index_symbols)}개 지수")
    
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        await self.cleanup()
    
    async def cleanup(self):
        """리소스 정리"""
        try:
            logger.info("🧹 금융 데이터 수집기 정리 완료")
        except Exception as e:
            logger.error(f"❌ 금융 데이터 수집기 정리 실패: {e}")
    
    @retry_on_error(max_retries=3, delay=2.0)
    async def get_stock_data(self, symbol: str) -> Optional[StockData]:
        """단일 주식 데이터 수집"""
        try:
            # 캐시 확인
            cache_key = f"stock_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M')}"
            cached_data = cache_manager.get(cache_key)
            
            if cached_data:
                logger.debug(f"💾 캐시된 주식 데이터 사용: {symbol}")
                return StockData(**cached_data)
            
            # yfinance로 데이터 수집
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 실시간 가격 데이터
            hist = ticker.history(period="1d", interval="1m")
            if hist.empty:
                raise Exception(f"가격 데이터 없음: {symbol}")
            
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Open'].iloc[0] if len(hist) > 1 else current_price
            
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100 if prev_close > 0 else 0
            
            # 주식 데이터 생성
            stock_data = StockData(
                symbol=symbol,
                name=info.get('longName', symbol),
                price=current_price,
                change=change,
                change_percent=change_percent,
                volume=int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else 0,
                market_cap=info.get('marketCap'),
                pe_ratio=info.get('trailingPE'),
                dividend_yield=info.get('dividendYield'),
                high_52w=info.get('fiftyTwoWeekHigh'),
                low_52w=info.get('fiftyTwoWeekLow'),
                timestamp=datetime.now().isoformat()
            )
            
            # 캐시 저장
            cache_manager.set(cache_key, stock_data.__dict__, ttl=300)  # 5분
            
            self.stats['successful_requests'] += 1
            logger.debug(f"✅ 주식 데이터 수집 완료: {symbol}")
            
            return stock_data
            
        except Exception as e:
            self.stats['failed_requests'] += 1
            self.error_handler.handle_error(e, f"주식 데이터 수집 실패 ({symbol})")
            logger.error(f"❌ 주식 데이터 수집 실패 ({symbol}): {e}")
            return None
    
    @retry_on_error(max_retries=3, delay=2.0)
    async def get_index_data(self, symbol: str) -> Optional[IndexData]:
        """지수 데이터 수집"""
        try:
            # 캐시 확인
            cache_key = f"index_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M')}"
            cached_data = cache_manager.get(cache_key)
            
            if cached_data:
                logger.debug(f"💾 캐시된 지수 데이터 사용: {symbol}")
                return IndexData(**cached_data)
            
            # yfinance로 지수 데이터 수집
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d", interval="1m")
            
            if hist.empty:
                raise Exception(f"지수 데이터 없음: {symbol}")
            
            current_value = hist['Close'].iloc[-1]
            prev_close = hist['Open'].iloc[0] if len(hist) > 1 else current_value
            
            change = current_value - prev_close
            change_percent = (change / prev_close) * 100 if prev_close > 0 else 0
            
            # 지수 데이터 생성
            index_data = IndexData(
                symbol=symbol,
                name=self._get_index_name(symbol),
                value=current_value,
                change=change,
                change_percent=change_percent,
                volume=int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else None,
                timestamp=datetime.now().isoformat()
            )
            
            # 캐시 저장
            cache_manager.set(cache_key, index_data.__dict__, ttl=300)  # 5분
            
            self.stats['successful_requests'] += 1
            logger.debug(f"✅ 지수 데이터 수집 완료: {symbol}")
            
            return index_data
            
        except Exception as e:
            self.stats['failed_requests'] += 1
            self.error_handler.handle_error(e, f"지수 데이터 수집 실패 ({symbol})")
            logger.error(f"❌ 지수 데이터 수집 실패 ({symbol}): {e}")
            return None
    
    def _get_index_name(self, symbol: str) -> str:
        """지수명 반환"""
        index_names = {
            '^GSPC': 'S&P 500',
            '^DJI': 'Dow Jones',
            '^IXIC': 'NASDAQ',
            '^KS11': 'KOSPI',
            '^KQ11': 'KOSDAQ',
            '^TNX': '10-Year Treasury',
            '^VIX': 'VIX',
            'GC=F': 'Gold Futures',
            'CL=F': 'Crude Oil Futures'
        }
        return index_names.get(symbol, symbol)
    
    async def get_historical_data(self, symbol: str, period: str = "1y", 
                                 interval: str = "1d") -> Optional[pd.DataFrame]:
        """과거 데이터 수집"""
        try:
            # 캐시 확인
            cache_key = f"hist_{symbol}_{period}_{interval}_{datetime.now().strftime('%Y%m%d')}"
            cached_data = cache_manager.get(cache_key)
            
            if cached_data:
                logger.debug(f"💾 캐시된 과거 데이터 사용: {symbol}")
                return pd.DataFrame(cached_data)
            
            # yfinance로 과거 데이터 수집
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)
            
            if hist.empty:
                raise Exception(f"과거 데이터 없음: {symbol}")
            
            # 캐시 저장
            cache_manager.set(cache_key, hist.to_dict('records'), ttl=3600)  # 1시간
            
            logger.debug(f"✅ 과거 데이터 수집 완료: {symbol}")
            return hist
            
        except Exception as e:
            self.error_handler.handle_error(e, f"과거 데이터 수집 실패 ({symbol})")
            logger.error(f"❌ 과거 데이터 수집 실패 ({symbol}): {e}")
            return None
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """기술적 지표 계산"""
        try:
            indicators = {}
            
            if len(df) < 20:
                return indicators
            
            # 이동평균
            indicators['sma_20'] = df['Close'].rolling(window=20).mean().iloc[-1]
            indicators['sma_50'] = df['Close'].rolling(window=50).mean().iloc[-1]
            
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            indicators['rsi'] = 100 - (100 / (1 + rs.iloc[-1]))
            
            # MACD
            ema_12 = df['Close'].ewm(span=12).mean()
            ema_26 = df['Close'].ewm(span=26).mean()
            indicators['macd'] = ema_12.iloc[-1] - ema_26.iloc[-1]
            
            # 볼린저 밴드
            sma_20 = df['Close'].rolling(window=20).mean()
            std_20 = df['Close'].rolling(window=20).std()
            indicators['bb_upper'] = sma_20.iloc[-1] + (std_20.iloc[-1] * 2)
            indicators['bb_lower'] = sma_20.iloc[-1] - (std_20.iloc[-1] * 2)
            
            return indicators
            
        except Exception as e:
            logger.error(f"❌ 기술적 지표 계산 실패: {e}")
            return {}
    
    async def collect_all_stock_data(self) -> Dict[str, StockData]:
        """모든 주식 데이터 수집"""
        logger.info(f"📈 전체 주식 데이터 수집 시작: {len(self.stock_symbols)}개 종목")
        
        start_time = datetime.now()
        
        # 병렬 수집
        tasks = [self.get_stock_data(symbol) for symbol in self.stock_symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 처리
        for i, result in enumerate(results):
            if isinstance(result, StockData):
                self.stock_data[self.stock_symbols[i]] = result
            elif isinstance(result, Exception):
                logger.error(f"❌ 주식 데이터 수집 실패 ({self.stock_symbols[i]}): {result}")
        
        # 통계 업데이트
        processing_time = (datetime.now() - start_time).total_seconds()
        self.stats['processing_time'] = processing_time
        self.stats['last_update'] = datetime.now().isoformat()
        
        logger.info(f"✅ 주식 데이터 수집 완료: {len(self.stock_data)}개 성공")
        return self.stock_data
    
    async def collect_all_index_data(self) -> Dict[str, IndexData]:
        """모든 지수 데이터 수집"""
        logger.info(f"📊 전체 지수 데이터 수집 시작: {len(self.index_symbols)}개 지수")
        
        # 병렬 수집
        tasks = [self.get_index_data(symbol) for symbol in self.index_symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 처리
        for i, result in enumerate(results):
            if isinstance(result, IndexData):
                self.index_data[self.index_symbols[i]] = result
            elif isinstance(result, Exception):
                logger.error(f"❌ 지수 데이터 수집 실패 ({self.index_symbols[i]}): {result}")
        
        logger.info(f"✅ 지수 데이터 수집 완료: {len(self.index_data)}개 성공")
        return self.index_data
    
    def get_market_summary(self) -> Dict[str, Any]:
        """시장 요약 정보"""
        try:
            summary = {
                'timestamp': datetime.now().isoformat(),
                'stocks': {
                    'total_count': len(self.stock_data),
                    'gainers': len([s for s in self.stock_data.values() if s.change > 0]),
                    'losers': len([s for s in self.stock_data.values() if s.change < 0]),
                    'unchanged': len([s for s in self.stock_data.values() if s.change == 0]),
                    'top_gainers': sorted(self.stock_data.values(), key=lambda x: x.change_percent, reverse=True)[:5],
                    'top_losers': sorted(self.stock_data.values(), key=lambda x: x.change_percent)[:5]
                },
                'indices': {
                    'total_count': len(self.index_data),
                    'summary': [{'symbol': k, 'value': v.value, 'change': v.change_percent} 
                               for k, v in self.index_data.items()]
                },
                'statistics': self.stats
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ 시장 요약 생성 실패: {e}")
            return {}
    
    def save_data(self, file_path: str = "data/financial_data.json"):
        """데이터 저장"""
        try:
            data = {
                'stocks': {k: v.__dict__ for k, v in self.stock_data.items()},
                'indices': {k: v.__dict__ for k, v in self.index_data.items()},
                'summary': self.get_market_summary(),
                'timestamp': datetime.now().isoformat()
            }
            
            import json
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"💾 금융 데이터 저장: {file_path}")
            
        except Exception as e:
            logger.error(f"❌ 데이터 저장 실패: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """수집 통계 반환"""
        return {
            **self.stats,
            'error_statistics': self.error_handler.get_statistics(),
            'data_counts': {
                'stocks': len(self.stock_data),
                'indices': len(self.index_data),
                'economic_indicators': len(self.economic_data)
            },
            'timestamp': datetime.now().isoformat()
        }

# 사용 예시
async def main():
    """금융 데이터 수집기 테스트"""
    # 테스트용 설정
    test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
    test_indices = ['^GSPC', '^DJI', '^IXIC']
    
    collector = FinancialDataCollector()
    collector.stock_symbols = test_symbols
    collector.index_symbols = test_indices
    
    async with collector:
        # 주식 데이터 수집
        stocks = await collector.collect_all_stock_data()
        print(f"📈 주식 데이터: {len(stocks)}개 수집")
        
        # 지수 데이터 수집
        indices = await collector.collect_all_index_data()
        print(f"📊 지수 데이터: {len(indices)}개 수집")
        
        # 시장 요약
        summary = collector.get_market_summary()
        print(f"📋 시장 요약: 상승 {summary['stocks']['gainers']}개, 하락 {summary['stocks']['losers']}개")
        
        # 데이터 저장
        collector.save_data()

if __name__ == "__main__":
    asyncio.run(main()) 