import json
import sys

def verify_data():
    """
    대시보드 데이터를 검증하고, 실제 데이터인지 확인합니다.
    테스트 데이터가 감지되면 오류를 발생시킵니다.
    """
    try:
        with open('dashboard/api/latest-data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        riders = data.get('riders', [])
        test_names = ['김철수', '이영희', '박민수', '정수진']
        
        if len(riders) > 0:
            # 라이더 중 테스트 이름이 있는지 확인
            is_test_data = any(rider.get('name', '') in test_names for rider in riders)
            if is_test_data:
                print('⚠️ 테스트 데이터 감지됨 - 실제 데이터로 재시도 필요')
                sys.exit(1)

        print('✅ 실제 G라이더 데이터 확인됨')
        print(f"📊 총점: {data.get('총점', 0)}점")
        print(f"🏍️ 라이더: {len(riders)}명")
        if len(riders) > 0:
            top_rider = max(riders, key=lambda x: x.get('complete', 0))
            print(f"🏆 TOP 라이더: {top_rider.get('name', '이름없음')} ({top_rider.get('complete', 0)}건)")
            
    except FileNotFoundError:
        print('❌ 검증 실패: dashboard/api/latest-data.json 파일을 찾을 수 없습니다.')
        sys.exit(1)
    except Exception as e:
        print(f'❌ 데이터 검증 중 예외 발생: {e}')
        sys.exit(1)

if __name__ == "__main__":
    verify_data() 