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
from dotenv import load_dotenv

# Selenium 명시적 대기를 위한 모듈 추가
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

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
    """G라이더 데이터 수집기"""
    
    def __init__(self):
        self.driver_path = os.getenv('CHROME_DRIVER_PATH', '/usr/bin/chromedriver')
        
        # 설정 파일에서 선택자 및 URL 로드
        self.selectors = self._load_selectors()
        
        self.base_url = self.selectors.get('base_url', '')
        self.login_url = f"{self.base_url}{self.selectors.get('login', {}).get('url_path', '/login')}"
        self.dashboard_url = f"{self.base_url}{self.selectors.get('daily_data', {}).get('url_path', '/dashboard')}"
        self.sla_url = f"{self.base_url}{self.selectors.get('weekly_mission_data', {}).get('url_path', '/orders/sla/list')}"

        self.driver = None
        self.grider_id = os.getenv('GRIDER_ID')
        self.grider_password = os.getenv('GRIDER_PASSWORD')
        self.weather_api_key = os.getenv('WEATHER_API_KEY')
        self.holidays = []

    def _load_selectors(self):
        """selectors.json 파일에서 CSS 선택자를 로드합니다."""
        # 스크립트 파일의 위치를 기준으로 경로 설정
        current_dir = os.path.dirname(os.path.abspath(__file__))
        selectors_path = os.path.join(current_dir, '..', 'selectors.json')
        try:
            with open(selectors_path, 'r', encoding='utf-8') as f:
                logger.info(f"CSS 선택자 설정 파일 로드: {selectors_path}")
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"선택자 파일({selectors_path}) 로드 실패: {e}")
            return {}

    def _get_driver(self):
        """Headless Chrome 드라이버를 설정하고 반환합니다."""
        try:
            from selenium import webdriver
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

            if not self.grider_id or not self.grider_password: raise Exception("G라이더 로그인 정보가 없습니다.")

            login_url = f"{self.base_url}/login"
            logger.info(f"로그인 페이지로 이동: {login_url}")
            driver.get(login_url)

            # ID/PW 입력 필드가 나타날 때까지 명시적으로 대기
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'id')))
            
            driver.find_element(By.ID, 'id').send_keys(self.grider_id)
            driver.find_element(By.ID, 'password').send_keys(self.grider_password)
            driver.find_element(By.ID, 'loginBtn').click()
            WebDriverWait(driver, 30).until(EC.url_contains('/dashboard'))
            logger.info("✅ 로그인 성공")
            return driver
        except Exception as e:
            logger.error(f" G라이더 로그인 실패: {e}", exc_info=True)
            if 'driver' in locals() and driver:
                driver.quit()
            raise Exception("G라이더 로그인 실패")

    def _crawl_page(self, driver, url, wait_xpath, max_retries=3, retry_delay=5, sub_wait_xpath=None):
        # 이 함수는 이제 사용되지 않지만, 다른 곳에서 호출할 경우를 대비해 남겨둡니다.
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

    def _login(self, driver):
        """G라이더에 로그인합니다."""
        logger.info(f"로그인 페이지로 이동: {self.login_url}")
        try:
            driver.get(self.login_url)
            wait = WebDriverWait(driver, 15)
            
            # 선택자 파일에서 로그인 정보 가져오기
            s = self.selectors.get('login', {})
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, s.get('id_input')))).send_keys(self.grider_id)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, s.get('pw_input')))).send_keys(self.grider_password)
            driver.find_element(By.CSS_SELECTOR, s.get('login_button')).click()
            
            # 로그인 성공 확인 (대시보드 URL로 이동했는지 또는 특정 요소가 보이는지)
            wait.until(EC.url_to_be(self.dashboard_url))
            logger.info("✅ 로그인 성공")
            return True
        except TimeoutException:
            logger.error("G라이더 로그인 실패: 타임아웃", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"G라이더 로그인 실패: {e}", exc_info=True)
            return False

    def _get_mission_date(self):
        korea_time = get_korea_time()
        mission_time = korea_time - timedelta(hours=6)
        return mission_time.strftime('%Y-%m-%d')

    def _parse_weekly_data(self, driver):
        """SLA 페이지에서 주간 요약 점수와 라이더 실적 데이터를 파싱하고 계산합니다."""
        weekly_data = {}
        logger.info("'주간 미션 예상 점수' 데이터 수집을 시작합니다.")
        
        try:
            wait = WebDriverWait(driver, 15)
            
            s_weekly = self.selectors.get('weekly_mission_data', {})
            s_summary = s_weekly.get('summary', {})
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, s_summary.get('container'))))
            soup = BeautifulSoup(driver.page_source, 'lxml')

            summary_area = soup.select_one(s_summary.get('container'))
            if summary_area:
                def get_summary_score(data_text_key):
                    selector = s_summary.get(data_text_key)
                    node = summary_area.select_one(selector) if selector else None
                    return node.get_text(strip=True) if node else "0"

                weekly_data['예상총점수'] = get_summary_score('total_score')
                weekly_data['물량점수'] = get_summary_score('quantity_score')
                weekly_data['수락률점수'] = get_summary_score('acceptance_score')
                logger.info(f"✅ 예상 점수 카드 파싱 완료: {weekly_data}")
            else:
                logger.warning(f"예상 점수 요약 카드({s_summary.get('container')})를 찾지 못했습니다.")

            s_rider_list = s_weekly.get('weekly_rider_list', {})
            rider_list_container = soup.select_one(s_rider_list.get('container'))
            if rider_list_container:
                rider_items = rider_list_container.select(s_rider_list.get('item'))
                logger.info(f"{len(rider_items)}명의 주간 라이더 데이터를 기반으로 실적 계산을 시작합니다.")

                s_daily_keys = self.selectors.get('daily_data', {})
                total_completions = 0
                total_rejections = 0
                total_dispatch_cancels = 0
                total_delivery_cancels = 0

                for item in rider_items:
                    def get_stat(stat_name_key):
                        selector = s_daily_keys.get(stat_name_key)
                        node = item.select_one(selector) if selector else None
                        return self._get_safe_number(node.get_text(strip=True)) if node else 0

                    completed = get_stat('complete_count')
                    rejected = get_stat('reject_count')
                    dispatch_canceled = get_stat('accept_cancel_count')
                    delivery_canceled = get_stat('accept_cancel_rider_fault_count')

                    if completed == 0 and rejected == 0 and dispatch_canceled == 0 and delivery_canceled == 0:
                        continue

                    total_completions += completed
                    total_rejections += rejected
                    total_dispatch_cancels += dispatch_canceled
                    total_delivery_cancels += delivery_canceled

                calculated_total_rejections = total_rejections + total_dispatch_cancels + total_delivery_cancels
                total_for_rate = total_completions + calculated_total_rejections
                
                weekly_data['총완료'] = total_completions
                weekly_data['총거절'] = calculated_total_rejections
                weekly_data['수락률'] = f"{(total_completions / total_for_rate * 100):.2f}%" if total_for_rate > 0 else "0.00%"
                logger.info(f"✅ 주간 라이더 실적 계산 완료: 총완료={weekly_data['총완료']}, 총거절={weekly_data['총거절']}, 수락률={weekly_data['수락률']}")
            else:
                 logger.warning(f"주간 라이더 목록({s_rider_list.get('container')})를 찾지 못했습니다.")

        except Exception as e:
            logger.error(f"주간 데이터 파싱 중 오류 발생: {e}", exc_info=True)
            
        return weekly_data

    def _parse_daily_rider_data(self, driver):
        """대시보드에서 일간 라이더 데이터를 파싱합니다."""
        rider_list = []
        try:
            logger.info("로그인 후 대시보드에서 '일간 라이더 데이터' 수집을 시작합니다.")
            wait = WebDriverWait(driver, 10)
            
            s_daily = self.selectors.get('daily_data', {})
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, s_daily.get('container'))))
            logger.info("✅ 일간 라이더 목록이 로드되었습니다.")

            soup = BeautifulSoup(driver.page_source, 'lxml')
            
            rider_list_container = soup.select_one(s_daily.get('container'))
            if not rider_list_container:
                logger.warning(f"일간 라이더 목록 컨테이너({s_daily.get('container')})를 찾을 수 없습니다.")
                return {'daily_riders': []}
                
            rider_items = rider_list_container.select(s_daily.get('item', '.rider_item'))
            logger.info(f"{len(rider_items)}명의 라이더 데이터를 파싱합니다.")

            for item in rider_items:
                def get_stat(stat_name_key):
                    selector = s_daily.get(stat_name_key)
                    node = item.select_one(selector) if selector else None
                    return self._get_safe_number(node.get_text(strip=True)) if node else 0

                rider_list.append({
                    'name': (item.select_one(s_daily.get('name')) or Tag(name='span')).get_text(strip=True),
                    '완료': get_stat('complete_count'),
                    '거절': get_stat('reject_count'),
                    '배차취소': get_stat('accept_cancel_count'),
                    '배달취소': get_stat('accept_cancel_rider_fault_count'),
                })
        except Exception as e:
            logger.error(f"일간 라이더 데이터 파싱 중 오류 발생: {e}", exc_info=True)
        return {'daily_riders': rider_list}

    def _parse_mission_data(self, driver) -> dict:
        """SLA 페이지에서 오늘 날짜의 미션 데이터를 파싱합니다."""
        mission_data = {}
        try:
            logger.info(f"오늘 날짜({self._get_today_date()})의 미션 데이터 파싱을 시작합니다.")
            wait = WebDriverWait(driver, 10)
            
            s_mission = self.selectors.get('weekly_mission_data', {}).get('mission_table', {})
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, s_mission.get('container'))))
            soup = BeautifulSoup(driver.page_source, 'lxml')
            
            sla_table = soup.select_one(s_mission.get('container'))
            if not sla_table:
                logger.warning(f"'물량 점수관리' 테이블({s_mission.get('container')})을 찾을 수 없습니다.")
                return {}

            target_row = None
            today_str = self._get_today_date()
            all_rows = sla_table.select(s_mission.get('row', 'tbody tr'))
            for row in all_rows:
                date_cell = row.find_all('td')
                if len(date_cell) > 1 and today_str in date_cell[1].get_text():
                    target_row = row
                    break
            
            if not target_row:
                logger.warning(f"{today_str}에 해당하는 미션 데이터를 테이블에서 찾을 수 없습니다.")
                return {}

            cols = target_row.find_all('td')
            if len(cols) < 7:
                logger.warning("미션 데이터 테이블의 컬럼 수가 예상과 다릅니다.")
                return {}

            def parse_col(index):
                text = cols[index].get_text(strip=True)
                match = re.search(r'(\d+/\d+)', text)
                return match.group(1) if match else text

            mission_data = {
                'date': cols[1].get_text(strip=True),
                'total_score': cols[2].get_text(strip=True),
                'morning_peak': parse_col(3),
                'afternoon_offpeak': parse_col(4),
                'evening_peak': parse_col(5),
                'night_offpeak': parse_col(6),
            }
            logger.info(f"✅ 미션 데이터 파싱 완료: {mission_data}")

        except Exception as e:
            logger.error(f"미션 데이터 파싱 중 오류 발생: {e}", exc_info=True)

        return mission_data

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

    def _perform_login(self):
        """G라이더 웹사이트에 로그인하고 드라이버 객체를 반환합니다."""
        driver = self._get_driver()
        if not driver:
            raise Exception("웹 드라이버를 초기화할 수 없습니다.")
        
        if not self.grider_id or not self.grider_password:
            raise Exception("G라이더 ID 또는 비밀번호 환경 변수가 설정되지 않았습니다.")

        self._login(driver)
        return driver
    
    def _get_safe_number(self, text, to_float=False):
        """문자열에서 숫자만 안전하게 추출합니다. 숫자가 없으면 0을 반환합니다."""
        if text:
            try:
                if to_float:
                    return float(text)
                else:
                    return int(text)
            except ValueError:
                return 0
        else:
            return 0

class GriderAutoSender:
    """G-Rider 자동화 메시지 발송기"""
    
    def __init__(self, rest_api_key=None, refresh_token=None):
        self.config = {
            'REST_API_KEY': rest_api_key or os.getenv('KAKAO_REST_API_KEY'),
            'REFRESH_TOKEN': refresh_token or os.getenv('KAKAO_REFRESH_TOKEN')
        }
        self.token_manager = TokenManager(self.config['REST_API_KEY'], self.config['REFRESH_TOKEN'])
        self.data_collector = GriderDataCollector()

    def save_dashboard_data(self, data: dict):
        """크롤링된 데이터를 대시보드용 JSON 파일로 저장"""
        # 스크립트 파일의 위치를 기준으로 dashboard 디렉토리 경로 설정
        base_dir = os.path.dirname(os.path.abspath(__file__))
        dashboard_api_dir = os.path.join(base_dir, '..', 'dashboard', 'api')

        # 디렉토리가 없으면 생성
        os.makedirs(dashboard_api_dir, exist_ok=True)

        # 파일 경로 설정
        file_path = os.path.join(dashboard_api_dir, 'latest-data.json')

        try:
            # 데이터에 타임스탬프 추가
            data_to_save = data.copy()
            data_to_save['last_updated'] = get_korea_time().isoformat()

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
            logger.info(f"대시보드 데이터 저장 완료: {file_path}")
            return True
        except Exception as e:
            logger.error(f"대시보드 데이터 저장 실패: {e}")
            return False

    def send_report(self):
        """G-Rider 운행 리포트 자동 발송"""
        
        # 1. G-Rider 데이터 수집
        grider_data = self.data_collector.get_grider_data()
        
        # 2. 데이터 유효성 검사
        if grider_data['error']:
            logger.error(f"데이터 수집 실패: {grider_data['error_reason']}")
            # 에러 발생 시에도 대시보드 데이터는 업데이트 (상태 확인용)
            self.save_dashboard_data(grider_data)
            return

        # 3. 메시지 포맷팅
        formatted_message = self.format_message(grider_data)

        # 4. 카카오톡 메시지 전송
        self.send_kakao_message(formatted_message)
        
        # 5. 클립보드에 복사 (로컬 환경에서만)
        if os.getenv('GITHUB_ACTIONS') != 'true':
            try:
                import pyperclip
                pyperclip.copy(formatted_message)
                logger.info(" 메시지가 클립보드에 복사되었습니다.")
            except ImportError:
                logger.warning(" pyperclip 모듈이 설치되지 않아 클립보드 복사를 건너뜁니다.")
        
        # 6. 대시보드용 데이터 저장
        self.save_dashboard_data(grider_data)
    
    def send_kakao_message(self, text: str):
        """카카오톡 메시지 전송 실행"""
        access_token = self.token_manager.get_valid_token()
        if not access_token:
            logger.error("유효한 토큰이 없어 메시지 전송을 건너뜁니다.")
            return

        sender = KakaoSender(access_token)
        if not sender.send_text_message(text):
            logger.error("카카오톡 메시지 전송에 실패했습니다.")
        else:
            logger.info("카카오톡 리포트 전송을 요청했습니다.")

    def format_message(self, data: dict) -> str:
        """카카오톡 전송을 위한 메시지 포맷팅"""
        
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
    """환경변수 또는 .env 파일에서 설정 로드"""
    # .env 파일 경로를 스크립트 파일 기준으로 설정
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path)
    
    config = {
        'GRIDER_ID': os.getenv('GRIDER_ID'),
        'GRIDER_PASSWORD': os.getenv('GRIDER_PASSWORD'),
        'KAKAO_REST_API_KEY': os.getenv('KAKAO_REST_API_KEY'),
        'KAKAO_REFRESH_TOKEN': os.getenv('KAKAO_REFRESH_TOKEN'),
        'KOREA_HOLIDAY_API_KEY': os.getenv('KOREA_HOLIDAY_API_KEY')
    }
    
    # 필수 설정값 확인
    if not all([config['GRIDER_ID'], config['GRIDER_PASSWORD'], config['KAKAO_REST_API_KEY'], config['KAKAO_REFRESH_TOKEN']]):
        logger.warning("필수 환경변수가 모두 설정되지 않았습니다.")
        
    return config

def main():
    """메인 실행 함수"""
    logger.info("="*50)
    logger.info(" G-Rider 자동화 스크립트 시작")
    logger.info("="*50)
    
    config = load_config()
    sender = GriderAutoSender(
        rest_api_key=config.get('KAKAO_REST_API_KEY'),
        refresh_token=config.get('KAKAO_REFRESH_TOKEN')
    )
    sender.send_report()
    
    logger.info("="*50)
    logger.info(" G-Rider 자동화 스크립트 종료")
    logger.info("="*50)

if __name__ == '__main__':
    main() 