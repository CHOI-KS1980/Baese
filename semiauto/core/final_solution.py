#!/usr/bin/env python3
"""
🎯 최종 검증된 솔루션: 카카오톡 나에게 보내기 + 수동 복사
- 웹 크롤링 → 데이터 가공 (자동)
- 카카오톡 나에게 보내기 (자동)
- 클립보드 자동 복사 (자동)
- 오픈채팅방 복사/붙여넣기 (수동 5초)
"""

import requests
import json
import time
from datetime import datetime, timedelta, time as dt_time
# pyperclip은 조건부 import (GitHub Actions 환경에서는 사용 불가)
import logging
import os
import re
import pytz  # 한국시간 설정을 위해 추가
from bs4 import BeautifulSoup  # BeautifulSoup import 추가
from xml.etree import ElementTree as ET  # 한국천문연구원 API용

from semiauto.utils import holiday_checker
from .data_collection import GriderDataCollector
from .kakao_sender import KakaoSender
from .token_manager import TokenManager

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
            logger.info("🇰🇷 한국천문연구원 특일 정보 API 공휴일 체커 초기화")
            self.load_year_holidays(datetime.now(KST).year)
        else:
            logger.info("⚠️ KOREA_HOLIDAY_API_KEY 환경변수가 설정되지 않음 - 기본 공휴일 사용")
    
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
                    date_name = item.find('dateName')
                    loc_date = item.find('locdate')
                    is_holiday = item.find('isHoliday')
                    
                    if date_name is not None and loc_date is not None:
                        holiday_name = date_name.text
                        holiday_date = loc_date.text
                        holiday_status = is_holiday.text if is_holiday is not None else 'Y'
                        
                        # 날짜 형식 변환
                        if len(holiday_date) == 8:
                            formatted_date = f"{holiday_date[:4]}-{holiday_date[4:6]}-{holiday_date[6:8]}"
                            holidays.append({
                                'date': formatted_date,
                                'name': holiday_name,
                                'is_holiday': holiday_status == 'Y'
                            })
                            logger.info(f"📅 공휴일 확인: {formatted_date} - {holiday_name}")
                
                return holidays
                
        except Exception as e:
            logger.error(f"❌ 공휴일 API 오류: {e}")
        
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
        logger.info(f"✅ {year}년 전체월 공휴일 {len(holidays)}개 로드 완료")
    
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
                return True, holiday['name']
        
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
        
        # 즉시 토큰 갱신 시도
        logger.info("🔄 TokenManager 초기화 - 토큰 갱신 시도")
        if not self.refresh_access_token():
            logger.error("❌ 초기 토큰 갱신 실패")
    
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
                # 액세스 토큰은 6시간 유효
                self.token_expires_at = datetime.now() + timedelta(hours=6)
                
                # 새로운 리프레시 토큰이 있으면 업데이트
                if 'refresh_token' in result:
                    self.refresh_token = result['refresh_token']
                
                # 토큰 파일 업데이트
                self.save_tokens()
                
                logger.info(f"✅ 토큰 갱신 완료: {self.access_token[:20]}...")
                return True
            else:
                logger.error(f"❌ 토큰 갱신 실패: {result}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 토큰 갱신 중 오류: {e}")
            return False
    
    def get_valid_token(self):
        """유효한 액세스 토큰 반환 (필요시 자동 갱신)"""
        if not self.access_token or self.is_token_expired():
            logger.info("🔄 토큰 갱신 시도...")
            if not self.refresh_access_token():
                logger.error("❌ 토큰 갱신 실패 - None 반환")
                return None
        
        logger.info(f"✅ 유효한 토큰 반환: {self.access_token[:20] if self.access_token else 'None'}...")
        return self.access_token
    
    def is_token_expired(self):
        """토큰 만료 여부 확인"""
        if not self.token_expires_at:
            return True
        
        # 만료 30분 전에 미리 갱신
        return datetime.now() >= (self.token_expires_at - timedelta(minutes=30))
    
    def save_tokens(self):
        """토큰을 파일에 저장"""
        try:
            with open('kakao_tokens.txt', 'w') as f:
                f.write(f"ACCESS_TOKEN={self.access_token}\n")
                f.write(f"REFRESH_TOKEN={self.refresh_token}\n")
                f.write(f"EXPIRES_AT={self.token_expires_at.isoformat()}\n")
        except Exception as e:
            logger.error(f"❌ 토큰 저장 실패: {e}")

class KakaoSender:
    """카카오톡 메시지 전송 클래스"""
    
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    
    def send_text_message(self, text, link_url=None):
        """텍스트 메시지 전송"""
        # 방법: 메시지 API 대신 친구에게 메시지 API 사용 시도
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
        
        # 나에게 보내기 API 사용 (다른 엔드포인트)
        url = 'https://kapi.kakao.com/v2/api/talk/memo/default/send'
        
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
            response = requests.post(url, headers=headers, data=data)
            return response.json()
        except Exception as e:
            logger.error(f"❌ 메시지 전송 중 오류: {e}")
            return {"error": str(e)}
    
    def send_feed_message(self, title, description, image_url, link_url):
        """피드 메시지 전송"""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
        
        template_object = {
            "object_type": "feed",
            "content": {
                "title": title,
                "description": description,
                "image_url": image_url,
                "image_width": 640,
                "image_height": 640,
                "link": {
                    "web_url": link_url,
                    "mobile_web_url": link_url
                }
            },
            "buttons": [
                {
                    "title": "자세히 보기",
                    "link": {
                        "web_url": link_url,
                        "mobile_web_url": link_url
                    }
                }
            ]
        }
        
        data = {
            'template_object': json.dumps(template_object, ensure_ascii=False)
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, data=data)
            return response.json()
        except Exception as e:
            logger.error(f"❌ 피드 메시지 전송 중 오류: {e}")
            return {"error": str(e)}

class GriderDataCollector:
    """심플 배민 플러스 데이터 수집 클래스"""
    
    def __init__(self):
        self.base_url = "https://grider.co.kr"  # 실제 URL로 변경 필요
        self.mission_data_cache_file = 'mission_data_cache.json'
    
    def get_grider_data(self):
        """G라이더 데이터 수집"""
        try:
            # 캐시된 데이터 확인
            korea_time = self._get_korea_time()
            
            # 🎯 미션 날짜 기준으로 캐시 확인
            mission_date = self._get_mission_date()
            cached_data = self._load_mission_data_cache()
            
            # GitHub Actions 또는 상위 스케줄러에서 이미 시간 검증을 했으므로
            # 여기서는 추가 시간 체크를 하지 않고 바로 크롤링 진행
            logger.info("🚀 스케줄러에서 검증된 실행 - 크롤링 진행")
            
            logger.info("🚀 G라이더 실제 데이터 수집 시작...")
            
            html = self._crawl_jangboo()
            if not html:
                logger.error("❌ 크롤링 실패 - HTML을 가져올 수 없습니다")
                # 크롤링 실패 시 None 반환 (에러 메시지 전송 방지)
                return None
            
            # HTML에서 데이터 파싱
            data = self._parse_data(html)
            
            if data.get('error'):
                logger.error(f"❌ 데이터 파싱 실패: {data.get('error_reason', '알 수 없는 오류')}")
                # 파싱 실패 시 None 반환 (에러 메시지 전송 방지)
                return None
            
            logger.info("✅ G라이더 데이터 수집 완료")
            return data
            
        except Exception as e:
            logger.error(f"❌ 크롤링 중 오류 발생: {e}")
            # 모든 예외 발생 시 None 반환 (에러 메시지 전송 방지)
            return None

    def _validate_data(self, data):
        """수집된 데이터가 유효한지 검증"""
        if not data:
            return False
        
        # 필수 필드 확인
        required_fields = ['총점', '총완료', '수락률']
        for field in required_fields:
            if field not in data:
                logger.warning(f"필수 필드 누락: {field}")
                return False
        
        # 데이터 범위 확인 (비정상적인 값 체크)
        if data.get('총점', 0) < 0 or data.get('총점', 0) > 200:
            logger.warning(f"비정상적인 총점: {data.get('총점')}")
            return False
            
        if data.get('수락률', 0) < 0 or data.get('수락률', 0) > 100:
            logger.warning(f"비정상적인 수락률: {data.get('수락률')}")
            return False
        
        return True

    def _get_error_data(self, error_reason):
        """크롤링 실패 시 오류 메시지가 포함된 데이터"""
        return {
            '총점': 0,
            '물량점수': 0,
            '수락률점수': 0,
            '총완료': 0,
            '총거절': 0,
            '수락률': 0.0,
            '아침점심피크': {"current": 0, "target": 0},
            '오후논피크': {"current": 0, "target": 0},
            '저녁피크': {"current": 0, "target": 0},
            '심야논피크': {"current": 0, "target": 0},
            'riders': [],
            'error': True,
            'error_reason': error_reason,
            'timestamp': datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _crawl_jangboo(self, max_retries=3, retry_delay=5):
        """최적화된 크롤링 함수 (main_(2).py와 동일한 로직)"""
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        
        start_time = time.time()
        driver = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"크롤링 시도 {attempt + 1}/{max_retries}")
                
                # Chrome 옵션 설정 (main_(2).py와 동일)
                options = Options()
                
                # CloudFlare 우회를 위한 강화된 설정
                user_agents = [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
                
                chrome_args = [
                    '--headless=new',  # 새로운 headless 모드
                    '--no-sandbox', 
                    '--disable-dev-shm-usage',
                    '--disable-gpu', 
                    '--disable-images', 
                    '--memory-pressure-off',
                    '--max_old_space_size=4096', 
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor', 
                    '--disable-extensions',
                    '--no-first-run', 
                    '--ignore-certificate-errors', 
                    '--ignore-ssl-errors',
                    '--ignore-certificate-errors-spki-list',
                    # CloudFlare 우회 강화
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=VizDisplayCompositor',
                    '--user-agent=' + user_agents[attempt % len(user_agents)],
                    '--accept-language=ko-KR,ko;q=0.9,en;q=0.8',
                    '--accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    '--accept-encoding=gzip, deflate, br',
                    '--sec-fetch-dest=document',
                    '--sec-fetch-mode=navigate',
                    '--sec-fetch-site=none',
                    '--sec-fetch-user=?1',
                    '--upgrade-insecure-requests=1',
                    '--window-size=1920,1080',
                    '--viewport-size=1920,1080'
                ]
                
                for arg in chrome_args:
                    options.add_argument(arg)
                
                # 실험적 옵션 추가 (봇 감지 방지)
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                
                driver = webdriver.Chrome(options=options)
                
                # 봇 감지 방지 스크립트 실행
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                driver.set_page_load_timeout(60)  # 타임아웃 더 늘림
                driver.implicitly_wait(15)  # 암시적 대기 늘림
                
                # 로그인 페이지 로드 (안정적인 단일 URL로 직접 접근)
                LOGIN_URL = 'https://jangboo.grider.ai/login'
                logger.info(f"로그인 페이지 직접 접속 시도: {LOGIN_URL}")
                
                try:
                    driver.get(LOGIN_URL)
                    # CloudFlare 또는 페이지 로딩 대기
                    time.sleep(5)

                    # 만약의 경우를 대비한 현재 URL 확인
                    if "grider" not in driver.current_url.lower():
                        raise Exception(f"예상과 다른 페이지로 이동됨: {driver.current_url}")
                    
                    logger.info(f"✅ 로그인 페이지 접속 성공: {driver.current_url}")

                except Exception as access_error:
                    logger.error(f"❌ 로그인 페이지 접속 실패: {access_error}")
                    # 실패 시 재시도 로직으로 넘어감
                    raise access_error

                # 페이지 로드 완료 확인
                current_url = driver.current_url.lower()
                page_title = driver.title
                
                logger.info(f"📄 현재 페이지 정보:")
                logger.info(f"   URL: {driver.current_url}")
                logger.info(f"   제목: {page_title}")
                
                # 에러 페이지 감지
                if any(keyword in page_title.lower() for keyword in ['error', 'not satisfied', 'cloudflare', 'access denied']):
                    # 페이지 소스 저장하여 문제 분석
                    error_html = driver.page_source
                    with open(f'debug_error_page_{attempt + 1}.html', 'w', encoding='utf-8') as f:
                        f.write(error_html)
                    
                    raise Exception(f"접근 차단 감지: {page_title}")
                
                if "grider" not in current_url:
                    raise Exception(f"예상과 다른 페이지 로드: {driver.current_url}")

                # 로그인 처리
                logger.info("로그인 시도")
                
                # 환경변수 또는 config.txt에서 로그인 정보 가져오기
                import os
                USER_ID = None # os.getenv('GRIDER_ID')
                USER_PW = None # os.getenv('GRIDER_PASSWORD')
                
                logger.info(f"🔍 config.txt 우선 읽기 모드로 변경됨.")
                # logger.info(f"   • GRIDER_ID 존재: {'있음' if USER_ID else '없음'}")
                # logger.info(f"   • GRIDER_PASSWORD 존재: {'있음' if USER_PW else '없음'}")
                # if USER_ID:
                #     logger.info(f"   • GRIDER_ID 값: {USER_ID[:3]}***")
                
                # 환경변수가 없으면 config.txt에서 읽기
                if not USER_ID or not USER_PW:
                    config_file = 'config.txt'
                    if os.path.exists(config_file):
                        try:
                            # UTF-8 인코딩으로 파일 읽기
                            with open(config_file, 'r', encoding='utf-8') as f:
                                for line in f:
                                    if line.startswith('GRIDER_ID='):
                                        USER_ID = line.split('=')[1].strip()
                                    elif line.startswith('GRIDER_PASSWORD='):
                                        USER_PW = line.split('=')[1].strip()
                        except UnicodeDecodeError:
                            # UTF-8 실패시 다른 인코딩 시도
                            try:
                                with open(config_file, 'r', encoding='cp949') as f:
                                    for line in f:
                                        if line.startswith('GRIDER_ID='):
                                            USER_ID = line.split('=')[1].strip()
                                        elif line.startswith('GRIDER_PASSWORD='):
                                            USER_PW = line.split('=')[1].strip()
                            except:
                                logger.error("❌ config.txt 파일 인코딩 오류")
                
                if not USER_ID or not USER_PW:
                    raise Exception("G라이더 로그인 정보가 설정되지 않았습니다. GRIDER_ID와 GRIDER_PASSWORD를 확인하세요.")
                
                # 여러 선택자 시도 (웹사이트 구조 변경 대응)
                id_field = None
                pw_field = None
                login_btn = None
                
                # ID 필드 찾기 (여러 선택자 시도)
                id_selectors = ['#id', '[name="id"]', '[id="id"]', 'input[type="text"]', '.login-id', '#userId', '[name="userId"]']
                for selector in id_selectors:
                    try:
                        if selector.startswith('#') or selector.startswith('.'):
                            id_field = driver.find_element(By.CSS_SELECTOR, selector)
                        elif selector.startswith('['):
                            id_field = driver.find_element(By.CSS_SELECTOR, selector)
                        else:
                            id_field = driver.find_element(By.ID, selector)
                        logger.info(f"✅ ID 필드 발견: {selector}")
                        break
                    except:
                        continue
                
                # 비밀번호 필드 찾기
                pw_selectors = ['#password', '[name="password"]', '[id="password"]', 'input[type="password"]', '.login-password', '#userPw', '[name="userPw"]']
                for selector in pw_selectors:
                    try:
                        if selector.startswith('#') or selector.startswith('.'):
                            pw_field = driver.find_element(By.CSS_SELECTOR, selector)
                        elif selector.startswith('['):
                            pw_field = driver.find_element(By.CSS_SELECTOR, selector)
                        else:
                            pw_field = driver.find_element(By.ID, selector)
                        logger.info(f"✅ 비밀번호 필드 발견: {selector}")
                        break
                    except:
                        continue
                
                # 로그인 버튼 찾기
                btn_selectors = ['#loginBtn', '[id="loginBtn"]', 'button[type="submit"]', '.login-btn', '.btn-login', 'input[type="submit"]']
                for selector in btn_selectors:
                    try:
                        if selector.startswith('#') or selector.startswith('.'):
                            login_btn = driver.find_element(By.CSS_SELECTOR, selector)
                        elif selector.startswith('['):
                            login_btn = driver.find_element(By.CSS_SELECTOR, selector)
                        else:
                            login_btn = driver.find_element(By.ID, selector)
                        logger.info(f"✅ 로그인 버튼 발견: {selector}")
                        break
                    except:
                        continue
                
                if not id_field:
                    raise Exception("ID 입력 필드를 찾을 수 없습니다. 웹사이트 구조가 변경되었을 가능성이 있습니다.")
                if not pw_field:
                    raise Exception("비밀번호 입력 필드를 찾을 수 없습니다.")
                if not login_btn:
                    raise Exception("로그인 버튼을 찾을 수 없습니다.")
                
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
                
                # 🎯 날짜별 데이터 조회 로직 추가
                target_date = self._get_mission_date()
                logger.info(f"🎯 타겟 미션 날짜: {target_date}")
                
                # 날짜별 데이터 조회 시도
                html = self._navigate_to_date_data(driver, target_date)
                
                if len(html) < 1000:  # HTML이 너무 짧으면 실패로 판단
                    raise Exception("HTML 길이가 너무 짧습니다. 페이지 로딩 실패 가능성")
                
                # 디버깅용 HTML 저장
                with open('debug_grider_page.html', 'w', encoding='utf-8') as f:
                    f.write(html)
                logger.info("📄 디버깅용 페이지 소스를 debug_grider_page.html에 저장했습니다")
                
                logger.info(f"✅ 크롤링 성공 (시도: {attempt + 1}/{max_retries}, 소요시간: {time.time() - start_time:.2f}초)")
                return html
                
            except Exception as e:
                logger.error(f"❌ 크롤링 시도 {attempt + 1} 실패: {e}")
                
                # 디버깅 정보 수집
                if driver:
                    try:
                        current_url = driver.current_url
                        page_title = driver.title
                        page_source_length = len(driver.page_source)
                        
                        logger.error(f"🔍 디버깅 정보:")
                        logger.error(f"   현재 URL: {current_url}")
                        logger.error(f"   페이지 제목: {page_title}")
                        logger.error(f"   페이지 소스 길이: {page_source_length}")
                        
                        # 실패한 페이지 소스 저장
                        with open(f'debug_failed_page_{attempt + 1}.html', 'w', encoding='utf-8') as f:
                            f.write(driver.page_source)
                        logger.error(f"   실패한 페이지 소스 저장: debug_failed_page_{attempt + 1}.html")
                        
                        # 로그인 필드 존재 여부 확인
                        try:
                            login_elements = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"], input[type="password"], input[id*="id"], input[name*="id"]')
                            logger.error(f"   발견된 입력 필드 수: {len(login_elements)}")
                            for i, elem in enumerate(login_elements[:5]):  # 최대 5개만 표시
                                try:
                                    logger.error(f"   필드 {i+1}: tag={elem.tag_name}, id={elem.get_attribute('id')}, name={elem.get_attribute('name')}, type={elem.get_attribute('type')}")
                                except:
                                    pass
                        except:
                            logger.error("   입력 필드 확인 실패")
                            
                    except Exception as debug_e:
                        logger.error(f"   디버깅 정보 수집 실패: {debug_e}")
                    
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
                    logger.error("🚨 크롤링 실패 - 대체 데이터로 메시지를 전송합니다")
                    
            finally:
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
        
        return None

    def _navigate_to_date_data(self, driver, target_date: str) -> str:
        """URL 파라미터 방식으로 날짜별 데이터 조회"""
        
        logger.info(f"🔍 날짜별 데이터 조회 시작: {target_date}")
        
        try:
            # URL 파라미터 방식으로 날짜 조회 시도 (가장 안정적)
            logger.info("🔄 URL 파라미터 방식으로 날짜 조회 시도")
            
            base_url = "https://jangboo.grider.ai/dashboard"
            url_with_date = f"{base_url}?date={target_date}"
            
            logger.info(f"Navigating to: {url_with_date}")
            driver.get(url_with_date)
            time.sleep(5) # 데이터 로딩 대기

            if self._verify_date_in_html(driver.page_source, target_date):
                logger.info(f"✅ URL 파라미터 방식 성공: ?date={target_date}")
                return driver.page_source
            else:
                raise Exception("URL 파라미터 방식 후 날짜 검증 실패")

        except Exception as e:
            logger.error(f"❌ 날짜별 데이터 조회 중 심각한 오류 발생: {e}")
            
            # 실패 시 디버깅 정보 저장
            error_html = driver.page_source
            with open(f'debug_date_nav_failed.html', 'w', encoding='utf-8') as f:
                f.write(error_html)
            
            return ""

    def _verify_date_in_html(self, html: str, target_date: str) -> bool:
        """HTML 내용에서 날짜를 확인하여 정확한 페이지인지 검증"""
        try:
            # 다양한 날짜 포맷으로 검증
            date_variations = [
                target_date,  # 2025-06-26
                target_date.replace('-', '.'),  # 2025.06.26
                target_date.replace('-', '/'),  # 2025/06/26
            ]
            
            found_dates = []
            for date_format in date_variations:
                if date_format in html:
                    found_dates.append(date_format)
            
            if found_dates:
                logger.info(f"✅ HTML에서 발견된 날짜 포맷: {found_dates}")
                return True
            else:
                logger.warning(f"⚠️ HTML에서 타겟 날짜({target_date}) 관련 텍스트를 찾을 수 없습니다")
                date_patterns = re.findall(r'\d{4}[-./]\d{1,2}[-./]\d{1,2}', html)
                if date_patterns:
                    logger.info(f"🔍 HTML에서 발견된 날짜 패턴들: {set(date_patterns[:5])}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 날짜 검증 중 오류: {e}")
            return False

    def _get_korea_time(self):
        """한국시간 기준 현재 시간 반환"""
        try:
            import pytz
            korea_tz = pytz.timezone('Asia/Seoul')
            return datetime.now(korea_tz)
        except ImportError:
            # pytz가 없으면 UTC+9로 계산
            utc_now = datetime.utcnow()
            return utc_now + timedelta(hours=9)

    def _is_cache_valid_for_current_time(self):
        """현재 시간 기준으로 캐시가 유효한지 확인"""
        try:
            if not os.path.exists(self.mission_data_cache_file):
                return False
            
            with open(self.mission_data_cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 캐시 생성 시간 확인
            cache_timestamp = cache_data.get('timestamp')
            if not cache_timestamp:
                return False
            
            cache_time = datetime.fromisoformat(cache_timestamp.replace('Z', '+00:00'))
            current_time = self._get_korea_time()
            
            # 캐시가 1시간 이내에 생성되었는지 확인
            time_diff = (current_time - cache_time.replace(tzinfo=current_time.tzinfo)).total_seconds()
            
            if time_diff < 3600:  # 1시간 = 3600초
                logger.info(f"✅ 캐시 유효 (생성 {time_diff/60:.1f}분 전)")
                return True
            else:
                logger.info(f"⏰ 캐시 만료 (생성 {time_diff/60:.1f}분 전)")
                return False
                
        except Exception as e:
            logger.error(f"❌ 캐시 유효성 확인 실패: {e}")
            return False

    def _validate_peak_data_with_date(self, peak_data: dict, target_date: str, html: str) -> dict:
        """파싱된 피크 데이터를 한국시간 기준으로 검증"""
        try:
            validation_result = {
                'is_valid': True,
                'reason': '',
                'message': '',
                'suggestion': ''
            }
            
            # 1. 기본 데이터 구조 검증
            required_peaks = ['아침점심피크', '오후논피크', '저녁피크', '심야논피크']
            missing_peaks = [peak for peak in required_peaks if peak not in peak_data]
            
            if missing_peaks:
                validation_result['is_valid'] = False
                validation_result['reason'] = f"필수 피크 데이터 누락: {missing_peaks}"
                validation_result['suggestion'] = "테이블 파싱 로직 확인 필요"
                return validation_result
            
            # 2. 데이터 값 유효성 검증
            total_current = sum(peak_data[peak].get('current', 0) for peak in required_peaks)
            total_target = sum(peak_data[peak].get('target', 0) for peak in required_peaks)
            
            if total_current == 0 and total_target == 0:
                validation_result['is_valid'] = False
                validation_result['reason'] = "모든 피크 데이터가 0입니다"
                validation_result['suggestion'] = "올바른 날짜 데이터가 파싱되었는지 확인 필요"
                return validation_result
            
            # 3. 시간대별 데이터 합리성 검증
            korea_time = self._get_korea_time()
            current_hour = korea_time.hour
            
            # 현재 시간에 따른 예상 패턴 검증
            expected_pattern = self._get_expected_data_pattern(current_hour)
            
            # 4. HTML에서 직접 날짜 재검증
            html_date_valid = self._verify_date_in_html(html, target_date)
            if not html_date_valid:
                validation_result['is_valid'] = False
                validation_result['reason'] = f"HTML에서 타겟 날짜({target_date}) 확인 실패"
                validation_result['suggestion'] = "G라이더 웹사이트에서 올바른 날짜로 조회되었는지 확인"
                return validation_result
            
            # 5. 어제 데이터 패턴 감지
            yesterday = (korea_time - timedelta(days=1)).strftime('%Y-%m-%d')
            if self._verify_date_in_html(html, yesterday):
                validation_result['is_valid'] = False
                validation_result['reason'] = f"어제 날짜({yesterday}) 데이터가 감지됨"
                validation_result['suggestion'] = "G라이더 웹사이트에서 날짜 선택기를 통해 오늘 날짜로 변경 필요"
                return validation_result
            
            # 모든 검증 통과
            validation_result['message'] = f"타겟 날짜({target_date}) 데이터 검증 완료 (총 {total_current}/{total_target}건)"
            return validation_result
            
        except Exception as e:
            logger.error(f"❌ 데이터 검증 중 오류: {e}")
            return {
                'is_valid': False,
                'reason': f"검증 중 오류 발생: {e}",
                'message': '',
                'suggestion': '검증 로직 확인 필요'
            }

    def _get_expected_data_pattern(self, current_hour: int) -> dict:
        """현재 시간에 맞는 피크 데이터 패턴 반환"""
        # 이 기능은 현재 사용되지 않으며, 단순화를 위해 남겨둠
        return {"아침점심피크": (0, 0), "오후논피크": (0, 0), "저녁피크": (0, 0), "심야논피크": (0, 0)}

    def _get_sample_data(self):
        """테스트용 샘플 데이터 반환 (실제 크롤링 없이)"""
        return {} # 내용을 비워 단순화

    def _parse_data(self, html: str) -> dict:
        """HTML을 파싱하여 최종 데이터 구조를 반환합니다."""
        if not html:
            return self._get_error_data("HTML 내용 없음")

        soup = BeautifulSoup(html, 'html.parser')
        
        # 각 부분별 데이터 파싱
        score_data = self._parse_score_data(soup)
        mission_data = self._parse_mission_data(soup)
        riders_data = self._parse_riders_data(soup)
        
        # 데이터 종합
        final_data = {**score_data, **mission_data, "riders": riders_data}
        
        # 타임스탬프 추가
        korea_now = self._get_korea_time()
        final_data.update({
            "timestamp": korea_now.isoformat(),
            "mission_date": self._get_mission_date(),
            "crawl_time": korea_now.strftime("%Y-%m-%d %H:%M:%S")
        })
        
        logger.info(f"데이터 파싱 완료: 총점={final_data['총점']}, 라이더={len(final_data['riders'])}명")
        return final_data

    def _parse_score_data(self, soup: BeautifulSoup) -> dict:
        """점수, 완료/거절/취소 건수, 수락률을 파싱합니다."""
        def get_int(selector):
            node = soup.select_one(selector)
            return int(re.sub(r'[^0-9]', '', node.text)) if node and node.text else 0

        data = {
            "총점": get_int('.total_score_text > strong'),
            "물량점수": get_int('.delivery_score_text > strong'),
            "수락률점수": get_int('.acceptance_rate_text > strong'),
            "총완료": 0, "총거절": 0, "총취소": 0, "수락률": 100.0
        }

        for item in soup.select('.statics_box .statics_item'):
            title_node = item.select_one('.title')
            value_node = item.select_one('.value')
            if title_node and value_node:
                title = title_node.text.strip()
                value = int(re.sub(r'[^0-9]', '', value_node.text) or 0)
                if '완료' in title: data['총완료'] = value
                elif '거절' in title: data['총거절'] = value
                elif '취소' in title: data['총취소'] = value
        
        if (total_requests := data['총완료'] + data['총거절']) > 0:
            data['수락률'] = round((data['총완료'] / total_requests * 100), 2)
            
        return data

    def _parse_mission_data(self, soup: BeautifulSoup) -> dict:
        """미션별 완료/목표 건수를 파싱합니다."""
        missions = {'아침점심피크': {}, '오후논피크': {}, '저녁피크': {}, '심야논피크': {}}
        mission_keys = list(missions.keys())

        for i, item in enumerate(soup.select('.quantity_item')):
            if i >= len(mission_keys): break
            try:
                current_node = item.select_one('.performance_value')
                target_node = item.select_one('.number_value span:not(.performance_value)')
                missions[mission_keys[i]] = {
                    "current": int(re.sub(r'[^0-9]', '', current_node.text)) if current_node else 0,
                    "target": int(re.sub(r'[^0-9]', '', target_node.text)) if target_node else 0
                }
            except (AttributeError, ValueError, TypeError) as e:
                logger.warning(f"{mission_keys[i]} 파싱 실패: {e}")
                missions[mission_keys[i]] = {"current": 0, "target": 0}
        return missions

    def _parse_riders_data(self, soup: BeautifulSoup) -> list:
        """라이더 목록 및 상세 정보를 파싱합니다."""
        riders = []
        rider_list = soup.select_one('.rider_list')
        if not rider_list: return riders

        for item in rider_list.select('.item'):
            try:
                complete_node = item.select_one('.count')
                complete_count = int(complete_node.text) if complete_node and complete_node.text.isdigit() else 0
                if complete_count > 0:
                    name_node = item.select_one('.name')
                    rate_node = item.select_one('.acceptance_rate .rate')
                    status_node = item.select_one('.status')
                    counts = [int(n.text) for n in item.select('.count') if n.text.isdigit()]
                    riders.append({
                        'name': name_node.text.strip() if name_node else 'N/A',
                        'complete': complete_count,
                        'reject': counts[1] if len(counts) > 1 else 0,
                        'cancel': counts[2] if len(counts) > 2 else 0,
                        'acceptance_rate': float(re.sub(r'[^0-9.]', '', rate_node.text) or 0) if rate_node else 0.0,
                        'status': status_node.text.strip() if status_node else 'N/A'
                    })
            except Exception as e:
                logger.warning(f"라이더 파싱 중 오류: {e}")
                continue
        return riders

    def _save_mission_data_cache(self, mission_date, peak_data):
        """오늘의 미션 데이터 캐시 저장"""
        try:
            cache_data = {
                'date': mission_date,
                'timestamp': datetime.now().isoformat(),
                'peak_data': peak_data
            }
            
            with open(self.mission_data_cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 미션 데이터 캐시 저장 완료: {mission_date}")
            
        except Exception as e:
            logger.error(f"❌ 미션 데이터 캐시 저장 실패: {e}")

    def _load_mission_data_cache(self):
        """캐시된 미션 데이터 로드"""
        try:
            if not os.path.exists(self.mission_data_cache_file):
                logger.info("📂 미션 데이터 캐시 파일이 없습니다.")
                return None
            
            with open(self.mission_data_cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 캐시된 데이터의 날짜 확인
            cached_date = cache_data.get('date')
            current_mission_date = self._get_mission_date()
            
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

    def _get_mission_date(self):
        """한국시간 기준 현재 미션 날짜 반환 (06시 기준)"""
        korea_time = self._get_korea_time()
        if korea_time.hour < 6:
            return (korea_time - timedelta(days=1)).strftime('%Y-%m-%d')
        return korea_time.strftime('%Y-%m-%d')

    def _is_message_time(self):
        """15분 간격 전송 시간인지 확인"""
        # 이 기능은 enhanced_scheduler.py로 이전됨
        return True

    def _parse_grider_html_old(self, soup):
        """(사용되지 않음) 구버전 HTML 파싱 함수"""
        try:
            data = {}
            
            # main_(2).py의 검증된 선택자 사용
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

            # 검증된 선택자 사용 (main_(2).py와 동일)
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
            
            # 기본 점수 정보
            data['총점'] = results['total_score']
            data['물량점수'] = results['quantity_score']
            data['수락률점수'] = results['acceptance_score']
            data['총완료'] = results['total_complete']
            data['총거절'] = results['total_reject']
            data['수락률'] = results['acceptance_rate_total']
            
            logger.info(f"기본 점수 파싱 성공: 총점={data['총점']}, 물량={data['물량점수']}, 수락률={data['수락률점수']}")
            
            # 미션 데이터 파싱 (main_(2).py 로직 적용)
            peak_data = {}
            quantity_items = soup.select('.quantity_item')
            logger.info(f"quantity_item 요소 {len(quantity_items)}개 발견")
            
            if quantity_items:
                # 통일된 용어 사용
                web_peak_names = ['아침점심피크', '오후논피크', '저녁피크', '심야논피크']
                
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
                                'target': target
                            }
                            logger.info(f"미션 파싱 성공: {name} = {current}/{target}건")
                            
                    except Exception as e:
                        logger.warning(f"미션 아이템 {idx} 파싱 실패: {e}")
                        continue
            
            # 파싱된 미션 데이터를 data에 추가
            if peak_data:
                data.update(peak_data)
                logger.info("✅ 실제 미션 데이터 파싱 성공!")
            else:
                # 파싱 실패 시 기본값
                data['아침점심피크'] = {"current": 0, "target": 0}
                data['오후논피크'] = {"current": 0, "target": 0}
                data['저녁피크'] = {"current": 0, "target": 0}
                data['심야논피크'] = {"current": 0, "target": 0}
                logger.warning("미션 데이터 파싱 실패 - 기본값 사용")
            
            # 라이더 데이터 파싱 (main_(2).py 로직 적용)
            riders = []
            rider_items = soup.select('.rider_item')
            logger.info(f"라이더 아이템 {len(rider_items)}개 발견")
            
            for rider in rider_items:
                try:
                    rider_data = {}
                    
                    # 라이더 이름
                    name_node = rider.select_one('.rider_name')
                    if name_node:
                        rider_data['name'] = name_node.text.strip().split('수락률')[0].strip()
                    else:
                        rider_data['name'] = '이름없음'
                    
                    # 완료 건수
                    complete_node = rider.select_one('.complete_count')
                    if complete_node:
                        complete_text = complete_node.text
                        complete_match = re.search(r'\d+', complete_text)
                        rider_data['complete'] = int(complete_match.group()) if complete_match else 0
                    else:
                        rider_data['complete'] = 0
                    
                    # 수락률
                    acceptance_rate = 0.0
                    acc_node = rider.select_one('.rider_contents.acceptance_rate')
                    if acc_node:
                        acc_text = acc_node.get_text()
                        match = re.search(r'(\d+(?:\.\d+)?)\s*%', acc_text)
                        if match:
                            acceptance_rate = float(match.group(1))
                    rider_data['acceptance_rate'] = acceptance_rate
                    
                    # 거절 건수
                    reject = 0
                    reject_node = rider.select_one('.rider_contents.reject_count')
                    if reject_node:
                        reject_text = reject_node.get_text()
                        match = re.search(r'(\d+)', reject_text)
                        if match:
                            reject = int(match.group(1))
                    rider_data['reject'] = reject
                    
                    # 배차취소 건수
                    cancel = 0
                    cancel_node = rider.select_one('.rider_contents.accept_cancel_count')
                    if cancel_node:
                        cancel_text = cancel_node.get_text()
                        match = re.search(r'(\d+)', cancel_text)
                        if match:
                            cancel = int(match.group(1))
                    rider_data['cancel'] = cancel
                    
                    # 피크별 건수 파싱 (main_(2).py와 동일한 선택자 사용)
                    morning_node = rider.select_one('.morning_peak_count')
                    afternoon_node = rider.select_one('.afternoon_peak_count')
                    evening_node = rider.select_one('.evening_peak_count')
                    midnight_node = rider.select_one('.midnight_peak_count')  # night -> midnight
                    
                    morning = 0
                    afternoon = 0
                    evening = 0
                    midnight = 0
                    
                    if morning_node:
                        match = re.search(r'\d+', morning_node.text)
                        morning = int(match.group()) if match else 0
                    
                    if afternoon_node:
                        match = re.search(r'\d+', afternoon_node.text)
                        afternoon = int(match.group()) if match else 0
                    
                    if evening_node:
                        match = re.search(r'\d+', evening_node.text)
                        evening = int(match.group()) if match else 0
                    
                    if midnight_node:
                        match = re.search(r'\d+', midnight_node.text)
                        midnight = int(match.group()) if match else 0
                    
                    # 통일된 용어와 기존 호환성 모두 저장
                    rider_data['아침점심피크'] = morning
                    rider_data['오후논피크'] = afternoon
                    rider_data['저녁피크'] = evening
                    rider_data['심야논피크'] = midnight
                    
                    # 기존 호환성 유지
                    rider_data['오전피크'] = morning
                    rider_data['오후피크'] = afternoon
                    rider_data['심야피크'] = midnight
                    
                    if rider_data['complete'] > 0:  # 완료 건수가 있는 라이더만 추가
                        riders.append(rider_data)
                        logger.info(f"라이더 파싱 성공: {rider_data['name']} ({rider_data['complete']}건)")
                        
                except Exception as e:
                    logger.warning(f"라이더 데이터 파싱 실패: {e}")
                    continue
            
            # 라이더별 미션 기여도 계산 (main_(2).py와 동일한 로직)
            peak_names = ['오전피크', '오후피크', '저녁피크', '심야피크']
            for rider in riders:
                peak_contributions = []
                
                for peak in peak_names:
                    # 해당 피크의 목표값 가져오기
                    peak_mapping = {
                        '오전피크': '아침점심피크',
                        '오후피크': '오후논피크', 
                        '저녁피크': '저녁피크',
                        '심야피크': '심야논피크'
                    }
                    mapped_peak = peak_mapping.get(peak, peak)
                    target = data.get(mapped_peak, {'target': 0}).get('target', 0)
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
            
            data['riders'] = riders
            data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            logger.info(f"✅ 전체 데이터 파싱 완료: 기본정보, 미션 {len(peak_data)}개, 라이더 {len(riders)}명")
            # 라이더별 기여도 로그 (f-string 오류 방지)
            rider_contributions = [f"{r['name']}({r['contribution']:.1f}%)" for r in riders[:3]]
            logger.info(f"라이더별 기여도 계산 완료: {rider_contributions}")
            return data
            
        except Exception as e:
            logger.error(f"❌ HTML 파싱 실패: {e}")
            return None

class GriderAutoSender:
    """G-Rider 자동화 메인 클래스"""

    def __init__(self, rest_api_key=None, refresh_token=None):
        """초기화. API 키가 없으면 설정 파일에서 로드합니다."""
        if not rest_api_key or not refresh_token:
            key, token = load_config()
            rest_api_key, refresh_token = key, token
        
        if not rest_api_key or not refresh_token:
            raise ValueError("❌ 카카오 API 설정(REST_API_KEY, REFRESH_TOKEN)이 필요합니다.")

        self.token_manager = TokenManager(rest_api_key, refresh_token)
        self.data_collector = GriderDataCollector()

    def send_report(self):
        data = self.data_collector.get_grider_data()
        if not data: return
        access_token = self.token_manager.get_valid_token()
        if not access_token: return
        message = self.format_message(data)
        KakaoSender(access_token).send_text_message(message)

    def format_message(self, data: dict) -> str:
        """수집된 데이터를 상세한 카카오톡 메시지 형식으로 변환합니다."""
        try:
            korea_time = self.data_collector._get_korea_time()
            is_weekend_or_holiday = korea_time.weekday() >= 5 or holiday_checker.is_holiday_advanced(korea_time)[0]
            day_type = "휴일" if is_weekend_or_holiday else "평일"

            # 1. 헤더 (인사말, 날짜)
            greeting = "📊 G-Rider 실시간 현황"
            header = f"{greeting}\n📅 {korea_time.strftime('%Y-%m-%d %H:%M')} ({day_type})"

            # 2. 미션 현황
            mission_parts = ["\n🎯 금일 미션 현황"]
            peak_order = ['아침점심피크', '오후논피크', '저녁피크', '심야논피크']
            peak_emojis = {'아침점심피크': '🌅', '오후논피크': '🌇', '저녁피크': '🌃', '심야논피크': '🌙'}
            
            for key in peak_order:
                mission = data.get(key, {})
                current = mission.get('current', 0)
                target = mission.get('target', 0)
                if target > 0:
                    status = '✅' if current >= target else f'⏳ {target - current}건'
                    mission_parts.append(f"{peak_emojis.get(key, '')} {key}: {current}/{target} {status}")

            # 3. 종합 점수 및 요약
            summary_parts = [
                "\n📊 종합 점수",
                f"총점: {data.get('총점', 0)} (물량:{data.get('물량점수', 0)}, 수락률:{data.get('수락률점수', 0)})",
                f"수락률: {data.get('수락률', 0.0):.1f}% | 완료: {data.get('총완료', 0)} | 거절: {data.get('총거절', 0)}"
            ]

            # 4. 라이더 순위 (핵심 복원)
            riders = data.get('riders', [])
            rider_parts = [f"\n🏆 라이더 순위 (운행: {len(riders)}명)"]
            if riders:
                sorted_riders = sorted(riders, key=lambda x: x.get('complete', 0), reverse=True)
                medals = ['🥇', '🥈', '🥉']

                for i, rider in enumerate(sorted_riders[:10]):  # 상위 10명까지 표시
                    name = rider.get('name', 'N/A')
                    complete = rider.get('complete', 0)
                    acceptance = rider.get('acceptance_rate', 0.0)
                    prefix = f"{medals[i]} " if i < 3 else f"{i+1}. "
                    rider_parts.append(f"{prefix}{name}: {complete}건 (수락률: {acceptance:.1f}%)")

            # 최종 조합
            full_message = "\n".join([header] + mission_parts + summary_parts + rider_parts)
            return full_message

        except Exception as e:
            logger.error(f"❌ 메시지 포맷팅 실패: {e}")
            return "리포트 생성 중 오류가 발생했습니다."

def load_config():
    """설정 파일 또는 환경변수에서 로드"""
    import os
    
    # GitHub Actions 환경변수에서 먼저 시도
    rest_api_key = os.getenv('KAKAO_REST_API_KEY') or os.getenv('REST_API_KEY')
    refresh_token = os.getenv('KAKAO_REFRESH_TOKEN') or os.getenv('REFRESH_TOKEN')
    
    if rest_api_key and refresh_token:
        logger.info("✅ 환경변수에서 카카오 API 키 로드 완료")
        logger.info(f"   • REST_API_KEY: {rest_api_key[:10]}...")
        logger.info(f"   • REFRESH_TOKEN: {refresh_token[:10]}...")
        return rest_api_key, refresh_token
    
    config_file = 'config.txt'
    if not os.path.exists(config_file):
        logger.error(f"❌ 설정 파일이 없습니다: {config_file}")
        logger.info("📝 config.txt 파일을 생성하고 다음 내용을 입력하세요:")
        logger.info("REST_API_KEY=your_rest_api_key_here")
        logger.info("REFRESH_TOKEN=your_refresh_token_here")
        return None, None
    try:
        # UTF-8 인코딩으로 파일 읽기
        with open(config_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        rest_api_key = None
        refresh_token = None
        for line in lines:
            if line.startswith('REST_API_KEY='):
                rest_api_key = line.split('=')[1].strip()
            elif line.startswith('REFRESH_TOKEN='):
                refresh_token = line.split('=')[1].strip()
        if not rest_api_key or not refresh_token:
            logger.error("❌ 설정 파일에 필수 정보가 없습니다")
            return None, None
        return rest_api_key, refresh_token
    except Exception as e:
        logger.error(f"❌ 설정 파일 로드 실패: {e}")
        return None, None

def main():
    """메인 실행 함수"""
    try:
        auto_sender = GriderAutoSender()
        auto_sender.send_report()
    except ValueError as e:
        logger.error(e)
    except Exception as e:
        logger.error(f"❌ 예상치 못한 오류 발생: {e}")

if __name__ == '__main__':
    main() 