"""
테스트용 리뷰 데이터를 Fixture 형식으로 내보내기
"""
import os
import sys
import django
import json
from datetime import datetime, timedelta
import random

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pjt.settings')
django.setup()

from reviews.models import Review, ReviewLike
from accounts.models import User
from movies.models import Movie

# Fixture 디렉토리 확인
fixture_dir = os.path.join(os.path.dirname(__file__), 'reviews', 'fixtures')
os.makedirs(fixture_dir, exist_ok=True)

print("\n[테스트용 리뷰 Fixture 생성 중...]")

# 테스트용 사용자 데이터 (실제 사용자 제외, 샘플만)
# 또는 기존 사용자 중 일부만 선택
all_users = list(User.objects.all())
all_movies = list(Movie.objects.all())

if not all_users or not all_movies:
    print("[오류] 사용자 또는 영화 데이터가 없습니다.")
    print("먼저 영화 fixture를 로드하고 테스트 사용자를 생성하세요.")
    sys.exit(1)

# 모든 리뷰 데이터 포함
all_reviews = Review.objects.all()

review_data = []
review_like_data = []

for review in all_reviews:
    # 리뷰 데이터
    review_data.append({
        "model": "reviews.review",
        "pk": review.id,
        "fields": {
            "user": review.user.id,
            "movie": review.movie.id,
            "rating": float(review.rating),
            "content": review.content if review.content else "",
            "original_content": review.original_content if review.original_content else "",
            "likes_count": review.likes_count,
            "is_spoiler": review.is_spoiler,
            "created_at": review.created_at.isoformat() if review.created_at else None,
            "updated_at": review.updated_at.isoformat() if review.updated_at else None
        }
    })

# 모든 리뷰 좋아요 데이터 포함
all_likes = ReviewLike.objects.all()
for like in all_likes:
    review_like_data.append({
        "model": "reviews.reviewlike",
        "pk": like.id,
        "fields": {
            "user": like.user.id,
            "review": like.review.id,
            "created_at": like.created_at.isoformat() if like.created_at else None
        }
    })

# 전체 데이터 합치기
all_data = review_data + review_like_data

# JSON 파일로 저장 (UTF-8 인코딩)
output_file = os.path.join(fixture_dir, 'reviews_sample.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f"\n[완료] 리뷰 Fixture 파일 생성 완료!")
print(f"위치: {output_file}")
print(f"리뷰: {len(review_data)}개")
print(f"리뷰 좋아요: {len(review_like_data)}개")
print(f"총: {len(all_data)}개 항목")
print(f"\n로드 방법:")
print(f"  python manage.py loaddata reviews/fixtures/reviews_sample.json")
print(f"\n주의: 리뷰를 로드하기 전에 영화와 사용자 데이터가 있어야 합니다.")
print(f"\n참고: 모든 리뷰 데이터가 포함되었습니다.")

