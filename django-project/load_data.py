import os
import django
import sys
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pjt.settings')
django.setup()

import requests
import random
from django.conf import settings
from movies.models import Movie, Genre
from accounts.models import User
from reviews.models import Review

API_KEY = settings.TMDB_API_KEY
BASE_URL = 'https://api.themoviedb.org/3'
IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/original'


def load_genres():
    """장르 데이터 로드"""
    print("\n[1단계] 장르 데이터 로딩...")
    genre_url = f"{BASE_URL}/genre/movie/list"
    genre_response = requests.get(genre_url, params={'api_key': API_KEY, 'language': 'ko-KR'})
    genre_count = 0

    for g in genre_response.json()['genres']:
        Genre.objects.get_or_create(genre_name=g['name'])
        print(f"  ✓ {g['name']}")
        genre_count += 1

    print(f"\n장르 {genre_count}개 로드 완료!\n")
    return genre_count


def load_movies(pages=10):
    """영화 데이터 로드"""
    print("[2단계] 영화 데이터 로딩...")
    total = 0

    for page in range(1, pages + 1):
        print(f"\n페이지 {page}/{pages} 처리 중...")
        url = f"{BASE_URL}/movie/popular"
        response = requests.get(url, params={
            'api_key': API_KEY, 
            'language': 'ko-KR', 
            'page': page
        })
        
        movies_data = response.json().get('results', [])
        
        for movie_data in movies_data:
            try:
                # 상세 정보 가져오기 (영어와 한국어 모두)
                detail_url = f"{BASE_URL}/movie/{movie_data['id']}"
                
                # 영어 정보 가져오기 (AI embedding용)
                detail_en = requests.get(detail_url, params={
                    'api_key': API_KEY, 
                    'language': 'en-US',
                    'append_to_response': 'credits'
                }).json()
                
                # 한국어 정보 가져오기 (UI 표시용)
                detail_ko = requests.get(detail_url, params={
                    'api_key': API_KEY, 
                    'language': 'ko-KR',
                    'append_to_response': 'credits'
                }).json()
                
                # 영어 설명 (기본, AI embedding용)
                description = detail_en.get('overview', 'No description available.')
                # 한국어 설명 (UI 표시용)
                kor_description = detail_ko.get('overview', '')
                
                # 영어 original_title
                original_title = detail_en.get('original_title', '')
                # 한국어 title
                title = detail_ko.get('title', detail_en.get('title', ''))
                
                # 감독 찾기
                director = "정보 없음"
                if 'credits' in detail_en and 'crew' in detail_en['credits']:
                    for crew in detail_en['credits']['crew']:
                        if crew['job'] == 'Director':
                            director = crew['name']
                            break
                
                # 출연진 (상위 5명)
                cast_list = []
                if 'credits' in detail_en and 'cast' in detail_en['credits']:
                    cast_list = [actor['name'] for actor in detail_en['credits']['cast'][:5]]
                cast = ', '.join(cast_list) if cast_list else "정보 없음"
                
                # 포스터 URL
                poster_url = ""
                if detail_en.get('poster_path'):
                    poster_url = f"{IMAGE_BASE_URL}{detail_en['poster_path']}"
                
                # 개봉년도
                release_year = 2000
                if detail_en.get('release_date'):
                    try:
                        release_year = int(detail_en['release_date'][:4])
                    except:
                        pass
                
                # 영화 저장 (tmdb_id를 기준으로 중복 방지)
                tmdb_id = detail_en.get('id')
                movie, created = Movie.objects.update_or_create(
                    tmdb_id=tmdb_id,
                    defaults={
                        'title': title,
                        'original_title': original_title,
                        'description': description,  # 영어 설명 (AI embedding용)
                        'kor_description': kor_description,  # 한국어 설명 (UI 표시용)
                        'poster_url': poster_url,
                        'release_year': release_year,
                        'runtime': detail_en.get('runtime', 0),
                        'director': director,
                        'cast': cast,
                    }
                )
                
                # 장르 연결 (한국어 장르명 사용)
                if 'genres' in detail_ko:
                    for genre_data in detail_ko['genres']:
                        genre, _ = Genre.objects.get_or_create(genre_name=genre_data['name'])
                        movie.genres.add(genre)
                
                total += 1
                status = "생성" if created else "업데이트"
                print(f"  ✓ [{status}] {movie.title} ({movie.release_year})")
                
            except Exception as e:
                print(f"  ✗ 에러 발생: {movie_data.get('title', 'Unknown')} - {str(e)}")
                continue

    return total


def update_empty_descriptions():
    """설명이 비어있는 영화 업데이트"""
    print("=" * 50)
    print("설명이 비어있는 영화 업데이트 중...")
    print("=" * 50)

    # 설명이 비어있는 영화 찾기
    empty_movies = Movie.objects.filter(description='')
    print(f"\n총 {empty_movies.count()}개 영화 발견\n")

    updated = 0
    for movie in empty_movies:
        if not movie.tmdb_id:
            print(f"  ⚠ {movie.title}: tmdb_id가 없어서 건너뜀")
            continue
        
        try:
            # 영어 정보 가져오기
            detail_url = f"{BASE_URL}/movie/{movie.tmdb_id}"
            detail_en = requests.get(detail_url, params={
                'api_key': API_KEY, 
                'language': 'en-US'
            }).json()
            
            # 한국어 정보 가져오기
            detail_ko = requests.get(detail_url, params={
                'api_key': API_KEY, 
                'language': 'ko-KR'
            }).json()
            
            # 영어 설명 (AI embedding용)
            description = detail_en.get('overview', 'No description available.')
            # 한국어 설명 (UI 표시용)
            kor_description = detail_ko.get('overview', '')
            
            # 업데이트
            movie.description = description
            movie.kor_description = kor_description
            movie.save()
            updated += 1
            print(f"  ✓ {movie.title}: 설명 업데이트 완료")
            
        except Exception as e:
            print(f"  ✗ {movie.title}: 에러 발생 - {str(e)}")
            continue

    print("\n" + "=" * 50)
    print(f"완료! 총 {updated}개 영화 설명 업데이트됨")
    print("=" * 50)
    return updated


def update_all_movies():
    """모든 영화의 설명 업데이트 (description: 영어, kor_description: 한국어)"""
    print("=" * 50)
    print("영화 설명 업데이트 중...")
    print("(description: 영어, kor_description: 한국어)")
    print("=" * 50)

    # 모든 영화 가져오기
    movies = Movie.objects.all()
    total = movies.count()
    print(f"\n총 {total}개 영화 업데이트 시작\n")

    updated = 0
    for idx, movie in enumerate(movies, 1):
        if not movie.tmdb_id:
            print(f"[{idx}/{total}] ⚠ {movie.title}: tmdb_id가 없어서 건너뜀")
            continue
        
        try:
            # 영어 정보 가져오기
            detail_url = f"{BASE_URL}/movie/{movie.tmdb_id}"
            detail_en = requests.get(detail_url, params={
                'api_key': API_KEY, 
                'language': 'en-US'
            }).json()
            
            # 한국어 정보 가져오기
            detail_ko = requests.get(detail_url, params={
                'api_key': API_KEY, 
                'language': 'ko-KR'
            }).json()
            
            # 영어 설명 (AI embedding용)
            description = detail_en.get('overview', 'No description available.')
            # 한국어 설명 (UI 표시용)
            kor_description = detail_ko.get('overview', '')
            
            # 영어 original_title
            original_title = detail_en.get('original_title', '')
            # 한국어 title
            title = detail_ko.get('title', detail_en.get('title', ''))
            
            # 업데이트
            movie.description = description
            movie.kor_description = kor_description
            movie.original_title = original_title
            movie.title = title
            movie.save()
            
            updated += 1
            if idx % 20 == 0:
                print(f"[{idx}/{total}] 진행 중... ({updated}개 업데이트 완료)")
            
        except Exception as e:
            print(f"[{idx}/{total}] ✗ {movie.title}: 에러 발생 - {str(e)}")
            continue

    print("\n" + "=" * 50)
    print(f"완료! 총 {updated}개 영화 업데이트됨")
    print("=" * 50)
    return updated


def create_test_users_and_reviews(num_users=5, reviews_per_user=10):
    """테스트용 사용자와 리뷰 데이터 생성"""
    print("=" * 50)
    print("테스트 사용자 및 리뷰 데이터 생성 중...")
    print("=" * 50)
    
    # 리뷰 템플릿
    review_templates = [
        "정말 재미있었어요! {rating}점 드립니다.",
        "기대 이상이었습니다. {rating}점입니다.",
        "괜찮은 영화였어요. {rating}점.",
        "완벽한 영화였습니다! {rating}점 드립니다.",
        "스토리가 인상적이었어요. {rating}점.",
        "연출이 훌륭했습니다. {rating}점.",
        "배우들의 연기가 좋았어요. {rating}점.",
        "영상미가 아름다웠습니다. {rating}점.",
        "감동적인 영화였어요. {rating}점 드립니다.",
        "시간 가는 줄 몰랐습니다. {rating}점.",
    ]
    
    # 사용자 생성
    users = []
    for i in range(1, num_users + 1):
        username = f"testuser{i}"
        email = f"test{i}@example.com"
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': f'테스트{i}',
                'last_name': '사용자',
            }
        )
        
        if created:
            user.set_password('test1234')
            user.save()
            print(f"  ✓ 사용자 생성: {username}")
        else:
            print(f"  - 사용자 이미 존재: {username}")
        
        users.append(user)
    
    # 영화 목록 가져오기
    movies = list(Movie.objects.all())
    if not movies:
        print("\n  ✗ 영화 데이터가 없습니다. 먼저 영화 데이터를 로드해주세요.")
        return
    
    print(f"\n총 {len(movies)}개 영화 중에서 리뷰 작성 중...\n")
    
    # 각 사용자마다 리뷰 작성
    total_reviews = 0
    for user in users:
        # 각 사용자가 랜덤하게 영화 선택 (중복 방지)
        user_movies = random.sample(movies, min(reviews_per_user, len(movies)))
        
        for movie in user_movies:
            # 평점 랜덤 생성 (2.0 ~ 5.0)
            rating = round(random.uniform(2.0, 5.0), 1)
            
            # 리뷰 내용 생성
            template = random.choice(review_templates)
            content = template.format(rating=rating)
            
            # 스포일러 여부 랜덤
            is_spoiler = random.choice([True, False])
            if is_spoiler:
                content += " (스포일러 주의)"
            
            # 리뷰 생성 또는 업데이트
            review, created = Review.objects.update_or_create(
                user=user,
                movie=movie,
                defaults={
                    'rating': rating,
                    'content': content,
                    'is_spoiler': is_spoiler,
                }
            )
            
            total_reviews += 1
        
        print(f"  ✓ {user.username}: {len(user_movies)}개 리뷰 작성")
    
    print("\n" + "=" * 50)
    print(f"완료! 총 {len(users)}명 사용자, {total_reviews}개 리뷰 생성됨")
    print("=" * 50)
    return len(users), total_reviews


def main():
    """메인 함수 - 명령줄 인자에 따라 다른 작업 수행"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'update-empty':
            update_empty_descriptions()
        elif command == 'update-all':
            update_all_movies()
        elif command == 'genres':
            load_genres()
        elif command == 'movies':
            pages = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            load_movies(pages)
        elif command == 'test-data':
            num_users = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            reviews_per_user = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            create_test_users_and_reviews(num_users, reviews_per_user)
        else:
            print("사용법:")
            print("  python load_data.py                    # 전체 데이터 로드 (장르 + 영화)")
            print("  python load_data.py genres             # 장르만 로드")
            print("  python load_data.py movies [페이지수]        # 영화만 로드 (기본 10페이지)")
            print("  python load_data.py update-empty      # 설명이 비어있는 영화만 업데이트")
            print("  python load_data.py update-all        # 모든 영화 설명 업데이트")
            print("  python load_data.py test-data [사용자수] [리뷰수]  # 테스트 사용자 및 리뷰 생성")
    else:
        # 기본: 전체 데이터 로드
        print("=" * 50)
        print("TMDB 데이터 가져오는 중...")
        print("=" * 50)
        
        load_genres()
        total = load_movies()
        
        print("\n" + "=" * 50)
        print(f"완료! 총 {total}개 영화 저장됨")
        print("=" * 50)


if __name__ == '__main__':
    main()
if __name__ == '__main__':
    main()
