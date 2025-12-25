"""
TMDB API 연결 테스트 스크립트
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pjt.settings')
django.setup()

import requests
from django.conf import settings

API_KEY = settings.TMDB_API_KEY
BASE_URL = 'https://api.themoviedb.org/3'

print("=" * 60)
print("TMDB API 연결 테스트")
print("=" * 60)
print(f"\nAPI 키 설정: {'있음' if API_KEY else '없음'}")
if API_KEY:
    print(f"API 키 길이: {len(API_KEY)}")
    print(f"API 키 앞 10자: {API_KEY[:10]}...")

print("\n장르 API 테스트...")
genre_url = f"{BASE_URL}/genre/movie/list"

try:
    response = requests.get(genre_url, params={'api_key': API_KEY, 'language': 'ko-KR'}, timeout=10)
    print(f"HTTP 상태 코드: {response.status_code}")
    print(f"응답 헤더: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n응답 키: {list(data.keys())}")
        
        if 'genres' in data:
            print(f"\n✓ 성공! 장르 {len(data['genres'])}개 발견")
            for g in data['genres'][:5]:
                print(f"  - {g['name']}")
        else:
            print(f"\n✗ 오류: 'genres' 키가 없습니다.")
            print(f"응답 내용: {data}")
    else:
        print(f"\n[ERROR] HTTP 오류: {response.status_code}")
        print(f"응답 내용: {response.text[:500]}")
        if response.status_code == 401:
            print("\n[중요] API 키가 유효하지 않습니다!")
            print("1. .env 파일에 올바른 TMDB_API_KEY를 설정하세요.")
            print("2. API 키는 https://www.themoviedb.org/settings/api 에서 발급받을 수 있습니다.")
        
except requests.exceptions.RequestException as e:
    print(f"\n[ERROR] 요청 실패: {str(e)}")
except Exception as e:
    print(f"\n[ERROR] 예상치 못한 오류: {str(e)}")

print("\n" + "=" * 60)

