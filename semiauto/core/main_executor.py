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
from datetime import datetime, timedelta, timezone
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException

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
        self.selectors = self._load_all_selectors()
        
        self.base_url = "https://jangboo.grider.ai"
        self.login_url = f"{self.base_url}{self.selectors.get('login', {}).get('url_path', '/login')}"
        self.dashboard_url = f"{self.base_url}{self.selectors.get('daily_data', {}).get('url_path', '/dashboard')}"
        self.sla_url = f"{self.base_url}{self.selectors.get('weekly_summary', {}).get('url_path', '/orders/sla/list')}"

        self.driver = None
        self.grider_id = os.getenv('GRIDER_ID')
        self.grider_password = os.getenv('GRIDER_PASSWORD')
        self.weather_api_key = os.getenv('WEATHER_API_KEY')
        self.holidays = []

    def _load_all_selectors(self):
        """'semiauto/selectors' 디렉토리의 모든 .json 파일을 로드하여 병합합니다."""
        all_selectors = {}
        current_dir = os.path.dirname(os.path.abspath(__file__))
        selectors_dir = os.path.join(current_dir, '..', 'selectors')
        
        if not os.path.isdir(selectors_dir):
            logger.error(f"선택자 디렉토리가 존재하지 않습니다: {selectors_dir}")
            return {}

        for filename in os.listdir(selectors_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(selectors_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # 파일 이름(확장자 제외)을 key로 사용하여 데이터를 저장합니다.
                        key_name = os.path.splitext(filename)[0]
                        all_selectors[key_name] = data
                        logger.info(f"선택자 파일 로드 완료: {filename}")
                except (FileNotFoundError, json.JSONDecodeError) as e:
                    logger.error(f"선택자 파일({filename}) 로드 실패: {e}")
        
        return all_selectors

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

            login_selectors = self.selectors.get('login', {})
            login_url = f"{self.base_url}{login_selectors.get('url_path', '/login')}"

            logger.info(f"로그인 페이지로 이동: {login_url}")
            driver.get(login_url)

            # ID/PW 입력 필드가 나타날 때까지 명시적으로 대기
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, login_selectors.get('id_input'))))
            
            driver.find_element(By.CSS_SELECTOR, login_selectors.get('id_input')).send_keys(self.grider_id)
            driver.find_element(By.CSS_SELECTOR, login_selectors.get('pw_input')).send_keys(self.grider_password)
            driver.find_element(By.CSS_SELECTOR, login_selectors.get('login_button')).click()
            
            # 페이지 전환을 위한 충분한 대기 시간
            time.sleep(2) # 로그인 후 페이지가 완전히 로드될 때까지 잠시 대기
            
            if "dashboard" in driver.current_url:
                logger.info("✅ 로그인 성공")
                return driver
            else:
                logger.error("로그인 실패: 로그인 후 대시보드로 이동하지 않음")
                return None
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
            
            # 페이지 전환을 위한 충분한 대기 시간
            time.sleep(2) # 로그인 후 페이지가 완전히 로드될 때까지 잠시 대기
            
            if "dashboard" in driver.current_url:
                logger.info("✅ 로그인 성공")
                return True
            else:
                logger.error("로그인 실패: 로그인 후 대시보드로 이동하지 않음")
                return False
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

    def _get_today_date(self):
        """한국시간 기준 오늘 날짜를 'YYYY-MM-DD' 형식으로 반환합니다."""
        return get_korea_time().strftime('%Y-%m-%d')

    def _parse_weekly_data(self, driver):
        """SLA 페이지에서 주간 요약 점수와 라이더 실적 데이터를 파싱하고 계산합니다."""
        weekly_data = {}
        try:
            driver.get(self.sla_url)
            time.sleep(2) # 페이지 전환을 위한 대기
            wait = WebDriverWait(driver, 10)

            # 1. 주간 요약 점수 파싱 (카드에 표시된 점수만 가져옴)
            summary_scores = {}
            s_summary = self.selectors.get('weekly_summary', {})
            summary_container_selector = s_summary.get('summary', {}).get('container')
            if summary_container_selector:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, summary_container_selector)))
                summary_scores['예상총점수'] = driver.find_element(By.CSS_SELECTOR, s_summary.get('summary', {}).get('total_score')).text.strip()
                summary_scores['물량점수'] = driver.find_element(By.CSS_SELECTOR, s_summary.get('summary', {}).get('quantity_score')).text.strip()
                summary_scores['수락률점수'] = driver.find_element(By.CSS_SELECTOR, s_summary.get('summary', {}).get('acceptance_score')).text.strip()
                logger.info(f"✅ 예상 점수 카드 파싱 완료: {summary_scores}")
            else:
                logger.warning("주간 요약 점수 선택자를 찾을 수 없습니다.")

            # 2. 주간 라이더 목록을 기반으로 실적 직접 계산
            calculated_stats = { '총완료': 0, '총거절': 0, '수락률': 0.0 }
            s_rider_list = self.selectors.get('weekly_riders', {})
            rider_list_container = s_rider_list.get('container')

            if rider_list_container:
                # 주간 라이더 목록의 첫번째 아이템이 나타날 때까지 대기
                item_selector = f"{rider_list_container} {s_rider_list.get('item')}"
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, item_selector)))
                
                riders = driver.find_elements(By.CSS_SELECTOR, item_selector)
                logger.info(f"{len(riders)}명의 주간 라이더 데이터를 기반으로 실적 계산을 시작합니다.")

                if riders:
                    total_completions = 0
                    total_rejections = 0
                    total_dispatch_cancels = 0
                    total_delivery_cancels = 0

                    for rider_element in riders:
                        try:
                            total_completions += int(rider_element.find_element(By.CSS_SELECTOR, s_rider_list.get('complete_count')).text.strip())
                            total_rejections += int(rider_element.find_element(By.CSS_SELECTOR, s_rider_list.get('reject_count')).text.strip())
                            total_dispatch_cancels += int(rider_element.find_element(By.CSS_SELECTOR, s_rider_list.get('dispatch_cancel_count')).text.strip())
                            total_delivery_cancels += int(rider_element.find_element(By.CSS_SELECTOR, s_rider_list.get('delivery_cancel_count')).text.strip())
                        except (NoSuchElementException, ValueError) as e:
                            logger.warning(f"라이더 데이터 파싱 중 오류(건너뜀): {e}")
                            continue
                    
                    calculated_total_rejections = total_rejections + total_dispatch_cancels + total_delivery_cancels
                    total_for_rate = total_completions + calculated_total_rejections
                    
                    calculated_stats['총완료'] = total_completions
                    calculated_stats['총거절'] = calculated_total_rejections
                    calculated_stats['수락률'] = (total_completions / total_for_rate * 100) if total_for_rate > 0 else 0.0
                    
                    logger.info(f"✅ 주간 라이더 실적 직접 계산 완료: 총완료={calculated_stats['총완료']}, 총거절={calculated_stats['총거절']}, 수락률={calculated_stats['수락률']:.2f}%")
                else:
                    logger.warning(f"주간 라이더 목록({rider_list_container})를 찾았으나, 개별 라이더({s_rider_list.get('item')})가 없습니다.")
            else:
                 logger.warning(f"주간 라이더 목록 선택자를 찾지 못했습니다.")

            # 3. 최종 데이터 조합
            weekly_data.update(summary_scores)
            weekly_data.update(calculated_stats)

        except Exception as e:
            logger.error(f"'주간/미션 데이터' 파싱 중 예외 발생: {e}", exc_info=True)
            
        return weekly_data

    def _parse_daily_rider_data(self, driver):
        """대시보드에서 일간 라이더 데이터를 파싱합니다."""
        daily_data = {}
        rider_list = []
        try:
            logger.info("로그인 후 대시보드에서 '일간 라이더 데이터' 수집을 시작합니다.")
            driver.get(self.dashboard_url)
            time.sleep(3) # JS 실행을 위한 최소 대기

            s_rider_list = self.selectors.get('daily_data', {})
            rider_list_container_selector = s_rider_list.get('container')
            item_selector = s_rider_list.get('item')
            full_item_selector = f"{rider_list_container_selector} {item_selector}"

            for attempt in range(2): # 총 2번 시도
                try:
                    logger.info(f"데이터 수집 시도 #{attempt + 1}")
                    wait = WebDriverWait(driver, 20)

                    # 1단계: 컨테이너가 먼저 존재하는지 확인
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, rider_list_container_selector)))
                    logger.info("✅ 라이더 목록 컨테이너 로드 완료.")

                    # 2단계: 실제 데이터 항목이 나타나는지 확인
                    rider_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, full_item_selector)))
                    logger.info(f"✅ 일간 라이더 목록 아이템 {len(rider_elements)}개 로드 완료.")
                    
                    # 성공 시 루프 탈출
                    break
                except TimeoutException:
                    logger.warning(f"시도 #{attempt + 1}에서 타임아웃 발생.")
                    if attempt == 0:
                        logger.info("페이지를 새로고침하고 다시 시도합니다.")
                        driver.refresh()
                        time.sleep(5) # 새로고침 후 JS 실행 대기
                    else:
                        logger.error("재시도 후에도 일간 라이더 데이터 항목을 로드하지 못했습니다.")
                        daily_data['daily_riders'] = []
                        return daily_data
            
            logger.info(f"{len(rider_elements)}명의 라이더 데이터를 파싱합니다.")

            for rider_element in rider_elements:
                try:
                    # find_elements를 사용하여 NoSuchElementException을 방지하는 안전한 get_stat 함수
                    def get_stat(stat_name_key):
                        selector = s_rider_list.get(stat_name_key)
                        if not selector: return 0
                        nodes = rider_element.find_elements(By.CSS_SELECTOR, selector)
                        if nodes:
                            return self._get_safe_number(nodes[0].text.strip())
                        return 0
 
                    name_nodes = rider_element.find_elements(By.CSS_SELECTOR, s_rider_list.get('name'))
                    if not name_nodes:
                        logger.warning("라이더 이름을 찾을 수 없어 해당 항목을 건너뜁니다.")
                        continue
                    name = name_nodes[0].text.strip()

                    rider_list.append({
                        'name': name,
                        '완료': get_stat('complete_count'),
                        '거절': get_stat('reject_count'),
                        '배차취소': get_stat('accept_cancel_count'),
                        '배달취소': get_stat('accept_cancel_rider_fault_count'),
                        '아침점심피크': get_stat('morning_count'),
                        '오후논피크': get_stat('afternoon_count'),
                        '저녁피크': get_stat('evening_count'),
                        '심야논피크': get_stat('midnight_count'),
                    })
                except Exception as e:
                    logger.warning(f"라이더 데이터 한 항목을 파싱하는 중 오류: {e}")
                    continue

            daily_data['daily_riders'] = rider_list
        except Exception as e:
            logger.error(f"일간 라이더 데이터 파싱 중 오류 발생: {e}", exc_info=True)
        return daily_data

    def _parse_mission_string(self, text: str):
        """'47/31건 (+3점)' 형태의 문자열을 딕셔너리로 파싱합니다."""
        if not text:
            return {'current': 0, 'target': 0, 'score': '0'}
        
        counts_match = re.search(r'(\d+)/(\d+)건', text)
        score_match = re.search(r'\((.+?)\)', text)
        
        current = int(counts_match.group(1)) if counts_match else 0
        target = int(counts_match.group(2)) if counts_match else 0
        score = score_match.group(1).replace('점', '') if score_match else '0'
        
        return {'current': current, 'target': target, 'score': score}

    def _parse_mission_data(self, driver):
        """SLA 페이지에서 오늘 날짜에 해당하는 미션 데이터를 파싱합니다."""
        mission_data = {}
        try:
            s_mission_table = self.selectors.get('mission_table', {})
            today_str = self._get_mission_date()
            logger.info(f"오늘 날짜({today_str})의 미션 데이터 파싱을 시작합니다.")
            
            wait = WebDriverWait(driver, 10)
            
            container_selector = s_mission_table.get('container')
            if not container_selector:
                logger.warning("미션 테이블 container 선택자가 설정 파일에 없습니다.")
                return {}
            
            # 미션 테이블의 실제 데이터 행이 로드될 때까지 대기
            row_selector = s_mission_table.get('rows')
            full_row_selector = f"{container_selector} {row_selector}"
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, full_row_selector)))

            s_date_cell = s_mission_table.get('date_cell')
            s_score_cell = s_mission_table.get('score_cell')
            s_morning_peak = s_mission_table.get('morning_peak_cell')
            s_afternoon_peak = s_mission_table.get('afternoon_peak_cell')
            s_evening_peak = s_mission_table.get('evening_peak_cell')
            s_midnight_peak = s_mission_table.get('midnight_peak_cell')

            if not all([row_selector, s_date_cell, s_score_cell, s_morning_peak, s_afternoon_peak, s_evening_peak, s_midnight_peak]):
                logger.error("미션 테이블에 필요한 선택자가 설정 파일에 모두 정의되지 않았습니다.")
                return {}

            mission_table_rows = driver.find_elements(By.CSS_SELECTOR, full_row_selector)
            
            found = False
            for row in mission_table_rows:
                try:
                    date_cell = row.find_element(By.CSS_SELECTOR, s_date_cell)
                    if date_cell.text.strip() == today_str:
                        mission_data['일일미션점수'] = row.find_element(By.CSS_SELECTOR, s_score_cell).text.strip()
                        
                        raw_morning = row.find_element(By.CSS_SELECTOR, s_morning_peak).text.strip().replace('\\n', ' ')
                        raw_afternoon = row.find_element(By.CSS_SELECTOR, s_afternoon_peak).text.strip().replace('\\n', ' ')
                        raw_evening = row.find_element(By.CSS_SELECTOR, s_evening_peak).text.strip().replace('\\n', ' ')
                        raw_midnight = row.find_element(By.CSS_SELECTOR, s_midnight_peak).text.strip().replace('\\n', ' ')

                        mission_data['아침점심피크'] = self._parse_mission_string(raw_morning)
                        mission_data['오후논피크'] = self._parse_mission_string(raw_afternoon)
                        mission_data['저녁피크'] = self._parse_mission_string(raw_evening)
                        mission_data['심야논피크'] = self._parse_mission_string(raw_midnight)
                        
                        found = True
                        logger.info(f"✅ {today_str} 미션 데이터 파싱 완료: {mission_data}")
                        break
                except NoSuchElementException:
                    # 행에 특정 셀이 없는 경우가 있을 수 있으므로 경고만 남기고 계속 진행
                    logger.warning("미션 테이블의 한 행에서 특정 셀을 찾지 못했습니다. 건너뜁니다.")
                    continue
                except Exception as e:
                    logger.warning(f"미션 테이블의 한 행을 파싱하는 중 오류 발생: {e}")
                    continue

            if not found:
                logger.warning(f"{today_str}에 해당하는 미션 데이터를 테이블에서 찾을 수 없습니다.")

        except TimeoutException:
            logger.error(f"'{container_selector}' 미션 테이블을 시간 안에 찾지 못했습니다.")
        except Exception as e:
            logger.error(f"'미션 테이블' 파싱 중 예외 발생: {e}", exc_info=True)
        
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

    def collect_all_data(self):
        """
        모든 G-Rider 관련 데이터를 수집, 파싱하고 통합된 딕셔너리로 반환합니다.
        오류 발생 시, 'error' 키를 포함한 딕셔너리를 반환합니다.
        """
        driver = None
        collected_data = {'error': False, 'error_reason': ''}

        try:
            driver = self._get_driver()
            
            # 1. 일간 라이더 데이터 수집
            daily_data = self._parse_daily_rider_data(driver)
            collected_data.update(daily_data)
            
            # 2. 주간/미션 데이터 수집
            driver.get(self.sla_url)
            weekly_data = self._parse_weekly_data(driver)
            collected_data.update(weekly_data)
            
            mission_data = self._parse_mission_data(driver)
            collected_data.update(mission_data)

            # 3. 날씨 정보 가져오기 (오류가 발생해도 전체를 중단시키지 않음)
            try:
                collected_data['weather_info'] = self._get_weather_info_detailed()
            except Exception as e:
                logger.error(f"날씨 정보 수집 실패: {e}")
                collected_data['weather_info'] = "날씨 정보 조회 불가"

            return collected_data

        except Exception as e:
            logger.error(f"전체 데이터 수집 프로세스 실패: {e}", exc_info=True)
            collected_data['error'] = True
            collected_data['error_reason'] = str(e)
            return collected_data
        
        finally:
            if driver:
                driver.quit()
                logger.info("Selenium 드라이버 종료")

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
        grider_data = self.data_collector.collect_all_data()
        
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
            if not isinstance(percentage, (int, float)) or not 0 <= percentage <= 100: 
                return ""
            filled_blocks = round(percentage / 10) # 10칸
            return '🟩' * filled_blocks + '⬜' * (10 - filled_blocks)

        def get_rider_progress_bar(contribution: float) -> str:
            if not isinstance(contribution, (int, float)) or contribution < 0: contribution = 0
            contribution = min(contribution, 100)
            filled_blocks = round(contribution / 20) # 5 blocks total
            return '🟩' * filled_blocks + '⬜' * (5 - filled_blocks)
        
        # 미션 시간 정의
        MISSION_START_TIMES = {
            '아침점심피크': 10,
            '오후논피크': 14,
            '저녁피크': 17,
            '심야논피크': 21
        }
        korea_now = get_korea_time()
        header = "심플 배민 플러스 미션 알리미"

        # 미션 정보 (현재 시간에 따라 동적 표시)
        mission_details = []
        mission_alerts = [] # 미션 부족 알림 저장용
        mission_order = ['아침점심피크', '오후논피크', '저녁피크', '심야논피크']
        mission_emojis_for_summary = {'아침점심피크': '🌅', '오후논피크': '🌇', '저녁피크': '🌃', '심야논피크': '🌙'}
        mission_short_names = {'아침점심피크': '아침점심', '오후논피크': '오후논', '저녁피크': '저녁', '심야논피크': '심야'}
        
        for mission_name in mission_order:
            start_hour = MISSION_START_TIMES.get(mission_name)
            if start_hour is not None and korea_now.hour >= start_hour:
                details = data.get(mission_name)
                if details and isinstance(details, dict):
                    current = details.get('current', 0)
                    target = details.get('target', 0)
                    emoji = mission_emojis_for_summary.get(mission_name, '')
                    
                    status = ""
                    if target > 0:
                        if current >= target:
                            status = " ✅ (달성)"
                        else:
                            shortage = target - current
                            status = f" ❌ ({shortage}건 부족)"
                            short_name = mission_short_names.get(mission_name, mission_name)
                            mission_alerts.append(f"{short_name} {shortage}건")
                            
                    mission_details.append(f"{emoji} {mission_name}: {current}/{target}{status}")
        mission_summary = "\n".join(mission_details)

        # 금일 수행 내역
        all_daily_riders = data.get('daily_riders', []) 
        daily_total_completed = sum(r.get('완료', 0) for r in all_daily_riders)
        daily_total_rejected = sum(r.get('거절', 0) + r.get('배차취소', 0) + r.get('배달취소', 0) for r in all_daily_riders)
        daily_total_for_rate = daily_total_completed + daily_total_rejected
        daily_acceptance_rate = (daily_total_completed / daily_total_for_rate * 100) if daily_total_for_rate > 0 else 100.0
        daily_rider_summary = (
            f"📈 금일 수행 내역\n"
            f"완료: {daily_total_completed}  거절(취소포함): {daily_total_rejected}\n"
            f"수락률: {daily_acceptance_rate:.1f}%\n"
            f"{get_acceptance_progress_bar(daily_acceptance_rate)}"
        )
        
        # 이번주 미션 예상점수
        total_score = data.get('예상총점수', '0')
        quantity_score = data.get('물량점수', '0')
        acceptance_score = data.get('수락률점수', '0')
        weekly_acceptance_rate = float(data.get('수락률', 0))
        weekly_completed = data.get('총완료', 0)
        weekly_rejected = data.get('총거절', 0)
        weekly_summary = (
            f"📊 이번주 미션 예상점수\n"
            f"총점: {total_score}점 (물량:{quantity_score}, 수락률:{acceptance_score})\n"
            f"완료: {weekly_completed}  거절(취소포함): {weekly_rejected}\n"
            f"수락률: {weekly_acceptance_rate:.1f}%\n"
            f"{get_acceptance_progress_bar(weekly_acceptance_rate)}"
        )

        # 라이더 순위 (상세)
        rider_ranking_summary = ""
        if all_daily_riders:
            active_riders = sorted([r for r in all_daily_riders if r.get('완료', 0) > 0], key=lambda x: x.get('완료', 0), reverse=True)
            total_daily_count = sum(r.get('완료', 0) for r in active_riders)
            
            if active_riders:
                ranking_list = [f"🏆 라이더 순위 (운행: {len(active_riders)}명)"]
                for i, rider in enumerate(active_riders[:5]): # Top 5
                    rank_icon = ["🥇", "🥈", "🥉"][i] if i < 3 else f"  {i+1}."
                    contribution = (rider.get('완료', 0) / total_daily_count * 100) if total_daily_count > 0 else 0
                    rider_name = rider.get('name', '이름없음').replace('(본인)', '').strip()
                    
                    rider_completed = rider.get('완료', 0)
                    rider_rejected = rider.get('거절', 0)
                    rider_canceled = rider.get('배차취소', 0) + rider.get('배달취소', 0)
                    rider_fail = rider_rejected + rider_canceled
                    rider_acceptance_rate = (rider_completed / (rider_completed + rider_fail) * 100) if (rider_completed + rider_fail) > 0 else 100.0
                    
                    # 시간대별 실적 문자열 생성
                    peak_emojis = {'아침점심피크': '🌅', '오후논피크': '🌇', '저녁피크': '🌃', '심야논피크': '🌙'}
                    peak_counts = []
                    for peak_name, peak_emoji in peak_emojis.items():
                        count = rider.get(peak_name, 0)
                        peak_counts.append(f"{peak_emoji}{count}")
                    peak_counts_str = ' '.join(peak_counts)

                    rider_details = (
                        f"{rank_icon} {rider_name} | {get_rider_progress_bar(contribution)} {contribution:.1f}%\n"
                        f"    총 {rider_completed}건 ({peak_counts_str})\n"
                        f"    수락률: {rider_acceptance_rate:.1f}% (거절:{rider_rejected}, 취소:{rider_canceled})"
                    )
                    ranking_list.append(rider_details)
                rider_ranking_summary = "\n".join(ranking_list)

        weather_summary = data.get('weather_info', '날씨 정보 조회 불가')

        # 특이사항 (미션 부족 알림)
        alert_summary = ""
        if mission_alerts:
            alert_summary = "⚠️ 미션 부족: " + ", ".join(mission_alerts)
        
        message_parts = [
            header,
            mission_summary,
            daily_rider_summary,
            weather_summary,
            weekly_summary,
            rider_ranking_summary,
            alert_summary,
        ]
        return "\n\n".join(filter(None, message_parts))

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