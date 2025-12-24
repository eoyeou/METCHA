"""
영화 데이터를 Fixture 형식으로 내보내기
인코딩 문제를 해결하기 위한 스크립트
"""
import os
import sys
import django
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pjt.settings')
django.setup()

from movies.models import Movie, Genre

# Fixture 디렉토리 확인
fixture_dir = os.path.join(os.path.dirname(__file__), 'movies', 'fixtures')
os.makedirs(fixture_dir, exist_ok=True)

# 장르 데이터 내보내기
genres = Genre.objects.all()
genre_data = []
for genre in genres:
    genre_data.append({
        "model": "movies.genre",
        "pk": genre.id,
        "fields": {
            "genre_name": genre.genre_name
        }
    })

# 영화 데이터 내보내기 (처음 200개만)
movies = Movie.objects.all()[:200]
movie_data = []

for movie in movies:
    # 장르 ID 목록
    genre_ids = list(movie.genres.values_list('id', flat=True))
    
    # 특수 문자 처리
    title = movie.title if movie.title else ""
    original_title = movie.original_title if movie.original_title else ""
    description = movie.description if movie.description else ""
    kor_description = movie.kor_description if movie.kor_description else ""
    director = movie.director if movie.director else ""
    cast = movie.cast if movie.cast else ""
    poster_url = movie.poster_url if movie.poster_url else ""
    
    movie_data.append({
        "model": "movies.movie",
        "pk": movie.id,
        "fields": {
            "tmdb_id": movie.tmdb_id,
            "title": title,
            "original_title": original_title,
            "description": description,
            "kor_description": kor_description,
            "poster_url": poster_url,
            "release_year": movie.release_year,
            "runtime": movie.runtime,
            "director": director,
            "cast": cast,
            "avg_rating": float(movie.avg_rating) if movie.avg_rating else 0.0,
            "review_count": movie.review_count,
            "heaviness": movie.heaviness,
            "satisfaction": movie.satisfaction,
            "genres": genre_ids,
            "created_at": movie.created_at.isoformat() if movie.created_at else None
        }
    })

# MovieGenre 중간 테이블 데이터
from movies.models import MovieGenre
movie_genre_data = []
for mg in MovieGenre.objects.all():
    movie_genre_data.append({
        "model": "movies.moviegenre",
        "pk": mg.id,
        "fields": {
            "movie": mg.movie.id,
            "genre": mg.genre.id
        }
    })

# 전체 데이터 합치기
all_data = genre_data + movie_data + movie_genre_data

# JSON 파일로 저장 (UTF-8 인코딩)
output_file = os.path.join(fixture_dir, 'movies_initial.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f"\n[완료] Fixture 파일 생성 완료!")
print(f"위치: {output_file}")
print(f"장르: {len(genre_data)}개")
print(f"영화: {len(movie_data)}개")
print(f"영화-장르 관계: {len(movie_genre_data)}개")
print(f"총: {len(all_data)}개 항목")

