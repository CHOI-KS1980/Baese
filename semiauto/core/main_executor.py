import os
import re
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging
import requests
import xml.etree.ElementTree as ET

import pytz
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, InvalidArgumentException

try:
    from webdriver_manager.chrome import ChromeDriverManager
    import chromedriver_autoinstaller
    WEBDRIVER_INSTALLED = True
except ImportError:
    WEBDRIVER_INSTALLED = False

# ==============================================================================
# 로깅 설정
# ==============================================================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# =https://www.kma.go.kr/weather/forecast/mid-term-rss3.jsp?stnId=109
# 유틸리티 함수
# ==============================================================================
def get_korea_time():
    """한국 시간(KST)을 반환합니다."""
    return datetime.now(pytz.timezone('Asia/Seoul'))

class KoreaHolidayChecker:
    """한국천문연구원 특일 정보 API를 사용하여 공휴일을 확인합니다."""
    def __init__(self):
        # 한국천문연구원 특일 정보 API
        self.api_url = "https://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo"
        self.api_key = os.getenv('KOREA_HOLIDAY_API_KEY')
        self.holidays = {}
        if not self.api_key:
            logger.info("KOREA_HOLIDAY_API_KEY 환경변수가 설정되지 않음 - 기본 공휴일 사용")
        else:
            logger.info("한국천문연구원 특일 정보 API 공휴일 체커 초기화")


    def get_holidays_from_api(self, year, month=None):
        """API로부터 특정 연도 또는 특정 월의 공휴일 정보를 가져옵니다."""
        if not self.api_key:
            return []

        params = {
            'serviceKey': requests.utils.unquote(self.api_key),
            'solYear': year,
            'numOfRows': 100
        }
        if month:
            params['solMonth'] = f"{month:02d}"

        try:
            response = requests.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            holidays = []
            for item in root.findall('.//item'):
                locdate_str = item.find('locdate').text
                date_name = item.find('dateName').text
                is_holiday = item.find('isHoliday').text == 'Y'
                if is_holiday:
                    holidays.append({'date': datetime.strptime(locdate_str, '%Y%m%d').date(), 'name': date_name})
                    logger.info(f"공휴일 확인: {datetime.strptime(locdate_str, '%Y%m%d').strftime('%Y-%m-%d')} - {date_name}")
            return holidays
        except requests.RequestException as e:
            logger.error(f"공휴일 API 요청 실패: {e}")
        except ET.ParseError as e:
            logger.error(f"공휴일 API XML 파싱 실패: {e}")
        return []


    def load_year_holidays(self, year):
        """특정 연도의 모든 공휴일을 로드하고 캐싱합니다."""
        if year in self.holidays:
            return

        all_holidays = self.get_holidays_from_api(year)
        self.holidays[year] = {h['date']: h['name'] for h in all_holidays}
        logger.info(f"{year}년 전체월 공휴일 {len(self.holidays[year])}개 로드 완료")


    def is_holiday_advanced(self, target_date):
        """주어진 날짜가 주말 또는 공휴일인지 확인합니다."""
        year = target_date.year
        if year not in self.holidays:
            self.load_year_holidays(year)
            # 다음 해 1월 초 공휴일도 미리 로드 (심야 시간 처리)
            if target_date.month == 12:
                self.load_year_holidays(year + 1)
        
        # 주말 확인 (토요일, 일요일)
        if target_date.weekday() >= 5:
            return True

        # 공휴일 확인
        return target_date.date() in self.holidays.get(year, {})


class TokenManager:
    """카카오톡 토큰을 관리하고, 필요 시 갱신합니다."""
    def __init__(self, rest_api_key, refresh_token):
        self.rest_api_key = rest_api_key
        self.access_token = None
        self.refresh_token = refresh_token
        self.token_url = "https://kauth.kakao.com/oauth/token"
        self.last_refreshed = None
        self.token_file = Path(__file__).parent / 'kakao_token.json'
        self._load_tokens_from_file()

    def refresh_access_token(self):
        """Refresh token을 사용하여 Access token을 갱신합니다."""
        logger.info("TokenManager 초기화 - 토큰 갱신 시도")
        payload = {
            'grant_type': 'refresh_token',
            'client_id': self.rest_api_key,
            'refresh_token': self.refresh_token,
        }
        try:
            response = requests.post(self.token_url, data=payload, timeout=10)
            response.raise_for_status()
            tokens = response.json()
            
            self.access_token = tokens['access_token']
            # 일부 응답에는 refresh_token이 포함되지 않을 수 있음
            if 'refresh_token' in tokens:
                self.refresh_token = tokens['refresh_token']
                
            self.last_refreshed = get_korea_time()
            self._save_tokens_to_file()
            logger.info(f"토큰 갱신 완료: {self.access_token[:20]}...")
            return True
        except requests.RequestException as e:
            logger.error(f"카카오 토큰 갱신 실패: {e}")
            return False

    def get_valid_token(self):
        """유효한 토큰을 반환합니다. 필요 시 갱신합니다."""
        if not self.access_token or self.is_token_expired():
            if not self.refresh_access_token():
                return None
        logger.info(f"유효한 토큰 반환: {self.access_token[:20]}...")
        return self.access_token

    def is_token_expired(self):
        """토큰이 만료되었는지 확인합니다 (만료 1시간 전 갱신)."""
        if not self.last_refreshed:
            return True
        return (get_korea_time() - self.last_refreshed) > timedelta(hours=5)

    def _save_tokens_to_file(self):
        """토큰 정보를 파일에 저장합니다."""
        tokens = {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'last_refreshed': self.last_refreshed.isoformat() if self.last_refreshed else None
        }
        try:
            with self.token_file.open('w') as f:
                json.dump(tokens, f)
        except IOError as e:
            logger.error(f"토큰 파일 저장 실패: {e}")

    def _load_tokens_from_file(self):
        """파일에서 토큰 정보를 불러옵니다."""
        if not self.token_file.exists():
            return
        try:
            with self.token_file.open('r') as f:
                tokens = json.load(f)
                self.access_token = tokens.get('access_token')
                self.refresh_token = tokens.get('refresh_token')
                last_refreshed_iso = tokens.get('last_refreshed')
                if last_refreshed_iso:
                    self.last_refreshed = datetime.fromisoformat(last_refreshed_iso)
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"토큰 파일 로드 실패: {e}")

class KakaoSender:
    """카카오톡 '나에게 보내기' 기능을 사용하여 메시지를 전송합니다."""
    def __init__(self, access_token):
        self.access_token = access_token
        self.send_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

    def send_text_message(self, text: str, link_url: str = None):
        """지정된 텍스트 메시지를 카카오톡으로 전송합니다."""
        headers = {'Authorization': f'Bearer {self.access_token}'}
        template = {
            'object_type': 'text',
            'text': text,
            'link': {'web_url': link_url, 'mobile_web_url': link_url} if link_url else {},
        }
        
        try:
            response = requests.post(self.send_url, headers=headers, data={'template_object': json.dumps(template)}, timeout=10)
            response.raise_for_status()
            if response.json().get('result_code') == 0:
                logger.info("✅ 카카오톡 메시지 전송 성공")
                return True
            else:
                logger.error(f"카카오톡 메시지 전송 실패: {response.text}")
                return False
        except requests.RequestException as e:
            logger.error(f"카카오톡 API 요청 실패: {e}")
            return False
            
class GriderDataCollector:
    """G-Rider 웹사이트에서 데이터를 수집하는 클래스입니다."""
    def __init__(self):
        self.base_url = "https://jangboo.grider.ai"
        self.dashboard_url = f"{self.base_url}/dashboard"
        self.sla_url = f"{self.base_url}/op/sla"
        
        self.grider_id = os.getenv('GRIDER_ID')
        self.grider_password = os.getenv('GRIDER_PW')
        
        self.selectors = self._load_all_selectors()

    def _load_all_selectors(self):
        """'selectors' 디렉토리에서 모든 .json 설정 파일을 로드합니다."""
        selectors = {}
        selector_dir = Path(__file__).parent.parent / 'selectors'
        for file_path in selector_dir.glob('*.json'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    selectors[file_path.stem] = json.load(f)
                    logger.info(f"선택자 파일 로드 완료: {file_path.name}")
            except (IOError, json.JSONDecodeError) as e:
                logger.error(f"선택자 파일 '{file_path.name}' 로드 실패: {e}")
        return selectors

    def _get_driver(self):
        """Selenium WebDriver를 초기화하고 반환합니다."""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")
        
        if not self.grider_id or not self.grider_password:
            raise Exception("G라이더 로그인 정보가 없습니다.")

        if WEBDRIVER_INSTALLED:
            try:
                # webdriver-manager 사용
                service = ChromeService(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                logger.info("✅ Chrome WebDriver 초기화 성공 (webdriver-manager)")
                return driver
            except Exception as e:
                logger.warning(f"webdriver-manager 초기화 실패, chromedriver-autoinstaller로 재시도: {e}")
                # chromedriver-autoinstaller로 재시도
                chromedriver_autoinstaller.install()
                driver = webdriver.Chrome(options=options)
                logger.info("✅ Chrome WebDriver 초기화 성공 (chromedriver-autoinstaller)")
                return driver
        else:
            # 수동 설정 (대안)
            driver = webdriver.Chrome(options=options)
            logger.info("✅ Chrome WebDriver 수동 초기화 성공")
            return driver

    def _login(self, driver):
        """로그인 페이지에서 로그인을 수행합니다."""
        s_login = self.selectors.get('login', {})
        login_url = self.base_url + s_login.get('url_path', '/login')
        
        try:
            driver.get(login_url)
            wait = WebDriverWait(driver, 20)
            
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
        """대시보드에서 일간 라이더 데이터를 파싱합니다. (선택자 기반)"""
        daily_data = {}
        rider_list = []
        try:
            logger.info("로그인 후 대시보드에서 '일간 라이더 데이터' 수집을 시작합니다.")
            driver.get(self.dashboard_url)
            s_daily = self.selectors.get('daily_data', {})
            wait = WebDriverWait(driver, 20)

            # 1. 일일 총계 데이터 파싱
            try:
                total_container_selector = s_daily.get('total_row_header')
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
                    name = name_element.text.strip()
                    if not name:
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
                    logger.warning("라이더 항목 내에서 일부 데이터(예: 이름 또는 그룹)를 찾지 못해 건너뜁니다.")
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
            
            rows = driver.find_elements(By.CSS_SELECTOR, full_row_selector)
            
            for row in rows:
                try:
                    date_element = row.find_element(By.CSS_SELECTOR, s_mission_table.get('date_in_row'))
                    if date_element.text.strip() == today_str:
                        logger.info(f"✅ 오늘({today_str}) 날짜의 미션 행을 찾았습니다.")
                        
                        delivery_text = row.find_element(By.CSS_SELECTOR, s_mission_table.get('delivery_mission')).text
                        safety_text = row.find_element(By.CSS_SELECTOR, s_mission_table.get('safety_mission')).text
                        
                        mission_data['delivery_mission'] = self._parse_mission_string(delivery_text)
                        mission_data['safety_mission'] = self._parse_mission_string(safety_text)
                        
                        logger.info(f"✅ 미션 데이터 파싱 완료: {mission_data}")
                        return mission_data
                except Exception as e:
                    logger.warning(f"미션 테이블의 한 행을 처리하는 중 오류 발생(건너뜀): {e}")
                    continue
            
            logger.warning(f"오늘 날짜({today_str})에 해당하는 미션 데이터를 테이블에서 찾지 못했습니다.")
            
        except TimeoutException:
            logger.error("미션 데이터 테이블 로드 시간 초과", exc_info=True)
        except Exception as e:
            logger.error(f"미션 데이터 파싱 중 예외 발생: {e}", exc_info=True)
            
        return mission_data

    def _get_weather_info_detailed(self, location="서울"):
        """기상청 RSS 피드에서 상세 날씨 정보를 가져옵니다."""
        try:
            rss_url = "https://www.kma.go.kr/weather/forecast/mid-term-rss3.jsp?stnId=109"
            response = requests.get(rss_url, timeout=10)
            response.raise_for_status()

            root = ET.fromstring(response.content)
            location_element = root.find(f".//location[city='{location}']")

            if location_element is not None:
                data_element = location_element.find(".//data[1]") # 첫 번째 data 요소 (가장 가까운 예보)
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
        except Exception as e:
            logger.error(f"상세 날씨 정보 조회 실패: {e}")
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
            final_data['weather_info'] = self._get_weather_info_detailed()
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
            final_data['metadata']['error'] = str(e)
            logger.error(f"데이터 수집 실패: {e}", exc_info=True)
        finally:
            if driver:
                driver.quit()
        return final_data


class GriderAutoSender:
    """수집된 데이터를 처리하고 카카오톡으로 리포트를 전송합니다."""
    def __init__(self, rest_api_key=None, refresh_token=None):
        self.kakao_sender = None
        self.dashboard_api_dir = Path(__file__).parent.parent / 'dashboard' / 'api'
        
        if rest_api_key and refresh_token:
            token_manager = TokenManager(rest_api_key, refresh_token)
            access_token = token_manager.get_valid_token()
            if access_token:
                self.kakao_sender = KakaoSender(access_token)
        else:
            logger.warning("카카오톡 API 키가 설정되지 않아, 콘솔에만 메시지를 출력합니다.")

    def save_dashboard_data(self, data: dict):
        """수집된 데이터를 JSON 파일로 저장합니다."""
        self.dashboard_api_dir.mkdir(exist_ok=True)
        history_dir = self.dashboard_api_dir / 'history'
        history_dir.mkdir(exist_ok=True)

        latest_data_path = self.dashboard_api_dir / 'latest-data.json'
        history_file_path = history_dir / f"history-{data['metadata']['report_date']}.json"

        try:
            with open(latest_data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"대시보드 데이터 저장 완료: {latest_data_path}")
            
            with open(history_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"히스토리 데이터 저장 완료: {history_file_path}")
        except IOError as e:
            logger.error(f"데이터 파일 저장 실패: {e}")

    def send_report(self):
        """최신 데이터를 로드하고, 포맷하여 카카오톡으로 전송합니다."""
        latest_data_path = self.dashboard_api_dir / 'latest-data.json'
        try:
            with open(latest_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if data['metadata'].get('error'):
                error_message = f"데이터 수집 중 오류 발생: {data['metadata']['error']}"
                self.send_kakao_message(error_message)
            else:
                formatted_message = self.format_message(data)
                self.send_kakao_message(formatted_message)

        except (IOError, json.JSONDecodeError) as e:
            error_message = f"리포트 파일 처리 중 오류 발생: {e}"
            logger.error(error_message)
            self.send_kakao_message(error_message)

    def send_kakao_message(self, text: str):
        """메시지를 카카오톡 또는 콘솔로 전송합니다."""
        if self.kakao_sender:
            self.kakao_sender.send_text_message(text)
        else:
            print("\n" + "--- 카카오톡 전송 메시지 (콘솔 출력) ---")
            print(text)
            print("---------------------------------------" + "\n")

    def format_message(self, data: dict) -> str:
        """데이터를 카카오톡 메시지 형식으로 변환합니다."""
        def get_acceptance_progress_bar(percentage: float) -> str:
            """수락률에 따라 진행률 막대 이모지를 반환합니다."""
            if percentage >= 95: return "🟩🟩🟩🟩🟩"
            if percentage >= 90: return "🟩🟩🟩🟩🟨"
            if percentage >= 80: return "🟩🟩🟩🟨🟨"
            if percentage >= 70: return "🟩🟩🟨🟨🟨"
            if percentage >= 60: return "🟨🟨🟨🟨🟨"
            return "🟥🟥🟥🟥🟥"

        def get_rider_progress_bar(contribution: float) -> str:
            BAR_LENGTH = 5
            filled_count = int(contribution / 100 * BAR_LENGTH)
            return '🟩' * filled_count + '⬜' * (BAR_LENGTH - filled_count)

        report_date = data['metadata']['report_date']
        
        # 날씨 정보
        weather = data.get('weather_info')
        weather_str = f"{weather['icon']} {weather['description']} ({weather['temp_min']}°C / {weather['temp_max']}°C)" if weather else "날씨 정보 없음"

        # 주간 요약
        weekly = data['weekly_summary']
        weekly_acceptance_rate = weekly.get('수락률', 0)
        acceptance_bar = get_acceptance_progress_bar(weekly_acceptance_rate)
        
        weekly_summary_str = (
            f"✅ 주간 예상 총 점수: {weekly.get('예상총점수', 'N/A')}\n"
            f"  - 물량점수: {weekly.get('물량점수', 'N/A')}\n"
            f"  - 수락률점수: {weekly.get('수락률점수', 'N/A')}\n"
            f"✅ 주간 실적 요약\n"
            f"  - 총완료: {weekly.get('총완료', 0)}건, 총거절: {weekly.get('총거절', 0)}건\n"
            f"  - 수락률: {weekly_acceptance_rate:.2f}% {acceptance_bar}"
        )
        
        # 미션 현황
        mission = data.get('mission_status', {})
        delivery_mission = mission.get('delivery_mission', {})
        safety_mission = mission.get('safety_mission', {})
        mission_str = (
            f"✅ 금일 미션 현황\n"
            f"  - 배달: {delivery_mission.get('current', 0)}/{delivery_mission.get('target', 0)}건 ({delivery_mission.get('score', '0')}점)\n"
            f"  - 안전: {safety_mission.get('current', 0)}/{safety_mission.get('target', 0)}건 ({safety_mission.get('score', '0')}점)"
        )
        
        # 일일 라이더별 실적
        riders = sorted(data.get('daily_riders', []), key=lambda x: x.get('완료', 0), reverse=True)
        total_completions = sum(r.get('완료', 0) for r in riders)
        
        rider_strs = ["✅ 금일 라이더별 실적 TOP 5"]
        if not riders:
            rider_strs.append("  - 데이터 없음")
        else:
            for i, rider in enumerate(riders[:5]):
                contribution = (rider.get('완료', 0) / total_completions * 100) if total_completions > 0 else 0
                progress_bar = get_rider_progress_bar(contribution)
                
                # 상세 실적
                details = (
                    f"완료 {rider.get('완료', 0)} / 거절 {rider.get('거절', 0)} / "
                    f"취소 {rider.get('배차취소', 0)+rider.get('배달취소', 0)}"
                )
                rider_strs.append(
                    f"  {i+1}. {rider['name']}: {progress_bar} {contribution:.1f}%\n"
                    f"     ({details})"
                )

        # 메시지 조합
        message = (
            f"📊 G-Rider 리포트 ({report_date})\n"
            f"{weather_str}\n\n"
            f"{'='*15}\n"
            f"주간 실적 요약 (SLA)\n"
            f"{'-'*18}\n"
            f"{weekly_summary_str}\n\n"
            f"{'='*15}\n"
            f"미션 현황 (SLA)\n"
            f"{'-'*18}\n"
            f"{mission_str}\n\n"
            f"{'='*15}\n"
            f"일일 실적 요약 (대시보드)\n"
            f"{'-'*18}\n"
            f"{rider_strs[0]}\n" + "\n".join(rider_strs[1:])
        )
        
        return message

def load_config():
    """환경변수 및 .env 파일에서 설정을 로드합니다."""
    # .env 파일이 있으면 로드
    env_path = Path('.') / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        logger.info(".env 파일에서 환경변수를 로드했습니다.")

    config = {
        'GRIDER_ID': os.getenv('GRIDER_ID'),
        'GRIDER_PW': os.getenv('GRIDER_PW'),
        'KAKAO_REST_API_KEY': os.getenv('KAKAO_REST_API_KEY'),
        'KAKAO_REFRESH_TOKEN': os.getenv('KAKAO_REFRESH_TOKEN'),
        'KOREA_HOLIDAY_API_KEY': os.getenv('KOREA_HOLIDAY_API_KEY')
    }
    
    # 필수 환경변수 확인
    required_vars = ['GRIDER_ID', 'GRIDER_PW', 'KAKAO_REST_API_KEY', 'KAKAO_REFRESH_TOKEN']
    if not all(config.get(var) for var in required_vars):
        logger.warning("필수 환경변수가 모두 설정되지 않았습니다.")
        
    return config

def main():
    """메인 실행 함수"""
    logger.info("=" * 50)
    logger.info(" G-Rider 자동화 스크립트 시작")
    logger.info("=" * 50)

    config = load_config()

    # 데이터 수집
    collector = GriderDataCollector()
    data = collector.collect_all_data()
    
    # 리포트 전송
    sender = GriderAutoSender(
        rest_api_key=config['KAKAO_REST_API_KEY'],
        refresh_token=config['KAKAO_REFRESH_TOKEN']
    )
    sender.save_dashboard_data(data)
    sender.send_report()

    logger.info("=" * 50)
    logger.info(" G-Rider 자동화 스크립트 종료")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()+
