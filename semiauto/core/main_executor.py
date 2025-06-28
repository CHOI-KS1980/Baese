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
        """SLA 페이지에서 주간 요약 점수와 라이더 실적 데이터를 파싱하고 계산합니다."""
        weekly_data = {}
        try:
            # driver.get(self.sla_url) # 대시보드에 모든 정보가 있으므로 페이지 이동 불필요
            wait = WebDriverWait(driver, 20) # 대기시간 20초로 증가

            # 1. 주간 요약 점수 파싱 (카드에 표시된 점수만 가져옴)
            summary_scores = {}
            s_summary = self.selectors.get('weekly_summary', {})
            summary_container_selector = s_summary.get('summary', {}).get('container')
            if summary_container_selector:
                # 점수 카드가 모두 나타날 때까지 대기
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, s_summary.get('summary', {}).get('total_score'))))
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, s_summary.get('summary', {}).get('quantity_score'))))
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, s_summary.get('summary', {}).get('acceptance_score'))))
                
                summary_scores['예상총점수'] = driver.find_element(By.CSS_SELECTOR, s_summary.get('summary', {}).get('total_score')).text.strip()
                summary_scores['물량점수'] = driver.find_element(By.CSS_SELECTOR, s_summary.get('summary', {}).get('quantity_score')).text.strip()
                summary_scores['수락률점수'] = driver.find_element(By.CSS_SELECTOR, s_summary.get('summary', {}).get('acceptance_score')).text.strip()
                logger.info(f"✅ 예상 점수 카드 파싱 완료: {summary_scores}")
            else:
                logger.warning("주간 요약 점수 선택자를 찾을 수 없습니다.")

            # 2. 주간 통계 파싱 (총 완료, 거절, 수락률)
            weekly_stats = {}
            s_stats = s_summary.get('stats', {}) # 'summary_etc' -> 'stats'
            stats_container_selector = s_stats.get('container')
            if stats_container_selector:
                try:
                    # 주간 라이더 목록의 첫번째 아이템이 나타날 때까지 대기
                    item_selector = f"{stats_container_selector} {s_stats.get('item')}"
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
                                total_completions += int(rider_element.find_element(By.CSS_SELECTOR, s_stats.get('complete_count')).text.strip())
                                total_rejections += int(rider_element.find_element(By.CSS_SELECTOR, s_stats.get('reject_count')).text.strip())
                                total_dispatch_cancels += int(rider_element.find_element(By.CSS_SELECTOR, s_stats.get('dispatch_cancel_count')).text.strip())
                                total_delivery_cancels += int(rider_element.find_element(By.CSS_SELECTOR, s_stats.get('delivery_cancel_count')).text.strip())
                            except (NoSuchElementException, ValueError) as e:
                                logger.warning(f"라이더 데이터 파싱 중 오류(건너뜀): {e}")
                                continue
                        
                        calculated_total_rejections = total_rejections + total_dispatch_cancels + total_delivery_cancels
                        total_for_rate = total_completions + calculated_total_rejections
                        
                        weekly_stats['총완료'] = total_completions
                        weekly_stats['총거절'] = calculated_total_rejections
                        weekly_stats['수락률'] = (total_completions / total_for_rate * 100) if total_for_rate > 0 else 0.0
                        
                        logger.info(f"✅ 주간 라이더 실적 직접 계산 완료: 총완료={weekly_stats['총완료']}, 총거절={weekly_stats['총거절']}, 수락률={weekly_stats['수락률']:.2f}%")
                    else:
                        logger.warning(f"주간 라이더 목록({stats_container_selector})를 찾았으나, 개별 라이더({s_stats.get('item')})가 없습니다.")
                except Exception as e:
                    logger.error(f"주간 통계 파싱 중 오류: {e}")
            else:
                 logger.warning(f"주간 통계 선택자를 찾지 못했습니다.")

            # 3. 최종 데이터 조합
            weekly_data.update(summary_scores)
            weekly_data.update(weekly_stats)

        except TimeoutException as e:
            logger.error(f"'주간/미션 데이터' 파싱 타임아웃. 현재 페이지 소스를 로그에 기록합니다.", exc_info=True)
            logger.error(f"PAGE_SOURCE_START\n{driver.page_source}\nPAGE_SOURCE_END")
        except Exception as e:
            logger.error(f"'주간/미션 데이터' 파싱 중 예외 발생: {e}", exc_info=True)
            
        return weekly_data

    def _parse_daily_rider_data(self, driver):
        """대시보드에서 일간 라이더 데이터를 파싱합니다. (선택자 기반)"""
        daily_data = {}
        rider_list = []
        try:
            logger.info("로그인 후 대시보드에서 '일간 라이더 데이터' 수집을 시작합니다.")
            driver.get(self.dashboard_url)
            s_daily = self.selectors.get('daily_data', {})
            wait = WebDriverWait(driver, 20)

            # 1. 일일 총계 데이터 파싱
            total_container_selector = s_daily.get('total_container')
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
                    logger.error(f"일일 총계 데이터 파싱 중 오류: {e}", exc_info=True)
                    daily_data.update({'total_completed': 0, 'total_rejected': 0, 'total_canceled': 0})
            else:
                logger.warning("일일 총계 컨테이너 선택자를 찾을 수 없습니다.")

            # 2. 개별 라이더 데이터 파싱
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
                    rider_data['아침점심피크'] = self._get_safe_number(rider_element.find_element(By.CSS_SELECTOR, s_daily.get('morning_count')).text)
                    rider_data['오후논피크'] = self._get_safe_number(rider_element.find_element(By.CSS_SELECTOR, s_daily.get('afternoon_count')).text)
                    rider_data['저녁피크'] = self._get_safe_number(rider_element.find_element(By.CSS_SELECTOR, s_daily.get('evening_count')).text)
                    rider_data['심야논피크'] = self._get_safe_number(rider_element.find_element(By.CSS_SELECTOR, s_daily.get('midnight_count')).text)

                    total_actions = sum(v for k, v in rider_data.items() if k != 'name')
                    if total_actions > 0:
                        rider_list.append(rider_data)
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
            
            daily_data['daily_riders'] = rider_list
            logger.info(f"✅ {len(rider_list)}명의 활동 라이더 데이터 파싱 완료.")

        except TimeoutException:
            logger.error("미션 데이터 테이블 로드 시간 초과. 현재 페이지 소스를 로그에 기록합니다.", exc_info=True)
            logger.error(f"PAGE_SOURCE_START\n{driver.page_source}\nPAGE_SOURCE_END")
        except Exception as e:
            logger.error(f"일간 라이더 데이터 파싱 중 심각한 오류 발생: {e}", exc_info=True)
            daily_data.setdefault('daily_riders', [])
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
            # findall('.//location') 을 통해 전체 XML 문서에서 location 태그를 찾습니다.
            for loc_element in root.findall('.//location'):
                city_element = loc_element.find('city')
                if city_element is not None and city_element.text == location:
                    # 첫 번째 data 요소 (가장 가까운 예보)
                    data_element = loc_element.find("./data[1]")
                    if data_element is not None:
                        weather_desc = data_element.find('wf').text
                        min_temp = data_element.find('tmn').text
                        max_temp = data_element.find('tmx').text

                        def get_icon(desc):
                            if "맑음" in desc: return "☀️"
                            if "구름많" in desc: return "☁️"
                            if "흐림" in desc: return "🌫️"
                            if "비" in desc: return "🌧️"
                            if "눈" in desc: return "❄️"
                            return "❓"

                        return {
                            "description": weather_desc,
                            "icon": get_icon(weather_desc),
                            "temp_min": min_temp,
                            "temp_max": max_temp
                        }
            # 서울 지역을 찾지 못한 경우
            logger.warning(f"기상청 데이터에서 '{location}' 지역을 찾을 수 없습니다.")

        except ET.ParseError as e:
            logger.error(f"날씨 정보 XML 파싱 실패: {e}", exc_info=True)
            # 파싱 실패 시 원본 내용을 로그로 남겨 분석을 돕습니다.
            logger.debug(f"파싱 실패한 XML 내용:\n{response.text}")
        except Exception as e:
            logger.error(f"상세 날씨 정보 조회 중 알 수 없는 오류 발생: {e}", exc_info=True)
            
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

    def _get_safe_number(self, text, to_float=False):
        """문자열에서 숫자만 추출하여 int 또는 float로 반환합니다. '%' 등 비숫자 문자 제거."""
        if not isinstance(text, str):
            return float(text) if to_float else int(text)
        
        # 정규표현식을 사용하여 숫자(소수점 포함) 부분만 추출
        match = re.search(r'[-+]?\d*\.?\d+', text.strip())
        if match:
            num_str = match.group(0)
            return float(num_str) if to_float else int(float(num_str)) # float으로 먼저 변환하여 소수점 있는 정수 처리
        return 0.0 if to_float else 0

    def collect_all_data(self):
        """모든 데이터를 수집하고 종합하여 반환합니다."""
        driver = None
        final_data = {
            'metadata': {
                'report_date': self._get_today_date(),
                'error': None
            },
            'weather_info': {},
            'daily_summary': {},
            'weekly_summary': {},
            'mission_status': {},
            'daily_riders': []
        }
        
        try:
            # final_data['weather_info'] = self._get_weather_info_detailed() # 날씨 조회 임시 비활성화
            driver = self._perform_login()
            if not driver:
                raise Exception("G라이더 로그인 실패")

            # 데이터 수집
            daily_data = self._parse_daily_rider_data(driver)
            weekly_and_mission_data = self._parse_weekly_data(driver) # 주간/미션 데이터는 같은 페이지에서 가져옴
            mission_data = self._parse_mission_data(driver)

            # 데이터 조합
            final_data['daily_summary'] = {
                'total_completed': daily_data.get('total_completed', 0),
                'total_rejected': daily_data.get('total_rejected', 0),
                'total_canceled': daily_data.get('total_canceled', 0),
            }
            final_data['weekly_summary'] = weekly_and_mission_data
            final_data['mission_status'] = mission_data
            final_data['daily_riders'] = daily_data.get('daily_riders', [])
            
        except Exception as e:
            error_message = f"데이터 수집 실패: {e}"
            logger.error(error_message, exc_info=True)
            final_data['metadata']['error'] = error_message
        finally:
            if driver:
                driver.quit()
        
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
        
        if data['metadata']['error']:
            error_message = f"데이터 수집 중 오류 발생: {data['metadata']['error']}"
            self.send_kakao_message(error_message)
            return

        formatted_message = self.format_message(data)
        
        # pyperclip을 이용한 클립보드 복사 (로컬 환경에서만)
        if 'GITHUB_ACTIONS' not in os.environ:
            try:
                import pyperclip
                pyperclip.copy(formatted_message)
                logger.info("✅ 메시지가 클립보드에 복사되었습니다.")
            except Exception as e:
                logger.warning(f"클립보드 복사 실패. 'pyperclip'이 설치되지 않았을 수 있습니다: {e}")

        # 카카오톡 메시지 전송
        self.send_kakao_message(formatted_message)

    def send_kakao_message(self, text: str):
        """카카오톡 메시지를 전송합니다."""
        if self.kakao_sender:
            self.kakao_sender.send_text_message(text)
        else:
            logger.warning("카카오톡 발송기(sender)가 초기화되지 않아 메시지를 전송할 수 없습니다.")
            # 비상 플랜: 콘솔에 메시지 출력
            print("\n--- 카카오톡 전송 메시지 (콘솔 출력) ---\n")
            print(text)
            print("\n---------------------------------------\n")

    def format_message(self, data: dict) -> str:
        """수집된 데이터를 기반으로 카카오톡 메시지 문자열을 생성합니다."""
        
        def get_acceptance_progress_bar(percentage: float) -> str:
            """수락률에 따라 프로그레스 바 아이콘 반환"""
            if percentage >= 98: return "🟩🟩🟩🟩🟩"
            if percentage >= 95: return "🟨🟨🟨🟨🟨"
            if percentage > 90:  return "🟧🟧🟧🟧🟧"
            return "🟥🟥🟥🟥🟥"

        def get_rider_progress_bar(contribution: float) -> str:
            """기여도에 따라 프로그레스 바 아이콘 반환"""
            bar = "▰" * int(contribution / 10)
            return bar if bar else "▱"

        # 데이터 추출
        report_date = data.get('metadata', {}).get('report_date', '날짜 없음')
        daily = data.get('daily_summary', {})
        weekly = data.get('weekly_summary', {})
        mission = data.get('mission_status', {})
        riders = data.get('daily_riders', [])

        # 날짜 및 공휴일 정보
        today_date_obj = datetime.strptime(report_date, '%Y-%m-%d')
        day_of_week = ['월', '화', '수', '목', '금', '토', '일'][today_date_obj.weekday()]
        is_holiday, holiday_name = holiday_checker.is_holiday_advanced(report_date)
        date_str = f"{today_date_obj.month}/{today_date_obj.day}({day_of_week})"
        if is_holiday:
            date_str += f" HOLIDAY! ({holiday_name})"

        # 날씨 정보
        weather = data.get('weather_info')
        # weather_str = f"{weather['icon']} {weather['description']} ({weather['temp_min']}°C / {weather['temp_max']}°C)" if weather else "날씨 정보 없음"
        weather_str = "날씨 정보 (임시 비활성화)"

        # 메시지 헤더
        header = f"📊 {date_str} - {weather_str}\n"
        header += "==============================\n"

        # 주간 요약
        weekly_total_completed = weekly.get('총완료', 0)
        weekly_total_rejected = weekly.get('총거절', 0)
        weekly_acceptance_rate = weekly.get('수락률', 0.0)
        
        weekly_summary_str = (
            f"📈 주간 요약\n"
            f"├ 총완료: {weekly_total_completed}건 | 총거절: {weekly_total_rejected}건\n"
            f"├ 수락률: {weekly_acceptance_rate:.2f}% {get_acceptance_progress_bar(weekly_acceptance_rate)}\n"
            f"└ 예상점수: 총 {weekly.get('예상총점수','-')}점 (물량 {weekly.get('물량점수','-')} + 수락률 {weekly.get('수락률점수','-')})\n"
        )
        
        # 미션 현황
        delivery_mission = mission.get('delivery_mission', {})
        safety_mission = mission.get('safety_mission', {})
        mission_str = (
            f"🎯 오늘의 미션\n"
            f"├ 배달: {delivery_mission.get('current', 0)}/{delivery_mission.get('target', 0)}건 ({delivery_mission.get('score', '0')}점)\n"
            f"└ 안전: {safety_mission.get('current', 0)}/{safety_mission.get('target', 0)}건 ({safety_mission.get('score', '0')}점)\n"
        )
        
        # 일간 요약
        daily_total = daily.get('total_completed', 0)
        daily_rejected = daily.get('total_rejected', 0)
        daily_canceled = daily.get('total_canceled', 0)
        daily_acceptance_rate = (daily_total / (daily_total + daily_rejected + daily_canceled) * 100) if (daily_total + daily_rejected + daily_canceled) > 0 else 0
        
        daily_summary_str = (
            f"📉 일간 요약\n"
            f"├ 완료: {daily_total}건 | 거절: {daily_rejected}건 | 취소: {daily_canceled}건\n"
            f"└ 수락률: {daily_acceptance_rate:.2f}%\n"
        )

        # 라이더별 상세
        rider_str = "👤 라이더별 상세\n"
        if not riders:
            rider_str += "  - 운행 중인 라이더 정보가 없습니다.\n"
        else:
            # 기여도 계산 및 정렬
            for rider in riders:
                rider['total'] = rider.get('완료', 0)
                rider['contribution'] = (rider['total'] / daily_total * 100) if daily_total > 0 else 0
            
            sorted_riders = sorted(riders, key=lambda x: x['total'], reverse=True)

            for rider in sorted_riders[:10]: # 상위 10명만 표시
                progress_bar = get_rider_progress_bar(rider['contribution'])
                rider_str += (
                    f"├ {rider['name']} {rider['total']}건 ({rider['contribution']:.1f}%) {progress_bar}\n"
                    f"|    (거절 {rider.get('거절',0)}, 배취 {rider.get('배차취소',0)}, 배달취소 {rider.get('배달취소',0)})\n"
                )

        # 전체 메시지 조합
        return f"{header}\n{weekly_summary_str}\n{mission_str}\n{daily_summary_str}\n{rider_str}"

def load_config():
    """환경변수를 .env 파일에서 로드합니다."""
    # .env 파일이 현재 작업 디렉토리에 있는지 확인
    if os.path.exists('.env'):
        load_dotenv()
        logger.info(".env 파일에서 환경변수를 로드했습니다.")
    # GitHub Actions 환경인지 확인
    elif 'GITHUB_ACTIONS' in os.environ:
        logger.info("GitHub Actions 환경으로 감지되었습니다. 환경변수는 Secrets를 통해 주입됩니다.")
    else:
        logger.warning(".env 파일이 없으며, GitHub Actions 환경이 아닙니다. 필요한 환경변수가 설정되지 않았을 수 있습니다.")

def main():
    """메인 실행 함수"""
    logger.info("==================================================")
    logger.info(" G-Rider 자동화 스크립트 시작")
    logger.info("==================================================")
    
    load_config()
    
    # 환경변수 로드 확인
    required_vars = ['GRIDER_ID', 'GRIDER_PASSWORD', 'KAKAO_REST_API_KEY', 'KAKAO_REFRESH_TOKEN']
    if not all(os.getenv(var) for var in required_vars):
        logger.warning("필수 환경변수가 모두 설정되지 않았습니다.")

    sender = GriderAutoSender(
        rest_api_key=os.getenv("KAKAO_REST_API_KEY"),
        refresh_token=os.getenv("KAKAO_REFRESH_TOKEN")
    )
    sender.send_report()
    
    logger.info("==================================================")
    logger.info(" G-Rider 자동화 스크립트 종료")
    logger.info("==================================================")


if __name__ == '__main__':
    main()
