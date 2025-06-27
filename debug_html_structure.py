#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML 구조 디버깅 스크립트
실제 웹사이트에서 일일 데이터의 정확한 위치를 찾습니다.
"""

import requests
from bs4 import BeautifulSoup
import re
import os

def debug_html_structure():
    """실제 HTML에서 일일 데이터 위치를 찾습니다."""
    
    print("⚠️  이 스크립트는 실제 로그인 정보가 필요합니다.")
    print("📝 현재는 main_executor.py에서 이미 크롤링한 HTML을 분석해야 합니다.")
    print("🔍 대신 로그 파일에서 일일 데이터 크롤링 결과를 확인해보겠습니다.")
    
    # 실제로는 main_executor.py의 로그를 통해 디버깅해야 함
    print("\n" + "=" * 60)
    print("🎯 문제 해결 방향:")
    print("1. 현재 코드가 올바른 HTML 셀렉터를 사용하고 있는지 확인")
    print("2. 웹사이트 HTML 구조가 변경되었는지 확인") 
    print("3. 일일 데이터와 주간 데이터가 다른 페이지에 있는지 확인")
    print("4. JavaScript로 동적 로딩되는 데이터인지 확인")
    
    print("\n📋 현재 사용중인 셀렉터:")
    selectors = [
        "div.total_value_item[data-total_value='complete_count']",
        "div.total_value_item[data-total_value='reject_count']", 
        "div.total_value_item[data-total_value='accept_cancel_count']",
        "div.total_value_item[data-total_value='accept_cancel_rider_fault_count']"
    ]
    
    for selector in selectors:
        print(f"   - {selector}")
    
    print("\n💡 해결책:")
    print("1. main_executor.py에 더 상세한 로깅 추가")
    print("2. HTML 구조 변경 감지 로직 추가") 
    print("3. 크롤링 실패시 대체 셀렉터 시도")

if __name__ == "__main__":
    debug_html_structure() 