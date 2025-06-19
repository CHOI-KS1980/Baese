#!/usr/bin/env python3
"""
G라이더 HTML 구조 분석 도구
실제 데이터 파싱 로직 개발을 위해 HTML 구조를 분석합니다.
"""

import requests
from bs4 import BeautifulSoup
import json
import re

def analyze_grider_html():
    """G라이더 사이트 HTML 구조 분석"""
    try:
        print("🔄 G라이더 사이트 분석 중...")
        
        response = requests.get('https://jangboo.grider.ai/', 
                              headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                              timeout=30)
        
        html_data = response.text
        print(f"✅ HTML 데이터 수집 완료 ({len(html_data)} bytes)")
        
        # BeautifulSoup으로 파싱
        soup = BeautifulSoup(html_data, 'html.parser')
        
        print("\n📊 HTML 구조 분석:")
        print("=" * 60)
        
        # Title 확인
        title = soup.find('title')
        if title:
            print(f"📌 페이지 제목: {title.get_text().strip()}")
        
        # 로그인 리다이렉트 체크
        if "<script>location.href='/login';</script>" in html_data:
            print("⚠️ 로그인 필요 상태")
            return
        
        # 주요 요소들 찾기
        print("\n🔍 주요 요소 검색:")
        
        # 미션 관련 텍스트 검색
        mission_keywords = ['미션', '아침', '점심', '저녁', '심야', '달성', '부족']
        for keyword in mission_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
            if elements:
                print(f"  '{keyword}' 발견: {len(elements)}개")
                for i, elem in enumerate(elements[:3]):  # 처음 3개만
                    print(f"    {i+1}. {elem.strip()[:50]}...")
        
        # 라이더 이름 패턴 검색
        print("\n👥 라이더 관련 정보:")
        rider_patterns = [r'[가-힣]{2,4}', r'\d+건', r'\d+\.?\d*%']
        for pattern in rider_patterns:
            matches = re.findall(pattern, html_data)
            if matches:
                print(f"  패턴 '{pattern}': {len(matches)}개 발견")
                print(f"    예시: {matches[:5]}")
        
        # 테이블 구조 확인
        tables = soup.find_all('table')
        print(f"\n📋 테이블: {len(tables)}개 발견")
        for i, table in enumerate(tables):
            rows = table.find_all('tr')
            print(f"  테이블 {i+1}: {len(rows)}행")
            if rows:
                first_row = rows[0].get_text().strip()
                print(f"    첫 번째 행: {first_row[:50]}...")
        
        # DIV 클래스들 확인
        divs_with_class = soup.find_all('div', class_=True)
        print(f"\n📦 클래스가 있는 DIV: {len(divs_with_class)}개")
        class_names = set()
        for div in divs_with_class:
            classes = div.get('class', [])
            class_names.update(classes)
        
        print(f"  고유 클래스: {len(class_names)}개")
        for cls in sorted(list(class_names)[:10]):  # 처음 10개만
            print(f"    - {cls}")
        
        # 스크립트 태그 확인
        scripts = soup.find_all('script')
        print(f"\n⚙️ 스크립트 태그: {len(scripts)}개")
        for i, script in enumerate(scripts):
            if script.string and len(script.string.strip()) > 20:
                content = script.string.strip()[:100]
                print(f"  스크립트 {i+1}: {content}...")
        
        # 전체 텍스트에서 숫자 패턴 찾기
        print("\n🔢 숫자 패턴 분석:")
        number_patterns = {
            '퍼센트': r'\d+\.?\d*%',
            '건수': r'\d+건',
            '점수': r'\d+점',
            '시간': r'\d{1,2}:\d{2}',
            '온도': r'\d+°C'
        }
        
        for name, pattern in number_patterns.items():
            matches = re.findall(pattern, html_data)
            if matches:
                print(f"  {name}: {matches[:5]}")
        
        # 원시 HTML 일부 저장 (디버깅용)
        print(f"\n💾 HTML 샘플 저장...")
        with open('grider_html_sample.txt', 'w', encoding='utf-8') as f:
            f.write(f"G라이더 HTML 분석 결과\n")
            f.write(f"{'='*50}\n\n")
            f.write(f"HTML 길이: {len(html_data)} bytes\n")
            f.write(f"Title: {title.get_text().strip() if title else 'None'}\n\n")
            f.write("HTML 처음 2000자:\n")
            f.write("-" * 30 + "\n")
            f.write(html_data[:2000])
            f.write("\n" + "-" * 30 + "\n\n")
            f.write("HTML 마지막 1000자:\n")
            f.write("-" * 30 + "\n")
            f.write(html_data[-1000:])
        
        print("✅ 분석 완료! 'grider_html_sample.txt' 파일을 확인하세요.")
        
    except Exception as e:
        print(f"❌ 분석 오류: {e}")

if __name__ == "__main__":
    analyze_grider_html() 