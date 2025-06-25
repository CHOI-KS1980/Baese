#!/usr/bin/env python3
"""
📊 Auto Finance 고도화 대시보드 시작 스크립트
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from dashboard.advanced_dashboard import advanced_dashboard
    
    if __name__ == '__main__':
        print("🚀 Auto Finance 고도화 대시보드 시작")
        print("📊 대시보드: http://localhost:8050")
        advanced_dashboard.run(debug=True)
        
except ImportError as e:
    print(f"❌ 대시보드 모듈 임포트 실패: {e}")
    print("의존성을 설치하세요: pip install -r requirements.txt")
except Exception as e:
    print(f"❌ 대시보드 실행 실패: {e}")
