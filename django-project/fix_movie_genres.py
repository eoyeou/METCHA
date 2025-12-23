"""
영화 데이터에 장르를 다시 연결하는 스크립트
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pjt.settings')
django.setup()

import requests
from django.conf import settings
from movies.models import Movie, Genre

API_KEY = settings.TMDB_API_KEY
BASE_URL = 'https://api.themoviedb.org/3'


def fix_movie_genres():
    """기존 영화들의 장르를 TMDB API에서 가져와서 연결"""
    print("\n[영화 장르 수정 시작]")
    
    movies = Movie.objects.all()
    total = movies.count()
    print(f"총 {total}개의 영화를 처리합니다.\n")
    
    fixed_count = 0
    error_count = 0
    
    for idx, movie in enumerate(movies, 1):
        try:
            # 장르가 이미 있는지 확인
            if movie.genres.exists():
                try:
                    print(f"[{idx}/{total}] {movie.title}: 이미 장르가 있습니다. ({movie.genres.count()}개)")
                except UnicodeEncodeError:
                    print(f"[{idx}/{total}] Movie ID {movie.id}: 이미 장르가 있습니다. ({movie.genres.count()}개)")
                continue
            
            # TMDB ID가 없으면 스킵
            if not movie.tmdb_id:
                try:
                    print(f"[{idx}/{total}] {movie.title}: TMDB ID가 없어서 스킵합니다.")
                except UnicodeEncodeError:
                    print(f"[{idx}/{total}] Movie ID {movie.id}: TMDB ID가 없어서 스킵합니다.")
                continue
            
            # TMDB API에서 영화 상세 정보 가져오기 (한국어)
            detail_url = f"{BASE_URL}/movie/{movie.tmdb_id}"
            params = {
                'api_key': API_KEY,
                'language': 'ko-KR'
            }
            
            response = requests.get(detail_url, params=params)
            if response.status_code != 200:
                try:
                    print(f"[{idx}/{total}] {movie.title}: TMDB API 호출 실패 (상태 코드: {response.status_code})")
                except UnicodeEncodeError:
                    print(f"[{idx}/{total}] Movie ID {movie.id}: TMDB API 호출 실패 (상태 코드: {response.status_code})")
                error_count += 1
                continue
            
            detail_data = response.json()
            
            # 장르 정보 추출
            if 'genres' in detail_data and detail_data['genres']:
                genre_count = 0
                for genre_data in detail_data['genres']:
                    genre_name = genre_data.get('name')
                    if genre_name:
                        # 장르 가져오기 또는 생성
                        genre, created = Genre.objects.get_or_create(genre_name=genre_name)
                        # 영화에 장르 연결 (중복 방지)
                        if not movie.genres.filter(id=genre.id).exists():
                            movie.genres.add(genre)
                            genre_count += 1
                
                if genre_count > 0:
                    try:
                        print(f"[{idx}/{total}] [OK] {movie.title}: {genre_count}개 장르 연결 완료")
                    except UnicodeEncodeError:
                        print(f"[{idx}/{total}] [OK] Movie ID {movie.id}: {genre_count}개 장르 연결 완료")
                    fixed_count += 1
                else:
                    try:
                        print(f"[{idx}/{total}] {movie.title}: 장르 정보가 없습니다.")
                    except UnicodeEncodeError:
                        print(f"[{idx}/{total}] Movie ID {movie.id}: 장르 정보가 없습니다.")
            else:
                try:
                    print(f"[{idx}/{total}] {movie.title}: TMDB 응답에 장르 정보가 없습니다.")
                except UnicodeEncodeError:
                    print(f"[{idx}/{total}] Movie ID {movie.id}: TMDB 응답에 장르 정보가 없습니다.")
            
            # API 호출 제한을 피하기 위해 약간의 딜레이
            if idx % 10 == 0:
                import time
                time.sleep(0.5)
                
        except Exception as e:
            try:
                print(f"[{idx}/{total}] [ERROR] {movie.title}: 에러 발생 - {str(e)}")
            except UnicodeEncodeError:
                print(f"[{idx}/{total}] [ERROR] Movie ID {movie.id}: 에러 발생 - {str(e)}")
            error_count += 1
            continue
    
    print(f"\n[완료]")
    print(f"  - 장르 연결 완료: {fixed_count}개")
    print(f"  - 에러 발생: {error_count}개")
    print(f"  - 이미 장르 있음: {total - fixed_count - error_count}개")


if __name__ == '__main__':
    fix_movie_genres()

