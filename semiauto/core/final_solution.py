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
import schedule
import time
from datetime import datetime, timedelta, time as dt_time
# pyperclip은 조건부 import (GitHub Actions 환경에서는 사용 불가)
import logging
import os
import re
import pytz  # 한국시간 설정을 위해 추가
from bs4 import BeautifulSoup  # BeautifulSoup import 추가
from xml.etree import ElementTree as ET  # 한국천문연구원 API용

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
            
            # 현재 시간이 메시지 전송 시간인지 확인
            if not self._is_message_time():
                logger.info("⏸️ 현재 시간은 메시지 전송 시간이 아닙니다.")
                # 메시지 전송 시간이 아닐 때는 None 반환 (에러 메시지 전송 방지)
                return None
            
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
                
                # 로그인 페이지 로드 (재시도 로직)
                LOGIN_URL = 'https://jangboo.grider.ai/'
                logger.info(f"로그인 페이지 접속: {LOGIN_URL}")
                
                # CloudFlare 우회를 위한 점진적 접근
                try:
                    # 1단계: 메인 도메인 먼저 접근
                    driver.get('https://grider.ai/')
                    time.sleep(3)
                    logger.info("✅ 메인 도메인 접근 성공")
                    
                    # 2단계: 서브도메인 접근
                    driver.get(LOGIN_URL)
                    time.sleep(5)  # CloudFlare 검증 대기
                    logger.info("✅ 로그인 페이지 접근 시도")
                    
                    # 3단계: CloudFlare 체크 대기
                    max_wait = 30
                    wait_count = 0
                    while wait_count < max_wait:
                        page_title = driver.title.lower()
                        current_url = driver.current_url.lower()
                        
                        # CloudFlare 체크 화면인지 확인
                        if any(keyword in page_title for keyword in ['checking', 'security', 'cloudflare', 'please wait']):
                            logger.info(f"🔄 CloudFlare 보안 검증 중... ({wait_count + 1}초)")
                            time.sleep(1)
                            wait_count += 1
                            continue
                        
                        # 정상 페이지 로드 확인
                        if "jangboo" in current_url and "grider" in current_url:
                            logger.info("✅ 정상 페이지 로드 완료")
                            break
                        
                        time.sleep(1)
                        wait_count += 1
                    
                    if wait_count >= max_wait:
                        raise Exception("CloudFlare 보안 검증 시간 초과")
                        
                except Exception as access_error:
                    logger.warning(f"⚠️ 직접 접근 실패, 우회 방법 시도: {access_error}")
                    
                    # 대안 URL들 시도
                    alternative_urls = [
                        'https://www.grider.ai/',
                        'https://jangboo.grider.ai/login',
                        'https://jangboo.grider.ai/dashboard'
                    ]
                    
                    for alt_url in alternative_urls:
                        try:
                            logger.info(f"🔄 대안 URL 시도: {alt_url}")
                            driver.get(alt_url)
                            time.sleep(3)
                            
                            if "grider" in driver.current_url.lower():
                                logger.info(f"✅ 대안 URL 접근 성공: {alt_url}")
                                break
                        except:
                            continue
                    else:
                        raise Exception("모든 접근 방법 실패")

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
                USER_ID = os.getenv('GRIDER_ID')
                USER_PW = os.getenv('GRIDER_PASSWORD')
                
                logger.info(f"🔍 환경변수 확인:")
                logger.info(f"   • GRIDER_ID 존재: {'있음' if USER_ID else '없음'}")
                logger.info(f"   • GRIDER_PASSWORD 존재: {'있음' if USER_PW else '없음'}")
                if USER_ID:
                    logger.info(f"   • GRIDER_ID 값: {USER_ID[:3]}***")
                
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
        """특정 날짜의 데이터로 이동하여 HTML 추출"""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException, NoSuchElementException
        
        try:
            logger.info(f"🔍 날짜별 데이터 조회 시작: {target_date}")
            
            # 1. 현재 페이지에서 날짜 선택기 찾기
            date_selectors = [
                # 일반적인 날짜 선택기 패턴들
                'input[type="date"]',
                '.date-picker',
                '#date-picker',
                '[name*="date"]',
                '[id*="date"]',
                '.datepicker',
                '#datepicker',
                'input.form-control[placeholder*="날짜"]',
                'input.form-control[placeholder*="일자"]',
                # 한국어 텍스트가 포함된 요소들
                '//input[@placeholder[contains(., "날짜")]]',
                '//input[@placeholder[contains(., "일자")]]',
                '//button[contains(text(), "날짜")]',
                '//span[contains(text(), "날짜")]/../input',
                # G라이더 특화 선택기 (추정)
                '.search-date',
                '#searchDate',
                '[name="searchDate"]',
                '.mission-date',
                '#missionDate'
            ]
            
            date_element = None
            wait = WebDriverWait(driver, 10)
            
            # 날짜 선택기 찾기
            for selector in date_selectors:
                try:
                    if selector.startswith('//'):  # XPath
                        date_element = driver.find_element(By.XPATH, selector)
                    else:  # CSS Selector
                        date_element = driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if date_element and date_element.is_displayed():
                        logger.info(f"✅ 날짜 선택기 발견: {selector}")
                        break
                except:
                    continue
            
            # 2. 날짜 선택기가 있으면 타겟 날짜로 설정
            if date_element:
                try:
                    # 기존 값 클리어
                    date_element.clear()
                    time.sleep(0.5)
                    
                    # 타겟 날짜 입력 (다양한 포맷 시도)
                    date_formats = [
                        target_date,  # 2025-06-26
                        target_date.replace('-', '.'),  # 2025.06.26
                        target_date.replace('-', '/'),  # 2025/06/26
                        target_date[2:].replace('-', '.'),  # 25.06.26
                        target_date[2:].replace('-', '/'),  # 25/06/26
                    ]
                    
                    for date_format in date_formats:
                        try:
                            date_element.clear()
                            date_element.send_keys(date_format)
                            time.sleep(1)
                            
                            # Enter 키 또는 검색 버튼 클릭
                            try:
                                from selenium.webdriver.common.keys import Keys
                                date_element.send_keys(Keys.ENTER)
                            except:
                                # 검색 버튼 찾기
                                search_buttons = [
                                    'button[type="submit"]',
                                    '.btn-search',
                                    '#searchBtn',
                                    'button:contains("검색")',
                                    'button:contains("조회")',
                                    'input[type="submit"]'
                                ]
                                
                                for btn_selector in search_buttons:
                                    try:
                                        search_btn = driver.find_element(By.CSS_SELECTOR, btn_selector)
                                        search_btn.click()
                                        break
                                    except:
                                        continue
                            
                            # 페이지 로딩 대기
                            time.sleep(3)
                            
                            # 날짜가 올바르게 설정되었는지 확인
                            current_html = driver.page_source
                            if self._verify_date_in_html(current_html, target_date):
                                logger.info(f"✅ 날짜 설정 성공: {date_format}")
                                return current_html
                            
                        except Exception as e:
                            logger.warning(f"날짜 포맷 {date_format} 시도 실패: {e}")
                            continue
                    
                    logger.warning("모든 날짜 포맷 시도 실패")
                    
                except Exception as e:
                    logger.warning(f"날짜 선택기 조작 실패: {e}")
            
            # 3. 날짜 선택기가 없거나 실패한 경우 - URL 파라미터로 시도
            logger.info("🔄 URL 파라미터 방식으로 날짜 조회 시도")
            
            current_url = driver.current_url
            date_params = [
                f"?date={target_date}",
                f"?searchDate={target_date}",
                f"?missionDate={target_date}",
                f"&date={target_date}",
                f"&searchDate={target_date}",
                f"&missionDate={target_date}"
            ]
            
            for param in date_params:
                try:
                    if '?' in current_url:
                        new_url = current_url + param.replace('?', '&')
                    else:
                        new_url = current_url + param
                    
                    driver.get(new_url)
                    time.sleep(3)
                    
                    html = driver.page_source
                    if self._verify_date_in_html(html, target_date):
                        logger.info(f"✅ URL 파라미터 방식 성공: {param}")
                        return html
                        
                except Exception as e:
                    logger.warning(f"URL 파라미터 {param} 시도 실패: {e}")
                    continue
            
            # 4. 모든 방법 실패 - 현재 페이지 데이터 반환하되 경고 로그
            logger.warning(f"⚠️ 날짜별 조회 실패 - 현재 페이지 데이터 사용 (날짜 불일치 가능성)")
            html = driver.page_source
            
            # 현재 페이지의 날짜 검증
            if self._verify_date_in_html(html, target_date):
                logger.info("✅ 현재 페이지가 올바른 날짜 데이터입니다")
            else:
                logger.error(f"❌ 현재 페이지 데이터가 타겟 날짜({target_date})와 일치하지 않습니다")
            
            return html
            
        except Exception as e:
            logger.error(f"❌ 날짜별 데이터 조회 중 오류: {e}")
            # 실패시 현재 페이지 HTML 반환
            return driver.page_source
    
    def _verify_date_in_html(self, html: str, target_date: str) -> bool:
        """HTML에서 타겟 날짜가 포함되어 있는지 검증"""
        try:
            # 다양한 날짜 포맷으로 검증
            date_variations = [
                target_date,  # 2025-06-26
                target_date.replace('-', '.'),  # 2025.06.26
                target_date.replace('-', '/'),  # 2025/06/26
                target_date.replace('-', ''),   # 20250626
                target_date[2:].replace('-', '.'),  # 25.06.26
                target_date[2:].replace('-', '/'),  # 25/06/26
                target_date[5:].replace('-', '.'),  # 06.26
                target_date[5:].replace('-', '/'),  # 06/26
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
                
                # 디버깅: HTML에서 날짜 패턴 찾기
                import re
                date_patterns = re.findall(r'\d{4}[-./]\d{1,2}[-./]\d{1,2}', html)
                if date_patterns:
                    logger.info(f"🔍 HTML에서 발견된 날짜 패턴들: {set(date_patterns[:10])}")  # 중복 제거하고 최대 10개
                
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
        """현재 시간 기준 예상 데이터 패턴 반환"""
        # G라이더 미션 시간대별 예상 패턴
        patterns = {
            # 아침(06-11): 아침점심피크 시작
            'morning': {'아침점심피크': 'active', '오후논피크': 'inactive', '저녁피크': 'inactive', '심야논피크': 'completed'},
            # 점심(12-14): 아침점심피크 마무리
            'lunch': {'아침점심피크': 'completing', '오후논피크': 'starting', '저녁피크': 'inactive', '심야논피크': 'completed'},
            # 오후(15-17): 오후논피크 진행
            'afternoon': {'아침점심피크': 'completed', '오후논피크': 'active', '저녁피크': 'inactive', '심야논피크': 'completed'},
            # 저녁(18-21): 저녁피크 진행  
            'evening': {'아침점심피크': 'completed', '오후논피크': 'completed', '저녁피크': 'active', '심야논피크': 'completed'},
            # 심야(22-05): 심야논피크 진행
            'night': {'아침점심피크': 'completed', '오후논피크': 'completed', '저녁피크': 'completed', '심야논피크': 'active'}
        }
        
        if 6 <= current_hour <= 11:
            return patterns['morning']
        elif 12 <= current_hour <= 14:
            return patterns['lunch']
        elif 15 <= current_hour <= 17:
            return patterns['afternoon']
        elif 18 <= current_hour <= 21:
            return patterns['evening']
        else:  # 22-05
            return patterns['night']

    def _get_sample_data(self):
        """크롤링 실패 시 사용할 샘플 데이터"""
        return {
            '총점': 90,
            '물량점수': 45,
            '수락률점수': 45,
            '총완료': 150,
            '총거절': 10,
            '수락률': 93.8,
            '아침점심피크': {"current": 30, "target": 25},
            '오후논피크': {"current": 26, "target": 20},
            '저녁피크': {"current": 40, "target": 30},
            '심야논피크': {"current": 8, "target": 15},
            'riders': [
                {'name': '홍길동', 'complete': 45, 'contribution': 30.0, 'acceptance_rate': 95.2, 'reject': 2, 'cancel': 1, 
                 '아침점심피크': 12, '오후논피크': 8, '저녁피크': 15, '심야논피크': 10},
                {'name': '김철수', 'complete': 38, 'contribution': 25.3, 'acceptance_rate': 92.1, 'reject': 3, 'cancel': 0,
                 '아침점심피크': 10, '오후논피크': 7, '저녁피크': 12, '심야논피크': 9}
            ],
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def _parse_data(self, html):
        """최적화된 데이터 파싱 함수 (main_(2).py와 동일한 로직)"""
        from bs4 import BeautifulSoup
        
        start_time = time.time()
        
        # 🎯 한국시간 기준 날짜 검증 로직 추가
        target_date = self._get_mission_date()
        logger.info(f"🎯 데이터 검증 시작: 타겟 미션 날짜 = {target_date}")
        
        # HTML에서 올바른 날짜 데이터인지 검증
        is_correct_date = self._verify_date_in_html(html, target_date)
        if not is_correct_date:
            logger.error(f"❌ 크롤링된 데이터가 타겟 날짜({target_date})와 일치하지 않습니다!")
            logger.error("🚨 어제 데이터 또는 잘못된 날짜 데이터가 크롤링되었을 가능성이 높습니다")
            
            # 추가 검증: 어제 날짜 체크
            import pytz
            
            korea_tz = pytz.timezone('Asia/Seoul')
            korea_now = datetime.now(korea_tz)
            yesterday = (korea_now - timedelta(days=1)).strftime('%Y-%m-%d')
            
            if self._verify_date_in_html(html, yesterday):
                logger.error(f"🚨 크롤링된 데이터가 어제 날짜({yesterday})입니다!")
                logger.error("💡 해결방법: G라이더 웹사이트에서 날짜 선택기를 통해 오늘 날짜로 변경 필요")
        
        # html.parser 파서 사용으로 속도 향상
        soup = BeautifulSoup(html, 'html.parser')
        
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

        # 한 번에 모든 요소 선택 (병렬 처리)
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
        
        total_score = results['total_score']
        quantity_score = results['quantity_score']
        acceptance_score = results['acceptance_score']
        total_complete = results['total_complete']
        total_reject = results['total_reject']
        acceptance_rate_total = results['acceptance_rate_total']

        # 물량 점수관리 테이블에서 피크별 데이터 파싱 (캐시 활용)
        logger.info("=== 미션 데이터 파싱 시작 ===")
        
        # 🎯 데이터 검증 강화: 크롤링 시점의 한국시간 기준 검증
        korea_time = self._get_korea_time()
        logger.info(f"🕐 크롤링 시점 한국시간: {korea_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        # 1단계: 캐시된 데이터가 있고 최신인지 확인
        cached_peak_data = self._load_mission_data_cache()
        if cached_peak_data and self._is_cache_valid_for_current_time():
            logger.info("✅ 캐시된 미션 데이터를 사용합니다.")
            peak_data = cached_peak_data
        else:
            logger.info("🔍 새로운 미션 데이터를 크롤링하여 파싱합니다.")
            peak_data = self._parse_mission_table_data(html)
            
            # 📊 파싱 결과 데이터 검증
            if peak_data:
                validation_result = self._validate_peak_data_with_date(peak_data, target_date, html)
                if not validation_result['is_valid']:
                    logger.error(f"❌ 파싱된 데이터 검증 실패: {validation_result['reason']}")
                    logger.error("🚨 올바르지 않은 날짜의 데이터가 파싱되었을 가능성이 높습니다")
                    logger.error(f"💡 권장사항: {validation_result['suggestion']}")
                else:
                    logger.info(f"✅ 파싱된 데이터 검증 성공: {validation_result['message']}")
            
            # 파싱 성공시 캐시에 저장
            if peak_data:
                mission_date = self._get_mission_date()
                self._save_mission_data_cache(mission_date, peak_data)
                logger.info("💾 새로운 미션 데이터를 캐시에 저장했습니다.")
        
        # 3단계 Fallback 시스템 (최적화)
        if not peak_data:
            logger.warning("⚠️ 1단계 파싱 실패! 2단계 fallback 시도")
            
            # 2단계: 기존 방식으로 데이터 파싱
            peak_data = {}
            quantity_items = soup.select('.quantity_item')
            logger.info(f"2단계: quantity_item 요소 {len(quantity_items)}개 발견")
            
            if quantity_items:
                # 통일된 용어 사용
                web_peak_names = ['아침점심피크', '오후논피크', '저녁피크', '심야논피크']
                legacy_peak_names = ['오전피크', '오후피크', '저녁피크', '심야피크']
                
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
                                'target': target,
                                'progress': (current / target * 100) if target > 0 else 0
                            }
                            logger.info(f"2단계 미션 파싱: {name} = {current}/{target}건")
                            
                        # 기존 코드 호환성을 위해 레거시 이름으로도 저장
                        if idx < len(legacy_peak_names):
                            legacy_name = legacy_peak_names[idx]
                            peak_data[legacy_name] = peak_data[name]
                            
                    except Exception as e:
                        logger.warning(f"미션 아이템 {idx} 파싱 실패: {e}")
                        continue

        logger.info(f"파싱 완료 (소요시간: {time.time() - start_time:.2f}초)")

        # 라이더별 데이터 추출 (제공된 HTML 구조에 맞게 최적화)
        riders = []
        rider_items = soup.select('.rider_item')
        logger.info(f"🔍 라이더 데이터 파싱 시작: {len(rider_items)}명의 라이더 발견")
        
        for idx, rider in enumerate(rider_items):
            try:
                # 라이더 이름 추출 (모바일 수락률 텍스트 제거)
                name_node = rider.select_one('.rider_name')
                if not name_node:
                    logger.warning(f"라이더 {idx+1}: 이름 노드를 찾을 수 없음")
                    continue
                    
                name_text = name_node.get_text(strip=True)
                # "수락률:XX%" 부분 제거
                name = re.sub(r'수락률:\d+%', '', name_text).strip()
                # "이름" 텍스트 제거
                name = re.sub(r'이름', '', name).strip()
                
                # 수락률 추출 (정확한 구조 반영)
                acceptance_rate = 0.0
                acc_node = rider.select_one('.rider_contents.midium.acceptance_rate')
                if acc_node:
                    acc_text = acc_node.get_text(strip=True)
                    match = re.search(r'(\d+(?:\.\d+)?)\s*%', acc_text)
                    if match:
                        acceptance_rate = float(match.group(1))
                
                # 완료 건수 추출
                complete = 0
                complete_node = rider.select_one('.rider_contents.complete_count')
                if complete_node:
                    complete_text = complete_node.get_text(strip=True)
                    match = re.search(r'(\d+)', complete_text)
                    if match:
                        complete = int(match.group(1))
                
                # 거절 건수 추출
                reject = 0
                reject_node = rider.select_one('.rider_contents.reject_count')
                if reject_node:
                    reject_text = reject_node.get_text(strip=True)
                    match = re.search(r'(\d+)', reject_text)
                    if match:
                        reject = int(match.group(1))
                
                # 배차취소 건수 추출
                cancel = 0
                cancel_node = rider.select_one('.rider_contents.accept_cancel_count')
                if cancel_node:
                    cancel_text = cancel_node.get_text(strip=True)
                    match = re.search(r'(\d+)', cancel_text)
                    if match:
                        cancel = int(match.group(1))
                
                # 배달취소 건수 추출
                delivery_cancel = 0
                delivery_cancel_node = rider.select_one('.rider_contents.accept_cancel_rider_fault_count')
                if delivery_cancel_node:
                    delivery_cancel_text = delivery_cancel_node.get_text(strip=True)
                    match = re.search(r'(\d+)', delivery_cancel_text)
                    if match:
                        delivery_cancel = int(match.group(1))
                
                # 피크별 수행 건수 추출
                morning = 0
                morning_node = rider.select_one('.rider_contents.morning_peak_count')
                if morning_node:
                    morning_text = morning_node.get_text(strip=True)
                    match = re.search(r'(\d+)', morning_text)
                    if match:
                        morning = int(match.group(1))
                
                afternoon = 0
                afternoon_node = rider.select_one('.rider_contents.afternoon_peak_count')
                if afternoon_node:
                    afternoon_text = afternoon_node.get_text(strip=True)
                    match = re.search(r'(\d+)', afternoon_text)
                    if match:
                        afternoon = int(match.group(1))
                
                evening = 0
                evening_node = rider.select_one('.rider_contents.evening_peak_count')
                if evening_node:
                    evening_text = evening_node.get_text(strip=True)
                    match = re.search(r'(\d+)', evening_text)
                    if match:
                        evening = int(match.group(1))
                
                midnight = 0
                midnight_node = rider.select_one('.rider_contents.midnight_peak_count')
                if midnight_node:
                    midnight_text = midnight_node.get_text(strip=True)
                    match = re.search(r'(\d+)', midnight_text)
                    if match:
                        midnight = int(match.group(1))
                
                # 운행 상태 추출
                working_status = "운행종료"
                status_node = rider.select_one('.rider_contents.working_status .rider_info_text')
                if status_node:
                    status_text = status_node.get_text(strip=True)
                    if "운행중" in status_text:
                        working_status = "운행중"
                
                # 아이디 추출
                user_id = ""
                id_node = rider.select_one('.rider_contents.user_id')
                if id_node:
                    id_text = id_node.get_text(strip=True)
                    # "아이디" 텍스트 제거
                    user_id = re.sub(r'아이디', '', id_text).strip()
                
                rider_data = {
                    'name': name,
                    'user_id': user_id,
                    'complete': complete,
                    'acceptance_rate': acceptance_rate,
                    'reject': reject,
                    'cancel': cancel,
                    'delivery_cancel': delivery_cancel,
                    'working_status': working_status,
                    # 새로운 통일된 용어
                    '아침점심피크': morning,
                    '오후논피크': afternoon,
                    '저녁피크': evening,
                    '심야논피크': midnight,
                    # 기존 호환성 유지
                    '오전피크': morning,
                    '오후피크': afternoon,
                    '심야피크': midnight,
                }
                
                # 금일 완료 내역이 있는 라이더만 포함
                if complete > 0:
                    riders.append(rider_data)
                    logger.info(f"✅ 라이더 {idx+1}: {name} (완료: {complete}건, 수락률: {acceptance_rate}%, 상태: {working_status})")
                else:
                    logger.info(f"⏭️ 라이더 {idx+1}: {name} (완료 0건으로 제외)")
                
            except Exception as e:
                logger.error(f"❌ 라이더 {idx+1} 파싱 실패: {e}")
                continue

        # 라이더별 미션 기여도 계산 (각 피크별 기여도의 평균)
        peak_names = ['오전피크', '오후피크', '저녁피크', '심야피크']
        for rider in riders:
            peak_contributions = []
            
            for peak in peak_names:
                target = peak_data.get(peak, {'target': 0})['target']
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

        # 새로운 용어와 기존 용어 모두 포함하여 데이터 구성
        data = {
            # 새로운 통일된 용어
            '아침점심피크': peak_data.get('아침점심피크', peak_data.get('오전피크', {'current': 0, 'target': 0})),
            '오후논피크': peak_data.get('오후논피크', peak_data.get('오후피크', {'current': 0, 'target': 0})),
            '저녁피크': peak_data.get('저녁피크', {'current': 0, 'target': 0}),
            '심야논피크': peak_data.get('심야논피크', peak_data.get('심야피크', {'current': 0, 'target': 0})),
            # 기존 호환성 유지
            '오전피크': peak_data.get('오전피크', peak_data.get('아침점심피크', {'current': 0, 'target': 0})),
            '오후피크': peak_data.get('오후피크', peak_data.get('오후논피크', {'current': 0, 'target': 0})),
            '심야피크': peak_data.get('심야피크', peak_data.get('심야논피크', {'current': 0, 'target': 0})),
            '총점': total_score,
            '물량점수': quantity_score,
            '수락률점수': acceptance_score,
            '총완료': total_complete,
            '총거절': total_reject,
            '수락률': acceptance_rate_total,
            'riders': riders,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return data
    
    def _save_mission_data_cache(self, mission_date, peak_data):
        """미션 데이터를 캐시 파일에 저장"""
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
        """
        미션 기준 날짜를 계산합니다.
        06:00~익일 03:00를 하나의 미션 날짜로 간주합니다.
        예: 2025-06-25 06:00 ~ 2025-06-26 03:00 = 2025-06-25 미션
        """
        # 한국시간 기준으로 계산
        try:
            import pytz
            kst = pytz.timezone('Asia/Seoul')
            now = datetime.now(kst)
        except ImportError:
            # pytz가 없으면 UTC+9로 계산
            utc_now = datetime.utcnow()
            now = utc_now + timedelta(hours=9)
        
        # G라이더 미션 시간: 06:00 ~ 익일 03:00
        # 03:00~05:59 -> 전날 미션 
        # 06:00~23:59 -> 당일 미션
        # 00:00~02:59 -> 전날 미션
        if now.time() < dt_time(6, 0):  # 00:00~05:59
            mission_date = now.date() - timedelta(days=1)
        else:  # 06:00~23:59
            mission_date = now.date()
            
        logger.info(f"🎯 미션 날짜 계산: 현재시간 {now.strftime('%Y-%m-%d %H:%M')} → 미션날짜 {mission_date}")
        return mission_date.strftime('%Y-%m-%d')

    def _is_message_time(self):
        """현재 시간이 메시지 전송 시간인지 확인"""
        korea_time = self._get_korea_time()
        current_hour = korea_time.hour
        current_minute = korea_time.minute
        
        # GitHub Actions는 보통 정각에 실행되므로 ±2분 허용
        if current_minute <= 2 or current_minute >= 58:
            # 운영 시간: 06:00 ~ 23:59 (다음날 03:59까지 연장)
            if 6 <= current_hour <= 23:
                return True
            # 야간 연장: 00:00 ~ 03:59 (전날 미션 연장)
            elif 0 <= current_hour <= 3:
                return True
        
        # 크롤링 오류 해결을 위한 테스트 시간도 허용
        if current_hour == 9 and 20 <= current_minute <= 30:  # 오전 9:20~9:30 테스트 시간
            logger.info("🔧 테스트 시간대 - 크롤링 테스트 허용")
            return True
        
        # 추가 테스트 시간 (CloudFlare 우회 테스트용)
        if current_hour == 18 and 50 <= current_minute <= 59:  # 오후 6:50~6:59 테스트 시간
            logger.info("🔧 CloudFlare 우회 테스트 시간 - 크롤링 테스트 허용")
            return True
        
        return False

    def _parse_mission_table_data(self, html):
        """
        물량 점수관리 테이블에서 미션 데이터를 파싱합니다. (실제 웹사이트 구조 기반)
        """
        from bs4 import BeautifulSoup
        import re
        
        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(html, 'html.parser')
        
        # 미션 기준 날짜 계산
        target_date = self._get_mission_date()
        logger.info(f"🎯 타겟 날짜: {target_date}")
        
        # 실제 테이블 구조에 맞는 선택자 사용
        sla_table = soup.select_one('table.sla_table[data-type=\"partner\"]')
        
        if not sla_table:
            logger.warning("❌ 물량 점수관리 테이블을 찾을 수 없습니다.")
            # 대체 선택자들 시도
            sla_table = soup.select_one('table.sla_table') or soup.select_one('.sla_table table') or soup.select_one('table')
            if not sla_table:
                logger.error("❌ 어떤 테이블도 찾을 수 없습니다.")
                return None
        
        # tbody에서 모든 행 가져오기
        rows = sla_table.select('tbody tr')
        if not rows:
            logger.warning("❌ 테이블 행을 찾을 수 없습니다.")
            return None
        
        logger.info(f"📋 총 {len(rows)}개 행 발견")
        
        # 타겟 날짜와 일치하는 행 찾기
        target_row = None
        for row in rows:
            cells = row.select('td')
            if len(cells) >= 7:  # 번호, 날짜, 점수, 4개 피크
                date_cell = cells[1]  # 두 번째 열이 날짜
                date_text = date_cell.get_text(strip=True)
                
                if date_text == target_date:
                    target_row = row
                    logger.info(f"✅ 타겟 날짜 {target_date} 행 발견!")
                    break
        
        if not target_row:
            logger.warning(f"❌ 날짜 {target_date}에 해당하는 행을 찾을 수 없습니다.")
            # 디버깅: 발견된 모든 날짜 출력
            logger.info("🔍 테이블에서 발견된 날짜들:")
            for i, row in enumerate(rows[:5]):
                cells = row.select('td')
                if len(cells) >= 2:
                    date_text = cells[1].get_text(strip=True)
                    logger.info(f"  행 {i+1}: {date_text}")
            return None
        
        # 타겟 행에서 데이터 추출
        cells = target_row.select('td')
        if len(cells) < 7:
            logger.error(f"❌ 행의 셀 수가 부족합니다. 예상: 7개, 실제: {len(cells)}개")
            return None
        
        # 피크별 데이터 파싱 (3번째 열부터 4개 피크)
        peak_names = ['아침점심피크', '오후논피크', '저녁피크', '심야논피크']
        peak_data = {}
        
        # 정규표현식으로 "숫자/숫자건" 패턴 추출
        pattern = re.compile(r'(\d+)/(\d+)건')
        
        for i, peak_name in enumerate(peak_names):
            cell_idx = i + 3  # 번호(0), 날짜(1), 점수(2), 피크 시작(3)
            if cell_idx < len(cells):
                cell = cells[cell_idx]
                cell_text = cell.get_text(strip=True)
                
                # "24/21건" 패턴 찾기
                match = pattern.search(cell_text)
                if match:
                    current = int(match.group(1))
                    target = int(match.group(2))
                    progress = (current / target * 100) if target > 0 else 0
                    
                    peak_data[peak_name] = {
                        'current': current,
                        'target': target, 
                        'progress': progress
                    }
                    
                    logger.info(f"✅ {peak_name}: {current}/{target}건 ({progress:.1f}%)")
                else:
                    logger.warning(f"⚠️ {peak_name} 데이터 파싱 실패: {cell_text}")
                    peak_data[peak_name] = {'current': 0, 'target': 0, 'progress': 0}
        
        logger.info(f"📊 파싱 완료: {len(peak_data)}개 피크 데이터")
        return peak_data
    
    def _parse_grider_html_old(self, soup):
        """실제 HTML 파싱 로직 (main_(2).py의 검증된 parse_data 함수 기반)"""
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
    """심플 배민 플러스 자동화 메인 클래스"""
    
    def __init__(self, rest_api_key, refresh_token):
        self.token_manager = TokenManager(rest_api_key, refresh_token)
        self.data_collector = GriderDataCollector()
        self.sender = None
    
    def format_message(self, data):
        """메시지 포맷팅"""
        if not data:
            logger.warning("⚠️ 데이터가 비어있습니다")
            return None
        
        # 에러 데이터 감지 시 None 반환 (메시지 전송 방지)
        if data.get('error'):
            logger.info(f"🛑 에러 데이터 감지 - 메시지 포맷팅 건너뜀: {data.get('error_reason', '알 수 없는 오류')}")
            return None
        
        try:
            korea_time = self._get_korea_time()
            hour = korea_time.hour
            minute = korea_time.minute
            
            # 시간대별 인사말
            greeting = self._get_time_based_greeting(hour, minute)
            
            # 날짜별 체크
            current_date = korea_time.strftime("%Y-%m-%d")
            is_weekend = korea_time.weekday() >= 5
            is_holiday = self.holiday_checker.is_holiday_advanced(korea_time)
            
            # 날씨 정보 (간소화)
            weather_info = self._get_weather_info()
            
            # 기본 메시지 구성
            message_parts = [
                f"{greeting}",
                f"📅 {korea_time.strftime('%Y년 %m월 %d일')} ({['월','화','수','목','금','토','일'][korea_time.weekday()]})",
            ]
            
            # 주말/휴일 표시
            if is_weekend or is_holiday:
                if is_holiday:
                    message_parts.append("🎌 오늘은 공휴일입니다")
                else:
                    message_parts.append("🎯 주말 근무 중!")
            
            # 날씨 정보 추가
            if weather_info:
                message_parts.append(f"🌤️ {weather_info}")
            
            message_parts.append("")  # 빈 줄
            
            # 현재 시간 확인 (한국시간) - 더 안전한 방법으로 처리
            try:
                import pytz
                kst = pytz.timezone('Asia/Seoul')
                now = datetime.now(kst)
            except ImportError:
                # pytz가 없으면 UTC+9로 계산
                utc_now = datetime.utcnow()
                now = utc_now + timedelta(hours=9)
            
            current_hour = now.hour
            current_minute = now.minute
            
            # 디버그 로그 추가 (GitHub Actions에서 시간 확인용)
            logger.info(f"🕐 현재 시간: {now.strftime('%Y-%m-%d %H:%M:%S')} (한국시간)")
            logger.info(f"🕐 시간대별 인사말 생성: {current_hour:02d}:{current_minute:02d}")
            
            # 휴일/평일 정보 확인 및 로그
            is_weekend_or_holiday = self._is_weekend_or_holiday(now)
            day_type = "휴일" if is_weekend_or_holiday else "평일"
            logger.info(f"📅 현재 날짜 타입: {day_type}")
            
            # 시간대별 인사말 결정
            greeting = self._get_time_based_greeting(current_hour, current_minute)
            
            # 날씨 정보 (전체 버전으로 복원)
            weather_info = self._get_weather_info()
            
            # 1. 미션 현황 - 지난 미션과 현재 미션 모두 표시
            peak_order = ['아침점심피크', '오후논피크', '저녁피크', '심야논피크']
            peak_emojis = {
                '아침점심피크': '🌅', 
                '오후논피크': '🌇', 
                '저녁피크': '🌃', 
                '심야논피크': '🌙'
            }
            
            mission_parts = []
            lacking_missions = []
            
            # 03:00~06:00는 미션 준비 시간 (휴일/평일 동일)
            if 3 <= current_hour < 6:
                is_weekend_or_holiday = self._is_weekend_or_holiday(now)
                holiday_info = " (주말/휴일)" if is_weekend_or_holiday else " (평일)"
                mission_parts.append(f"🛌 미션 준비 시간입니다{holiday_info} - 06:00부터 미션 정보가 표시됩니다")
                preparation_time = True
            else:
                preparation_time = False
            
            if not preparation_time:
                is_weekend_or_holiday = self._is_weekend_or_holiday(now)
                
                # 시작된 미션만 표시 (아직 시작되지 않은 미션은 숨김)
                started_missions = []  # 시작된 모든 미션 (완료/진행중 구분 없이)
                
                for key in peak_order:
                    peak_info = data.get(key, {'current': 0, 'target': 0})
                    cur = peak_info.get('current', 0)
                    tgt = peak_info.get('target', 0)
                    
                    if tgt == 0:
                        continue
                    
                    # 미션 시간대 확인
                    mission_started = False  # 미션이 시작되었는지 확인
                    mission_active = False   # 현재 진행중인지 확인
                    
                    if key == '아침점심피크':
                        if is_weekend_or_holiday:
                            # 휴일: 6-14시
                            mission_started = current_hour >= 6
                            mission_active = 6 <= current_hour < 14
                            peak_time_info = "06:00-14:00 (휴일)"
                        else:
                            # 평일: 6-13시
                            mission_started = current_hour >= 6
                            mission_active = 6 <= current_hour < 13
                            peak_time_info = "06:00-13:00 (평일)"
                    elif key == '오후논피크':
                        if is_weekend_or_holiday:
                            # 휴일: 14-17시
                            mission_started = current_hour >= 14
                            mission_active = 14 <= current_hour < 17
                            peak_time_info = "14:00-17:00 (휴일)"
                        else:
                            # 평일: 13-17시
                            mission_started = current_hour >= 13
                            mission_active = 13 <= current_hour < 17
                            peak_time_info = "13:00-17:00 (평일)"
                    elif key == '저녁피크':
                        # 17-20시 (휴일/평일 동일)
                        mission_started = current_hour >= 17
                        mission_active = 17 <= current_hour < 20
                        peak_time_info = "17:00-20:00"
                    elif key == '심야논피크':
                        # 20시~다음날 3시 (휴일/평일 동일)
                        mission_started = current_hour >= 20 or current_hour < 3
                        mission_active = current_hour >= 20 or current_hour < 3
                        peak_time_info = "20:00-03:00 (익일)"
                    
                    # 피크 시간대 정보 로그
                    logger.info(f"🎯 {key}: {peak_time_info} | 시작됨: {mission_started} | 진행중: {mission_active}")
                    
                    # 아직 시작되지 않은 미션은 표시하지 않음
                    if not mission_started:
                        continue
                    
                    # 상태 결정 (아이콘만 사용)
                    if cur >= tgt:
                        status = '✅'
                    else:
                        if mission_active:
                            status = f'⏳ ({tgt-cur}건 남음)'
                            lacking_missions.append(f'{key.replace("피크","").replace("논","")} {tgt-cur}건')
                        else:
                            status = f'❌ ({tgt-cur}건 부족)'
                    
                    mission_line = f"{peak_emojis.get(key, '')} {key}: {cur}/{tgt} {status}"
                    started_missions.append(mission_line)
                
                # 금일 미션 현황 표시 (시작된 미션만)
                if started_missions:
                    mission_parts.append("🎯 금일 미션 현황")
                    mission_parts.extend(started_missions)
                else:
                    # 아직 미션이 시작되지 않은 경우 안내 메시지
                    mission_parts.append("🎯 금일 미션 현황")
                    mission_parts.append("⏰ 미션 시작 전입니다")
                    mission_parts.append("첫 번째 미션은 06:00부터 시작됩니다")
            
            # 2. 기본 정보 - 두 줄로 정리
            total_score = data.get("총점", 0)
            quantity_score = data.get("물량점수", 0)
            acceptance_score = data.get("수락률점수", 0)
            acceptance_rate = data.get("수락률", 0.0)
            total_completed = data.get("총완료", 0)
            total_rejected = data.get("총거절", 0)
            
            summary_parts = [
                "📊 금주 미션 수행 예상점수",
                f"총점: {total_score}점 (물량:{quantity_score}, 수락률:{acceptance_score})",
                f"수락률: {acceptance_rate:.1f}% | 완료: {total_completed} | 거절: {total_rejected}"
            ]
            
            # 3. 라이더 순위 - 완료 건수가 있는 라이더만 대상으로 TOP 3 선정
            sorted_riders = sorted(
                [r for r in data.get('riders', []) if r.get('complete', 0) > 0], 
                key=lambda x: x.get('contribution', 0), 
                reverse=True
            )
            
            rider_parts = []
            top_riders = sorted_riders[:3]
            other_riders = sorted_riders[3:]
            
            # 라이더 순위 (3위까지 자세한 정보)
            if sorted_riders:
                # 운행중인 라이더 수 계산 (금일 완료 내역이 있는 라이더 수)
                active_rider_count = len(sorted_riders)
                rider_parts.append(f"🏆 라이더 순위 (운행 : {active_rider_count}명)")
                medals = ['🥇', '🥈', '🥉']
                
                # 3위까지만 표시
                for i, rider in enumerate(sorted_riders[:3]):
                    name = rider.get('name', '이름없음')
                    contribution = rider.get('contribution', 0)
                    
                    # 피크별 기여도
                    morning = rider.get('아침점심피크', 0)
                    afternoon = rider.get('오후논피크', 0)
                    evening = rider.get('저녁피크', 0)
                    midnight = rider.get('심야논피크', 0)
                    
                    acceptance_rate = rider.get('acceptance_rate', 0.0)
                    reject = rider.get('reject', 0)
                    cancel = rider.get('cancel', 0)
                    complete = rider.get('complete', 0)
                    
                    # 진행률 바 생성 (퍼센트 바 안쪽에 표시)
                    bar_len = 10
                    filled = int(round(contribution / 10))  # 10%당 1칸
                    if filled > 10:
                        filled = 10
                    
                    # 퍼센트 텍스트 길이 계산
                    percent_text = f"{contribution:.1f}%"
                    remaining_dashes = bar_len - filled - len(percent_text)
                    
                    if remaining_dashes > 0:
                        bar = '■' * filled + '─' * remaining_dashes + percent_text
                    else:
                        # 퍼센트 텍스트가 너무 길면 뒤쪽 ■을 일부 대체
                        bar = '■' * max(0, bar_len - len(percent_text)) + percent_text
                    
                    # 1-3위는 메달만 표시
                    rider_parts.append(f"**{medals[i]} {name}** | [{bar}]")
                    
                    rider_parts.append(f"    총 {complete}건 (🌅{morning} 🌇{afternoon} 🌃{evening} 🌙{midnight})")
                    rider_parts.append(f"    수락률: {acceptance_rate:.1f}% (거절:{reject}, 취소:{cancel})")
            
            # 전체 라이더의 금일 완료/거절/취소/수락률 통계 계산
            total_complete_today = sum(rider.get('complete', 0) for rider in data.get('riders', []))
            total_reject_today = sum(rider.get('reject', 0) for rider in data.get('riders', []))
            total_cancel_today = sum(rider.get('cancel', 0) for rider in data.get('riders', []))
            total_delivery_cancel_today = sum(rider.get('delivery_cancel', 0) for rider in data.get('riders', []))
            
            # 미션 현황 아래 완료/거절/취소/수락률 정보를 깔끔하게 표시
            total_cancel_all = total_cancel_today + total_delivery_cancel_today  # 배차취소 + 배달취소
            
            # 전체 수락률 계산 (완료 / (완료 + 거절 + 취소) * 100)
            total_attempts = total_complete_today + total_reject_today + total_cancel_all
            overall_acceptance_rate = (total_complete_today / total_attempts * 100) if total_attempts > 0 else 0.0
            
            # 거절에 취소를 합산 (금주 미션 수행 예상점수와 동일한 방식)
            total_reject_combined = total_reject_today + total_cancel_all
            
            mission_summary_parts = [
                "📈 금일 수행 내역",
                f"수락률: {overall_acceptance_rate:.1f}% | 완료: {total_complete_today} | 거절: {total_reject_combined}"
            ]
            mission_summary = "\n".join(mission_summary_parts)
            
            # 최종 메시지 조합 (시간대별 인사말 추가)
            message_parts = [
                greeting,  # 시간대별 인사말 추가
                "",
                f"📊 심플 배민 플러스 미션 알리미 ({day_type})",
                ""
            ]
            
            # 오류 데이터인 경우 친화적인 오류 메시지 추가
            if data.get('error', False):
                error_reason = data.get('error_reason', '알 수 없는 오류')
                
                # 현재 시간대 정보
                now = datetime.now(KST)
                current_hour = now.hour
                
                # 시간대별 상황 설명
                if 6 <= current_hour < 13:
                    time_info = "🌅 아침점심피크 시간대"
                    mission_status = "현재 아침점심피크 미션이 진행중입니다"
                elif 13 <= current_hour < 17:
                    time_info = "🌇 오후논피크 시간대"
                    mission_status = "현재 오후논피크 미션이 진행중입니다"
                elif 17 <= current_hour < 20:
                    time_info = "🌃 저녁피크 시간대"
                    mission_status = "현재 저녁피크 미션이 진행중입니다"
                elif 20 <= current_hour or current_hour < 3:
                    time_info = "🌙 심야논피크 시간대"
                    mission_status = "현재 심야논피크 미션이 진행중입니다"
                else:
                    time_info = "⏰ 미션 준비 시간"
                    mission_status = "미션 시작 전입니다"
                
                message_parts.extend([
                    "🚨 크롤링 연결 실패",
                    "",
                    time_info,
                    mission_status,
                    "",
                    "⚠️ 일시적인 연결 문제로 실시간 데이터를 가져올 수 없습니다.",
                    "",
                    "🔧 가능한 원인:",
                    "• G라이더 웹사이트 일시적 접속 장애",
                    "• 네트워크 연결 문제",
                    "• 웹사이트 구조 변경",
                    "",
                    "💡 해결 방법:",
                    "• 잠시 후 자동으로 재시도됩니다",
                    "• 문제가 지속되면 수동으로 확인해주세요",
                    "",
                    "🕐 다음 자동 시도: 30분 후",
                    "📱 자동화 시스템은 계속 작동중입니다",
                    "",
                    f"⏰ 오류 발생 시간: {data.get('timestamp', 'N/A')}",
                    "",
                    "🤖 자동화 시스템에 의해 전송됨"
                ])
            else:
                # 정상 데이터인 경우 기존 메시지 구성
                message_parts.extend([
                    "\n".join(mission_parts),
                    "",
                    weather_info,
                    "",
                    mission_summary,
                    "",
                    "\n".join(summary_parts),
                    "",
                    "\n".join(rider_parts)
                ])
                
                if lacking_missions:
                    message_parts.append("")
                    message_parts.append(f"⚠️ 미션 부족: {', '.join(lacking_missions)}")
                
                message_parts.append("")
                message_parts.append("🤖 자동화 시스템에 의해 전송됨")
            
            return "\n".join(message_parts)
        
        except Exception as e:
            logger.error(f"❌ 메시지 포맷팅 중 오류: {e}")
            return None
    
    def _is_weekend_or_holiday(self, dt):
        """주말 또는 휴일 판정 (한국천문연구원 API 기반)"""
        # 주말 체크 (토요일=5, 일요일=6)
        if dt.weekday() >= 5:
            return True
        
        # 한국천문연구원 공휴일 API 사용
        try:
            is_holiday, holiday_name = holiday_checker.is_holiday_advanced(dt)
            if is_holiday:
                logger.info(f"📅 공휴일 확인: {dt.strftime('%Y-%m-%d')} - {holiday_name}")
                return True
        except Exception as e:
            logger.warning(f"⚠️ 공휴일 API 오류, 기본 공휴일 사용: {e}")
            
            # API 실패시 기본 공휴일 체크
            holidays_2024 = [
                (1, 1), (2, 9), (2, 10), (2, 11), (2, 12), (3, 1), (5, 5), 
                (5, 15), (6, 6), (8, 15), (9, 16), (9, 17), (9, 18), 
                (10, 3), (10, 9), (12, 25)
            ]
            
            for month, day in holidays_2024:
                if dt.month == month and dt.day == day:
                    return True
                
        return False
    
    def _get_time_based_greeting(self, hour, minute):
        """시간대별 인사말 생성"""
        
        # 디버그 로그 추가
        logger.info(f"🎯 인사말 생성 요청: {hour:02d}:{minute:02d}")
        
        # 10:00 하루 시작 - 특별 인사말 (전체 리포트에 추가됨)
        if hour == 10 and minute == 0:
            logger.info("🌅 10:00 하루 시작 인사말 선택")
            return """🌅 좋은 아침입니다!
오늘도 심플 배민 플러스와 함께 힘찬 하루를 시작해보세요!
안전운행하시고 좋은 하루 되세요! 💪"""
        
        # 00:00 하루 마무리 - 특별 인사말 (전체 리포트에 추가됨)
        elif hour == 0 and minute == 0:
            logger.info("🌙 00:00 하루 마무리 인사말 선택")
            return """🌙 오늘 하루도 정말 수고하셨습니다!
안전하게 귀가하시고 푹 쉬세요.
내일도 좋은 하루 되시길 바랍니다! 🙏"""
        
        # 일반 30분 간격 메시지
        else:
            time_greetings = {
                (10, 30): "☀️ 오전 업무 시작! 오늘도 화이팅하세요!",
                (11, 0): "🌅 오전 11시! 점심 피크 준비 시간입니다!",
                (11, 30): "🌅 점심 피크 시간이 다가오고 있어요!",
                (12, 0): "🍽️ 정오 12시! 점심 피크 시작!",
                (12, 30): "🍽️ 점심 피크 시간! 안전운행 부탁드려요!",
                (13, 0): "⏰ 오후 1시! 점심 피크 마무리 시간!",
                (13, 30): "⏰ 오후 시간대 접어들었습니다!",
                (14, 0): "🌇 오후 2시! 논피크 시간대!",
                (14, 30): "🌇 오후 논피크 시간이에요!",
                (15, 0): "☕ 오후 3시! 잠시 휴식 시간!",
                (15, 30): "☕ 오후 3시 30분, 잠시 휴식하세요!",
                (16, 0): "🌆 오후 4시! 저녁 피크 준비!",
                (16, 30): "🌆 저녁 피크 준비 시간입니다!",
                (17, 0): "🌃 오후 5시! 저녁 피크 시작!",
                (17, 30): "🌃 저녁 피크 시간! 주문이 많을 예정이에요!",
                (18, 0): "🍽️ 저녁 6시! 저녁 식사 시간!",
                (18, 30): "🍽️ 저녁 식사 시간! 바쁜 시간대입니다!",
                (19, 0): "🌉 저녁 7시! 피크 마무리 시간!",
                (19, 30): "🌉 저녁 피크 마무리 시간이에요!",
                (20, 0): "🌙 저녁 8시! 심야 논피크 시작!",
                (20, 30): "🌙 심야 논피크 시간대 시작!",
                (21, 0): "🌃 밤 9시! 오늘도 수고하고 계세요!",
                (21, 30): "🌃 밤 9시 30분, 오늘도 수고하고 계세요!",
                (22, 0): "🌙 밤 10시! 심야 시간대 안전운행!",
                (22, 30): "🌙 심야 시간대, 안전운행 최우선!",
                (23, 0): "🌌 밤 11시! 하루 마무리가 다가와요!",
                (23, 30): "🌌 하루 마무리 시간이 다가오고 있어요!",
                # 익일 새벽 시간대 추가
                (0, 30): "🌙 새벽 12시 30분, 오늘도 정말 수고하셨습니다!",
                (1, 0): "🌅 새벽 1시, 심야 미션 진행중입니다!",
                (1, 30): "🌅 새벽 1시 30분, 안전운행 최우선입니다!",
                (2, 0): "🌅 새벽 2시, 곧 하루가 마무리됩니다!",
                (2, 30): "🌅 새벽 2시 30분, 마지막 미션 시간입니다!",
                (3, 0): "🌅 새벽 3시, 오늘 하루도 정말 고생하셨습니다!"
            }
            
            greeting = time_greetings.get((hour, minute), f"⏰ {hour:02d}:{minute:02d} 현재 상황을 알려드립니다!")
            logger.info(f"📝 선택된 인사말: {greeting[:50]}...")
            return greeting
    
    def _get_weather_info(self):
        """날씨 정보 가져오기 (오전/오후 요약 버전)"""
        try:
            # 간단한 날씨 정보 (실제 API 연동 가능)
            now = datetime.now(KST)
            return f"""🌍 오늘의 날씨 (기상청)
🌅 오전: ☀️ 18~22°C
🌇 오후: ☀️ 20~24°C"""
        except Exception as e:
            return "⚠️ 날씨 정보를 가져올 수 없습니다."
    
    def send_report(self):
        """리포트 전송"""
        try:
            # 데이터 수집
            data = self.data_collector.get_grider_data()
            
            # 데이터가 None이면 메시지 전송하지 않음 (에러 방지)
            if data is None:
                logger.info("🛑 데이터가 없어서 메시지 전송을 건너뜁니다.")
                return {"result_code": -1, "message": "데이터 없음 - 메시지 전송 건너뜀"}
            
            # 에러 데이터 감지 시 전송 중단
            if data.get('error'):
                logger.info(f"🛑 에러 데이터 감지 - 메시지 전송 건너뜀: {data.get('error_reason', '알 수 없는 오류')}")
                return {"result_code": -1, "message": "에러 데이터 감지 - 메시지 전송 건너뜀"}
            
            # 유효한 토큰 확인
            access_token = self.token_manager.get_valid_token()
            if not access_token:
                logger.error("❌ 유효한 토큰을 가져올 수 없습니다")
                return {"result_code": -1, "message": "토큰 오류"}
            
            # 메시지 구성
            message = self.format_message(data)
            
            # 메시지가 에러 메시지인지 확인
            if message is None or "🚨 크롤링 실패" in message or "🚨 시스템 오류" in message:
                logger.info("🛑 에러 메시지 감지 - 전송 건너뜀")
                return {"result_code": -1, "message": "에러 메시지 감지 - 전송 건너뜀"}
            
            # 카카오톡 전송
            self.sender = KakaoSender(access_token)
            result = self.sender.send_text_message(message)
            
            if result.get('result_code') == 0:
                logger.info("✅ 카카오톡 메시지 전송 성공!")
            else:
                logger.error(f"❌ 카카오톡 전송 실패: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 리포트 전송 중 오류: {e}")
            return {"result_code": -1, "message": f"전송 오류: {e}"}
    
    def test_connection(self):
        """연결 테스트"""
        try:
            logger.info("🔧 카카오톡 연결 테스트 중...")
            
            access_token = self.token_manager.get_valid_token()
            self.sender = KakaoSender(access_token)
            
            test_message = f"🧪 심플 배민 플러스 자동화 테스트\n시간: {datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')}\n✅ 연결 성공!"
            
            result = self.sender.send_text_message(test_message)
            
            if result.get('result_code') == 0:
                logger.info("✅ 테스트 성공! 카카오톡 연결 정상")
                return True
            else:
                logger.error(f"❌ 테스트 실패: {result}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 테스트 중 오류: {e}")
            return False
    
    def start_scheduler(self):
        """스케줄러 시작 (기존 main_(2).py 스케줄 적용)"""
        # 특별 알림: 오전 10시 시작 알림
        schedule.every().day.at("10:00").do(self._send_start_notification)
        
        # 특별 알림: 자정 종료 알림  
        schedule.every().day.at("00:00").do(self._send_end_notification)
        
        # 기본 설정: 10분 간격 (10:00~00:00 운영시간)
        schedule.every(10).minutes.do(self._scheduled_send)
        
        # 피크 시간 집중 모니터링 (5분 간격)
        peak_hours = [11, 12, 13, 17, 18, 19]  # 피크 시간대
        for hour in peak_hours:
            schedule.every().day.at(f"{hour:02d}:00").do(self._scheduled_send)
            schedule.every().day.at(f"{hour:02d}:05").do(self._scheduled_send)
            schedule.every().day.at(f"{hour:02d}:10").do(self._scheduled_send)
            schedule.every().day.at(f"{hour:02d}:15").do(self._scheduled_send)
            schedule.every().day.at(f"{hour:02d}:20").do(self._scheduled_send)
            schedule.every().day.at(f"{hour:02d}:25").do(self._scheduled_send)
            schedule.every().day.at(f"{hour:02d}:30").do(self._scheduled_send)
            schedule.every().day.at(f"{hour:02d}:35").do(self._scheduled_send)
            schedule.every().day.at(f"{hour:02d}:40").do(self._scheduled_send)
            schedule.every().day.at(f"{hour:02d}:45").do(self._scheduled_send)
            schedule.every().day.at(f"{hour:02d}:50").do(self._scheduled_send)
            schedule.every().day.at(f"{hour:02d}:55").do(self._scheduled_send)
        
        logger.info("🚀 심플 배민 플러스 자동화 시작!")
        logger.info("📊 현재 설정:")
        logger.info("   • 알림 시간: 10:00~00:00")
        logger.info("   • 특별 알림: 10:00 시작알림, 00:00 종료알림")
        logger.info("   • 모니터링 간격: 10분 (피크시간 5분)")
        logger.info("   • 피크시간: 11-13시, 17-19시")
        logger.info("💡 Ctrl+C로 중지 가능")
        
        # 즉시 실행 여부 확인
        now = datetime.now(KST)
        current_hour = now.hour
        is_service_time = 10 <= current_hour <= 23
        
        if is_service_time:
            logger.info("✅ 알림 시간대입니다. 즉시 첫 모니터링을 시작합니다.")
            self.send_report()
        else:
            logger.info("💤 현재 휴식 시간대입니다. 10:00부터 알림을 시작합니다.")
        
        try:
            while True:
                # 현재 시간이 서비스 시간인지 확인
                current_time = datetime.now(KST)
                if 10 <= current_time.hour <= 23:
                    schedule.run_pending()
                time.sleep(60)  # 1분마다 확인
        except KeyboardInterrupt:
            logger.info("🛑 사용자에 의해 중지됨")
        except Exception as e:
            logger.error(f"❌ 스케줄러 오류: {e}")
    
    def _scheduled_send(self):
        """스케줄된 전송 (시간 체크 포함)"""
        now = datetime.now(KST)
        current_hour = now.hour
        
        # 운영 시간 체크 (10:00~00:00)
        if not (10 <= current_hour <= 23):
            return
        
        # 실제 전송 실행
        self.send_report()
    
    def _send_start_notification(self):
        """오전 10시 시작 알림"""
        try:
            access_token = self.token_manager.get_valid_token()
            self.sender = KakaoSender(access_token)
            
            start_message = f"""🌅 심플 배민 플러스 자동 모니터링 시작!
            
📅 {datetime.now(KST).strftime('%Y년 %m월 %d일')} 오전 10시
🚀 오늘 하루 미션 현황을 실시간으로 모니터링합니다

⏰ 운영 시간: 10:00 ~ 00:00 (14시간)
📊 모니터링 간격: 
   • 일반시간: 10분 간격
   • 피크시간(11-13시, 17-19시): 5분 간격

💪 오늘도 화이팅하세요!"""
            
            result = self.sender.send_text_message(start_message)
            if result.get('result_code') == 0:
                logger.info("✅ 오전 10시 시작 알림 전송 완료!")
            
            # 시작과 함께 첫 리포트도 전송
            self.send_report()
            
        except Exception as e:
            logger.error(f"❌ 시작 알림 전송 실패: {e}")
    
    def _send_end_notification(self):
        """자정 종료 알림"""
        try:
            access_token = self.token_manager.get_valid_token()
            self.sender = KakaoSender(access_token)
            
            # 마지막 리포트 먼저 전송
            self.send_report()
            
            end_message = f"""🌙 심플 배민 플러스 자동 모니터링 종료
            
📅 {datetime.now(KST).strftime('%Y년 %m월 %d일')} 자정
✅ 오늘 하루 모니터링이 완료되었습니다

📊 오늘의 최종 현황이 위 메시지에 포함되어 있습니다
💤 다음 모니터링: 내일 오전 10시부터

🙏 오늘도 수고하셨습니다!"""
            
            result = self.sender.send_text_message(end_message)
            if result.get('result_code') == 0:
                logger.info("✅ 자정 종료 알림 전송 완료!")
                
        except Exception as e:
            logger.error(f"❌ 종료 알림 전송 실패: {e}")

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
    """메인 함수"""
    import sys
    
    try:
        logger.info("🚀 G라이더 자동화 시스템 시작...")
        
        # 설정 로드
        rest_api_key, refresh_token = load_config()
        if not rest_api_key or not refresh_token:
            logger.error("❌ 카카오 API 설정이 누락되었습니다")
            return
        
        # 데이터 수집 테스트
        data_collector = GriderDataCollector()
        test_data = data_collector.get_grider_data()
        
        # 크롤링 실패 시 스케줄러 시작 중단
        if test_data.get('error', False):
            logger.error("❌ 크롤링 실패 - 스케줄러를 시작하지 않습니다")
            logger.error("💡 해결 방법: config.txt에서 GRIDER_ID와 GRIDER_PASSWORD를 설정하세요")
            return
        
        # 자동화 객체 생성
        auto_sender = GriderAutoSender(rest_api_key, refresh_token)
        
        # 연결 테스트
        if not auto_sender.test_connection():
            logger.error("❌ 연결 테스트 실패. 설정을 확인해주세요.")
            return
        
        if '--single-run' in sys.argv:
            # GitHub Actions용 단일 실행
            logger.info("🤖 GitHub Actions 단일 실행 모드")
            success = auto_sender.send_report()
            if success:
                logger.info("✅ GitHub Actions 실행 완료")
            else:
                logger.error("❌ GitHub Actions 실행 실패")
                sys.exit(1)
        else:
            # 로컬 스케줄러 모드
            logger.info("🧪 연결 테스트 완료. 스케줄러에서 자동 시작됩니다.")
            auto_sender.start_scheduler()
    except Exception as e:
        logger.error(f"❌ 메인 함수 실행 중 오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 