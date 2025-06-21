import os
import time
import schedule
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import pandas as pd
import re
import matplotlib
import datetime
import numpy as np
from typing import Dict, List, Tuple, Optional
import json
from concurrent.futures import ThreadPoolExecutor
import logging
from flask import Flask, request, jsonify
import threading

# 성능 최적화 설정
matplotlib.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 환경변수 로드 (아이디/비밀번호 등)
load_dotenv()
USER_ID = 'DP2406035262'  # 또는 본인 아이디
USER_PW = 'wldud050323!'  # 또는 본인 비밀번호

LOGIN_URL = 'https://jangboo.grider.ai/'

# 미션 데이터 캐싱을 위한 파일 경로
MISSION_DATA_CACHE_FILE = 'mission_data_cache.json'

def save_mission_data_cache(mission_date: str, peak_data: dict):
    """미션 데이터를 캐시 파일에 저장"""
    try:
        cache_data = {
            'date': mission_date,
            'timestamp': datetime.datetime.now().isoformat(),
            'peak_data': peak_data
        }
        
        with open(MISSION_DATA_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ 미션 데이터 캐시 저장 완료: {mission_date}")
        
    except Exception as e:
        logger.error(f"❌ 미션 데이터 캐시 저장 실패: {e}")

def load_mission_data_cache() -> Optional[dict]:
    """캐시된 미션 데이터 로드"""
    try:
        if not os.path.exists(MISSION_DATA_CACHE_FILE):
            logger.info("📂 미션 데이터 캐시 파일이 없습니다.")
            return None
        
        with open(MISSION_DATA_CACHE_FILE, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        # 캐시된 데이터의 날짜 확인
        cached_date = cache_data.get('date')
        current_mission_date = get_mission_date()
        
        if cached_date == current_mission_date:
            logger.info(f"✅ 캐시된 미션 데이터 사용: {cached_date}")
            return cache_data.get('peak_data')
        else:
            logger.info(f"🔄 날짜 변경 감지: {cached_date} → {current_mission_date}")
            logger.info("새로운 미션 데이터 크롤링이 필요합니다.")
            return None
    
    except Exception as e:
        logger.error(f"❌ 미션 데이터 캐시 로드 실패: {e}")
        return None

def is_mission_data_fresh() -> bool:
    """미션 데이터가 최신인지 확인"""
    try:
        if not os.path.exists(MISSION_DATA_CACHE_FILE):
            return False
        
        with open(MISSION_DATA_CACHE_FILE, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        cached_date = cache_data.get('date')
        current_mission_date = get_mission_date()
        
        return cached_date == current_mission_date
    
    except Exception as e:
        logger.error(f"미션 데이터 freshness 확인 실패: {e}")
        return False

def get_mission_date():
    """
    미션 기준 날짜를 계산합니다.
    06:00~다음날 03:00를 하나의 미션 날짜로 간주합니다.
    예: 2025-06-15 06:00 ~ 2025-06-16 03:00 = 2025-06-15 미션
    """
    now = datetime.datetime.now()
    
    # 현재 시간이 06:00 이전이면 전날을 미션 날짜로 계산
    if now.time() < datetime.time(6, 0):
        mission_date = now.date() - datetime.timedelta(days=1)
    else:
        mission_date = now.date()
    
    return mission_date.strftime('%Y-%m-%d')

def parse_mission_table_data(html):
    """
    물량 점수관리 테이블에서 미션 데이터를 파싱합니다. (최적화)
    """
    # html.parser 파서 사용으로 속도 향상
    soup = BeautifulSoup(html, 'html.parser')
    
    # 미션 기준 날짜 계산
    target_date = get_mission_date()
    
    # 물량 점수관리 테이블 찾기 (다양한 선택자 시도)
    sla_table = None
    
    # 여러 가능한 선택자들을 시도
    possible_selectors = [
        'table.sla_table[data-type="partner"]',
        'table.sla_table',
        'table[data-type="partner"]',
        '.sla_table',
        'table[id*="sla"]',
        'table[class*="sla"]',
        '.mission_table',
        '.quantity_table'
    ]
    
    # 1단계: CSS 선택자로 테이블 찾기
    for selector in possible_selectors:
        try:
            sla_table = soup.select_one(selector)
            if sla_table:
                logger.info(f"✅ 테이블 발견 (선택자: {selector})")
                break
        except Exception as e:
            continue
    
    # 2단계: 텍스트 내용으로 테이블 찾기
    if not sla_table:
        tables = soup.find_all('table')
        for table in tables:
            table_text = table.get_text()
            if any(keyword in table_text for keyword in ['물량 점수관리', '아침점심피크', '오후논피크', '저녁피크', '심야논피크']):
                sla_table = table
                logger.info(f"✅ 테이블 발견 (텍스트 기반 검색)")
                break
    
    if not sla_table:
        logger.warning("물량 점수관리 테이블을 찾을 수 없습니다.")
        return None
    
    # 모든 행을 한 번에 가져오기
    rows = sla_table.select('tbody tr')
    if not rows:
        # tbody가 없는 경우 tr 직접 선택
        rows = sla_table.select('tr')
    
    target_row = None
    
    # 날짜 매칭 최적화 (정규표현식 미리 컴파일)
    date_pattern = re.compile(target_date)
    for row in rows:
        # 첫 번째 또는 두 번째 셀에서 날짜 찾기
        for idx in range(min(3, len(row.select('td')))):
            date_cell = row.select('td')[idx] if row.select('td') else None
            if date_cell and date_pattern.search(date_cell.get_text(strip=True)):
                target_row = row
                break
        if target_row:
            break
    
    if not target_row:
        logger.warning(f"날짜 {target_date}에 해당하는 데이터를 찾을 수 없습니다.")
        return None
    
    # 모든 셀을 한 번에 파싱
    cells = target_row.select('td')
    if len(cells) < 4:
        logger.warning("테이블 구조가 예상과 다릅니다.")
        return None
    
    # 정규표현식 패턴 미리 컴파일 (성능 향상)
    count_pattern = re.compile(r'(\d+)/(\d+)')
    
    def parse_mission_cell(cell_text):
        """최적화된 미션 셀 파싱"""
        match = count_pattern.search(cell_text)
        if match:
            return int(match.group(1)), int(match.group(2))
        return 0, 0
    
    # 실제 웹사이트 테이블 헤더에 맞는 용어 사용
    web_peak_names = ['아침점심피크', '오후논피크', '저녁피크', '심야논피크']
    # 기존 코드와의 호환성을 위한 용어 매핑
    legacy_peak_names = ['오전피크', '오후피크', '저녁피크', '심야피크']
    
    # 피크별 데이터 병렬 파싱
    # 날짜 셀 다음부터 4개 피크 데이터 추출
    peak_start_idx = 1  # 일반적으로 날짜 다음이 피크 데이터
    for idx, cell in enumerate(cells):
        if date_pattern.search(cell.get_text(strip=True)):
            peak_start_idx = idx + 1
            break
    
    peak_data = {}
    peak_cells = cells[peak_start_idx:peak_start_idx + 4]
    
    for idx, cell in enumerate(peak_cells):
        if idx >= len(web_peak_names):
            break
            
        text = cell.get_text(strip=True)
        current, target = parse_mission_cell(text)
        # 통일된 용어로 저장 (아침점심피크, 오후논피크, 저녁피크, 심야논피크)
        unified_name = web_peak_names[idx] if idx < len(web_peak_names) else f'피크{idx+1}'
        
        peak_data[unified_name] = {
            'current': current, 
            'target': target,
            'progress': (current / target * 100) if target > 0 else 0
        }
        
        # 기존 코드 호환성을 위해 레거시 이름으로도 저장
        if idx < len(legacy_peak_names):
            legacy_name = legacy_peak_names[idx]
            peak_data[legacy_name] = peak_data[unified_name]
    
    logger.info(f"파싱된 미션 데이터 ({target_date}): {len(web_peak_names)}개 피크")
    for name in web_peak_names:
        if name in peak_data:
            data = peak_data[name]
            logger.info(f"✅ {name}: {data['current']}/{data['target']}건 ({data['progress']:.1f}%)")
    
    return peak_data

# 1. Selenium으로 로그인 및 데이터 크롤링 (최적화 + 연결 안정성 개선)
def crawl_jangboo(max_retries=3, retry_delay=5):
    """최적화된 크롤링 함수 (연결 실패 대응 강화)"""
    start_time = time.time()
    driver = None
    
    for attempt in range(max_retries):
        try:
            logger.info(f"크롤링 시도 {attempt + 1}/{max_retries}")
            
            driver = webdriver.Chrome(options=create_chrome_options())
            driver.set_page_load_timeout(30)  # 타임아웃 늘림
            driver.implicitly_wait(10)  # 암시적 대기 추가
            
            # 로그인 페이지 로드 (재시도 로직)
            logger.info(f"로그인 페이지 접속: {LOGIN_URL}")
            driver.get(LOGIN_URL)
            time.sleep(2)  # 페이지 로딩 대기

            # 페이지 로드 완료 확인
            if "jangboo" not in driver.current_url.lower():
                raise Exception(f"예상과 다른 페이지 로드: {driver.current_url}")

            # 로그인 처리
            logger.info("로그인 시도")
            id_field = driver.find_element(By.ID, 'id')
            pw_field = driver.find_element(By.ID, 'password')
            login_btn = driver.find_element(By.ID, 'loginBtn')
            
            # 입력 필드 클리어 후 입력
            id_field.clear()
            id_field.send_keys(USER_ID)
            
            pw_field.clear()
            pw_field.send_keys(USER_PW)
            
            login_btn.click()
            time.sleep(3)  # 로그인 처리 대기

            # 로그인 성공 확인
            current_url = driver.current_url
            logger.info(f"로그인 후 현재 URL: {current_url}")
            
            # HTML 추출
            html = driver.page_source
            
            if len(html) < 1000:  # HTML이 너무 짧으면 실패로 판단
                raise Exception("HTML 길이가 너무 짧습니다. 페이지 로딩 실패 가능성")
            
            logger.info(f"✅ 크롤링 성공 (시도: {attempt + 1}/{max_retries}, 소요시간: {time.time() - start_time:.2f}초)")
            return html
            
        except Exception as e:
            logger.error(f"❌ 크롤링 시도 {attempt + 1} 실패: {e}")
            
            if driver:
                try:
                    driver.quit()
                except:
                    pass
                driver = None
            
            # 마지막 시도가 아니면 재시도
            if attempt < max_retries - 1:
                logger.info(f"⏳ {retry_delay}초 후 재시도...")
                time.sleep(retry_delay)
            else:
                logger.error(f"❌ 모든 크롤링 시도 실패 ({max_retries}회)")
                
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    return None

# 2. BeautifulSoup으로 데이터 파싱 (최적화)
def parse_data(html):
    """최적화된 데이터 파싱 함수"""
    start_time = time.time()
    
    # html.parser 파서 사용으로 속도 향상
    soup = BeautifulSoup(html, 'html.parser')
    
    # 정규표현식 패턴 미리 컴파일 (성능 향상)
    int_pattern = re.compile(r'[\d,]+')  # 쉼표 포함 숫자 패턴
    float_pattern = re.compile(r'(\d+(?:\.\d+)?)')

    def fast_parse_int(selector, default=0):
        """최적화된 정수 파싱 (쉼표 처리 포함)"""
        node = soup.select_one(selector)
        if node:
            match = int_pattern.search(node.get_text(strip=True))
            if match:
                # 쉼표 제거 후 정수 변환
                number_str = match.group().replace(',', '')
                return int(number_str) if number_str.isdigit() else default
        return default

    def fast_parse_float(selector, default=0.0):
        """최적화된 실수 파싱"""
        node = soup.select_one(selector)
        if node:
            match = float_pattern.search(node.get_text(strip=True))
            return float(match.group(1)) if match else default
        return default

    # 한 번에 모든 요소 선택 (병렬 처리)
    selectors = {
        'total_score': '.score_total_value[data-text="total"]',
        'quantity_score': '.detail_score_value[data-text="quantity"]',
        'acceptance_score': '.detail_score_value[data-text="acceptance"]',
        'total_complete': '.etc_value[data-etc="complete"] span',
        'total_reject': '.etc_value[data-etc="reject"] span',
        'acceptance_rate_total': '.etc_value[data-etc="acceptance"] span'
    }
    
    # 병렬로 파싱
    results = {}
    for key, selector in selectors.items():
        if key == 'acceptance_rate_total':
            results[key] = fast_parse_float(selector)
        else:
            results[key] = fast_parse_int(selector)
    
    total_score = results['total_score']
    quantity_score = results['quantity_score']
    acceptance_score = results['acceptance_score']
    total_complete = results['total_complete']
    total_reject = results['total_reject']
    acceptance_rate_total = results['acceptance_rate_total']

    # 물량 점수관리 테이블에서 피크별 데이터 파싱 (캐시 활용)
    logger.info("=== 미션 데이터 파싱 시작 ===")
    
    # 1단계: 캐시된 데이터가 있고 최신인지 확인
    cached_peak_data = load_mission_data_cache()
    if cached_peak_data:
        logger.info("✅ 캐시된 미션 데이터를 사용합니다.")
        peak_data = cached_peak_data
    else:
        logger.info("🔍 새로운 미션 데이터를 크롤링하여 파싱합니다.")
        peak_data = parse_mission_table_data(html)
        
        # 파싱 성공시 캐시에 저장
        if peak_data:
            mission_date = get_mission_date()
            save_mission_data_cache(mission_date, peak_data)
            logger.info("💾 새로운 미션 데이터를 캐시에 저장했습니다.")
    
    # 3단계 Fallback 시스템 (최적화)
    if not peak_data:
        logger.warning("⚠️ 1단계 파싱 실패! 2단계 fallback 시도")
        
        # 2단계: 기존 방식으로 데이터 파싱
        peak_data = {}
        quantity_items = soup.select('.quantity_item')
        logger.info(f"2단계: quantity_item 요소 {len(quantity_items)}개 발견")
        
        if quantity_items:
            # 통일된 용어 사용
            web_peak_names = ['아침점심피크', '오후논피크', '저녁피크', '심야논피크']
            legacy_peak_names = ['오전피크', '오후피크', '저녁피크', '심야피크']
            
            for idx, item in enumerate(quantity_items):
                try:
                    name_node = item.select_one('.quantity_title')
                    current_node = item.select_one('.performance_value')
                    target_node = item.select_one('.number_value span:not(.performance_value)')

                    # 통일된 용어 사용
                    name = web_peak_names[idx] if idx < len(web_peak_names) else f'피크{idx+1}'
                    if name_node:
                        parsed_name = name_node.get_text(strip=True)
                        # 웹사이트에서 가져온 이름을 통일된 용어로 매핑
                        name_mapping = {
                            '오전피크': '아침점심피크',
                            '오후피크': '오후논피크', 
                            '저녁피크': '저녁피크',
                            '심야피크': '심야논피크'
                        }
                        name = name_mapping.get(parsed_name, name)
                    
                    # 최적화된 숫자 파싱
                    current = 0
                    if current_node:
                        current_match = int_pattern.search(current_node.get_text(strip=True))
                        current = int(current_match.group()) if current_match else 0
                    
                    target = 0
                    if target_node:
                        target_match = int_pattern.search(target_node.get_text(strip=True))
                        target = int(target_match.group()) if target_match else 0
                    
                    if name:
                        peak_data[name] = {
                            'current': current,
                            'target': target,
                            'progress': (current / target * 100) if target > 0 else 0
                        }
                        
                        # 기존 코드 호환성을 위해 레거시 이름으로도 저장
                        if idx < len(legacy_peak_names):
                            legacy_name = legacy_peak_names[idx]
                            if name != legacy_name:  # 중복 저장 방지
                                peak_data[legacy_name] = peak_data[name]
                        
                        logger.info(f"  2단계 파싱: {name} = {current}/{target}건")
                        
                except Exception as e:
                    logger.warning(f"아이템 {idx} 파싱 실패: {e}")
                    continue
        
        # 3단계: 2단계도 실패했다면 최소한의 기본 구조 제공
        if not peak_data or len(peak_data) == 0:
            logger.warning("⚠️ 2단계 파싱도 실패! 3단계: 기본 구조 적용 (크롤링 시 업데이트 필요)")
            # 기본 구조만 제공하고 실제 데이터는 크롤링에서 가져와야 함
            peak_data = {
                '아침점심피크': {'current': 0, 'target': 0, 'progress': 0},
                '오후논피크': {'current': 0, 'target': 0, 'progress': 0},
                '저녁피크': {'current': 0, 'target': 0, 'progress': 0},
                '심야논피크': {'current': 0, 'target': 0, 'progress': 0},
                # 기존 코드 호환성
                '오전피크': {'current': 0, 'target': 0, 'progress': 0},
                '오후피크': {'current': 0, 'target': 0, 'progress': 0},
                '심야피크': {'current': 0, 'target': 0, 'progress': 0}
            }
            logger.warning("  ⚠️ 3단계: 기본 구조 적용됨. 실제 미션 데이터 크롤링 필요!")
        else:
            # 2단계 파싱이 성공했으므로 실제 데이터를 그대로 사용
            logger.info("✅ 2단계 파싱 성공! 실제 크롤링된 데이터를 사용합니다.")
            for peak, data in peak_data.items():
                if isinstance(data, dict) and 'current' in data:
                    logger.info(f"  ✅ {peak}: {data['current']}/{data['target']}건 ({data.get('progress', 0):.1f}%)")
    else:
        logger.info("✅ 1단계 테이블 파싱 성공!")
        for peak, data in peak_data.items():
            logger.info(f"  {peak}: {data['current']}/{data['target']}건 ({data.get('progress', 0):.1f}%)")
    
    logger.info(f"파싱 완료 (소요시간: {time.time() - start_time:.2f}초)")

    # 라이더별 데이터 추출
    riders = []
    rider_items = soup.select('.rider_item')
    for rider in rider_items:
        name = rider.select_one('.rider_name').text.strip().split('수락률')[0].strip()
        # 라이더별 수락률 추출 (정확한 구조 반영)
        acceptance_rate = None
        acc_node = rider.select_one('.rider_contents.acceptance_rate')
        if acc_node:
            acc_text = acc_node.get_text()
            match = re.search(r'(\d+(?:\.\d+)?)\s*%', acc_text)
            if match:
                acceptance_rate = float(match.group(1))
        if acceptance_rate is None:
            acceptance_rate = 0.0
        # 거절 건수 추출
        reject = 0
        reject_node = rider.select_one('.rider_contents.reject_count')
        if reject_node:
            reject_text = reject_node.get_text()
            match = re.search(r'(\d+)', reject_text)
            if match:
                reject = int(match.group(1))
        # 배차취소 건수 추출
        cancel = 0
        cancel_node = rider.select_one('.rider_contents.accept_cancel_count')
        if cancel_node:
            cancel_text = cancel_node.get_text()
            match = re.search(r'(\d+)', cancel_text)
            if match:
                cancel = int(match.group(1))
        # 숫자만 추출
        complete_text = rider.select_one('.complete_count').text
        complete = int(re.search(r'\d+', complete_text).group()) if re.search(r'\d+', complete_text) else 0
        morning = int(re.search(r'\d+', rider.select_one('.morning_peak_count').text).group()) if re.search(r'\d+', rider.select_one('.morning_peak_count').text) else 0
        afternoon = int(re.search(r'\d+', rider.select_one('.afternoon_peak_count').text).group()) if re.search(r'\d+', rider.select_one('.afternoon_peak_count').text) else 0
        evening = int(re.search(r'\d+', rider.select_one('.evening_peak_count').text).group()) if re.search(r'\d+', rider.select_one('.evening_peak_count').text) else 0
        midnight = int(re.search(r'\d+', rider.select_one('.midnight_peak_count').text).group()) if re.search(r'\d+', rider.select_one('.midnight_peak_count').text) else 0
        riders.append({
            'name': name,
            'complete': complete,
            # 새로운 통일된 용어
            '아침점심피크': morning,
            '오후논피크': afternoon,
            '저녁피크': evening,
            '심야논피크': midnight,
            # 기존 호환성 유지
            '오전피크': morning,
            '오후피크': afternoon,
            '심야피크': midnight,
            'acceptance_rate': acceptance_rate,
            'reject': reject,
            'cancel': cancel
        })

    # 라이더별 미션 기여도 계산 (각 피크별 기여도의 평균)
    peak_names = ['오전피크', '오후피크', '저녁피크', '심야피크']
    for rider in riders:
        peak_contributions = []
        
        for peak in peak_names:
            target = peak_data.get(peak, {'target': 0})['target']
            performed = rider.get(peak, 0)
            
            if target > 0:
                # 각 피크별 기여도 = (개인 수행 ÷ 목표) × 100
                peak_contribution = (performed / target) * 100
                peak_contributions.append(peak_contribution)
            else:
                # 목표가 0이면 기여도도 0
                peak_contributions.append(0)
        
        # 4개 피크의 평균 기여도
        rider['contribution'] = round(sum(peak_contributions) / len(peak_contributions), 1)
        
        # 디버깅용: 각 피크별 기여도도 저장
        rider['peak_contributions'] = {
            '오전피크': round(peak_contributions[0], 1),
            '오후피크': round(peak_contributions[1], 1),
            '저녁피크': round(peak_contributions[2], 1),
            '심야피크': round(peak_contributions[3], 1)
        }

    # 새로운 용어와 기존 용어 모두 포함하여 데이터 구성
    data = {
        # 새로운 통일된 용어
        '아침점심피크': peak_data.get('아침점심피크', peak_data.get('오전피크', {'current': 0, 'target': 0})),
        '오후논피크': peak_data.get('오후논피크', peak_data.get('오후피크', {'current': 0, 'target': 0})),
        '저녁피크': peak_data.get('저녁피크', {'current': 0, 'target': 0}),
        '심야논피크': peak_data.get('심야논피크', peak_data.get('심야피크', {'current': 0, 'target': 0})),
        # 기존 호환성 유지
        '오전피크': peak_data.get('오전피크', peak_data.get('아침점심피크', {'current': 0, 'target': 0})),
        '오후피크': peak_data.get('오후피크', peak_data.get('오후논피크', {'current': 0, 'target': 0})),
        '심야피크': peak_data.get('심야피크', peak_data.get('심야논피크', {'current': 0, 'target': 0})),
        '총점': total_score,
        '물량점수': quantity_score,
        '수락률점수': acceptance_score,
        '총완료': total_complete,
        '총거절': total_reject,
        '수락률': acceptance_rate_total,
        'riders': riders
    }
    return data

# 3. 미션 달성/부족 계산 및 메시지 포맷팅
def get_active_peaks():
    """현재 시간에 맞는 활성 피크 확인 (간소화)"""
    now = datetime.datetime.now()
    current_hour = now.hour
    
    # 시간대별 피크 매핑
    time_peak_map = {
        (6, 13): '아침점심피크',
        (13, 17): '오후논피크', 
        (17, 20): '저녁피크',
        (20, 6): '심야논피크'  # 20시~다음날 6시
    }
    
    active_peaks = []
    
    # 03:00~06:00는 미션 준비 시간
    if 3 <= current_hour < 6:
        return active_peaks
    
    for (start, end), peak_name in time_peak_map.items():
        if start < end:  # 일반 범위
            is_active = start <= current_hour < end
        else:  # 자정을 넘는 범위 (심야)
            is_active = current_hour >= start or current_hour < end
        
        if is_active:
            active_peaks.append(peak_name)
    
    return active_peaks

def make_message(data):
    """데이터를 기반으로 카카오톡에 보낼 깔끔한 포맷의 메시지를 생성합니다."""
    
    # 0. 날씨 정보 추가
    try:
        from weather_service import get_ansan_weather
        weather_info = get_ansan_weather()
    except Exception as e:
        weather_info = "⚠️ 날씨 정보를 가져올 수 없습니다."
        print(f"날씨 정보 조회 실패: {e}")
    
    # 1. 미션 현황 섹션
    mission_status_parts = []
    lacking_missions = []
    
    # 통일된 용어 사용
    peak_order = ['아침점심피크', '오후논피크', '저녁피크', '심야논피크']
    peak_emojis = {
        '아침점심피크': '🌅', 
        '오후논피크': '🌇', 
        '저녁피크': '🌃', 
        '심야논피크': '🌙'
    }
    
    # 현재 시간 기준으로 시작된 피크들과 완료된 피크들을 모두 표시
    active_peaks = get_active_peaks()
    now = datetime.datetime.now()
    current_hour = now.hour
    
    for key in peak_order:
        # 통일된 용어로 데이터 가져오기
        peak_info = data.get(key, {'current': 0, 'target': 0})
        
        cur = peak_info.get('current', 0)
        tgt = peak_info.get('target', 0)
        
        # 목표값이 0이면 표시하지 않음
        if tgt == 0:
            continue
            
        # 시간대별로 표시 여부 결정
        should_show = False
        if key == '아침점심피크' and current_hour >= 6:  # 6시 이후부터 표시
            should_show = True
        elif key == '오후논피크' and current_hour >= 13:  # 13시 이후부터 표시
            should_show = True
        elif key == '저녁피크' and current_hour >= 17:  # 17시 이후부터 표시
            should_show = True
        elif key == '심야논피크' and (current_hour >= 20 or current_hour < 6):  # 20시~다음날 6시
            should_show = True
            
        if not should_show:
            continue
            
        if cur >= tgt:
            status = '✅ (달성)'
        else:
            status = f'❌ ({tgt-cur}건 부족)'
            lacking_missions.append(f'{key.replace("피크","").replace("논","")} {tgt-cur}건')
        
        mission_status_parts.append(f"{peak_emojis.get(key, '')} {key}: {cur}/{tgt} {status}")

    mission_status_str = "\n".join(mission_status_parts)

    # 2. 종합 정보 섹션
    summary_str = (
        f'총점: {data.get("총점", 0)}점 (물량:{data.get("물량점수", 0)}, 수락률:{data.get("수락률점수", 0)})\n'
        f'수락률: {data.get("수락률", 0.0)}% | 완료: {data.get("총완료", 0)} | 거절: {data.get("총거절", 0)}'
    )
    
    # 3. 라이더별 기여도 섹션
    rider_parts = []
    # 'complete' 건수가 1 이상인 라이더만 필터링하고, 'contribution' 기준으로 내림차순 정렬
    sorted_riders = sorted(
        [r for r in data.get('riders', []) if r.get('complete', 0) > 0], 
        key=lambda x: x.get('contribution', 0), 
        reverse=True
    )
    
    top_riders = sorted_riders[:3]
    other_riders = sorted_riders[3:]

    # TOP 3 라이더
    if top_riders:
        rider_parts.append("🏆 <b>TOP 3 라이더</b>")
        medals = ['🥇', '🥈', '🥉']
        for i, rider in enumerate(top_riders):
            bar_len = 12
            filled = int(round(rider.get('contribution', 0) / 100 * bar_len))
            bar = '■' * filled + '─' * (bar_len - filled)
            
            # 모든 정보를 포함한 라인 (통일된 용어 사용)
            details = (
                f"총 {rider.get('complete', 0)}건 (아침:{rider.get('아침점심피크',0)}/오후:{rider.get('오후논피크',0)}/저녁:{rider.get('저녁피크',0)}/심야:{rider.get('심야논피크',0)})\n"
                f"    └ 수락률: {rider.get('acceptance_rate', 0.0)}% (거절:{rider.get('reject', 0)}, 취소:{rider.get('cancel', 0)})"
            )
            rider_parts.append(f"{medals[i]} {rider.get('name', '이름없음')} | [{bar}] {rider.get('contribution', 0.0)}%\n    └ {details}")

    # 기타 라이더
    if other_riders:
        if top_riders:
             rider_parts.append("─" * 15)
        rider_parts.append("🏃 <b>그 외 라이더</b>")
        for i, rider in enumerate(other_riders, 4):
            details = (
                f"총 {rider.get('complete', 0)}건 (아침:{rider.get('아침점심피크',0)}/오후:{rider.get('오후논피크',0)}/저녁:{rider.get('저녁피크',0)}/심야:{rider.get('심야논피크',0)})\n"
                f"   └ 수락률: {rider.get('acceptance_rate', 0.0)}% (거절:{rider.get('reject', 0)}, 취소:{rider.get('cancel', 0)})"
            )
            rider_parts.append(f"{i}. {rider.get('name', '이름없음')} ({rider.get('contribution', 0.0)}%)\n   └ {details}")

    rider_str = "\n".join(rider_parts)

    # 최종 메시지 조합
    separator = "\n" + "─" * 22 + "\n"
    
    msg = (
        f"📊 <b>미션 현황 리포트</b>\n"
        f"{mission_status_str}"
        f"{separator}"
        f"{weather_info}"
        f"{separator}"
        f"{summary_str}"
        f"{separator}"
        f"{rider_str}"
    )
    
    if lacking_missions:
        msg += f"{separator}⚠️ **미션 부족**: {', '.join(lacking_missions)}"

    msg += '\n\n(그래프 이미지는 첨부파일로 전송됩니다.)'
    
    return msg

# ========== 최적화된 Chrome 옵션 (전역에서 사용) ==========
def create_chrome_options():
    """통합된 Chrome 옵션 생성"""
    options = Options()
    chrome_args = [
        '--headless', '--no-sandbox', '--disable-dev-shm-usage',
        '--disable-gpu', '--disable-images', '--memory-pressure-off',
        '--max_old_space_size=4096', '--disable-web-security',
        '--disable-features=VizDisplayCompositor', '--disable-extensions',
        '--no-first-run', '--ignore-certificate-errors', '--ignore-ssl-errors',
        '--ignore-certificate-errors-spki-list',
        '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    ]
    
    for arg in chrome_args:
        options.add_argument(arg)
    
    return options

# ========== 메시지 전송 설정 통합 ==========
MESSAGE_CONFIGS = {
    'telegram': {
        'token': os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN'),
        'chat_id': os.getenv('TELEGRAM_CHAT_ID', 'YOUR_CHAT_ID')
    },
    'slack': {'webhook_url': os.getenv('SLACK_WEBHOOK_URL', 'YOUR_SLACK_WEBHOOK_URL')},
    'discord': {'webhook_url': os.getenv('DISCORD_WEBHOOK_URL', 'YOUR_DISCORD_WEBHOOK_URL')},
    'kakao': {'webhook_url': os.getenv('KAKAO_OPENBUILDER_URL', 'YOUR_KAKAO_OPENBUILDER_WEBHOOK_URL')}
}

# 피크 시간대 매핑 (통일된 용어)
PEAK_NAMES = {
    'web': ['아침점심피크', '오후논피크', '저녁피크', '심야논피크'],
    'legacy': ['오전피크', '오후피크', '저녁피크', '심야피크']
}

# ========== 통합 메시지 전송 시스템 ==========

class MessageSender:
    """통합 메시지 전송 클래스"""
    
    @staticmethod
    def safe_request(method, url, **kwargs):
        """안전한 HTTP 요청"""
        try:
            response = requests.request(method, url, timeout=10, **kwargs)
            return response.status_code in [200, 204]
        except Exception as e:
            logger.error(f"HTTP 요청 실패: {e}")
            return False
    
    @staticmethod
    def send_telegram(message: str) -> bool:
        """텔레그램 메시지 전송"""
        config = MESSAGE_CONFIGS['telegram']
        if config['token'] == 'YOUR_TELEGRAM_BOT_TOKEN':
            return False
        
        url = f"https://api.telegram.org/bot{config['token']}/sendMessage"
        payload = {
            'chat_id': config['chat_id'],
            'text': message.replace('**', '*'),  # 마크다운 변환
            'parse_mode': 'Markdown'
        }
        
        success = MessageSender.safe_request('POST', url, json=payload)
        if success:
            logger.info("✅ 텔레그램 전송 성공")
        return success
    
    @staticmethod
    def send_slack(message: str) -> bool:
        """슬랙 메시지 전송"""
        config = MESSAGE_CONFIGS['slack']
        if config['webhook_url'] == 'YOUR_SLACK_WEBHOOK_URL':
            return False
        
        payload = {
            "text": "🚚 장부 모니터링 알림",
            "blocks": [{"type": "section", "text": {"type": "mrkdwn", "text": f"```{message}```"}}]
        }
        
        success = MessageSender.safe_request('POST', config['webhook_url'], json=payload)
        if success:
            logger.info("✅ 슬랙 전송 성공")
        return success
    
    @staticmethod
    def send_discord(message: str) -> bool:
        """디스코드 메시지 전송"""
        config = MESSAGE_CONFIGS['discord']
        if config['webhook_url'] == 'YOUR_DISCORD_WEBHOOK_URL':
            return False
        
        payload = {"content": f"🚚 **장부 모니터링 알림**\n```\n{message}\n```"}
        
        success = MessageSender.safe_request('POST', config['webhook_url'], json=payload)
        if success:
            logger.info("✅ 디스코드 전송 성공")
        return success
    
    @staticmethod
    def send_kakao(message: str) -> bool:
        """카카오 오픈빌더 메시지 전송"""
        config = MESSAGE_CONFIGS['kakao']
        if config['webhook_url'] == 'YOUR_KAKAO_OPENBUILDER_WEBHOOK_URL':
            return False
        
        payload = {
            "version": "2.0",
            "template": {"outputs": [{"simpleText": {"text": message}}]}
        }
        
        success = MessageSender.safe_request('POST', config['webhook_url'], json=payload)
        if success:
            logger.info("✅ 카카오 전송 성공")
        return success

def send_message(message: str) -> bool:
    """메시지 전송 (여러 방법 시도)"""
    senders = [
        MessageSender.send_telegram,
        MessageSender.send_slack,
        MessageSender.send_discord,
        MessageSender.send_kakao
    ]
    
    for sender in senders:
        try:
            if sender(message):
                return True
        except Exception as e:
            logger.warning(f"메시지 전송 실패: {e}")
    
    # 모든 방법 실패시 콘솔 출력
    logger.error("⚠️ 모든 메시지 전송 방법 실패, 콘솔에 출력")
    print("📱 장부 모니터링 알림:")
    print("=" * 50)
    print(message)
    print("=" * 50)
    return False

# ========== 간소화된 그래프 생성 ==========

def draw_peak_graph(data, save_path='mission_graph.png'):
    """피크 그래프 생성 (간소화)"""
    peak_data = data.get('peak_data', {})
    peaks = PEAK_NAMES['legacy']  # 기존 호환성
    
    수행량 = [peak_data.get(p, {}).get('current', 0) for p in peaks]
    목표량 = [peak_data.get(p, {}).get('target', 0) for p in peaks]
    
    plt.figure(figsize=(12, 8))
    x = np.arange(len(peaks))
    width = 0.35
    
    plt.bar(x - width/2, 목표량, width, label='목표량', color='lightblue', alpha=0.7)
    plt.bar(x + width/2, 수행량, width, label='수행량', color='orange', alpha=0.8)
    
    plt.xlabel('피크 시간대')
    plt.ylabel('미션 수량 (건)')
    plt.title('피크별 미션 현황')
    plt.xticks(x, peaks)
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()

# 5. 전체 플로우 함수
def job():
    """메인 작업 함수 - 데이터 크롤링 및 메시지 전송 (연결 실패 대응 강화)"""
    try:
        logger.info("🔄 작업 시작")
        
        # 미션 데이터 freshness 체크
        if not is_mission_data_fresh():
            logger.info("🆕 미션 데이터가 오래되었거나 없습니다. 새로 크롤링합니다.")
            
        # 강화된 크롤링 (재시도 포함)
        html = crawl_jangboo(max_retries=3, retry_delay=5)
        
        if html:
            logger.info("✅ 크롤링 성공, 데이터 파싱 시작")
            data = parse_data(html)
            
            # 그래프 생성 (에러 처리 추가)
            try:
                draw_peak_graph(data)
                logger.info("📊 그래프 생성 완료")
            except Exception as graph_error:
                logger.warning(f"⚠️ 그래프 생성 실패 (계속 진행): {graph_error}")
            
            # 메시지 생성 및 전송
            try:
                msg = make_message(data)
                send_message(msg)
                logger.info("✅ 메시지 전송 완료")
            except Exception as msg_error:
                logger.warning(f"⚠️ 메시지 전송 실패: {msg_error}")
            
            logger.info("✅ 작업 완료")
            
        else:
            # 크롤링 실패 시 상세한 에러 메시지와 대안 제시
            error_msg = """❌ 크롤링 연결 실패

🔍 가능한 원인:
• 인터넷 연결 문제
• VPN 연결 문제  
• 웹사이트 일시적 접근 불가
• 로그인 정보 변경 필요
• 웹사이트 구조 변경

💡 권장 해결 방법:
1. 인터넷 연결 상태 확인
2. VPN 연결 상태 확인 (필요시 재연결)
3. 몇 분 후 자동 재시도
4. 계속 실패시 로그인 정보 확인 필요

⏰ 다음 자동 재시도: 10분 후"""
            
            logger.error(error_msg)
            
            # 캐시된 데이터가 있다면 사용
            cached_data = load_mission_data_cache()
            if cached_data:
                logger.info("📦 캐시된 데이터로 제한적 서비스 제공")
                try:
                    # 캐시 데이터로 기본 메시지 생성
                    fallback_data = {
                        'peak_data': cached_data,
                        'total_score': 0,
                        'riders': []
                    }
                    cached_msg = f"""⚠️ 연결 문제로 캐시 데이터 사용

{make_message(fallback_data)}

📝 참고: 실시간 점수/라이더 정보는 연결 복구 후 업데이트됩니다."""
                    send_message(cached_msg)
                    logger.info("💾 캐시 데이터로 메시지 전송 완료")
                except Exception as cache_error:
                    logger.error(f"❌ 캐시 데이터 메시지 전송 실패: {cache_error}")
            else:
                logger.warning("⚠️ 캐시된 데이터도 없습니다. 연결 복구 대기 중...")
                
    except Exception as e:
        logger.error(f"❌ 작업 중 예상치 못한 오류 발생: {e}")
        logger.error(f"오류 타입: {type(e).__name__}")
        
        # 시스템 상태 체크
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            logger.info("✅ 기본 인터넷 연결은 정상입니다")
        except:
            logger.error("❌ 기본 인터넷 연결도 실패. 네트워크 설정을 확인하세요")
        
        # 에러 알림 전송 시도
        try:
            error_notification = f"""🚨 시스템 오류 발생

오류: {str(e)}
시간: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

자동 복구를 시도합니다..."""
            send_kakao_message(error_notification)
        except:
            logger.error("❌ 오류 알림 전송도 실패했습니다")

# 6. 스마트 스케줄링 시스템
def setup_smart_schedule():
    """스마트 스케줄링 설정 - 사용자 정의 가능"""
    
    # 기본 설정: 10분 간격
    schedule.every(10).minutes.do(job)
    
    # 피크 시간 집중 모니터링 (5분 간격)
    peak_hours = [11, 12, 13, 17, 18, 19]  # 피크 시간대
    for hour in peak_hours:
        schedule.every().day.at(f"{hour:02d}:00").do(job)
        schedule.every().day.at(f"{hour:02d}:05").do(job)
        schedule.every().day.at(f"{hour:02d}:10").do(job)
        schedule.every().day.at(f"{hour:02d}:15").do(job)
        schedule.every().day.at(f"{hour:02d}:20").do(job)
        schedule.every().day.at(f"{hour:02d}:25").do(job)
        schedule.every().day.at(f"{hour:02d}:30").do(job)
        schedule.every().day.at(f"{hour:02d}:35").do(job)
        schedule.every().day.at(f"{hour:02d}:40").do(job)
        schedule.every().day.at(f"{hour:02d}:45").do(job)
        schedule.every().day.at(f"{hour:02d}:50").do(job)
        schedule.every().day.at(f"{hour:02d}:55").do(job)

def main():
    """메인 실행 함수 - 설정 확인 및 모니터링 시작"""
    
    print("🚀 장부 모니터링 시스템 시작")
    print("="*50)
    
    # 설정 확인
    print("📊 현재 설정:")
    print(f"   • 미션 데이터 기준: 06:00~다음날 03:00")
    print(f"   • 알림 시간: 10:00~00:00")
    print(f"   • 모니터링 간격: 10분 (피크시간 5분)")
    print()
    
    # 메시지 전송 방법 확인
    message_methods = []
    if MESSAGE_CONFIGS['telegram']['token'] != "YOUR_TELEGRAM_BOT_TOKEN":
        message_methods.append("텔레그램")
    if MESSAGE_CONFIGS['slack']['webhook_url'] != "YOUR_SLACK_WEBHOOK_URL":
        message_methods.append("슬랙")
    if MESSAGE_CONFIGS['discord']['webhook_url'] != "YOUR_DISCORD_WEBHOOK_URL":
        message_methods.append("디스코드")
    if MESSAGE_CONFIGS['kakao']['webhook_url'] != "YOUR_KAKAO_OPENBUILDER_WEBHOOK_URL":
        message_methods.append("카카오 오픈빌더")
    
    if message_methods:
        print(f"📱 설정된 알림 방법: {', '.join(message_methods)}")
    else:
        print("⚠️ 알림 방법이 설정되지 않음 (콘솔 출력만)")
        print("   설정 방법: python3 kakao_setup_guide.py 실행")
    
    print()
    print("🎯 현재 미션 날짜:", get_mission_date())
    print("⏰ 현재 시각:", datetime.datetime.now().strftime("%H:%M:%S"))
    print()
    
    # 즉시 실행 여부 확인
    now = datetime.datetime.now()
    current_hour = now.hour
    is_service_time = 10 <= current_hour <= 23
    
    if is_service_time:
        print("✅ 알림 시간대입니다. 즉시 첫 모니터링을 시작합니다.")
        try:
            job()
        except Exception as e:
            logger.error(f"초기 실행 실패: {e}")
    else:
        print("💤 현재 휴식 시간대입니다. 10:00부터 알림을 시작합니다.")
    
    # 스케줄 설정
    setup_smart_schedule()
    
    print("\n🔄 스케줄러가 시작되었습니다.")
    print("   • 중지하려면 Ctrl+C를 누르세요")
    print("   • 실시간 로그를 확인하세요")
    print()
    
    try:
        while True:
            # 현재 시간이 서비스 시간인지 확인
            current_time = datetime.datetime.now()
            if 10 <= current_time.hour <= 23:
                schedule.run_pending()
            time.sleep(60)  # 1분마다 확인
            
    except KeyboardInterrupt:
        print("\n\n⏹️ 모니터링이 중지되었습니다.")
        print("감사합니다! 🙏")

def quick_test():
    """빠른 테스트 실행"""
    print("🧪 빠른 테스트 실행")
    print("-" * 30)
    
    try:
        # 크롤링 테스트
        print("1️⃣ 크롤링 테스트...")
        html = crawl_jangboo()
        if html:
            print("   ✅ 크롤링 성공")
        else:
            print("   ❌ 크롤링 실패")
            return
        
        # 파싱 테스트
        print("2️⃣ 데이터 파싱 테스트...")
        data = parse_data(html)
        if data:
            print("   ✅ 파싱 성공")
            print(f"   📊 미션 데이터: {len(data.get('riders', []))}명 라이더")
        else:
            print("   ❌ 파싱 실패")
            return
        
        # 메시지 생성 테스트
        print("3️⃣ 메시지 생성 테스트...")
        message = make_message(data)
        if message:
            print("   ✅ 메시지 생성 성공")
        
        # 메시지 전송 테스트
        print("4️⃣ 메시지 전송 테스트...")
        success = send_kakao_message(message)
        if success:
            print("   ✅ 메시지 전송 성공")
        else:
            print("   ⚠️ 메시지 전송 실패 (설정 확인 필요)")
        
        print("\n🎉 테스트 완료!")
        
    except Exception as e:
        print(f"   ❌ 테스트 중 오류: {e}")
        logger.error(f"테스트 실패: {e}")



# 카카오 오픈빌더 웹훅 서버 클래스
class KakaoOpenBuilderServer:
    """카카오 오픈빌더 웹훅 서버"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.latest_data = None
        self.setup_routes()
        
    def setup_routes(self):
        """Flask 라우트 설정"""
        
        @self.app.route('/webhook', methods=['POST'])
        def webhook():
            """카카오 오픈빌더 웹훅 엔드포인트"""
            try:
                data = request.get_json()
                logger.info(f"카카오 웹훅 요청: {json.dumps(data, ensure_ascii=False, indent=2)}")
                
                # 사용자 발화 추출
                user_utterance = ""
                if 'userRequest' in data and 'utterance' in data['userRequest']:
                    user_utterance = data['userRequest']['utterance'].strip()
                
                logger.info(f"사용자 발화: {user_utterance}")
                
                # 발화에 따른 응답 처리
                if any(keyword in user_utterance.lower() for keyword in ['현황', '모니터링', '장부', '미션', '상태', '확인']):
                    # 실시간 모니터링 실행
                    try:
                        html = crawl_jangboo()
                        if html:
                            parsed_data = parse_data(html)
                            if parsed_data:
                                message = self.format_monitoring_message(parsed_data)
                                response = self.create_response_template(message)
                            else:
                                response = self.create_response_template("📊 데이터 파싱에 실패했습니다.")
                        else:
                            response = self.create_response_template("📊 데이터를 가져올 수 없습니다.")
                    except Exception as e:
                        logger.error(f"모니터링 실행 오류: {e}")
                        response = self.create_response_template("❌ 모니터링 중 오류가 발생했습니다.")
                        
                elif any(keyword in user_utterance.lower() for keyword in ['새로고침', '업데이트', '갱신', 'refresh']):
                    # 강제 새로고침
                    try:
                        html = crawl_jangboo()
                        if html:
                            parsed_data = parse_data(html)
                            if parsed_data:
                                message = self.format_monitoring_message(parsed_data)
                                response = self.create_response_template(f"🔄 업데이트 완료!\n\n{message}")
                            else:
                                response = self.create_response_template("❌ 데이터 파싱 실패")
                        else:
                            response = self.create_response_template("❌ 데이터 가져오기 실패")
                    except Exception as e:
                        logger.error(f"새로고침 오류: {e}")
                        response = self.create_response_template("❌ 새로고침 중 오류가 발생했습니다.")
                        
                elif any(keyword in user_utterance.lower() for keyword in ['도움', 'help', '사용법', '명령어']):
                    help_message = """📖 장부 모니터링 봇 사용법:

🔸 '현황' - 실시간 미션 현황 보기
🔸 '새로고침' - 최신 데이터로 업데이트  
🔸 '도움' - 이 도움말 보기

⏰ 자동 업데이트 시간:
• 평시: 10분마다
• 피크시간(11-13시, 17-19시): 5분마다
• 운영시간: 10:00~00:00

💡 '현황'이라고 말하면 최신 정보를 확인할 수 있습니다!"""
                    response = self.create_response_template(help_message)
                    
                elif any(keyword in user_utterance.lower() for keyword in ['안녕', 'hello', 'hi', '시작', '처음']):
                    welcome_message = """👋 안녕하세요! 장부 모니터링 봇입니다.

🚚 실시간으로 배달 미션 현황을 모니터링하여
오픈채팅방에 알려드립니다.

📝 주요 기능:
• 실시간 미션 달성률 확인
• 라이더별 기여도 분석  
• 피크시간 자동 알림

💬 '현황'이라고 말해보세요!"""
                    response = self.create_response_template(welcome_message)
                    
                else:
                    # 기본 응답 - 스마트 키워드 매칭
                    default_message = """🤖 무엇을 도와드릴까요?

📋 사용 가능한 명령어:
• '현황' - 실시간 미션 현황
• '새로고침' - 데이터 업데이트
• '도움' - 상세 사용법

🔍 또는 다음과 같이 말해보세요:
"미션 어떻게 되어가?", "현재 상황은?", "업데이트해줘" 등

💡 자연스러운 대화로 정보를 확인하세요!"""
                    response = self.create_response_template(default_message)
                
                return jsonify(response)
                
            except Exception as e:
                logger.error(f"웹훅 처리 오류: {e}")
                error_response = self.create_response_template("❌ 처리 중 오류가 발생했습니다.\n잠시 후 다시 시도해주세요.")
                return jsonify(error_response)
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """헬스 체크"""
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.datetime.now().isoformat(),
                "server": "카카오 오픈빌더 웹훅 서버",
                "mission_date": get_mission_date()
            })
        
        @self.app.route('/test', methods=['GET'])
        def test():
            """테스트 엔드포인트"""
            test_response = self.create_response_template("🧪 테스트 응답입니다!\n서버가 정상 작동중입니다.")
            return jsonify(test_response)
    
    def format_monitoring_message(self, data):
        """모니터링 데이터를 카카오톡 형식으로 포맷"""
        if not data:
            return "📊 데이터가 없습니다."
        
        message = f"📊 장부 모니터링\n"
        message += f"📅 {datetime.datetime.now().strftime('%m/%d %H:%M')}\n\n"
        
        # 미션 현황
        if 'missions' in data:
            message += "🎯 미션 현황:\n"
            for peak_name, peak_info in data['missions'].items():
                current = peak_info.get('current', 0)
                target = peak_info.get('target', 0)
                progress = peak_info.get('progress', 0)
                status = "✅" if current >= target else "⏳"
                message += f"{status} {peak_name}: {current}/{target}건 ({progress:.1f}%)\n"
        
        # 라이더 요약
        if 'riders' in data:
            riders_count = len(data['riders'])
            active_riders = len([r for r in data['riders'] if r.get('complete', 0) > 0])
            message += f"\n👥 라이더: 총 {riders_count}명 (활동중 {active_riders}명)"
        
        return message
    
    def create_response_template(self, message):
        """카카오 오픈빌더 응답 템플릿"""
        return {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": message
                        }
                    }
                ],
                "quickReplies": [
                    {
                        "action": "message",
                        "label": "📊 현황",
                        "messageText": "현황"
                    },
                    {
                        "action": "message", 
                        "label": "🔄 새로고침",
                        "messageText": "새로고침"
                    },
                    {
                        "action": "message",
                        "label": "📖 도움",
                        "messageText": "도움"
                    }
                ]
            }
        }
    
    def start_server(self, port=5000):
        """웹훅 서버 시작"""
        print(f"🔶 카카오 오픈빌더 웹훅 서버 시작 (포트: {port})")
        print(f"🔗 웹훅 URL: http://localhost:{port}/webhook")
        print(f"❤️ 헬스체크: http://localhost:{port}/health")
        print(f"🧪 테스트: http://localhost:{port}/test")
        print("⚠️  카카오 오픈빌더에서 위 웹훅 URL을 스킬 서버로 등록하세요.")
        print("📱 ngrok 사용시: ngrok http 5000")
        
        self.app.run(host='0.0.0.0', port=port, debug=False)

def run_kakao_webhook_server():
    """카카오 오픈빌더 웹훅 서버 실행"""
    print("\n🔶 카카오 오픈빌더 설정 가이드")
    print("="*60)
    print("📋 1단계: 카카오 오픈빌더 챗봇 생성")
    print("  1. https://chatbot.kakao.com 접속")
    print("  2. 카카오 계정으로 로그인")
    print("  3. '챗봇 만들기' 클릭")
    print("  4. 챗봇 이름: '장부 모니터링 봇'")
    print()
    print("📋 2단계: 시나리오 설정")
    print("  1. '시나리오' 탭 클릭")
    print("  2. '폴백 블록' 선택")
    print("  3. '스킬' 추가")
    print("  4. 스킬 URL: http://localhost:5000/webhook")
    print("     (실제 운영시 공개 URL 필요)")
    print()
    print("📋 3단계: 공개 URL 생성 (개발용)")
    print("  1. 터미널에서: brew install ngrok")
    print("  2. 실행: ngrok http 5000")
    print("  3. https://abcd1234.ngrok.io/webhook 형태 URL 복사")
    print("  4. 카카오 오픈빌더 스킬 URL에 등록")
    print()
    print("📋 4단계: 테스트")
    print("  1. 카카오 오픈빌더에서 '시뮬레이션' 클릭")
    print("  2. '현황'이라고 입력하여 테스트")
    print("  3. 정상 작동 확인 후 배포 신청")
    print()
    print("⚠️ 중요사항:")
    print("  - 직접 메시지 발송 불가 (카카오 정책)")
    print("  - 사용자 발화에만 응답 가능")
    print("  - 오픈채팅방 관리자가 봇 초대 필요")
    print("  - 24시간 운영시 서버 배포 필요")
    print()
    
    # 웹훅 서버 시작
    server = KakaoOpenBuilderServer()
    server.start_server()

def test_table_parsing():
    """
    테이블 파싱 로직을 테스트하는 함수
    """
    # 예시 HTML (사용자가 제공한 테이블 구조)
    test_html = '''
    <div class="item column">
        <h3 class="page_sub_title row">
            물량 점수관리
        </h3>
        <div class="sla_item column">
            <div class="table_area table_responsive">
                <table class="table sla_table" data-type="partner">
                    <thead>
                        <tr>
                            <th>번호</th>
                            <th>날짜</th>
                            <th>일별 물량 점수</th>
                            <th>아침점심피크</th>
                            <th>오후논피크</th>
                            <th>저녁피크</th>
                            <th>심야논피크</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr class="highlight">
                            <td>5</td>
                            <td>2025-06-15</td>
                            <td class="highlight">5점</td>
                            <td>
                                94/33건
                                <span class="status_score on">(+3점)</span>
                            </td>
                            <td>
                                30/22건
                                <span class="status_score on">(+2점)</span>
                            </td>
                            <td>
                                0/35건
                                <span class="status_score ">(0점)</span>
                            </td>
                            <td>
                                0/30건
                                <span class="status_score ">(0점)</span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    '''
    
    print("=== 테이블 파싱 테스트 ===")
    print(f"현재 미션 날짜: {get_mission_date()}")
    
    # 테스트를 위해 강제로 2025-06-15로 설정
    original_get_mission_date = globals()['get_mission_date']
    globals()['get_mission_date'] = lambda: '2025-06-15'
    
    try:
        result = parse_mission_table_data(test_html)
        if result:
            print("파싱 성공!")
            for peak, data in result.items():
                print(f"  {peak}: {data['current']}/{data['target']}건")
        else:
            print("파싱 실패")
    finally:
        # 원래 함수 복원
        globals()['get_mission_date'] = original_get_mission_date
    
    print("========================")

if __name__ == '__main__':
    # 명령행 인수 확인
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            # 테스트 모드
            test_table_parsing()
            exit()
        elif sys.argv[1] == 'kakao':
            # 카카오 오픈빌더 웹훅 서버 실행
            run_kakao_webhook_server()
            exit()
        elif sys.argv[1] == 'telegram':
            # 기존 텔레그램 모니터링 실행
            main()
            exit()
    
    # 프로그램 시작 시 현재 시각 확인
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M")
    current_hour = now.hour
    mission_date = get_mission_date()
    
    print(f'서비스 시작 시각: {current_time}')
    print(f'현재 미션 날짜: {mission_date}')
    
    # 시작하자마자 한 번 실행 (알림 시간대일 경우에만)
    # 알림 시간: 10:00~00:00 (자정까지만)
    is_service_time = 10 <= current_hour <= 23
    
    if is_service_time:
        print('현재 시각이 알림 시간대입니다. 즉시 첫 실행을 시작합니다.')
        job()
    elif 0 <= current_hour < 6:
        print('현재 시각이 라이더 휴식 시간(00:00~06:00)입니다. 10:00부터 알림을 시작합니다.')
    elif 6 <= current_hour < 10:
        print('현재 시각이 미션 진행 중이지만 알림 시간 이전(06:00~10:00)입니다. 10:00부터 알림을 시작합니다.')
    
    # 스케줄러 시작
    main()

# 한글 폰트 테스트 (필요시)
# plt.plot([1,2,3], [1,2,3])
# plt.title('한글 테스트')
# plt.show() 

def get_ansan_weather():
    # 1순위: 기상청 API 사용
    kma_service = KMAWeatherService()
    kma_weather = kma_service.get_weather_summary()
    
    if kma_weather and "⚠️" not in kma_weather:
        return kma_weather
    
    # 2순위: OpenWeatherMap API 사용 (백업)
    weather_service = WeatherService()
    return weather_service.get_weather_summary()