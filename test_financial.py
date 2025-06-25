"""
📈 금융 데이터 수집 테스트 스크립트
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_financial_data():
    """금융 데이터 수집 테스트"""
    try:
        print("🚀 금융 데이터 수집 테스트 시작")
        
        # yfinance 직접 테스트
        import yfinance as yf
        
        # 미국 주식 테스트
        print("📊 Apple 주가 조회 중...")
        apple = yf.Ticker("AAPL")
        hist = apple.history(period="1d")
        
        if not hist.empty:
            latest = hist.iloc[-1]
            print(f"✅ Apple 현재가: ${latest['Close']:.2f}")
            print(f"   변동률: {((latest['Close'] - latest['Open']) / latest['Open'] * 100):.2f}%")
            print(f"   거래량: {latest['Volume']:,}")
        else:
            print("❌ Apple 데이터 조회 실패")
        
        # S&P 500 지수 조회
        print("\n📈 S&P 500 지수 조회 중...")
        sp500 = yf.Ticker("^GSPC")
        sp500_hist = sp500.history(period="1d")
        
        if not sp500_hist.empty:
            latest_sp500 = sp500_hist.iloc[-1]
            print(f"✅ S&P 500: {latest_sp500['Close']:.2f}")
            print(f"   변동률: {((latest_sp500['Close'] - latest_sp500['Open']) / latest_sp500['Open'] * 100):.2f}%")
        else:
            print("❌ S&P 500 데이터 조회 실패")
        
        # 주요 미국 종목들 조회
        print("\n📋 주요 미국 종목 조회 중...")
        major_stocks = {
            'Microsoft': 'MSFT',
            'Google': 'GOOGL',
            'Amazon': 'AMZN',
            'Tesla': 'TSLA'
        }
        
        for name, symbol in major_stocks.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")
                if not hist.empty:
                    latest = hist.iloc[-1]
                    change_pct = ((latest['Close'] - latest['Open']) / latest['Open'] * 100)
                    print(f"   {name}: ${latest['Close']:.2f} ({change_pct:+.2f}%)")
                else:
                    print(f"   {name}: 데이터 없음")
            except Exception as e:
                print(f"   {name}: 오류 - {e}")
        
        # 한국 주식 (다른 심볼로 시도)
        print("\n🇰🇷 한국 주식 조회 중...")
        korean_stocks = {
            'Samsung Electronics': '005930.KS',
            'SK Hynix': '000660.KS',
            'Hyundai Motor': '005380.KS'
        }
        
        for name, symbol in korean_stocks.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="5d")  # 더 긴 기간으로 시도
                if not hist.empty:
                    latest = hist.iloc[-1]
                    change_pct = ((latest['Close'] - hist.iloc[-2]['Close']) / hist.iloc[-2]['Close'] * 100) if len(hist) > 1 else 0
                    print(f"   {name}: {latest['Close']:,.0f}원 ({change_pct:+.2f}%)")
                else:
                    print(f"   {name}: 데이터 없음")
            except Exception as e:
                print(f"   {name}: 오류 - {e}")
        
        print("\n✅ 금융 데이터 수집 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_financial_data() 