"""
영화 점수 확인 스크립트
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pjt.settings')
django.setup()

from movies.models import Movie
from reviews.models import Review

# 전체 영화 수
total_movies = Movie.objects.count()
print(f'전체 영화 수: {total_movies}')

# 점수가 있는 영화 수
movies_with_scores = Movie.objects.filter(
    heaviness__isnull=False, 
    satisfaction__isnull=False
).count()
print(f'점수가 있는 영화 수: {movies_with_scores}')

# 점수가 없는 영화 수
movies_without_scores = Movie.objects.filter(
    heaviness__isnull=True
).count() | Movie.objects.filter(
    satisfaction__isnull=True
).count()
print(f'점수가 없는 영화 수: {movies_without_scores}')

# 전체 리뷰 수
total_reviews = Review.objects.count()
print(f'\n전체 리뷰 수: {total_reviews}')

# 점수가 있는 영화에 대한 리뷰 수
reviews_with_scores = Review.objects.filter(
    movie__heaviness__isnull=False,
    movie__satisfaction__isnull=False
).count()
print(f'점수가 있는 영화에 대한 리뷰 수: {reviews_with_scores}')

# 샘플 영화
sample = Movie.objects.filter(
    heaviness__isnull=False,
    satisfaction__isnull=False
).first()
if sample:
    print(f'\n샘플 영화: {sample.title}')
    print(f'  heaviness: {sample.heaviness}')
    print(f'  satisfaction: {sample.satisfaction}')
else:
    print('\n점수가 있는 영화가 없습니다.')

