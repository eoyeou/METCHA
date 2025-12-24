"""
Fixtures 로드 스크립트
모든 fixtures를 올바른 순서로 로드합니다.
"""
import os
import sys
import django

# Django 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pjt.settings')
django.setup()

from django.core.management import call_command
from django.core.management.base import CommandError


def load_fixtures():
    """모든 fixtures를 올바른 순서로 로드"""
    fixtures_order = [
        'movies/fixtures/movies_initial_fixed.json',
    ]
    
    print("=" * 60)
    print("Fixtures 로드 시작")
    print("=" * 60)
    
    # 영화 데이터 로드
    for fixture in fixtures_order:
        if os.path.exists(fixture):
            print(f"\n[{fixture}] 로드 중...")
            try:
                call_command('loaddata', fixture, verbosity=1)
                print(f"[OK] {fixture} 로드 완료")
            except CommandError as e:
                print(f"[FAIL] {fixture} 로드 실패: {e}")
            except Exception as e:
                print(f"[ERROR] {fixture} 로드 중 오류 발생: {e}")
        else:
            print(f"[NOT FOUND] {fixture} 파일을 찾을 수 없습니다.")
    
    # 리뷰 데이터는 사용자 데이터가 필요하므로 별도로 처리
    reviews_fixture = 'reviews/fixtures/reviews_sample.json'
    if os.path.exists(reviews_fixture):
        print(f"\n[{reviews_fixture}] 로드 중...")
        print("[주의] 리뷰 데이터를 로드하려면 사용자 데이터가 필요합니다.")
        try:
            call_command('loaddata', reviews_fixture, verbosity=1)
            print(f"[OK] {reviews_fixture} 로드 완료")
        except CommandError as e:
            print(f"[FAIL] {reviews_fixture} 로드 실패: {e}")
            print("\n[해결 방법]:")
            print("   1. 먼저 테스트 사용자를 생성하세요:")
            print("      python load_data.py test-data 10 20")
            print("   2. 또는 기존 사용자 데이터가 있는지 확인하세요.")
        except Exception as e:
            print(f"[ERROR] {reviews_fixture} 로드 중 오류 발생: {e}")
    
    print("\n" + "=" * 60)
    print("Fixtures 로드 완료")
    print("=" * 60)


def load_reviews_with_users():
    """사용자 생성 후 리뷰 데이터 로드"""
    from load_data import create_test_users_and_reviews
    
    print("=" * 60)
    print("사용자 및 리뷰 데이터 로드 시작")
    print("=" * 60)
    
    # 먼저 테스트 사용자 생성 (기본: 10명, 각 0개 리뷰)
    print("\n테스트 사용자 생성 중...")
    try:
        num_users, _ = create_test_users_and_reviews(num_users=10, reviews_per_user=0)
        print(f"[OK] {num_users}명의 사용자 생성 완료")
    except Exception as e:
        print(f"[FAIL] 사용자 생성 실패: {e}")
        return
    
    # 리뷰 fixtures 로드
    reviews_fixture = 'reviews/fixtures/reviews_sample.json'
    if os.path.exists(reviews_fixture):
        print(f"\n[{reviews_fixture}] 로드 중...")
        try:
            call_command('loaddata', reviews_fixture, verbosity=1)
            print(f"[OK] {reviews_fixture} 로드 완료")
        except CommandError as e:
            print(f"[FAIL] {reviews_fixture} 로드 실패: {e}")
        except Exception as e:
            print(f"[ERROR] {reviews_fixture} 로드 중 오류 발생: {e}")
    
    print("\n" + "=" * 60)
    print("사용자 및 리뷰 데이터 로드 완료")
    print("=" * 60)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--with-reviews':
        load_reviews_with_users()
    else:
        load_fixtures()

