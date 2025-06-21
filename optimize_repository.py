#!/usr/bin/env python3
"""
🚀 GitHub 리포지토리 통합 최적화 시스템

주요 기능:
1. 코드 최적화 및 중복 제거
2. 불필요한 파일 정리
3. 의존성 최적화
4. 성능 분석 및 리포트
5. 자동화 스크립트 최적화
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Set
import logging
from datetime import datetime
import re

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RepositoryOptimizer:
    """리포지토리 최적화 관리자"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.optimization_stats = {
            'files_analyzed': 0,
            'files_optimized': 0,
            'duplicates_removed': 0,
            'size_reduced_mb': 0,
            'errors': []
        }
        
    def analyze_repository(self) -> Dict[str, Any]:
        """리포지토리 전체 분석"""
        logger.info("🔍 리포지토리 분석 시작...")
        
        analysis = {
            'total_files': 0,
            'python_files': 0,
            'log_files': 0,
            'large_files': [],
            'duplicate_files': [],
            'unused_files': [],
            'optimization_opportunities': []
        }
        
        # 파일 분석
        for file_path in self.repo_path.rglob('*'):
            if file_path.is_file() and not self._should_ignore_file(file_path):
                analysis['total_files'] += 1
                
                # Python 파일 분석
                if file_path.suffix == '.py':
                    analysis['python_files'] += 1
                    self._analyze_python_file(file_path, analysis)
                
                # 로그 파일 분석
                elif file_path.suffix == '.log' or 'debug_' in file_path.name:
                    analysis['log_files'] += 1
                
                # 큰 파일 체크
                file_size_mb = file_path.stat().st_size / (1024 * 1024)
                if file_size_mb > 5:  # 5MB 이상
                    analysis['large_files'].append({
                        'path': str(file_path),
                        'size_mb': round(file_size_mb, 2)
                    })
        
        # 중복 파일 찾기
        analysis['duplicate_files'] = self._find_duplicate_files()
        
        # 사용되지 않는 파일 찾기
        analysis['unused_files'] = self._find_unused_files()
        
        logger.info(f"✅ 분석 완료: {analysis['total_files']}개 파일")
        return analysis
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """무시해야 할 파일인지 확인"""
        ignore_patterns = [
            '.git/', '__pycache__/', '.venv/', 'node_modules/',
            '.DS_Store', '*.pyc', '*.pyo', '*.pyd'
        ]
        
        file_str = str(file_path)
        return any(pattern in file_str for pattern in ignore_patterns)
    
    def _analyze_python_file(self, file_path: Path, analysis: Dict[str, Any]):
        """Python 파일 분석"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 중복 코드 패턴 찾기
            if self._has_duplicate_code_patterns(content):
                analysis['optimization_opportunities'].append({
                    'file': str(file_path),
                    'type': 'duplicate_code',
                    'description': '중복 코드 패턴 발견'
                })
            
            # 불필요한 import 찾기
            unused_imports = self._find_unused_imports(content)
            if unused_imports:
                analysis['optimization_opportunities'].append({
                    'file': str(file_path),
                    'type': 'unused_imports',
                    'imports': unused_imports
                })
                
        except Exception as e:
            logger.warning(f"⚠️ Python 파일 분석 실패 {file_path}: {e}")
    
    def _has_duplicate_code_patterns(self, content: str) -> bool:
        """중복 코드 패턴 감지"""
        # 간단한 중복 패턴 감지 (함수명, 클래스명 등)
        function_patterns = re.findall(r'def (\w+)\(', content)
        class_patterns = re.findall(r'class (\w+)', content)
        
        # 중복된 이름이 있는지 확인
        return (len(function_patterns) != len(set(function_patterns)) or
                len(class_patterns) != len(set(class_patterns)))
    
    def _find_unused_imports(self, content: str) -> List[str]:
        """사용되지 않는 import 찾기"""
        import_lines = re.findall(r'^import (\w+)', content, re.MULTILINE)
        from_imports = re.findall(r'^from \w+ import (\w+)', content, re.MULTILINE)
        
        all_imports = import_lines + from_imports
        unused = []
        
        for imp in all_imports:
            # 간단한 사용 여부 체크 (정확하지 않지만 기본적인 감지)
            if imp not in content.replace(f'import {imp}', '').replace(f'from', ''):
                unused.append(imp)
        
        return unused
    
    def _find_duplicate_files(self) -> List[Dict[str, Any]]:
        """중복 파일 찾기 (이름 기준)"""
        file_names = {}
        duplicates = []
        
        for file_path in self.repo_path.rglob('*'):
            if file_path.is_file() and not self._should_ignore_file(file_path):
                name = file_path.name
                if name in file_names:
                    duplicates.append({
                        'name': name,
                        'paths': [file_names[name], str(file_path)]
                    })
                else:
                    file_names[name] = str(file_path)
        
        return duplicates
    
    def _find_unused_files(self) -> List[str]:
        """사용되지 않는 파일 찾기"""
        # 간단한 휴리스틱으로 사용되지 않는 파일 감지
        unused = []
        
        # 오래된 백업 파일들
        for file_path in self.repo_path.rglob('*'):
            if file_path.is_file():
                name = file_path.name
                if any(pattern in name for pattern in ['_backup', '_old', '_temp', '.bak']):
                    unused.append(str(file_path))
        
        return unused
    
    def optimize_python_files(self) -> Dict[str, Any]:
        """Python 파일 최적화"""
        logger.info("🐍 Python 파일 최적화 시작...")
        
        results = {
            'optimized_files': 0,
            'removed_imports': 0,
            'formatted_files': 0,
            'errors': []
        }
        
        for file_path in self.repo_path.rglob('*.py'):
            if self._should_ignore_file(file_path):
                continue
                
            try:
                # 파일 최적화
                if self._optimize_python_file(file_path):
                    results['optimized_files'] += 1
                    
            except Exception as e:
                error_msg = f"Python 파일 최적화 실패 {file_path}: {e}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
        
        logger.info(f"✅ Python 최적화 완료: {results['optimized_files']}개 파일")
        return results
    
    def _optimize_python_file(self, file_path: Path) -> bool:
        """개별 Python 파일 최적화"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            optimized_content = original_content
            
            # 불필요한 공백 제거
            optimized_content = re.sub(r'\n\s*\n\s*\n', '\n\n', optimized_content)
            
            # 중복 import 제거
            optimized_content = self._remove_duplicate_imports(optimized_content)
            
            # 변경사항이 있으면 파일 업데이트
            if optimized_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(optimized_content)
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"파일 최적화 실패 {file_path}: {e}")
            return False
    
    def _remove_duplicate_imports(self, content: str) -> str:
        """중복 import 제거"""
        lines = content.split('\n')
        imports = set()
        optimized_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                if stripped not in imports:
                    imports.add(stripped)
                    optimized_lines.append(line)
                # 중복 import는 건너뛰기
            else:
                optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def clean_unnecessary_files(self) -> Dict[str, Any]:
        """불필요한 파일 정리"""
        logger.info("🧹 불필요한 파일 정리 시작...")
        
        results = {
            'deleted_files': 0,
            'freed_space_mb': 0,
            'errors': []
        }
        
        # 정리할 파일 패턴
        cleanup_patterns = [
            '*.pyc', '*.pyo', '*.pyd',
            '__pycache__/',
            '*.log',
            'debug_*.html',
            '*.tmp', '*.temp',
            '.DS_Store',
            'Thumbs.db'
        ]
        
        for pattern in cleanup_patterns:
            for file_path in self.repo_path.rglob(pattern):
                try:
                    if file_path.is_file():
                        file_size = file_path.stat().st_size / (1024 * 1024)
                        file_path.unlink()
                        results['deleted_files'] += 1
                        results['freed_space_mb'] += file_size
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)
                        results['deleted_files'] += 1
                        
                except Exception as e:
                    error_msg = f"파일 삭제 실패 {file_path}: {e}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
        
        logger.info(f"✅ 정리 완료: {results['deleted_files']}개 파일, {results['freed_space_mb']:.1f}MB 절약")
        return results
    
    def optimize_dependencies(self) -> Dict[str, Any]:
        """의존성 최적화"""
        logger.info("📦 의존성 최적화 시작...")
        
        results = {
            'requirements_optimized': False,
            'unused_packages': [],
            'errors': []
        }
        
        # requirements.txt 파일들 찾기
        req_files = list(self.repo_path.rglob('requirements*.txt'))
        
        for req_file in req_files:
            try:
                if self._optimize_requirements_file(req_file):
                    results['requirements_optimized'] = True
                    
            except Exception as e:
                error_msg = f"requirements 최적화 실패 {req_file}: {e}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
        
        return results
    
    def _optimize_requirements_file(self, req_file: Path) -> bool:
        """requirements.txt 파일 최적화"""
        try:
            with open(req_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 중복 제거 및 정렬
            unique_lines = list(set(line.strip() for line in lines if line.strip()))
            unique_lines.sort()
            
            optimized_content = '\n'.join(unique_lines) + '\n'
            
            # 변경사항이 있으면 업데이트
            original_content = ''.join(lines)
            if optimized_content != original_content:
                with open(req_file, 'w', encoding='utf-8') as f:
                    f.write(optimized_content)
                logger.info(f"📝 {req_file} 최적화 완료")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"requirements 파일 최적화 실패 {req_file}: {e}")
            return False
    
    def generate_optimization_report(self, analysis: Dict[str, Any]) -> str:
        """최적화 리포트 생성"""
        report = f"""🚀 GitHub 리포지토리 최적화 리포트

📅 생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 분석 결과:
• 전체 파일 수: {analysis['total_files']}개
• Python 파일: {analysis['python_files']}개
• 로그 파일: {analysis['log_files']}개
• 큰 파일 (5MB+): {len(analysis['large_files'])}개
• 중복 파일: {len(analysis['duplicate_files'])}개
• 사용되지 않는 파일: {len(analysis['unused_files'])}개

🎯 최적화 기회:
• 최적화 가능 항목: {len(analysis['optimization_opportunities'])}개

📈 최적화 통계:
• 분석된 파일: {self.optimization_stats['files_analyzed']}개
• 최적화된 파일: {self.optimization_stats['files_optimized']}개
• 제거된 중복: {self.optimization_stats['duplicates_removed']}개
• 절약된 용량: {self.optimization_stats['size_reduced_mb']:.1f}MB

💡 권장사항:
"""
        
        # 권장사항 추가
        if analysis['large_files']:
            report += "• 큰 파일들을 .gitignore에 추가하거나 압축 고려\n"
        
        if analysis['duplicate_files']:
            report += "• 중복 파일들을 통합하거나 제거\n"
        
        if analysis['unused_files']:
            report += "• 사용되지 않는 파일들 삭제\n"
        
        if analysis['optimization_opportunities']:
            report += "• Python 코드 리팩토링 고려\n"
        
        return report
    
    def run_full_optimization(self) -> Dict[str, Any]:
        """전체 최적화 실행"""
        logger.info("🚀 전체 리포지토리 최적화 시작...")
        
        # 1. 분석
        analysis = self.analyze_repository()
        
        # 2. Python 파일 최적화
        python_results = self.optimize_python_files()
        
        # 3. 불필요한 파일 정리
        cleanup_results = self.clean_unnecessary_files()
        
        # 4. 의존성 최적화
        deps_results = self.optimize_dependencies()
        
        # 5. 통계 업데이트
        self.optimization_stats.update({
            'files_analyzed': analysis['total_files'],
            'files_optimized': python_results['optimized_files'] + cleanup_results['deleted_files'],
            'size_reduced_mb': cleanup_results['freed_space_mb']
        })
        
        # 6. 리포트 생성
        report = self.generate_optimization_report(analysis)
        
        # 리포트 파일 저장
        report_file = f"optimization_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"✅ 전체 최적화 완료! 리포트: {report_file}")
        
        return {
            'analysis': analysis,
            'python_optimization': python_results,
            'cleanup': cleanup_results,
            'dependencies': deps_results,
            'report_file': report_file,
            'stats': self.optimization_stats
        }

    def optimize_github_actions(self):
        """GitHub Actions 워크플로우 최적화"""
        print("\n🚀 GitHub Actions 워크플로우 최적화 중...")
        
        workflows_dir = Path('.github/workflows')
        if not workflows_dir.exists():
            return
            
        optimizations = []
        
        for workflow_file in workflows_dir.glob('*.yml'):
            try:
                with open(workflow_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_size = len(content)
                
                # 1. 중복 단계 제거
                content = self._remove_duplicate_steps(content)
                
                # 2. 캐시 최적화 추가
                content = self._optimize_caching(content)
                
                # 3. 타임아웃 최적화
                content = self._optimize_timeouts(content)
                
                # 4. 조건부 실행 최적화
                content = self._optimize_conditions(content)
                
                new_size = len(content)
                
                if new_size != original_size:
                    with open(workflow_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    optimizations.append({
                        'file': workflow_file.name,
                        'original_size': original_size,
                        'new_size': new_size,
                        'saved': original_size - new_size
                    })
                    
            except Exception as e:
                print(f"⚠️ {workflow_file.name} 최적화 중 오류: {e}")
        
        if optimizations:
            print(f"✅ {len(optimizations)}개 워크플로우 최적화 완료")
            for opt in optimizations:
                print(f"   📄 {opt['file']}: {opt['saved']}바이트 절약")
        else:
            print("✅ 모든 워크플로우가 이미 최적화되어 있습니다")
    
    def _remove_duplicate_steps(self, content):
        """중복 단계 제거"""
        lines = content.split('\n')
        seen_steps = set()
        result_lines = []
        
        for line in lines:
            if 'name:' in line and 'steps:' not in line:
                step_name = line.strip()
                if step_name not in seen_steps:
                    seen_steps.add(step_name)
                    result_lines.append(line)
                else:
                    continue
            else:
                result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    def _optimize_caching(self, content):
        """캐시 최적화"""
        if 'cache: \'pip\'' in content and 'cache-dependency-path:' not in content:
            content = content.replace(
                'cache: \'pip\'',
                'cache: \'pip\'\n        cache-dependency-path: \'requirements.txt\''
            )
        return content
    
    def _optimize_timeouts(self, content):
        """타임아웃 최적화"""
        if 'timeout-minutes:' not in content and 'runs-on: ubuntu-latest' in content:
            content = content.replace(
                'runs-on: ubuntu-latest',
                'runs-on: ubuntu-latest\n    timeout-minutes: 10'
            )
        return content
    
    def _optimize_conditions(self, content):
        """조건부 실행 최적화"""
        if 'if: github.repository ==' not in content and 'jobs:' in content:
            content = content.replace(
                'steps:',
                'if: github.repository == github.event.repository.full_name\n    \n    steps:'
            )
        return content

def main():
    """메인 실행 함수"""
    print("🚀 GitHub 리포지토리 통합 최적화 시스템")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        optimizer = RepositoryOptimizer()
        
        if command == 'analyze':
            # 분석만 실행
            analysis = optimizer.analyze_repository()
            print(json.dumps(analysis, indent=2, ensure_ascii=False))
            
        elif command == 'python':
            # Python 파일만 최적화
            results = optimizer.optimize_python_files()
            print(f"✅ Python 최적화 완료: {results}")
            
        elif command == 'clean':
            # 파일 정리만 실행
            results = optimizer.clean_unnecessary_files()
            print(f"✅ 파일 정리 완료: {results}")
            
        elif command == 'deps':
            # 의존성 최적화만 실행
            results = optimizer.optimize_dependencies()
            print(f"✅ 의존성 최적화 완료: {results}")
            
        elif command == 'full':
            # 전체 최적화 실행
            results = optimizer.run_full_optimization()
            print("✅ 전체 최적화 완료!")
            print(f"📋 리포트: {results['report_file']}")
            
        elif command == 'actions':
            # GitHub Actions 워크플로우 최적화
            optimizer.optimize_github_actions()
            
        else:
            print("사용법: python optimize_repository.py [analyze|python|clean|deps|full|actions]")
    
    else:
        # 기본: 전체 최적화 실행
        optimizer = RepositoryOptimizer()
        optimizer.run_full_optimization()

if __name__ == "__main__":
    main() 