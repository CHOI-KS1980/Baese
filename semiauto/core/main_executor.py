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
from bs4 import BeautifulSoup  # BeautifulSoup import 추가
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
                    
                    if date_name_node is not None and loc_date_node is not None:
                        holiday_name = date_name_node.text
                        holiday_date = loc_date_node.text
                        holiday_status = is_holiday_node.text if is_holiday_node is not None else 'Y'
                        
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
        """G라이더 데이터 수집"""
        try:
            if use_sample:
                return self._get_error_data("샘플 데이터 사용")

            logger.info(" G라이더 실제 데이터 수집 시작...")
            
            html = self._crawl_jangboo()
            if not html:
                logger.error(" 크롤링 실패 - HTML을 가져올 수 없습니다")
                return self._get_error_data("크롤링 실패(HTML 없음)")
            
            data = self._parse_data(html)
            
            if data.get('error'):
                logger.error(f" 데이터 파싱 실패: {data.get('error_reason', '알 수 없는 오류')}")
                return data
            
            logger.info(" G라이더 데이터 수집 완료")
            return data
            
        except Exception as e:
            logger.error(f" 크롤링 중 오류 발생: {e}", exc_info=True)
            return self._get_error_data(f"크롤링 중 예외 발생: {e}")

    def _get_error_data(self, error_reason):
        """크롤링 실패 시 오류 메시지가 포함된 데이터"""
        return {
            '총점': 0, '물량점수': 0, '수락률점수': 0, '총완료': 0, '총거절': 0, '수락률': 0.0,
            '아침점심피크': {"current": 0, "target": 0}, '오후논피크': {"current": 0, "target": 0},
            '저녁피크': {"current": 0, "target": 0}, '심야논피크': {"current": 0, "target": 0},
            'riders': [], 'error': True, 'error_reason': error_reason,
            'timestamp': datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _crawl_jangboo(self, max_retries=3, retry_delay=5):
        """최적화된 크롤링 함수"""
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        
        driver = None
        for attempt in range(max_retries):
            try:
                logger.info(f"크롤링 시도 {attempt + 1}/{max_retries}")
                
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
                
                wait = WebDriverWait(driver, 20) # 명시적 대기 객체 생성

                driver.get('https://jangboo.grider.ai/login')
                
                # ID 필드가 나타날 때까지 최대 20초 대기
                wait.until(EC.presence_of_element_located((By.ID, 'id')))
                
                USER_ID = os.getenv('GRIDER_ID')
                USER_PW = os.getenv('GRIDER_PASSWORD')
                if not USER_ID or not USER_PW:
                    raise Exception("G라이더 로그인 정보가 없습니다.")
                
                driver.find_element(By.ID, 'id').send_keys(USER_ID)
                driver.find_element(By.ID, 'password').send_keys(USER_PW)
                driver.find_element(By.ID, 'loginBtn').click()
                
                # 로그인 성공 후 대시보드 URL로 변경될 때까지 대기
                wait.until(EC.url_contains('/dashboard'))

                target_date = self._get_mission_date()
                html = self._navigate_to_date_data(driver, target_date)
                
                if len(html) < 1000:
                    raise Exception("HTML 길이가 너무 짧아 로딩 실패로 간주")
                
                logger.info(" 크롤링 성공")

                # 임시 디버깅: 전체 HTML 로그 출력
                logger.info("================ HTML START ================")
                print(html)
                logger.info("================ HTML END ================")

                # 성공 시 디버깅을 위해 HTML 파일 저장
                with open('debug_grider_page.html', 'w', encoding='utf-8') as f:
                    f.write(html)
                
                return html
                
            except Exception as e:
                logger.error(f" 크롤링 시도 {attempt + 1} 실패: {e}")
                if driver:
                    with open(f'debug_failed_page_{attempt + 1}.html', 'w', encoding='utf-8') as f:
                        f.write(driver.page_source)
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    logger.error(" 모든 크롤링 시도 실패")
            finally:
                if driver:
                    driver.quit()
        return None

    def _navigate_to_date_data(self, driver, target_date: str) -> str:
        """URL 파라미터 방식으로 날짜별 데이터 조회"""
        url_with_date = f"https://jangboo.grider.ai/dashboard?date={target_date}"
        driver.get(url_with_date)
        
        # 데이터가 로드될 때까지 명시적으로 대기 (총점 값에 숫자가 나타날 때까지)
        try:
            WebDriverWait(driver, 30).until(
                lambda d: re.search(r'\d', d.find_element(By.CSS_SELECTOR, ".score_total_value").text)
            )
            logger.info("✅ 대시보드 데이터 로드 확인 (총점 확인)")
        except Exception:
            logger.warning("⚠️ 총점 데이터 로드 확인 시간 초과, 페이지 소스를 그대로 반환합니다.")

        if self._verify_date_in_html(driver.page_source, target_date):
            return driver.page_source
        raise Exception("날짜 검증 실패")

    def _verify_date_in_html(self, html: str, target_date: str) -> bool:
        """HTML 내용에서 날짜를 확인"""
        return target_date in html or target_date.replace('-', '.') in html

    def _get_korea_time(self):
        """한국시간 기준 현재 시간 반환"""
        return datetime.now(KST)

    def _get_mission_date(self):
        """한국시간 기준 현재 미션 날짜 반환 (06시 기준)"""
        korea_time = self._get_korea_time()
        if korea_time.hour < 6:
            return (korea_time - timedelta(days=1)).strftime('%Y-%m-%d')
        return korea_time.strftime('%Y-%m-%d')

    def _parse_data(self, html: str) -> dict:
        """HTML을 파싱하여 핵심 데이터를 추출합니다."""
        soup = BeautifulSoup(html, 'html.parser')
        parsed_data = self._parse_dashboard_html(soup)
        if parsed_data is None:
            return self._get_error_data("HTML 파싱 실패 (new parser)")
        parsed_data['mission_date'] = self._get_mission_date()
        return parsed_data

    def _parse_dashboard_html(self, soup):
        """새로운 대시보드 구조에 맞게 HTML을 파싱하는 함수"""
        try:
            data = {}
            int_pattern = re.compile(r'[\d,]+')
            float_pattern = re.compile(r'(\d+(?:\.\d+)?)')

            def fast_parse(selector, is_float=False, parent=None):
                base = parent if parent else soup
                node = base.select_one(selector)
                if not node: return 0.0 if is_float else 0
                text = node.get_text(strip=True)
                pattern = float_pattern if is_float else int_pattern
                match = pattern.search(text)
                if not match: return 0.0 if is_float else 0
                val_str = match.group(1) if is_float else match.group().replace(',', '')
                return float(val_str) if is_float else int(val_str)

            # 새로운 선택자 적용
            data['총점'] = fast_parse('.score_total_value[data-text="total"]')
            data['물량점수'] = fast_parse('.detail_score_value[data-text="quantity"]')
            data['수락률점수'] = fast_parse('.detail_score_value[data-text="acceptance"]')

            # etc_value는 span이 없음
            data['총완료'] = fast_parse('.etc_value[data-etc="complete"]')
            data['총거절'] = fast_parse('.etc_value[data-etc="reject"]')
            data['수락률'] = fast_parse('.etc_value[data-etc="acceptance"]', is_float=True)
            
            # 피크 타임 파싱 로직 변경
            peak_map = {'오전피크': '아침점심피크', '오후피크': '오후논피크', '저녁피크': '저녁피크', '심야피크': '심야논피크'}
            for item in soup.select('.quantity_item'):
                title_node = item.select_one('.quantity_title')
                info_node = item.select_one('.quantity_info')
                
                if title_node and info_node:
                    title_text = title_node.get_text(strip=True)
                    info_text = info_node.get_text(strip=True)
                    
                    if title_text in peak_map:
                        key = peak_map[title_text]
                        # "15 / 20" 같은 형식의 텍스트 파싱
                        parts = [p.strip() for p in info_text.split('/')]
                        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                            data[key] = {'current': int(parts[0]), 'target': int(parts[1])}
                        else:
                            data[key] = {'current': 0, 'target': 0}

            # 라이더 리스트는 새로운 HTML 구조를 확인해야 하므로 일단 비워둠
            data['riders'] = []
            logger.info("라이더 리스트 파싱은 새로운 HTML 구조 확인 후 진행해야 합니다.")

            data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return data
            
        except Exception as e:
            logger.error(f" HTML 파싱 실패: {e}", exc_info=True)
            return None

    def _get_weather_info_detailed(self, location="서울"):
        """상세 날씨 정보 (오전/오후) 가져오기"""
        try:
            url = f"https://wttr.in/{location}?format=j1"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            weather_data = response.json()
            
            am_temps, pm_temps = [], []
            am_icons, pm_icons = [], []

            weather_icon_map = {"Sunny": "", "Clear": "", "Partly cloudy": "", "Cloudy": "", "Overcast": "", "Mist": "", "Fog": "", "Patchy rain possible": "", "Light rain": "", "Rain": "", "Thundery outbreaks possible": "", "Thunderstorm": "", "Snow": "", "Blizzard": ""}
            def get_icon(desc):
                return next((icon for key, icon in weather_icon_map.items() if key in desc), "")

            for forecast in weather_data.get('weather', [{}])[0].get('hourly', []):
                hour = int(forecast.get('time', '0')) // 100
                temp = int(forecast.get('tempC', '0'))
                icon = get_icon(forecast.get('weatherDesc', [{}])[0].get('value', ''))
                
                if 6 <= hour < 12: (am_temps.append(temp), am_icons.append(icon))
                elif 12 <= hour < 18: (pm_temps.append(temp), pm_icons.append(icon))

            am_icon = max(set(am_icons), key=am_icons.count) if am_icons else ""
            pm_icon = max(set(pm_icons), key=pm_icons.count) if pm_icons else ""
            
            am_line = f" 오전: {am_icon} {min(am_temps)}~{max(am_temps)}C" if am_temps else ""
            pm_line = f" 오후: {pm_icon} {min(pm_temps)}~{max(pm_temps)}C" if pm_temps else ""
            
            return f" 오늘의 날씨 (기상청)\n{am_line}\n{pm_line}".strip()
        except Exception:
            return " 오늘의 날씨 (기상청)\n날씨 정보 조회 불가"

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
        data = self.data_collector.get_grider_data()
        if not data: return
        access_token = self.token_manager.get_valid_token()
        if not access_token: return
        message = self.format_message(data)
        KakaoSender(access_token).send_text_message(message)

    def _get_time_based_greeting(self, hour: int, minute: int) -> str:
        """시간대별 인사말 생성"""
        if hour == 10 and minute == 0: return " 좋은 아침입니다!\n오늘도 심플 배민 플러스와 함께 힘찬 하루를 시작해보세요!\n안전운행하시고 좋은 하루 되세요! "
        if hour == 0 and minute == 0: return " 오늘 하루도 정말 수고하셨습니다!\n안전하게 귀가하시고 푹 쉬세요.\n내일도 좋은 하루 되시길 바랍니다! "
        time_greetings = {
            (11, 30): " 점심 피크 시간이 다가오고 있어요!", (12, 0): " 정오 12시! 점심 피크 시작!",
            (17, 30): " 저녁 피크 시간! 주문이 많을 예정이에요!", (18, 0): " 저녁 6시! 저녁 식사 시간!",
            (23, 0): " 밤 11시! 하루 마무리가 다가와요!", (0, 30): " 오늘도 정말 수고하셨습니다!"
        }
        return time_greetings.get((hour, minute), f" {datetime.now(KST).strftime('%H:%M')} 현재 상황을 알려드립니다!")

    def format_message(self, data: dict) -> str:
        """사용자 정의 규칙에 따라 상세한 카카오톡 메시지를 생성합니다."""
        try:
            korea_time = self.data_collector._get_korea_time()
            is_holiday, _ = holiday_checker.is_holiday_advanced(korea_time)
            day_type = "휴일" if korea_time.weekday() >= 5 or is_holiday else "평일"

            greeting = self._get_time_based_greeting(korea_time.hour, korea_time.minute)
            header = f"{greeting}\n\n 심플 배민 플러스 미션 알리미 ({day_type})"

            mission_parts = ["\n 금일 미션 현황"]
            missions_behind_summary = []
            peak_emojis = {'아침점심피크': '', '오후논피크': '', '저녁피크': '', '심야논피크': ''}
            for key, emoji in peak_emojis.items():
                mission = data.get(key, {})
                current, target = mission.get('current', 0), mission.get('target', 0)
                if target > 0:
                    remaining = target - current
                    status = f" ({remaining}건 남음)" if '논피크' in key and remaining > 0 else f" ({remaining}건 부족)" if remaining > 0 else ''
                    if remaining > 0: missions_behind_summary.append(f"{key.replace('피크','').replace('논','')} {remaining}건")
                    mission_parts.append(f"{emoji} {key}: {current}/{target} {status}")

            weather_info = self.data_collector._get_weather_info_detailed()

            all_riders = data.get('riders', [])
            total_daily_complete = sum(r.get('complete', 0) for r in all_riders)
            total_daily_reject_cancel = sum(r.get('reject', 0) + r.get('cancel', 0) for r in all_riders)
            total_attempts = total_daily_complete + total_daily_reject_cancel
            daily_acceptance_rate = (total_daily_complete / total_attempts * 100) if total_attempts > 0 else 0.0
            
            daily_perf_parts = ["\n 금일 수행 내역", f"수락률: {daily_acceptance_rate:.1f}% | 완료: {total_daily_complete} | 거절: {total_daily_reject_cancel}"]
            
            weekly_score_parts = ["\n 금주 미션 수행 예상점수", f"총점: {data.get('총점', 0)}점 (물량:{data.get('물량점수', 0)}, 수락률:{data.get('수락률점수', 0)})"]

            riders = [r for r in all_riders if r.get('complete', 0) > 0]
            rider_parts = [f"\n 라이더 순위 (운행 : {len(riders)}명)"]
            if riders:
                sorted_riders = sorted(riders, key=lambda x: x.get('contribution', 0.0), reverse=True)
                medals = ['', '', '']
                for i, r in enumerate(sorted_riders[:10]):
                    name = r.get('name', '이름없음')
                    contribution = r.get('contribution', 0.0)
                    
                    bar_length = 10
                    filled_count = int(round(contribution / 100 * bar_length))
                    bar = '' * filled_count + '' * (10 - filled_count)
                    progress = f"[{bar}] {contribution:.1f}%"
                    
                    peak_counts = " ".join([f"{peak_emojis.get(p, '')}{r.get(p, 0)}" for p in peak_emojis])
                    
                    prefix = f"{medals[i]} {name}" if i < 3 else f"{i+1}. {name}"
                    line1 = f"**{prefix}** | {progress}"
                    line2 = f"    총 {r.get('complete', 0)}건 ({peak_counts})"
                    line3 = f"    수락률: {r.get('acceptance_rate', 0.0):.1f}% (거절:{r.get('reject', 0)}, 취소:{r.get('cancel', 0)})"
                    rider_parts.extend(["", line1, line2, line3])

            warning_part = [f"\n 미션 부족: {', '.join(missions_behind_summary)}"] if missions_behind_summary else []
            footer = "\n\n 자동화 시스템에 의해 전송됨"
            
            message_parts = [header] + mission_parts + [f"\n{weather_info}"] + daily_perf_parts + weekly_score_parts + rider_parts + warning_part + [footer]
            return "\n".join(filter(None, message_parts))

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
