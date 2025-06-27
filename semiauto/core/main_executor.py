#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 최종 검증된 솔루션: 카카오톡 나에게 보내기 + 수동 복사
- 웹 크롤링  데이터 가공 (자동)
- 카카오톡 나에게 보내기 (자동)
- 클립보드 자동 복사 (자동)
- 오픈채팅방 복사/붙여넣기 (수동 5초)
"""

import requests
import json
import time
from datetime import datetime, timedelta
# pyperclip은 조건부 import (GitHub Actions 환경에서는 사용 불가)
import logging
import os
import re
import pytz  # 한국시간 설정을 위해 추가
from bs4 import BeautifulSoup, Tag
from xml.etree import ElementTree as ET  # 한국천문연구원 API용

# Selenium 명시적 대기를 위한 모듈 추가
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# selenium 등 동적으로 import 되는 모듈에 대한 Linter 경고 무시
# pyright: reportMissingImports=false

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('grider_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 한국시간 설정
KST = pytz.timezone('Asia/Seoul')

def get_korea_time():
    """한국시간 기준 현재 시간 반환"""
    return datetime.now(KST)

class KoreaHolidayChecker:
    """한국천문연구원 공휴일 체커"""
    
    def __init__(self):
        # 한국천문연구원 특일 정보 API
        self.api_key = os.getenv('KOREA_HOLIDAY_API_KEY')
        self.base_url = "http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService"
        self.holidays_cache = {}
        
        if self.api_key:
            logger.info(" 한국천문연구원 특일 정보 API 공휴일 체커 초기화")
            self.load_year_holidays(datetime.now(KST).year)
        else:
            logger.info(" KOREA_HOLIDAY_API_KEY 환경변수가 설정되지 않음 - 기본 공휴일 사용")
    
    def get_holidays_from_api(self, year, month=None):
        """API에서 공휴일 정보 가져오기"""
        if not self.api_key:
            return []
        
        url = f"{self.base_url}/getRestDeInfo"
        
        params = {
            'serviceKey': self.api_key,
            'pageNo': '1',
            'numOfRows': '50',
            'solYear': str(year)
        }
        
        if month:
            params['solMonth'] = f"{month:02d}"
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                
                holidays = []
                items = root.findall('.//item')
                
                for item in items:
                    date_name_node = item.find('dateName')
                    loc_date_node = item.find('locdate')
                    is_holiday_node = item.find('isHoliday')
                    
                    if date_name_node is not None and loc_date_node is not None and date_name_node.text and loc_date_node.text:
                        holiday_name = date_name_node.text
                        holiday_date = loc_date_node.text
                        holiday_status = is_holiday_node.text if is_holiday_node is not None and is_holiday_node.text else 'Y'
                        
                        if holiday_date and len(holiday_date) == 8:
                            formatted_date = f"{holiday_date[:4]}-{holiday_date[4:6]}-{holiday_date[6:8]}"
                            holidays.append({
                                'date': formatted_date,
                                'name': holiday_name,
                                'is_holiday': holiday_status == 'Y'
                            })
                            logger.info(f" 공휴일 확인: {formatted_date} - {holiday_name}")
                
                return holidays
                
        except Exception as e:
            logger.error(f" 공휴일 API 오류: {e}")
        
        return []
    
    def load_year_holidays(self, year):
        """전체 년도 공휴일 로드"""
        if year in self.holidays_cache:
            return
        
        holidays = []
        for month in range(1, 13):
            month_holidays = self.get_holidays_from_api(year, month)
            holidays.extend(month_holidays)
        
        self.holidays_cache[year] = holidays
        logger.info(f" {year}년 전체월 공휴일 {len(holidays)}개 로드 완료")
    
    def is_holiday_advanced(self, target_date):
        """고급 공휴일 판정"""
        if isinstance(target_date, str):
            target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        elif isinstance(target_date, datetime):
            target_date = target_date.date()
        
        year = target_date.year
        if year not in self.holidays_cache:
            self.load_year_holidays(year)
        
        target_str = target_date.strftime('%Y-%m-%d')
        
        holidays = self.holidays_cache.get(year, [])
        for holiday in holidays:
            if holiday['date'] == target_str:
                return True, holiday.get('name')
        
        return False, None

# 전역 공휴일 체커 (한 번만 초기화)
holiday_checker = KoreaHolidayChecker()

class TokenManager:
    """카카오톡 토큰 관리 클래스"""
    
    def __init__(self, rest_api_key, refresh_token):
        self.rest_api_key = rest_api_key
        self.refresh_token = refresh_token
        self.access_token = None
        self.token_expires_at = None
        
        logger.info(" TokenManager 초기화 - 토큰 갱신 시도")
        if not self.refresh_access_token():
            logger.error(" 초기 토큰 갱신 실패")
    
    def refresh_access_token(self):
        """액세스 토큰 갱신"""
        url = "https://kauth.kakao.com/oauth/token"
        data = {
            'grant_type': 'refresh_token',
            'client_id': self.rest_api_key,
            'refresh_token': self.refresh_token
        }
        
        try:
            response = requests.post(url, data=data)
            result = response.json()
            
            if 'access_token' in result:
                self.access_token = result['access_token']
                expires_in = result.get('expires_in', 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                if 'refresh_token' in result:
                    self.refresh_token = result['refresh_token']
                
                self.save_tokens()
                
                logger.info(f" 토큰 갱신 완료: {self.access_token[:20]}...")
                return True
            else:
                logger.error(f" 토큰 갱신 실패: {result}")
                return False
                
        except Exception as e:
            logger.error(f" 토큰 갱신 중 오류: {e}")
            return False
    
    def get_valid_token(self):
        """유효한 액세스 토큰 반환 (필요시 자동 갱신)"""
        if not self.access_token or self.is_token_expired():
            logger.info(" 토큰 갱신 시도...")
            if not self.refresh_access_token():
                logger.error(" 토큰 갱신 실패 - None 반환")
                return None
        
        logger.info(f" 유효한 토큰 반환: {self.access_token[:20] if self.access_token else 'None'}...")
        return self.access_token
    
    def is_token_expired(self):
        """토큰 만료 여부 확인"""
        if not self.token_expires_at:
            return True
        return datetime.now() >= (self.token_expires_at - timedelta(minutes=30))
    
    def save_tokens(self):
        """토큰을 파일에 저장"""
        try:
            with open('kakao_tokens.txt', 'w') as f:
                f.write(f"ACCESS_TOKEN={self.access_token}\n")
                f.write(f"REFRESH_TOKEN={self.refresh_token}\n")
                if self.token_expires_at:
                    f.write(f"EXPIRES_AT={self.token_expires_at.isoformat()}\n")
        except Exception as e:
            logger.error(f" 토큰 저장 실패: {e}")

class KakaoSender:
    """카카오톡 메시지 전송 클래스"""
    
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    
    def send_text_message(self, text, link_url=None):
        """텍스트 메시지 전송"""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
        
        template_object = {
            "object_type": "text",
            "text": text,
            "link": {
                "web_url": "https://www.google.com"
            }
        }
        
        data = {
            'template_object': json.dumps(template_object, ensure_ascii=False)
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, data=data)
            return response.json()
        except Exception as e:
            logger.error(f" 메시지 전송 중 오류: {e}")
            return {"error": str(e)}

class GriderDataCollector:
    """심플 배민 플러스 데이터 수집 클래스"""
    
    def __init__(self):
        self.base_url = "https://grider.co.kr"
        self.mission_data_cache_file = 'mission_data_cache.json'
    
    def get_grider_data(self, use_sample=False):
        """G라이더 주간/일간 데이터를 모두 수집"""
        if use_sample:
            return self._get_error_data("샘플 데이터 사용")

        logger.info(" G라이더 실제 데이터 수집 시작...")
        
        driver = None
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.chrome.options import Options
            
            options = Options()
            chrome_args = [
                '--headless=new', '--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', 
                '--disable-images', '--disable-web-security', '--disable-extensions',
                '--ignore-certificate-errors', '--disable-blink-features=AutomationControlled',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                '--window-size=1920,1080'
            ]
            for arg in chrome_args:
                options.add_argument(arg)
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            driver = webdriver.Chrome(options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.set_page_load_timeout(60)

            if not self._perform_login(driver):
                raise Exception("G라이더 로그인 실패")
            
            # 1. 로그인 후 자동으로 이동된 대시보드에서 바로 일간 데이터 수집
            logger.info("로그인 성공 후 대시보드에서 일간 데이터 수집 시도...")
            daily_wait_xpath = "//div[contains(@class, 'rider_container')]"
            daily_sub_wait_xpath = ".//div[contains(@class, 'rider_item')]" # 첫 라이더 아이템이 로드될 때까지 대기
            try:
                # _perform_login에서 이미 URL 이동을 확인했지만, 여기서 컨텐츠가 확실히 로드될 때까지 한번 더 기다립니다.
                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, daily_wait_xpath)))
                logger.info(f"✅ 대시보드 컨텐츠 로드 확인 ({daily_wait_xpath})")
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, daily_sub_wait_xpath)))
                logger.info(f"✅ 대시보드 하위 리스트 로드 확인 ({daily_sub_wait_xpath})")
                
                daily_html = driver.page_source
                if len(daily_html) < 1000: raise Exception("대시보드 HTML 길이가 너무 짧아 로딩 실패로 간주")
            except Exception as e:
                # 오류 발생 시 디버깅을 위한 스크린샷 및 페이지 소스 저장
                timestamp = get_korea_time().strftime("%Y%m%d_%H%M%S")
                screenshot_path = f"error_screenshot_{timestamp}.png"
                pagesource_path = f"error_page_source_{timestamp}.html"
                
                try:
                    driver.save_screenshot(screenshot_path)
                    with open(pagesource_path, "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                    logger.info(f"📸 오류 스크린샷 저장: {screenshot_path}")
                    logger.info(f"📄 오류 페이지 소스 저장: {pagesource_path}")
                except Exception as save_e:
                    logger.error(f"디버깅 파일 저장 실패: {save_e}")

                logger.error(f"대시보드에서 데이터 수집 실패: {e}", exc_info=True)
                return self._get_error_data("일간 데이터 페이지(대시보드) 크롤링 실패")

            daily_data = self._parse_daily_data(daily_html)
            logger.info("✅ 일간 데이터 파싱 완료")

            # 2. 주간 데이터 페이지로 이동하여 주간 데이터 수집
            weekly_url = "https://jangboo.grider.ai/orders/sla/list"
            weekly_wait_xpath = "//div[contains(@class, 'rider_container')]"
            # 점수 영역의 숫자가 실제로 로드될 때까지 추가로 기다립니다. (숫자가 하나라도 포함될 때까지)
            sub_wait_xpath = "//span[@data-text='total' and string-length(text()) > 0 and number(translate(text(), '0123456789', '')) != number(text())]"
            weekly_html = self._crawl_page(driver, weekly_url, weekly_wait_xpath, sub_wait_xpath=sub_wait_xpath)
            if not weekly_html: return self._get_error_data("주간 데이터 페이지 크롤링 실패")
            
            weekly_data = self._parse_weekly_data(weekly_html)
            logger.info("✅ 주간 데이터 파싱 완료")
            
            final_data = {**weekly_data, **daily_data}
            final_data['weather_info'] = self._get_weather_info_detailed()
            final_data['timestamp'] = get_korea_time().strftime("%Y-%m-%d %H:%M:%S")
            final_data['mission_date'] = self._get_mission_date()
            final_data['error'] = False
            
            logger.info(" G라이더 데이터 수집 완료")
            return final_data

        except Exception as e:
            logger.error(f" 크롤링 중 오류 발생: {e}", exc_info=True)
            return self._get_error_data(f"크롤링 중 예외 발생: {e}")
        finally:
            if driver:
                driver.quit()

    def _get_error_data(self, error_reason):
        return {
            '총점': 0, '물량점수': 0, '수락률점수': 0, '총완료': 0, '총거절': 0, '수락률': 0.0,
            '아침점심피크': {"current": 0, "target": 0}, '오후논피크': {"current": 0, "target": 0},
            '저녁피크': {"current": 0, "target": 0}, '심야논피크': {"current": 0, "target": 0},
            'daily_riders': [], 'error': True, 'error_reason': error_reason,
            'timestamp': datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _perform_login(self, driver):
        try:
            wait = WebDriverWait(driver, 20)
            driver.get('https://jangboo.grider.ai/login')
            wait.until(EC.presence_of_element_located((By.ID, 'id')))
            
            USER_ID = os.getenv('GRIDER_ID')
            USER_PW = os.getenv('GRIDER_PASSWORD')
            if not USER_ID or not USER_PW: raise Exception("G라이더 로그인 정보가 없습니다.")
            
            driver.find_element(By.ID, 'id').send_keys(USER_ID)
            driver.find_element(By.ID, 'password').send_keys(USER_PW)
            driver.find_element(By.ID, 'loginBtn').click()
            WebDriverWait(driver, 30).until(EC.url_contains('/dashboard'))
            logger.info("✅ 로그인 성공")
            return True
        except Exception as e:
            logger.error(f"로그인 과정에서 오류 발생: {e}")
            return False

    def _crawl_page(self, driver, url, wait_xpath, max_retries=3, retry_delay=5, sub_wait_xpath=None):
        for attempt in range(max_retries):
            try:
                logger.info(f"{url} 페이지 크롤링 시도 {attempt + 1}/{max_retries}")
                driver.get(url)
                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, wait_xpath)))
                logger.info(f"✅ 페이지 로드 확인 ({wait_xpath})")

                if sub_wait_xpath:
                    logger.info(f"하위 요소 대기 시작: {sub_wait_xpath}")
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, sub_wait_xpath)))
                    logger.info(f"✅ 하위 요소 로드 확인 ({sub_wait_xpath})")
                
                html = driver.page_source
                if len(html) < 1000: raise Exception("HTML 길이가 너무 짧아 로딩 실패로 간주")
                return html
            except Exception as e:
                logger.error(f" 크롤링 시도 {attempt + 1} 실패: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    logger.error(f" 모든 크롤링 시도 실패 ({url})")
                    return None

    def _get_mission_date(self):
        korea_time = get_korea_time()
        mission_time = korea_time - timedelta(hours=6)
        return mission_time.strftime('%Y-%m-%d')

    def _parse_weekly_data(self, html: str) -> dict:
        soup = BeautifulSoup(html, 'html.parser')
        data = {
            '총점': 0, '물량점수': 0, '수락률점수': 0, '총완료': 0, '총거절': 0, '수락률': 0.0,
            '아침점심피크': {"current": 0, "target": 0}, '오후논피크': {"current": 0, "target": 0},
            '저녁피크': {"current": 0, "target": 0}, '심야논피크': {"current": 0, "target": 0},
        }

        def get_number(text, to_float=False):
            if not text: return 0.0 if to_float else 0
            cleaned_text = text.replace(',', '').strip()
            match = re.search(r'(-?[\d\.]+)', cleaned_text)
            return float(match.group(1)) if match and to_float else int(match.group(1)) if match else 0

        def get_text_safe(node):
            return node.get_text(strip=True) if node and isinstance(node, Tag) else ""

        # 1. 점수 영역 파싱 (예상 총 점수, 물량/수락률 점수)
        summary_score_area = soup.select_one('.summary_score')
        if summary_score_area:
            logger.info("✅ 주간 데이터의 점수 요약 (.summary_score)을 찾았습니다.")
            data['총점'] = get_number(get_text_safe(summary_score_area.select_one('.score_total_value[data-text="total"]')))
            data['물량점수'] = get_number(get_text_safe(summary_score_area.select_one('.detail_score_value[data-text="quantity"]')))
            data['수락률점수'] = get_number(get_text_safe(summary_score_area.select_one('.detail_score_value[data-text="acceptance"]')))
            logger.info(f"점수 파싱: 총점={data['총점']}, 물량={data['물량점수']}, 수락률={data['수락률점수']}")
        else:
            logger.warning("⚠️ 주간 데이터에서 점수 요약 영역(.summary_score)을 찾지 못했습니다.")

        # 2. 건수 영역 파싱 (총 완료/거절 건수 및 수락률 재계산)
        summary_header = soup.select_one('.rider_th.total_value_th')
        if summary_header:
            logger.info("✅ 주간 데이터의 라이더 요약 헤더 (.rider_th.total_value_th)를 찾았습니다.")

            def get_total_val(cls, to_float=False):
                node = summary_header.select_one(f'div[data-total_value="{cls}"]')
                text = get_text_safe(node)
                return get_number(text, to_float)

            # 사용자 요청에 따라 이 곳의 데이터를 최종 값으로 사용
            data['총완료'] = get_total_val('complete_count')
            
            base_rejects = get_total_val('reject_count')
            accept_cancel = get_total_val('accept_cancel_count')
            rider_fault_cancel = get_total_val('accept_cancel_rider_fault_count')
            data['총거절'] = base_rejects + accept_cancel + rider_fault_cancel

            # 사용자 요청에 따라 수락률 재계산
            total_for_rate = data['총완료'] + data['총거절']
            if total_for_rate > 0:
                data['수락률'] = (data['총완료'] / total_for_rate) * 100
            else:
                data['수락률'] = 0.0
            
            logger.info(f"주간 건수 계산: 완료={data['총완료']}, 거절(합산)={data['총거절']}, 재계산된 수락률={data['수락률']:.1f}%")
        else:
            logger.warning("⚠️ 주간 데이터에서 라이더 요약 헤더 (.rider_th.total_value_th)를 찾지 못했습니다.")

        return data

    def _parse_daily_data(self, html: str) -> dict:
        soup = BeautifulSoup(html, 'html.parser')
        
        def get_number(text, to_float=False):
            if not text: return 0.0 if to_float else 0
            cleaned_text = text.replace(',', '').strip()
            match = re.search(r'(-?[\d\.]+)', cleaned_text)
            return float(match.group(1)) if match and to_float else int(match.group(1)) if match else 0
            
        riders = []
        rider_container = soup.select_one('div.rider_container')
        
        if rider_container and isinstance(rider_container, Tag):
            rider_items = rider_container.select('.rider_list .rider_item')
            logger.info(f"✅ 일간 데이터에서 {len(rider_items)}명의 라이더 데이터를 찾았습니다.")
            
            def get_val(item, cls, to_float=False):
                node = item.select_one(f'.{cls}')
                text_content = node.get_text(strip=True) if node and isinstance(node, Tag) else ""
                text = re.sub(r'^[가-힣A-Za-z]+', '', text_content).strip()
                return get_number(text, to_float)

            for item in rider_items:
                name_node = item.select_one('.rider_name')
                id_node = item.select_one('.user_id')
                acceptance_node = item.select_one('.acceptance_rate')

                name = '이름없음'
                if name_node and isinstance(name_node, Tag):
                    for child in name_node.find_all(['span', 'p', 'div']): child.decompose()
                    name = name_node.get_text(strip=True)
                
                acceptance_text = acceptance_node.get_text(strip=True) if acceptance_node and isinstance(acceptance_node, Tag) else "0"
                id_text = id_node.get_text(strip=True).replace('아이디', '') if id_node and isinstance(id_node, Tag) else ''

                riders.append({
                    'name': name, 'id': id_text,
                    '수락률': get_number(acceptance_text, to_float=True),
                    '완료': get_val(item, 'complete_count'),
                    '거절': get_val(item, 'reject_count'),
                    '배차취소': get_val(item, 'accept_cancel_count'),
                    '배달취소': get_val(item, 'accept_cancel_rider_fault_count'),
                    '아침점심피크': get_val(item, 'morning_peak_count'),
                    '오후논피크': get_val(item, 'afternoon_peak_count'),
                    '저녁피크': get_val(item, 'evening_peak_count'),
                    '심야논피크': get_val(item, 'midnight_peak_count'),
                })
        else:
            logger.warning("⚠️ 일간 데이터에서 '라이더 현황' 컨테이너 (div.rider_container)를 찾지 못했습니다.")
        
        return {'daily_riders': riders}

    def _get_weather_info_detailed(self, location="서울"):
        try:
            url = f"https://wttr.in/{location}?format=j1"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            weather_data = response.json()
            
            am_temps, pm_temps = [], []
            am_icons, pm_icons = [], []

            weather_icon_map = {
                "Sunny": "☀️", "Clear": "☀️", "Partly cloudy": "⛅️", "Cloudy": "☁️", 
                "Overcast": "☁️", "Mist": "🌫️", "Fog": "🌫️", 
                "Patchy rain possible": "🌦️", "Light rain": "🌦️", "Rain": "🌧️", 
                "Thundery outbreaks possible": "⛈️", "Thunderstorm": "⛈️", 
                "Snow": "❄️", "Blizzard": "🌨️"
            }
            def get_icon(desc):
                return next((icon for key, icon in weather_icon_map.items() if key in desc), "☁️")

            for forecast in weather_data.get('weather', [{}])[0].get('hourly', []):
                hour = int(forecast.get('time', '0')) // 100
                temp = int(forecast.get('tempC', '0'))
                icon = get_icon(forecast.get('weatherDesc', [{}])[0].get('value', ''))
                
                if 6 <= hour < 12: (am_temps.append(temp), am_icons.append(icon))
                elif 12 <= hour < 18: (pm_temps.append(temp), pm_icons.append(icon))

            am_icon = max(set(am_icons), key=am_icons.count) if am_icons else "☁️"
            pm_icon = max(set(pm_icons), key=pm_icons.count) if pm_icons else "☁️"
            
            am_line = f" 오전: {am_icon} {min(am_temps)}~{max(am_temps)}C" if am_temps else ""
            pm_line = f" 오후: {pm_icon} {min(pm_temps)}~{max(pm_temps)}C" if pm_temps else ""
            
            return f"🌍 오늘의 날씨 (기상청)\n{am_line}\n{pm_line}".strip()
        except Exception:
            return "🌍 오늘의 날씨 (기상청)\n날씨 정보 조회 불가"

class GriderAutoSender:
    """G-Rider 자동화 메인 클래스"""
    def __init__(self, rest_api_key=None, refresh_token=None):
        if not rest_api_key or not refresh_token:
            key, token = load_config()
            rest_api_key, refresh_token = key, token
        if not rest_api_key or not refresh_token:
            raise ValueError(" 카카오 API 설정이 필요합니다.")
        self.token_manager = TokenManager(rest_api_key, refresh_token)
        self.data_collector = GriderDataCollector()

    def send_report(self):
        """데이터를 수집하고, 파일로 저장한 뒤, 카톡으로 리포트를 전송합니다."""
        data = self.data_collector.get_grider_data()
        if not data or data.get('error'):
            logger.error(f"데이터 수집에 실패하여 리포트 전송을 중단합니다. 원인: {data.get('error_reason', '알 수 없음')}")
            return

        output_path = 'docs/api/latest-data.json'
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ 크롤링 결과를 {output_path} 파일로 성공적으로 저장했습니다.")
        except Exception as e:
            logger.error(f"❌ 크롤링 결과를 파일로 저장하는 중 오류 발생: {e}", exc_info=True)
        
        access_token = self.token_manager.get_valid_token()
        if not access_token:
            logger.error("유효한 카카오 토큰이 없어 리포트 전송을 중단합니다.")
            return
            
        message = self.format_message(data)
        kakao_sender = KakaoSender(access_token)
        kakao_sender.send_text_message(message)
        logger.info("카카오톡 리포트 전송을 요청했습니다.")

    def format_message(self, data: dict) -> str:
        """사용자 정의 규칙에 따라 상세한 카카오톡 메시지를 생성합니다."""
        
        def get_acceptance_progress_bar(percentage: float) -> str:
            if not 0 <= percentage <= 100: return ""
            filled_blocks = round(percentage / 10)
            return '🟩' * filled_blocks + '⬜' * (10 - filled_blocks)

        def get_rider_progress_bar(contribution: float) -> str:
            if not isinstance(contribution, (int, float)) or contribution < 0: contribution = 0
            contribution = min(contribution, 100)
            filled_blocks = round(contribution / 20)
            return '🟩' * filled_blocks + '⬜' * (5 - filled_blocks)

        try:
            header = "심플 배민 플러스 미션 알리미"

            peak_emojis = {'아침점심피크': '🌅', '오후논피크': '🌇', '저녁피크': '🌃', '심야논피크': '🌙'}
            peak_order = ['아침점심피크', '오후논피크', '저녁피크', '심야논피크']
            peak_start_hours = { '아침점심피크': 10, '오후논피크': 14, '저녁피크': 17, '심야논피크': 21 }
            
            peak_summary, alerts = "", []
            current_hour = get_korea_time().hour

            for peak in peak_order:
                if current_hour < peak_start_hours.get(peak, 0): continue
                details = data.get(peak, {'current': 0, 'target': 0})
                emoji = peak_emojis.get(peak, '❓')
                
                if details and details.get('target', 0) > 0:
                    is_achieved = details['current'] >= details['target']
                    shortfall = details['target'] - details['current']
                    status_icon = "✅ (달성)" if is_achieved else f"❌ ({shortfall}건 부족)"
                    peak_summary += f"{emoji} {peak}: {details['current']}/{details['target']} {status_icon}\n"
                    if not is_achieved and shortfall > 0:
                        alerts.append(f"{peak.replace('피크','')} {shortfall}건")
                else:
                     peak_summary += f"{emoji} {peak}: 데이터 없음\n"

            peak_summary = peak_summary.strip() or "ℹ️ 아직 시작된 당일 미션이 없습니다."

            # 일간 라이더 실적 요약
            all_daily_riders = data.get('daily_riders', []) 
            daily_total_completed = sum(r.get('완료', 0) for r in all_daily_riders)
            daily_total_rejected = sum(r.get('거절', 0) + r.get('배차취소', 0) + r.get('배달취소', 0) for r in all_daily_riders)
            daily_total_for_rate = daily_total_completed + daily_total_rejected
            daily_acceptance_rate = (daily_total_completed / daily_total_for_rate * 100) if daily_total_for_rate > 0 else 100

            daily_rider_summary = (
                "📈 일간 라이더 실적 요약\n"
                f"완료: {daily_total_completed}  거절: {daily_total_rejected}\n"
                f"수락률: {daily_acceptance_rate:.1f}%\n"
                f"{get_acceptance_progress_bar(daily_acceptance_rate)}"
            )

            # 이번주 미션 예상 점수
            total_score, quantity_score, acceptance_score = data.get('총점', 0), data.get('물량점수', 0), data.get('수락률점수', 0)
            weekly_acceptance_rate = float(data.get('수락률', 0))
            weekly_completed, weekly_rejected = data.get('총완료', 0), data.get('총거절', 0)

            weekly_summary = (
                "📊 이번주 미션 예상점수\n"
                f"총점: {total_score}점 (물량:{quantity_score}, 수락률:{acceptance_score})\n"
                f"완료: {weekly_completed}  거절: {weekly_rejected}\n"
                f"수락률: {weekly_acceptance_rate:.1f}%\n"
                f"{get_acceptance_progress_bar(weekly_acceptance_rate)}"
            )

            weather_summary = data.get('weather_info', '날씨 정보 조회 불가')

            # 라이더 순위 (일간)
            active_riders = sorted([r for r in all_daily_riders if r.get('완료', 0) > 0], key=lambda x: x.get('완료', 0), reverse=True)
            total_daily_count = sum(r.get('완료', 0) for r in active_riders)
            
            rider_ranking_summary = f"🏆 라이더 순위 (운행: {len(active_riders)}명)\n"
            for i, rider in enumerate(active_riders[:5]):
                rank_icon = ["🥇", "🥈", "🥉"][i] if i < 3 else f"  {i+1}."
                contribution = (rider.get('완료', 0) / total_daily_count * 100) if total_daily_count > 0 else 0
                rider_name = rider.get('name', '이름없음').replace('(본인)', '').strip()
                
                peak_counts_str = ' '.join([f"{peak_emojis.get(p, '❓')}{rider.get(p, 0)}" for p in peak_order])
                
                rider_completed = rider.get('완료', 0)
                rider_fail = rider.get('거절', 0) + rider.get('배차취소', 0) + rider.get('배달취소', 0)
                rider_acceptance_rate = (rider_completed / (rider_completed + rider_fail) * 100) if (rider_completed + rider_fail) > 0 else 100
                
                rider_ranking_summary += (
                    f"**{rank_icon} {rider_name}** | {get_rider_progress_bar(contribution)} {contribution:.1f}%\n"
                    f"    총 {rider_completed}건 ({peak_counts_str})\n"
                    f"    수락률: {rider_acceptance_rate:.1f}% (거절:{rider.get('거절',0)}, 취소:{rider.get('배차취소',0)+rider.get('배달취소',0)})"
                )
                if i < len(active_riders) - 1 and i < 4:
                    rider_ranking_summary += "\n"

            alert_summary = "⚠️ 미션 부족: " + ", ".join(alerts) if alerts else ""
            
            message_parts = [
                header, peak_summary, daily_rider_summary, weather_summary, 
                weekly_summary, rider_ranking_summary, alert_summary
            ]
            return "\n\n".join(filter(None, message_parts))

        except Exception as e:
            logger.error(f" 메시지 포맷팅 실패: {e}", exc_info=True)
            return "리포트 생성 중 오류가 발생했습니다."

def load_config():
    """설정 파일 또는 환경변수에서 로드"""
    rest_api_key = os.getenv('KAKAO_REST_API_KEY')
    refresh_token = os.getenv('KAKAO_REFRESH_TOKEN')
    if rest_api_key and refresh_token: return rest_api_key, refresh_token
    
    config_file = 'semiauto/config.txt'
    if not os.path.exists(config_file): return None, None
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = {line.split('=')[0]: line.split('=')[1].strip() for line in f if '=' in line}
        return config.get('REST_API_KEY'), config.get('REFRESH_TOKEN')
    except Exception as e:
        logger.error(f" 설정 파일 로드 실패: {e}")
        return None, None

def main():
    try:
        GriderAutoSender().send_report()
    except (ValueError, Exception) as e:
        logger.error(f" 실행 실패: {e}", exc_info=True)

if __name__ == '__main__':
    main() 