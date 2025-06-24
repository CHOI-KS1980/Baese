#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
장부 모니터링 시스템 (최적화 버전)
- 중복 코드 제거
- 성능 최적화  
- 코드 간결화
"""

import os
import time
import schedule
import logging
import datetime
import json
import re
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor

# 외부 라이브러리
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import numpy as np
from flask import Flask, request, jsonify
import threading

# ========== 설정 및 상수 ==========

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 환경변수 로드
load_dotenv()
USER_ID = 'DP2406035262'
USER_PW = 'wldud050323!'
LOGIN_URL = 'https://jangboo.grider.ai/'
MISSION_DATA_CACHE_FILE = 'mission_data_cache.json'

# 그래프 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# 메시지 전송 설정
MESSAGE_CONFIGS = {
    'telegram': {
        'token': os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN'),
        'chat_id': os.getenv('TELEGRAM_CHAT_ID', 'YOUR_CHAT_ID')
    },
    'slack': {
        'webhook_url': os.getenv('SLACK_WEBHOOK_URL', 'YOUR_SLACK_WEBHOOK_URL')
    },
    'discord': {
        'webhook_url': os.getenv('DISCORD_WEBHOOK_URL', 'YOUR_DISCORD_WEBHOOK_URL')
    },
    'kakao': {
        'webhook_url': os.getenv('KAKAO_OPENBUILDER_URL', 'YOUR_KAKAO_OPENBUILDER_WEBHOOK_URL')
    }
}

# 피크 시간대 매핑 (통일된 용어)
PEAK_NAMES = {
    'web': ['아침점심피크', '오후논피크', '저녁피크', '심야논피크'],
    'legacy': ['오전피크', '오후피크', '저녁피크', '심야피크']
}

# 피크시간 정의 (한국시간 기준)
PEAK_TIMES = {
    '아침점심피크': {'start': 7, 'end': 13},    # 07:00-13:00
    '오후논피크': {'start': 13, 'end': 17},     # 13:00-17:00  
    '저녁피크': {'start': 17, 'end': 21},       # 17:00-21:00
    '심야논피크': {'start': 21, 'end': 7}       # 21:00-07:00 (다음날)
}

# ========== 유틸리티 함수들 ==========

def get_korean_time():
    """한국시간 반환"""
    try:
        import pytz
        kst = pytz.timezone('Asia/Seoul')
        return datetime.datetime.now(kst)
    except ImportError:
        # pytz가 없으면 UTC+9로 계산
        utc_now = datetime.datetime.utcnow()
        kst_now = utc_now + datetime.timedelta(hours=9)
        return kst_now

def get_mission_date() -> str:
    """미션 기준 날짜 계산 (03:00~다음날 02:59를 하나의 미션 날짜로 간주)"""
    now = get_korean_time()
    if now.time() < datetime.time(3, 0):
        mission_date = now.date() - datetime.timedelta(days=1)
    else:
        mission_date = now.date()
    logger.info(f"🎯 미션 날짜 계산: 현재시간 {now.strftime('%Y-%m-%d %H:%M')} → 미션날짜 {mission_date}")
    return mission_date.strftime('%Y-%m-%d')

def is_peak_time() -> bool:
    """현재가 피크시간인지 확인"""
    now = get_korean_time()
    current_hour = now.hour
    
    for peak_name, time_range in PEAK_TIMES.items():
        start_hour = time_range['start']
        end_hour = time_range['end']
        
        if start_hour <= end_hour:
            # 일반적인 시간대 (예: 07:00-13:00)
            if start_hour <= current_hour < end_hour:
                return True
        else:
            # 심야시간대 (예: 21:00-07:00)
            if current_hour >= start_hour or current_hour < end_hour:
                return True
    
    return False

def get_current_peak_name() -> str:
    """현재 피크시간 이름 반환"""
    now = get_korean_time()
    current_hour = now.hour
    
    for peak_name, time_range in PEAK_TIMES.items():
        start_hour = time_range['start']
        end_hour = time_range['end']
        
        if start_hour <= end_hour:
            if start_hour <= current_hour < end_hour:
                return peak_name
        else:
            if current_hour >= start_hour or current_hour < end_hour:
                return peak_name
    
    return "일반시간"

def safe_file_operation(operation, *args, **kwargs):
    """안전한 파일 작업 래퍼"""
    try:
        return operation(*args, **kwargs)
    except Exception as e:
        logger.error(f"파일 작업 실패: {e}")
        return None

def create_chrome_options() -> Options:
    """최적화된 Chrome 옵션 생성"""
    options = Options()
    chrome_args = [
        '--headless', '--no-sandbox', '--disable-dev-shm-usage',
        '--disable-gpu', '--disable-images', '--memory-pressure-off',
        '--max_old_space_size=4096', '--disable-web-security',
        '--disable-features=VizDisplayCompositor', '--disable-extensions',
        '--no-first-run', '--ignore-certificate-errors', '--ignore-ssl-errors',
        '--ignore-certificate-errors-spki-list',
        '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ]
    
    for arg in chrome_args:
        options.add_argument(arg)
    
    return options

# ========== 캐시 시스템 ==========

def save_mission_data_cache(mission_date: str, peak_data: dict) -> bool:
    """미션 데이터 캐시 저장"""
    cache_data = {
        'date': mission_date,
        'timestamp': datetime.datetime.now().isoformat(),
        'peak_data': peak_data
    }
    
    def _save():
        with open(MISSION_DATA_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        return True
    
    result = safe_file_operation(_save)
    if result:
        logger.info(f"✅ 미션 데이터 캐시 저장 완료: {mission_date}")
    return result is not None

def load_mission_data_cache() -> Optional[dict]:
    """캐시된 미션 데이터 로드"""
    if not os.path.exists(MISSION_DATA_CACHE_FILE):
        logger.info("📂 미션 데이터 캐시 파일이 없습니다.")
        return None
    
    def _load():
        with open(MISSION_DATA_CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    cache_data = safe_file_operation(_load)
    if not cache_data:
        return None
    
    cached_date = cache_data.get('date')
    current_mission_date = get_mission_date()
    
    if cached_date == current_mission_date:
        logger.info(f"✅ 캐시된 미션 데이터 사용: {cached_date}")
        return cache_data.get('peak_data')
    else:
        logger.info(f"🔄 날짜 변경 감지: {cached_date} → {current_mission_date}")
        return None

def is_mission_data_fresh() -> bool:
    """미션 데이터 freshness 확인"""
    cache_data = load_mission_data_cache()
    return cache_data is not None

# ========== 데이터 파싱 ==========

class DataParser:
    """데이터 파싱을 위한 클래스"""
    
    def __init__(self):
        self.int_pattern = re.compile(r'[\d,]+')
        self.float_pattern = re.compile(r'(\d+(?:\.\d+)?)')
        self.count_pattern = re.compile(r'(\d+)/(\d+)')
        self.date_pattern = None
    
    def parse_int(self, soup, selector: str, default: int = 0) -> int:
        """최적화된 정수 파싱"""
        node = soup.select_one(selector)
        if node:
            match = self.int_pattern.search(node.get_text(strip=True))
            if match:
                number_str = match.group().replace(',', '')
                return int(number_str) if number_str.isdigit() else default
        return default
    
    def parse_float(self, soup, selector: str, default: float = 0.0) -> float:
        """최적화된 실수 파싱"""
        node = soup.select_one(selector)
        if node:
            match = self.float_pattern.search(node.get_text(strip=True))
            return float(match.group(1)) if match else default
        return default
    
    def parse_mission_cell(self, cell_text: str) -> tuple:
        """미션 셀 파싱 (current/target)"""
        match = self.count_pattern.search(cell_text)
        if match:
            return int(match.group(1)), int(match.group(2))
        return 0, 0
    
    def find_mission_table(self, soup) -> Optional[object]:
        """미션 테이블 찾기"""
        selectors = [
            'table.sla_table[data-type="partner"]',
            'table.sla_table', 'table[data-type="partner"]',
            '.sla_table', 'table[id*="sla"]', 'table[class*="sla"]',
            '.mission_table', '.quantity_table'
        ]
        
        # CSS 선택자로 찾기
        for selector in selectors:
            try:
                table = soup.select_one(selector)
                if table:
                    logger.info(f"✅ 테이블 발견 (선택자: {selector})")
                    return table
            except:
                continue
        
        # 텍스트 기반 검색
        tables = soup.find_all('table')
        keywords = ['물량 점수관리', '아침점심피크', '오후논피크', '저녁피크', '심야논피크']
        for table in tables:
            if any(keyword in table.get_text() for keyword in keywords):
                logger.info("✅ 테이블 발견 (텍스트 기반 검색)")
                return table
        
        return None
    
    def parse_mission_table_data(self, html: str) -> Optional[dict]:
        """미션 테이블 데이터 파싱"""
        soup = BeautifulSoup(html, 'html.parser')
        target_date = get_mission_date()
        self.date_pattern = re.compile(target_date)
        
        # 테이블 찾기
        sla_table = self.find_mission_table(soup)
        if not sla_table:
            logger.warning("물량 점수관리 테이블을 찾을 수 없습니다.")
            return None
        
        # 행 찾기
        rows = sla_table.select('tbody tr') or sla_table.select('tr')
        target_row = None
        
        for row in rows:
            cells = row.select('td')
            for idx in range(min(3, len(cells))):
                if self.date_pattern.search(cells[idx].get_text(strip=True)):
                    target_row = row
                    break
            if target_row:
                break
        
        if not target_row:
            logger.warning(f"날짜 {target_date}에 해당하는 데이터를 찾을 수 없습니다.")
            return None
        
        # 데이터 파싱
        cells = target_row.select('td')
        if len(cells) < 4:
            logger.warning("테이블 구조가 예상과 다릅니다.")
            return None
        
        # 피크 데이터 시작 인덱스 찾기
        peak_start_idx = 1
        for idx, cell in enumerate(cells):
            if self.date_pattern.search(cell.get_text(strip=True)):
                peak_start_idx = idx + 1
                break
        
        # 피크 데이터 파싱
        peak_data = {}
        peak_cells = cells[peak_start_idx:peak_start_idx + 4]
        
        for idx, cell in enumerate(peak_cells):
            if idx >= len(PEAK_NAMES['web']):
                break
            
            text = cell.get_text(strip=True)
            current, target = self.parse_mission_cell(text)
            
            # 통일된 용어로 저장
            web_name = PEAK_NAMES['web'][idx]
            legacy_name = PEAK_NAMES['legacy'][idx]
            
            peak_info = {
                'current': current,
                'target': target,
                'progress': (current / target * 100) if target > 0 else 0
            }
            
            peak_data[web_name] = peak_info
            if web_name != legacy_name:  # 중복 방지
                peak_data[legacy_name] = peak_info
        
        logger.info(f"파싱된 미션 데이터 ({target_date}): {len(PEAK_NAMES['web'])}개 피크")
        return peak_data

# ========== 크롤링 시스템 ==========

def crawl_jangboo(max_retries: int = 3, retry_delay: int = 5) -> Optional[str]:
    """최적화된 크롤링 함수"""
    start_time = time.time()
    
    for attempt in range(max_retries):
        driver = None
        try:
            logger.info(f"크롤링 시도 {attempt + 1}/{max_retries}")
            
            driver = webdriver.Chrome(options=create_chrome_options())
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            
            # 로그인 페이지 접속
            logger.info(f"로그인 페이지 접속: {LOGIN_URL}")
            driver.get(LOGIN_URL)
            time.sleep(2)
            
            # 페이지 확인
            if "jangboo" not in driver.current_url.lower():
                raise Exception(f"예상과 다른 페이지 로드: {driver.current_url}")
            
            # 로그인 처리
            logger.info("로그인 시도")
            id_field = driver.find_element(By.ID, 'id')
            pw_field = driver.find_element(By.ID, 'password')
            login_btn = driver.find_element(By.ID, 'loginBtn')
            
            id_field.clear()
            id_field.send_keys(USER_ID)
            pw_field.clear()
            pw_field.send_keys(USER_PW)
            login_btn.click()
            time.sleep(3)
            
            # HTML 추출
            html = driver.page_source
            if len(html) < 1000:
                raise Exception("HTML 길이가 너무 짧습니다.")
            
            logger.info(f"✅ 크롤링 성공 (시도: {attempt + 1}, 소요시간: {time.time() - start_time:.2f}초)")
            return html
            
        except Exception as e:
            logger.error(f"❌ 크롤링 시도 {attempt + 1} 실패: {e}")
            
            if attempt < max_retries - 1:
                logger.info(f"⏳ {retry_delay}초 후 재시도...")
                time.sleep(retry_delay)
            else:
                logger.error(f"❌ 모든 크롤링 시도 실패")
        
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    return None

def parse_data(html: str) -> dict:
    """데이터 파싱 메인 함수"""
    start_time = time.time()
    soup = BeautifulSoup(html, 'html.parser')
    parser = DataParser()
    
    # 기본 점수 정보 파싱
    selectors = {
        'total_score': '.score_total_value[data-text="total"]',
        'quantity_score': '.detail_score_value[data-text="quantity"]',
        'acceptance_score': '.detail_score_value[data-text="acceptance"]',
        'total_complete': '.etc_value[data-etc="complete"] span',
        'total_reject': '.etc_value[data-etc="reject"] span',
        'acceptance_rate_total': '.etc_value[data-etc="acceptance"] span'
    }
    
    parsed_data = {}
    for key, selector in selectors.items():
        if key == 'acceptance_rate_total':
            parsed_data[key] = parser.parse_float(soup, selector)
        else:
            parsed_data[key] = parser.parse_int(soup, selector)
    
    # 미션 데이터 파싱 (캐시 활용)
    logger.info("=== 미션 데이터 파싱 시작 ===")
    cached_peak_data = load_mission_data_cache()
    
    if cached_peak_data:
        logger.info("✅ 캐시된 미션 데이터를 사용합니다.")
        peak_data = cached_peak_data
    else:
        logger.info("🔍 새로운 미션 데이터를 크롤링하여 파싱합니다.")
        peak_data = parser.parse_mission_table_data(html)
        
        if peak_data:
            save_mission_data_cache(get_mission_date(), peak_data)
        else:
            # Fallback: quantity_item 방식으로 파싱 시도
            peak_data = fallback_parse_mission_data(soup, parser)
    
    # 최종 데이터 구성
    parsed_data['peak_data'] = peak_data or create_default_peak_data()
    parsed_data['riders'] = parse_rider_data(soup, parser)
    
    logger.info(f"파싱 완료 (소요시간: {time.time() - start_time:.2f}초)")
    return parsed_data

def fallback_parse_mission_data(soup, parser) -> dict:
    """Fallback 미션 데이터 파싱"""
    logger.warning("⚠️ 1단계 파싱 실패! 2단계 fallback 시도")
    
    peak_data = {}
    quantity_items = soup.select('.quantity_item')
    
    if quantity_items:
        for idx, item in enumerate(quantity_items):
            if idx >= len(PEAK_NAMES['web']):
                break
            
            try:
                current_node = item.select_one('.performance_value')
                target_node = item.select_one('.number_value span:not(.performance_value)')
                
                current = 0
                if current_node:
                    current_text = current_node.get_text(strip=True)
                    match = parser.int_pattern.search(current_text)
                    current = int(match.group()) if match else 0
                
                target = 0
                if target_node:
                    target_text = target_node.get_text(strip=True)
                    match = parser.int_pattern.search(target_text)
                    target = int(match.group()) if match else 0
                
                web_name = PEAK_NAMES['web'][idx]
                legacy_name = PEAK_NAMES['legacy'][idx]
                
                peak_info = {
                    'current': current,
                    'target': target,
                    'progress': (current / target * 100) if target > 0 else 0
                }
                
                peak_data[web_name] = peak_info
                if web_name != legacy_name:
                    peak_data[legacy_name] = peak_info
                
                logger.info(f"  2단계 파싱: {web_name} = {current}/{target}건")
                
            except Exception as e:
                logger.warning(f"아이템 {idx} 파싱 실패: {e}")
    
    return peak_data

def create_default_peak_data() -> dict:
    """기본 피크 데이터 구조 생성"""
    logger.warning("⚠️ 기본 구조 적용 (크롤링 시 업데이트 필요)")
    
    peak_data = {}
    default_info = {'current': 0, 'target': 0, 'progress': 0}
    
    for web_name, legacy_name in zip(PEAK_NAMES['web'], PEAK_NAMES['legacy']):
        peak_data[web_name] = default_info.copy()
        if web_name != legacy_name:
            peak_data[legacy_name] = default_info.copy()
    
    return peak_data

def parse_rider_data(soup, parser) -> list:
    """라이더 데이터 파싱"""
    riders = []
    rider_items = soup.select('.rider_item, .user_item')
    
    for item in rider_items:
        try:
            name_node = item.select_one('.rider_name, .user_name')
            complete_node = item.select_one('.complete_count')
            
            if name_node and complete_node:
                name = name_node.get_text(strip=True)
                # "이름" 텍스트 제거
                name = re.sub(r'이름', '', name).strip()
                complete_text = complete_node.get_text(strip=True)
                complete_match = parser.int_pattern.search(complete_text)
                complete = int(complete_match.group()) if complete_match else 0
                
                if complete > 0:  # 실적이 있는 라이더만 포함
                    riders.append({
                        'name': name,
                        'complete': complete,
                        'contribution': 0  # 나중에 계산
                    })
        except Exception as e:
            logger.warning(f"라이더 데이터 파싱 실패: {e}")
    
    # 기여도 계산
    total_complete = sum(rider['complete'] for rider in riders)
    if total_complete > 0:
        for rider in riders:
            rider['contribution'] = round(rider['complete'] / total_complete * 100, 1)
    
    return sorted(riders, key=lambda x: x['complete'], reverse=True)

# ========== 메시지 시스템 ==========

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
            logger.info("✅ 텔레그램 메시지 전송 성공")
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
            logger.info("✅ 슬랙 메시지 전송 성공")
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
            logger.info("✅ 디스코드 메시지 전송 성공")
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
            logger.info("✅ 카카오 오픈빌더 메시지 전송 성공")
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

# ========== 메시지 생성 ==========

def get_active_peaks(peak_data: dict) -> list:
    """활성 피크 시간대 확인"""
    now = datetime.datetime.now()
    current_hour = now.hour
    
    # 시간대별 피크 매핑
    time_peak_map = {
        (6, 11): ['아침점심피크', '오전피크'],
        (12, 17): ['오후논피크', '오후피크'],
        (18, 21): ['저녁피크'],
        (22, 5): ['심야논피크', '심야피크']  # 22시~다음날 5시
    }
    
    active_peaks = []
    for (start, end), peak_names in time_peak_map.items():
        if start <= end:
            is_active = start <= current_hour <= end
        else:  # 자정을 넘는 경우
            is_active = current_hour >= start or current_hour <= end
        
        if is_active:
            for peak_name in peak_names:
                if peak_name in peak_data:
                    active_peaks.append(peak_name)
                    break  # 첫 번째로 찾은 피크만 사용
    
    return active_peaks

def make_message(data: dict) -> str:
    """최적화된 메시지 생성"""
    peak_data = data.get('peak_data', {})
    riders = data.get('riders', [])
    total_score = data.get('total_score', 0)
    
    # 헤더
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    mission_date = get_mission_date()
    
    # 활성 피크 확인
    active_peaks = get_active_peaks(peak_data)
    
    # 미션 현황
    mission_status = []
    lacking_missions = []
    
    for peak_name in PEAK_NAMES['web']:
        if peak_name in peak_data:
            peak_info = peak_data[peak_name]
            current = peak_info['current']
            target = peak_info['target']
            progress = peak_info.get('progress', 0)
            
            status_emoji = "🔥" if peak_name in active_peaks else "⏳"
            if current >= target:
                status_emoji = "✅"
            elif progress < 50:
                status_emoji = "⚠️"
                lacking_missions.append(peak_name)
            
            mission_status.append(f"{status_emoji} {peak_name}: {current}/{target}건 ({progress:.1f}%)")
    
    # 라이더 현황 (상위 5명)
    rider_status = []
    for i, rider in enumerate(riders[:5]):
        rank_emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i] if i < 5 else f"{i+1}."
        rider_status.append(f"{rank_emoji} {rider['name']}: {rider['complete']}건 ({rider['contribution']}%)")
    
    # 메시지 조합
    separator = "\n" + "─" * 30 + "\n"
    
    msg_parts = [
        f"📊 **미션 현황 리포트**",
        f"🕐 {current_time} | 📅 {mission_date}",
        f"🎯 총점: {total_score:,}점",
        separator,
        "📈 **미션 현황**",
        "\n".join(mission_status),
        separator,
        "👥 **라이더 현황** (TOP 5)",
        "\n".join(rider_status) if rider_status else "데이터 없음"
    ]
    
    if lacking_missions:
        msg_parts.extend([separator, f"⚠️ **미션 부족**: {', '.join(lacking_missions)}"])
    
    return "\n".join(msg_parts)

# ========== 그래프 생성 ==========

def draw_peak_graph(data: dict, save_path: str = 'mission_graph.png'):
    """피크 그래프 생성"""
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

# ========== 메인 실행 함수들 ==========

def job():
    """메인 작업 함수"""
    try:
        logger.info("🔄 작업 시작")
        
        if not is_mission_data_fresh():
            logger.info("🆕 미션 데이터가 오래되었거나 없습니다. 새로 크롤링합니다.")
        
        html = crawl_jangboo()
        
        if html:
            logger.info("✅ 크롤링 성공, 데이터 파싱 시작")
            data = parse_data(html)
            
            # 그래프 생성
            try:
                draw_peak_graph(data)
                logger.info("📊 그래프 생성 완료")
            except Exception as graph_error:
                logger.warning(f"⚠️ 그래프 생성 실패 (계속 진행): {graph_error}")
            
            # 메시지 전송
            try:
                msg = make_message(data)
                send_message(msg)
                logger.info("✅ 메시지 전송 완료")
            except Exception as msg_error:
                logger.warning(f"⚠️ 메시지 전송 실패: {msg_error}")
            
            logger.info("✅ 작업 완료")
            
        else:
            # 캐시된 데이터 활용
            cached_data = load_mission_data_cache()
            if cached_data:
                logger.info("📦 캐시된 데이터로 제한적 서비스 제공")
                fallback_data = {'peak_data': cached_data, 'total_score': 0, 'riders': []}
                cached_msg = f"⚠️ 연결 문제로 캐시 데이터 사용\n\n{make_message(fallback_data)}\n\n📝 참고: 실시간 점수/라이더 정보는 연결 복구 후 업데이트됩니다."
                send_message(cached_msg)
            else:
                logger.warning("⚠️ 캐시된 데이터도 없습니다. 연결 복구 대기 중...")
                
    except Exception as e:
        logger.error(f"❌ 작업 중 예상치 못한 오류 발생: {e}")
        
        # 네트워크 상태 체크
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            logger.info("✅ 기본 인터넷 연결은 정상입니다")
        except:
            logger.error("❌ 기본 인터넷 연결도 실패. 네트워크 설정을 확인하세요")

def setup_smart_schedule():
    """스마트 스케줄링 설정 (한국시간 기준)"""
    logger.info("📅 스마트 스케줄링 설정 시작")
    
    # 기본 30분 간격 스케줄 (10:00-00:00)
    for hour in range(10, 24):  # 10시부터 23시까지
        for minute in [0, 30]:  # 0분, 30분
            schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(job)
    
    # 자정 실행 (00:00)
    schedule.every().day.at("00:00").do(job)
    
    # 피크시간 15분 간격 추가 스케줄
    peak_hours = {
        '아침점심피크': range(7, 13),   # 07:00-12:59
        '오후논피크': range(13, 17),    # 13:00-16:59
        '저녁피크': range(17, 21),      # 17:00-20:59
        '심야논피크': list(range(21, 24)) + list(range(0, 7))  # 21:00-06:59
    }
    
    for peak_name, hours in peak_hours.items():
        for hour in hours:
            for minute in [15, 45]:  # 15분, 45분
                if hour == 0 and minute == 45:  # 00:45는 이미 30분 간격에 포함
                    continue
                schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(job)
    
    logger.info("✅ 스케줄링 설정 완료")
    logger.info(f"   • 기본 간격: 30분 (10:00-00:00)")
    logger.info(f"   • 피크시간 추가: 15분 간격")
    logger.info(f"   • 현재 피크시간: {get_current_peak_name()}")

def is_message_time() -> bool:
    """메시지 전송 시간대(00:00~02:59, 10:00~23:59)인지 확인"""
    now = get_korean_time()
    t = now.time()
    return (datetime.time(0, 0) <= t < datetime.time(3, 0)) or (datetime.time(10, 0) <= t <= datetime.time(23, 59, 59))

def main():
    print("🚀 장부 모니터링 시스템 시작 (최적화 버전)")
    print("=" * 50)
    kst_now = get_korean_time()
    current_mission_date = get_mission_date()
    print("📊 현재 설정:")
    print(f"   • 미션 데이터 기준: 03:00~다음날 02:59")
    print(f"   • 알림 시간: 00:00~02:59, 10:00~23:59")
    print(f"   • 모니터링 간격: 30분 (피크시간 15분 추가)")
    print(f"🎯 현재 미션 날짜: {current_mission_date}")
    print(f"⏰ 현재 시각: {kst_now.strftime('%Y-%m-%d %H:%M:%S')} (KST)")
    print(f"📈 현재 피크시간: {get_current_peak_name()}")
    if is_message_time():
        print("✅ 메시지 전송 시간대입니다. 즉시 첫 모니터링을 시작합니다.")
        try:
            job()
        except Exception as e:
            logger.error(f"초기 실행 실패: {e}")
    else:
        print("💤 현재 휴식 시간대입니다. 10:00부터 알림을 시작합니다.")
    setup_smart_schedule()
    print("\n🔄 스케줄러가 시작되었습니다.")
    print("   • 중지하려면 Ctrl+C를 누르세요")
    try:
        while True:
            kst_now = get_korean_time()
            if is_message_time():
                schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n\n⏹️ 모니터링이 중지되었습니다. 감사합니다! 🙏")

# ========== 카카오 웹훅 서버 (간소화) ==========

class KakaoOpenBuilderServer:
    """카카오 오픈빌더 웹훅 서버 (간소화 버전)"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.route('/webhook', methods=['POST'])
        def webhook():
            try:
                req_data = request.get_json()
                user_msg = req_data.get('userRequest', {}).get('utterance', '')
                
                if '현황' in user_msg or '상태' in user_msg:
                    # 캐시된 데이터로 응답
                    cached_data = load_mission_data_cache()
                    if cached_data:
                        data = {'peak_data': cached_data, 'total_score': 0, 'riders': []}
                        message = make_message(data)
                    else:
                        message = "현재 미션 데이터를 불러올 수 없습니다. 잠시 후 다시 시도해주세요."
                    
                    return jsonify({
                        "version": "2.0",
                        "template": {"outputs": [{"simpleText": {"text": message}}]}
                    })
                else:
                    return jsonify({
                        "version": "2.0",
                        "template": {"outputs": [{"simpleText": {"text": "안녕하세요! '현황'이라고 말씀해주시면 미션 현황을 알려드립니다."}}]}
                    })
            except Exception as e:
                logger.error(f"웹훅 처리 오류: {e}")
                return jsonify({"error": "처리 중 오류가 발생했습니다."}), 500
        
        @self.app.route('/health', methods=['GET'])
        def health():
            return {"status": "healthy", "timestamp": datetime.datetime.now().isoformat()}
    
    def start_server(self, port: int = 5000):
        self.app.run(host='0.0.0.0', port=port, debug=False)

def run_kakao_webhook_server():
    """카카오 웹훅 서버 실행"""
    server = KakaoOpenBuilderServer()
    print("🌐 카카오 오픈빌더 웹훅 서버 시작 (포트: 5000)")
    server.start_server()

# ========== 실행 부분 ==========

if __name__ == "__main__":
    main() 