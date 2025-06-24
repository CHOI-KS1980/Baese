"""
⚙️ 설정 검증 유틸리티
환경변수, 설정 파일, API 키 검증 등
"""

import os
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
from auto_finance.utils.logger import setup_logger

logger = setup_logger(__name__)

class ConfigValidator:
    """설정 검증 클래스"""
    
    def __init__(self):
        self.validation_errors = []
        self.validation_warnings = []
    
    def validate_environment_variables(self, required_vars: List[str], 
                                     optional_vars: List[str] = None) -> Dict[str, Any]:
        """환경변수 검증"""
        validation_result = {
            'is_valid': True,
            'missing_required': [],
            'missing_optional': [],
            'available_vars': [],
            'errors': []
        }
        
        # 필수 환경변수 검증
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                validation_result['missing_required'].append(var)
                validation_result['is_valid'] = False
                self.validation_errors.append(f"필수 환경변수 누락: {var}")
            else:
                validation_result['available_vars'].append(var)
        
        # 선택적 환경변수 검증
        if optional_vars:
            for var in optional_vars:
                value = os.getenv(var)
                if not value:
                    validation_result['missing_optional'].append(var)
                    self.validation_warnings.append(f"선택적 환경변수 누락: {var}")
                else:
                    validation_result['available_vars'].append(var)
        
        return validation_result
    
    def validate_api_keys(self, api_config: Dict[str, Any]) -> Dict[str, Any]:
        """API 키 검증"""
        validation_result = {
            'is_valid': True,
            'valid_apis': [],
            'invalid_apis': [],
            'errors': []
        }
        
        for api_name, config in api_config.items():
            api_key = config.get('api_key')
            required = config.get('required', False)
            
            if not api_key:
                if required:
                    validation_result['invalid_apis'].append(api_name)
                    validation_result['is_valid'] = False
                    self.validation_errors.append(f"필수 API 키 누락: {api_name}")
                else:
                    self.validation_warnings.append(f"선택적 API 키 누락: {api_name}")
            else:
                # API 키 형식 검증
                if self._validate_api_key_format(api_key, config.get('format')):
                    validation_result['valid_apis'].append(api_name)
                else:
                    validation_result['invalid_apis'].append(api_name)
                    validation_result['is_valid'] = False
                    self.validation_errors.append(f"API 키 형식 오류: {api_name}")
        
        return validation_result
    
    def _validate_api_key_format(self, api_key: str, expected_format: Optional[str] = None) -> bool:
        """API 키 형식 검증"""
        if not api_key:
            return False
        
        # 기본 검증 (길이, 문자 등)
        if len(api_key) < 10:
            return False
        
        # 특정 형식 검증
        if expected_format:
            if expected_format == 'openai':
                return api_key.startswith('sk-')
            elif expected_format == 'google':
                return len(api_key) >= 30
            elif expected_format == 'alpha_vantage':
                return len(api_key) >= 10
        
        return True
    
    def validate_file_paths(self, paths_config: Dict[str, str]) -> Dict[str, Any]:
        """파일 경로 검증"""
        validation_result = {
            'is_valid': True,
            'valid_paths': [],
            'invalid_paths': [],
            'errors': []
        }
        
        for path_name, path_value in paths_config.items():
            path = Path(path_value)
            
            if path.exists():
                validation_result['valid_paths'].append(path_name)
            else:
                # 디렉토리 생성 시도
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    validation_result['valid_paths'].append(path_name)
                    logger.info(f"📁 디렉토리 생성: {path_value}")
                except Exception as e:
                    validation_result['invalid_paths'].append(path_name)
                    validation_result['is_valid'] = False
                    error_msg = f"경로 생성 실패 ({path_name}): {e}"
                    validation_result['errors'].append(error_msg)
                    self.validation_errors.append(error_msg)
        
        return validation_result
    
    def validate_urls(self, urls_config: Dict[str, str]) -> Dict[str, Any]:
        """URL 형식 검증"""
        validation_result = {
            'is_valid': True,
            'valid_urls': [],
            'invalid_urls': [],
            'errors': []
        }
        
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        for url_name, url_value in urls_config.items():
            if url_pattern.match(url_value):
                validation_result['valid_urls'].append(url_name)
            else:
                validation_result['invalid_urls'].append(url_name)
                validation_result['is_valid'] = False
                error_msg = f"잘못된 URL 형식 ({url_name}): {url_value}"
                validation_result['errors'].append(error_msg)
                self.validation_errors.append(error_msg)
        
        return validation_result
    
    def validate_data_types(self, data: Dict[str, Any], 
                           expected_types: Dict[str, type]) -> Dict[str, Any]:
        """데이터 타입 검증"""
        validation_result = {
            'is_valid': True,
            'valid_fields': [],
            'invalid_fields': [],
            'errors': []
        }
        
        for field_name, expected_type in expected_types.items():
            if field_name not in data:
                error_msg = f"필드 누락: {field_name}"
                validation_result['errors'].append(error_msg)
                validation_result['is_valid'] = False
                continue
            
            actual_value = data[field_name]
            if isinstance(actual_value, expected_type):
                validation_result['valid_fields'].append(field_name)
            else:
                validation_result['invalid_fields'].append(field_name)
                validation_result['is_valid'] = False
                error_msg = f"타입 불일치 ({field_name}): 예상 {expected_type.__name__}, 실제 {type(actual_value).__name__}"
                validation_result['errors'].append(error_msg)
                self.validation_errors.append(error_msg)
        
        return validation_result
    
    def validate_config_file(self, config_file: str) -> Dict[str, Any]:
        """설정 파일 검증"""
        validation_result = {
            'is_valid': True,
            'file_exists': False,
            'is_readable': False,
            'is_valid_json': False,
            'errors': []
        }
        
        config_path = Path(config_file)
        
        # 파일 존재 여부
        if config_path.exists():
            validation_result['file_exists'] = True
        else:
            validation_result['is_valid'] = False
            error_msg = f"설정 파일이 존재하지 않습니다: {config_file}"
            validation_result['errors'].append(error_msg)
            self.validation_errors.append(error_msg)
            return validation_result
        
        # 파일 읽기 가능 여부
        if os.access(config_path, os.R_OK):
            validation_result['is_readable'] = True
        else:
            validation_result['is_valid'] = False
            error_msg = f"설정 파일을 읽을 수 없습니다: {config_file}"
            validation_result['errors'].append(error_msg)
            self.validation_errors.append(error_msg)
            return validation_result
        
        # JSON 형식 검증
        try:
            import json
            with open(config_path, 'r', encoding='utf-8') as f:
                json.load(f)
            validation_result['is_valid_json'] = True
        except json.JSONDecodeError as e:
            validation_result['is_valid'] = False
            error_msg = f"잘못된 JSON 형식 ({config_file}): {e}"
            validation_result['errors'].append(error_msg)
            self.validation_errors.append(error_msg)
        except Exception as e:
            validation_result['is_valid'] = False
            error_msg = f"설정 파일 읽기 실패 ({config_file}): {e}"
            validation_result['errors'].append(error_msg)
            self.validation_errors.append(error_msg)
        
        return validation_result
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """검증 결과 요약"""
        return {
            'total_errors': len(self.validation_errors),
            'total_warnings': len(self.validation_warnings),
            'errors': self.validation_errors,
            'warnings': self.validation_warnings,
            'timestamp': datetime.now().isoformat()
        }
    
    def clear_validation_results(self):
        """검증 결과 초기화"""
        self.validation_errors.clear()
        self.validation_warnings.clear()

# 전역 설정 검증기 인스턴스
config_validator = ConfigValidator() 