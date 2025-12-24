"""
영화의 Heaviness와 Satisfaction 점수를 분석하는 스크립트
GPT 5 mini API와 검색 기능을 사용하여 영화를 분석합니다.
"""

import os
import sys
import django
import json
import requests
from typing import Dict, Optional, Tuple
from tqdm import tqdm

# Django 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pjt.settings')
django.setup()

from movies.models import Movie

# GPT 5 mini API 설정
GMS_KEY = "S14P02CA08-ef67111a-1584-41bf-a74c-3517ed705314"
GMS_API_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions"

# 검색 API 설정 (DuckDuckGo 사용)
try:
    from duckduckgo_search import DDGS
    USE_DUCKDUCKGO = True
except ImportError:
    USE_DUCKDUCKGO = False
    print("[경고] duckduckgo-search가 설치되지 않았습니다. pip install duckduckgo-search로 설치하세요.")
    print("검색 없이 진행합니다.")


class MovieAnalyzer:
    """영화 분석 Agent 클래스"""
    
    def __init__(self):
        self.search_engine = None
        if USE_DUCKDUCKGO:
            try:
                self.search_engine = DDGS()
            except Exception as e:
                print(f"[경고] DuckDuckGo 검색 엔진 초기화 실패: {e}")
                self.search_engine = None
    
    def search_movie_info_with_gpt(self, title: str, release_year: int, original_title: str = "") -> str:
        """
        GPT 5 mini를 사용하여 영화 정보를 검색하고 정리합니다.
        
        Args:
            title: 영화 제목
            release_year: 개봉 연도
            original_title: 원제 (선택)
            
        Returns:
            검색 및 정리된 영화 정보 텍스트
        """
        # 먼저 DuckDuckGo로 검색
        raw_search_results = ""
        if self.search_engine:
            try:
                query = f"{title} {release_year} movie plot summary review"
                results = list(self.search_engine.text(query, max_results=5))
                
                if results:
                    raw_search_results = "\n\n".join([
                        f"제목: {r.get('title', '')}\n내용: {r.get('body', '')}"
                        for r in results[:5]
                    ])
            except Exception as e:
                print(f"[경고] 검색 중 오류 발생: {e}")
        
        # GPT 5 mini에게 검색 결과를 정리하고 추가 정보를 수집하도록 요청
        search_prompt = f"""다음 영화에 대한 정보를 검색하고 정리해주세요.

영화 제목: {title}
원제: {original_title or 'N/A'}
개봉 연도: {release_year}

검색 결과:
{raw_search_results if raw_search_results else '검색 결과가 없습니다.'}

위 검색 결과를 바탕으로 다음 정보를 정리해주세요:
1. 영화의 줄거리/스토리
2. 영화의 장르와 특징
3. 영화의 평가와 반응
4. 영화의 주요 내용

중요한 정보만 간결하게 정리해주세요. (200자 이내)"""
        
        messages = [
            {
                "role": "developer",
                "content": "Answer in Korean"
            },
            {
                "role": "user",
                "content": search_prompt
            }
        ]
        
        gpt_result = self.call_gpt_api(messages)
        return gpt_result if gpt_result else raw_search_results
    
    def call_gpt_api(self, messages: list) -> Optional[str]:
        """
        GPT 5 mini API를 호출합니다.
        
        Args:
            messages: 메시지 리스트
            
        Returns:
            API 응답 텍스트 또는 None
        """
        try:
            response = requests.post(
                GMS_API_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {GMS_KEY}"
                },
                json={
                    "model": "gpt-5-mini",
                    "messages": messages,
                    "max_completion_tokens": 1000  # 토큰 제한 증가
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('choices', [{}])[0].get('message', {}).get('content', '')
            else:
                print(f"[오류] API 호출 실패: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"[오류] API 호출 중 예외 발생: {e}")
            return None
    
    def analyze_movie(self, movie: Movie, use_search: bool = True) -> Tuple[Optional[int], Optional[int]]:
        """
        영화를 분석하여 Heaviness와 Satisfaction 점수를 반환합니다.
        
        Args:
            movie: Movie 객체
            use_search: 검색 기능 사용 여부
            
        Returns:
            (heaviness, satisfaction) 튜플
        """
        # 영화 기본 정보 수집
        has_description = movie.description and len(movie.description.strip()) > 50
        
        movie_info = f"""
영화 제목: {movie.title}
원제: {movie.original_title or 'N/A'}
개봉 연도: {movie.release_year}
상영 시간: {movie.runtime}분
감독: {movie.director}
출연진: {movie.cast}
설명: {movie.description[:500] if has_description else 'N/A'}
"""
        
        # 줄거리가 없거나 짧은 경우에만 GPT 5 mini로 검색하여 정보 수집
        search_info = ""
        if not has_description and use_search:
            print(f"[검색] 줄거리가 없는 영화: {movie.title} - GPT로 정보 수집 중...")
            search_results = self.search_movie_info_with_gpt(
                movie.title, 
                movie.release_year, 
                movie.original_title or ""
            )
            if search_results:
                search_info = f"\n\nGPT 검색 결과:\n{search_results}"
        # 설명이 충분한 경우에는 검색하지 않음 (토큰 제한 방지)
        
        # GPT에게 분석 요청
        prompt = f"""다음 영화 정보를 분석하여 Heaviness(무게감)와 Satisfaction(대중성) 점수를 각각 0-100 사이의 정수로 평가해주세요.

영화 정보:
{movie_info}{search_info}

평가 기준:
1. Heaviness (무게감, 0-100):
   - 0-30: 가볍고 오락적인 영화 (코미디, 액션, 로맨스 등)
   - 31-60: 중간 수준의 무게감 (드라마, 스릴러 등)
   - 61-100: 무겁고 진지한 영화 (사회비판, 철학적 주제, 다큐멘터리 등)

2. Satisfaction (대중성, 0-100):
   - 0-30: 소수 취향, 비주류 영화
   - 31-60: 일반적인 대중 영화
   - 61-100: 대중적으로 인기 있는 영화 (블록버스터, 히트작 등)

중요: 반드시 유효한 JSON 형식으로만 응답하세요. 다른 텍스트나 설명은 포함하지 마세요.

응답 형식:
{{
    "heaviness": <0-100 사이의 정수>,
    "satisfaction": <0-100 사이의 정수>,
    "reasoning": "<간단한 이유 설명>"
}}
"""
        
        messages = [
            {
                "role": "developer",
                "content": "Answer in Korean"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = self.call_gpt_api(messages)
        
        if not response:
            return None, None
        
        # JSON 파싱 시도
        try:
            # JSON 부분만 추출 (코드 블록 제거)
            response = response.strip()
            
            # 코드 블록 제거
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                if end != -1:
                    response = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                if end != -1:
                    response = response[start:end].strip()
            
            # JSON 객체 찾기
            start_brace = response.find("{")
            end_brace = response.rfind("}")
            if start_brace != -1 and end_brace != -1 and end_brace > start_brace:
                response = response[start_brace:end_brace+1]
            
            response = response.strip()
            
            result = json.loads(response)
            heaviness = int(result.get('heaviness', 0))
            satisfaction = int(result.get('satisfaction', 0))
            
            # 범위 검증
            heaviness = max(0, min(100, heaviness))
            satisfaction = max(0, min(100, satisfaction))
            
            return heaviness, satisfaction
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"[경고] JSON 파싱 실패: {e}")
            print(f"[응답 내용]: {response[:300]}")
            return None, None
    
    def analyze_all_movies(self, limit: Optional[int] = None, use_search: bool = True, force_update: bool = False):
        """
        DB에 있는 모든 영화를 분석합니다.
        
        Args:
            limit: 분석할 영화 수 제한 (None이면 전체)
            use_search: 검색 기능 사용 여부
            force_update: True이면 이미 점수가 있는 영화도 다시 분석
        """
        if force_update:
            # 모든 영화 분석 (점수가 있어도 다시 분석)
            movies = Movie.objects.all()
        else:
            # 점수가 없는 영화만 분석
            movies = Movie.objects.filter(heaviness__isnull=True, satisfaction__isnull=True)
        
        if limit:
            movies = movies[:limit]
        
        total = movies.count()
        print(f"\n총 {total}개의 영화를 분석합니다...")
        
        success_count = 0
        fail_count = 0
        
        for movie in tqdm(movies, desc="영화 분석 중"):
            try:
                heaviness, satisfaction = self.analyze_movie(movie, use_search=use_search)
                
                if heaviness is not None and satisfaction is not None:
                    movie.heaviness = heaviness
                    movie.satisfaction = satisfaction
                    movie.save()
                    success_count += 1
                    # Windows 인코딩 문제 방지를 위해 ASCII만 사용
                    try:
                        tqdm.write(f"[OK] {movie.title} ({movie.release_year}) - H:{heaviness}, S:{satisfaction}")
                    except UnicodeEncodeError:
                        tqdm.write(f"[OK] Movie ID:{movie.id} - H:{heaviness}, S:{satisfaction}")
                else:
                    fail_count += 1
                    try:
                        tqdm.write(f"[FAIL] {movie.title} ({movie.release_year}) - Score calculation failed")
                    except UnicodeEncodeError:
                        tqdm.write(f"[FAIL] Movie ID:{movie.id} - Score calculation failed")
            except KeyboardInterrupt:
                print("\n\n[중단] 사용자에 의해 중단되었습니다.")
                break
            except Exception as e:
                fail_count += 1
                try:
                    tqdm.write(f"[ERROR] {movie.title} ({movie.release_year}) - {str(e)[:50]}")
                except UnicodeEncodeError:
                    tqdm.write(f"[ERROR] Movie ID:{movie.id} - {str(e)[:50]}")
        
        print(f"\n[완료] 성공: {success_count}개, 실패: {fail_count}개")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='DB에 있는 영화의 Heaviness와 Satisfaction 점수 분석')
    parser.add_argument('--limit', type=int, default=None, help='분석할 영화 수 제한')
    parser.add_argument('--no-search', action='store_true', help='검색 기능 사용 안 함')
    parser.add_argument('--movie-id', type=int, default=None, help='특정 영화 ID만 분석')
    parser.add_argument('--force', action='store_true', help='이미 점수가 있는 영화도 다시 분석')
    
    args = parser.parse_args()
    
    analyzer = MovieAnalyzer()
    
    if args.movie_id:
        # 특정 영화만 분석
        try:
            movie = Movie.objects.get(id=args.movie_id)
            print(f"\n영화 분석: {movie.title} ({movie.release_year})")
            heaviness, satisfaction = analyzer.analyze_movie(movie, use_search=not args.no_search)
            
            if heaviness is not None and satisfaction is not None:
                movie.heaviness = heaviness
                movie.satisfaction = satisfaction
                movie.save()
                print(f"[성공] Heaviness: {heaviness}, Satisfaction: {satisfaction}")
            else:
                print("[실패] 점수 계산 실패")
        except Movie.DoesNotExist:
            print(f"[오류] 영화 ID {args.movie_id}를 찾을 수 없습니다.")
    else:
        # DB에 있는 영화 분석 (기본적으로 점수가 없는 영화만)
        analyzer.analyze_all_movies(limit=args.limit, use_search=not args.no_search, force_update=args.force)


if __name__ == "__main__":
    main()

