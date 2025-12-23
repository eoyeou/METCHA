"""
더 많은 리뷰 데이터를 수집하기 위한 개선된 스크립트

전략:
1. TMDB에서 더 많은 페이지와 언어로 리뷰 수집
2. 인기 영화 위주로 수집 (리뷰가 더 많음)
3. 여러 영화에 대해 병렬 처리
"""
import os
import django
import sys
import time
import random
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pjt.settings')
django.setup()

import requests
from django.conf import settings
from django.utils import timezone
from movies.models import Movie
from accounts.models import User
from reviews.models import Review

API_KEY = settings.TMDB_API_KEY
BASE_URL = 'https://api.themoviedb.org/3'


def get_tmdb_popular_movies(api_key, pages=20):
    """TMDB 인기 영화 목록 가져오기 (리뷰가 많을 가능성)"""
    all_movies = []
    
    for page in range(1, pages + 1):
        url = f"{BASE_URL}/movie/popular"
        params = {
            'api_key': api_key,
            'language': 'ko-KR',
            'page': page
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'results' not in data:
                break
            
            all_movies.extend(data['results'])
            
            if page >= data.get('total_pages', 1):
                break
            
            time.sleep(0.25)
            
        except Exception as e:
            print(f"페이지 {page} 실패: {str(e)}")
            break
    
    return all_movies


def get_tmdb_top_rated_movies(api_key, pages=10):
    """TMDB 최고 평점 영화 목록 (리뷰가 많을 가능성)"""
    all_movies = []
    
    for page in range(1, pages + 1):
        url = f"{BASE_URL}/movie/top_rated"
        params = {
            'api_key': api_key,
            'language': 'ko-KR',
            'page': page
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'results' not in data:
                break
            
            all_movies.extend(data['results'])
            
            if page >= data.get('total_pages', 1):
                break
            
            time.sleep(0.25)
            
        except Exception as e:
            print(f"페이지 {page} 실패: {str(e)}")
            break
    
    return all_movies


def get_all_tmdb_reviews(movie_id, api_key):
    """TMDB에서 가능한 모든 리뷰 가져오기 (모든 페이지, 모든 언어)"""
    all_reviews = []
    seen_ids = set()
    languages = ['en-US', 'ko-KR', 'es-ES', 'fr-FR', 'de-DE', 'ja-JP']
    
    for language in languages:
        for page in range(1, 100):  # 최대 100페이지까지
            url = f"{BASE_URL}/movie/{movie_id}/reviews"
            params = {
                'api_key': api_key,
                'language': language,
                'page': page
            }
            
            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if 'results' not in data or len(data['results']) == 0:
                    break
                
                for review in data['results']:
                    review_id = review.get('id')
                    if review_id and review_id not in seen_ids:
                        all_reviews.append(review)
                        seen_ids.add(review_id)
                
                if page >= data.get('total_pages', 1):
                    break
                
                time.sleep(0.2)
                
            except Exception as e:
                break
    
    return all_reviews


def load_reviews_from_popular_movies(max_movies=200, max_reviews_per_movie=100):
    """TMDB 인기 영화에서 리뷰 대량 수집"""
    print("=" * 60)
    print("TMDB 인기 영화에서 리뷰 대량 수집")
    print("=" * 60)
    
    # TMDB 사용자 생성
    tmdb_user, _ = User.objects.get_or_create(
        username='tmdb_reviewer',
        defaults={'email': 'tmdb@example.com', 'is_active': True}
    )
    
    # 인기 영화 + 최고 평점 영화 가져오기
    print("\n[1단계] TMDB 인기 영화 목록 가져오기...")
    popular_movies = get_tmdb_popular_movies(API_KEY, pages=20)
    top_rated_movies = get_tmdb_top_rated_movies(API_KEY, pages=10)
    
    # 중복 제거
    all_tmdb_movies = {}
    for movie in popular_movies + top_rated_movies:
        tmdb_id = movie.get('id')
        if tmdb_id:
            all_tmdb_movies[tmdb_id] = movie
    
    print(f"  ✓ 총 {len(all_tmdb_movies)}개 영화 발견")
    
    # DB에 영화가 있는지 확인하고 리뷰 수집
    print("\n[2단계] 리뷰 수집 시작...")
    total_saved = 0
    processed = 0
    
    for idx, (tmdb_id, tmdb_movie) in enumerate(list(all_tmdb_movies.items())[:max_movies], 1):
        try:
            # DB에 영화가 있는지 확인
            movie = Movie.objects.filter(tmdb_id=tmdb_id).first()
            
            if not movie:
                # 영화가 없으면 건너뛰거나 생성할 수 있음
                print(f"  [{idx}] {tmdb_movie.get('title')}: DB에 없음, 건너뜀")
                continue
            
            print(f"\n[{idx}/{max_movies}] {movie.title}")
            
            # 모든 리뷰 가져오기
            reviews = get_all_tmdb_reviews(tmdb_id, API_KEY)
            
            if not reviews:
                print(f"  ⚠ 리뷰 없음")
                continue
            
            print(f"  ✓ {len(reviews)}개 리뷰 발견")
            
            # 리뷰 저장
            saved = 0
            for review_data in reviews[:max_reviews_per_movie]:
                try:
                    content = review_data.get('content', '').strip()
                    if not content or len(content) < 10:
                        continue
                    
                    author = review_data.get('author_details', {})
                    rating_value = author.get('rating')
                    
                    if rating_value:
                        rating = round((rating_value / 10) * 5, 1)
                    else:
                        rating = round(random.uniform(2.5, 5.0), 1)
                    
                    created_at_str = review_data.get('created_at', '')
                    if created_at_str:
                        try:
                            created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                            created_at = timezone.make_aware(created_at)
                        except:
                            created_at = timezone.now()
                    else:
                        created_at = timezone.now()
                    
                    Review.objects.get_or_create(
                        user=tmdb_user,
                        movie=movie,
                        defaults={
                            'content': content,
                            'rating': rating,
                            'is_spoiler': False,
                            'created_at': created_at,
                        }
                    )
                    saved += 1
                    
                except Exception as e:
                    continue
            
            total_saved += saved
            processed += 1
            print(f"  ✓ {saved}개 리뷰 저장 완료")
            
            if idx % 10 == 0:
                print(f"\n[진행 상황] {idx}/{max_movies} 영화 처리 ({total_saved}개 리뷰 저장)")
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  ✗ 에러: {str(e)}")
            continue
    
    print("\n" + "=" * 60)
    print(f"완료!")
    print(f"  - 처리된 영화: {processed}개")
    print(f"  - 저장된 리뷰: {total_saved}개")
    print("=" * 60)
    
    return total_saved


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='TMDB 리뷰 대량 수집')
    parser.add_argument('--max-movies', type=int, default=200,
                        help='처리할 최대 영화 수')
    parser.add_argument('--max-reviews', type=int, default=100,
                        help='영화당 최대 리뷰 수')
    
    args = parser.parse_args()
    
    load_reviews_from_popular_movies(
        max_movies=args.max_movies,
        max_reviews_per_movie=args.max_reviews
    )

