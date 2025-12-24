"""
리뷰 fixtures 로드를 위한 사용자 생성 스크립트
"""
import os
import sys
import django
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pjt.settings')
django.setup()

from accounts.models import User


def create_users_for_reviews():
    """리뷰 fixtures에 필요한 사용자 생성"""
    # reviews_sample.json 파일 읽기
    reviews_fixture_path = 'reviews/fixtures/reviews_sample.json'
    
    if not os.path.exists(reviews_fixture_path):
        print(f"[ERROR] {reviews_fixture_path} 파일을 찾을 수 없습니다.")
        return
    
    # 필요한 사용자 ID 추출
    with open(reviews_fixture_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    user_ids = set()
    for item in data:
        if item['model'] == 'reviews.review':
            user_ids.add(item['fields']['user'])
        elif item['model'] == 'reviews.reviewlike':
            user_ids.add(item['fields']['user'])
    
    if not user_ids:
        print("[INFO] 리뷰 fixtures에 사용자 데이터가 없습니다.")
        return
    
    max_user_id = max(user_ids)
    print(f"[INFO] 필요한 최대 사용자 ID: {max_user_id}")
    print(f"[INFO] 필요한 사용자 수: {len(user_ids)}명")
    
    # 사용자 생성
    created_count = 0
    existing_count = 0
    
    for user_id in range(1, max_user_id + 1):
        username = f"testuser{user_id}"
        email = f"test{user_id}@example.com"
        
        user, created = User.objects.get_or_create(
            id=user_id,
            defaults={
                'username': username,
                'email': email,
                'first_name': f'테스트{user_id}',
                'last_name': '사용자',
            }
        )
        
        if created:
            user.set_password('test1234')
            user.save()
            created_count += 1
            print(f"[OK] 사용자 생성: ID={user_id}, username={username}")
        else:
            # 기존 사용자도 비밀번호 확인 및 설정
            if not user.check_password('test1234'):
                user.set_password('test1234')
                user.save()
                print(f"[OK] 사용자 비밀번호 설정: ID={user_id}, username={username}")
            existing_count += 1
    
    print("\n" + "=" * 60)
    print(f"완료! 새로 생성: {created_count}명, 기존: {existing_count}명")
    print("=" * 60)


if __name__ == '__main__':
    create_users_for_reviews()

