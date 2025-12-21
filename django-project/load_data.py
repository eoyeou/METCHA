import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pjt.settings')
django.setup()

import requests
from django.conf import settings
from movies.models import Movie, Genre

API_KEY = settings.TMDB_API_KEY
BASE_URL = 'https://api.themoviedb.org/3'
IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/original'

print("=" * 50)
print("TMDB 데이터 가져오는 중...")
print("=" * 50)

# 1. 장르 가져오기
print("\n[1단계] 장르 데이터 로딩...")
genre_url = f"{BASE_URL}/genre/movie/list"
genre_response = requests.get(genre_url, params={'api_key': API_KEY, 'language': 'ko-KR'})
genre_count = 0

for g in genre_response.json()['genres']:
    Genre.objects.get_or_create(genre_name=g['name'])
    print(f"  ✓ {g['name']}")
    genre_count += 1

print(f"\n장르 {genre_count}개 로드 완료!\n")

# 2. 영화 가져오기
print("[2단계] 영화 데이터 로딩...")
total = 0
PAGES = 3  # 가져올 페이지 수 (1페이지 = 약 20개 영화)

for page in range(1, PAGES + 1):
    print(f"\n페이지 {page}/{PAGES} 처리 중...")
    url = f"{BASE_URL}/movie/popular"
    response = requests.get(url, params={
        'api_key': API_KEY, 
        'language': 'ko-KR', 
        'page': page
    })
    
    movies_data = response.json().get('results', [])
    
    for movie_data in movies_data:
        try:
            # 상세 정보 가져오기
            detail_url = f"{BASE_URL}/movie/{movie_data['id']}"
            detail = requests.get(detail_url, params={
                'api_key': API_KEY, 
                'language': 'ko-KR',
                'append_to_response': 'credits'
            }).json()
            
            # 감독 찾기
            director = "정보 없음"
            if 'credits' in detail and 'crew' in detail['credits']:
                for crew in detail['credits']['crew']:
                    if crew['job'] == 'Director':
                        director = crew['name']
                        break
            
            # 출연진 (상위 5명)
            cast_list = []
            if 'credits' in detail and 'cast' in detail['credits']:
                cast_list = [actor['name'] for actor in detail['credits']['cast'][:5]]
            cast = ', '.join(cast_list) if cast_list else "정보 없음"
            
            # 포스터 URL
            poster_url = ""
            if detail.get('poster_path'):
                poster_url = f"{IMAGE_BASE_URL}{detail['poster_path']}"
            
            # 개봉년도
            release_year = 2000
            if detail.get('release_date'):
                try:
                    release_year = int(detail['release_date'][:4])
                except:
                    pass
            
            # 영화 저장
            movie, created = Movie.objects.update_or_create(
                title=detail['title'],
                defaults={
                    'original_title': detail.get('original_title', ''),
                    'description': detail.get('overview', ''),
                    'poster_url': poster_url,
                    'release_year': release_year,
                    'runtime': detail.get('runtime', 0),
                    'director': director,
                    'cast': cast,
                }
            )
            
            # 장르 연결
            if 'genres' in detail:
                for genre_data in detail['genres']:
                    genre, _ = Genre.objects.get_or_create(genre_name=genre_data['name'])
                    movie.genres.add(genre)
            
            total += 1
            status = "생성" if created else "업데이트"
            print(f"  ✓ [{status}] {movie.title} ({movie.release_year})")
            
        except Exception as e:
            print(f"  ✗ 에러 발생: {movie_data.get('title', 'Unknown')} - {str(e)}")
            continue

print("\n" + "=" * 50)
print(f"완료! 총 {total}개 영화 저장됨")
print("=" * 50)