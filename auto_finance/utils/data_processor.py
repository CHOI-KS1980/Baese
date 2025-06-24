"""
📊 데이터 처리 유틸리티
데이터 정제, 변환, 검증, 통계 계산 등
"""

import re
import json
import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from auto_finance.utils.logger import setup_logger

logger = setup_logger(__name__)

class DataProcessor:
    """데이터 처리 클래스"""
    
    def __init__(self):
        self.processed_count = 0
        self.error_count = 0
    
    def clean_text(self, text: str) -> str:
        """텍스트 정제"""
        if not text:
            return ""
        
        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)
        
        # 특수 문자 정리
        text = re.sub(r'[\r\n\t]+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # 앞뒤 공백 제거
        text = text.strip()
        
        return text
    
    def extract_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """키워드 추출"""
        if not text or not keywords:
            return []
        
        found_keywords = []
        text_lower = text.lower()
        
        for keyword in keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """텍스트 유사도 계산 (간단한 Jaccard 유사도)"""
        if not text1 or not text2:
            return 0.0
        
        # 단어 집합으로 변환
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def remove_duplicates(self, data_list: List[Dict], key_field: str = 'title', 
                         similarity_threshold: float = 0.8) -> List[Dict]:
        """중복 데이터 제거"""
        if not data_list:
            return []
        
        unique_data = []
        processed_titles = []
        
        for item in data_list:
            title = item.get(key_field, '')
            if not title:
                continue
            
            # 유사도 체크
            is_duplicate = False
            for processed_title in processed_titles:
                similarity = self.calculate_similarity(title, processed_title)
                if similarity >= similarity_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_data.append(item)
                processed_titles.append(title)
        
        removed_count = len(data_list) - len(unique_data)
        if removed_count > 0:
            logger.info(f"🗑️ 중복 데이터 제거: {removed_count}개")
        
        return unique_data
    
    def validate_data(self, data: Dict, required_fields: List[str]) -> Dict[str, Any]:
        """데이터 검증"""
        validation_result = {
            'is_valid': True,
            'missing_fields': [],
            'errors': []
        }
        
        for field in required_fields:
            if field not in data or not data[field]:
                validation_result['missing_fields'].append(field)
                validation_result['is_valid'] = False
        
        return validation_result
    
    def normalize_data(self, data: Dict) -> Dict:
        """데이터 정규화"""
        normalized = {}
        
        for key, value in data.items():
            # 키 정규화
            normalized_key = key.lower().replace(' ', '_')
            
            # 값 정규화
            if isinstance(value, str):
                normalized_value = self.clean_text(value)
            elif isinstance(value, (int, float)):
                normalized_value = value
            elif isinstance(value, list):
                normalized_value = [self.clean_text(str(item)) if isinstance(item, str) else item 
                                  for item in value]
            elif isinstance(value, dict):
                normalized_value = self.normalize_data(value)
            else:
                normalized_value = str(value)
            
            normalized[normalized_key] = normalized_value
        
        return normalized
    
    def calculate_statistics(self, data_list: List[Dict]) -> Dict[str, Any]:
        """데이터 통계 계산"""
        if not data_list:
            return {}
        
        stats = {
            'total_count': len(data_list),
            'fields': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # 필드별 통계
        if data_list:
            sample_item = data_list[0]
            for field, value in sample_item.items():
                field_stats = {
                    'count': 0,
                    'null_count': 0,
                    'unique_count': 0,
                    'avg_length': 0
                }
                
                values = []
                lengths = []
                
                for item in data_list:
                    field_value = item.get(field)
                    if field_value is not None and field_value != "":
                        field_stats['count'] += 1
                        values.append(field_value)
                        
                        if isinstance(field_value, str):
                            lengths.append(len(field_value))
                    else:
                        field_stats['null_count'] += 1
                
                if values:
                    field_stats['unique_count'] = len(set(values))
                    if lengths:
                        field_stats['avg_length'] = sum(lengths) / len(lengths)
                
                stats['fields'][field] = field_stats
        
        return stats
    
    def filter_data(self, data_list: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """데이터 필터링"""
        if not data_list or not filters:
            return data_list
        
        filtered_data = []
        
        for item in data_list:
            matches_all_filters = True
            
            for field, filter_value in filters.items():
                item_value = item.get(field)
                
                if isinstance(filter_value, dict):
                    # 복잡한 필터 (범위, 정규식 등)
                    if 'min' in filter_value and item_value < filter_value['min']:
                        matches_all_filters = False
                    elif 'max' in filter_value and item_value > filter_value['max']:
                        matches_all_filters = False
                    elif 'regex' in filter_value:
                        if not re.search(filter_value['regex'], str(item_value)):
                            matches_all_filters = False
                else:
                    # 단순 필터
                    if item_value != filter_value:
                        matches_all_filters = False
                
                if not matches_all_filters:
                    break
            
            if matches_all_filters:
                filtered_data.append(item)
        
        return filtered_data
    
    def sort_data(self, data_list: List[Dict], sort_field: str, 
                  reverse: bool = False) -> List[Dict]:
        """데이터 정렬"""
        if not data_list:
            return []
        
        try:
            return sorted(data_list, key=lambda x: x.get(sort_field, ''), reverse=reverse)
        except Exception as e:
            logger.error(f"❌ 데이터 정렬 실패: {e}")
            return data_list
    
    def convert_to_dataframe(self, data_list: List[Dict]) -> pd.DataFrame:
        """리스트를 DataFrame으로 변환"""
        if not data_list:
            return pd.DataFrame()
        
        try:
            df = pd.DataFrame(data_list)
            logger.info(f"📊 DataFrame 변환 완료: {len(df)}행 x {len(df.columns)}열")
            return df
        except Exception as e:
            logger.error(f"❌ DataFrame 변환 실패: {e}")
            return pd.DataFrame()
    
    def save_to_file(self, data: Any, file_path: str, format: str = 'json') -> bool:
        """데이터를 파일로 저장"""
        try:
            if format == 'json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            elif format == 'csv':
                if isinstance(data, pd.DataFrame):
                    data.to_csv(file_path, index=False, encoding='utf-8')
                else:
                    pd.DataFrame(data).to_csv(file_path, index=False, encoding='utf-8')
            else:
                logger.error(f"❌ 지원하지 않는 형식: {format}")
                return False
            
            logger.info(f"💾 파일 저장 완료: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 파일 저장 실패 ({file_path}): {e}")
            return False
    
    def load_from_file(self, file_path: str, format: str = 'json') -> Any:
        """파일에서 데이터 로드"""
        try:
            if format == 'json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif format == 'csv':
                return pd.read_csv(file_path, encoding='utf-8')
            else:
                logger.error(f"❌ 지원하지 않는 형식: {format}")
                return None
            
        except Exception as e:
            logger.error(f"❌ 파일 로드 실패 ({file_path}): {e}")
            return None

# 전역 데이터 프로세서 인스턴스
data_processor = DataProcessor() 