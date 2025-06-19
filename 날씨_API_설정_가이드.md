# 날씨 API 설정 가이드

## 1. 기상청 API 설정 (우선 사용 - 무료)

### 1.1 공공데이터포털 회원가입
1. [공공데이터포털](https://www.data.go.kr/) 접속
2. 회원가입 및 로그인

### 1.2 기상청 단기예보 API 신청
1. 검색창에 "기상청_단기예보" 검색
2. "기상청_단기예보 ((구)_동네예보) 조회서비스" 선택
3. "활용신청" 클릭
4. 신청 완료 후 승인 대기 (보통 1-2시간)

### 1.3 API 키 확인
1. 마이페이지 > 개발계정 상세
2. 일반 인증키(Encoding) 복사

### 1.4 환경변수 설정
```bash
# .env 파일에 추가
KMA_API_KEY=your_kma_api_key_here
```

## 2. OpenWeatherMap API 설정 (백업용)

### 2.1 OpenWeatherMap 계정 생성
1. [OpenWeatherMap](https://openweathermap.org/api) 접속
2. "Sign Up" 클릭하여 무료 계정 생성
3. 이메일 인증 완료

### 2.2 API 키 발급
1. 로그인 후 "API keys" 탭 이동
2. 기본 API 키 확인 또는 새로 생성
3. API 키 복사 (활성화까지 최대 2시간 소요)

### 2.3 환경변수 설정
```bash
# .env 파일에 추가 (기상청 API와 함께)
KMA_API_KEY=your_kma_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
```

## 3. 사용법

### 3.1 기본 사용
```python
from weather_service import get_ansan_weather

# 자동으로 기상청 API 우선 사용, 실패시 OpenWeatherMap 사용
weather_info = get_ansan_weather()
print(weather_info)
```

### 3.2 개별 API 사용
```python
from weather_service import KMAWeatherService, WeatherService

# 기상청 API만 사용
kma_service = KMAWeatherService()
kma_weather = kma_service.get_weather_summary()

# OpenWeatherMap API만 사용
owm_service = WeatherService()
owm_weather = owm_service.get_weather_summary()
```

## 4. API 특징 비교

| 구분 | 기상청 API | OpenWeatherMap API |
|------|------------|-------------------|
| **비용** | 완전 무료 | 무료 (제한있음) |
| **정확도** | 한국 날씨에 최적화 | 글로벌 서비스 |
| **업데이트** | 3시간마다 | 실시간 |
| **데이터** | 한국 기상청 공식 | 글로벌 기상 데이터 |
| **언어** | 한국어 | 영어 |
| **제한** | 일 1,000회 | 일 1,000회 |

## 5. 문제 해결

### 5.1 기상청 API 오류
- **403 Forbidden**: API 키 확인, 승인 상태 확인
- **데이터 없음**: 좌표값 확인 (안산시: nx=58, ny=121)
- **시간 오류**: 발표시간 기준 확인 (02, 05, 08, 11, 14, 17, 20, 23시)

### 5.2 OpenWeatherMap API 오류
- **401 Unauthorized**: API 키 활성화 대기 (최대 2시간)
- **429 Too Many Requests**: 일일 요청 한도 초과

### 5.3 일반적인 문제
- **.env 파일 위치**: 프로젝트 루트 디렉토리에 위치
- **환경변수 로딩**: `python-dotenv` 패키지 설치 필요
- **네트워크 오류**: 인터넷 연결 상태 확인

## 6. 설치 필요 패키지

```bash
pip install requests python-dotenv
```

## 7. 테스트 방법

```bash
# 날씨 서비스 테스트
python weather_service.py

# 전체 시스템 테스트
python main_\(2\).py
```

이제 기상청 API가 우선적으로 사용되며, 실패할 경우 자동으로 OpenWeatherMap API로 전환됩니다. 