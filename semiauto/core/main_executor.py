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
from xml.etree import ElementTree as ET  # 한국천문연구원 API용
from dotenv import load_dotenv
import sys

# 프로젝트 루트를 Python 경로에 추가하여 weather_service 모듈 임포트 허용
# 이 스크립트(main_executor.py)는 semiauto/core/ 안에 있으므로,
# 프로젝트 루트(Baese/)로 가려면 세 번 상위 디렉토리로 이동해야 합니다.
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# 이제 weather_service를 import 할 수 있습니다.
try:
    from weather_service import WeatherService
except ImportError:
    # weather_service.py가 없는 경우를 대비한 예외 처리
    class WeatherService:
        def get_weather(self):
            return {"error": "WeatherService 모듈을 찾을 수 없습니다."}


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
        
        data = {'template_object': json.dumps(template_object)}
        
        try:
            response = requests.post(self.base_url, headers=headers, data=data)
            response.raise_for_status()
            logger.info("✅ 카카오톡 메시지 전송 성공")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ 카카오톡 메시지 전송 실패: {e.response.text if e.response else e}")
            return None

class GriderDataCollector:
    """G라이더 웹사이트 데이터 수집 클래스"""
    
    def __init__(self):
        self.grider_id = os.getenv('GRIDER_ID')
        self.grider_password = os.getenv('GRIDER_PASSWORD')
        self.base_url = "https://jangboo.grider.ai"
        self.dashboard_url = f"{self.base_url}/dashboard"
        self.sla_url = f"{self.base_url}/dashboard/sla"
        self.selectors = self._load_all_selectors()
        
    def _load_all_selectors(self):
        """selectors 폴더의 모든 .json 파일을 읽어 딕셔너리로 반환합니다."""
        selectors = {}
        current_script_path = os.path.dirname(os.path.abspath(__file__))
        selectors_dir = os.path.join(current_script_path, '..', 'selectors')
        
        for filename in os.listdir(selectors_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(selectors_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        key = filename.replace('.json', '')
                        selectors[key] = json.load(f)
                        logger.info(f"선택자 파일 로드 완료: {filename}")
                except Exception as e:
                    logger.error(f"선택자 파일 '{filename}' 로드 실패: {e}")
        return selectors

    def _get_driver(self):
        """Selenium WebDriver 인스턴스를 반환합니다."""
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service as ChromeService
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.options import Options

        if not self.grider_id or not self.grider_password:
             raise Exception("G라이더 로그인 정보가 없습니다.")

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        try:
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_page_load_timeout(30)
            driver.set_window_size(1920, 1080)
            logger.info("✅ Chrome WebDriver 초기화 성공 (webdriver-manager)")
            return driver
        except Exception as e:
            logger.error(f"❌ Chrome WebDriver 초기화 실패: {e}", exc_info=True)
            raise

    def _login(self, driver):
        """G라이더 웹사이트에 로그인합니다."""
        try:
            s_login = self.selectors.get('login', {})
            login_url = self.base_url + s_login.get('url_path', '/')
            driver.get(login_url)
            
            wait = WebDriverWait(driver, 10)
            
            id_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, s_login.get('id_input'))))
            id_input.send_keys(self.grider_id)
            
            pw_input = driver.find_element(By.CSS_SELECTOR, s_login.get('pw_input'))
            pw_input.send_keys(self.grider_password)
            
            login_button = driver.find_element(By.CSS_SELECTOR, s_login.get('login_button'))
            login_button.click()
            
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, s_login.get('login_success_indicator'))))
            logger.info("✅ G라이더 로그인 성공")
            return True
            
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"G라이더 로그인 실패 (요소 찾기 실패 또는 타임아웃): {e}", exc_info=True)
            self._save_page_source(driver, "login_failure")
            return False
        except Exception as e:
            logger.error(f"G라이더 로그인 중 예외 발생: {e}", exc_info=True)
            self._save_page_source(driver, "login_exception")
            return False

    def _save_page_source(self, driver, filename_prefix):
        """디버깅을 위해 현재 페이지 소스를 파일에 저장하고 로그로도 출력합니다."""
        try:
            # 1. 파일에 저장
            timestamp = datetime.now(KST).strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_{timestamp}.html"
            
            debug_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'debug')
            os.makedirs(debug_dir, exist_ok=True)
            filepath = os.path.join(debug_dir, filename)
            
            page_source = driver.page_source
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(page_source)
            logger.info(f"📄 디버깅을 위해 페이지 소스를 저장했습니다: {filepath}")

            # 2. 로그로 출력
            logger.info(f"PAGE_SOURCE_START\n{page_source}\nPAGE_SOURCE_END")

        except Exception as e:
            logger.error(f"페이지 소스 저장/로깅 실패: {e}", exc_info=True)


    def _get_today_date(self):
        """한국시간 기준 오늘 날짜를 'YYYY-MM-DD' 형식으로 반환합니다."""
        return get_korea_time().strftime('%Y-%m-%d')

    def _parse_weekly_data(self, driver):
        """대시보드에서 주간 요약 점수와 통계 데이터를 파싱합니다."""
        weekly_data = {}
        try:
            wait = WebDriverWait(driver, 20)
            s_summary = self.selectors.get('weekly_summary', {})

            summary_container_selector = s_summary.get('summary', {}).get('container')
            if summary_container_selector:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, summary_container_selector)))
                weekly_data['총점'] = self._get_safe_number(driver.find_element(By.CSS_SELECTOR, s_summary['summary']['total_score']).text)
                weekly_data['물량점수'] = self._get_safe_number(driver.find_element(By.CSS_SELECTOR, s_summary['summary']['quantity_score']).text)
                weekly_data['수락률점수'] = self._get_safe_number(driver.find_element(By.CSS_SELECTOR, s_summary['summary']['acceptance_score']).text)
                logger.info(f"✅ 예상 점수 카드 파싱 완료: {weekly_data}")
            else:
                logger.warning("주간 요약 점수 선택자를 찾을 수 없습니다.")

            stats_container_selector = s_summary.get('stats', {}).get('container')
            if stats_container_selector:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, stats_container_selector)))
                total_completed = self._get_safe_number(driver.find_element(By.CSS_SELECTOR, s_summary['stats']['total_completed']).text)
                total_rejected = self._get_safe_number(driver.find_element(By.CSS_SELECTOR, s_summary['stats']['total_rejected']).text)
                acceptance_rate_text = driver.find_element(By.CSS_SELECTOR, s_summary['stats']['acceptance_rate']).text
                acceptance_rate = float(re.search(r'\d+\.?\d*', acceptance_rate_text).group()) if re.search(r'\d+\.?\d*', acceptance_rate_text) else 0.0
                
                weekly_data['총완료'] = total_completed
                weekly_data['총거절'] = total_rejected
                weekly_data['수락률'] = acceptance_rate
                logger.info(f"✅ 주간 통계 파싱 완료: {weekly_data}")
            else:
                logger.warning("주간 통계 선택자를 찾을 수 없습니다.")

        except Exception as e:
            logger.error(f"주간 요약/통계 데이터 파싱 중 오류 발생: {e}", exc_info=True)
            self._save_page_source(driver, "weekly_summary_parsing_error")
        
        return weekly_data

    def _parse_daily_rider_data(self, driver):
        s_daily = self.selectors['daily_data']
        wait = WebDriverWait(driver, 20)
        daily_data = {'riders': [], 'total_completed': 0, 'total_rejected': 0, 'total_canceled': 0}

        total_container_selector = s_daily.get('daily_total_container')
        if total_container_selector:
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, total_container_selector)))
                
                daily_data['total_completed'] = self._get_safe_number(driver.find_element(By.CSS_SELECTOR, s_daily.get('daily_total_complete')).text)
                daily_data['total_rejected'] = self._get_safe_number(driver.find_element(By.CSS_SELECTOR, s_daily.get('daily_total_reject')).text)
                cancel_dispatch = self._get_safe_number(driver.find_element(By.CSS_SELECTOR, s_daily.get('daily_total_accept_cancel')).text)
                cancel_delivery = self._get_safe_number(driver.find_element(By.CSS_SELECTOR, s_daily.get('daily_total_accept_cancel_rider_fault')).text)
                daily_data['total_canceled'] = cancel_dispatch + cancel_delivery
                logger.info(f"✅ 일일 총계 파싱 완료: {daily_data}")

            except Exception as e:
                logger.error(f"일일 총계 파싱 실패: {e}", exc_info=True)
                self._save_page_source(driver, "daily_total_parsing_error")


        try:
            rider_list_container_selector = s_daily.get('container')
            rider_item_selector = s_daily.get('item')
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, rider_list_container_selector)))
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, f"{rider_list_container_selector} {rider_item_selector}")))
            time.sleep(1) 

            rider_elements = driver.find_elements(By.CSS_SELECTOR, rider_item_selector)
            logger.info(f"✅ 일간 라이더 목록 아이템 {len(rider_elements)}개 로드 완료. 파싱을 시작합니다.")

            for rider_element in rider_elements:
                try:
                    name_element = rider_element.find_element(By.CSS_SELECTOR, s_daily.get('name'))
                    full_text = name_element.text
                    child_spans = name_element.find_elements(By.TAG_NAME, 'span')
                    name_only = full_text
                    for span in child_spans:
                        name_only = name_only.replace(span.text, '')
                    name = name_only.strip()

                    if not name:
                        logger.warning(f"라이더 이름이 비어있어 건너뜁니다.")
                        continue
                    
                    rider_data = {'name': name}
                    rider_data['완료'] = self._get_safe_number(rider_element.find_element(By.CSS_SELECTOR, s_daily.get('complete_count')).text)
                    rider_data['거절'] = self._get_safe_number(rider_element.find_element(By.CSS_SELECTOR, s_daily.get('reject_count')).text)
                    rider_data['배차취소'] = self._get_safe_number(rider_element.find_element(By.CSS_SELECTOR, s_daily.get('accept_cancel_count')).text)
                    rider_data['배달취소'] = self._get_safe_number(rider_element.find_element(By.CSS_SELECTOR, s_daily.get('accept_cancel_rider_fault_count')).text)
                    rider_data['오전'] = self._get_safe_number(rider_element.find_element(By.CSS_SELECTOR, s_daily.get('morning_count')).text)
                    rider_data['오후'] = self._get_safe_number(rider_element.find_element(By.CSS_SELECTOR, s_daily.get('afternoon_count')).text)
                    rider_data['저녁'] = self._get_safe_number(rider_element.find_element(By.CSS_SELECTOR, s_daily.get('evening_count')).text)
                    rider_data['심야'] = self._get_safe_number(rider_element.find_element(By.CSS_SELECTOR, s_daily.get('midnight_count')).text)

                    total_actions = sum(v for k, v in rider_data.items() if k != 'name')

                    if total_actions > 0:
                        daily_data['riders'].append(rider_data)
                    else:
                        logger.info(f"라이더 '{name}'는 실적이 없어 데이터 수집에서 제외합니다.")

                except NoSuchElementException:
                    logger.warning(f"라이더 항목 내에서 일부 데이터를 찾지 못해 건너뜁니다.")
                    continue
                except Exception as e:
                    name_for_log = '알 수 없음'
                    try:
                        name_for_log = rider_element.find_element(By.CSS_SELECTOR, s_daily.get('name')).text.strip()
                    except:
                        pass
                    logger.warning(f"라이더 '{name_for_log}'의 데이터 파싱 중 예외 발생: {e}", exc_info=True)
                    continue
            
            daily_data['riders'].sort(key=lambda x: x.get('완료', 0), reverse=True)
            logger.info(f"✅ {len(daily_data['riders'])}명의 활동 라이더 데이터 파싱 완료.")

        except TimeoutException:
            logger.error("일일 라이더 목록 로드 시간 초과.", exc_info=True)
            self._save_page_source(driver, "daily_rider_timeout")
        except Exception as e:
            logger.error(f"일간 라이더 데이터 파싱 중 심각한 오류 발생: {e}", exc_info=True)
            self._save_page_source(driver, "daily_rider_parsing_error")
            daily_data.setdefault('riders', [])
        return daily_data

    def _parse_mission_data(self, driver):
        mission_data = {}
        try:
            s_mission_table = self.selectors.get('mission_table', {})
            mission_data['오전피크'] = self._get_safe_number(driver.find_element(By.CSS_SELECTOR, s_mission_table.get('morning')).text)
            mission_data['오후피크'] = self._get_safe_number(driver.find_element(By.CSS_SELECTOR, s_mission_table.get('afternoon')).text)
            mission_data['저녁피크'] = self._get_safe_number(driver.find_element(By.CSS_SELECTOR, s_mission_table.get('evening')).text)
            mission_data['심야피크'] = self._get_safe_number(driver.find_element(By.CSS_SELECTOR, s_mission_table.get('midnight')).text)
            logger.info(f"✅ 피크타임 미션 데이터 파싱 완료: {mission_data}")
        except Exception as e:
            logger.error(f"미션 데이터 파싱 중 예외 발생: {e}", exc_info=True)
            self._save_page_source(driver, "mission_data_parsing_error")
        return mission_data

    def _perform_login(self):
        driver = None
        try:
            driver = self._get_driver()
            if not self._login(driver):
                raise Exception("로그인 함수 실패")
            return driver
        except Exception as e:
            logger.error(f"로그인 절차 실패: {e}", exc_info=True)
            if driver:
                driver.quit()
            return None

    def _get_safe_number(self, text):
        if not isinstance(text, str):
            return 0
        text = text.strip()
        if text in ['N/A', '-', '']:
            return 0
        text = text.replace('점', '').replace('건', '').replace('회', '')
        numbers = re.findall(r'[-+]?\d*\.\d+|\d+', text)
        if numbers:
            try:
                return int(float(numbers[0]))
            except (ValueError, IndexError):
                return 0
        return 0

    def collect_all_data(self):
        """모든 데이터를 수집하고 구조화합니다."""
        all_data = {
            "daily_data": {},
            "weekly_summary": {},
            "mission_data": {},
            "metadata": {}
        }
        self.driver = None

        try:
            self.driver = self._perform_login()
            if not self.driver:
                raise Exception("G라이더 로그인 실패")

            all_data['weekly_summary'] = self._parse_weekly_data(self.driver)
            all_data['daily_data'] = self._parse_daily_rider_data(self.driver)
            all_data['mission_data'] = self._parse_mission_data(self.driver)
            
            all_data['metadata'] = {
                'report_date': get_korea_time().strftime('%Y-%m-%d'),
                'error': None
            }
        except Exception as e:
            logger.error(f"전체 데이터 수집 프로세스 실패: {e}", exc_info=True)
            if self.driver:
                self._save_page_source(self.driver, "collect_all_data_exception")
            all_data['metadata']['error'] = str(e)
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("WebDriver를 종료했습니다.")
        
        return all_data

class GriderAutoSender:
    """G라이더 자동화 실행 및 카카오톡 전송 클래스"""
    
    def __init__(self, rest_api_key=None, refresh_token=None):
        self.collector = GriderDataCollector()
        self.kakao_sender = None
        if rest_api_key and refresh_token:
            token_manager = TokenManager(rest_api_key, refresh_token)
            access_token = token_manager.get_valid_token()
            if access_token:
                self.kakao_sender = KakaoSender(access_token)

    def save_dashboard_data(self, data: dict):
        try:
            current_script_path = os.path.dirname(os.path.abspath(__file__))
            save_path = os.path.join(current_script_path, '..', 'dashboard', 'api', 'latest-data.json')
            
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logger.info(f"대시보드 데이터 저장 완료: {save_path}")
            
            history_dir = os.path.join(current_script_path, '..', 'dashboard', 'api', 'history')
            os.makedirs(history_dir, exist_ok=True)
            history_filename = f"history-{get_korea_time().strftime('%Y-%m-%d')}.json"
            history_filepath = os.path.join(history_dir, history_filename)
            with open(history_filepath, 'w', encoding='utf-8') as f:
                 json.dump(data, f, ensure_ascii=False, indent=4)
            logger.info(f"히스토리 데이터 저장 완료: {history_filepath}")

        except Exception as e:
            logger.error(f"대시보드 데이터 저장 실패: {e}", exc_info=True)

    def send_report(self):
        data = self.collector.collect_all_data()
        self.save_dashboard_data(data)
        
        if data.get('metadata', {}).get('error'):
            logger.error(f"데이터 수집 중 오류가 발생하여 리포트를 전송하지 않습니다: {data['metadata']['error']}")
            return
        
        message = self.format_message(data)
        if self.kakao_sender:
            self.kakao_sender.send_text_message(message)
        else:
            logger.error("카카오톡 발신기가 초기화되지 않아 메시지를 보낼 수 없습니다.")

    def format_message(self, data):
        try:
            template_path = os.path.join(os.path.dirname(__file__), '..', 'message_template.md')
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
        except FileNotFoundError:
            logger.error(f"메시지 템플릿 파일을 찾을 수 없습니다: semiauto/message_template.md")
            return "오류: 메시지 템플릿 파일을 찾을 수 없습니다."

        daily_data = data.get('daily_data', {})
        weekly_summary_data = data.get('weekly_summary', {})
        mission_data = data.get('mission_data', {})
        riders_data = daily_data.get('riders', [])

        daily_completed = daily_data.get('total_completed', 0)
        daily_rejected_and_canceled = daily_data.get('total_rejected', 0) + daily_data.get('total_canceled', 0)
        total_daily_for_rate = daily_completed + daily_rejected_and_canceled
        daily_acceptance_rate = (daily_completed / total_daily_for_rate * 100) if total_daily_for_rate > 0 else 0.0
        
        mission_summary = self._format_mission_summary(mission_data)
        daily_acceptance_bar = self._format_progress_bar(daily_acceptance_rate)
        weather_summary = self._format_weather_summary()
        weekly_acceptance_bar = self._format_progress_bar(weekly_summary_data.get('수락률', 0.0))
        rider_rankings, active_rider_count = self._format_rider_rankings(riders_data)
        mission_shortage_summary = self._format_mission_shortage_summary(mission_data)

        return template.format(
            mission_summary=mission_summary,
            daily_completed=daily_completed,
            daily_rejected_and_canceled=daily_rejected_and_canceled,
            daily_acceptance_rate=f"{daily_acceptance_rate:.1f}",
            daily_acceptance_bar=daily_acceptance_bar,
            weather_summary=weather_summary,
            weekly_total_score=weekly_summary_data.get('총점', 0),
            weekly_delivery_score=weekly_summary_data.get('물량점수', 0),
            weekly_acceptance_score=weekly_summary_data.get('수락률점수', 0),
            weekly_completed=weekly_summary_data.get('총완료', 0),
            weekly_rejected_and_canceled=weekly_summary_data.get('총거절', 0),
            weekly_acceptance_rate=f"{weekly_summary_data.get('수락률', 0.0):.1f}",
            weekly_acceptance_bar=weekly_acceptance_bar,
            active_rider_count=active_rider_count,
            rider_rankings=rider_rankings,
            mission_shortage_summary=mission_shortage_summary
        )

    def _format_progress_bar(self, percentage, length=10):
        if not isinstance(percentage, (int, float)):
            percentage = 0
        fill_count = int(round(percentage / (100 / length)))
        return '🟩' * fill_count + '⬜' * (length - fill_count)

    def _format_mission_summary(self, missions):
        lines = []
        if not missions: return "피크타임 정보 없음"
        
        total_peak_deliveries = sum(missions.values())
        lines.append(f"📈 피크타임 총 {total_peak_deliveries}건 완료")
        
        for mission_name, count in missions.items():
            lines.append(f" - {mission_name}: {count}건")
        return "\n".join(lines)
        
    def _format_weather_summary(self):
        try:
            weather_service = WeatherService()
            weather_info = weather_service.get_weather()
            if weather_info and 'error' not in weather_info:
                return (f"🌍 오늘의 날씨 ({weather_info['source']})\n"
                        f" 🌅 오전: {weather_info['am_temp_min']}~{weather_info['am_temp_max']}°C, 강수확률 {weather_info['am_rain_prob']}%\n"
                        f" 🌇 오후: {weather_info['pm_temp_min']}~{weather_info['pm_temp_max']}°C, 강수확률 {weather_info['pm_rain_prob']}%")
        except NameError:
             logger.warning("WeatherService를 찾을 수 없어 날씨 정보를 표시할 수 없습니다.")
        except Exception as e:
            logger.warning(f"날씨 정보 조회 실패: {e}")
        return "🌍 날씨 정보 (조회 실패)"

    def _format_rider_rankings(self, riders):
        if not riders:
            return "운행 중인 라이더 정보가 없습니다.", 0

        active_rider_count = len(riders)
        top_riders = riders[:5]
        
        top_rider_completed = top_riders[0].get('완료', 0) if top_riders else 0

        rank_icons = ["🥇", "🥈", "🥉"]
        lines = []
        for i, rider in enumerate(top_riders):
            name = rider.get('name', 'N/A')
            completed = rider.get('완료', 0)
            
            rank_str = f"**{rank_icons[i]} {name}**" if i < len(rank_icons) else f"  **{i+1}. {name}**"
            
            progress_percent = (completed / top_rider_completed * 100) if top_rider_completed > 0 else 0
            progress_bar = self._format_progress_bar(progress_percent, 5)
            
            rejected = rider.get('거절', 0)
            canceled = rider.get('배차취소', 0) + rider.get('배달취소', 0)
            total_decisions = completed + rejected + canceled
            acceptance_rate = (completed / total_decisions * 100) if total_decisions > 0 else 100

            lines.append(
                f"{rank_str} | {progress_bar} {progress_percent:.1f}%\n"
                f"    총 {completed}건 (🌅{rider.get('오전', 0)} 🌇{rider.get('오후', 0)} 🌃{rider.get('저녁', 0)} 🌙{rider.get('심야', 0)})\n"
                f"    수락률: {acceptance_rate:.1f}% (거절:{rejected}, 취소:{canceled})"
            )
        return "\n\n".join(lines), active_rider_count

    def _format_mission_shortage_summary(self, missions):
        if not missions: return "미션 정보 없음"
        total_peak_deliveries = sum(missions.values())
        return f"총 {total_peak_deliveries}건의 피크타임 배달을 완료했습니다."

def main():
    load_dotenv()
    
    holiday_api_key = os.getenv("HOLIDAY_API_KEY")
    if holiday_api_key:
        # 이 변수는 전역 holiday_checker 인스턴스에 의해 사용됩니다.
        pass
    else:
        logging.warning("HOLIDAY_API_KEY가 설정되지 않아 공휴일 정보를 로드할 수 없습니다.")

    logging.info("==================================================")
    logging.info(" G-Rider 자동화 스크립트 시작")
    logging.info("==================================================")
    
    executor = GriderAutoSender(
        rest_api_key=os.getenv("KAKAO_REST_API_KEY"),
        refresh_token=os.getenv("KAKAO_REFRESH_TOKEN")
    )
    executor.send_report()
    
    logging.info("==================================================")
    logging.info(" G-Rider 자동화 스크립트 종료")
    logging.info("==================================================")

if __name__ == "__main__":
    main()
