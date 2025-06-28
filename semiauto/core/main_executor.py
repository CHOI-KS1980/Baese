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
import sys

# 프로젝트 루트를 Python 경로에 추가하여 weather_service 모듈 임포트 허용
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

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
        # 'semiauto/selectors' 디렉토리의 절대 경로를 만듭니다.
        # 이 스크립트(main_executor.py)의 위치를 기준으로 경로를 설정합니다.
        current_script_path = os.path.dirname(os.path.abspath(__file__))
        selectors_dir = os.path.join(current_script_path, '..', 'selectors')
        
        for filename in os.listdir(selectors_dir):
            if filename.endswith('.json'):
                # 파일의 전체 경로를 만듭니다.
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
            # webdriver-manager를 사용하여 ChromeDriver 자동 설치 및 로드
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
            
            # 로그인 후 대시보드 페이지의 특정 요소가 나타날 때까지 대기
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, s_login.get('login_success_indicator'))))
            logger.info("✅ G라이더 로그인 성공")
            return True
            
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"G라이더 로그인 실패 (요소 찾기 실패 또는 타임아웃): {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"G라이더 로그인 중 예외 발생: {e}", exc_info=True)
            return False

    def _get_mission_date(self):
        """오늘 날짜를 기반으로 미션 날짜를 계산합니다 (공휴일 등 고려)."""
        korea_time = get_korea_time()
        mission_time = korea_time - timedelta(hours=6)
        return mission_time.strftime('%Y-%m-%d')

    def _get_today_date(self):
        """한국시간 기준 오늘 날짜를 'YYYY-MM-DD' 형식으로 반환합니다."""
        return get_korea_time().strftime('%Y-%m-%d')

    def _parse_weekly_data(self, driver):
        """대시보드에서 주간 요약 점수와 통계 데이터를 파싱합니다."""
        weekly_data = {}
        try:
            wait = WebDriverWait(driver, 20)
            s_summary = self.selectors.get('weekly_summary', {})

            # 1. 주간 요약 점수 파싱
            summary_container_selector = s_summary.get('summary', {}).get('container')
            if summary_container_selector:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, summary_container_selector)))
                weekly_data['총점'] = self._get_safe_number(driver.find_element(By.CSS_SELECTOR, s_summary['summary']['total_score']).text)
                weekly_data['물량점수'] = self._get_safe_number(driver.find_element(By.CSS_SELECTOR, s_summary['summary']['quantity_score']).text)
                weekly_data['수락률점수'] = self._get_safe_number(driver.find_element(By.CSS_SELECTOR, s_summary['summary']['acceptance_score']).text)
                logger.info(f"✅ 예상 점수 카드 파싱 완료: {weekly_data}")
            else:
                logger.warning("주간 요약 점수 선택자를 찾을 수 없습니다.")

            # 2. 주간 통계 파싱 (총 완료, 거절, 수락률)
            stats_container_selector = s_summary.get('stats', {}).get('container')
            if stats_container_selector:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, stats_container_selector)))
                total_completed = self._get_safe_number(driver.find_element(By.CSS_SELECTOR, s_summary['stats']['total_completed']).text)
                total_rejected = self._get_safe_number(driver.find_element(By.CSS_SELECTOR, s_summary['stats']['total_rejected']).text)
                acceptance_rate_text = driver.find_element(By.CSS_SELECTOR, s_summary['stats']['acceptance_rate']).text
                acceptance_rate = float(re.search(r'\d+\.?\d*', acceptance_rate_text).group()) if re.search(r'\d+\.?\d*', acceptance_rate_text) else 0.0
                
                weekly_data['총완료'] = total_completed
                weekly_data['총거절'] = total_rejected # 주간 총 거절은 취소 포함된 값으로 추정
                weekly_data['수락률'] = acceptance_rate
                logger.info(f"✅ 주간 통계 파싱 완료: {weekly_data}")
            else:
                logger.warning("주간 통계 선택자를 찾을 수 없습니다.")

        except Exception as e:
            logger.error(f"주간 요약/통계 데이터 파싱 중 오류 발생: {e}", exc_info=True)
        
        return weekly_data

    def _parse_daily_rider_data(self, driver):
        """대시보드에서 일간 라이더 데이터를 파싱합니다."""
        s_daily = self.selectors['daily_data']
        wait = WebDriverWait(driver, 20)
        daily_data = {'riders': [], 'total_completed': 0, 'total_rejected': 0, 'total_canceled': 0}

        # 일일 총계 파싱
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

        # 라이더 목록 파싱
        try:
            rider_list_container_selector = s_daily.get('container')
            rider_item_selector = s_daily.get('item')
            # 컨테이너와 최소 1개의 아이템이 로드될 때까지 대기
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, rider_list_container_selector)))
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, f"{rider_list_container_selector} {rider_item_selector}")))
            time.sleep(1) # 동적 컨텐츠 렌더링을 위한 추가 대기

            rider_elements = driver.find_elements(By.CSS_SELECTOR, rider_item_selector)
            logger.info(f"✅ 일간 라이더 목록 아이템 {len(rider_elements)}개 로드 완료. 파싱을 시작합니다.")

            for rider_element in rider_elements:
                try:
                    name_element = rider_element.find_element(By.CSS_SELECTOR, s_daily.get('name'))
                    # 이름 추출 로직 수정: 자식 요소의 텍스트를 제거하여 순수 텍스트 노드만 남김
                    full_text = name_element.text
                    child_spans = name_element.find_elements(By.TAG_NAME, 'span')
                    name_only = full_text
                    for span in child_spans:
                        name_only = name_only.replace(span.text, '')
                    name = name_only.strip()

                    if not name:
                        logger.warning(f"라이더 이름이 비어있어 건너뜁니다. 해당 행 HTML: {rider_element.get_attribute('outerHTML')}")
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
                    logger.warning(f"라이더 항목 내에서 일부 데이터(예: 이름)를 찾지 못해 건너뜁니다. 해당 행 HTML: {rider_element.get_attribute('outerHTML')}")
                    continue
                except Exception as e:
                    name_for_log = '알 수 없음'
                    try:
                        name_for_log = rider_element.find_element(By.CSS_SELECTOR, s_daily.get('name')).text.strip()
                    except:
                        pass
                    logger.warning(f"라이더 '{name_for_log}'의 데이터 파싱 중 예외 발생: {e}", exc_info=True)
                    continue
            
            daily_data['riders'] = daily_data['riders'][:5] # 상위 5명만 유지
            logger.info(f"✅ {len(daily_data['riders'])}명의 활동 라이더 데이터 파싱 완료.")

        except TimeoutException:
            logger.error("미션 데이터 테이블 로드 시간 초과. 현재 페이지 소스를 로그에 기록합니다.", exc_info=True)
            logger.error(f"PAGE_SOURCE_START\n{driver.page_source}\nPAGE_SOURCE_END")
        except Exception as e:
            logger.error(f"일간 라이더 데이터 파싱 중 심각한 오류 발생: {e}", exc_info=True)
            daily_data.setdefault('riders', [])
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
            
            # 피크 타임 데이터는 대시보드에 이미 로드되어 있으므로, 바로 파싱 시작
            mission_data['오전피크'] = self._get_safe_number(driver.find_element(By.CSS_SELECTOR, s_mission_table.get('morning')).text)
            mission_data['오후피크'] = self._get_safe_number(driver.find_element(By.CSS_SELECTOR, s_mission_table.get('afternoon')).text)
            mission_data['저녁피크'] = self._get_safe_number(driver.find_element(By.CSS_SELECTOR, s_mission_table.get('evening')).text)
            mission_data['심야피크'] = self._get_safe_number(driver.find_element(By.CSS_SELECTOR, s_mission_table.get('midnight')).text)

        except Exception as e:
            logger.error(f"미션 데이터 파싱 중 예외 발생: {e}", exc_info=True)
            # 페이지 소스 로깅은 타임아웃 외의 다른 예외에서도 유용할 수 있음
            logger.error(f"PAGE_SOURCE_START\\n{driver.page_source}\\nPAGE_SOURCE_END")

        return mission_data

    def _get_weather_info_detailed(self, location="서울"):
        """기상청 RSS 피드에서 상세 날씨 정보를 가져옵니다."""
        try:
            # RSS 피드는 구조가 불안정할 수 있으므로, XML 전체를 가져와서 파싱합니다.
            rss_url = "https://www.kma.go.kr/weather/forecast/mid-term-rss3.jsp?stnId=109"
            response = requests.get(rss_url, timeout=10)
            response.raise_for_status()

            # XML 내용에서 불필요한 공백과 줄바꿈을 제거합니다.
            xml_content = response.content.decode('utf-8').strip()
            
            # XML 파싱을 시도합니다.
            root = ET.fromstring(xml_content)
            
            # 'location' 태그를 직접 찾습니다. RSS 구조가 변경되어도 유연하게 대처하기 위함입니다.
            # findall('.//location') 을 통해 전체 XML 문서에서 city 이름이 일치하는 location을 찾습니다.
            location_element = root.find(f".//location[city='{location}']")

            if location_element is None:
                logger.warning(f"날씨 정보에서 '{location}' 지역을 찾을 수 없습니다.")
                return None

            # 해당 지역의 첫 번째 데이터(가장 가까운 예보)를 가져옵니다.
            data_element = location_element.find('data')
            if data_element is None:
                logger.warning(f"'{location}' 지역의 날씨 data 요소를 찾을 수 없습니다.")
                return None
            
            # 오전/오후 날씨, 최저/최고 기온 추출
            am_weather = data_element.find('wfAm').text
            pm_weather = data_element.find('wfPm').text
            temp_min = data_element.find('tmn').text
            temp_max = data_element.find('tmx').text

            # 아이콘 매핑
            icon_map = {
                '맑음': '☀️', '구름많음': '☁️', '흐림': '🌥️',
                '비': '🌧️', '눈': '🌨️', '소나기': '🌦️'
            }
            am_icon = icon_map.get(am_weather, '-')
            pm_icon = icon_map.get(pm_weather, '-')

            return {
                'am_icon': am_icon, 'am_weather': am_weather, 'pm_icon': pm_icon, 'pm_weather': pm_weather,
                'temp_min': temp_min, 'temp_max': temp_max
            }

        except ET.ParseError as e:
            logger.error(f"날씨 정보 XML 파싱 실패. 원본 내용을 로그에 기록합니다.", exc_info=True)
            logger.error(f"XML_CONTENT_START\\n{xml_content}\\nXML_CONTENT_END")
            return None
        except Exception as e:
            logger.error(f"상세 날씨 정보를 가져오는 중 오류 발생: {e}", exc_info=True)
            return None

    def _perform_login(self):
        """로그인 절차를 수행하고 성공 시 드라이버를, 실패 시 None을 반환합니다."""
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
        """문자열에서 숫자만 추출하여 정수로 변환합니다. 변환 실패 시 0을 반환합니다."""
        if not isinstance(text, str):
            return 0
        
        text = text.strip()
        # 'N/A', '-', 등 숫자 변환이 불가능한 경우를 처리
        if text in ['N/A', '-', '']:
            return 0
            
        # '점', '건', '회' 등 단위 제거
        text = text.replace('점', '').replace('건', '').replace('회', '')
        
        # 정규표현식을 사용하여 숫자 부분만 추출 (소수점도 고려)
        numbers = re.findall(r'[-+]?\d*\.\d+|\d+', text)
        
        if numbers:
            try:
                # 첫 번째로 찾은 숫자를 정수로 변환
                return int(float(numbers[0]))
            except (ValueError, IndexError):
                return 0
        return 0

    def collect_all_data(self):
        """모든 데이터를 수집하고 종합하여 반환합니다."""
        final_data = {}
        self.driver = None # 드라이버 인스턴스를 클래스 속성으로 초기화
        
        try:
            # final_data['weather_info'] = self._get_weather_info_detailed() # 날씨 조회 임시 비활성화
            self.driver = self._perform_login()
            if not self.driver:
                raise Exception("G라이더 로그인 실패")

            # 모든 데이터는 로그인 후의 대시보드에서 수집
            daily_data = self._parse_daily_rider_data(self.driver)
            weekly_and_mission_data = self._parse_weekly_data(self.driver)
            mission_data = self._parse_mission_data(self.driver)

            # 최종 데이터 구조화
            final_data['metadata'] = {'report_date': get_korea_time().strftime('%Y-%m-%d')}
            final_data['daily_data'] = daily_data
            final_data['weekly_summary'] = weekly_and_mission_data
            final_data['mission_status'] = mission_data
            final_data['daily_riders'] = daily_data.get('riders', [])
            final_data['metadata']['error'] = None # 성공 시 에러 없음을 명시적으로 기록
            
        except Exception as e:
            logger.error(f"전체 데이터 수집 프로세스 실패: {e}", exc_info=True)
            if 'metadata' not in final_data:
                final_data['metadata'] = {}
            final_data['metadata']['error'] = str(e) # 실패 시 에러 기록
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("WebDriver를 종료했습니다.")
        
        return final_data

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
        """수집된 데이터를 JSON 파일로 저장합니다."""
        try:
            current_script_path = os.path.dirname(os.path.abspath(__file__))
            # 'semiauto/dashboard/api' 디렉토리의 절대 경로
            save_path = os.path.join(current_script_path, '..', 'dashboard', 'api', 'latest-data.json')
            
            # 디렉토리가 없으면 생성
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logger.info(f"대시보드 데이터 저장 완료: {save_path}")
            
            # 히스토리 데이터 저장
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
        """데이터 수집, 메시지 포매팅 및 전송을 총괄합니다."""
        data = self.collector.collect_all_data()
        self.save_dashboard_data(data) # 데이터 저장
        
        if data.get('metadata', {}).get('error'):
            logger.error(f"데이터 수집 중 오류가 발생하여 리포트를 전송하지 않습니다: {data['metadata']['error']}")
            # 필요시 오류 상황을 알리는 메시지를 보낼 수도 있음
            # self.kakao_manager.send_message("자동화 스크립트 실행 중 오류가 발생했습니다.")
            return
        
        message = self.format_message(data)
        self.kakao_sender.send_text_message(message)

    def format_message(self, data):
        """템플릿 파일을 기반으로 최종 메시지를 생성합니다."""
        try:
            with open('semiauto/message_template.md', 'r', encoding='utf-8') as f:
                template = f.read()
        except FileNotFoundError:
            logger.error("semiauto/message_template.md 파일을 찾을 수 없습니다.")
            return "오류: 메시지 템플릿 파일을 찾을 수 없습니다."

        # 데이터 추출 및 계산
        daily_summary_data = data.get('daily_summary', {})
        weekly_summary_data = data.get('weekly_summary', {})
        mission_data = data.get('mission_status', {})
        riders_data = data.get('daily_riders', [])

        daily_completed = daily_summary_data.get('total_completed', 0)
        daily_rejected_and_canceled = daily_summary_data.get('total_rejected', 0) + daily_summary_data.get('total_canceled', 0)
        total_daily_for_rate = daily_completed + daily_rejected_and_canceled
        daily_acceptance_rate = (daily_completed / total_daily_for_rate * 100) if total_daily_for_rate > 0 else 0.0
        
        # 각 섹션 포맷팅
        mission_summary = self._format_mission_summary(mission_data)
        daily_acceptance_bar = self._format_progress_bar(daily_acceptance_rate)
        weather_summary = self._format_weather_summary()
        weekly_acceptance_bar = self._format_progress_bar(weekly_summary_data.get('수락률', 0.0))
        rider_rankings, active_rider_count = self._format_rider_rankings(riders_data)
        mission_shortage_summary = self._format_mission_shortage_summary(mission_data)

        # 플레이스홀더 채우기
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
        """백분율을 기반으로 텍스트 진행률 표시줄을 만듭니다."""
        if not isinstance(percentage, (int, float)):
            percentage = 0
        fill_count = int(round(percentage / (100 / length)))
        return '🟩' * fill_count + '⬜' * (length - fill_count)

    def _format_mission_summary(self, missions):
        lines = []
        if not missions: return ""
        for mission_name, details in missions.items():
            current, goal = details.get('current',0), details.get('goal',0)
            status_icon = "✅" if details.get('is_achieved') else "⚠️"
            status_text = "(달성)" if details.get('is_achieved') else f"({details.get('shortage',0)}건 부족)"
            lines.append(f"{details.get('icon','')} {status_icon} {mission_name}: {current}/{goal} {status_text}")
        return "\n".join(lines)
        
    def _format_weather_summary(self):
        try:
            weather_service = WeatherService()
            weather_info = weather_service.get_weather()
            if weather_info and 'error' not in weather_info:
                return (f"🌍 오늘의 날씨 ({weather_info['source']})\n"
                        f" 🌅 오전: {weather_info['am_temp_min']}~{weather_info['am_temp_max']}°C, 강수확률 {weather_info['am_rain_prob']}%\n"
                        f" 🌇 오후: {weather_info['pm_temp_min']}~{weather_info['pm_temp_max']}°C, 강수확률 {weather_info['pm_rain_prob']}%")
        except Exception as e:
            logger.warning(f"날씨 정보 조회 실패: {e}")
        return "🌍 날씨 정보 (조회 실패)"

    def _format_rider_rankings(self, riders):
        if not riders:
            return "운행 중인 라이더 정보가 없습니다.", 0

        riders.sort(key=lambda x: x.get('완료', 0), reverse=True)
        
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
        shortages = [f"{details.get('short_name','')} {details.get('shortage',0)}건" 
                     for details in missions.values() if not details.get('is_achieved')]
        if not shortages:
            return "🎉 모든 미션 달성! 🎉"
        return "⚠️ 미션 부족: " + ", ".join(shortages)

    def _get_safe_number(self, text):
        """문자열에서 숫자만 추출하여 정수로 변환합니다. 변환 실패 시 0을 반환합니다."""
        if not isinstance(text, str):
            return 0
        
        text = text.strip()
        # 'N/A', '-', 등 숫자 변환이 불가능한 경우를 처리
        if text in ['N/A', '-', '']:
            return 0
            
        # '점', '건', '회' 등 단위 제거
        text = text.replace('점', '').replace('건', '').replace('회', '')
        
        # 정규표현식을 사용하여 숫자 부분만 추출 (소수점도 고려)
        numbers = re.findall(r'[-+]?\d*\.\d+|\d+', text)
        
        if numbers:
            try:
                # 첫 번째로 찾은 숫자를 정수로 변환
                return int(float(numbers[0]))
            except (ValueError, IndexError):
                return 0
        return 0

    def collect_all_data(self):
        """모든 데이터를 수집하고 종합하여 반환합니다."""
        final_data = {}
        self.driver = None # 드라이버 인스턴스를 클래스 속성으로 초기화
        
        try:
            # final_data['weather_info'] = self._get_weather_info_detailed() # 날씨 조회 임시 비활성화
            self.driver = self._perform_login()
            if not self.driver:
                raise Exception("G라이더 로그인 실패")

            # 모든 데이터는 로그인 후의 대시보드에서 수집
            daily_data = self._parse_daily_rider_data(self.driver)
            weekly_and_mission_data = self._parse_weekly_data(self.driver)
            mission_data = self._parse_mission_data(self.driver)

            # 최종 데이터 구조화
            final_data['metadata'] = {'report_date': get_korea_time().strftime('%Y-%m-%d')}
            final_data['daily_data'] = daily_data
            final_data['weekly_summary'] = weekly_and_mission_data
            final_data['mission_status'] = mission_data
            final_data['daily_riders'] = daily_data.get('riders', [])
            final_data['metadata']['error'] = None # 성공 시 에러 없음을 명시적으로 기록
            
        except Exception as e:
            logger.error(f"전체 데이터 수집 프로세스 실패: {e}", exc_info=True)
            if 'metadata' not in final_data:
                final_data['metadata'] = {}
            final_data['metadata']['error'] = str(e) # 실패 시 에러 기록
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("WebDriver를 종료했습니다.")
        
        return final_data

def main():
    """스크립트의 메인 실행 함수입니다."""
    load_dotenv()
    
    holiday_api_key = os.getenv("HOLIDAY_API_KEY")
    if holiday_api_key:
        holiday_checker = KoreaHolidayChecker()
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
