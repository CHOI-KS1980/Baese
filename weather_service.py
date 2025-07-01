import requests
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import urllib.parse
import pytz

load_dotenv()

# 한국시간 설정
KST = pytz.timezone('Asia/Seoul')

def get_korea_time():
    """한국시간 기준 현재 시간 반환"""
    return datetime.now(KST)

class WeatherService:
    def __init__(self):
        # OpenWeatherMap API 키 (무료)
        self.api_key = os.getenv('OPENWEATHER_API_KEY', 'YOUR_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
        # 안산시 좌표 (위도, 경도)
        self.ansan_lat = 37.3236
        self.ansan_lon = 126.8219
    
    def get_current_weather(self):
        """현재 날씨 정보 가져오기"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                'lat': self.ansan_lat,
                'lon': self.ansan_lon,
                'appid': self.api_key,
                'units': 'metric',  # 섭씨 온도
                'lang': 'kr'  # 한국어
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return self._format_current_weather(data)
            else:
                return None
                
        except Exception as e:
            print(f"현재 날씨 조회 실패: {e}")
            return None
    
    def get_hourly_forecast(self, hours=6):
        """시간별 날씨 예보 가져오기 (최대 48시간)"""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'lat': self.ansan_lat,
                'lon': self.ansan_lon,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'kr'
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return self._format_hourly_forecast(data, hours)
            else:
                return None
                
        except Exception as e:
            print(f"시간별 예보 조회 실패: {e}")
            return None
    
    def _format_current_weather(self, data):
        """현재 날씨 데이터 포맷팅"""
        try:
            weather = {
                'location': '경기도 안산시',
                'temperature': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'wind_speed': round(data['wind']['speed'] * 3.6, 1),  # m/s를 km/h로 변환
                'visibility': data.get('visibility', 0) // 1000,  # m를 km로 변환
                'pressure': data['main']['pressure'],
                'icon': self._get_weather_emoji(data['weather'][0]['icon']),
                'time': get_korea_time().strftime('%H:%M')
            }
            return weather
        except Exception as e:
            print(f"현재 날씨 포맷팅 실패: {e}")
            return None
    
    def _format_hourly_forecast(self, data, hours):
        """시간별 예보 데이터 포맷팅"""
        try:
            forecasts = []
            for i, item in enumerate(data['list'][:hours]):
                forecast_time = datetime.fromtimestamp(item['dt'], KST)
                forecast = {
                    'time': forecast_time.strftime('%H시'),
                    'temperature': round(item['main']['temp']),
                    'description': item['weather'][0]['description'],
                    'rain_probability': round(item.get('pop', 0) * 100),  # 강수확률
                    'icon': self._get_weather_emoji(item['weather'][0]['icon'])
                }
                forecasts.append(forecast)
            return forecasts
        except Exception as e:
            print(f"시간별 예보 포맷팅 실패: {e}")
            return []
    
    def _get_weather_emoji(self, icon_code):
        """날씨 아이콘 코드를 이모지로 변환"""
        emoji_map = {
            '01d': '☀️',  # 맑음 (낮)
            '01n': '🌙',  # 맑음 (밤)
            '02d': '⛅',  # 구름 조금 (낮)
            '02n': '☁️',  # 구름 조금 (밤)
            '03d': '☁️',  # 구름 많음
            '03n': '☁️',  # 구름 많음
            '04d': '☁️',  # 흐림
            '04n': '☁️',  # 흐림
            '09d': '🌧️',  # 소나기
            '09n': '🌧️',  # 소나기
            '10d': '🌦️',  # 비 (낮)
            '10n': '🌧️',  # 비 (밤)
            '11d': '⛈️',  # 천둥번개
            '11n': '⛈️',  # 천둥번개
            '13d': '❄️',  # 눈
            '13n': '❄️',  # 눈
            '50d': '🌫️',  # 안개
            '50n': '🌫️'   # 안개
        }
        return emoji_map.get(icon_code, '🌤️')
    
    def get_weather_summary(self):
        """날씨 요약 정보 (오전/오후 요약 형식)"""
        hourly_forecast = self.get_hourly_forecast(hours=8) # 24시간(8*3) 데이터 가져오기
        
        if not hourly_forecast:
            return "⚠️ 날씨 정보를 가져올 수 없습니다."
            
        now = get_korea_time()
        morning_forecasts = []
        afternoon_forecasts = []

        for forecast in hourly_forecast:
            forecast_time = datetime.strptime(forecast['time'], '%H시').replace(year=now.year, month=now.month, day=now.day)
            
            # 오전 (6시 ~ 12시), 오후 (12시 ~ 18시)
            if 6 <= forecast_time.hour < 12:
                morning_forecasts.append(forecast)
            elif 12 <= forecast_time.hour < 18:
                afternoon_forecasts.append(forecast)

        def format_period_summary(period_name, forecasts):
            if not forecasts:
                return f" {period_name}: 정보 없음"

            temps = [f['temperature'] for f in forecasts]
            min_temp, max_temp = min(temps), max(temps)
            
            # 가장 빈번한 날씨 아이콘 선택
            icons = [f['icon'] for f in forecasts]
            icon = max(set(icons), key=icons.count) if icons else '🌤️'
            
            if min_temp == max_temp:
                temp_range = f"{min_temp}°C"
            else:
                temp_range = f"{min_temp}~{max_temp}°C"
                
            return f" {period_name}: {icon} {temp_range}"

        summary = "🌍 오늘의 날씨\n"
        summary += format_period_summary("오전", morning_forecasts) + "\n"
        summary += format_period_summary("오후", afternoon_forecasts)
        
        return summary

# 기상청 API 사용 버전 (대안)
class KMAWeatherService:
    def __init__(self):
        # 기상청 API 키 (URL 디코딩)
        encoded_key = os.getenv('KMA_API_KEY', 'XhrzW3H%2FRDDe%2B0RXDDLfhHMmBjgPtOWAAMRISzlRHrRIXfFwzbE9DV%2Bofbj3l3ZNucsrm7Aq1qG1MtlY4ZptDg%3D%3D')
        self.api_key = urllib.parse.unquote(encoded_key)
        self.base_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0"
        
        # 안산시 격자 좌표 (기상청 격자)
        self.nx = 58  # 안산시 X 격자
        self.ny = 121  # 안산시 Y 격자
    
    def get_weather_forecast(self):
        """기상청 단기예보 조회"""
        try:
            now = get_korea_time()
            base_date = now.strftime('%Y%m%d')
            base_time = self._get_base_time(now)
            
            url = f"{self.base_url}/getVilageFcst"
            params = {
                'serviceKey': self.api_key,
                'pageNo': 1,
                'numOfRows': 100,
                'dataType': 'JSON',
                'base_date': base_date,
                'base_time': base_time,
                'nx': self.nx,
                'ny': self.ny
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return self._parse_kma_data(data)
            else:
                return None
                
        except Exception as e:
            print(f"기상청 API 조회 실패: {e}")
            return None
    
    def _get_base_time(self, now):
        """기상청 API 발표 시간 계산"""
        # 기상청은 02, 05, 08, 11, 14, 17, 20, 23시에 발표
        base_times = ['0200', '0500', '0800', '1100', '1400', '1700', '2000', '2300']
        current_time = now.strftime('%H%M')
        
        for base_time in reversed(base_times):
            if current_time >= base_time:
                return base_time
        
        # 현재 시간이 02시 이전이면 전날 23시 데이터 사용
        return '2300'
    
    def _parse_kma_data(self, data):
        """기상청 데이터 파싱"""
        try:
            items = data['response']['body']['items']['item']
            weather_data = {}
            
            for item in items:
                fcst_date = item['fcstDate']
                fcst_time = item['fcstTime']
                category = item['category']
                value = item['fcstValue']
                
                key = f"{fcst_date}_{fcst_time}"
                if key not in weather_data:
                    weather_data[key] = {}
                
                weather_data[key][category] = value
            
            return self._format_kma_weather(weather_data)
            
        except Exception as e:
            print(f"기상청 데이터 파싱 실패: {e}")
            return None
    
    def _format_kma_weather(self, weather_data):
        """기상청 데이터 포맷팅"""
        formatted = []
        
        for key, data in list(weather_data.items())[:6]:  # 6시간 예보
            date_str, time_str = key.split('_')
            # datetime.strptime으로 파싱한 후 한국시간으로 설정
            time_obj = datetime.strptime(f"{date_str}{time_str}", '%Y%m%d%H%M')
            time_obj = KST.localize(time_obj)
            
            weather_info = {
                'time': time_obj.strftime('%H시'),
                'temperature': data.get('TMP', 'N/A'),  # 온도
                'humidity': data.get('REH', 'N/A'),     # 습도
                'rain_probability': data.get('POP', 'N/A'),  # 강수확률
                'sky_condition': self._get_sky_condition(data.get('SKY', '1')),
                'precipitation': data.get('PTY', '0')    # 강수형태
            }
            formatted.append(weather_info)
        
        return formatted
    
    def _get_sky_condition(self, sky_code):
        """하늘 상태 코드를 텍스트로 변환"""
        sky_map = {
            '1': '☀️ 맑음',
            '3': '⛅ 구름많음', 
            '4': '☁️ 흐림'
        }
        return sky_map.get(sky_code, '🌤️ 알수없음')
    
    def _get_precipitation_type(self, pty_code):
        """강수형태 코드를 이모지로 변환"""
        pty_map = {
            '0': '',  # 없음
            '1': '🌧️',  # 비
            '2': '🌨️',  # 비/눈
            '3': '❄️',  # 눈
            '4': '🌦️'   # 소나기
        }
        return pty_map.get(pty_code, '')
    
    def get_weather_summary(self):
        """기상청 날씨 요약 정보 (카카오톡 메시지용)"""
        forecast_data = self.get_weather_forecast()
        
        if not forecast_data:
            return "⚠️ 기상청 날씨 정보를 가져올 수 없습니다."
        
        # 현재 시간 기준 가장 가까운 예보 사용
        current_forecast = forecast_data[0] if forecast_data else None
        
        if not current_forecast:
            return "⚠️ 날씨 예보 데이터가 없습니다."
        
        # 현재 날씨 정보
        temp = current_forecast.get('temperature', 'N/A')
        humidity = current_forecast.get('humidity', 'N/A')
        rain_prob = current_forecast.get('rain_probability', 'N/A')
        sky_condition = current_forecast.get('sky_condition', '🌤️ 알수없음')
        precipitation = current_forecast.get('precipitation', '0')
        
        # 강수형태 이모지
        precip_emoji = self._get_precipitation_type(precipitation)
        
        summary = f"🌍 **경기도 안산시 날씨** (기상청)\n"
        summary += f"\n🕐 **현재 날씨**\n"
        sky_emoji = sky_condition.split()[0] if sky_condition else '🌤️'
        sky_text = sky_condition.split()[1] if len(sky_condition.split()) > 1 else ''
        weather_display = f"{sky_emoji}{precip_emoji}  {temp}°C {sky_text}"
        summary += f"{weather_display}\n"
        summary += f"💧 습도: {humidity}% | ☔ 강수확률: {rain_prob}%\n"
        
        # 비 예보 시 할증 안내 메시지 확인
        rain_info = self._check_rain_forecast(forecast_data)
        
        # 시간별 예보 (4시간)
        if len(forecast_data) > 1:
            summary += f"\n⏰ **시간별 예보**\n"
            for forecast in forecast_data[1:5]:  # 다음 4시간
                time_str = forecast.get('time', '')
                temp_str = forecast.get('temperature', 'N/A')
                rain_str = forecast.get('rain_probability', 'N/A')
                sky_str = forecast.get('sky_condition', '🌤️')
                precip_str = forecast.get('precipitation', '0')
                
                sky_emoji = sky_str.split()[0] if sky_str else '🌤️'
                precip_emoji = self._get_precipitation_type(precip_str)
                rain_percentage = f"({rain_str}%)" if rain_str != 'N/A' and int(rain_str) > 0 else ""
                
                # 가독성 개선: 아이콘과 온도 사이 충분한 공백 확보
                weather_icons = f"{sky_emoji}{precip_emoji}" if precip_emoji else sky_emoji
                summary += f"{time_str}: {weather_icons}  {temp_str}°C {rain_percentage}\n"
        
        # 비 예보 시 할증 안내 메시지 추가
        if rain_info['has_rain']:
            summary += f"\n💰 **할증 안내**\n"
            summary += f"🌧️  {rain_info['start_time']}부터 비가 예보되어 할증이 예상됩니다!\n"
            summary += f"💡  할증이 없으면 배달의민족에 신청하세요!"
        
        return summary
    
    def _check_rain_forecast(self, forecast_data):
        """비 예보 여부 및 시작 시점 확인 (현재 + 4시간 예보 기준)"""
        if not forecast_data:
            return {'has_rain': False, 'start_time': None}
        
        # 현재 + 다음 4시간 예보에서 비 확인
        check_forecasts = forecast_data[:5] if len(forecast_data) >= 5 else forecast_data
        
        for forecast in check_forecasts:
            precipitation = forecast.get('precipitation', '0')
            # 강수형태 코드: 1=비, 2=비/눈, 4=소나기
            if precipitation in ['1', '2', '4']:
                time_str = forecast.get('time', '현재')
                return {'has_rain': True, 'start_time': time_str}
        
        return {'has_rain': False, 'start_time': None}

# 사용 예시 (기상청 API 우선 사용)
def get_ansan_weather():
    """안산시 날씨 정보 가져오기 (기상청 API 우선)"""
    # 1순위: 기상청 API 사용
    kma_service = KMAWeatherService()
    kma_weather = kma_service.get_weather_summary()
    
    if kma_weather and "⚠️" not in kma_weather:
        return kma_weather
    
    # 2순위: OpenWeatherMap API 사용 (백업)
    print("기상청 API 실패, OpenWeatherMap API로 대체")
    weather_service = WeatherService()
    return weather_service.get_weather_summary()

if __name__ == "__main__":
    # 테스트
    weather = get_ansan_weather()
    print(weather) 